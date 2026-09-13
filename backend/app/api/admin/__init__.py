"""
Administrative API (/api/admin). Aggregates the admin routers.
"""
from fastapi import APIRouter

from app.api.admin import (
    audit,
    categories,
    config,
    ingredients,
    metrics,
    recipes,
    tags,
    users,
)

admin_router = APIRouter()

admin_router.include_router(categories.router, prefix="/categories", tags=["admin:categories"])
admin_router.include_router(tags.router, prefix="/tags", tags=["admin:tags"])
admin_router.include_router(users.router, prefix="/users", tags=["admin:users"])
admin_router.include_router(recipes.router, prefix="/recipes", tags=["admin:recipes"])
admin_router.include_router(ingredients.router, prefix="/ingredients", tags=["admin:ingredients"])
admin_router.include_router(metrics.router, prefix="/metrics", tags=["admin:metrics"])
admin_router.include_router(config.router, prefix="/config", tags=["admin:config"])
admin_router.include_router(audit.router, prefix="/audit-log", tags=["admin:audit"])
