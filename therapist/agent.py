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
        """ query the last 20 history in reverse order
        """
        messages = (
            self._session.query(Message)
            .where(Message.conversation_id == self.conversation.id)
            .order_by(Message.created_at.desc())
            .limit(n)
            .all()
        )

        return messages

    def summarize_history(self, history: List[str]) -> Message:
        pass

    def _create_context(self, message: str) -> str:
        """retrieve user context"""
        return """You're a helpful, professional therapist.
You care about people's feeling and know what to ask when they are feeling ok.
Your first question is usually: how are you doing and how can I help you today?"""

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
        self._save_message(message)

        # call predict
        lm_ctx = self._create_context(message)
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

        if m.role == "assistant":
            role = f"[bright_cyan][bold]{m.role}[/bold][/bright_cyan]: "
            content = f"[cyan]{m.content}[/cyan]"
        elif m.role == "user":
            role = f"[bright_yellow][bold]{m.role}[/bold][/bright_yellow]: "
            content = f"{m.content}"

        console.print(
            f"[bright_black][{timestamp}][/bright_black] " + role + content,
        )

    @staticmethod
    def user_input(message_id: int) -> str:
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
            existing_messages.append(
                Message(
                    id=0,
                    role="assistant",
                    content="Hello world! I'm happy to help you with any questions or problems",
                    conversation_id=self.conversation.id,
                )
            )

        for m in reversed(existing_messages):
            self.pprint_message(m)

        message_id = existing_messages[0].id + 1
        history = [m.content for m in existing_messages]
        try:
            while True:
                answer = self.turn(message_id, history)
                message_id += answer.id + 1

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
        except Exception as e:
            raise e
