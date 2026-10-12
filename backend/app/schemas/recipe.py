"""
Recipe schemas
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.units import VALID_UNITS
from app.schemas.auth import UserResponse

# Units allowed in a recipe's ingredient list (RB-ING-02 / RB-11) live in
# app.core.units so the admin and public ingredient routes share one set.


class RecipeIngredient(BaseModel):
    """One ingredient line of a recipe.

    ``ingredient_id`` must point to an existing, active catalog entry; it is
    validated against the database in the endpoint layer.
    """

    ingredient_id: UUID | None = Field(
        default=None,
        description="Catalog id; required so the ingredient can be resolved",
    )
    name: str = Field(..., min_length=1, max_length=100)
    amount: float | None = Field(None, gt=0)
    unit: str | None = Field(None, max_length=20)
    notes: str | None = Field(None, max_length=500)

    @field_validator("unit")
    @classmethod
    def unit_must_be_known(cls, v: str | None) -> str | None:
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


def ingredients_as_dicts(items: list[RecipeIngredient] | None) -> list[dict]:
    """Serialize validated ingredients into the plain JSONB shape stored in the DB."""
    if not items:
        return []
    # mode="json" is required: the JSONB column cannot encode UUID objects.
    return [item.model_dump(mode="json") for item in items]


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = None
    category_id: UUID
    image_url: str | None = Field(None, max_length=500)
    prep_time_minutes: int | None = Field(None, ge=0)
    cook_time_minutes: int | None = Field(None, ge=0)
    servings: int | None = Field(None, ge=1)
    difficulty: str | None = Field(None, pattern="^(easy|medium|hard)$")
    instructions: str = Field(..., min_length=10)
    # Kept permissive on the read path so legacy JSONB rows still deserialize.
    ingredients: list[dict] = Field(default_factory=list)
    is_public: bool = True


class RecipeCreate(RecipeBase):
    tags: list[str] = Field(default_factory=list)
    ingredients: list[RecipeIngredient] = Field(default_factory=list)

    @model_validator(mode="after")
    def no_duplicate_ingredients(self) -> "RecipeCreate":
        ids = [i.ingredient_id for i in self.ingredients if i.ingredient_id]
        if len(ids) != len(set(ids)):
            raise ValueError("Un ingrediente no puede repetirse en la receta")
        return self


class RecipeUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = None
    category_id: UUID | None = None
    image_url: str | None = Field(None, max_length=500)
    prep_time_minutes: int | None = Field(None, ge=0)
    cook_time_minutes: int | None = Field(None, ge=0)
    servings: int | None = Field(None, ge=1)
    difficulty: str | None = Field(None, pattern="^(easy|medium|hard)$")
    instructions: str | None = Field(None, min_length=10)
    ingredients: list[RecipeIngredient] | None = None
    is_public: bool | None = None
    tags: list[str] | None = None

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
    tags: list["TagResponse"] = []
    visit_count: int
    save_count: int
    avg_rating: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    similar_recipes: list["SimilarRecipe"] = []
    my_rating: int | None = None

    class Config:
        from_attributes = True


class RecipeListItem(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str | None = None
    category: "CategoryResponse"
    tags: list["TagResponse"] = []
    image_url: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int | None = None
    difficulty: str | None = None
    visit_count: int
    save_count: int
    avg_rating: float
    rating_count: int
    author: UserResponse
    is_public: bool = True
    deleted_at: datetime | None = None
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
    icon: str | None = None
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
