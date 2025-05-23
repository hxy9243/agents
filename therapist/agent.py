from typing import List
import os
from pathlib import Path
import sys
import traceback
from datetime import datetime
import uuid

from dotenv import load_dotenv
import dspy
from dspy.retrieve.chromadb_rm import ChromadbRM
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from rich.console import Console

from therapist.models import Conversation, Message, init_session


console = Console()


class ChatBot:

    def __init__(self):
        load_dotenv()

        self.history_threshold = 70
        self.summary_length = 50
        self.distance_threshold = 0.4

        assert self.history_threshold > self.summary_length

        self._init_lm()

        current_file = Path(__file__).resolve()
        project_top = current_file.parent

        database_dir = project_top / os.getenv("DATABASE_DIR", "database/")
        self._init_embed_retriever(f"{database_dir}/chroma/")
        self._session = init_session(f"sqlite:///{database_dir}/database.db")

        self.conversation = self._init_conversation()

    def _init_lm(self):
        lm = dspy.LM(
            api_base=os.getenv("LM_BASE_URL"),
            api_key=os.getenv("LM_API_KEY"),
            model=os.getenv("LM_MODEL_NAME"),
        )
        dspy.configure(lm=lm, track_usage=True)

        self.lm = dspy.ChainOfThought(
            "context: str, history: list, message: str -> answer: str",
        )

    def _init_embed_retriever(self, path: str | Path):
        self.embedding = OpenAIEmbeddingFunction(
            api_base=os.getenv("LM_BASE_URL"),
            api_key=os.getenv("LM_API_KEY"),
            model_name=os.getenv("EMBED_MODEL_NAME"),
        )

        client = chromadb.Client(
            Settings(
                persist_directory=str(path),
                is_persistent=True,
            )
        )
        self.embedding_model = os.getenv("EMBED_MODEL_NAME")
        self.embed_coll = client.get_or_create_collection("embedding")

    def _init_conversation(self) -> Conversation:
        conversation = (
            self._session.query(Conversation)
            .order_by(Conversation.last_updated.desc())
            .first()
        )

        if not conversation:
            name = input("Starting a new conversation, give it a name: ")
            conversation = Conversation(name=name)
            self._session.add(conversation)
            self._session.commit()

        return conversation

    def query_history(self, n=20) -> List[Message]:
        """query the last 20 history, and return in natural order"""
        messages = (
            self._session.query(Message)
            .where(Message.conversation_id == self.conversation.id)
            .order_by(Message.created_at.desc())
            .limit(n)
            .all()
        )

        # only include residual length if there's a summary message
        residual_length = self.history_threshold - self.summary_length
        summary_index = -1

        for i, m in enumerate(messages):
            if m.is_summary:
                summary_index = i
            if summary_index != -1 and i > summary_index + residual_length:
                break
        messages = messages[: i + 1]

        return list(reversed(messages))

    def summarize_history(self, message_id: int, history: List[str]) -> Message:
        summarizer = dspy.Predict("context: str, history: list -> summary: str")

        resp = summarizer(
            context="Summarize this for me, list the important talking points, and keep it informative and concise.\n"
            "Be sure to include previous summaries too.\n"
            "And based on this conversation, analyze the personality, and biggest trouble faced by the user.\n",
            history=history,
        )

        return Message(
            id=message_id,
            role="system",
            content=resp.summary,
            is_summary=True,
        )

    def _create_context(self, message: Message) -> str:
        """retrieve user context"""
        CONTEXT_PROMPT = """You're a helpful, professional therapist.
You care about people's feeling and know what to ask when they are feeling ok.
Your first question is usually: how are you doing and how can I help you today?"""
        results = self.embed_coll.query(
            query_embeddings=self.embedding([message.content]),
            n_results=5,
            include=["metadatas", "documents", "distances"]
        )

        # Filter by distance (assuming lower distance is better)
        filtered_docs = []
        for doc, distance, metadata in zip(results['documents'][0], results['distances'][0], results['metadatas'][0]):
            if distance < self.distance_threshold:
                filtered_docs.append(f'{metadata.get("time")} {metadata["role"]}: {doc}')

        # Concatenate messages
        context = "\n----\n".join(filtered_docs)
        return f"{CONTEXT_PROMPT}\n\nRelevant Context in previous conversation:\n{context}"

    def _save_message(self, message: Message, **kwargs) -> Message:
        """save the conversation in the dbs"""

        message.conversation_id = self.conversation.id
        try:
            self.embed_coll.add(
                ids=[str(message.id)],
                metadatas=[
                    {
                        "conversation_id": self.conversation.id,
                        "role": message.role,
                        "model": self.embedding_model,
                        "time": str(message.created_at),
                        "id": message.id,
                    }
                ],
                documents=[message.content],
                embeddings=self.embedding([message.content]),
            )

            self._session.add(message)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            self.embed_coll.delete(ids=[str(message.id)])
            raise e

        return message

    def turn(self, message_id: int, history: List[str]) -> Message:
        # format and save user message
        message = self.user_input(message_id)
        history.append(f"{message.role}: {message.content}")
        self.pprint_message(message)
        lm_ctx = self._create_context(message)

        self._save_message(message)

        # call predict
        try:
            resp = self.lm(context=lm_ctx, history=history, message=message.content)
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise (e)

        # format and save answer
        answer = Message(role="assistant", content=resp.answer, id=message.id + 1)
        self._save_message(answer)
        history.append(f"{answer.role}: {answer.content}")
        self.pprint_message(answer)

        return answer

    @staticmethod
    def pprint_message(m: Message):
        timestamp = m.created_at.strftime("%Y-%m-%d %H:%M:%S")

        if m.role == "assistant" or m.role == "system":
            role = f"[bright_cyan][bold]{m.role}[/bold][/bright_cyan]: "
            content = f"[cyan]{m.content}[/cyan]"
        elif m.role == "user":
            role = f"[bright_yellow][bold]{m.role}[/bold][/bright_yellow]: "
            content = f"{m.content}"

        console.print(
            f"[bright_black][{timestamp}][/bright_black] " + role + content,
        )

    @staticmethod
    def user_input(message_id: int) -> Message:
        user_input = console.input(r"[yellow][bold]user[/bold][/yellow]: ")

        # move cursor up 1 line
        sys.stdout.write(f"\x1b[1A")
        # clear line
        sys.stdout.write("\r\x1b[0K")

        return Message(
            id=message_id,
            role="user",
            created_at=datetime.now(),
            content=user_input,
        )

    def run(self):
        print(f"Starting conversation: {self.conversation.name}")

        existing_messages = self.query_history(n=50)
        if not existing_messages:
            m = self._save_message(
                Message(
                    id=0,
                    role="assistant",
                    content=(
                        "Hello world! I'm here to help you with any questions or problems. "
                        "What's on your mind right now?"
                    ),
                    conversation_id=self.conversation.id,
                )
            )
            existing_messages.append(m)

        for m in existing_messages:
            self.pprint_message(m)

        message_id = existing_messages[-1].id + 1
        history = [m.content for m in existing_messages]

        try:
            while True:
                answer = self.turn(message_id, history)
                message_id += answer.id + 1

                if len(history) > self.history_threshold:
                    summary = self.summarize_history(
                        message_id, history[: self.summary_length]
                    )
                    self._save_message(summary)
                    self.pprint_message(summary)

                    residual_length = self.history_threshold - self.summary_length

                    history = (
                        history[:residual_length]
                        + [summary]
                        + history[self.summary_length :]
                    )
                    message_id += answer.id + 1

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
        except Exception as e:
            raise e
