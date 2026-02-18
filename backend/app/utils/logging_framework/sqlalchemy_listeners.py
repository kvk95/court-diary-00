import logging
import time
from datetime import datetime

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

from ...core.context import get_request_context
from .log_types import LogType
from .logging_util import add_to_queue, mask_sensitive

_log = logging.getLogger(__name__)



def _reconstruct_query(raw, params):
    try:
        if params is None:
            return raw

        if isinstance(params, (list, tuple)):
            final = raw
            for p in params:
                final = final.replace("%s", repr(p), 1)
            return final

        if isinstance(params, dict):
            final = raw
            for key, val in params.items():
                rep = repr(val)
                final = final.replace(f":{key}", rep)
                final = final.replace(f"%({key})s", rep)
            return final
    except Exception:
        _log.exception("Failed to reconstruct query")

    return None


def attach_listeners(async_engine: AsyncEngine):
    """
    Attach SQLAlchemy listeners to capture DB call metrics.
    Routing is handled later by LoggingQueueManager.
    """

    @event.listens_for(async_engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        context._query_start_time = time.perf_counter()
        context._log_payload = {
                "timestamp": None,
                "duration_ms": None,
                "raw_query": statement,
                "params": mask_sensitive(parameters) if parameters else {},
                "final_query": None,
                "repo": None,
                "user_id": None,
                "company_id": None,
                "error": None,
                "metadataz": {},
        }

    @event.listens_for(async_engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        try:
            payload = getattr(context, "_log_payload", None)
            if not payload:
                return

            start = getattr(context, "_query_start_time", None)
            duration_ms = (
                (time.perf_counter() - start) * 1000.0 if start else 0.0
            )

            ctx = get_request_context()

            payload.update(
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "duration_ms": round(duration_ms, 3),
                    "final_query": _reconstruct_query(statement, parameters),
                    "repo": ctx.get("repo") if ctx else None,
                    "user_id": ctx.get("user_id") if ctx else None,
                    "company_id": ctx.get("company_id") if ctx else None,
                }
            )
            
            add_to_queue(log_type= LogType.DB_CALL, payload =  payload)

        except Exception:
            _log.exception("after_cursor_execute error")

    @event.listens_for(async_engine.sync_engine, "handle_error")
    def handle_error(exception_context):
        try:
            ctx = get_request_context()

            payload = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "duration_ms": None,
                    "raw_query": getattr(exception_context, "statement", "") or "",
                    "params": mask_sensitive(
                        getattr(exception_context, "parameters", None)
                    ),
                    "final_query": None,
                    "repo": ctx.get("repo") if ctx else None,
                    "user_id": ctx.get("user_id") if ctx else None,
                    "company_id": ctx.get("company_id") if ctx else None,
                    "error": str(exception_context.original_exception),
                    "metadataz": {
                        "exception_context": str(exception_context)
                },
            }
            add_to_queue(log_type= LogType.DB_CALL, payload =  payload)

        except Exception:
            _log.exception("handle_error log failed")
