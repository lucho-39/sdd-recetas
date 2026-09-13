"""
Admin: dashboard metrics (/api/admin/metrics).
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Category, Ingredient, Rating, Recipe, Tag, User, Visit
from app.schemas.admin import DashboardStats

router = APIRouter()

_MONTHS_ES = [
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
]


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


def _month_start(d: datetime) -> datetime:
    return d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _add_months(d: datetime, n: int) -> datetime:
    month = d.month - 1 + n
    year = d.year + month // 12
    month = month % 12 + 1
    return d.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)


def _week_start(d: datetime) -> datetime:
    start = d - timedelta(days=d.weekday())
    return start.replace(hour=0, minute=0, second=0, microsecond=0)


@router.get("/recipes-series", summary="Recipes created per month/week (admin)")
async def recipes_series(
    interval: str = Query("month", pattern="^(month|week)$"),
    periods: int = Query(12, ge=1, le=52),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Return the number of recipes created per month or per week.

    The series always has ``periods`` buckets (oldest first), filling gaps
    with zero so the chart has a stable x-axis.
    """
    trunc = "month" if interval == "month" else "week"
    bucket = func.date_trunc(trunc, Recipe.created_at)
    result = await db.execute(
        select(bucket.label("bucket"), func.count().label("count"))
        .group_by(bucket)
        .order_by(bucket)
    )

    counts: dict = {}
    for raw_key, count in result.all():
        key = raw_key.date() if isinstance(raw_key, datetime) else raw_key
        counts[key] = count

    now = datetime.utcnow()
    series = []
    for i in range(periods - 1, -1, -1):
        if interval == "month":
            start = _add_months(_month_start(now), -i)
            label = f"{_MONTHS_ES[start.month - 1]} {start.year}"
        else:
            start = _week_start(now) - timedelta(weeks=i)
            label = f"{start.day:02d}/{start.month:02d}"
        series.append({"label": label, "count": counts.get(start.date(), 0)})

    return {"interval": interval, "series": series}
