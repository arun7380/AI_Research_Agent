from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.database import get_db
from models.user import User
from schemas.document import DocumentResponse
from services.upload_service import process_and_save_upload, get_user_documents, get_document_by_id
from utils.helpers import is_allowed_file

router = APIRouter(prefix="/documents", tags=["Document Upload"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document (PDF, DOCX, TXT) for ingestion into the RAG vector pipeline.
    """
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension not supported. Please upload PDF, DOCX, or TXT.",
        )

    try:
        doc = process_and_save_upload(file=file, user=current_user, db=db)
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document upload: {str(e)}",
        )


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all uploaded documents for current user.
    """
    return get_user_documents(user_id=str(current_user.id), db=db)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get metadata for a specific document by ID.
    """
    doc = get_document_by_id(document_id=document_id, db=db)
    if not doc or str(doc.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
