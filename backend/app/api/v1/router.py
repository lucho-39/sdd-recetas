"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, users, recipes, categories, tags, ingredients, favorites, ratings, visits, uploads, notifications, push

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(push.router, prefix="/push", tags=["push"])