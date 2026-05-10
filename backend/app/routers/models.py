from fastapi import APIRouter
from app.services.model_router import route_model
from app.services.ollama_client import list_models

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
def models():
    return {"models": list_models()}


@router.get("/route")
def route(prompt: str, model: str | None = None):
    return route_model(model, prompt)
