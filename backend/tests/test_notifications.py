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
