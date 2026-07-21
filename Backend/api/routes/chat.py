from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.database import get_db
from models.chat import Chat
from models.user import User
from schemas.chat import ChatRequest, ChatResponse
from agents.graph import workflow

router = APIRouter(prefix="/chat", tags=["Agent Chat"])


@router.post("/", response_model=ChatResponse)
def chat_with_agent(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Query the Multi-Agent Research System. Runs Planner -> Research -> Web -> Memory -> Citation -> Critic.
    """
    try:
        res = workflow.run(
            question=req.question,
            user_id=str(current_user.id),
            document_id=str(req.document_id) if req.document_id else None,
            db=db,
        )

        # Save to Chat history in database
        chat_record = Chat(
            user_id=str(current_user.id),
            document_id=str(req.document_id) if req.document_id else None,
            user_message=req.question,
            assistant_response=res["answer"],
            citations="; ".join(res.get("citations", []))
        )
        db.add(chat_record)
        db.commit()

        return ChatResponse(
            answer=res["answer"],
            citations=res.get("citations", []),
            sources=[s.get("filename") or s.get("title", "") for s in res.get("sources", [])]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow error: {str(e)}")
