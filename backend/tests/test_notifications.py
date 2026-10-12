"""Tests for the notifications endpoints and their live triggers."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipe, User

from conftest import create_ingredient


async def test_notifications_require_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/notifications")
    assert response.status_code == 401


async def test_favorite_notifies_recipe_author(
    client: AsyncClient, recipe: Recipe, auth_headers: dict, admin_headers: dict
) -> None:
    # admin_user favorites the recipe owned by user
    added = await client.post(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)
    assert added.status_code == 201

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["unread_count"] == 1
    assert body["total"] == 1
    item = body["items"][0]
    assert item["type"] == "favorite"
    assert item["recipe_slug"] == recipe.slug
    assert item["actor"]["display_name"] == "Admin"
    assert item["is_read"] is False


async def test_rating_notifies_with_score(
    client: AsyncClient, recipe: Recipe, auth_headers: dict, admin_headers: dict
) -> None:
    await client.post(f"/api/v1/ratings/{recipe.id}?score=5", headers=admin_headers)

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    item = listing.json()["items"][0]
    assert item["type"] == "rating"
    assert item["detail"]["score"] == 5


async def test_self_action_does_not_notify(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=auth_headers)

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    assert listing.json()["total"] == 0


async def test_repeated_rating_refreshes_single_notification(
    client: AsyncClient, recipe: Recipe, auth_headers: dict, admin_headers: dict
) -> None:
    await client.post(f"/api/v1/ratings/{recipe.id}?score=5", headers=admin_headers)
    await client.post(f"/api/v1/ratings/{recipe.id}?score=3", headers=admin_headers)

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    body = listing.json()
    assert body["total"] == 1
    assert body["items"][0]["detail"]["score"] == 3


async def test_mark_read_updates_unread_count(
    client: AsyncClient, recipe: Recipe, auth_headers: dict, admin_headers: dict
) -> None:
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)

    unread = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert unread.json()["unread_count"] == 1

    item_id = (await client.get("/api/v1/notifications", headers=auth_headers)).json()["items"][0]["id"]
    read = await client.post(f"/api/v1/notifications/{item_id}/read", headers=auth_headers)
    assert read.status_code == 200

    after = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert after.json()["unread_count"] == 0


async def test_delete_one_and_all(
    client: AsyncClient, recipe: Recipe, auth_headers: dict, admin_headers: dict
) -> None:
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)
    item_id = (await client.get("/api/v1/notifications", headers=auth_headers)).json()["items"][0]["id"]

    deleted = await client.delete(f"/api/v1/notifications/{item_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert (await client.get("/api/v1/notifications", headers=auth_headers)).json()["total"] == 0

    # unfavorite and favorite again to trigger a fresh notification
    await client.delete(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)
    assert (await client.get("/api/v1/notifications", headers=auth_headers)).json()["total"] == 1

    cleared = await client.delete("/api/v1/notifications", headers=auth_headers)
    assert cleared.status_code == 200
    assert cleared.json()["deleted"] == 1


async def test_cannot_touch_another_users_notification(
    client: AsyncClient, recipe: Recipe, auth_headers: dict, admin_headers: dict
) -> None:
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)
    item_id = (await client.get("/api/v1/notifications", headers=auth_headers)).json()["items"][0]["id"]

    # admin (the actor, not the recipient) must not read or delete it
    read = await client.post(f"/api/v1/notifications/{item_id}/read", headers=admin_headers)
    assert read.status_code == 404
    delete = await client.delete(f"/api/v1/notifications/{item_id}", headers=admin_headers)
    assert delete.status_code == 404


async def test_default_preferences(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get(
        "/api/v1/users/me/notification-preferences", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["in_app_enabled"] is True
    assert body["email_enabled"] is False
    assert body["push_enabled"] is False
    assert body["favorites_enabled"] is True


async def test_update_preferences_partial(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.put(
        "/api/v1/users/me/notification-preferences",
        headers=auth_headers,
        json={"push_enabled": True, "ratings_enabled": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["push_enabled"] is True
    assert body["ratings_enabled"] is False
    assert body["in_app_enabled"] is True  # untouched


async def test_email_channel_queues_outbox(
    client: AsyncClient,
    db_session,
    user,
    recipe: Recipe,
    auth_headers: dict,
    admin_headers: dict,
) -> None:
    from sqlalchemy import select

    from app.models import EmailOutbox

    # author opts into email and out of in-app
    await client.put(
        "/api/v1/users/me/notification-preferences",
        headers=auth_headers,
        json={"email_enabled": True, "in_app_enabled": False},
    )

    await client.post(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    assert listing.json()["total"] == 0

    rows = (
        await db_session.execute(
            select(EmailOutbox).where(EmailOutbox.to_email == user.email)
        )
    ).scalars().all()
    assert len(rows) == 1
    assert rows[0].status == "queued"
    assert "guardó tu receta" in rows[0].subject


async def test_disabled_event_notifies_nothing(
    client: AsyncClient, recipe: Recipe, auth_headers: dict, admin_headers: dict
) -> None:
    await client.put(
        "/api/v1/users/me/notification-preferences",
        headers=auth_headers,
        json={"favorites_enabled": False},
    )
    await client.post(f"/api/v1/favorites/{recipe.id}", headers=admin_headers)

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    assert listing.json()["total"] == 0


async def test_rating_email_message(
    client: AsyncClient,
    db_session,
    user,
    recipe: Recipe,
    auth_headers: dict,
    admin_headers: dict,
) -> None:
    from sqlalchemy import select

    from app.models import EmailOutbox

    await client.put(
        "/api/v1/users/me/notification-preferences",
        headers=auth_headers,
        json={"email_enabled": True},
    )
    await client.post(f"/api/v1/ratings/{recipe.id}?score=4", headers=admin_headers)

    rows = (
        await db_session.execute(
            select(EmailOutbox).where(EmailOutbox.to_email == user.email)
        )
    ).scalars().all()
    assert len(rows) == 1
    subject = rows[0].subject
    assert "recibió una calificación de 4 estrellas" in subject
    assert "'Admin'" in subject
    assert recipe.title in subject


async def test_custom_email_template(
    client: AsyncClient,
    db_session,
    user,
    recipe: Recipe,
    auth_headers: dict,
    admin_headers: dict,
) -> None:
    from sqlalchemy import select

    from app.models import EmailOutbox

    await client.put(
        "/api/v1/users/me/notification-preferences",
        headers=auth_headers,
        json={"email_enabled": True},
    )
    await client.put(
        "/api/admin/config",
        headers=admin_headers,
        json={"settings": {"email_rating_subject": "[Nueva] {score}★ en {recipe}"}},
    )
    await client.post(f"/api/v1/ratings/{recipe.id}?score=5", headers=admin_headers)

    rows = (
        await db_session.execute(
            select(EmailOutbox).where(EmailOutbox.to_email == user.email)
        )
    ).scalars().all()
    assert rows[-1].subject == "[Nueva] 5★ en Tarta de manzana"


async def test_ingredient_rejection_notifies_creator(
    client: AsyncClient,
    admin_headers: dict,
    auth_headers: dict,
    db_session: AsyncSession,
    user: User,
) -> None:
    """UC-ADMIN-016 AC3: the creator gets an in-app notification with the reason."""
    ingredient = await create_ingredient(
        db_session, slug="rechazable", name="Rechazable", created_by=user.id
    )

    rejected = await client.post(
        f"/api/admin/ingredients/{ingredient.id}/reject",
        headers=admin_headers,
        json={"reason": "Spam"},
    )
    assert rejected.status_code == 200

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    assert listing.status_code == 200
    item = listing.json()["items"][0]
    assert item["type"] == "ingredient_rejected"
    assert item["detail"]["reason"] == "Spam"
    assert item["detail"]["ingredient_name"] == "Rechazable"
    # There is no recipe behind this event; the frontend falls back to '/'.
    assert item["recipe_id"] is None


async def test_ingredient_rejection_skips_seed_ingredients(
    client: AsyncClient,
    admin_headers: dict,
    auth_headers: dict,
    db_session: AsyncSession,
) -> None:
    """A catalog entry with no creator has nobody to notify."""
    ingredient = await create_ingredient(db_session, slug="sin-creador", name="Sin Creador")

    rejected = await client.post(
        f"/api/admin/ingredients/{ingredient.id}/reject",
        headers=admin_headers,
        json={"reason": "Otro"},
    )
    assert rejected.status_code == 200

    listing = await client.get("/api/v1/notifications", headers=auth_headers)
    assert listing.json()["total"] == 0


async def test_ingredient_rejection_sends_email_when_enabled(
    client: AsyncClient,
    admin_headers: dict,
    auth_headers: dict,
    db_session: AsyncSession,
    user: User,
) -> None:
    """The channel preference is honoured; the per-event ones are not."""
    from sqlalchemy import select

    from app.models import EmailOutbox

    await client.put(
        "/api/v1/users/me/notification-preferences",
        headers=auth_headers,
        json={"email_enabled": True, "favorites_enabled": False, "ratings_enabled": False},
    )
    ingredient = await create_ingredient(
        db_session, slug="por-email", name="Por Email", created_by=user.id
    )

    rejected = await client.post(
        f"/api/admin/ingredients/{ingredient.id}/reject",
        headers=admin_headers,
        json={"reason": "Duplicado"},
    )
    assert rejected.status_code == 200

    rows = (
        await db_session.execute(
            select(EmailOutbox).where(EmailOutbox.to_email == user.email)
        )
    ).scalars().all()
    assert any("Por Email" in row.subject for row in rows)
