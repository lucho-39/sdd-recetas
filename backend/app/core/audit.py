"""
Audit trail helper for administrative actions.
"""
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def record_audit(
    db: AsyncSession,
    actor_id: Optional[UUID],
    action: str,
    *,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    detail: Optional[dict[str, Any]] = None,
) -> None:
    """Insert an audit entry; the caller is responsible for committing."""
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            detail=detail,
        )
    )
