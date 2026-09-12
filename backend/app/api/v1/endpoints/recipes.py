"""
Recipe endpoints
"""
import re
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.models import Recipe, Category, Tag, User, Favorite, Rating, Visit
from app.schemas import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeListItem,
    SimilarRecipe,
    UserResponse,
)

router = APIRouter()


def slugify(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    text = re.sub(r'[\s_-]+', '-', text, flags=re.UNICODE)
    text = re.sub(r'^-+|-+$', '', text)
    return text


async def generate_unique_slug(db: AsyncSession, title: str, exclude_id: Optional[UUID] = None) -> tuple[str, List[SimilarRecipe]]:
    """
    Generate a unique slug for a recipe title.
    Returns the slug and a list of similar existing recipes.
    """
    base_slug = slugify(title)
    if not base_slug:
        base_slug = "recipe"

    # Find similar existing recipes (by title similarity)
    similar_query = select(Recipe.id, Recipe.slug, Recipe.title).where(
        Recipe.deleted_at.is_(None),
        Recipe.is_public == True
    )
    if exclude_id:
        similar_query = similar_query.where(Recipe.id != exclude_id)

    result = await db.execute(similar_query)
    existing_recipes = result.all()

    # Find recipes with similar titles (simple containment check)
    similar_recipes = []
    for recipe in existing_recipes:
        # Check if titles share significant words
        title_words = set(title.lower().split())
        existing_words = set(recipe.title.lower().split())
        common_words = title_words & existing_words
        if len(common_words) >= 2 or base_slug in recipe.slug:
            similarity = len(common_words) / max(len(title_words), len(existing_words))
            similar_recipes.append(SimilarRecipe(
                id=recipe.id,
                slug=recipe.slug,
                title=recipe.title,
                similarity=similarity
            ))

    # Sort by similarity descending
    similar_recipes.sort(key=lambda x: x.similarity, reverse=True)
    similar_recipes = similar_recipes[:5]  # Top 5 similar

    # Check if base_slug is taken
    slug_query = select(Recipe.slug).where(Recipe.slug.like(f"{base_slug}%"))
    if exclude_id:
        slug_query = slug_query.where(Recipe.id != exclude_id)
    result = await db.execute(slug_query)
    existing_slugs = {row[0] for row in result.all()}

    if base_slug not in existing_slugs:
        return base_slug, similar_recipes

    # Find next available number
    counter = 2
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1

    return f"{base_slug}-{counter}", similar_recipes


@router.get("", summary="List recipes", response_model=dict)
async def list_recipes(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    tags: Optional[List[str]] = Query(None, description="Filter by tag slugs"),
    ingredients: Optional[List[str]] = Query(None, description="Filter by ingredient slugs"),
    query: Optional[str] = Query(None, description="Search in title and description"),
    sort: str = Query("recent", description="Sort order: recent, visited, saved, top_rated"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional),
):
    """List recipes with filtering and pagination (public read)."""
    filters = [Recipe.is_public == True, Recipe.deleted_at.is_(None)]

    # Apply filters
    if category:
        filters.append(Recipe.category.has(slug=category))

    if tags:
        for tag in tags:
            filters.append(Recipe.tags.any(Tag.slug == tag))

    if ingredients:
        for ingredient in ingredients:
            filters.append(Recipe.ingredients.contains([{"ingredient_id": str(ingredient)}]))

    if query:
        filters.append(
            or_(
                Recipe.title.ilike(f"%{query}%"),
                Recipe.description.ilike(f"%{query}%")
            )
        )

    query_builder = select(Recipe).where(*filters)

    # Apply sorting
    if sort == "recent":
        query_builder = query_builder.order_by(Recipe.created_at.desc())
    elif sort == "visited":
        query_builder = query_builder.order_by(Recipe.visit_count.desc())
    elif sort == "saved":
        query_builder = query_builder.order_by(Recipe.save_count.desc())
    elif sort == "top_rated":
        query_builder = query_builder.order_by(Recipe.avg_rating.desc())

    # Pagination
    offset = (page - 1) * limit
    query_builder = query_builder.offset(offset).limit(limit)

    result = await db.execute(query_builder.options(
        selectinload(Recipe.author),
        selectinload(Recipe.category),
        selectinload(Recipe.tags),
    ))
    recipes = result.scalars().all()

    # Get total count with the same filters applied
    total = await db.scalar(select(func.count()).select_from(Recipe).where(*filters))

    return {
        "recipes": [RecipeListItem.model_validate(r) for r in recipes],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": (page * limit) < total,
    }


@router.get("/{slug}", summary="Get recipe by slug", response_model=RecipeResponse)
async def get_recipe(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional),
):
    """Get recipe by slug (public read)."""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.slug == slug, Recipe.deleted_at.is_(None))
        .options(
            selectinload(Recipe.author),
            selectinload(Recipe.category),
            selectinload(Recipe.tags),
        )
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Increment visit count
    recipe.visit_count += 1
    await db.commit()

    return RecipeResponse.model_validate(recipe)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RecipeResponse)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Create a new recipe with automatic slug generation and similar recipe suggestions."""
    # Verify category exists
    category_result = await db.execute(
        select(Category).where(Category.id == recipe_data.category_id, Category.is_active == True)
    )
    category = category_result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")

    # Generate unique slug and find similar recipes
    slug, similar_recipes = await generate_unique_slug(db, recipe_data.title)

    # Create recipe
    recipe = Recipe(
        author_id=current_user.id,
        title=recipe_data.title,
        slug=slug,
        description=recipe_data.description,
        category_id=recipe_data.category_id,
        image_url=recipe_data.image_url,
        prep_time_minutes=recipe_data.prep_time_minutes,
        cook_time_minutes=recipe_data.cook_time_minutes,
        servings=recipe_data.servings,
        difficulty=recipe_data.difficulty,
        instructions=recipe_data.instructions,
        ingredients=recipe_data.ingredients,
        is_public=recipe_data.is_public,
    )

    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)

    # Load relationships for response
    await db.refresh(recipe, attribute_names=["author", "category", "tags"])

    response = RecipeResponse.model_validate(recipe)
    # Attach similar recipes as a custom attribute (not in schema but available)
    response.similar_recipes = similar_recipes

    return response


@router.patch("/{slug}", response_model=RecipeResponse)
async def update_recipe(
    slug: str,
    recipe_data: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Update a recipe."""
    result = await db.execute(
        select(Recipe).where(Recipe.slug == slug, Recipe.author_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Update fields if provided
    update_data = recipe_data.model_dump(exclude_unset=True)

    # Handle title change -> slug regeneration
    similar_recipes: List[SimilarRecipe] = []
    if "title" in update_data and update_data["title"] != recipe.title:
        new_slug, similar_recipes = await generate_unique_slug(
            db, update_data["title"], exclude_id=recipe.id
        )
        update_data["slug"] = new_slug

    for field, value in update_data.items():
        setattr(recipe, field, value)

    await db.commit()
    await db.refresh(recipe, attribute_names=["author", "category", "tags"])

    response = RecipeResponse.model_validate(recipe)
    response.similar_recipes = similar_recipes
    return response


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Delete a recipe (soft delete) - cascades to favorites, ratings, visits via DB constraints."""
    result = await db.execute(
        select(Recipe).where(Recipe.slug == slug, Recipe.author_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    from datetime import datetime
    recipe.deleted_at = datetime.utcnow()
    await db.commit()

    return None


@router.get("/{slug}/similar", response_model=List[SimilarRecipe], summary="Find similar recipes")
async def find_similar_recipes(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Find recipes similar to the given one by title."""
    result = await db.execute(
        select(Recipe).where(Recipe.slug == slug, Recipe.deleted_at.is_(None))
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Find similar recipes
    similar_query = select(Recipe.id, Recipe.slug, Recipe.title).where(
        Recipe.deleted_at.is_(None),
        Recipe.is_public == True,
        Recipe.id != recipe.id
    )
    similar_result = await db.execute(similar_query)
    existing_recipes = similar_result.all()

    similar_recipes = []
    title_words = set(recipe.title.lower().split())
    for r in existing_recipes:
        existing_words = set(r.title.lower().split())
        common_words = title_words & existing_words
        if len(common_words) >= 2:
            similarity = len(common_words) / max(len(title_words), len(existing_words))
            similar_recipes.append(SimilarRecipe(
                id=r.id,
                slug=r.slug,
                title=r.title,
                similarity=similarity
            ))

    similar_recipes.sort(key=lambda x: x.similarity, reverse=True)
    return similar_recipes[:10]