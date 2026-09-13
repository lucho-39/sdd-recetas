"""
Notification service: persist likes/ratings notifications, honour per-user
preferences and push them live over Socket.IO (email channel included).
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.app_settings import current_settings
from app.models import Notification, NotificationPreference, Recipe, User
from app.realtime.server import emit_notification
from app.services.email import send_email
from app.services.webpush import send_web_push

DEFAULT_PREFERENCES: Dict[str, bool] = {
    "in_app_enabled": True,
    "email_enabled": False,
    "push_enabled": False,
    "favorites_enabled": True,
    "ratings_enabled": True,
}

_EVENT_FIELD = {
    "favorite": "favorites_enabled",
    "rating": "ratings_enabled",
}


async def get_preferences(db: AsyncSession, user_id: UUID) -> Dict[str, bool]:
    """Return the user's preferences, falling back to the defaults."""
    preference = await db.get(NotificationPreference, user_id)
    if preference is None:
        return dict(DEFAULT_PREFERENCES)
    return {
        "in_app_enabled": preference.in_app_enabled,
        "email_enabled": preference.email_enabled,
        "push_enabled": preference.push_enabled,
        "favorites_enabled": preference.favorites_enabled,
        "ratings_enabled": preference.ratings_enabled,
    }


def build_payload(
    notification: Optional[Notification], recipe: Recipe, actor: Optional[User], detail: Optional[dict]
) -> Dict[str, Any]:
    return {
        "id": str(notification.id) if notification else None,
        "type": notification.type if notification else None,
        "recipe_id": str(recipe.id),
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
        "detail": notification.detail if notification else detail,
        "is_read": notification.is_read if notification else False,
        "created_at": (
            notification.created_at.isoformat()
            if notification and notification.created_at
            else datetime.utcnow().isoformat()
        ),
    }


def _message(type: str, actor: User, recipe: Recipe, detail: Optional[dict]) -> str:
    """Human-readable notification message (shared wording with the UI)."""
    who = actor.display_name
    title = recipe.title
    if type == "rating":
        score = (detail or {}).get("score")
        if score:
            stars = "estrella" if score == 1 else "estrellas"
            return (
                f"Tu receta '{title}' recibió una calificación de {score} {stars} "
                f"de parte de '{who}'"
            )
        return f"Tu receta '{title}' recibió una calificación de parte de '{who}'"
    return f"'{who}' guardó tu receta '{title}'"


def _context(actor: User, recipe: Recipe, detail: Optional[dict]) -> Dict[str, Any]:
    score = (detail or {}).get("score")
    stars = f"{score} {'estrella' if score == 1 else 'estrellas'}" if score else ""
    return {
        "actor": actor.display_name,
        "recipe": recipe.title,
        "score": score if score is not None else "",
        "stars": stars,
        "url": f"/receta/{recipe.slug}",
    }


def _render(template: str, context: Dict[str, Any], fallback: str) -> str:
    try:
        return template.format(**context)
    except (KeyError, IndexError, ValueError):
        return fallback


def _email_content(
    type: str, actor: User, recipe: Recipe, detail: Optional[dict]
) -> tuple[str, str]:
    settings = current_settings()
    context = _context(actor, recipe, detail)
    fallback = _message(type, actor, recipe, detail)
    if type == "rating":
        subject_template = settings["email_rating_subject"]
        body_template = settings["email_rating_body"]
    else:
        subject_template = settings["email_favorite_subject"]
        body_template = settings["email_favorite_body"]
    subject = _render(subject_template, context, fallback)[:200]
    body = _render(body_template, context, fallback)
    return subject, body


async def notify_recipe_author(
    db: AsyncSession,
    *,
    actor: User,
    recipe: Recipe,
    type: str,
    detail: Optional[Dict[str, Any]] = None,
) -> Optional[Notification]:
    """Notify the recipe author honouring their preferences.

    Self-actions are ignored. The in-app channel dedupes by
    (recipient, actor, recipe, type); email/push are sent once per new event.
    """
    recipient_id = recipe.author_id
    if recipient_id == actor.id:
        return None

    preferences = await get_preferences(db, recipient_id)
    event_field = _EVENT_FIELD.get(type, "favorites_enabled")
    if not preferences.get(event_field, True):
        return None

    in_app = preferences["in_app_enabled"]
    push = preferences["push_enabled"]
    email = preferences["email_enabled"]

    notification: Optional[Notification] = None
    if in_app:
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

    if in_app or push:
        payload = build_payload(notification, recipe, actor, detail)
        payload["in_app"] = in_app
        await emit_notification(str(recipient_id), payload)

    if email:
        recipient = await db.get(User, recipient_id)
        if recipient and recipient.email:
            subject, body = _email_content(type, actor, recipe, detail)
            await send_email(db, to_email=recipient.email, subject=subject, body=body)

    if push:
        await send_web_push(
            db,
            user_id=recipient_id,
            payload={
                "title": "Recetario IA",
                "body": _message(type, actor, recipe, detail),
                "url": f"/receta/{recipe.slug}",
                "tag": f"{type}-{recipe.id}",
            },
        )

    return notification
