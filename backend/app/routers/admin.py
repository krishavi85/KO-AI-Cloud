from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import APIKey, Document, Message, UsageLog, User

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")


@router.get("/analytics")
def analytics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(user)
    latest_usage = db.query(UsageLog).order_by(UsageLog.created_at.desc()).limit(20).all()
    return {
        "users": db.query(User).count(),
        "api_keys": db.query(APIKey).count(),
        "documents": db.query(Document).count(),
        "messages": db.query(Message).count(),
        "requests": db.query(UsageLog).count(),
        "latest_usage": [
            {
                "id": u.id,
                "user_id": u.user_id,
                "model": u.model,
                "route": u.route,
                "prompt_chars": u.prompt_chars,
                "completion_chars": u.completion_chars,
                "status": u.status,
                "created_at": u.created_at,
            }
            for u in latest_usage
        ],
    }
