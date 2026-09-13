"""Tests for the Web Push endpoints and VAPID key handling."""
import base64

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PushSubscription
from app.services.webpush import generate_vapid_keys, send_web_push


async def test_vapid_public_key(client: AsyncClient) -> None:
    response = await client.get("/api/v1/push/public-key")
    assert response.status_code == 200
    public_key = response.json()["public_key"]
    raw = base64.urlsafe_b64decode(public_key + "=" * (-len(public_key) % 4))
    assert len(raw) == 65
    assert raw[0] == 4  # uncompressed EC point


def test_generate_vapid_keys() -> None:
    public_key, private_pem = generate_vapid_keys()
    assert private_pem.startswith("-----BEGIN PRIVATE KEY-----")
    raw = base64.urlsafe_b64decode(public_key + "=" * (-len(public_key) % 4))
    assert len(raw) == 65


async def test_subscribe_and_unsubscribe(
    client: AsyncClient, auth_headers: dict
) -> None:
    payload = {
        "endpoint": "https://push.example.com/sub/abc",
        "keys": {"p256dh": "p256dh-key", "auth": "auth-secret"},
    }

    created = await client.post(
        "/api/v1/push/subscribe", headers=auth_headers, json=payload
    )
    assert created.status_code == 201

    # upsert is idempotent
    again = await client.post(
        "/api/v1/push/subscribe", headers=auth_headers, json=payload
    )
    assert again.status_code == 201

    removed = await client.request(
        "DELETE",
        "/api/v1/push/subscribe",
        headers=auth_headers,
        json={"endpoint": payload["endpoint"]},
    )
    assert removed.status_code == 200


async def test_push_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/push/subscribe",
        json={"endpoint": "https://e/1", "keys": {"p256dh": "a", "auth": "b"}},
    )
    assert response.status_code == 401


async def test_send_web_push_handles_unreachable_endpoint(
    db_session: AsyncSession, user
) -> None:
    db_session.add(
        PushSubscription(
            user_id=user.id,
            endpoint="https://127.0.0.1:1/none",
            p256dh="p256dh-key",
            auth="auth-secret",
        )
    )
    await db_session.commit()

    # Delivery fails (unreachable) but must not raise; returns 0 delivered.
    sent = await send_web_push(db_session, user_id=user.id, payload={"title": "x"})
    assert sent == 0
