"""
Admin schemas: payloads for the administrative API (/api/admin).
"""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Categories
# --------------------------------------------------------------------------- #
class CategoryAdminCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=50)
    description: str | None = None
    icon: str | None = Field(None, max_length=10)
    color: str = Field("#FB923C", max_length=7)
    sort_order: int = 0


class CategoryAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = None
    icon: str | None = Field(None, max_length=10)
    color: str | None = Field(None, max_length=7)
    sort_order: int | None = None
    is_active: bool | None = None


# --------------------------------------------------------------------------- #
# Tags
# --------------------------------------------------------------------------- #
class TagAdminCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=80)
    name: str = Field(..., min_length=2, max_length=80)


class TagAdminUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=80)


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
class UserAdminUpdate(BaseModel):
    role: str | None = Field(None, pattern="^(user|admin)$")
    is_active: bool | None = None
    is_verified: bool | None = None


class UserAdminListItem(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
class DashboardStats(BaseModel):
    users_total: int
    users_active: int
    recipes_total: int
    recipes_public: int
    recipes_deleted: int
    ingredients_total: int
    ingredients_pending: int
    categories_total: int
    tags_total: int
    ratings_total: int
    visits_total: int


# --------------------------------------------------------------------------- #
# Recipes
# --------------------------------------------------------------------------- #
class RecipeAdminUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = None
    category_id: UUID | None = None
    instructions: str | None = Field(None, min_length=10)
    difficulty: str | None = Field(None, pattern="^(easy|medium|hard)$")
    prep_time_minutes: int | None = Field(None, ge=0)
    cook_time_minutes: int | None = Field(None, ge=0)
    servings: int | None = Field(None, ge=1)
    is_public: bool | None = None


class RecipeVisibilityUpdate(BaseModel):
    is_public: bool


# --------------------------------------------------------------------------- #
# Ingredients
# --------------------------------------------------------------------------- #
class IngredientRejectRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class IngredientRecoverRequest(BaseModel):
    """Reason a rejected ingredient is being moved back to pending."""

    reason: str = Field(..., min_length=3, max_length=500)


class IngredientNormalizeRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=80)
    category: str | None = Field(None, max_length=30)
    default_unit: str | None = Field(None, max_length=20)
    allowed_units: list[str] | None = None
    aliases: list[str] | None = None
    mark_validated: bool = True


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
class ConfigUpdate(BaseModel):
    settings: dict[str, Any]


# --------------------------------------------------------------------------- #
# Audit log
# --------------------------------------------------------------------------- #
class AuditLogItem(BaseModel):
    id: UUID
    actor_id: UUID | None = None
    actor_name: str | None = None
    action: str
    target_type: str | None = None
    target_id: str | None = None
    detail: dict[str, Any] | None = None
    created_at: datetime


class GdprEraseRequest(BaseModel):
    delete_recipes: bool = False


class IngredientMergeRequest(BaseModel):
    target_id: UUID
