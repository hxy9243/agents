"""
Memory implements a very simple memory interface for persist conversation,
including saving, retrieving information, and summarizing memory
so as to save context.

It saves information in the SQL db and embedding db, for persistence
and for relevance retrieval.

It saves:

- A short term memory (a list of message in the conversation),
- A long term memory (LM summarized view of the messages).
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
    def __init__(
        self,
        persistence_path: str,
    ):
        self.persistence_path = persistence_path

        self._init_db_session(f"sqlite:///{persistence_path}/database.db")
        self._init_embed_retriever(f"{persistence_path}/chroma/")

        self.summarizer = dspy.Predict(
            "history: list -> summary: str",
            instructions=(
                "Summarize the conversation history, "
                "keep all the key information and focus on the user characteristics"
            ),
        )

        self.conversation = self._init_conversation()

    def _init_conversation(self) -> Conversation:
        conversation = (
            self._session
            .query(Conversation)
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

    def summarize(self, history: List[str]) -> Message:
        return self.summarizer(history=history)

    def retrieve(
        self, query: str, limit: int = 5, threshold: float = 0.6
    ) -> List[str]:

        retrieved = self.embed_coll.query(
            query_embeddings=self.embedding([query]),
            n_results=5,
            include=["metadatas", "documents", "distances"]
        )
        # Filter by distance (assuming lower distance is better)
        results = []
        for doc, distance, metadata in zip(retrieved['documents'][0], retrieved['distances'][0], retrieved['metadatas'][0]):
            if distance < self.distance_threshold:
                results.append(f'{metadata.get("time")} {metadata["role"]}: {doc}')

        return results
