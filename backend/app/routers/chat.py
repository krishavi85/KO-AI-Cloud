import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_api_key
from app.models import APIKey, Conversation, Message, UsageLog
from app.schemas import ChatCompletionRequest
from app.services.gpu_router import distributed_chat
from app.services.model_router import route_model
from app.services.ollama_client import chat, stream_chat
from app.services.rag import inject_rag
from app.services.token_shield import compress_messages, output_limit

router = APIRouter(prefix="/v1", tags=["chat"])


def persist_user_messages(db: Session, user_id: int, session_id: str, messages):
    existing = db.query(Conversation).filter(Conversation.user_id == user_id, Conversation.session_id == session_id).first()
    if not existing:
        db.add(Conversation(user_id=user_id, session_id=session_id, title="Conversation"))
    for m in messages:
        db.add(Message(user_id=user_id, session_id=session_id, role=m.role, content=m.content))


def normalize(messages):
    return [{"role": m.role, "content": m.content} for m in messages]


@router.post("/chat/completions")
def chat_completions(payload: ChatCompletionRequest, api_key: APIKey = Depends(get_api_key), db: Session = Depends(get_db)):
    session_id = payload.session_id or "default"
    latest_prompt = next((m.content for m in reversed(payload.messages) if m.role == "user"), "")
    route = route_model(payload.model, latest_prompt)
    messages = payload.messages
    rag_count = 0

    if payload.use_rag:
        messages, rag_count = inject_rag(messages, api_key.user_id)

    messages, compressed = compress_messages(messages)
    max_tokens = output_limit(payload.max_tokens)
    normalized = normalize(messages)

    routed_response = distributed_chat({"model": route["model"], "messages": normalized, "max_tokens": max_tokens})
    response_text = routed_response or chat(route["model"], normalized, max_tokens)

    persist_user_messages(db, api_key.user_id, session_id, payload.messages)
    db.add(Message(user_id=api_key.user_id, session_id=session_id, role="assistant", content=response_text))
    db.add(UsageLog(user_id=api_key.user_id, api_key_id=api_key.id, model=route["model"], route=route["route"], prompt_chars=sum(len(m.content) for m in payload.messages), completion_chars=len(response_text), status="success"))
    api_key.last_used_at = datetime.now(timezone.utc)
    db.commit()

    return {"model": route["model"], "route": route["route"], "response": response_text, "compressed": compressed, "rag_chunks": rag_count}


@router.post("/chat/stream")
def chat_stream(payload: ChatCompletionRequest, api_key: APIKey = Depends(get_api_key), db: Session = Depends(get_db)):
    session_id = payload.session_id or "default"
    latest_prompt = next((m.content for m in reversed(payload.messages) if m.role == "user"), "")
    route = route_model(payload.model, latest_prompt)
    messages = payload.messages
    rag_count = 0

    if payload.use_rag:
        messages, rag_count = inject_rag(messages, api_key.user_id)

    messages, compressed = compress_messages(messages)
    max_tokens = output_limit(payload.max_tokens)
    normalized = normalize(messages)

    def event_stream():
        full = ""
        meta = {"model": route["model"], "route": route["route"], "compressed": compressed, "rag_chunks": rag_count}
        yield "event: meta\ndata: " + json.dumps(meta) + "\n\n"
        for token in stream_chat(route["model"], normalized, max_tokens):
            full += token
            yield "data: " + json.dumps({"token": token}) + "\n\n"
        persist_user_messages(db, api_key.user_id, session_id, payload.messages)
        db.add(Message(user_id=api_key.user_id, session_id=session_id, role="assistant", content=full))
        db.add(UsageLog(user_id=api_key.user_id, api_key_id=api_key.id, model=route["model"], route=route["route"], prompt_chars=sum(len(m.content) for m in payload.messages), completion_chars=len(full), status="success"))
        api_key.last_used_at = datetime.now(timezone.utc)
        db.commit()
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
