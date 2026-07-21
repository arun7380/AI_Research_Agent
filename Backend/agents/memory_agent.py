from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.chat import Chat


class MemoryAgent:
    """
    Retrieves and filters past chat history for conversational context.
    Prevents context leakage when generating standalone reports, slides, or document analyses.
    """

    def get_context(
        self,
        user_id: str,
        db: Session,
        query: str = "",
        document_id: str = None,
        mode: str = "research",
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        # Exclude memory context during report generation, slide deck creation, or explicit document analysis
        if not db or not user_id or mode in ["report", "slides"] or document_id:
            return []

        history = (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
            .limit(limit)
            .all()
        )

        chats = []
        query_words = set(query.lower().split()) if query else set()

        for chat in reversed(history):
            # If query is provided, verify at least some keyword relevance to avoid mixing unrelated topics
            if query_words:
                user_msg_lower = (chat.user_message or "").lower()
                if not any(w in user_msg_lower for w in query_words if len(w) > 3):
                    continue

            chats.append({
                "user_message": chat.user_message,
                "assistant_response": chat.assistant_response,
            })

        return chats

