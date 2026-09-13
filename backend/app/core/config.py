"""
Recetario IA - Backend Configuration
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, field_validator
from typing import List, Union


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Auth: email verification email delivery is v2, so in the MVP new
    # registrations are auto-verified. Flip to true once email is wired.
    REQUIRE_EMAIL_VERIFICATION: bool = Field(default=False)

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://recetario:changeme@postgres:5432/recetario"
    )

    # JWT
    JWT_SECRET: str = Field(default="changeme")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Admin bootstrap
    ADMIN_INITIAL_USER: str = Field(default="admin@recetario.local")
    ADMIN_INITIAL_PASSWORD: str = Field(default="ChangeMeOnFirstLogin123!")

    # CORS
    CORS_ORIGINS: Union[List[str], str] = Field(
        default="http://localhost:3000,http://localhost:3001"
    )

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Recetario IA"

    # Uploads (local disk; served at /uploads)
    UPLOADS_DIR: str = Field(default="/app/uploads")
    MAX_UPLOAD_SIZE_MB: int = Field(default=5)

    # Email (SMTP). When SMTP_HOST is empty, outgoing emails are persisted in
    # the `email_outbox` table instead of being sent (dev transport).
    SMTP_HOST: str = Field(default="")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_FROM: str = Field(default="no-reply@recetario.local")
    SMTP_USE_TLS: bool = Field(default=True)

    # Web Push (VAPID). If the keys are empty they are generated on first use
    # and persisted in app_settings (private key never leaves the server).
    VAPID_SUBJECT: str = Field(default="mailto:admin@recetario.local")
    VAPID_PUBLIC_KEY: str = Field(default="")
    VAPID_PRIVATE_KEY: str = Field(default="")

    # Admin
    ADMIN_INITIAL_USER: str = "admin@recetario.local"
    ADMIN_INITIAL_PASSWORD: str = "ChangeMeOnFirstLogin123!"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> "Settings":
    return Settings()