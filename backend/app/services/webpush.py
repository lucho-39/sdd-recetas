"""
Web Push (VAPID) delivery.

If VAPID keys are not configured via env, a key pair is generated on first use
and stored in ``app_settings`` (the private key never leaves the server). The
public key is exposed so the Service Worker can subscribe.
"""
import asyncio
import base64
import json
import logging
from typing import Any, Dict, List, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from pywebpush import WebPushException, webpush
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import AppSetting, PushSubscription

logger = logging.getLogger(__name__)

_PUBLIC_KEY_SETTING = "vapid_public_key"
_PRIVATE_KEY_SETTING = "vapid_private_key"


def generate_vapid_keys() -> Tuple[str, str]:
    """Return (public_key_base64url, private_key_pem)."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    public_key = base64.urlsafe_b64encode(public_raw).decode().rstrip("=")
    return public_key, private_pem


async def _read_setting(db: AsyncSession, key: str) -> str | None:
    row = await db.get(AppSetting, key)
    return row.value if row and row.value else None


async def _write_setting(db: AsyncSession, key: str, value: str) -> None:
    row = await db.get(AppSetting, key)
    if row is None:
        db.add(AppSetting(key=key, value=value))
    else:
        row.value = value


async def ensure_vapid_keys(db: AsyncSession) -> Tuple[str, str]:
    """Return the VAPID key pair, generating and persisting it if needed."""
    settings = get_settings()
    if settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY:
        return settings.VAPID_PUBLIC_KEY, settings.VAPID_PRIVATE_KEY

    public_key = await _read_setting(db, _PUBLIC_KEY_SETTING)
    private_key = await _read_setting(db, _PRIVATE_KEY_SETTING)
    if public_key and private_key:
        return public_key, private_key

    public_key, private_key = generate_vapid_keys()
    await _write_setting(db, _PUBLIC_KEY_SETTING, public_key)
    await _write_setting(db, _PRIVATE_KEY_SETTING, private_key)
    await db.commit()
    return public_key, private_key


async def get_public_key(db: AsyncSession) -> str:
    public_key, _ = await ensure_vapid_keys(db)
    return public_key


def _send_one(
    subscription_info: Dict[str, Any], data: Dict[str, Any], private_key: str, subject: str
) -> None:
    webpush(
        subscription_info=subscription_info,
        data=json.dumps(data),
        vapid_private_key=private_key,
        vapid_claims={"sub": subject},
        timeout=5,
    )


async def send_web_push(db: AsyncSession, *, user_id, payload: Dict[str, Any]) -> int:
    """Send a Web Push notification to every subscription of a user.

    Returns how many were delivered. Subscriptions the push service reports as
    gone (404/410) are removed.
    """
    settings = get_settings()
    subscriptions = (
        await db.execute(select(PushSubscription).where(PushSubscription.user_id == user_id))
    ).scalars().all()
    if not subscriptions:
        return 0

    try:
        _, private_key = await ensure_vapid_keys(db)
    except Exception:  # pragma: no cover - key generation must not break requests
        logger.warning("VAPID keys unavailable; skipping web push", exc_info=True)
        return 0

    sent = 0
    stale: List[PushSubscription] = []
    for subscription in subscriptions:
        info = {
            "endpoint": subscription.endpoint,
            "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
        }
        try:
            await asyncio.to_thread(
                _send_one, info, payload, private_key, settings.VAPID_SUBJECT
            )
            sent += 1
        except WebPushException as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code in (404, 410):
                stale.append(subscription)
            else:
                logger.warning("Web push failed for subscription %s: %s", subscription.id, exc)
        except Exception:  # pragma: no cover - network/transport errors
            logger.warning("Web push error for subscription %s", subscription.id, exc_info=True)

    for subscription in stale:
        await db.delete(subscription)
    if stale:
        await db.commit()
    return sent
