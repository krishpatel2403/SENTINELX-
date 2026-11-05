"""Application configuration using Pydantic Settings.

Values are loaded from environment variables and an optional `.env` file.
Never commit real secrets to source control — use `.env.example` as a template.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SentinelX"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Security / JWT
    SECRET_KEY: str = "change-me-to-a-strong-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./sentinelx.db"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "sentinelx"
    POSTGRES_PASSWORD: str = "change-me"
    POSTGRES_DB: str = "sentinelx"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Uploads
    MAX_UPLOAD_SIZE_MB: int = 50

    # Rate limiting (requests per window)
    RATE_LIMIT_AUTH: int = 10
    RATE_LIMIT_INGESTION: int = 30

    # Threat intelligence (optional public feeds — disabled by default)
    THREAT_FEED_ENABLED: bool = False
    THREAT_FEED_URL: str = ""

    # Seed default admin (change in production)
    SEED_ADMIN_USERNAME: str = "admin"
    SEED_ADMIN_PASSWORD: str = "ChangeMeAdmin123!"
    SEED_ADMIN_EMAIL: str = "admin@sentinelx.com"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
