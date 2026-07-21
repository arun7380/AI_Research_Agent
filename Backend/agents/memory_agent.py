from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.chat import Chat


class MemoryAgent:
    """
    Retrieves and summarizes past chat history for conversational context.
    """

    def get_context(self, user_id: str, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        if not db or not user_id:
            return []

        history = (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
            .limit(limit)
            .all()
        )

        chats = []
        for chat in reversed(history):
            chats.append({
                "user_message": chat.user_message,
                "assistant_response": chat.assistant_response,
            })

        return chats
