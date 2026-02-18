# app/auth/deps.py

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast

from app.auth.jwt import decode_token
from app.core.context import get_request_context, set_request_context
from app.database.models.base.session import get_session
from app.database.repositories.users_repository import UsersRepository
from app.dtos.oauth_dtos import CurrentUserContext
from app.validators import ValidationErrorDetail, ErrorCodes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/oauth/token", auto_error=False)  # Important: don't raise on missing token

async def get_current_user(
    request: Request,  # Inject Request to get headers
    token: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> CurrentUserContext | None:
    """
    Returns authenticated user, but caches it in request context to avoid repeated DB hits.
    Returns None if no valid token.
    """
    ctx = get_request_context()

    # If we already resolved and cached the user in this request → return it
    if "current_user" in ctx:
        return cast(CurrentUserContext, ctx["current_user"])

    # No token → anonymous
    if not token:
        return None

    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="Invalid token payload 1")

    user_id = payload.get("sub")
    if not user_id:
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="Invalid token payload 2")

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="Invalid token payload 3")

    # Fetch user from DB
    user = await UsersRepository().get_by_id(session=session, id_values=user_id_int)
    if not user or user.is_deleted:
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="Invalid token payload 4")

    # Build context DTO
    user_context = CurrentUserContext(
        user_id=user.user_id,
        company_id=user.company_id,
        store_id = user.store_id if user.store_id else 0,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status_ind=user.status_ind,
        is_email_verified=bool(user.email_verified),
    )

    # CACHE in context for future calls in same request
    set_request_context(
        user_id=user_context.user_id,
        company_id=user_context.company_id,
        current_user=user_context,
        # ip already set in middleware
    )

    return user_context