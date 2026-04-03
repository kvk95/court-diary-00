import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.utils.logging_framework.config import LoggingSettings
from app.database.models.activity_log import ActivityLog
from app.database.models.db_call_log import DbCallLog
from app.utils.logging_framework.schemas import (
    ActivityLogPayload,
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

    async def insert_db_call(self, payload: dict):
        try:            
            ctx = payload.get("_ctx", {})

            clean_payload = {k: v for k, v in payload.items() if k != "_ctx"}
            # 🔥 Convert dict → Pydantic model
            # db_log_payload = DBCallLogPayload(**clean_payload)
            
            inst = DbCallLog(
                id=DbCallLog.generate_uuid(),
                timestamp=payload["timestamp"],
                duration_ms=payload["duration_ms"],
                raw_query=payload["raw_query"],
                params=payload["params"] or {},
                final_query=payload["final_query"],
                repo=payload["repo"],
                actor_user_id=ctx.get("user_id"),
                actor_chamber_id=ctx.get("chamber_id"),
                error=payload["error"],
                metadata_json=payload["metadata_json"] or {},
            )
            # await self._insert(inst)
        except Exception as e:
            _log.exception(f"Failed to insert DB_CALL_LOG: {e}")

    async def insert_exception(self, payload: ExceptionLogPayload):
        try:
            pass  # TODO
        except Exception:
            _log.exception("Failed to insert EXCEPTION_LOG")

    async def insert_activity(self, payload: dict):
        try:
            ctx = payload.get("_ctx", {})

            clean_payload = {k: v for k, v in payload.items() if k != "_ctx"}
            # 🔥 Convert dict → Pydantic model
            activity_payload = ActivityLogPayload(**clean_payload)

            inst = ActivityLog(
                timestamp=activity_payload.timestamp,
                action=activity_payload.action,
                target=activity_payload.target,
                metadata_json=(
                    activity_payload.metadata_json.model_dump()
                    if activity_payload.metadata_json else None
                ),

                actor_user_id=ctx.get("user_id"),
                actor_chamber_id=ctx.get("chamber_id"),
                ip_address=ctx.get("ip"),

                created_by=ctx.get("user_id"),
            )

            await self._insert(inst)

        except Exception as e:            
            print(e)
            _log.exception("Failed to insert ACTIVITY_LOG")
