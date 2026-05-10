from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, RegisterRequest
from app.security import create_jwt, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def resolve_role(email: str, user_count: int) -> str:
    normalized_email = email.strip().lower()
    if normalized_email == settings.ADMIN_EMAIL.strip().lower():
        return "admin"
    return "admin" if user_count == 0 else "user"


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    normalized_email = payload.email.strip().lower()
    if db.query(User).filter(User.email == normalized_email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        role=resolve_role(normalized_email, db.query(User).count()),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "registered", "user_id": user.id, "role": user.role}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    normalized_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login")

    correct_role = resolve_role(user.email, db.query(User).count())
    if user.role != correct_role:
        user.role = correct_role
        db.commit()
        db.refresh(user)

    return {"access_token": create_jwt(user.id, user.role), "token_type": "bearer", "role": user.role}
