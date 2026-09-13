"""
Web Push endpoints (VAPID subscriptions).
"""
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import PushSubscription
from app.services.webpush import get_public_key, send_web_push

router = APIRouter()


class PushKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscribeRequest(BaseModel):
    endpoint: str
    keys: PushKeys


class PushUnsubscribeRequest(BaseModel):
    endpoint: str


@router.get("/public-key", summary="VAPID public key")
async def vapid_public_key(db: AsyncSession = Depends(get_db)):
    return {"public_key": await get_public_key(db)}


@router.post("/subscribe", status_code=status.HTTP_201_CREATED, summary="Subscribe to push")
async def subscribe(
    data: PushSubscribeRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    existing = (
        await db.execute(
            select(PushSubscription).where(PushSubscription.endpoint == data.endpoint)
        )
    ).scalar_one_or_none()

    if existing is not None:
        existing.user_id = current_user.id
        existing.p256dh = data.keys.p256dh
        existing.auth = data.keys.auth
    else:
        db.add(
            PushSubscription(
                user_id=current_user.id,
                endpoint=data.endpoint,
                p256dh=data.keys.p256dh,
                auth=data.keys.auth,
            )
        )
    await db.commit()
    return {"subscribed": True}


@router.delete("/subscribe", summary="Unsubscribe from push")
async def unsubscribe(
    data: PushUnsubscribeRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    subscription = (
        await db.execute(
            select(PushSubscription).where(
                PushSubscription.endpoint == data.endpoint,
                PushSubscription.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if subscription is not None:
        await db.delete(subscription)
        await db.commit()
    return {"unsubscribed": True}


@router.post("/test", summary="Send a test push")
async def test_push(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    sent = await send_web_push(
        db,
        user_id=current_user.id,
        payload={
            "title": "Recetario IA",
            "body": "Notificación de prueba",
            "url": "/",
        },
    )
    return {"sent": sent}
