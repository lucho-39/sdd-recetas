"""Tests for the rating endpoints."""
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Rating, Recipe


async def test_rate_recipe(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.post(
        f"/api/v1/ratings/{recipe.id}?score=5", headers=auth_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Rating saved"
    assert body["avg_rating"] == 5.0
    assert body["rating_count"] == 1


async def test_rate_recipe_rejects_out_of_range_score(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    too_low = await client.post(
        f"/api/v1/ratings/{recipe.id}?score=0", headers=auth_headers
    )
    assert too_low.status_code == 400

    too_high = await client.post(
        f"/api/v1/ratings/{recipe.id}?score=6", headers=auth_headers
    )
    assert too_high.status_code == 400


async def test_rate_unknown_recipe_returns_404(
    client: AsyncClient, auth_headers: dict
) -> None:
    response = await client.post(
        "/api/v1/ratings/00000000-0000-0000-0000-000000000000?score=5",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_rate_requires_authentication(client: AsyncClient, recipe: Recipe) -> None:
    response = await client.post(f"/api/v1/ratings/{recipe.id}?score=5")
    assert response.status_code == 401


async def test_rating_updates_recipe_aggregates(
    client: AsyncClient,
    db_session: AsyncSession,
    recipe: Recipe,
    auth_headers: dict,
) -> None:
    await client.post(f"/api/v1/ratings/{recipe.id}?score=4", headers=auth_headers)

    refreshed = await db_session.get(Recipe, recipe.id)
    assert refreshed is not None
    await db_session.refresh(refreshed)
    assert refreshed.rating_count == 1
    assert refreshed.avg_rating == 4.0


async def test_rating_is_upserted_per_user(
    client: AsyncClient,
    db_session: AsyncSession,
    recipe: Recipe,
    auth_headers: dict,
) -> None:
    await client.post(f"/api/v1/ratings/{recipe.id}?score=4", headers=auth_headers)
    await client.post(f"/api/v1/ratings/{recipe.id}?score=2", headers=auth_headers)

    result = await db_session.execute(
        select(Rating).where(Rating.recipe_id == recipe.id)
    )
    ratings = result.scalars().all()
    assert len(ratings) == 1
    assert ratings[0].score == 2


async def test_get_recipe_ratings(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    await client.post(
        f"/api/v1/ratings/{recipe.id}?score=5&review_text=Riquísima",
        headers=auth_headers,
    )

    response = await client.get(f"/api/v1/ratings/{recipe.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["ratings"][0]["score"] == 5
    assert body["ratings"][0]["review_text"] == "Riquísima"
