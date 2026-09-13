"""Tests for the administrative API (/api/admin)."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole

from conftest import create_category


async def test_admin_endpoints_require_auth(client: AsyncClient) -> None:
    response = await client.get("/api/admin/metrics/dashboard")
    assert response.status_code == 401


async def test_admin_endpoints_require_admin_role(
    client: AsyncClient, auth_headers: dict
) -> None:
    response = await client.get("/api/admin/metrics/dashboard", headers=auth_headers)
    assert response.status_code == 403


async def test_dashboard_returns_counts(
    client: AsyncClient, admin_headers: dict, user: User, category
) -> None:
    response = await client.get("/api/admin/metrics/dashboard", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["users_total"] >= 2  # admin + user fixtures
    assert body["categories_total"] >= 1
    assert "ingredients_pending" in body


async def test_admin_list_users(
    client: AsyncClient, admin_headers: dict, user: User
) -> None:
    response = await client.get("/api/admin/users", headers=admin_headers)
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()["items"]]
    assert user.email in emails


async def test_admin_deactivate_and_activate_user(
    client: AsyncClient, admin_headers: dict, user: User, db_session: AsyncSession
) -> None:
    deact = await client.post(f"/api/admin/users/{user.id}/deactivate", headers=admin_headers)
    assert deact.status_code == 200
    assert deact.json()["is_active"] is False

    act = await client.post(f"/api/admin/users/{user.id}/activate", headers=admin_headers)
    assert act.status_code == 200
    assert act.json()["is_active"] is True


async def test_admin_change_user_role(
    client: AsyncClient, admin_headers: dict, user: User, db_session: AsyncSession
) -> None:
    response = await client.patch(
        f"/api/admin/users/{user.id}/role",
        headers=admin_headers,
        json={"role": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


async def test_admin_categories_crud(
    client: AsyncClient, admin_headers: dict
) -> None:
    create = await client.post(
        "/api/admin/categories",
        headers=admin_headers,
        json={"slug": "admin-test", "name": "Admin Test", "color": "#123456"},
    )
    assert create.status_code == 201
    category_id = create.json()["id"]

    listing = await client.get("/api/admin/categories?search=admin", headers=admin_headers)
    assert listing.status_code == 200
    assert any(c["id"] == category_id for c in listing.json()["items"])

    update = await client.patch(
        f"/api/admin/categories/{category_id}",
        headers=admin_headers,
        json={"name": "Admin Test 2"},
    )
    assert update.status_code == 200
    assert update.json()["name"] == "Admin Test 2"

    delete = await client.delete(
        f"/api/admin/categories/{category_id}", headers=admin_headers
    )
    assert delete.status_code == 200
    assert delete.json()["deleted"] is True


async def test_admin_tags_crud(client: AsyncClient, admin_headers: dict) -> None:
    create = await client.post(
        "/api/admin/tags",
        headers=admin_headers,
        json={"slug": "admin-tag", "name": "Admin Tag"},
    )
    assert create.status_code == 201
    tag_id = create.json()["id"]

    update = await client.patch(
        f"/api/admin/tags/{tag_id}", headers=admin_headers, json={"name": "Admin Tag 2"}
    )
    assert update.status_code == 200
    assert update.json()["name"] == "Admin Tag 2"

    delete = await client.delete(f"/api/admin/tags/{tag_id}", headers=admin_headers)
    assert delete.status_code == 200
