"""
Database-backed application settings with code defaults.

Values are stored as JSON in ``app_settings`` and can be edited from the admin
panel. Missing keys fall back to ``DEFAULTS``.
"""
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AppSetting

DEFAULTS: Dict[str, Any] = {
    "registration_open": True,
    "require_email_verification": False,
    "max_upload_size_mb": 5,
}


async def get_setting(db: AsyncSession, key: str) -> Any:
    """Return one setting, falling back to the code default."""
    row = await db.get(AppSetting, key)
    if row is None or row.value is None:
        return DEFAULTS.get(key)
    return row.value


async def get_all_settings(db: AsyncSession) -> Dict[str, Any]:
    """Return every setting merged with the code defaults."""
    result = await db.execute(select(AppSetting))
    data: Dict[str, Any] = dict(DEFAULTS)
    for row in result.scalars().all():
        data[row.key] = row.value
    return data


async def set_settings(db: AsyncSession, values: Dict[str, Any]) -> None:
    """Upsert the provided settings (unknown keys are ignored)."""
    for key, value in values.items():
        if key not in DEFAULTS:
            continue
        row = await db.get(AppSetting, key)
        if row is None:
            db.add(AppSetting(key=key, value=value))
        else:
            row.value = value
