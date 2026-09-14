"""
Ingredient endpoints
"""
import re
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_, cast, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.models import Ingredient

router = APIRouter()

VALID_CATEGORIES = {"proteina", "verdura", "fruta", "lacteo", "grano", "condimento", "grasa", "otro"}
VALID_UNITS = {"g", "kg", "ml", "l", "unidad", "cucharada", "cucharadita", "taza", "pizca"}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text, flags=re.UNICODE)
    return re.sub(r"^-+|-+$", "", text)


class IngredientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: str = Field("otro", max_length=30)
    default_unit: str = Field("unidad", max_length=20)
    aliases: List[str] = Field(default_factory=list)


def _serialize(ingredient: Ingredient) -> dict:
    return {
        "id": str(ingredient.id),
        "slug": ingredient.slug,
        "name": ingredient.name,
        "category": ingredient.category,
        "default_unit": ingredient.default_unit,
        "aliases": ingredient.aliases or [],
        "is_active": ingredient.is_active,
        "validated_by_admin": ingredient.validated_by_admin,
    }


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


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create an ingredient")
async def create_ingredient(
    data: IngredientCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a catalog ingredient (pending admin validation).

    If the slug already exists the existing ingredient is returned, so the
    selector can safely reuse it.
    """
    if data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    if data.default_unit not in VALID_UNITS:
        raise HTTPException(status_code=400, detail="Invalid default unit")

    slug = slugify(data.name)
    if not slug:
        raise HTTPException(status_code=400, detail="Invalid name")

    existing = await db.scalar(select(Ingredient).where(Ingredient.slug == slug))
    if existing is not None:
        return _serialize(existing)

    ingredient = Ingredient(
        slug=slug,
        name=data.name.strip(),
        category=data.category,
        default_unit=data.default_unit,
        aliases=data.aliases or [],
        is_active=True,
        validated_by_admin=False,
        created_by=current_user.id,
    )
    db.add(ingredient)
    await db.commit()
    await db.refresh(ingredient)
    return _serialize(ingredient)


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