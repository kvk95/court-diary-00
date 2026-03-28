import traceback
from datetime import datetime

from ...core.context import get_request_context
from .log_types import LogType
from .logging_util import add_to_queue


async def log_exception(exc: Exception, request=None, error_code: str | None = None):
    """
    Enqueue exception log.
    Routing (none / console / db / file) is handled by the queue worker.
    """

    ctx = get_request_context()

    path = method = query_params = body = headers = None

    if request is not None:
        try:
            path = str(request.url.path)
            method = request.method

            try:
                query_params = dict(request.query_params)
            except Exception:
                query_params = None

            try:
                if hasattr(request, "body"):
                    raw_body = await request.body()
                    if raw_body:
                        body = raw_body.decode("utf-8", errors="replace")[:10_000]
            except Exception:
                body = None

            try:
                headers = dict(request.headers)
                # OPTIONAL hardening: strip auth headers
                headers.pop("authorization", None)
                headers.pop("cookie", None)
            except Exception:
                headers = None

        except Exception:
            pass

    payload = {     
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "exception_type": exc.__class__.__name__,
        "message": str(exc),
        "stacktrace": "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ),
        "path": path,
        "method": method,
        "query_params": query_params,
        "request_body": body,
        "headers": headers,
        "user_id": ctx.get("user_id") if ctx else None,
        "company_id": ctx.get("company_id") if ctx else None,
        "error_code": error_code,
        "meta": {},
    }
    
    await add_to_queue(log_type= LogType.EXCEPTION, payload =  payload)
