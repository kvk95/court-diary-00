# app/middleware/request_context_middleware.py

import json
import time
import uuid
from typing import Any
from urllib.parse import parse_qsl

from fastapi import Request
from starlette.types import ASGIApp, Scope, Receive, Send

from app.core.context import (
    clear_request_context,
    get_request_context,
)
from app.core.config import settings
from app.utils.logging_framework.log_types import LogType
from app.utils.logging_framework.logging_util import add_to_queue
from app.utils.logging_framework.config import LogTarget
from app.utils.logging_framework.logging_util import mask_sensitive

MAX_BODY_SIZE = 10_000
EXCLUDED_PATHS = {
    "/openapi.json",
    "/openapi.json.temp",
    "/apispec_1.json",
    "/docs",
    "/redoc",
    "/metrics",
    "/health",
}


def _safe_json_parse(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return text


def _trim_to_status_if_bas_out_dto(data: Any) -> Any:
    if (
        isinstance(data, dict)
        and "status" in data
        and "result" in data
        and isinstance(data["status"], dict)
        and "code" in data["status"]
    ):
        return {"status": data["status"]}
    return data


class RequestContextMiddleware:
    """
    Unified ASGI middleware that:
    1) Sets request-scoped context (request_id, ip)
    2) Lets dependencies enrich context (user_id, company_id)
    3) Logs request/response (config-driven)
    4) Clears context safely
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        # --------------------------------------------------
        # 1?? SET CONTEXT (ALWAYS FIRST)
        # --------------------------------------------------
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        ip = request.client.host if request.client else None

        start_time = time.perf_counter()

        body_bytes = b""
        response_bytes = b""
        status_code: int | None = None
        error: str | None = None
        content_type: str | None = None
        content_disposition: str | None = None

        # -------------------------
        # Wrap receive (request body)
        # -------------------------
        receive_ = receive

        async def receive_wrapper():
            nonlocal body_bytes
            message = await receive_()
            if message["type"] == "http.request" and len(body_bytes) < MAX_BODY_SIZE:
                body_bytes += message.get("body", b"")[: MAX_BODY_SIZE - len(body_bytes)]
            return message

        # -------------------------
        # Wrap send (response body)
        # -------------------------
        send_ = send

        async def send_wrapper(message):
            nonlocal response_bytes, status_code, content_type, content_disposition
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = dict(message.get("headers", []))
                for k, v in headers.items():
                    if k.lower() == b"content-type":
                        content_type = v.decode(errors="ignore").lower()
                    elif k.lower() == b"content-disposition":
                        content_disposition = v.decode(errors="ignore")
            elif message["type"] == "http.response.body":
                response_bytes += message.get("body", b"")
            await send_(message)

        def _extract_filename(content_disposition: str | None) -> str | None:
            if not content_disposition:
                return None
            # Typical format: attachment; filename="Invoice_123.pdf"
            parts = content_disposition.split(";")
            for part in parts:
                if "filename=" in part:
                    filename = part.split("=", 1)[1].strip().strip('"')
                    return filename
            return None

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        except Exception as exc:
            error = str(exc)
            status_code = 500
            raise
        finally:
            # --------------------------------------------------
            # 2?? OPTIONAL REQUEST / RESPONSE LOGGING
            # --------------------------------------------------
            if LogTarget.NONE not in settings.LOGGING.LOG_REQ_RESP:
                duration_ms = (time.perf_counter() - start_time) * 1000
                ctx = get_request_context() or {}

                # Decode request body
                request_body: Any = None
                if body_bytes:
                    text = body_bytes.decode("utf-8", errors="replace")[:MAX_BODY_SIZE]
                    request_body = _safe_json_parse(text)

                # response body decode
                response_body = None
                filename = _extract_filename(content_disposition)
                if response_bytes:
                    if content_type and not (
                        content_type.startswith("application/json")
                        # or content_type.startswith("text/")
                    ):
                        # Binary response ? omit body, log filename instead
                        response_body = {
                            "note": f"... {content_type.upper()} RESPONSE OMITTED ...",
                            "filename": filename,
                        }
                    else:
                        text = response_bytes.decode("utf-8", errors="replace")
                        parsed = _safe_json_parse(text)
                        url_path = scope["path"]

                        # -------------------------
                        # Mask / Exclude heavy responses
                        # -------------------------

                        if url_path in EXCLUDED_PATHS:
                            # For excluded paths, don’t log the heavy payload
                            parsed = {
                                "note": f"... RESPONSE OMITTED ...",
                                "filename": url_path,
                            }

                        response_body = _trim_to_status_if_bas_out_dto(parsed)

                payload = {
                    "request_id": ctx.get("request_id"),
                    "timestamp": time.time(),
                    "method": scope.get("method", "UNKNOWN"),
                    "path": scope["path"],
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                    "query_params": mask_sensitive(
                        dict(parse_qsl(scope.get("query_string", b"").decode()))
                    ),
                    "path_params": mask_sensitive(scope.get("path_params", {})),
                    "request_body": mask_sensitive(request_body),
                    "content_type": content_type,
                    "response_body": mask_sensitive(response_body),
                    "user_id": ctx.get("user_id"),
                    "company_id": ctx.get("company_id"),
                    "ip": ctx.get("ip"),
                    "error": error,
                }
                
                await add_to_queue(LogType.HTTP_LOG, payload)

            # --------------------------------------------------
            # 3?? CLEAR CONTEXT (ALWAYS LAST)
            # --------------------------------------------------
            clear_request_context()
