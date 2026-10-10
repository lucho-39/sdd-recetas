"""
Recipe schemas
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.auth import UserResponse

# Units allowed in a recipe's ingredient list (RB-ING-02 / RB-11).
VALID_UNITS = {
    "g",
    "kg",
    "ml",
    "l",
    "unidad",
    "cucharada",
    "cucharadita",
    "taza",
    "pizca",
}


class RecipeIngredient(BaseModel):
    """One ingredient line of a recipe.

    ``ingredient_id`` must point to an existing, active catalog entry; it is
    validated against the database in the endpoint layer.
    """

    ingredient_id: Optional[UUID] = Field(
        default=None,
        description="Catalog id; required so the ingredient can be resolved",
    )
    name: str = Field(..., min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("unit")
    @classmethod
    def unit_must_be_known(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = v.strip().lower()
        if not cleaned:
            return None
        if cleaned not in VALID_UNITS:
            raise ValueError(
                f"Unidad inválida: '{v}'. Valores permitidos: {', '.join(sorted(VALID_UNITS))}"
            )
        return cleaned

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("El nombre del ingrediente no puede estar vacío")
        return cleaned


def ingredients_as_dicts(items: Optional[List[RecipeIngredient]]) -> List[dict]:
    """Serialize validated ingredients into the plain JSONB shape stored in the DB."""
    if not items:
        return []
    # mode="json" is required: the JSONB column cannot encode UUID objects.
    return [item.model_dump(mode="json") for item in items]


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
    # Kept permissive on the read path so legacy JSONB rows still deserialize.
    ingredients: List[dict] = Field(default_factory=list)
    is_public: bool = True


class RecipeCreate(RecipeBase):
    tags: List[str] = Field(default_factory=list)
    ingredients: List[RecipeIngredient] = Field(default_factory=list)

    @model_validator(mode="after")
    def no_duplicate_ingredients(self) -> "RecipeCreate":
        ids = [i.ingredient_id for i in self.ingredients if i.ingredient_id]
        if len(ids) != len(set(ids)):
            raise ValueError("Un ingrediente no puede repetirse en la receta")
        return self


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
    ingredients: Optional[List[RecipeIngredient]] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None

    @model_validator(mode="after")
    def no_duplicate_ingredients(self) -> "RecipeUpdate":
        if self.ingredients is None:
            return self
        ids = [i.ingredient_id for i in self.ingredients if i.ingredient_id]
        if len(ids) != len(set(ids)):
            raise ValueError("Un ingrediente no puede repetirse en la receta")
        return self


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
    my_rating: Optional[int] = None

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