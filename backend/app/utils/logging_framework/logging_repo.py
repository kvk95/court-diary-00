import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.utils.logging_framework.config import LoggingSettings
from app.database.models.activity_log import ActivityLog
from app.database.models.db_call_log import DbCallLog
from app.utils.logging_framework.schemas import (
    ActivityLogPayload,
    DBCallLogPayload,
    ExceptionLogPayload,
)

_log = logging.getLogger(__name__)


class LoggingRepo:
    def __init__(self, logging_settings: LoggingSettings):
        self.logging_settings = logging_settings

        # Async engine for logging database
        self.engine = create_async_engine(
            self.logging_settings.logging_database_url,
            future=True,
            pool_pre_ping=True,
        )

        self.SessionLocal = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def _insert(self, instance):
        async with self.SessionLocal() as session:
            async with session.begin():
                session.add(instance)

    async def insert_db_call(self, payload: DBCallLogPayload):
        try:
            inst = DbCallLog(
                timestamp=payload.timestamp,
                duration_ms=payload.duration_ms,
                raw_query=payload.raw_query,
                params=json.dumps(payload.params or {}),
                final_query=payload.final_query,
                repo=payload.repo,
                user_id=payload.user_id,
                company_id=payload.company_id,
                error=payload.error,
                metadataz=json.dumps(payload.metadataz or {}),
            )
            await self._insert(inst)
        except Exception:
            _log.exception("Failed to insert DB_CALL_LOG")

    async def insert_exception(self, payload: ExceptionLogPayload):
        try:
            pass  # TODO
        except Exception:
            _log.exception("Failed to insert EXCEPTION_LOG")

    async def insert_activity(self, payload: ActivityLogPayload):
        try:
            inst = ActivityLog(
                timestamp=payload.timestamp,
                action=payload.action,
                actor_user_id=payload.actor_user_id,
                actor_company_id=payload.actor_company_id,
                target=payload.target,
                metadataz=json.dumps(payload.metadataz or {}),
                ip_address=payload.ip_address,
            )
            await self._insert(inst)
        except Exception:
            _log.exception("Failed to insert ACTIVITY_LOG")
