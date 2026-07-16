import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class Chat(Base):
    __tablename__ = "chat_history"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    document_id = Column(
        String(36),
        ForeignKey("documents.id"),
        nullable=True
    )

    user_message = Column(
        Text,
        nullable=False
    )

    assistant_response = Column(
        Text,
        nullable=False
    )

    citations = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        backref="chat_history"
    )

    document = relationship(
        "Document",
        backref="chat_history"
    )