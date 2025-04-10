from typing import List
import os
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

from models import Conversation, Message, init_session


console = Console()


class ChatBot:

    def __init__(self):
        load_dotenv()

        self._init_lm()
        self._init_embed_retriever()

        self._session = init_session()

        self.conversation = self._init_conversation()

    def _init_lm(self):
        lm = dspy.LM(
            api_base=os.getenv("LM_BASE_URL"),
            api_key=os.getenv("LM_API_KEY"),
            model=os.getenv("LM_MODEL_NAME"),
        )
        dspy.configure(lm=lm)

        self.lm = dspy.ChainOfThought(
            "context, history, message -> answer",
        )

    def _init_embed_retriever(self):
        self.embedding = embedding = OpenAIEmbeddingFunction(
            api_base=os.getenv("LM_BASE_URL"),
            api_key=os.getenv("LM_API_KEY"),
            model_name=os.getenv("EMBED_MODEL_NAME"),
        )

        client = chromadb.Client(
            Settings(
                persist_directory="chroma",
                is_persistent=True,
            )
        )
        self.embedding_model = os.getenv("EMBED_MODEL_NAME")
        self.embed_coll = client.get_or_create_collection("embedding")

    def _init_conversation(self):
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

    def query_history(self, n=20):
        messages = (
            self._session.query(Message)
            .where(Message.conversation_id == self.conversation.id)
            .order_by(Message.created_at.desc())
            .limit(n)
            .all()
        )

        return messages

    def _create_context(self, message: str):
        """retrieve user context"""
        return """You're a helpful, professional therapist.
You care about people's feeling and know what to ask when they are feeling ok.
Your first question is usually: how are you doing and how can I help you today?"""

    def _read_history(self, message: str):
        pass

    def summarize_history(self, history: List[str]):
        pass

    def _save_message(self, message: Message, **kwargs):
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
            raise e

        return message

    def turn(self, history: List[str], message: Message):
        lm_ctx = self._create_context(message)

        # save info
        self._save_message(message)

        # call predict
        try:
            resp = self.lm(context=lm_ctx, history=history, message=message.content)
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise (e)

        resp = Message(role="assistant", content=resp.answer, id=message.id + 1)
        self._save_message(resp)
        return resp

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
    def user_input() -> str:
        user_input = console.input(r"[yellow][bold]user[/bold][/yellow]: ")

        # move cursor up 1 line
        sys.stdout.write(f'\x1b[1A')
        # clear line
        sys.stdout.write('\r\x1b[0K')

        return user_input

    def run(self):
        print(f"Starting conversation: {self.conversation.name}")

        existing_messages = self.query_history(n=50)
        message_id = 0
        if existing_messages:
            message_id = existing_messages[0].id + 1

        for m in reversed(existing_messages):
            self.pprint_message(m)

        history = [m.content for m in existing_messages]
        try:
            while True:
                user_input = self.user_input()
                message = Message(
                    role="user",
                    created_at=datetime.now(),
                    content=user_input,
                    id=message_id,
                )
                history.append(message.content)

                self.pprint_message(message)

                answer = self.turn(history, message)
                history.append(answer.content)

                self.pprint_message(answer)
                message_id = answer.id + 1

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
        except Exception as e:
            raise e
