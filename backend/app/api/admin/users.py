"""
Admin: user management (/api/admin/users).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.database import get_db
from app.core.security import require_admin
from app.models import User, UserRole
from app.schemas.admin import UserAdminUpdate, UserAdminListItem
from app.schemas.auth import UserResponse

router = APIRouter()


def _to_item(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
    }


@router.get("", summary="List users (admin)")
async def list_users(
    search: str | None = Query(None),
    is_active: bool | None = Query(None),
    role: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if search:
        term = f"%{search}%"
        filters.append(or_(User.email.ilike(term), User.display_name.ilike(term)))
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if role in ("user", "admin"):
        filters.append(User.role == UserRole(role))

    total = await db.scalar(select(func.count()).select_from(User).where(*filters))
    result = await db.execute(
        select(User)
        .where(*filters)
        .order_by(User.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    users = result.scalars().all()
    return {
        "items": [_to_item(u) for u in users],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{user_id}", response_model=UserResponse, summary="User detail (admin)")
async def get_user(
    user_id: UUID,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/activate", summary="Activate user (admin)")
async def activate_user(
    user_id: UUID,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    user.is_verified = True
    await record_audit(db, admin.id, "user.activate", target_type="user", target_id=str(user.id))
    await db.commit()
    return _to_item(user)


@router.post("/{user_id}/deactivate", summary="Deactivate user (admin)")
async def deactivate_user(
    user_id: UUID,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await record_audit(db, admin.id, "user.deactivate", target_type="user", target_id=str(user.id))
    await db.commit()
    return _to_item(user)


@router.patch("/{user_id}/role", summary="Change user role (admin)")
async def change_role(
    user_id: UUID,
    data: UserAdminUpdate,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.role is not None:
        user.role = UserRole(data.role)
    if data.is_verified is not None:
        user.is_verified = data.is_verified
    await record_audit(
        db,
        admin.id,
        "user.update",
        target_type="user",
        target_id=str(user.id),
        detail=data.model_dump(exclude_unset=True),
    )
    await db.commit()
    return _to_item(user)
