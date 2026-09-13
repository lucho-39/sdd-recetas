"""
Admin: category management (/api/admin/categories).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Category, Recipe
from app.schemas.admin import CategoryAdminCreate, CategoryAdminUpdate

router = APIRouter()


@router.get("", summary="List categories (admin)")
async def list_categories(
    search: str | None = Query(None),
    is_active: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if search:
        term = f"%{search}%"
        filters.append(or_(Category.name.ilike(term), Category.slug.ilike(term)))
    if is_active is not None:
        filters.append(Category.is_active == is_active)

    base = select(Category).where(*filters)
    total = await db.scalar(select(func.count()).select_from(Category).where(*filters))
    result = await db.execute(
        base.order_by(Category.sort_order, Category.name)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    items = result.scalars().all()
    return {
        "items": [
            {
                "id": str(c.id),
                "slug": c.slug,
                "name": c.name,
                "description": c.description,
                "icon": c.icon,
                "color": c.color,
                "sort_order": c.sort_order,
                "is_active": c.is_active,
            }
            for c in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("", status_code=201, summary="Create category (admin)")
async def create_category(
    data: CategoryAdminCreate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    exists = await db.scalar(select(Category.id).where(Category.slug == data.slug))
    if exists:
        raise HTTPException(status_code=400, detail="Category slug already exists")
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return {"id": str(category.id), "slug": category.slug, "name": category.name}


@router.patch("/{category_id}", summary="Update category (admin)")
async def update_category(
    category_id: UUID,
    data: CategoryAdminUpdate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return {"id": str(category.id), "slug": category.slug, "name": category.name, "is_active": category.is_active}


@router.delete("/{category_id}", summary="Delete or deactivate category (admin)")
async def delete_category(
    category_id: UUID,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    recipe_count = await db.scalar(
        select(func.count()).select_from(Recipe).where(Recipe.category_id == category.id)
    )
    if recipe_count and recipe_count > 0:
        category.is_active = False
        await db.commit()
        return {"deleted": False, "deactivated": True, "recipes": recipe_count}

    await db.delete(category)
    await db.commit()
    return {"deleted": True, "deactivated": False, "recipes": 0}
