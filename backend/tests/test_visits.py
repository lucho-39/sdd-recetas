"""Tests for the visit tracking endpoint."""
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipe, User, Visit


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


async def test_get_recipe_by_slug_does_not_increment_visit_count(
    client: AsyncClient, db_session: AsyncSession, recipe: Recipe
) -> None:
    """RB-04: a plain read (F5) must not inflate the counter.

    Visits are recorded only through POST /visits, which deduplicates.
    """
    for _ in range(3):
        response = await client.get(f"/api/v1/recipes/{recipe.slug}")
        assert response.status_code == 200

    await db_session.refresh(recipe)
    assert recipe.visit_count == 0


async def test_authenticated_visit_is_deduplicated_per_user(
    client: AsyncClient,
    db_session: AsyncSession,
    recipe: Recipe,
    auth_headers: dict[str, str],
    user: User,
) -> None:
    """RB-04: logged-in visitors are identified by user_id, not by fingerprint."""
    first = await client.post(f"/api/v1/visits/{recipe.id}", headers=auth_headers)
    assert first.status_code == 201
    assert first.json()["message"] == "Visit recorded"

    second = await client.post(f"/api/v1/visits/{recipe.id}", headers=auth_headers)
    assert second.status_code == 201
    assert second.json()["message"] == "Visit already recorded today"

    await db_session.refresh(recipe)
    assert recipe.visit_count == 1

    result = await db_session.execute(
        select(Visit).where(Visit.recipe_id == recipe.id)
    )
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].user_id == user.id
