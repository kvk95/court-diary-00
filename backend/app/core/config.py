# app\core\config.py

from __future__ import annotations

from typing import Optional, Sequence
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.logging_framework.config import LoggingSettings


class Settings(BaseSettings):
    """
    Central application configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Project Metadata
    # -------------------------------------------------------------------------
    PROJECT_NAME: str = "Court Diary FastAPI"
    VERSION: str = "1.0"
    DESCRIPTION: str = "Production-ready backend for Court Diary POS"

    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    OPENAPI_URL: Optional[str] = "/openapi.json"

    # -------------------------------------------------------------------------
    # Server Settings
    # -------------------------------------------------------------------------
    APP_PORT: int = 5000
    APP_ENV: str = "development"  # development | staging | production

    # -------------------------------------------------------------------------
    # Security / Secrets
    # -------------------------------------------------------------------------
    SECRET_KEY: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # -------------------------------------------------------------------------
    # Database Settings
    # -------------------------------------------------------------------------
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_DRIVER: Optional[str] = None  # e.g., postgresql+asyncpg

    UI_URL:Optional[str] = None 

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    CORS_ALLOWED_ORIGINS: Sequence[str] = (
        "http://localhost:3000",
        "http://localhost:3001",
    )
    CORS_ENABLED: bool = True

    SMTP_SERVER: Optional[str] = None
    SMTP_SERVER_PORT: Optional[str] = None
    SMTP_SERVER_USERNAME: Optional[str] = None
    SMTP_SERVER_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: Optional[bool] = False

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        """Allow comma-separated strings in .env."""
        if isinstance(v, str):
            return tuple(o.strip() for o in v.split(",") if o.strip())
        return v

    # -------------------------------------------------------------------------
    # Derived Properties
    # -------------------------------------------------------------------------
    @property
    def effective_database_url(self) -> str:
        """Build a SQLAlchemy-compatible DB URL."""
        required = [
            self.DB_DRIVER,
            self.DB_USER,
            self.DB_PASSWORD,
            self.DB_HOST,
            self.DB_PORT,
            self.DB_NAME,
        ]
        if not all(required):
            raise ValueError("Database settings are incomplete. Check your .env file.")

        return (
            f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def effective_secret(self) -> str:
        """Choose JWT secret if available, otherwise fallback to SECRET_KEY."""
        return self.JWT_SECRET_KEY or self.SECRET_KEY or ""

    # -------------------------------------------------------------------------
    # Security Validation — Always run at startup
    # -------------------------------------------------------------------------
    @model_validator(mode="after")
    def validate_security(self):
        """
        Ensures that SECRET_KEY or JWT_SECRET_KEY is strong enough.
        This validator runs *after* all fields are loaded.
        """
        secret = self.JWT_SECRET_KEY or self.SECRET_KEY

        if (
            not secret
            or len(secret) < 32
            or secret in {
                "changeme",
                "secret",
                "your-secret-key-here",
                "CHANGE_ME_32+_CHAR_KEY",
            }
        ):
            raise ValueError(
                "\n" + "=" * 80 +
                "\nFATAL SECURITY ERROR: SECRET_KEY is weak or missing!\n"
                "Please generate a strong key using:\n\n"
                "   python - <<EOF\n"
                "import secrets\n"
                "print('SECRET_KEY=', secrets.token_urlsafe(64))\n"
                "EOF\n\n"
                "The server will not start until a secure key is provided.\n" +
                "=" * 80 + "\n"
            )

        return self

    # ---------------------------------------------------------------------
    # Subsystems (composition)
    # ---------------------------------------------------------------------
    LOGGING:LoggingSettings = LoggingSettings()


# Instantiate once
settings = Settings()
