"""
Recetario IA - Backend Configuration
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn
from typing import List


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
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:3001"])

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Recetario IA"

    # Admin
    ADMIN_INITIAL_USER: str = "admin@recetario.local"
    ADMIN_INITIAL_PASSWORD: str = "ChangeMeOnFirstLogin123!"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]


@lru_cache
def get_settings() -> "Settings":
    return Settings()