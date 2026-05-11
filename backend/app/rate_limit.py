import time
from fastapi import HTTPException, Request
from redis import Redis

from app.config import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def rate_limit(identifier: str, limit: int, window_seconds: int):
    now = int(time.time())
    bucket = now // window_seconds
    key = f"rate:{identifier}:{bucket}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window_seconds + 5)
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please slow down.")
    return {"limit": limit, "remaining": max(0, limit - current), "window_seconds": window_seconds}


def client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
