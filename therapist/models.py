from typing import Dict, List
from datetime import datetime
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import Mapped, mapped_column


Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    messages: Mapped[List["Message"]] = relationship('Message', back_populates='conversation')


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_summary: Mapped[bool] = mapped_column(Boolean, default=False)

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey('conversations.id'))

    conversation: Mapped[Conversation] = relationship(back_populates='messages')

    def __str__(self):
        return f'[{self.created_at}] {self.role}: {self.content}'

    def __repr__(self):
        return self.__str__()


def init_session():
    engine = create_engine('sqlite:///database.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    return Session()
