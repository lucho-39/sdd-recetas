"""
Visit tracking endpoints
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user, create_visitor_fingerprint
from app.models import Visit, Recipe

router = APIRouter()


@router.post("/{recipe_id}", status_code=201)
async def record_visit(
    recipe_id: str,
    request: Request,
    db = Depends(get_db),
):
    """Record a recipe visit (handles both authenticated and anonymous users)."""
    from app.models import Recipe, Visit

    # Verify recipe exists
    recipe = await db.get(Recipe, recipe_id)
    if not recipe or recipe.deleted_at:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Generate visitor fingerprint for anonymous users
    fingerprint = create_visitor_fingerprint(request)

    # Check if this visitor already visited today
    existing_result = await db.execute(
        select(Visit).where(
            Visit.recipe_id == recipe_id,
            Visit.visitor_fingerprint == fingerprint,
            func.date(Visit.visited_at) == datetime.utcnow().date()
        )
    )
    existing = existing_result.scalar_one_or_none()

    if not existing:
        visit = Visit(
            recipe_id=recipe_id,
            user_id=None,  # Would be set if authenticated
            visitor_fingerprint=fingerprint,
        )
        db.add(visit)
        recipe.visit_count += 1
        await db.commit()

    return {"message": "Visit recorded"}