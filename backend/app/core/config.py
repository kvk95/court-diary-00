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
    CIPHER_SECRET_KEY: Optional[str] = None
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

    UI_URL:str = "http://localhost:8080/"

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    CORS_ALLOWED_ORIGINS: Sequence[str] = (
        "http://localhost:3000",
        "http://localhost:3001",
    )
    CORS_ENABLED: bool = True

    SMTP_SERVER: Optional[str] = None
    SMTP_SERVER_PORT: Optional[int] = None
    SMTP_SERVER_USERNAME: Optional[str] = None
    SMTP_SERVER_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: Optional[bool] = False

    # OAUTH
    GOOGLE_OAUTH_CLOCK_SKEW_IN_SECONDS:int = 0

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
    
    @model_validator(mode="after")
    def validate_smtp(self):
        """
        Ensures SMTP configuration is valid when provided.
        Enforces security best practices.
        """

        # If partially configured → fail
        if not self.SMTP_SERVER or not self.SMTP_SERVER_PORT or not self.SMTP_SERVER_USERNAME or not self.SMTP_SERVER_PASSWORD:
            raise ValueError(
                "\n" + "=" * 80 +
                "\nFATAL CONFIG ERROR: Incomplete SMTP configuration!\n"
                "All SMTP fields must be provided:\n"
                "  - SMTP_SERVER\n"
                "  - SMTP_SERVER_PORT\n"
                "  - SMTP_SERVER_USERNAME\n"
                "  - SMTP_SERVER_PASSWORD\n"
                "=" * 80 + "\n"
            )

        # Port validation
        if not (1 <= int(self.SMTP_SERVER_PORT) <= 65535):
            raise ValueError("SMTP_SERVER_PORT must be between 1 and 65535")

        # Basic security checks
        weak_values = {"", "changeme", "password", "123456"}

        if self.SMTP_SERVER_PASSWORD.lower() in weak_values:
            raise ValueError(
                "\n" + "=" * 80 +
                "\nFATAL SECURITY ERROR: Weak SMTP password detected!\n"
                "Use a strong app-specific password.\n"
                "=" * 80 + "\n"
            )

        # TLS recommendation enforcement
        if not self.SMTP_USE_TLS:
            raise ValueError(
                "\n" + "=" * 80 +
                "\nFATAL SECURITY ERROR: SMTP_USE_TLS is disabled!\n"
                "TLS is required to protect credentials in transit.\n"
                "=" * 80 + "\n"
            )

        return self

    # ---------------------------------------------------------------------
    # Subsystems (composition)
    # ---------------------------------------------------------------------
    LOGGING:LoggingSettings = LoggingSettings()


# Instantiate once
settings = Settings()
