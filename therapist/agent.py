from typing import List
import os
import traceback
from datetime import datetime
import uuid

from dotenv import load_dotenv
import dspy
from dspy.retrieve.chromadb_rm import ChromadbRM
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
# from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

from models import Conversation, Message, init_session

class QAAgent:

    def __init__(self):
        load_dotenv()

        self._init_lm()
        self._init_embed_retriever()

        self._session = init_session()

        self.message_id = 0
        self.conversation_id = str(uuid.uuid4())

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
            model=os.getenv("EMBED_MODEL_NAME"),
        )

        client = chromadb.Client(
            Settings(
                persist_directory="chroma",
                is_persistent=True,
            )
        )
        self.embed_coll = client.get_or_create_collection("embedding")

    def _create_context(self, message: str):
        """retrieve user context"""
        return """You're a helpful, professional therapist.
You care about people's feeling and know what to ask when they are feeling ok.
Your first question is usually: how are you doing and how can I help you today?"""

    def _read_history(self, message: str):
        pass

    def summarize_history(self, history: List[str]):
        pass

    def _save_message(self, role: str, message: str, **kwargs):
        """save the conversation in the dbs"""

        try:
            self.embed_coll.add(
                ids=[str(self.message_id)],
                metadatas=[{'conversation_id': self.conversation_id, 'role': role}],
                documents=[message],
                embeddings=self.embedding(message),
            )

            self._session.add(
                Message(
                    id=self.message_id,
                    content=message,
                    created_at=datetime.now(),
                    conversation_id=self.conversation_id,
            ))
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e

        self.message_id += 1

    def turn(self, history: List[str], message: str):
        lm_ctx = self._create_context(message)

        # save info
        self._save_message('user', message)

        # call predict
        try:
            resp = self.lm(context=lm_ctx, history=history, message=message)
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise(e)

        self._save_message('assistant', resp.answer)
        return resp.answer

    def run(self):
        history = []
        try:
            while True:
                message = input(r"User: ")
                answer = self.turn(history, message)
                history.append(message)

                print("Assistant: ", answer)
                history.append(answer)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
        except Exception as e:
            raise e