from typing import List
import os
import traceback

from dotenv import load_dotenv
import dspy
from dspy.retrieve.chromadb_rm import ChromadbRM
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction


class QAAgent:

    def __init__(self):
        load_dotenv()

        self._init_lm()
        self._init_embed_retriever()

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
        client = chromadb.Client(
            Settings(
                persist_directory="chroma",
                is_persistent=True,
            )
        )
        self.embed_coll = client.get_or_create_collection("embedding")

    def _init_db(self):
        pass

    def _create_context(self, message: str):
        """retrieve user context"""
        return "You're a helpful, professional therapist. You care about people's feeling and know what to ask when they are feeling ok. Your first question is usually: how are you doing and how can I help you today?"

    def _save_message(self, message: str):
        """save the conversation in the dbs"""
        pass

    def turn(self, history: List[str], message: str):
        lm_ctx = self._create_context(message)

        # call predict
        try:
            resp = self.lm(context=lm_ctx, history=history, message=message)
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise(e)

        # save info
        self._save_message(message)
        return resp.answer

    def run(self):
        history = []
        try:
            while True:
                message = input(r"User: ")
                history.append(message)

                answer = self.turn(history, message)

                print("Assistant: ", answer)
                history.append(answer)

        except KeyboardInterrupt:
            print("\nGoodbye!")


if __name__ == "__main__":
    agent = QAAgent()

    agent.run()
