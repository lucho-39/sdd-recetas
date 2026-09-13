"""
Admin: audit log (/api/admin/audit-log).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models import AuditLog, User

router = APIRouter()


@router.get("", summary="List audit log (admin)")
async def list_audit_log(
    action: str | None = Query(None, description="Filter by action (partial match)"),
    target_type: str | None = Query(None, description="Filter by target type"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if action:
        filters.append(AuditLog.action.ilike(f"%{action}%"))
    if target_type:
        filters.append(AuditLog.target_type == target_type)

    total = await db.scalar(select(func.count()).select_from(AuditLog).where(*filters))

    result = await db.execute(
        select(AuditLog, User.display_name)
        .outerjoin(User, AuditLog.actor_id == User.id)
        .where(*filters)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    items = [
        {
            "id": str(log.id),
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "actor_name": actor_name,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "detail": log.detail,
            "created_at": log.created_at,
        }
        for log, actor_name in result.all()
    ]

    return {"items": items, "total": total, "page": page, "limit": limit}
