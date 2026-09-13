"""
Recetario IA - Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db, async_session_maker
from app.core.seed import seed_initial_data
from app.api.v1.router import api_router
from app.api.admin import admin_router
from app.api.v1.endpoints.auth import create_admin_user

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create schema and idempotently seed initial data
    await init_db()
    async with async_session_maker() as session:
        await create_admin_user(session)
        await seed_initial_data(session)
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

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Include admin API router
app.include_router(admin_router, prefix="/api/admin")


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