from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import APIKey, UsageLog, User
from app.schemas import APIKeyCreateRequest
from app.security import generate_api_key

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("")
def create_key(payload: APIKeyCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    raw_value, hashed_value, prefix = generate_api_key()
    record = APIKey(user_id=user.id, name=payload.name, key_hash=hashed_value, key_prefix=prefix)
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "key": raw_value, "warning": "Save this value now. It will not be shown again."}


@router.get("")
def list_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(APIKey).filter(APIKey.user_id == user.id).order_by(APIKey.created_at.desc()).all()
    return [
        {
            "id": key.id,
            "name": key.name,
            "prefix": key.key_prefix,
            "active": key.is_active,
            "created_at": key.created_at,
            "last_used_at": key.last_used_at,
        }
        for key in keys
    ]


@router.get("/{item_id}/usage")
def key_usage(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(APIKey).filter(APIKey.id == item_id, APIKey.user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Developer credential not found")

    logs = db.query(UsageLog).filter(UsageLog.api_key_id == record.id).order_by(UsageLog.created_at.desc()).limit(100).all()
    return {
        "id": record.id,
        "name": record.name,
        "active": record.is_active,
        "requests": len(logs),
        "prompt_chars": sum(item.prompt_chars for item in logs),
        "completion_chars": sum(item.completion_chars for item in logs),
        "latest": [
            {
                "id": item.id,
                "model": item.model,
                "route": item.route,
                "prompt_chars": item.prompt_chars,
                "completion_chars": item.completion_chars,
                "status": item.status,
                "created_at": item.created_at,
            }
            for item in logs
        ],
    }


@router.delete("/{item_id}")
def revoke_key(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(APIKey).filter(APIKey.id == item_id, APIKey.user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Developer credential not found")
    record.is_active = False
    db.commit()
    return {"revoked": True, "id": record.id}
