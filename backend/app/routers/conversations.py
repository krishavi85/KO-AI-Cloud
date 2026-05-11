from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Conversation, Message, User

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationCreate(BaseModel):
    title: str = "New conversation"


class ConversationRename(BaseModel):
    title: str


@router.post("")
def create_conversation(payload: ConversationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session_id = f"session-{user.id}-{db.query(Conversation).filter(Conversation.user_id == user.id).count() + 1}"
    conversation = Conversation(user_id=user.id, session_id=session_id, title=payload.title[:255])
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return {"id": conversation.id, "session_id": conversation.session_id, "title": conversation.title}


@router.get("")
def list_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc()).all()
    return [
        {
            "id": item.id,
            "session_id": item.session_id,
            "title": item.title,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        for item in items
    ]


@router.get("/{session_id}/messages")
def list_messages(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.session_id == session_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = db.query(Message).filter(Message.user_id == user.id, Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]


@router.patch("/{session_id}")
def rename_conversation(session_id: str, payload: ConversationRename, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.session_id == session_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation.title = payload.title[:255]
    db.commit()
    return {"session_id": conversation.session_id, "title": conversation.title}


@router.delete("/{session_id}")
def delete_conversation(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.session_id == session_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.query(Message).filter(Message.user_id == user.id, Message.session_id == session_id).delete()
    db.delete(conversation)
    db.commit()
    return {"deleted": True, "session_id": session_id}
