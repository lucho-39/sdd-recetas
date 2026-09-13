"""
Ingredient endpoints
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_, cast, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.models import Ingredient

router = APIRouter()


@router.get("", summary="Search ingredients")
async def search_ingredients(
    query: Optional[str] = Query(None, description="Search ingredients"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = 20,
    db = Depends(get_db),
    current_user = Depends(get_current_user_optional),
):
    """Autocomplete search for ingredients (public read)."""
    query_stmt = select(Ingredient).where(Ingredient.is_active == True)

    if query:
        search_term = f"%{query}%"
        query_stmt = query_stmt.where(
            or_(
                Ingredient.name.ilike(search_term),
                Ingredient.slug.ilike(search_term),
                cast(Ingredient.aliases, Text).ilike(search_term),
            )
        )

    if category:
        query_stmt = query_stmt.where(Ingredient.category == category)

    query_stmt = query_stmt.order_by(Ingredient.name).limit(limit)
    result = await db.execute(query_stmt)
    return result.scalars().all()


@router.get("/categories", summary="List ingredient categories")
async def list_categories(
    db = Depends(get_db),
):
    """List ingredient categories with counts."""
    result = await db.execute(
        select(Ingredient.category, func.count(Ingredient.id).label("count"))
        .where(Ingredient.is_active == True)
        .group_by(Ingredient.category)
        .order_by(func.count(Ingredient.id).desc())
    )
    return [{"category": row[0], "count": row[1]} for row in result.all()]


@router.get("/{ingredient_id}", summary="Get ingredient by ID")
async def get_ingredient(
    ingredient_id: UUID,
    db = Depends(get_db),
    current_user = Depends(get_current_user_optional),
):
    """Get ingredient by ID (public reference data)."""
    result = await db.execute(
        select(Ingredient).where(Ingredient.id == ingredient_id, Ingredient.is_active == True)
    )
    ingredient = result.scalar_one_or_none()

    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    return ingredient