from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------
# Chat Request
# ---------------------------------------
class ChatRequest(BaseModel):
    document_id: UUID | None = None

    question: str


# ---------------------------------------
# Chat Response
# ---------------------------------------
class ChatResponse(BaseModel):
    answer: str

    citations: list[str] = []

    sources: list[str] = []


# ---------------------------------------
# Chat History
# ---------------------------------------
class ChatHistoryResponse(BaseModel):
    id: UUID

    user_id: UUID

    document_id: UUID | None = None

    user_message: str

    assistant_response: str

    citations: str | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)