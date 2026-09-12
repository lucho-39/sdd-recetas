"""
Pytest fixtures shared across the backend test suite.

Strategy
--------
- Real PostgreSQL test database (``recetario_test``) because the models use
  PostgreSQL-specific types (``UUID``, ``JSONB``, ``ENUM``).
- The schema is created once per session; each test runs inside a transaction
  that is rolled back at the end, so tests are isolated and order-independent.
- HTTP is exercised with ``httpx.ASGITransport`` against the real FastAPI app,
  with the ``get_db`` dependency overridden to the per-test session.
"""
import os

# Ensure tests always run with a symmetric signing algorithm. The container
# environment may force RS256 without providing an RSA key pair.
os.environ["JWT_ALGORITHM"] = os.environ.get("TEST_JWT_ALGORITHM", "HS256")

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models import Category, Ingredient, Recipe, Tag, User, UserRole

settings = get_settings()

_DEFAULT_TEST_DB = "recetario_test"


def _database_url_with_name(url: str, database: str) -> str:
    """Replace the database name of an async SQLAlchemy URL."""
    base, _, _ = url.rpartition("/")
    return f"{base}/{database}"


def _test_database_url() -> str:
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit
    return _database_url_with_name(str(settings.DATABASE_URL), _DEFAULT_TEST_DB)


def _admin_database_url() -> str:
    return _database_url_with_name(str(settings.DATABASE_URL), "postgres")


TEST_DATABASE_URL = _test_database_url()
ADMIN_DATABASE_URL = _admin_database_url()

# Hash once and reuse across fixtures/tests instead of paying bcrypt cost per test.
TEST_PASSWORD = "supersecret123"
TEST_PASSWORD_HASH = get_password_hash(TEST_PASSWORD)


async def _ensure_database_exists() -> None:
    """Create the test database if it does not exist yet."""
    admin_engine = create_async_engine(
        ADMIN_DATABASE_URL,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        async with admin_engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": _DEFAULT_TEST_DB},
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{_DEFAULT_TEST_DB}"'))
    finally:
        await admin_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Session-scoped async engine pointing at the test database."""
    await _ensure_database_exists()
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Per-test database session wrapped in a transaction.

    ``create_savepoint`` makes ORM/endpoint ``commit()`` calls release a
    savepoint instead of the outer transaction, so the final rollback wipes
    every change made during the test.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client bound to the app, sharing the per-test DB session."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Model factories
# ---------------------------------------------------------------------------


async def create_user(
    db: AsyncSession,
    *,
    email: str = "user@example.com",
    display_name: str = "Test User",
    password: str = TEST_PASSWORD,
    role: UserRole = UserRole.USER,
    is_active: bool = True,
    is_verified: bool = True,
    must_change_password: bool = False,
) -> User:
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        display_name=display_name,
        role=role,
        is_active=is_active,
        is_verified=is_verified,
        must_change_password=must_change_password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_category(
    db: AsyncSession,
    *,
    slug: str = "pastas",
    name: str = "Pastas",
    color: str = "#FB923C",
    sort_order: int = 0,
) -> Category:
    category = Category(slug=slug, name=name, color=color, sort_order=sort_order)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def create_recipe(
    db: AsyncSession,
    *,
    author: User,
    category: Category,
    title: str = "Pizza de mozzarella",
    slug: str = "pizza-de-mozzarella",
    is_public: bool = True,
    ingredients: list[dict] | None = None,
) -> Recipe:
    recipe = Recipe(
        author_id=author.id,
        title=title,
        slug=slug,
        description="Rica receta de prueba",
        category_id=category.id,
        instructions="Mezclar todo y cocinar.",
        ingredients=ingredients or [],
        is_public=is_public,
    )
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return recipe


async def create_tag(
    db: AsyncSession,
    *,
    slug: str = "italiana",
    name: str = "Italiana",
    usage_count: int = 1,
) -> Tag:
    tag = Tag(slug=slug, name=name, usage_count=usage_count)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def create_ingredient(
    db: AsyncSession,
    *,
    slug: str = "tomate",
    name: str = "Tomate",
    category: str = "vegetales",
    default_unit: str = "unidad",
    aliases: list[str] | None = None,
    is_active: bool = True,
) -> Ingredient:
    ingredient = Ingredient(
        slug=slug,
        name=name,
        category=category,
        default_unit=default_unit,
        aliases=aliases or [],
        is_active=is_active,
    )
    db.add(ingredient)
    await db.commit()
    await db.refresh(ingredient)
    return ingredient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    return await create_user(db_session)


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    return await create_user(
        db_session,
        email="admin@recetario.local",
        display_name="Admin",
        role=UserRole.ADMIN,
    )


@pytest_asyncio.fixture
def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    token = create_access_token(subject=str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def category(db_session: AsyncSession) -> Category:
    return await create_category(db_session)


@pytest_asyncio.fixture
async def recipe(db_session: AsyncSession, user: User, category: Category) -> Recipe:
    return await create_recipe(
        db_session,
        author=user,
        category=category,
        title="Tarta de manzana",
        slug="tarta-de-manzana",
    )
