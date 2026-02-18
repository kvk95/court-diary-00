# app\utils\logging_framework\config.py

from enum import StrEnum
from typing import Any, Set, Optional
from pydantic import Field, field_validator, model_validator
import os, platform
from pydantic import BaseModel, ConfigDict

def default_log_dir() -> str:
    system = platform.system().lower()
    return (
        os.path.join("C:\\", "courtdiary", "logs")
        if system == "windows"
        else "/var/log/courtdiary"
    )


class LogTarget(StrEnum):
    NONE = "none"
    CONSOLE = "console"
    DB = "db"
    FILE = "file"
    ALL = "all"


class LoggingSettings(BaseModel):
    """
    Logging subsystem configuration.
    Loaded via composition inside app.core.config.Settings
    """
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    # ---- DB (logging sink) -----------------------------------------------
    LOG_DB_NAME: Optional[str] = Field(default=None, validation_alias="DB_NAME")
    LOG_DB_USER: Optional[str] = Field(default=None, validation_alias="DB_USER")
    LOG_DB_PASSWORD: Optional[str] = Field(default=None, validation_alias="DB_PASSWORD")
    LOG_DB_HOST: Optional[str] = Field(default=None, validation_alias="DB_HOST")
    LOG_DB_PORT: Optional[int] = Field(default=None, validation_alias="DB_PORT")
    LOG_DB_DRIVER: Optional[str] = Field(default=None, validation_alias="DB_DRIVER")

    # ---- Routing ----------------------------------------------------------
    LOG_DB_CALL: Set[LogTarget] = Field(default={LogTarget.CONSOLE}, validation_alias="DB_CALL")
    LOG_EXCEPTION: Set[LogTarget] = Field(default={LogTarget.NONE}, validation_alias="EXCEPTION")
    LOG_ACTIVITY: Set[LogTarget] = Field(default={LogTarget.NONE}, validation_alias="ACTIVITY")
    LOG_REQ_RESP: Set[LogTarget] = Field(default={LogTarget.CONSOLE}, validation_alias="REQ_RESP")

    # ---- File -------------------------------------------------------------
    LOG_FILE_MAX_BYTES: int = Field(default=100 * 1024 * 1024, validation_alias="FILE_MAX_BYTES")
    LOG_FILE_BACKUP_COUNT: int = Field(default=30, validation_alias="FILE_BACKUP_COUNT")
    LOG_FILE_DIR: str = Field(default_factory=default_log_dir, validation_alias="FILE_DIR")

    # ---- Queue ------------------------------------------------------------
    LOG_QUEUE_MAXSIZE: int = Field(default=10_000, validation_alias="QUEUE_MAXSIZE")
    LOG_WORKER_COUNT: int = Field(default=2, validation_alias="WORKER_COUNT")

    LOG_MASK_SENSITIVE: bool = True

    # ---------------------------------------------------------------------
    # Validators
    # ---------------------------------------------------------------------
    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for k, v in data.items():
                if v == "":
                    data[k] = None
        return data

    @field_validator(
        "LOG_DB_CALL",
        "LOG_EXCEPTION",
        "LOG_ACTIVITY",
        "LOG_REQ_RESP",
        mode="before",
    )
    @classmethod
    def parse_log_targets(cls, v):
        """
        Allow env values like:
        - console
        - console,db
        - none
        - all
        - ["console", "db"]  (JSON)
        """
        if v is None:
            return {LogTarget.NONE}

        # JSON list already parsed by dotenv loader
        if isinstance(v, (list, tuple, set)):
            targets = {LogTarget(item) for item in v}

        # Comma-separated string
        elif isinstance(v, str):
            parts = [p.strip().lower() for p in v.split(",") if p.strip()]
            targets = {LogTarget(p) for p in parts}

        else:
            raise TypeError(f"Invalid log target value: {v}")

        # Expand ALL
        if LogTarget.ALL in targets:
            return {LogTarget.CONSOLE, LogTarget.DB, LogTarget.FILE}

        # Validate NONE
        if LogTarget.NONE in targets and len(targets) > 1:
            raise ValueError("'none' cannot be combined with other log targets")

        return targets

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def log_to_console(self, targets: Set[LogTarget]) -> bool:
        return LogTarget.NONE not in targets and LogTarget.CONSOLE in targets

    def log_to_db(self, targets: Set[LogTarget]) -> bool:
        return LogTarget.NONE not in targets and LogTarget.DB in targets

    def log_to_file(self, targets: Set[LogTarget]) -> bool:
        return LogTarget.NONE not in targets and LogTarget.FILE in targets

    @property
    def logging_database_url(self) -> str:
        driver = self.LOG_DB_DRIVER or "mysql+aiomysql"
        user = self.LOG_DB_USER or ""
        pwd = self.LOG_DB_PASSWORD or ""
        host = self.LOG_DB_HOST or "localhost"
        port = self.LOG_DB_PORT or 3306
        db = self.LOG_DB_NAME or "logs_db"
        return f"{driver}://{user}:{pwd}@{host}:{port}/{db}"
