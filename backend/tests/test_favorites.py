"""Tests for the favorites endpoints."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipe


async def test_add_favorite(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.post(
        f"/api/v1/favorites/{recipe.id}", headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Added to favorites"


async def test_add_favorite_is_idempotent_guard(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=auth_headers)
    duplicate = await client.post(
        f"/api/v1/favorites/{recipe.id}", headers=auth_headers
    )
    assert duplicate.status_code == 400


async def test_add_favorite_unknown_recipe_returns_404(
    client: AsyncClient, auth_headers: dict
) -> None:
    response = await client.post(
        "/api/v1/favorites/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_list_favorites_includes_recipe(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=auth_headers)

    response = await client.get("/api/v1/favorites", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["recipe_id"] == str(recipe.id)


async def test_remove_favorite(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=auth_headers)

    response = await client.delete(
        f"/api/v1/favorites/{recipe.id}", headers=auth_headers
    )
    assert response.status_code == 204

    listing = await client.get("/api/v1/favorites", headers=auth_headers)
    assert listing.json() == []


async def test_remove_missing_favorite_returns_404(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.delete(
        f"/api/v1/favorites/{recipe.id}", headers=auth_headers
    )
    assert response.status_code == 404


async def test_list_collections_includes_default(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    await client.post(
        f"/api/v1/favorites/{recipe.id}?collection=verano", headers=auth_headers
    )

    response = await client.get("/api/v1/favorites/collections", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body[0]["name"] is None
    assert body[0]["count"] == 1
    assert any(item["name"] == "verano" and item["count"] == 1 for item in body)


async def test_favorites_require_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/favorites")
    assert response.status_code == 401
