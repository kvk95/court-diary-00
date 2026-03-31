# app/middleware/exception_handler.py

import traceback
from http import HTTPStatus
from typing import Any, Optional, cast

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError

from app.validators.error_codes import ErrorCodes, CodeDescription
from app.validators import ApplicationError, ValidationAggregateError, ValidationErrorDetail
from app.dtos.base.base_out_dto import BaseOutDto
from app.utils.logging_framework.exception_logger import (
    log_exception as exception_logger,
)
from app.core.config import settings


# Valid HTTP status values
VALID_HTTP_STATUSES = {status.value for status in HTTPStatus}


def format_validation_error(err: dict) -> str:
    """
    Format a FastAPI/Pydantic validation error into a readable string.

    - Uses `msg` as the base message.
    - Appends field path (excluding body/query/path) for clarity.
    """
    msg = err.get("msg", ErrorCodes.VALIDATION_ERROR.description)
    loc = err.get("loc", [])
    field_path = [str(p) for p in loc if p not in ("body", "query", "path")]

    if field_path:
        return f"{msg} {'/'.join(field_path)}"
    return msg


# =====================================================================
# CORE RESPONSE BUILDER
# =====================================================================
async def build_error_response(
    request: Request,
    *,
    code: CodeDescription,
    description: str,
    status_code: int = 200,  # Default: 200 unless overridden
    details: Any = None,
    exc: Optional[Exception] = None,
) -> JSONResponse:
    """
    Centralized error response builder.

    - HTTP 200 for business-level failures (default).
    - If the error code is a numeric string corresponding to a valid HTTP status (e.g., '500'), that status is used.
    - Extra diagnostics included in non-production environments.
    - Exceptions logged only for server-side failures (>=500).
    """

    # Override HTTP status only if ApplicationError encodes a valid HTTP code
    if isinstance(exc, ApplicationError):
        raw_code = exc.code.code
        if raw_code.isdigit():
            candidate = int(raw_code)
            if candidate in VALID_HTTP_STATUSES:
                status_code = candidate

    dto = BaseOutDto.failure(code=code, description=description)

    if details is not None:
        dto.result = {"details": details}

    # Development diagnostics
    if settings.APP_ENV != "production" and exc is not None:
        dto.result = dto.result or {}
        if status_code >= 500:
            dto.result["trace"] = traceback.format_exc()

    # Log only server-side failures
    if exc is not None and status_code >= 500:
        try:
            await exception_logger(exc, request=request)
        except Exception:
            pass
        
    return JSONResponse(status_code=status_code, content=dto.model_dump())


# =====================================================================
# Request validation errors
# =====================================================================
async def request_validation_exception_handler(request: Request, exc: Exception):
    """
    Handle FastAPI RequestValidationError (invalid request body/query/path).

    - Collects all validation messages.
    - Defaults to HTTP 500 (internal server error).
    - Includes full error details in non-production environments.
    In a well-tested system, these should be rare in production,
    but when they occur they indicate contract mismatch between client and server.
    """
    rve = cast(RequestValidationError, exc)
    errors = rve.errors()

    description = ", ".join(format_validation_error(err) for err in errors)

    return await build_error_response(
        request,
        code=ErrorCodes.VALIDATION_ERROR,
        description=description,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        details=errors if settings.APP_ENV != "production" else None,
        exc=rve,
    )


# =====================================================================
# ValidationErrorDetail (special 401 mapping)
# =====================================================================
async def validation_error_handler(request: Request, exc: Exception):
    """
    Handle ValidationErrorDetail (business-level validation errors).

    - Explicit mapping: only error code "401" → HTTP 401.
    - All other codes default to HTTP 200.
    """
    ve = cast(ValidationErrorDetail, exc)
    ERROR_CODE_TO_HTTP = {"401": 401}  # PERMISSION_DENIED

    status_code = ERROR_CODE_TO_HTTP.get(ve.code.code, 200)

    return await build_error_response(
        request,
        code=ve.code,
        description=ve.message,
        status_code=status_code,
        exc=ve,
    )


# =====================================================================
# Application errors (including ValidationAggregateError)
# =====================================================================
async def application_error_handler(request: Request, exc: Exception):
    """
    Handle ApplicationError and ValidationAggregateError.

    - Aggregates multiple validation messages if ValidationAggregateError.
    - Defaults to HTTP 200 unless overridden by numeric error code.
    """
    app_exc = cast(ApplicationError, exc)

    if isinstance(app_exc, ValidationAggregateError):
        description = ", ".join(
            e.message or ErrorCodes.VALIDATION_ERROR.description
            for e in getattr(app_exc, "errors", [])
        )
    else:
        description = app_exc.message

    return await build_error_response(
        request,
        code=app_exc.code,
        description=description,
        status_code=200,
        exc=app_exc,
    )


# =====================================================================
# Database integrity errors
# =====================================================================
async def integrity_error_handler(request: Request, exc: Exception):
    """
    Handle SQLAlchemy IntegrityError (constraint violations).

    - Always returns HTTP 200 with INTEGRITY_ERROR code.
    """
    ie = cast(IntegrityError, exc)
    msg = str(ie.orig) if ie.orig else str(ie)

    return await build_error_response(
        request,
        code=ErrorCodes.INTEGRITY_ERROR,
        description=msg,
        status_code=500,
        exc=ie,
    )


# =====================================================================
# Starlette HTTP exceptions (404, 401, etc.)
# =====================================================================
async def starlette_http_exception_handler(request: Request, exc: Exception):
    """
    Handle Starlette HTTPException (e.g., 404 Not Found, 401 Unauthorized).

    - Preserves original HTTP status code (404, 401, etc.).
    - Maps to appropriate application error codes when possible.
    - Maintains compatibility with client-side HTTP error handling.
    """
    http_exc = cast(StarletteHTTPException, exc)

    if http_exc.status_code == 404:
        code = ErrorCodes.NOT_FOUND
        description = ErrorCodes.NOT_FOUND.description
    elif http_exc.status_code == 401:
        code = ErrorCodes.PERMISSION_DENIED
        description = ErrorCodes.PERMISSION_DENIED.description
    else:
        code = ErrorCodes.FAILURE
        description = str(http_exc.detail)

    return await build_error_response(
        request,
        code=code,
        description=description,
        status_code=http_exc.status_code,  # ← preserve original status
        exc=http_exc,
    )


# =====================================================================
# Response validation errors
# =====================================================================
async def response_validation_exception_handler(request: Request, exc: Exception):
    """
    Handle FastAPI ResponseValidationError (invalid response model).

    In a well-tested system, this should not occur in production.
    Therefore, we treat it as a server error (500) to encourage contract adherence.

    - Defaults to HTTP 500.
    - Includes details in non-production environments.
    """
    rve = cast(ResponseValidationError, exc)
    errors = rve.errors()

    description = ", ".join(format_validation_error(err) for err in errors)

    return await build_error_response(
        request,
        code=ErrorCodes.VALIDATION_ERROR,
        description=description,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        details=errors if settings.APP_ENV != "production" else None,
        exc=rve,
    )


# =====================================================================
# Final fallback
# =====================================================================
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle all other uncaught exceptions.

    - Defaults to HTTP 500 with FAILURE code.
    - Includes full error details in non-production environments.
    """
    description = (
        str(exc)
        if settings.APP_ENV != "production"
        else ErrorCodes.FAILURE.description
    )

    return await build_error_response(
        request,
        code=ErrorCodes.FAILURE,
        description=description,
        status_code=500,
        exc=exc,
    )

def add_exception_handlers(app: FastAPI) -> None:
    """
    Register all application exception handlers with the FastAPI app.

    Handlers are registered in **most-specific to least-specific** order.
    FastAPI uses the **first matching handler**, so subclasses
    (e.g., ValidationErrorDetail) must be registered **before** their
    parent classes (e.g., ApplicationError).

    Registration order:
    1. Request/Response validation errors (schema mismatches)
    2. Custom business errors (ValidationErrorDetail, ApplicationError, etc.)
    3. Database integrity errors (SQLAlchemy IntegrityError)
    4. Standard HTTP exceptions (Starlette/FastAPI HTTPException)
    5. Generic fallback (catches all remaining exceptions)

    ⚠️ The generic `Exception` handler must always be last.
    """
    
    # ------------------------------------------------------------------
    # 1. FastAPI / Pydantic validation errors
    # ------------------------------------------------------------------
    # Raised when request or response data fails schema validation.
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ResponseValidationError, response_validation_exception_handler)

    # ------------------------------------------------------------------
    # 2. Custom application-level (business) errors
    # ------------------------------------------------------------------
    # Register specific subclasses before their parent class.
    # ValidationErrorDetail has special HTTP 401 handling.
    app.add_exception_handler(ValidationErrorDetail, validation_error_handler)
    app.add_exception_handler(ApplicationError, application_error_handler)

    # ------------------------------------------------------------------
    # 3. Database constraint violations
    # ------------------------------------------------------------------
    # IntegrityError from SQLAlchemy (e.g., unique constraint, FK violation).
    app.add_exception_handler(IntegrityError, integrity_error_handler)

    # ------------------------------------------------------------------
    # 4. Starlette HTTP exceptions (404 Not Found, 401 Unauthorized, etc.)
    # ------------------------------------------------------------------
    # Includes HTTPException raised internally by FastAPI or manually.
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)

    # ------------------------------------------------------------------
    # 5. Catch-all fallback for unhandled exceptions
    # ------------------------------------------------------------------
    # MUST be registered last — catches any exception not handled above.
    # Returns HTTP 500 with a generic failure message.
    app.add_exception_handler(Exception, generic_exception_handler)
