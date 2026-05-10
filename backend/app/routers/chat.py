import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
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
    existing = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.session_id == session_id,
    ).first()
    if not existing:
        db.add(Conversation(user_id=user_id, session_id=session_id, title="Conversation"))
    for message in messages:
        db.add(Message(user_id=user_id, session_id=session_id, role=message.role, content=message.content))


def normalize(messages):
    return [{"role": message.role, "content": message.content} for message in messages]


def save_error(db: Session, api_key: APIKey, model: str, route: str, prompt_chars: int):
    db.add(
        UsageLog(
            user_id=api_key.user_id,
            api_key_id=api_key.id,
            model=model,
            route=route,
            prompt_chars=prompt_chars,
            completion_chars=0,
            status="error",
        )
    )
    db.commit()


@router.post("/chat/completions")
def chat_completions(
    payload: ChatCompletionRequest,
    api_key: APIKey = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    session_id = payload.session_id or "default"
    latest_prompt = next((message.content for message in reversed(payload.messages) if message.role == "user"), "")
    selected = route_model(payload.model, latest_prompt)
    messages = payload.messages
    rag_count = 0

    if payload.use_rag:
        messages, rag_count = inject_rag(messages, api_key.user_id)

    messages, compressed = compress_messages(messages)
    max_tokens = output_limit(payload.max_tokens)
    normalized = normalize(messages)
    prompt_chars = sum(len(message.content) for message in payload.messages)

    try:
        routed_response = distributed_chat({"model": selected["model"], "messages": normalized, "max_tokens": max_tokens})
        response_text = routed_response or chat(selected["model"], normalized, max_tokens)
    except Exception as exc:
        save_error(db, api_key, selected["model"], selected["route"], prompt_chars)
        raise HTTPException(status_code=502, detail=f"Local model request failed: {exc}") from exc

    persist_user_messages(db, api_key.user_id, session_id, payload.messages)
    db.add(Message(user_id=api_key.user_id, session_id=session_id, role="assistant", content=response_text))
    db.add(
        UsageLog(
            user_id=api_key.user_id,
            api_key_id=api_key.id,
            model=selected["model"],
            route=selected["route"],
            prompt_chars=prompt_chars,
            completion_chars=len(response_text),
            status="success",
        )
    )
    api_key.last_used_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "model": selected["model"],
        "route": selected["route"],
        "response": response_text,
        "compressed": compressed,
        "rag_chunks": rag_count,
    }


@router.post("/chat/stream")
def chat_stream(payload: ChatCompletionRequest, api_key: APIKey = Depends(get_api_key)):
    session_id = payload.session_id or "default"
    latest_prompt = next((message.content for message in reversed(payload.messages) if message.role == "user"), "")
    selected = route_model(payload.model, latest_prompt)
    messages = payload.messages
    rag_count = 0

    if payload.use_rag:
        messages, rag_count = inject_rag(messages, api_key.user_id)

    messages, compressed = compress_messages(messages)
    max_tokens = output_limit(payload.max_tokens)
    normalized = normalize(messages)
    prompt_chars = sum(len(message.content) for message in payload.messages)

    def event_stream():
        full_response = ""
        meta = {
            "model": selected["model"],
            "route": selected["route"],
            "compressed": compressed,
            "rag_chunks": rag_count,
        }
        yield "event: meta\ndata: " + json.dumps(meta) + "\n\n"

        try:
            for token in stream_chat(selected["model"], normalized, max_tokens):
                full_response += token
                yield "data: " + json.dumps({"token": token}) + "\n\n"

            db = SessionLocal()
            try:
                db_api_key = db.query(APIKey).filter(APIKey.id == api_key.id).first()
                if db_api_key:
                    persist_user_messages(db, db_api_key.user_id, session_id, payload.messages)
                    db.add(Message(user_id=db_api_key.user_id, session_id=session_id, role="assistant", content=full_response))
                    db.add(
                        UsageLog(
                            user_id=db_api_key.user_id,
                            api_key_id=db_api_key.id,
                            model=selected["model"],
                            route=selected["route"],
                            prompt_chars=prompt_chars,
                            completion_chars=len(full_response),
                            status="success",
                        )
                    )
                    db_api_key.last_used_at = datetime.now(timezone.utc)
                    db.commit()
            finally:
                db.close()

            yield "event: done\ndata: {}\n\n"
        except Exception as exc:
            yield "event: error\ndata: " + json.dumps({"detail": str(exc)}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
