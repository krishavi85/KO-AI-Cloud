from app.config import settings


def classify_task(prompt: str) -> str:
    p = prompt.lower()
    if any(x in p for x in ["code", "bug", "python", "javascript", "kotlin", "react"]):
        return "code"
    if any(x in p for x in ["summarize", "summary", "document", "pdf"]):
        return "document"
    if any(x in p for x in ["image", "picture", "logo", "flyer"]):
        return "image"
    if any(x in p for x in ["voice", "audio", "transcribe", "speech"]):
        return "voice"
    return "general"


def route_model(requested_model: str | None, prompt: str) -> dict:
    task = classify_task(prompt)
    model = requested_model or settings.DEFAULT_CHAT_MODEL
    route = "local-ollama"

    if task == "code" and not requested_model:
        model = "qwen2.5-coder:7b"
    elif task == "document" and not requested_model:
        model = settings.DEFAULT_CHAT_MODEL

    if settings.ENABLE_GPU_ROUTER and settings.GPU_WORKER_URLS:
        route = "distributed-gpu"

    return {"task": task, "model": model, "route": route}
