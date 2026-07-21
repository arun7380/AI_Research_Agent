from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.database import get_db
from models.user import User
from services.slide_service import generate_presentation_slides

router = APIRouter(prefix="/slides", tags=["Presentation Slides"])


@router.post("/generate")
def generate_slides(
    topic: str,
    document_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate presentation slides JSON deck using the multi-agent framework.
    """
    try:
        slide_deck = generate_presentation_slides(
            topic=topic,
            document_id=document_id,
            user_id=str(current_user.id),
            db=db
        )
        return slide_deck
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation slides: {str(e)}")
