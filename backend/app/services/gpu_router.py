import itertools
import requests
from app.config import settings

_worker_cycle = None


def get_workers() -> list[str]:
    return [u.strip() for u in settings.GPU_WORKER_URLS.split(",") if u.strip()]


def choose_worker() -> str | None:
    global _worker_cycle
    workers = get_workers()
    if not workers:
        return None
    if _worker_cycle is None:
        _worker_cycle = itertools.cycle(workers)
    return next(_worker_cycle)


def distributed_chat(payload: dict) -> str | None:
    if not settings.ENABLE_GPU_ROUTER:
        return None
    worker = choose_worker()
    if not worker:
        return None
    response = requests.post(f"{worker.rstrip('/')}/v1/chat/completions", json=payload, timeout=300)
    response.raise_for_status()
    data = response.json()
    return data.get("response") or data.get("choices", [{}])[0].get("message", {}).get("content")
