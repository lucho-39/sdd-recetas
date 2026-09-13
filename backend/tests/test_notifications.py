"""Tests for the notifications endpoints and their live triggers."""
from httpx import AsyncClient

from app.models import Recipe


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
