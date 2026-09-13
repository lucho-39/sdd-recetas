"""Tests for the authentication endpoints."""
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import User, UserRole

from conftest import TEST_PASSWORD, create_user


async def test_register_creates_account(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "display_name": "New User",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newuser@example.com"
    assert body["display_name"] == "New User"
    # Email verification delivery is v2, so MVP auto-verifies on register.
    assert body["is_verified"] is True


async def test_register_rejects_duplicate_email(client: AsyncClient, user: User) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": user.email,
            "display_name": "Duplicate",
            "password": "password123",
        },
    )
    assert response.status_code == 400


async def test_register_validates_email_format(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "display_name": "Bad", "password": "password123"},
    )
    assert response.status_code == 422


async def test_register_validates_password_length(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "display_name": "Short", "password": "abc"},
    )
    assert response.status_code == 422


async def test_login_returns_token_and_sets_refresh_cookie(
    client: AsyncClient, user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] > 0
    assert "refresh_token" in response.cookies


async def test_login_rejects_wrong_password(client: AsyncClient, user: User) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_login_rejects_unknown_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "ghost@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401


async def test_login_rejects_unverified_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_user(db_session, email="unverified@example.com", is_verified=False)
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "unverified@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 403


async def test_me_returns_current_user(
    client: AsyncClient, user: User, auth_headers: dict
) -> None:
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user.email
    assert body["role"] == "user"


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


async def test_refresh_rotates_tokens(client: AsyncClient, user: User) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": TEST_PASSWORD},
    )
    assert login.status_code == 200
    access_token = login.json()["access_token"]

    refresh = await client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    new_body = refresh.json()
    assert new_body["access_token"]
    assert new_body["access_token"] != access_token
    assert "refresh_token" in refresh.cookies


async def test_refresh_without_cookie_fails(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


async def test_change_password_updates_credentials(
    client: AsyncClient, user: User, auth_headers: dict
) -> None:
    response = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": TEST_PASSWORD, "new_password": "brand-new-pass"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "brand-new-pass"},
    )
    assert login.status_code == 200


async def test_change_password_rejects_wrong_current(
    client: AsyncClient, user: User, auth_headers: dict
) -> None:
    response = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrong-password", "new_password": "brand-new-pass"},
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_logout_returns_success(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert "message" in response.json()


async def test_forgot_password_never_leaks_account_existence(
    client: AsyncClient, user: User
) -> None:
    known = await client.post(
        "/api/v1/auth/forgot-password", json={"email": user.email}
    )
    unknown = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "ghost@example.com"}
    )
    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json() == unknown.json()


async def test_bootstrap_admin_creates_admin_and_is_idempotent(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    settings = get_settings()

    first = await client.post("/api/v1/auth/bootstrap-admin")
    assert first.status_code == 201

    # Idempotent: running again must not fail or duplicate the admin.
    second = await client.post("/api/v1/auth/bootstrap-admin")
    assert second.status_code == 201

    result = await db_session.execute(
        select(User).where(User.email == settings.ADMIN_INITIAL_USER)
    )
    admins = result.scalars().all()
    assert len(admins) == 1
    assert admins[0].role == UserRole.ADMIN
    assert admins[0].must_change_password is True

    login = await client.post(
        "/api/v1/auth/login",
        data={
            "username": settings.ADMIN_INITIAL_USER,
            "password": settings.ADMIN_INITIAL_PASSWORD,
        },
    )
    assert login.status_code == 200

    # Regression: the bootstrap admin may use a reserved TLD (e.g. ``.local``),
    # which must not break response serialization on ``/me``.
    token = login.json()["access_token"]
    me = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == settings.ADMIN_INITIAL_USER
