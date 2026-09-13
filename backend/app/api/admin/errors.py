"""
Admin: error log (/api/admin/error-log).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models import ErrorLog

router = APIRouter()


@router.get("", summary="List error log (admin)")
async def list_error_log(
    status_code: int | None = Query(None),
    path: str | None = Query(None, description="Filter by path (partial match)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if status_code:
        filters.append(ErrorLog.status_code == status_code)
    if path:
        filters.append(ErrorLog.path.ilike(f"%{path}%"))

    total = await db.scalar(select(func.count()).select_from(ErrorLog).where(*filters))
    result = await db.execute(
        select(ErrorLog)
        .where(*filters)
        .order_by(ErrorLog.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    items = [
        {
            "id": str(entry.id),
            "path": entry.path,
            "method": entry.method,
            "status_code": entry.status_code,
            "message": entry.message,
            "created_at": entry.created_at,
        }
        for entry in result.scalars().all()
    ]
    return {"items": items, "total": total, "page": page, "limit": limit}
