"""
Recipe endpoints
"""
import copy
import re
import unicodedata
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.models import Category, Ingredient, Rating, Recipe, Tag, User
from app.schemas import (
    RecipeCreate,
    RecipeIngredient,
    RecipeListItem,
    RecipeResponse,
    RecipeUpdate,
    SimilarRecipe,
    ingredients_as_dicts,
)

router = APIRouter()


def slugify(text: str) -> str:
    """RB-02: generate a URL-friendly slug, ASCII-safe (no accents)."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def is_admin(user: User | None) -> bool:
    """True when the given user carries the admin role."""
    if user is None:
        return False
    role = user.role.value if hasattr(user.role, "value") else user.role
    return role == "admin"


def recipe_visible_to(recipe: Recipe, user: User | None) -> bool:
    """RB-09: a public recipe is readable by anyone, a private one only by its
    author (and by admins). Soft-deleted recipes are never visible."""
    if recipe.deleted_at is not None:
        return False
    if recipe.is_public:
        return True
    if user is None:
        return False
    return user.id == recipe.author_id or is_admin(user)


async def resolve_ingredient_catalog(
    db: AsyncSession, ingredients: list[dict] | None
) -> list[dict]:
    """Return a copy of the ingredient list with catalog data resolved.

    The JSONB stores only ``ingredient_id``; the UI needs the display name and,
    for RF-12.8, the unit whitelist that narrows the edit form's <select>.
    Unknown / non-UUID ids are left untouched.
    """
    items = copy.deepcopy(ingredients or [])
    ids: list[UUID] = []
    for item in items:
        value = item.get("ingredient_id")
        if not value:
            continue
        try:
            ids.append(UUID(str(value)))
        except (ValueError, TypeError):
            continue

    if ids:
        result = await db.execute(
            select(
                Ingredient.id,
                Ingredient.name,
                Ingredient.default_unit,
                Ingredient.allowed_units,
            ).where(Ingredient.id.in_(ids))
        )
        catalog = {str(row[0]): row for row in result.all()}
        for item in items:
            row = catalog.get(str(item.get("ingredient_id")))
            if row:
                item["name"] = row[1]
                item["default_unit"] = row[2]
                item["allowed_units"] = row[3] or []

    return items


async def validate_ingredients(
    db: AsyncSession, items: list[RecipeIngredient] | None
) -> list[dict]:
    """RB-ING-02 / RF-12.6: every ingredient must reference an existing, active
    catalog entry that has not been rejected by an admin."""
    if not items:
        return []

    ids = {i.ingredient_id for i in items if i.ingredient_id is not None}
    if ids:
        result = await db.execute(
            select(Ingredient.id, Ingredient.default_unit, Ingredient.allowed_units).where(
                Ingredient.id.in_(ids),
                Ingredient.is_active.is_(True),
                Ingredient.rejected.is_(False),
            )
        )
        catalog = {row[0]: (row[1], row[2] or []) for row in result.all()}
    else:
        catalog = {}

    unknown = [i.name for i in items if i.ingredient_id is None or i.ingredient_id not in catalog]
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredientes no disponibles o inexistentes: {', '.join(unknown)}",
        )

    # RF-12.8: an ingredient carrying a whitelist only accepts its default
    # unit plus the listed alternatives. An empty whitelist stays open, so
    # the 320 seeded catalog entries keep behaving as before.
    rejected_units = [
        f"{i.name} ({i.unit})"
        for i in items
        if i.unit
        and catalog[i.ingredient_id][1]
        and i.unit not in {catalog[i.ingredient_id][0], *catalog[i.ingredient_id][1]}
    ]
    if rejected_units:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Unidad no permitida para el ingrediente: "
                f"{', '.join(rejected_units)}"
            ),
        )

    return ingredients_as_dicts(items)


async def sync_recipe_tags(
    db: AsyncSession, recipe: Recipe, tag_slugs: list[str] | None
) -> None:
    """Replace a recipe's tags by slug, creating missing ones.

    ``usage_count`` is kept in sync: incremented for newly associated tags and
    decremented for the ones removed.
    """
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in tag_slugs or []:
        slug = slugify(str(raw))
        if slug and slug not in seen:
            seen.add(slug)
            normalized.append(slug)

    # Read current tags before any query so the collection is loaded without
    # triggering a lazy load after an autoflush (which would fail in async).
    current = {tag.slug: tag for tag in recipe.tags}

    existing: dict[str, Tag] = {}
    if normalized:
        # no_autoflush keeps a newly added (pending) recipe pending, so the
        # relationship assignment below does not need to load a collection.
        with db.no_autoflush:
            result = await db.execute(select(Tag).where(Tag.slug.in_(normalized)))
            existing = {tag.slug: tag for tag in result.scalars().all()}

    for slug, tag in current.items():
        if slug not in seen:
            tag.usage_count = max(0, tag.usage_count - 1)

    new_tags: list[Tag] = []
    for slug in normalized:
        tag = existing.get(slug)
        if tag is None:
            tag = Tag(slug=slug, name=slug.replace('-', ' ').title(), usage_count=1)
            db.add(tag)
        elif slug not in current:
            tag.usage_count += 1
        new_tags.append(tag)

    recipe.tags = new_tags


async def generate_unique_slug(
    db: AsyncSession, title: str, exclude_id: UUID | None = None
) -> tuple[str, list[SimilarRecipe]]:
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
    category: str | None = Query(None, description="Filter by category slug"),
    tags: list[str] | None = Query(None, description="Filter by tag slugs"),
    ingredients: list[str] | None = Query(None, description="Filter by ingredient ids"),
    query: str | None = Query(None, description="Search in title and description"),
    difficulty: str | None = Query(None, description="Filter by difficulty: easy|medium|hard"),
    max_time: int | None = Query(None, ge=1, description="Max total time in minutes"),
    sort: str = Query("recent", description="Sort order: recent, visited, saved, top_rated"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional),
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
        # RB-03 / RB-16: multiple selected ingredients are ORed together (a recipe
        # matching any of them is a hit), while category/tags/text stay ANDed.
        filters.append(
            or_(
                *[
                    Recipe.ingredients.contains([{"ingredient_id": str(ingredient)}])
                    for ingredient in ingredients
                ]
            )
        )

    if difficulty:
        filters.append(Recipe.difficulty == difficulty)

    if max_time:
        total_time = func.coalesce(Recipe.prep_time_minutes, 0) + func.coalesce(
            Recipe.cook_time_minutes, 0
        )
        filters.append(total_time <= max_time)

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
    current_user=Depends(get_current_user_optional),
):
    """Get recipe by slug (public read, private only for author/admin)."""
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

    # RB-09: a private recipe must not be reachable by slug guessing.
    if not recipe or not recipe_visible_to(recipe, current_user):
        raise HTTPException(status_code=404, detail="Recipe not found")

    # RB-04: visits are recorded by POST /visits/{recipe_id}, which deduplicates
    # per visitor per day. This read endpoint must not inflate the counter.

    response = RecipeResponse.model_validate(recipe)
    response.ingredients = await resolve_ingredient_catalog(db, response.ingredients)

    if current_user is not None:
        response.my_rating = await db.scalar(
            select(Rating.score).where(
                Rating.recipe_id == recipe.id,
                Rating.user_id == current_user.id,
            )
        )

    return response


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RecipeResponse)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
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
        ingredients=await validate_ingredients(db, recipe_data.ingredients),
        is_public=recipe_data.is_public,
    )

    db.add(recipe)
    await sync_recipe_tags(db, recipe, recipe_data.tags)
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
    current_user=Depends(get_current_active_user),
):
    """Update a recipe."""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.slug == slug, Recipe.author_id == current_user.id)
        .options(selectinload(Recipe.tags))
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Update fields if provided
    update_data = recipe_data.model_dump(exclude_unset=True)
    tag_slugs = update_data.pop("tags", None)
    if "ingredients" in update_data:
        update_data["ingredients"] = await validate_ingredients(
            db, recipe_data.ingredients
        )

    if "category_id" in update_data:
        category_result = await db.execute(
            select(Category).where(
                Category.id == update_data["category_id"],
                Category.is_active == True,
            )
        )
        if category_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=400, detail="Invalid category")

    # Handle title change -> slug regeneration
    similar_recipes: list[SimilarRecipe] = []
    if "title" in update_data and update_data["title"] != recipe.title:
        new_slug, similar_recipes = await generate_unique_slug(
            db, update_data["title"], exclude_id=recipe.id
        )
        update_data["slug"] = new_slug

    for field, value in update_data.items():
        setattr(recipe, field, value)

    if tag_slugs is not None:
        await sync_recipe_tags(db, recipe, tag_slugs)

    await db.commit()
    await db.refresh(recipe, attribute_names=["author", "category", "tags"])

    response = RecipeResponse.model_validate(recipe)
    response.similar_recipes = similar_recipes
    return response


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
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


@router.post("/{slug}/restore", response_model=RecipeResponse, summary="Restore a deleted recipe")
async def restore_recipe(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Restore a soft-deleted recipe (author only)."""
    result = await db.execute(
        select(Recipe).where(Recipe.slug == slug, Recipe.author_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.deleted_at is None:
        raise HTTPException(status_code=400, detail="Recipe is not deleted")

    recipe.deleted_at = None
    await db.commit()
    await db.refresh(recipe, attribute_names=["author", "category", "tags"])

    return RecipeResponse.model_validate(recipe)


@router.get("/{slug}/similar", response_model=list[SimilarRecipe], summary="Find similar recipes")
async def find_similar_recipes(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Find recipes similar to the given one by title."""
    result = await db.execute(
        select(Recipe).where(Recipe.slug == slug, Recipe.deleted_at.is_(None))
    )
    recipe = result.scalar_one_or_none()

    if not recipe or not recipe_visible_to(recipe, current_user):
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
