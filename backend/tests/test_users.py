"""Tests for the current-user profile endpoints."""
from httpx import AsyncClient

from app.models import User


async def test_get_me_returns_profile(
    client: AsyncClient, user: User, auth_headers: dict
) -> None:
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == user.email
    assert body["display_name"] == user.display_name


async def test_get_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_patch_me_updates_display_name(
    client: AsyncClient, user: User, auth_headers: dict
) -> None:
    response = await client.patch(
        "/api/v1/users/me",
        json={"display_name": "Nombre Actualizado"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Nombre Actualizado"


async def test_patch_me_updates_avatar_and_persists(
    client: AsyncClient, user: User, auth_headers: dict
) -> None:
    response = await client.patch(
        "/api/v1/users/me",
        json={"avatar_url": "https://example.com/avatar.png"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["avatar_url"] == "https://example.com/avatar.png"

    follow_up = await client.get("/api/v1/users/me", headers=auth_headers)
    assert follow_up.json()["avatar_url"] == "https://example.com/avatar.png"


async def test_patch_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/users/me", json={"display_name": "Anonymous"}
    )
    assert response.status_code == 401
