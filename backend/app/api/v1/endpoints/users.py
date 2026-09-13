"""
User endpoints: profile (private), public profile and user recipes.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import NotificationPreference, Recipe, User
from app.schemas.auth import (
    NotificationPreferenceUpdate,
    PublicProfileResponse,
    UserResponse,
    UserUpdate,
)
from app.schemas.recipe import RecipeListItem
from app.services.notifications import get_preferences

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user profile (private)."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's display name and/or avatar."""
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/recipes", summary="List the current user's recipes")
async def list_my_recipes(
    include_deleted: bool = Query(False, description="Include soft-deleted recipes"),
    include_private: bool = Query(True, description="Include private recipes"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List every recipe created by the current user (RF-02.4).

    Includes private recipes by default and can include soft-deleted ones.
    """
    filters = [Recipe.author_id == current_user.id]
    if not include_deleted:
        filters.append(Recipe.deleted_at.is_(None))
    if not include_private:
        filters.append(Recipe.is_public == True)  # noqa: E712

    offset = (page - 1) * limit
    result = await db.execute(
        select(Recipe)
        .where(*filters)
        .order_by(Recipe.created_at.desc())
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(Recipe.author),
            selectinload(Recipe.category),
            selectinload(Recipe.tags),
        )
    )
    recipes = result.scalars().all()
    total = await db.scalar(select(func.count()).select_from(Recipe).where(*filters))

    return {
        "recipes": [RecipeListItem.model_validate(r) for r in recipes],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": (page * limit) < total,
    }


@router.get(
    "/me/notification-preferences",
    summary="Get my notification preferences",
)
async def get_my_notification_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_preferences(db, current_user.id)


@router.put(
    "/me/notification-preferences",
    summary="Update my notification preferences",
)
async def update_my_notification_preferences(
    data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    preference = await db.get(NotificationPreference, current_user.id)
    if preference is None:
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(preference, field, value)
    await db.commit()
    return await get_preferences(db, current_user.id)


@router.get("/{user_id}", response_model=PublicProfileResponse, summary="Public profile")
async def get_public_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Public profile of a user (RB-17 / RF-11): no sensitive data."""
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")

    recipe_count = await db.scalar(
        select(func.count())
        .select_from(Recipe)
        .where(
            Recipe.author_id == user.id,
            Recipe.is_public == True,  # noqa: E712
            Recipe.deleted_at.is_(None),
        )
    )

    return PublicProfileResponse(
        id=user.id,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        recipe_count=recipe_count or 0,
    )


@router.get("/{user_id}/recipes", summary="List a user's public recipes")
async def list_user_public_recipes(
    user_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Public recipes published by a user (RB-17 / RF-11.2)."""
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")

    filters = [
        Recipe.author_id == user.id,
        Recipe.is_public == True,  # noqa: E712
        Recipe.deleted_at.is_(None),
    ]
    offset = (page - 1) * limit
    result = await db.execute(
        select(Recipe)
        .where(*filters)
        .order_by(Recipe.created_at.desc())
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(Recipe.author),
            selectinload(Recipe.category),
            selectinload(Recipe.tags),
        )
    )
    recipes = result.scalars().all()
    total = await db.scalar(select(func.count()).select_from(Recipe).where(*filters))

    return {
        "recipes": [RecipeListItem.model_validate(r) for r in recipes],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": (page * limit) < total,
    }
