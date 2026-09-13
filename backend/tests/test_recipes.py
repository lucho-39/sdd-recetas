"""Tests for the recipe endpoints."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Recipe, User

from conftest import create_category, create_recipe, create_user


def _recipe_payload(category: Category, **overrides: object) -> dict:
    payload: dict = {
        "title": "Pizza de mozzarella",
        "description": "Clásica pizza casera",
        "category_id": str(category.id),
        "instructions": "Preparar la masa, agregar queso y hornear.",
        "ingredients": [{"ingredient_id": "tomate", "quantity": 1, "unit": "unidad"}],
        "is_public": True,
    }
    payload.update(overrides)
    return payload


async def test_list_recipes_is_public(client: AsyncClient) -> None:
    response = await client.get("/api/v1/recipes")
    assert response.status_code == 200
    assert "recipes" in response.json()


async def test_list_recipes_returns_public_recipes(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.get("/api/v1/recipes", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["recipes"][0]["slug"] == recipe.slug


async def test_list_recipes_excludes_private_recipes(
    client: AsyncClient, db_session: AsyncSession, user: User, category: Category, auth_headers: dict
) -> None:
    await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Receta privada",
        slug="receta-privada",
        is_public=False,
    )

    response = await client.get("/api/v1/recipes", headers=auth_headers)
    assert response.json()["total"] == 0


async def test_list_recipes_filters_by_query(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.get(
        "/api/v1/recipes?query=manzana", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1

    missing = await client.get("/api/v1/recipes?query=inexistente", headers=auth_headers)
    assert missing.json()["total"] == 0


async def test_list_recipes_filters_by_category(
    client: AsyncClient, recipe: Recipe, category: Category, auth_headers: dict
) -> None:
    response = await client.get(
        f"/api/v1/recipes?category={category.slug}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_get_recipe_by_slug(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.get(f"/api/v1/recipes/{recipe.slug}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == recipe.slug
    assert body["title"] == recipe.title


async def test_get_unknown_recipe_returns_404(
    client: AsyncClient, auth_headers: dict
) -> None:
    response = await client.get("/api/v1/recipes/nope", headers=auth_headers)
    assert response.status_code == 404


async def test_create_recipe_generates_slug(
    client: AsyncClient, category: Category, auth_headers: dict
) -> None:
    response = await client.post(
        "/api/v1/recipes", json=_recipe_payload(category), headers=auth_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["slug"] == "pizza-de-mozzarella"
    assert body["similar_recipes"] == []


async def test_create_recipe_disambiguates_duplicate_slug(
    client: AsyncClient, category: Category, auth_headers: dict
) -> None:
    await client.post(
        "/api/v1/recipes", json=_recipe_payload(category), headers=auth_headers
    )
    response = await client.post(
        "/api/v1/recipes", json=_recipe_payload(category), headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "pizza-de-mozzarella-2"


async def test_create_recipe_suggests_similar_titles(
    client: AsyncClient, category: Category, auth_headers: dict
) -> None:
    await client.post(
        "/api/v1/recipes",
        json=_recipe_payload(category, title="Pizza de mozzarella"),
        headers=auth_headers,
    )
    response = await client.post(
        "/api/v1/recipes",
        json=_recipe_payload(category, title="Pizza de mozzarella especial"),
        headers=auth_headers,
    )
    assert response.status_code == 201
    similar = response.json()["similar_recipes"]
    assert any(item["slug"] == "pizza-de-mozzarella" for item in similar)


async def test_create_recipe_rejects_unknown_category(
    client: AsyncClient, auth_headers: dict
) -> None:
    response = await client.post(
        "/api/v1/recipes",
        json={
            "title": "Receta inválida",
            "category_id": "00000000-0000-0000-0000-000000000000",
            "instructions": "No debería crearse nunca.",
            "ingredients": [],
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_create_recipe_requires_authentication(
    client: AsyncClient, category: Category
) -> None:
    response = await client.post("/api/v1/recipes", json=_recipe_payload(category))
    assert response.status_code == 401


async def test_update_own_recipe(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.patch(
        f"/api/v1/recipes/{recipe.slug}",
        json={"description": "Descripción actualizada"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Descripción actualizada"


async def test_update_recipe_regenerates_slug_on_title_change(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.patch(
        f"/api/v1/recipes/{recipe.slug}",
        json={"title": "Tarta de pera"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Tarta de pera"
    assert body["slug"] == "tarta-de-pera"


async def test_update_other_users_recipe_returns_404(
    client: AsyncClient, db_session: AsyncSession, recipe: Recipe
) -> None:
    other = await create_user(db_session, email="intruder@example.com")
    from app.core.security import create_access_token

    headers = {"Authorization": f"Bearer {create_access_token(subject=str(other.id))}"}

    response = await client.patch(
        f"/api/v1/recipes/{recipe.slug}",
        json={"description": "No permitido"},
        headers=headers,
    )
    assert response.status_code == 404


async def test_delete_recipe_soft_deletes(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    delete = await client.delete(
        f"/api/v1/recipes/{recipe.slug}", headers=auth_headers
    )
    assert delete.status_code == 204

    after = await client.get(f"/api/v1/recipes/{recipe.slug}", headers=auth_headers)
    assert after.status_code == 404


async def test_delete_other_users_recipe_returns_404(
    client: AsyncClient, db_session: AsyncSession, recipe: Recipe
) -> None:
    other = await create_user(db_session, email="deleter@example.com")
    from app.core.security import create_access_token

    headers = {"Authorization": f"Bearer {create_access_token(subject=str(other.id))}"}

    response = await client.delete(
        f"/api/v1/recipes/{recipe.slug}", headers=headers
    )
    assert response.status_code == 404


async def test_find_similar_recipes(
    client: AsyncClient, db_session: AsyncSession, user: User, auth_headers: dict
) -> None:
    category = await create_category(db_session, slug="tartas", name="Tartas")
    first = await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Pizza de mozzarella",
        slug="pizza-de-mozzarella",
    )
    second = await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Pizza de mozzarella especial",
        slug="pizza-de-mozzarella-especial",
    )

    response = await client.get(
        f"/api/v1/recipes/{second.slug}/similar", headers=auth_headers
    )
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()]
    assert first.slug in slugs


async def test_restore_recipe(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    await client.delete(f"/api/v1/recipes/{recipe.slug}", headers=auth_headers)

    response = await client.post(
        f"/api/v1/recipes/{recipe.slug}/restore", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["deleted_at"] is None

    after = await client.get(f"/api/v1/recipes/{recipe.slug}", headers=auth_headers)
    assert after.status_code == 200


async def test_restore_active_recipe_returns_400(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.post(
        f"/api/v1/recipes/{recipe.slug}/restore", headers=auth_headers
    )
    assert response.status_code == 400


async def test_restore_other_users_recipe_returns_404(
    client: AsyncClient, db_session: AsyncSession, recipe: Recipe
) -> None:
    other = await create_user(db_session, email="restorer@example.com")
    from app.core.security import create_access_token

    headers = {"Authorization": f"Bearer {create_access_token(subject=str(other.id))}"}
    response = await client.post(
        f"/api/v1/recipes/{recipe.slug}/restore", headers=headers
    )
    assert response.status_code == 404


async def test_get_recipe_resolves_ingredient_names(
    client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    category: Category,
    auth_headers: dict,
) -> None:
    from conftest import create_ingredient

    ingredient = await create_ingredient(db_session, slug="harina", name="Harina")
    recipe = await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Pan casero",
        slug="pan-casero",
        ingredients=[
            {"ingredient_id": str(ingredient.id), "amount": 500, "unit": "g"}
        ],
    )

    response = await client.get(f"/api/v1/recipes/{recipe.slug}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ingredients"][0]["name"] == "Harina"


async def test_list_recipes_filters_by_max_time(
    client: AsyncClient, recipe: Recipe, auth_headers: dict
) -> None:
    response = await client.get("/api/v1/recipes?max_time=10", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_list_recipes_filters_by_difficulty(
    client: AsyncClient,
    db_session: AsyncSession,
    recipe: Recipe,
    user: User,
    category: Category,
    auth_headers: dict,
) -> None:
    hard = await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Receta difícil",
        slug="receta-dificil",
    )
    hard.difficulty = "hard"
    await db_session.commit()

    match = await client.get("/api/v1/recipes?difficulty=hard", headers=auth_headers)
    assert match.json()["total"] == 1
    assert match.json()["recipes"][0]["slug"] == "receta-dificil"

    none = await client.get("/api/v1/recipes?difficulty=easy", headers=auth_headers)
    assert none.json()["total"] == 0
