"""
Admin schemas: payloads for the administrative API (/api/admin).
"""
from typing import List, Optional
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
