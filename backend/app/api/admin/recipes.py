"""
Admin: recipe management (/api/admin/recipes).
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import record_audit
from app.core.database import get_db
from app.core.security import require_admin
from app.models import Category, Recipe, User
from app.schemas.admin import RecipeAdminUpdate, RecipeVisibilityUpdate
from app.schemas.recipe import RecipeResponse

router = APIRouter()


def _status(recipe: Recipe) -> str:
    if recipe.deleted_at is not None:
        return "deleted"
    return "public" if recipe.is_public else "private"


@router.get("", summary="List recipes (admin)")
async def list_recipes(
    search: str | None = Query(None),
    status: str | None = Query(None, pattern="^(public|private|deleted)$"),
    category_id: UUID | None = Query(None),
    author_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if search:
        term = f"%{search}%"
        filters.append(or_(Recipe.title.ilike(term), Recipe.slug.ilike(term)))
    if status == "deleted":
        filters.append(Recipe.deleted_at.is_not(None))
    elif status == "public":
        filters.extend([Recipe.deleted_at.is_(None), Recipe.is_public == True])  # noqa: E712
    elif status == "private":
        filters.extend([Recipe.deleted_at.is_(None), Recipe.is_public == False])  # noqa: E712
    if category_id:
        filters.append(Recipe.category_id == category_id)
    if author_id:
        filters.append(Recipe.author_id == author_id)

    total = await db.scalar(select(func.count()).select_from(Recipe).where(*filters))
    result = await db.execute(
        select(Recipe)
        .where(*filters)
        .order_by(Recipe.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .options(selectinload(Recipe.author), selectinload(Recipe.category))
    )
    recipes = result.scalars().all()
    return {
        "items": [
            {
                "id": str(r.id),
                "slug": r.slug,
                "title": r.title,
                "status": _status(r),
                "category": r.category.name if r.category else None,
                "author": r.author.display_name if r.author else None,
                "author_id": str(r.author_id),
                "visit_count": r.visit_count,
                "save_count": r.save_count,
                "avg_rating": float(r.avg_rating),
                "created_at": r.created_at,
            }
            for r in recipes
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{recipe_id}", response_model=RecipeResponse, summary="Recipe detail (admin)")
async def get_recipe(
    recipe_id: UUID,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(
            selectinload(Recipe.author),
            selectinload(Recipe.category),
            selectinload(Recipe.tags),
        )
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeResponse.model_validate(recipe)


@router.patch("/{recipe_id}", response_model=RecipeResponse, summary="Update recipe (admin)")
async def update_recipe(
    recipe_id: UUID,
    data: RecipeAdminUpdate,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = data.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        category = await db.get(Category, update_data["category_id"])
        if not category or not category.is_active:
            raise HTTPException(status_code=400, detail="Invalid or inactive category")

    for field, value in update_data.items():
        setattr(recipe, field, value)

    await record_audit(
        db,
        admin.id,
        "recipe.update",
        target_type="recipe",
        target_id=str(recipe.id),
        detail=update_data,
    )
    await db.commit()
    await db.refresh(recipe, attribute_names=["author", "category", "tags"])
    return RecipeResponse.model_validate(recipe)


@router.patch("/{recipe_id}/visibility", response_model=RecipeResponse, summary="Toggle recipe visibility (admin)")
async def set_visibility(
    recipe_id: UUID,
    data: RecipeVisibilityUpdate,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.is_public = data.is_public
    await record_audit(
        db,
        admin.id,
        "recipe.visibility",
        target_type="recipe",
        target_id=str(recipe.id),
        detail={"is_public": data.is_public},
    )
    await db.commit()
    await db.refresh(recipe, attribute_names=["author", "category", "tags"])
    return RecipeResponse.model_validate(recipe)


@router.delete("/{recipe_id}", summary="Soft-delete recipe (admin)")
async def delete_recipe(
    recipe_id: UUID,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.deleted_at is None:
        recipe.deleted_at = datetime.utcnow()
        recipe.is_public = False
        await record_audit(
            db, admin.id, "recipe.delete", target_type="recipe", target_id=str(recipe.id)
        )
        await db.commit()
    return {"deleted": True, "id": str(recipe.id)}
