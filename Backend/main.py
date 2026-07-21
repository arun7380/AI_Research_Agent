import os
import sys
from pathlib import Path

# Ensure Backend directory is in sys.path for top-level module resolution
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
FRONTEND_DIR = BASE_DIR / "Frontend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import auth, chat, report, slides, upload
from config.settings import settings
from database.database import engine, Base
from websocket import chat_ws

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("ai_research_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for table creation on startup.
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete.")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced AI Research Agent with Multi-Agent Workflow, RAG, and Citation Systems",
    lifespan=lifespan,
)

# Robust CORS Setup allowing file:// protocol (null origin) and dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "null",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")
app.include_router(slides.router, prefix="/api/v1")
app.include_router(chat_ws.router)

# Mount Frontend static dashboard at /app
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "frontend_url": "http://localhost:8000/app",
        "docs_url": "http://localhost:8000/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
