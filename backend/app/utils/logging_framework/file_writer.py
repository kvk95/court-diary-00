import asyncio
import json
import logging
import os
from logging.handlers import RotatingFileHandler

from app.utils.logging_framework.config import LoggingSettings


class FileWriter:
    def __init__(self, logging_settings: LoggingSettings):
        self.logging_settings = logging_settings
        os.makedirs(self.logging_settings.LOG_FILE_DIR, exist_ok=True)

        # Create dedicated loggers + handlers for each log type
        self.http_logger = self._create_logger("http.log", "file.http")
        self.db_call_logger = self._create_logger("db_calls.log", "file.db_call")
        self.exception_logger = self._create_logger("exceptions.log", "file.exception")
        self.activity_logger = self._create_logger("activity.log", "file.activity")

    def _create_logger(self, filename: str, logger_name: str) -> logging.Logger:
        file_path = os.path.join(self.logging_settings.LOG_FILE_DIR, filename)
        handler = RotatingFileHandler(
            file_path,
            maxBytes=self.logging_settings.LOG_FILE_MAX_BYTES,
            backupCount=self.logging_settings.LOG_FILE_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))

        logger = logging.getLogger(logger_name)
        logger.propagate = False
        logger.setLevel(logging.INFO)
        logger.handlers.clear()  # Ensure clean state
        logger.addHandler(handler)
        return logger

    async def _write(self, logger: logging.Logger, payload: dict):
        try:
            line = json.dumps(payload, default=str, ensure_ascii=False)
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, logger.info, line)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to write log to file: {e}")

    async def write_http(self, payload: dict):
        await self._write(self.http_logger, payload)

    async def write_db_call(self, payload: dict):
        await self._write(self.db_call_logger, payload)

    async def write_exception(self, payload: dict):
        await self._write(self.exception_logger, payload)

    async def write_activity(self, payload: dict):
        await self._write(self.activity_logger, payload)

    def close(self):
        """Close all handlers on shutdown"""
        for logger in [self.http_logger, self.db_call_logger,
                       self.exception_logger, self.activity_logger]:
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)