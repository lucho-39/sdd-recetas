"""
Recetario IA - Main Application
"""
from contextlib import asynccontextmanager
from pathlib import Path

import socketio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.app_settings import current_settings, load_settings_cache
from app.core.config import get_settings
from app.core.database import init_db, async_session_maker
from app.core.seed import seed_initial_data
from app.api.v1.router import api_router
from app.api.admin import admin_router
from app.api.v1.endpoints.auth import create_admin_user
from app.models import ErrorLog
from app.realtime.server import sio

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create schema and idempotently seed initial data
    await init_db()
    async with async_session_maker() as session:
        await create_admin_user(session)
        await seed_initial_data(session)
        await load_settings_cache(session)
    yield
    # Shutdown (if needed)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Recetario IA - Backend API",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limit buckets (per process): ip -> monotonic timestamps
_rate_buckets: dict[str, list[float]] = {}
_RATE_WINDOW_SECONDS = 60.0


async def _record_error(path: str, method: str, status_code: int, message: str | None) -> None:
    try:
        async with async_session_maker() as session:
            session.add(
                ErrorLog(path=path, method=method, status_code=status_code, message=message)
            )
            await session.commit()
    except Exception:  # pragma: no cover - never fail a request because of logging
        pass


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Rate limiting, maintenance mode and 5xx error logging."""
    config = current_settings()
    path = request.url.path

    limit = int(config.get("rate_limit_per_minute") or 0)
    if limit > 0 and path.startswith("/api/") and not path.startswith("/api/admin"):
        import time

        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = _rate_buckets.setdefault(client, [])
        bucket[:] = [stamp for stamp in bucket if now - stamp < _RATE_WINDOW_SECONDS]
        if len(bucket) >= limit:
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        bucket.append(now)

    if config.get("maintenance_mode"):
        allowed = (
            path.startswith("/api/admin")
            or path.startswith("/api/v1/auth")
            or path.startswith("/health")
            or path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi")
            or path.startswith("/uploads")
        )
        if not allowed:
            return JSONResponse(
                status_code=503, content={"detail": "Service under maintenance"}
            )

    try:
        response = await call_next(request)
    except Exception as exc:
        await _record_error(path, request.method, 500, str(exc))
        raise

    if response.status_code >= 500:
        await _record_error(path, request.method, response.status_code, None)
    return response

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Include admin API router
app.include_router(admin_router, prefix="/api/admin")

# Serve uploaded images (local disk)
_uploads_dir = Path(settings.UPLOADS_DIR)
_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_uploads_dir)), name="uploads")


@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "recetario-backend"},
    )


@app.get("/healthz", tags=["health"])
async def healthz_check():
    """Kubernetes-style health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "ok"},
    )


# Socket.IO shares the same port: run ``app.main:socket_app`` with uvicorn.
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)