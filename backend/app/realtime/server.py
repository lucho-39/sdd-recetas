"""
Socket.IO server for real-time notifications.

The FastAPI app stays the primary ASGI app; ``socket_app`` (in ``app.main``)
wraps it so Socket.IO and HTTP share the same port. Each authenticated socket
joins a room named ``user:<id>`` so notifications can be pushed to every
connected tab of a user.
"""
import logging
from typing import Any, Dict

import socketio

from app.core.config import get_settings
from app.core.security import decode_token

logger = logging.getLogger(__name__)

settings = get_settings()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
)


def user_room(user_id: str) -> str:
    return f"user:{user_id}"


@sio.event
async def connect(sid: str, environ: dict, auth: Any) -> None:
    token = auth.get("token") if isinstance(auth, dict) else None
    payload = decode_token(token) if token else None

    if not payload or payload.get("type") != "access":
        raise socketio.exceptions.ConnectionRefusedError("authentication required")

    user_id = payload.get("sub")
    if not user_id:
        raise socketio.exceptions.ConnectionRefusedError("authentication required")

    await sio.save_session(sid, {"user_id": str(user_id)})
    await sio.enter_room(sid, user_room(str(user_id)))


@sio.event
async def disconnect(sid: str) -> None:
    return None


async def emit_notification(user_id: str, payload: Dict[str, Any]) -> None:
    """Emit a notification to all sockets of a user (best effort)."""
    try:
        await sio.emit("notification", payload, room=user_room(str(user_id)))
    except Exception:  # pragma: no cover - never fail the request on emit issues
        logger.warning("Failed to emit notification to user %s", user_id, exc_info=True)
