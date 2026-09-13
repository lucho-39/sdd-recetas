"""
Notification endpoints (in-app notification center).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete as sql_delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import Notification

router = APIRouter()


def _serialize(notification: Notification) -> dict:
    actor = notification.actor
    recipe = notification.recipe
    return {
        "id": str(notification.id),
        "type": notification.type,
        "recipe_id": str(notification.recipe_id),
        "recipe_slug": recipe.slug if recipe else None,
        "recipe_title": recipe.title if recipe else None,
        "actor": (
            {
                "id": str(actor.id),
                "display_name": actor.display_name,
                "avatar_url": actor.avatar_url,
            }
            if actor
            else None
        ),
        "detail": notification.detail,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
    }


async def _unread_count(db: AsyncSession, user_id: UUID) -> int:
    return (
        await db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        )
    ) or 0


@router.get("", summary="List my notifications")
async def list_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    total = await db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == current_user.id)
    )
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .options(selectinload(Notification.recipe), selectinload(Notification.actor))
    )
    return {
        "items": [_serialize(n) for n in result.scalars().all()],
        "total": total or 0,
        "unread_count": await _unread_count(db, current_user.id),
        "page": page,
        "limit": limit,
    }


@router.get("/unread-count", summary="Unread notifications count")
async def unread_count(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return {"unread_count": await _unread_count(db, current_user.id)}


@router.post("/read-all", summary="Mark all my notifications as read")
async def mark_all_read(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id, Notification.is_read == False  # noqa: E712
        )
    )
    notifications = result.scalars().all()
    for notification in notifications:
        notification.is_read = True
    await db.commit()
    return {"updated": len(notifications)}


@router.post("/{notification_id}/read", summary="Mark a notification as read")
async def mark_read(
    notification_id: UUID,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    notification = await db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    await db.commit()
    return {"message": "Notification marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    notification = await db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.delete(notification)
    await db.commit()
    return None


@router.delete("", summary="Delete all my notifications")
async def delete_all_notifications(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        sql_delete(Notification).where(Notification.user_id == current_user.id)
    )
    await db.commit()
    return {"deleted": result.rowcount or 0}
