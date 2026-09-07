"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "recetario-backend"}


@router.get("/healthz", summary="Kubernetes health check")
async def healthz_check():
    """Kubernetes-style health check."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness check")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check - verifies database connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "database": "disconnected", "error": str(e)}