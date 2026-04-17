# app\auth\csrf_token_util.py

import secrets

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

from fastapi import Request
from app.validators import ValidationErrorDetail, ErrorCodes

async def validate_csrf(request: Request):
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")

    if not cookie_token or not header_token:
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="CSRF token missing",
        )

    if cookie_token != header_token:
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Invalid CSRF token",
        )