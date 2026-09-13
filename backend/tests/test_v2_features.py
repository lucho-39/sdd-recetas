"""Tests for the v2 flows: password reset, refresh reuse, OAuth and AI gating."""
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmailOutbox

from conftest import TEST_PASSWORD, create_user


async def test_forgot_password_queues_email(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_user(db_session, email="reset@example.com")

    response = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "reset@example.com"}
    )
    assert response.status_code == 200
    assert "token=" in response.json()["reset_url"]

    rows = (
        await db_session.execute(
            select(EmailOutbox).where(EmailOutbox.to_email == "reset@example.com")
        )
    ).scalars().all()
    assert len(rows) == 1


async def test_forgot_password_unknown_email_returns_no_link(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["reset_url"] is None


async def test_reset_password_flow(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_user(db_session, email="reset2@example.com")

    forgot = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "reset2@example.com"}
    )
    token = forgot.json()["reset_url"].split("token=")[1]

    reset = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "brandnewpass123"},
    )
    assert reset.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "reset2@example.com", "password": "brandnewpass123"},
    )
    assert login.status_code == 200


async def test_reset_password_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "not-a-token", "new_password": "whatever123"},
    )
    assert response.status_code == 400


async def test_refresh_rotation_and_reuse_detection(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_user(db_session, email="refresh@example.com")

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@example.com", "password": TEST_PASSWORD},
    )
    assert login.status_code == 200
    first_refresh = login.cookies.get("refresh_token")
    assert first_refresh

    rotated = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": first_refresh})
    assert rotated.status_code == 200
    second_refresh = rotated.cookies.get("refresh_token")
    assert second_refresh and second_refresh != first_refresh

    # Reusing the already-rotated token is detected and revokes the family.
    reuse = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": first_refresh})
    assert reuse.status_code == 401
    assert "reuse" in reuse.json()["detail"].lower()

    # The newest token is now revoked too (family compromised).
    after = await client.post("/api/v1/auth/refresh", cookies={"refresh_token": second_refresh})
    assert after.status_code == 401


async def test_oauth_unknown_provider(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/oauth/facebook", follow_redirects=False)
    assert response.status_code == 404


async def test_oauth_provider_not_configured(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/oauth/google", follow_redirects=False)
    assert response.status_code == 503


async def test_ai_generate_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/api/v1/ai/generate", json={"ingredients": "tomate"})
    assert response.status_code == 401


async def test_ai_generate_not_configured(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.post(
        "/api/v1/ai/generate", headers=auth_headers, json={"ingredients": "tomate, huevo"}
    )
    assert response.status_code == 503


async def test_ai_generate_validates_input(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.post(
        "/api/v1/ai/generate", headers=auth_headers, json={"ingredients": "x"}
    )
    assert response.status_code == 422
