"""
Category endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import Category

router = APIRouter()


@router.get("", summary="List categories")
async def list_categories(
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """List all categories."""
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.sort_order, Category.name)
    )
    return result.scalars().all()


@router.get("/{slug}", summary="Get category by slug")
async def get_category(
    slug: str,
    db = Depends(get_db),
):
    """Get category by slug."""
    result = await db.execute(
        select(Category).where(Category.slug == slug, Category.is_active == True)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category