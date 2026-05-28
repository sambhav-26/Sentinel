"""
Configuration settings for SentinelOS backend.
Loads from environment variables with sensible defaults.
"""

import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application configuration."""

    # API
    API_TITLE: str = "SentinelOS"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Autonomous AI Security Analysis Platform"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/sentinelos"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "./uploads")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Redis (for caching and Celery)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    # Scanning
    SCAN_TIMEOUT_SECONDS: int = 3600  # 1 hour
    MAX_CONCURRENT_SCANS: int = 5
    DEFAULT_SCAN_TYPE: str = "full"  # "full" or "quick"

    # AI/LLM (optional)
    USE_LLM_FOR_PATCHES: bool = os.getenv("USE_LLM_FOR_PATCHES", "false").lower() == "true"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # "openai", "gemini"
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", None)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo")

    @property
    def database_url_async(self) -> str:
        """Convert sync database URL to async (postgresql → postgresql+asyncpg)."""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses functools.lru_cache to ensure single instance across app.
    """
    return Settings()
