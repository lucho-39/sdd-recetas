"""Tests for the ingredient endpoints."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ingredient

from conftest import create_ingredient


async def test_search_ingredients_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/ingredients")
    assert response.status_code == 401


async def test_search_ingredients_returns_active_ingredients(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    await create_ingredient(db_session, slug="tomate", name="Tomate")
    inactive = await create_ingredient(
        db_session, slug="oculto", name="Oculto", is_active=False
    )

    response = await client.get("/api/v1/ingredients", headers=auth_headers)
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert "tomate" in slugs
    assert inactive.slug not in slugs


async def test_search_ingredients_matches_name(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    await create_ingredient(db_session, slug="tomate", name="Tomate")
    await create_ingredient(db_session, slug="cebolla", name="Cebolla")

    response = await client.get(
        "/api/v1/ingredients?query=tom", headers=auth_headers
    )
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert slugs == ["tomate"]


async def test_search_ingredients_matches_alias(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    await create_ingredient(
        db_session, slug="tomate", name="Tomate", aliases=["jitomate"]
    )

    response = await client.get(
        "/api/v1/ingredients?query=jitomate", headers=auth_headers
    )
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert slugs == ["tomate"]


async def test_search_ingredients_filters_by_category(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    await create_ingredient(
        db_session, slug="tomate", name="Tomate", category="vegetales"
    )
    await create_ingredient(
        db_session, slug="queso", name="Queso", category="lacteos"
    )

    response = await client.get(
        "/api/v1/ingredients?category=lacteos", headers=auth_headers
    )
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert slugs == ["queso"]


async def test_ingredient_categories_returns_counts(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_ingredient(
        db_session, slug="tomate", name="Tomate", category="vegetales"
    )
    await create_ingredient(
        db_session, slug="queso", name="Queso", category="lacteos"
    )

    response = await client.get("/api/v1/ingredients/categories")
    assert response.status_code == 200
    counts = {row["category"]: row["count"] for row in response.json()}
    assert counts["vegetales"] == 1
    assert counts["lacteos"] == 1


async def test_get_ingredient_by_id(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    ingredient = await create_ingredient(db_session, slug="tomate", name="Tomate")

    response = await client.get(
        f"/api/v1/ingredients/{ingredient.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["slug"] == "tomate"


async def test_get_unknown_ingredient_returns_404(
    client: AsyncClient, auth_headers: dict
) -> None:
    response = await client.get(
        "/api/v1/ingredients/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404
