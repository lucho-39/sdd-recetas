"""
Admin: ingredient catalog management (/api/admin/ingredients).
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import record_audit
from app.core.database import get_db
from app.core.security import require_admin
from app.core.units import VALID_CATEGORIES, VALID_UNITS
from app.models import Ingredient, Recipe, User
from app.schemas.admin import (
    IngredientMergeRequest,
    IngredientNormalizeRequest,
    IngredientRecoverRequest,
    IngredientRejectRequest,
)
from app.services.notifications import notify_ingredient_creator

router = APIRouter()


def _usage_count_expr():
    """Correlated count of live recipes referencing this ingredient.

    Recipes embed the id inside a JSONB array — there is no join table and no
    foreign key — so usage_count is counted on read instead of stored. The
    merge endpoint already rewrites those ids to the target, which makes the
    official ingredient absorb the duplicate's count with no bookkeeping.
    """
    reference = func.jsonb_build_array(
        func.jsonb_build_object("ingredient_id", cast(Ingredient.id, String))
    )
    return (
        select(func.count())
        .select_from(Recipe)
        .where(
            Recipe.deleted_at.is_(None),
            Recipe.ingredients.op("@>")(reference),
        )
        .correlate(Ingredient)
        .scalar_subquery()
        .label("usage_count")
    )


def _serialize(ing: Ingredient, usage_count: int = 0) -> dict:
    return {
        "id": str(ing.id),
        "slug": ing.slug,
        "name": ing.name,
        "category": ing.category,
        "default_unit": ing.default_unit,
        "allowed_units": ing.allowed_units or [],
        "aliases": ing.aliases or [],
        "usage_count": usage_count,
        "is_active": ing.is_active,
        "validated_by_admin": ing.validated_by_admin,
        "validated_by": str(ing.validated_by) if ing.validated_by else None,
        "validated_at": ing.validated_at,
        "rejected": ing.rejected,
        "rejection_reason": ing.rejection_reason,
        "rejected_by": str(ing.rejected_by) if ing.rejected_by else None,
        "rejected_at": ing.rejected_at,
        "merged_into": str(ing.merged_into) if ing.merged_into else None,
        "created_by": str(ing.created_by) if ing.created_by else None,
        "created_by_email": ing.created_by_user.email if ing.created_by_user else None,
        "created_at": ing.created_at,
    }


async def _usage_count_for(db: AsyncSession, ingredient_id: UUID) -> int:
    """Same count as _usage_count_expr, for the single-ingredient routes."""
    reference = func.jsonb_build_array(
        func.jsonb_build_object("ingredient_id", str(ingredient_id))
    )
    return await db.scalar(
        select(func.count())
        .select_from(Recipe)
        .where(
            Recipe.deleted_at.is_(None),
            Recipe.ingredients.op("@>")(reference),
        )
    ) or 0


async def _get_ingredient(db: AsyncSession, ingredient_id: UUID) -> Ingredient | None:
    """Load an ingredient with its creator so _serialize can show the email.

    Without this every single-ingredient route would lazy-load the relation
    and trip over SQLAlchemy's async detached-instance guard.
    """
    result = await db.execute(
        select(Ingredient)
        .where(Ingredient.id == ingredient_id)
        .options(selectinload(Ingredient.created_by_user))
    )
    return result.scalar_one_or_none()


async def _list(
    db: AsyncSession,
    *conditions,
    search: str | None,
    category: str | None,
    page: int,
    limit: int,
    sort: str = "name",
):
    filters = [
        # A merged duplicate is no longer manageable: it belongs to no queue.
        Ingredient.merged_into.is_(None),
        *conditions,
    ]
    if search:
        term = f"%{search}%"
        filters.append(or_(Ingredient.name.ilike(term), Ingredient.slug.ilike(term)))
    if category:
        filters.append(Ingredient.category == category)

    usage_count = _usage_count_expr()
    total = await db.scalar(select(func.count()).select_from(Ingredient).where(*filters))
    order = (
        (usage_count.desc(), Ingredient.name.asc())
        if sort == "usage"
        else (Ingredient.name.asc(),)
    )
    result = await db.execute(
        select(Ingredient, usage_count)
        .where(*filters)
        .options(selectinload(Ingredient.created_by_user))
        .order_by(*order)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return {
        "items": [
            _serialize(ing, usage_count=usage or 0)
            for ing, usage in result.all()
        ],
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
    sort: str = Query("usage", pattern="^(usage|name)$"),
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
        sort=sort,
    )


@router.get("/validated", summary="Validated ingredients (admin)")
async def list_validated(
    search: str | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("usage", pattern="^(usage|name)$"),
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
        sort=sort,
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
    ingredient = await _get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient.validated_by_admin = True
    ingredient.validated_at = datetime.utcnow()
    ingredient.validated_by = admin.id
    ingredient.rejected = False
    ingredient.is_active = True
    await record_audit(
        db,
        admin.id,
        "ingredient.validate",
        target_type="ingredient",
        target_id=str(ingredient.id),
    )
    await db.commit()
    await db.refresh(ingredient)
    usage = await _usage_count_for(db, ingredient.id)
    return _serialize(ingredient, usage_count=usage)


@router.post("/{ingredient_id}/reject", summary="Reject ingredient (admin)")
async def reject_ingredient(
    ingredient_id: UUID,
    data: IngredientRejectRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    ingredient = await _get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient.rejected = True
    ingredient.rejection_reason = data.reason
    ingredient.rejected_by = admin.id
    ingredient.rejected_at = datetime.utcnow()
    ingredient.is_active = False
    await record_audit(
        db,
        admin.id,
        "ingredient.reject",
        target_type="ingredient",
        target_id=str(ingredient.id),
        detail={"reason": data.reason},
    )
    await db.commit()
    await db.refresh(ingredient)
    # UC-016 AC3: after the commit so a notification failure cannot undo the
    # rejection. Same call shape as favorites/ratings.
    await notify_ingredient_creator(db, actor=admin, ingredient=ingredient, reason=data.reason)
    usage = await _usage_count_for(db, ingredient.id)
    return _serialize(ingredient, usage_count=usage)


@router.post("/{ingredient_id}/merge", summary="Merge ingredient into another (admin)")
async def merge_ingredient(
    ingredient_id: UUID,
    data: IngredientMergeRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Reassign every recipe reference from the source ingredient to the target
    and retire the duplicate (UC-ADMIN-015 AC2).

    The duplicate is soft-deleted, not deleted: `is_active=false` takes it out
    of the public catalog and `merged_into` records where it went so the merge
    stays auditable. The aliases are unioned into the target first.
    """
    if ingredient_id == data.target_id:
        raise HTTPException(status_code=400, detail="Cannot merge an ingredient into itself")

    source = await db.get(Ingredient, ingredient_id)
    target = await db.get(Ingredient, data.target_id)
    if not source or not target:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    result = await db.execute(
        select(Recipe).where(Recipe.ingredients.contains([{"ingredient_id": str(source.id)}]))
    )
    recipes_updated = 0
    for recipe in result.scalars().all():
        changed = False
        new_items = []
        for item in recipe.ingredients or []:
            if item.get("ingredient_id") == str(source.id):
                item = {**item, "ingredient_id": str(target.id), "name": target.name}
                changed = True
            new_items.append(item)
        if changed:
            recipe.ingredients = new_items
            recipes_updated += 1

    existing_aliases = target.aliases or []
    merged_aliases = list(
        dict.fromkeys([*existing_aliases, *(source.aliases or [])])
    )
    if merged_aliases != existing_aliases:
        target.aliases = merged_aliases

    await record_audit(
        db,
        admin.id,
        "ingredient.merge",
        target_type="ingredient",
        target_id=str(source.id),
        detail={
            "target_id": str(target.id),
            "recipes_updated": recipes_updated,
            "aliases_added": [a for a in merged_aliases if a not in existing_aliases],
        },
    )
    source.is_active = False
    source.merged_into = target.id
    await db.commit()
    target_usage = await _usage_count_for(db, target.id)
    return {
        "merged": True,
        "source_id": str(ingredient_id),
        "target_id": str(target.id),
        "recipes_updated": recipes_updated,
        "aliases_added": [a for a in merged_aliases if a not in existing_aliases],
        "target_usage_count": target_usage,
    }


@router.post("/{ingredient_id}/normalize", summary="Normalize ingredient (admin)")
async def normalize_ingredient(
    ingredient_id: UUID,
    data: IngredientNormalizeRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    ingredient = await _get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # UC-ADMIN-019 AC2: the slug feeds every recipe link and the public
    # autocomplete keys off category/unit, so a bad value here breaks the
    # public site long after the modal is closed.
    if data.slug is not None and data.slug != ingredient.slug:
        duplicate = await db.scalar(select(Ingredient.id).where(Ingredient.slug == data.slug))
        if duplicate:
            raise HTTPException(status_code=400, detail="Slug already in use")

    if data.category is not None and data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {data.category}")

    if data.default_unit is not None and data.default_unit not in VALID_UNITS:
        raise HTTPException(status_code=400, detail=f"Invalid unit: {data.default_unit}")

    # RF-12.8: the whitelist feeds validate_ingredients(), so a typo here
    # would silently lock every recipe out of that unit.
    if data.allowed_units is not None:
        invalid = [u for u in data.allowed_units if u not in VALID_UNITS]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid allowed units: {', '.join(sorted(invalid))}",
            )

    update_data = data.model_dump(exclude_unset=True, exclude={"mark_validated"})
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    if data.mark_validated:
        ingredient.validated_by_admin = True
        ingredient.validated_at = datetime.utcnow()
        ingredient.validated_by = admin.id
        ingredient.rejected = False
        ingredient.is_active = True

    await record_audit(
        db,
        admin.id,
        "ingredient.normalize",
        target_type="ingredient",
        target_id=str(ingredient.id),
        detail=update_data,
    )
    await db.commit()
    await db.refresh(ingredient)
    usage = await _usage_count_for(db, ingredient.id)
    return _serialize(ingredient, usage_count=usage)


@router.post("/{ingredient_id}/desvalidate", summary="Desvalidate ingredient (admin)")
async def desvalidate_ingredient(
    ingredient_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """UC-ADMIN-017 AC3: move a validated ingredient back to the pending queue.

    The ingredient stays active so recipes using it keep resolving; it just
    loses its official-catalogue status until it is reviewed again.
    """
    ingredient = await _get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    if not ingredient.validated_by_admin:
        raise HTTPException(status_code=400, detail="Ingredient is not validated")

    ingredient.validated_by_admin = False
    ingredient.validated_at = None
    ingredient.validated_by = None

    await record_audit(
        db,
        admin.id,
        "ingredient.desvalidate",
        target_type="ingredient",
        target_id=str(ingredient.id),
    )
    await db.commit()
    await db.refresh(ingredient)
    usage = await _usage_count_for(db, ingredient.id)
    return _serialize(ingredient, usage_count=usage)


@router.post("/{ingredient_id}/recover", summary="Recover rejected ingredient (admin)")
async def recover_ingredient(
    ingredient_id: UUID,
    data: IngredientRecoverRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """UC-ADMIN-018 AC3: move a rejected ingredient back to pending with a reason.

    The rejection fields are cleared (they describe the rejected state, not the
    transition) and the reason travels to the audit log instead.
    """
    ingredient = await _get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    if not ingredient.rejected:
        raise HTTPException(status_code=400, detail="Ingredient is not rejected")

    ingredient.rejected = False
    ingredient.rejection_reason = None
    ingredient.rejected_by = None
    ingredient.rejected_at = None
    ingredient.is_active = True

    await record_audit(
        db,
        admin.id,
        "ingredient.recover",
        target_type="ingredient",
        target_id=str(ingredient.id),
        detail={"reason": data.reason},
    )
    await db.commit()
    await db.refresh(ingredient)
    usage = await _usage_count_for(db, ingredient.id)
    return _serialize(ingredient, usage_count=usage)


@router.get(
    "/{ingredient_id}/usages",
    summary="Recipes using an ingredient (admin)",
)
async def list_ingredient_usages(
    ingredient_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """UC-ADMIN-017 AC3: show which recipes reference this ingredient.

    The same JSONB containment the count uses, but returning the rows so an
    admin can see where the ingredient is actually being used before
    deciding to desvalidate it.
    """
    if not await db.get(Ingredient, ingredient_id):
        raise HTTPException(status_code=404, detail="Ingredient not found")

    reference = func.jsonb_build_array(
        func.jsonb_build_object("ingredient_id", str(ingredient_id))
    )
    contains = Recipe.ingredients.op("@>")(reference)
    live = Recipe.deleted_at.is_(None)

    total = await db.scalar(
        select(func.count()).select_from(Recipe).where(live, contains)
    )
    result = await db.execute(
        select(Recipe)
        .where(live, contains)
        .order_by(Recipe.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .options(selectinload(Recipe.author))
    )
    return {
        "items": [
            {
                "id": str(r.id),
                "slug": r.slug,
                "title": r.title,
                "is_public": r.is_public,
                "author": r.author.display_name if r.author else None,
                "author_id": str(r.author_id),
                "created_at": r.created_at,
            }
            for r in result.scalars().all()
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }
