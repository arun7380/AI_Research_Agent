from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.database import get_db
from models.user import User
from services.report_service import generate_research_report

router = APIRouter(prefix="/reports", tags=["Research Reports"])


@router.post("/generate")
def generate_report(
    topic: str,
    document_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an academic markdown research report using the multi-agent framework.
    """
    try:
        report = generate_research_report(
            topic=topic,
            document_id=document_id,
            user_id=str(current_user.id),
            db=db
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
