"""
Memory implements a very simple memory interface for persist conversation,
including saving, retrieving information, and summarizing memory
so as to save context.

It saves information in the SQL db and embedding db, for persistence
and for relevance retrieval.
"""

from typing import List
import os
from pathlib import Path

import dspy
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from therapist.models import init_session, Message, Conversation


class Memory:
    """
    Memory saves the conversation in
    It saves:

    - A short term memory: a list of message in the conversation, you can
      query by listing the latest memory, or retrieve by embedding similarity.
    - A long term memory: LM summarized view of the messages.
    """

    def __init__(
        self,
        persistence_path: str,
        short_term_limit: int = 30,
    ):
        self.persistence_path = persistence_path

        os.makedirs(persistence_path, exist_ok=True)

        self._init_db_session(f"sqlite:///{persistence_path}/database.db")
        self._init_embed_retriever(f"{persistence_path}/chroma/")

        self.summarizer = dspy.Predict(
            "messages: list -> summary: str",
            instructions=(
                "Summarize the conversation history, "
                "keep all the key information and focus on the user characteristics. "
                "And list the conversation highlights in bullet points."
            ),
        )

        self.conversation = self._init_conversation()
        self.short_term = []
        self.short_term_limit = short_term_limit

        assert self.short_term_limit > 0

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

    def _init_db_session(self, path: str | Path):
        self._session = init_session(path)

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

    def save(self, message: Message):
        """
        Add a message to the memory.
        """
        message.conversation_id = self.conversation.id

        try:
            # saves in DB
            self._session.add(message)
            self._session.flush()

            # saves in embedding
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

            self._session.commit()
        except Exception as e:
            self._session.rollback()
            self.embed_coll.delete(ids=[str(message.id)])
            raise e

        return message

    def get(self, limit: int = 50, is_summary: bool = False) -> list[Message]:
        """
        Retrieve all messages from the memory.
        """
        messages = (
            self._session.query(Message)
            .where(
                Message.conversation_id == self.conversation.id,
                Message.is_summary == is_summary,
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(messages))

    def summarize(self, messages: List[Message]) -> Message:
        """
        Summarize the messages from the memory.
        """
        content = self.summarizer(messages=[m.content for m in messages])
        return Message(
            role="memory",
            content=content.summary,
            is_summary=True,
        )

    def get_long_term(self, limit: int = 10):
        return self.get(limit=limit, is_summary=True)

    def retrieve(self, query: str, limit: int = 5, threshold: float = 0.6) -> List[str]:
        retrieved = self.embed_coll.query(
            query_embeddings=self.embedding([query]),
            n_results=limit,
            include=["metadatas", "documents", "distances"],
        )
        # Filter by distance (assuming lower distance is better)
        results = []
        for doc, distance, metadata in zip(
            retrieved["documents"][0],
            retrieved["distances"][0],
            retrieved["metadatas"][0],
        ):
            if distance < threshold:
                results.append(f'{metadata.get("time")} {metadata["role"]}: {doc}')

        return results
