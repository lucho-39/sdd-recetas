"""Tests for the visit tracking endpoint."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipe


async def test_record_visit_increments_counter(
    client: AsyncClient, db_session: AsyncSession, recipe: Recipe
) -> None:
    response = await client.post(f"/api/v1/visits/{recipe.id}")
    assert response.status_code == 201
    assert response.json()["message"] == "Visit recorded"

    await db_session.refresh(recipe)
    assert recipe.visit_count == 1


async def test_repeated_visit_same_day_does_not_double_count(
    client: AsyncClient, db_session: AsyncSession, recipe: Recipe
) -> None:
    await client.post(f"/api/v1/visits/{recipe.id}")
    await client.post(f"/api/v1/visits/{recipe.id}")

    await db_session.refresh(recipe)
    assert recipe.visit_count == 1


async def test_record_visit_unknown_recipe_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/visits/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
