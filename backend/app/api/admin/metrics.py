"""
Admin: dashboard metrics (/api/admin/metrics).
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Category, Ingredient, Rating, Recipe, Tag, User, Visit
from app.schemas.admin import DashboardStats

router = APIRouter()


async def _count(db: AsyncSession, model, *conditions) -> int:
    value = await db.scalar(select(func.count()).select_from(model).where(*conditions))
    return value or 0


@router.get("/dashboard", response_model=DashboardStats, summary="Dashboard KPIs (admin)")
async def dashboard(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return DashboardStats(
        users_total=await _count(db, User),
        users_active=await _count(db, User, User.is_active == True),  # noqa: E712
        recipes_total=await _count(db, Recipe),
        recipes_public=await _count(db, Recipe, Recipe.is_public == True),  # noqa: E712
        recipes_deleted=await _count(db, Recipe, Recipe.deleted_at.is_not(None)),
        ingredients_total=await _count(db, Ingredient),
        ingredients_pending=await _count(
            db,
            Ingredient,
            Ingredient.validated_by_admin == False,  # noqa: E712
            Ingredient.rejected == False,  # noqa: E712
        ),
        categories_total=await _count(db, Category),
        tags_total=await _count(db, Tag),
        ratings_total=await _count(db, Rating),
        visits_total=await _count(db, Visit),
    )
