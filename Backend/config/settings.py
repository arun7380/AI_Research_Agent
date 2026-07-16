from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


### Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application Settings
    Values are loaded from .env file if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
### Application

    APP_NAME: str = "AI Research Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000
### Security

    SECRET_KEY: str = Field(..., description="JWT Secret Key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
### Database

    DATABASE_URL: str
### Redis

    REDIS_URL: str = "redis://localhost:6379"
### File Upload

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 100
### Vector Database

    VECTOR_DB: str = "faiss"       # faiss | qdrant | pinecone
    FAISS_INDEX_PATH: str = "vector_store/faiss.index"

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "documents"
### Embedding Model

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
### API Keys

    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    DEFAULT_LLM: str = "gemini"
### OCR

    TESSERACT_CMD: str | None = None
### Logging

    LOG_LEVEL: str = "INFO"
### CORS

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()

settings = get_settings()