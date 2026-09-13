"""Tests for the current-user profile endpoints."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Recipe, User

from conftest import create_recipe


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


async def test_public_profile_exposes_no_sensitive_data(
    client: AsyncClient, user: User
) -> None:
    response = await client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] == user.display_name
    assert "created_at" in body
    assert body["recipe_count"] == 0
    assert "email" not in body
    assert "role" not in body


async def test_public_profile_counts_published_recipes(
    client: AsyncClient, user: User, recipe: Recipe
) -> None:
    response = await client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["recipe_count"] == 1


async def test_public_profile_unknown_returns_404(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/users/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


async def test_user_public_recipes_exclude_private(
    client: AsyncClient, db_session: AsyncSession, user: User, category
) -> None:
    await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Receta pública",
        slug="receta-publica",
        is_public=True,
    )
    await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Receta privada",
        slug="receta-privada",
        is_public=False,
    )

    response = await client.get(f"/api/v1/users/{user.id}/recipes")
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()["recipes"]]
    assert "receta-publica" in slugs
    assert "receta-privada" not in slugs


async def test_my_recipes_includes_private_and_requires_auth(
    client: AsyncClient, db_session: AsyncSession, user: User, category, auth_headers: dict
) -> None:
    assert (await client.get("/api/v1/users/me/recipes")).status_code == 401

    await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Receta privada",
        slug="receta-privada",
        is_public=False,
    )

    response = await client.get("/api/v1/users/me/recipes", headers=auth_headers)
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()["recipes"]]
    assert "receta-privada" in slugs
