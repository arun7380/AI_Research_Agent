from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------
# Upload Response
# ---------------------------------------
class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_size: int


# ---------------------------------------
# Document Response
# ---------------------------------------
class DocumentResponse(BaseModel):
    id: UUID

    user_id: UUID

    filename: str

    file_type: str

    file_path: str

    file_size: int

    total_chunks: int

    embedding_model: str | None = None

    vector_store: str | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)