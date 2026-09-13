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
    "maintenance_mode": False,
    "rate_limit_per_minute": 0,
    # Email templates. Placeholders: {actor}, {recipe}, {score}, {stars}, {url}
    "email_favorite_subject": "'{actor}' guardó tu receta '{recipe}'",
    "email_favorite_body": (
        "Hola,\n\n'{actor}' guardó tu receta '{recipe}'.\n\n"
        "Podés verla en {url}\n\n— Recetario IA"
    ),
    "email_rating_subject": (
        "Tu receta '{recipe}' recibió una calificación de {stars} de parte de '{actor}'"
    ),
    "email_rating_body": (
        "Hola,\n\nTu receta '{recipe}' recibió una calificación de {stars} "
        "de parte de '{actor}'.\n\nPodés verla en {url}\n\n— Recetario IA"
    ),
}


async def get_setting(db: AsyncSession, key: str) -> Any:
    """Return one setting, falling back to the code default."""
    row = await db.get(AppSetting, key)
    if row is None or row.value is None:
        return DEFAULTS.get(key)
    return row.value


async def get_all_settings(db: AsyncSession) -> Dict[str, Any]:
    """Return every known setting merged with the code defaults.

    Rows with keys not declared in ``DEFAULTS`` (e.g. internally generated
    secrets) are intentionally excluded from API responses.
    """
    result = await db.execute(select(AppSetting))
    data: Dict[str, Any] = dict(DEFAULTS)
    for row in result.scalars().all():
        if row.key in DEFAULTS:
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


# In-process settings cache, primed at startup and refreshed on config updates.
# Middleware reads it synchronously so it never hits the database per request.
_cache: Dict[str, Any] = {"value": None}


def current_settings() -> Dict[str, Any]:
    """Cached settings (falls back to code defaults when not primed)."""
    cached = _cache["value"]
    return dict(cached) if cached is not None else dict(DEFAULTS)


def invalidate_settings_cache() -> None:
    _cache["value"] = None


async def load_settings_cache(db: AsyncSession) -> Dict[str, Any]:
    value = await get_all_settings(db)
    _cache["value"] = value
    return value
