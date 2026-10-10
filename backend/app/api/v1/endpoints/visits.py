"""
Visit tracking endpoints
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_visitor_fingerprint, get_current_user_optional
from app.models import Visit, Recipe

router = APIRouter()


@router.post("/{recipe_id}", status_code=201)
async def record_visit(
    recipe_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """RB-04: record at most one visit per recipe per visitor per calendar day.

    Authenticated visitors are identified by ``user_id``; anonymous ones by the
    ``visitor_fingerprint`` derived from IP + User-Agent. Repeated calls the
    same day (F5/refresh) are a no-op and do not bump ``recipes.visit_count``.
    """
    recipe = await db.get(Recipe, recipe_id)
    if not recipe or recipe.deleted_at:
        raise HTTPException(status_code=404, detail="Recipe not found")

    fingerprint = create_visitor_fingerprint(request)
    today = func.date(Visit.visited_at) == datetime.now(timezone.utc).date()

    conditions = [Visit.recipe_id == recipe_id, today]
    if current_user is not None:
        conditions.append(Visit.user_id == current_user.id)
    else:
        conditions.append(Visit.visitor_fingerprint == fingerprint)

    existing = await db.execute(select(Visit).where(*conditions))
    if existing.scalar_one_or_none() is not None:
        return {"message": "Visit already recorded today"}

    db.add(
        Visit(
            recipe_id=recipe_id,
            user_id=current_user.id if current_user is not None else None,
            visitor_fingerprint=fingerprint,
        )
    )
    recipe.visit_count += 1
    await db.commit()

    return {"message": "Visit recorded"}
