"""
Authentication schemas
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class UserBase(BaseModel):
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    # Responses never re-validate already-persisted values; bootstrap accounts
    # may legitimately use reserved TLDs such as ``.local``.
    email: str
    id: UUID
    avatar_url: str | None = None
    role: str
    is_active: bool
    is_verified: bool
    must_change_password: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PublicProfileResponse(BaseModel):
    """Public view of a user's profile (RB-17 / RF-11).

    Only non-sensitive data: no email, no roles, no private metrics.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    avatar_url: str | None = None
    created_at: datetime
    recipe_count: int = 0


class NotificationPreferenceUpdate(BaseModel):
    """Partial update of the current user's notification settings."""

    in_app_enabled: bool | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    favorites_enabled: bool | None = None
    ratings_enabled: bool | None = None


class AccountDeactivateRequest(BaseModel):
    """Baja lógica de la propia cuenta.

    `password` es obligatorio: es una operación destructiva y no basta con
    presentar una sesión válida (re-autenticación).
    """

    password: str
    delete_recipes: bool = False


class AccountDeleteRequest(BaseModel):
    """Eliminación definitiva (GDPR) de la propia cuenta.

    Igual que la baja, exige re-autenticación con la contraseña actual.
    """

    password: str
    confirm: bool = False
