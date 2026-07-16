from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------
# Create User
# ---------------------------------------
class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


# ---------------------------------------
# Login User
# ---------------------------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------------------------------------
# User Response
# ---------------------------------------
class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------
# JWT Token
# ---------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------
# JWT Payload
# ---------------------------------------
class TokenPayload(BaseModel):
    sub: str