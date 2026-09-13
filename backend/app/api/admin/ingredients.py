"""
Admin: ingredient catalog management (/api/admin/ingredients).
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Ingredient, User
from app.schemas.admin import IngredientNormalizeRequest, IngredientRejectRequest

router = APIRouter()


def _serialize(ing: Ingredient) -> dict:
    return {
        "id": str(ing.id),
        "slug": ing.slug,
        "name": ing.name,
        "category": ing.category,
        "default_unit": ing.default_unit,
        "aliases": ing.aliases or [],
        "is_active": ing.is_active,
        "validated_by_admin": ing.validated_by_admin,
        "validated_at": ing.validated_at,
        "rejected": ing.rejected,
        "rejection_reason": ing.rejection_reason,
        "created_at": ing.created_at,
    }


async def _list(
    db: AsyncSession,
    *conditions,
    search: str | None,
    category: str | None,
    page: int,
    limit: int,
):
    filters = list(conditions)
    if search:
        term = f"%{search}%"
        filters.append(or_(Ingredient.name.ilike(term), Ingredient.slug.ilike(term)))
    if category:
        filters.append(Ingredient.category == category)

    total = await db.scalar(select(func.count()).select_from(Ingredient).where(*filters))
    result = await db.execute(
        select(Ingredient)
        .where(*filters)
        .order_by(Ingredient.name)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return {
        "items": [_serialize(i) for i in result.scalars().all()],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/pending", summary="Ingredients pending validation (admin)")
async def list_pending(
    search: str | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await _list(
        db,
        Ingredient.validated_by_admin == False,  # noqa: E712
        Ingredient.rejected == False,  # noqa: E712
        search=search,
        category=category,
        page=page,
        limit=limit,
    )


@router.get("/validated", summary="Validated ingredients (admin)")
async def list_validated(
    search: str | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await _list(
        db,
        Ingredient.validated_by_admin == True,  # noqa: E712
        search=search,
        category=category,
        page=page,
        limit=limit,
    )


@router.get("/rejected", summary="Rejected ingredients (admin)")
async def list_rejected(
    search: str | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await _list(
        db,
        Ingredient.rejected == True,  # noqa: E712
        search=search,
        category=category,
        page=page,
        limit=limit,
    )


@router.post("/{ingredient_id}/validate", summary="Validate ingredient (admin)")
async def validate_ingredient(
    ingredient_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    ingredient = await db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient.validated_by_admin = True
    ingredient.validated_at = datetime.utcnow()
    ingredient.validated_by = admin.id
    ingredient.rejected = False
    ingredient.is_active = True
    await db.commit()
    await db.refresh(ingredient)
    return _serialize(ingredient)


@router.post("/{ingredient_id}/reject", summary="Reject ingredient (admin)")
async def reject_ingredient(
    ingredient_id: UUID,
    data: IngredientRejectRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    ingredient = await db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient.rejected = True
    ingredient.rejection_reason = data.reason
    ingredient.rejected_by = admin.id
    ingredient.rejected_at = datetime.utcnow()
    ingredient.is_active = False
    await db.commit()
    await db.refresh(ingredient)
    return _serialize(ingredient)


@router.post("/{ingredient_id}/normalize", summary="Normalize ingredient (admin)")
async def normalize_ingredient(
    ingredient_id: UUID,
    data: IngredientNormalizeRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    ingredient = await db.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    update_data = data.model_dump(exclude_unset=True, exclude={"mark_validated"})
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    if data.mark_validated:
        ingredient.validated_by_admin = True
        ingredient.validated_at = datetime.utcnow()
        ingredient.validated_by = admin.id
        ingredient.rejected = False
        ingredient.is_active = True

    await db.commit()
    await db.refresh(ingredient)
    return _serialize(ingredient)
