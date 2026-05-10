from datetime import timedelta
from uuid import uuid4

from livekit import api

from app.config import settings


def livekit_configured() -> bool:
    return bool(settings.LIVEKIT_URL and settings.LIVEKIT_API_KEY and settings.LIVEKIT_API_SECRET)


def create_voice_room_identity(user_id: int) -> str:
    return f"nexora-user-{user_id}-{uuid4().hex[:8]}"


def create_voice_token(user_id: int, room_name: str | None = None) -> dict:
    if not livekit_configured():
        return {
            "status": "not_configured",
            "message": "LiveKit is installed but LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be configured.",
            "room": room_name or settings.LIVEKIT_DEFAULT_ROOM,
            "url": settings.LIVEKIT_URL,
            "token": None,
        }

    room = room_name or settings.LIVEKIT_DEFAULT_ROOM
    identity = create_voice_room_identity(user_id)
    token = (
        api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_ttl(timedelta(hours=2))
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )

    return {
        "status": "ready",
        "url": settings.LIVEKIT_URL,
        "room": room,
        "identity": identity,
        "token": token,
    }
