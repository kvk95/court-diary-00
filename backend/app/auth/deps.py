from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast

from app.auth.jwt import decode_token
from app.core.context import get_request_context, set_request_context
from app.database.models.base.session import get_session
from app.database.repositories.users_repository import UsersRepository
from app.services.users_service import UsersService
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
    
    ctx = get_request_context() or {}

    # ✅ cache first
    if ctx.get("current_user"):
        return cast(CurrentUserContext, ctx["current_user"])

    # ✅ Prefer cookie over header
    cookie_token = request.cookies.get("access_token")

    if cookie_token:
        token = cookie_token

    # No token → anonymous
    if not token:
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Invalid token payload 0"
        )

    # ✅ reuse decoded token if available
    payload = ctx.get("token_payload")
    if not payload:
        payload = decode_token(token)
        set_request_context(**ctx, token_payload=payload)
        ctx = get_request_context() or {} 

    if not payload or payload.get("type") != "access":
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Invalid token payload 1"
        )
    temp_claim = payload.get("temp_claim", "")
    path = (ctx.get("path") or "").lower()
    method = (ctx.get("method") or "").lower()

    # ❌ Temp user → only login allowed
    if (temp_claim == "Y"):
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Invalid access for token type"
        )
    
    user_id = payload.get("sub")
    chamber_id = payload.get("chamber_id")
    if not user_id:
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Invalid token payload 2"
        )

    # Fetch user from DB
    user = await UsersRepository().get_by_id(
        session=session,
        id_values=user_id
    )

    if not user or user.deleted_ind:
        raise ValidationErrorDetail(
            code=ErrorCodes.PERMISSION_DENIED,
            message="User not found or deleted"
        )

    # ✅ Build context DTO (fixed field names)
    user_context = CurrentUserContext(
        user_id=user.user_id,
        chamber_id=chamber_id if chamber_id!=None else "",
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status_ind=user.status_ind,
        is_email_verified=bool(user.email_verified_ind),
    )

    user_service = UsersService(session=session)
    user_details = await user_service.get_user_full_details(user_id=user_context.user_id,
                                                                 chamber_id=user_context.chamber_id)
        

    # reset CACHE in context with user_details for future calls in same request
    set_request_context(
        **ctx,
        user_id=user_context.user_id,
        chamber_id=user_context.chamber_id,
        current_user=user_context,
        user_details=user_details,
    )
    

    return user_context