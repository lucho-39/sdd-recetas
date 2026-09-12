"""
Favorites endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import Favorite, Recipe

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

    result = await db.execute(query.options(selectinload(Favorite.recipe)))
    favorites = result.scalars().all()

    return favorites


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
    await db.commit()

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