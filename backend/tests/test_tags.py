"""Tests for the tag endpoints."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from conftest import create_tag


async def test_list_tags_is_public(client: AsyncClient) -> None:
    response = await client.get("/api/v1/tags")
    assert response.status_code == 200


async def test_list_tags_returns_only_used_tags(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    await create_tag(db_session, slug="italiana", name="Italiana", usage_count=5)
    unused = await create_tag(db_session, slug="sin-uso", name="Sin uso", usage_count=0)

    response = await client.get("/api/v1/tags", headers=auth_headers)
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert "italiana" in slugs
    assert unused.slug not in slugs


async def test_list_tags_filters_by_query(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
) -> None:
    await create_tag(db_session, slug="italiana", name="Italiana", usage_count=5)
    await create_tag(db_session, slug="mexicana", name="Mexicana", usage_count=3)

    response = await client.get(
        "/api/v1/tags?query=ital", headers=auth_headers
    )
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert slugs == ["italiana"]


async def test_popular_tags_are_ordered_by_usage(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_tag(db_session, slug="poco", name="Poco", usage_count=1)
    await create_tag(db_session, slug="mucho", name="Mucho", usage_count=99)

    response = await client.get("/api/v1/tags/popular")
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert slugs[0] == "mucho"
