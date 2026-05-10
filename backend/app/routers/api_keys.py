from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import APIKey, User
from app.schemas import APIKeyCreateRequest
from app.security import generate_api_key

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("")
def create_key(payload: APIKeyCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    raw, key_hash, prefix = generate_api_key()
    record = APIKey(user_id=user.id, name=payload.name, key_hash=key_hash, key_prefix=prefix)
    db.add(record)
    db.commit()
    return {"key": raw, "warning": "Save this key now. It will not be shown again."}


@router.get("")
def list_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
    return [{"id": k.id, "name": k.name, "prefix": k.key_prefix, "active": k.is_active, "created_at": k.created_at} for k in keys]
