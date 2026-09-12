"""
Tag endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import Tag, RecipeTag

router = APIRouter()


@router.get("", summary="List tags")
async def list_tags(
    query: Optional[str] = Query(None, description="Search tags by name"),
    limit: int = 20,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Search tags with autocomplete."""
    stmt = select(Tag).where(Tag.usage_count > 0)

    if query:
        search_term = f"%{query}%"
        stmt = stmt.where(Tag.slug.ilike(search_term) | Tag.name.ilike(search_term))

    stmt = stmt.order_by(Tag.usage_count.desc(), Tag.name).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/popular", summary="Get most popular tags")
async def popular_tags(
    limit: int = 20,
    db = Depends(get_db),
):
    """Get most used tags."""
    result = await db.execute(
        select(Tag)
        .where(Tag.usage_count > 0)
        .order_by(Tag.usage_count.desc())
        .limit(limit)
    )
    return result.scalars().all()