"""
Admin: application settings (/api/admin/config).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.app_settings import get_all_settings, load_settings_cache, set_settings
from app.core.audit import record_audit
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.admin import ConfigUpdate

router = APIRouter()


@router.get("", summary="Get application settings (admin)")
async def get_config(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return {"settings": await get_all_settings(db)}


@router.put("", summary="Update application settings (admin)")
async def update_config(
    payload: ConfigUpdate,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await set_settings(db, payload.settings)
    await record_audit(
        db, admin.id, "config.update", target_type="config", detail=payload.settings
    )
    await db.commit()
    return {"settings": await load_settings_cache(db)}
