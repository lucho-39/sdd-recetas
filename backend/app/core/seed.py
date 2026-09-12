"""
Idempotent startup seed: initial categories and a few demo recipes.

This makes the public home page meaningful on a fresh database. It never
duplicates rows: every entity is looked up by its unique slug first.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Category, Recipe, User

CATEGORIES: list[tuple[str, str, str, str]] = [
    ("postre", "Postre", "🍰", "#FB923C"),
    ("entrada", "Entrada", "🥗", "#4ADE80"),
    ("snack", "Snack", "🍿", "#FACC15"),
    ("plato-principal", "Plato principal", "🍽️", "#60A5FA"),
    ("acompañamiento", "Acompañamiento", "🥔", "#C084FC"),
    ("bebida", "Bebida", "🥤", "#22D3EE"),
    ("desayuno", "Desayuno", "☕", "#FB7185"),
    ("sopa-crema", "Sopa / Crema", "🍲", "#A3E635"),
    ("ensalada", "Ensalada", "🥗", "#34D399"),
    ("horneados", "Horneados", "🍞", "#F87171"),
]

DEMO_RECIPES: list[dict] = [
    {
        "slug": "tarta-de-manzana",
        "title": "Tarta de manzana",
        "description": "Una tarta clásica, dulce y especiada.",
        "category": "postre",
        "prep_time_minutes": 20,
        "cook_time_minutes": 45,
        "servings": 8,
        "difficulty": "easy",
        "instructions": "Pelar las manzanas, mezclar con azúcar y canela, cubrir con la masa y hornear 45 minutos.",
    },
    {
        "slug": "ensalada-cesar",
        "title": "Ensalada César",
        "description": "Fresca, crujiente y con aderezo cremoso.",
        "category": "ensalada",
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 2,
        "difficulty": "easy",
        "instructions": "Lavar la lechuga, preparar el aderezo, dorar el pollo y mezclar todo con crutones.",
    },
    {
        "slug": "sopa-de-calabaza",
        "title": "Sopa de calabaza",
        "description": "Cremosa y reconfortante, ideal para el invierno.",
        "category": "sopa-crema",
        "prep_time_minutes": 10,
        "cook_time_minutes": 30,
        "servings": 4,
        "difficulty": "medium",
        "instructions": "Cocinar la calabaza con cebolla, licuar, condimentar y servir con un hilo de crema.",
    },
]


async def seed_initial_data(db: AsyncSession) -> None:
    """Seed categories and demo recipes if they do not exist yet."""
    for order, (slug, name, icon, color) in enumerate(CATEGORIES):
        exists = await db.scalar(select(Category.id).where(Category.slug == slug))
        if not exists:
            db.add(Category(slug=slug, name=name, icon=icon, color=color, sort_order=order))
    await db.commit()

    settings = get_settings()
    admin = await db.scalar(select(User).where(User.email == settings.ADMIN_INITIAL_USER))
    if not admin:
        return

    for demo in DEMO_RECIPES:
        exists = await db.scalar(select(Recipe.id).where(Recipe.slug == demo["slug"]))
        if exists:
            continue
        category = await db.scalar(select(Category).where(Category.slug == demo["category"]))
        if not category:
            continue
        db.add(
            Recipe(
                author_id=admin.id,
                title=demo["title"],
                slug=demo["slug"],
                description=demo["description"],
                category_id=category.id,
                instructions=demo["instructions"],
                ingredients=[],
                is_public=True,
                prep_time_minutes=demo["prep_time_minutes"],
                cook_time_minutes=demo["cook_time_minutes"],
                servings=demo["servings"],
                difficulty=demo["difficulty"],
            )
        )
    await db.commit()
