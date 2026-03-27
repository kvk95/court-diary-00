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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/oauth/token", auto_error=False)

async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> CurrentUserContext | None:
    """
    Returns authenticated user, caches in request context to avoid repeated DB hits.
    Returns None if no valid token.
    """
    ctx = get_request_context()

    # If already resolved and cached → return it
    if "current_user" in ctx:
        return cast(CurrentUserContext, ctx["current_user"])

    # No token → anonymous
    if not token:
        return None

    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="Invalid token payload q")

    user_id = payload.get("sub")
    chamber_id = payload.get("chamber_id") 
    
    if not user_id:
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="Invalid token payload 2")

    try:
        user_id_val = user_id
    except ValueError:
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="Invalid token payload 3")

    # Fetch user from DB
    user = await UsersRepository().get_by_id(session=session, id_values=user_id_val)
    if not user or user.deleted_ind:
        raise ValidationErrorDetail(code=ErrorCodes.PERMISSION_DENIED, message="User not found or deleted")

    # ✅ Build context DTO (fixed field names)
    user_context = CurrentUserContext(
        user_id=user.user_id,
        chamber_id=chamber_id if chamber_id!=None else "",  # ✅ Changed from company_id
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status_ind=user.status_ind,
        is_email_verified=bool(user.email_verified_ind),  # ✅ Fixed field name
    )

    # CACHE in context for future calls in same request
    set_request_context(
        user_id=user_context.user_id,
        chamber_id=user_context.chamber_id,  # ✅ Changed from company_id
        current_user=user_context,
    )

    return user_context