"""
Recipe schemas
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from app.schemas.auth import UserResponse
from app.models import Category, Tag


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category_id: UUID
    image_url: Optional[str] = Field(None, max_length=500)
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    instructions: str = Field(..., min_length=10)
    ingredients: List[dict] = Field(default_factory=list)
    is_public: bool = True


class RecipeCreate(RecipeBase):
    tags: List[str] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    image_url: Optional[str] = Field(None, max_length=500)
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    instructions: Optional[str] = Field(None, min_length=10)
    ingredients: Optional[List[dict]] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class RecipeResponse(RecipeBase):
    id: UUID
    slug: str
    author: UserResponse
    category: "CategoryResponse"
    tags: List["TagResponse"] = []
    visit_count: int
    save_count: int
    avg_rating: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    similar_recipes: List["SimilarRecipe"] = []

    class Config:
        from_attributes = True


class RecipeListItem(BaseModel):
    id: UUID
    slug: str
    title: str
    description: Optional[str] = None
    category: "CategoryResponse"
    tags: List["TagResponse"] = []
    image_url: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    visit_count: int
    save_count: int
    avg_rating: float
    rating_count: int
    author: UserResponse
    is_public: bool = True
    deleted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SimilarRecipe(BaseModel):
    id: UUID
    slug: str
    title: str
    similarity: float


class CategoryResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    icon: Optional[str] = None
    color: str

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: UUID
    slug: str
    name: str

    class Config:
        from_attributes = True


RecipeResponse.model_rebuild()
RecipeListItem.model_rebuild()