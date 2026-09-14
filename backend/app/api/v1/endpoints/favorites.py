"""
Favorites endpoints
"""
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import Favorite, Recipe
from app.schemas.recipe import RecipeListItem
from app.services.notifications import notify_recipe_author

router = APIRouter()


@router.get("", summary="List user favorites")
async def list_favorites(
    collection: str = None,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """List user's favorite recipes."""
    query = select(Favorite).where(Favorite.user_id == current_user.id)

    if collection:
        query = query.where(Favorite.collection_name == collection)

    result = await db.execute(
        query.options(
            selectinload(Favorite.recipe).selectinload(Recipe.category),
            selectinload(Favorite.recipe).selectinload(Recipe.author),
            selectinload(Favorite.recipe).selectinload(Recipe.tags),
        )
    )
    favorites = result.scalars().all()

    return [
        {
            "user_id": str(f.user_id),
            "recipe_id": str(f.recipe_id),
            "collection_name": f.collection_name,
            "created_at": f.created_at,
            "recipe": RecipeListItem.model_validate(f.recipe) if f.recipe else None,
        }
        for f in favorites
    ]


@router.post("/{recipe_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    recipe_id: str,
    collection: str = None,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Add recipe to favorites."""
    # Check if recipe exists
    from app.models import Recipe
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Check if already in favorites
    from app.models import Favorite
    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.recipe_id == recipe_id,
            Favorite.collection_name == collection
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already in favorites")

    favorite = Favorite(
        user_id=current_user.id,
        recipe_id=recipe_id,
        collection_name=collection,
    )
    db.add(favorite)
    recipe.save_count += 1
    await db.commit()

    await notify_recipe_author(db, actor=current_user, recipe=recipe, type="favorite")

    return {"message": "Added to favorites"}


@router.delete("/{recipe_id}", status_code=204)
async def remove_favorite(
    recipe_id: str,
    collection: str = None,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Remove recipe from favorites."""
    from app.models import Favorite
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.recipe_id == recipe_id,
            Favorite.collection_name == collection
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    await db.execute(
        delete(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.recipe_id == recipe_id,
            Favorite.collection_name == favorite.collection_name,
        )
    )
    recipe = await db.get(Recipe, recipe_id)
    if recipe is not None:
        recipe.save_count = max(0, recipe.save_count - 1)
    await db.commit()

    return None


@router.get("/collections", summary="List user's collections")
async def list_collections(
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """List user's collections with counts."""
    result = await db.execute(
        select(Favorite.collection_name, func.count().label("count"))
        .where(Favorite.user_id == current_user.id, Favorite.collection_name.is_not(None))
        .group_by(Favorite.collection_name)
    )
    collections = [{"name": row[0], "count": row[1]} for row in result.all()]

    # Add default "Favorites" collection
    total_favs = await db.scalar(
        select(func.count()).select_from(Favorite).where(Favorite.user_id == current_user.id)
    )
    collections.insert(0, {"name": None, "count": total_favs})

    return collections


@router.patch("/{recipe_id}", summary="Move a favorite to another collection")
async def update_favorite(
    recipe_id: str,
    payload: dict = Body(...),
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Set (or clear) the collection of an existing favorite."""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.recipe_id == recipe_id,
        )
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    collection = payload.get("collection_name") or None
    favorite.collection_name = collection
    await db.commit()

    return {"message": "Favorite updated", "collection_name": collection}


@router.patch("/collections/{name}", summary="Rename a collection")
async def rename_collection(
    name: str,
    payload: dict = Body(...),
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Rename one of the user's collections."""
    new_name = (payload.get("new_name") or "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="new_name is required")

    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.collection_name == name,
        )
    )
    favorites = result.scalars().all()
    if not favorites:
        raise HTTPException(status_code=404, detail="Collection not found")

    for favorite in favorites:
        favorite.collection_name = new_name
    await db.commit()

    return {"message": "Collection renamed", "name": new_name, "count": len(favorites)}


@router.delete("/collections/{name}", summary="Delete a collection")
async def delete_collection(
    name: str,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Delete a collection, moving its favorites back to the default list."""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.collection_name == name,
        )
    )
    favorites = result.scalars().all()
    if not favorites:
        raise HTTPException(status_code=404, detail="Collection not found")

    for favorite in favorites:
        favorite.collection_name = None
    await db.commit()

    return {"message": "Collection deleted", "moved_to_default": len(favorites)}