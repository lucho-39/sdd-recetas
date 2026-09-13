"""
Recetario IA - Database Models
"""
import enum
from datetime import datetime
from typing import Any, List, Optional
from uuid import uuid4

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    recipes: Mapped[List["Recipe"]] = relationship(back_populates="author", lazy="dynamic")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user", lazy="dynamic")
    ratings: Mapped[List["Rating"]] = relationship(back_populates="user", lazy="dynamic")
    visits: Mapped[List["Visit"]] = relationship(back_populates="user", lazy="dynamic")
    tags_created: Mapped[List["Tag"]] = relationship(back_populates="created_by_user", lazy="dynamic")
    ingredients_created: Mapped[List["Ingredient"]] = relationship(
        back_populates="created_by_user",
        foreign_keys="Ingredient.created_by",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("ix_users_is_active", "is_active"),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#FB923C")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    recipes: Mapped[List["Recipe"]] = relationship(back_populates="category", lazy="dynamic")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    created_by_user: Mapped[Optional["User"]] = relationship(back_populates="tags_created")
    recipes: Mapped[List["Recipe"]] = relationship(secondary="recipe_tags", back_populates="tags")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    author_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    prep_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cook_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    servings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    ingredients: Mapped[List[dict]] = mapped_column(JSONB, nullable=False, default=list)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    visit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    save_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_rating: Mapped[float] = mapped_column(default=0.0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    author: Mapped["User"] = relationship(back_populates="recipes")
    category: Mapped["Category"] = relationship(back_populates="recipes")
    tags: Mapped[List["Tag"]] = relationship(secondary="recipe_tags", back_populates="recipes")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="recipe", lazy="dynamic")
    ratings: Mapped[List["Rating"]] = relationship(back_populates="recipe", lazy="dynamic")
    visits: Mapped[List["Visit"]] = relationship(back_populates="recipe", lazy="dynamic")

    __table_args__ = (
        Index("ix_recipes_is_public_created", "is_public", "created_at"),
        Index("ix_recipes_deleted_at", "deleted_at"),
    )


class RecipeTag(Base):
    __tablename__ = "recipe_tags"

    recipe_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    collection_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship(back_populates="favorites")


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recipe_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    visitor_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    visited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="visits")
    user: Mapped[Optional["User"]] = relationship(back_populates="visits")

    __table_args__ = (
        UniqueConstraint("recipe_id", "visitor_fingerprint", "visited_at", name="uq_visit_unique_daily"),
        Index("ix_visits_recipe_date", "recipe_id", "visited_at"),
    )


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recipe_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="ratings")
    user: Mapped["User"] = relationship(back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("recipe_id", "user_id", name="uq_rating_user_recipe"),
        CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score_range"),
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    default_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    aliases: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validated_by_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_by: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejected_by: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    created_by_user: Mapped[Optional["User"]] = relationship(
        back_populates="ingredients_created", foreign_keys=[created_by]
    )
    validated_by_user: Mapped[Optional["User"]] = relationship(foreign_keys=[validated_by])
    rejected_by_user: Mapped[Optional["User"]] = relationship(foreign_keys=[rejected_by])

    __table_args__ = (
        Index("ix_ingredients_category", "category"),
        Index("ix_ingredients_is_active", "is_active"),
    )


class AppSetting(Base):
    """Key/value application settings editable from the admin panel."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[Any] = mapped_column(JSONB, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class AuditLog(Base):
    """Audit trail of administrative actions."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_id: Mapped[Optional[uuid4]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    detail: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    actor: Mapped[Optional["User"]] = relationship(foreign_keys=[actor_id])


# Import for type hints
from typing import Optional, List
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID