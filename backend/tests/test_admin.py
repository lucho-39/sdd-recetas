"""Tests for the administrative API (/api/admin)."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ingredient, Recipe, User, UserRole

from conftest import create_category, create_ingredient, create_recipe


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


async def test_admin_recipes_list_detail_and_visibility(
    client: AsyncClient, admin_headers: dict, recipe: Recipe
) -> None:
    listing = await client.get("/api/admin/recipes?status=public", headers=admin_headers)
    assert listing.status_code == 200
    assert any(r["id"] == str(recipe.id) for r in listing.json()["items"])

    detail = await client.get(f"/api/admin/recipes/{recipe.id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["slug"] == recipe.slug

    vis = await client.patch(
        f"/api/admin/recipes/{recipe.id}/visibility",
        headers=admin_headers,
        json={"is_public": False},
    )
    assert vis.status_code == 200
    assert vis.json()["is_public"] is False


async def test_admin_recipe_update(
    client: AsyncClient, admin_headers: dict, recipe: Recipe
) -> None:
    response = await client.patch(
        f"/api/admin/recipes/{recipe.id}",
        headers=admin_headers,
        json={"title": "Editada por admin"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Editada por admin"


async def test_admin_recipe_soft_delete(
    client: AsyncClient, admin_headers: dict, recipe: Recipe, db_session: AsyncSession
) -> None:
    response = await client.delete(
        f"/api/admin/recipes/{recipe.id}", headers=admin_headers
    )
    assert response.status_code == 200
    await db_session.refresh(recipe)
    assert recipe.deleted_at is not None


async def test_admin_ingredient_validate(
    client: AsyncClient, admin_headers: dict, db_session: AsyncSession
) -> None:
    ingredient = await create_ingredient(db_session, slug="pendiente", name="Pendiente")

    pending = await client.get("/api/admin/ingredients/pending", headers=admin_headers)
    assert any(i["id"] == str(ingredient.id) for i in pending.json()["items"])

    validated = await client.post(
        f"/api/admin/ingredients/{ingredient.id}/validate", headers=admin_headers
    )
    assert validated.status_code == 200
    assert validated.json()["validated_by_admin"] is True

    listed = await client.get("/api/admin/ingredients/validated", headers=admin_headers)
    assert any(i["id"] == str(ingredient.id) for i in listed.json()["items"])


async def test_admin_ingredient_reject(
    client: AsyncClient, admin_headers: dict, db_session: AsyncSession
) -> None:
    ingredient = await create_ingredient(db_session, slug="rechazar", name="Rechazar")
    response = await client.post(
        f"/api/admin/ingredients/{ingredient.id}/reject",
        headers=admin_headers,
        json={"reason": "Duplicado"},
    )
    assert response.status_code == 200
    assert response.json()["rejected"] is True
    assert response.json()["rejection_reason"] == "Duplicado"


async def test_admin_ingredient_normalize(
    client: AsyncClient, admin_headers: dict, db_session: AsyncSession
) -> None:
    ingredient = await create_ingredient(db_session, slug="norm", name="Norm")
    response = await client.post(
        f"/api/admin/ingredients/{ingredient.id}/normalize",
        headers=admin_headers,
        json={"name": "Normalizado", "default_unit": "kg", "mark_validated": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Normalizado"
    assert body["validated_by_admin"] is True


async def test_admin_recipes_series(
    client: AsyncClient, admin_headers: dict, recipe: Recipe
) -> None:
    month = await client.get(
        "/api/admin/metrics/recipes-series?interval=month&periods=6",
        headers=admin_headers,
    )
    assert month.status_code == 200
    month_body = month.json()
    assert month_body["interval"] == "month"
    assert len(month_body["series"]) == 6
    assert sum(p["count"] for p in month_body["series"]) >= 1

    week = await client.get(
        "/api/admin/metrics/recipes-series?interval=week&periods=4",
        headers=admin_headers,
    )
    assert week.status_code == 200
    week_body = week.json()
    assert week_body["interval"] == "week"
    assert len(week_body["series"]) == 4
