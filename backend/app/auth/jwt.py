import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt, ExpiredSignatureError, JWTError

from app.core.config import settings
from app.validators import ValidationErrorDetail, ErrorCodes

ALGORITHM = settings.ALGORITHM


def create_access_token(
    subject: Any,
    extra_claims: dict | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    claims = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": now,
        "jti": secrets.token_urlsafe(12),
    }
    if extra_claims:
        claims.update(extra_claims)

    access_token: str = jwt.encode(
        claims, settings.effective_secret, algorithm=ALGORITHM
    )

    print("Token issued at:", datetime.now(timezone.utc))
    print(
        "Token expires at:",
        datetime.fromtimestamp(
            jwt.get_unverified_claims(access_token)["exp"], tz=timezone.utc
        ),
    )

    return access_token


def create_refresh_token(subject: Any, extra_claims: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    claims = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": now,
        "jti": secrets.token_urlsafe(32),
    }
    if extra_claims:
        claims.update(extra_claims)

    return jwt.encode(claims, settings.effective_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        # PyJWT automatically handles timezone-aware datetimes
        return jwt.decode(token, settings.effective_secret, algorithms=[ALGORITHM])

    except ExpiredSignatureError:
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Token has expired"
        )

    except JWTError:
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Invalid token"
        )
