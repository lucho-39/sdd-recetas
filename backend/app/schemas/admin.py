"""
Admin schemas: payloads for the administrative API (/api/admin).
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Categories
# --------------------------------------------------------------------------- #
class CategoryAdminCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    color: str = Field("#FB923C", max_length=7)
    sort_order: int = 0


class CategoryAdminUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=7)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# --------------------------------------------------------------------------- #
# Tags
# --------------------------------------------------------------------------- #
class TagAdminCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=80)
    name: str = Field(..., min_length=2, max_length=80)


class TagAdminUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=80)


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
class UserAdminUpdate(BaseModel):
    role: Optional[str] = Field(None, pattern="^(user|admin)$")
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserAdminListItem(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

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
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    instructions: Optional[str] = Field(None, min_length=10)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    is_public: Optional[bool] = None


class RecipeVisibilityUpdate(BaseModel):
    is_public: bool


# --------------------------------------------------------------------------- #
# Ingredients
# --------------------------------------------------------------------------- #
class IngredientRejectRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class IngredientNormalizeRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, max_length=30)
    default_unit: Optional[str] = Field(None, max_length=20)
    aliases: Optional[List[str]] = None
    mark_validated: bool = True


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
class ConfigUpdate(BaseModel):
    settings: Dict[str, Any]


# --------------------------------------------------------------------------- #
# Audit log
# --------------------------------------------------------------------------- #
class AuditLogItem(BaseModel):
    id: UUID
    actor_id: Optional[UUID] = None
    actor_name: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    detail: Optional[Dict[str, Any]] = None
    created_at: datetime
