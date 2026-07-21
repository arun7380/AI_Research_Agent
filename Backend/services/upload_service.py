import os
from pathlib import Path
from typing import List

from fastapi import UploadFile
from sqlalchemy.orm import Session

from config.settings import settings
from models.document import Document
from models.user import User
from rag.chunker import TextChunker
from rag.parser import DocumentParser
from rag.vector_store import VectorStore
from utils.helpers import generate_unique_filename, get_file_extension


def process_and_save_upload(file: UploadFile, user: User, db: Session) -> Document:
    """
    Saves uploaded file to disk, parses text/OCR, chunks text, embeds chunks into vector store, and saves document record to DB.
    """
    upload_dir = Path(settings.BASE_DIR) / settings.UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_name = generate_unique_filename(file.filename)
    dest_path = upload_dir / unique_name

    # Save file to disk
    contents = file.file.read()
    dest_path.write_bytes(contents)

    file_ext = get_file_extension(file.filename).lstrip(".")

    # Step 1: Parse Text
    parsed = DocumentParser.parse(str(dest_path))
    extracted_text = parsed.get("text", "")
    pages = parsed.get("pages", [])

    # Step 2: Create DB Record
    doc_record = Document(
        user_id=user.id,
        filename=file.filename,
        file_type=file_ext,
        file_path=str(dest_path.resolve()),
        file_size=len(contents),
        extracted_text=extracted_text,
        total_chunks=0,
        embedding_model=settings.EMBEDDING_MODEL,
        vector_store=settings.VECTOR_DB,
    )

    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Step 3: Chunk text
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.chunk_document(
        text=extracted_text,
        document_id=str(doc_record.id),
        filename=file.filename,
        pages=pages,
    )

    # Step 4: Index into VectorStore
    vstore = VectorStore()
    vstore.add_chunks(chunks)

    # Update DB record with total chunks
    doc_record.total_chunks = len(chunks)
    db.commit()
    db.refresh(doc_record)

    return doc_record


def get_user_documents(user_id: str, db: Session) -> List[Document]:
    """
    Retrieve all uploaded documents for a user.
    """
    return db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).all()


def get_document_by_id(document_id: str, db: Session) -> Document:
    """
    Retrieve single document record.
    """
    return db.query(Document).filter(Document.id == document_id).first()
