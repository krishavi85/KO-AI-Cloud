import json
import requests
from typing import Iterable
from app.config import settings


def chat(model: str, messages: list, max_tokens: int) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }
    response = requests.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload, timeout=300)
    response.raise_for_status()
    return response.json().get("message", {}).get("content", "")


def stream_chat(model: str, messages: list, max_tokens: int) -> Iterable[str]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"num_predict": max_tokens},
    }
    with requests.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload, stream=True, timeout=300) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))
            token = data.get("message", {}).get("content", "")
            if token:
                yield token
            if data.get("done"):
                break


def embed(text: str, model: str | None = None) -> list[float]:
    payload = {"model": model or settings.DEFAULT_EMBED_MODEL, "prompt": text}
    response = requests.post(f"{settings.OLLAMA_BASE_URL}/api/embeddings", json=payload, timeout=120)
    response.raise_for_status()
    return response.json().get("embedding", [])


def list_models() -> list[str]:
    response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=30)
    response.raise_for_status()
    return [m.get("name") for m in response.json().get("models", [])]
