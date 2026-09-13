"""
Administrative API (/api/admin). Aggregates the admin routers.
"""
from fastapi import APIRouter

from app.api.admin import categories, metrics, tags, users

admin_router = APIRouter()

admin_router.include_router(categories.router, prefix="/categories", tags=["admin:categories"])
admin_router.include_router(tags.router, prefix="/tags", tags=["admin:tags"])
admin_router.include_router(users.router, prefix="/users", tags=["admin:users"])
admin_router.include_router(metrics.router, prefix="/metrics", tags=["admin:metrics"])
