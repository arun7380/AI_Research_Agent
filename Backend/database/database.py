import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings

logger = logging.getLogger(__name__)

# Primary & Fallback Engine Setup
db_url = settings.DATABASE_URL

try:
    if db_url.startswith("sqlite"):
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )
    else:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.DEBUG,
        )
        # Verify connection
        with engine.connect() as conn:
            pass
except Exception as e:
    logger.warning(f"Could not connect to {db_url} ({e}). Falling back to SQLite database.")
    sqlite_fallback_url = "sqlite:///./ai_research.db"
    engine = create_engine(
        sqlite_fallback_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )

### Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

### Base Class
Base = declarative_base()


### Dependency for FastAPI
def get_db():
    """
    Creates a new database session for each request
    and closes it automatically.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()