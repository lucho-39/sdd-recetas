"""Tests for the category endpoints."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category

from conftest import create_category


async def test_list_categories_returns_active_categories(
    client: AsyncClient, category: Category, auth_headers: dict
) -> None:
    response = await client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert category.slug in slugs


async def test_list_categories_excludes_inactive(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    inactive = await create_category(db_session, slug="inactiva", name="Inactiva")
    inactive.is_active = False
    await db_session.commit()

    response = await client.get("/api/v1/categories", headers=auth_headers)
    slugs = [item["slug"] for item in response.json()]
    assert "inactiva" not in slugs


async def test_list_categories_is_public(client: AsyncClient) -> None:
    response = await client.get("/api/v1/categories")
    assert response.status_code == 200


async def test_get_category_by_slug(
    client: AsyncClient, category: Category, auth_headers: dict
) -> None:
    response = await client.get(
        f"/api/v1/categories/{category.slug}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == category.name


async def test_get_unknown_category_returns_404(
    client: AsyncClient, auth_headers: dict
) -> None:
    response = await client.get("/api/v1/categories/nope", headers=auth_headers)
    assert response.status_code == 404
