"""
Notification service: persist likes/ratings notifications and push them live.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, Recipe, User
from app.realtime.server import emit_notification


def build_payload(
    notification: Notification, recipe: Recipe, actor: Optional[User]
) -> Dict[str, Any]:
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
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


async def notify_recipe_author(
    db: AsyncSession,
    *,
    actor: User,
    recipe: Recipe,
    type: str,
    detail: Optional[Dict[str, Any]] = None,
) -> Optional[Notification]:
    """Notify the recipe author about an action performed by ``actor``.

    Self-actions are ignored. Repeating the same action refreshes the existing
    notification instead of creating duplicates. The notification is committed
    and then pushed over Socket.IO to every connected socket of the author.
    """
    recipient_id = recipe.author_id
    if recipient_id == actor.id:
        return None

    existing = (
        await db.execute(
            select(Notification).where(
                Notification.user_id == recipient_id,
                Notification.actor_id == actor.id,
                Notification.recipe_id == recipe.id,
                Notification.type == type,
            )
        )
    ).scalar_one_or_none()

    if existing is not None:
        existing.is_read = False
        existing.detail = detail
        existing.created_at = datetime.utcnow()
        notification = existing
    else:
        notification = Notification(
            user_id=recipient_id,
            actor_id=actor.id,
            recipe_id=recipe.id,
            type=type,
            detail=detail,
            is_read=False,
        )
        db.add(notification)

    await db.commit()
    await db.refresh(notification)

    await emit_notification(str(recipient_id), build_payload(notification, recipe, actor))
    return notification
