from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.chamber_resolver import resolve_user_chamber
from app.database.models.base.session import get_session
from app.database.repositories.users_repository import UsersRepository
from app.services.users_service import UsersService
from app.core.context import set_request_context
from app.utils.phone_util import normalize_phone
from app.validators import ValidationErrorDetail, ErrorCodes


async def get_current_user_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    data = await request.form()
    phone = data.get("From", "")

    if not phone:
        raise ValidationErrorDetail(
            code=ErrorCodes.NOT_FOUND,
            message="Phone not provided"
        )
    
    # Validate & narrow types
    if not isinstance(phone, str) or not phone:
        raise  ValidationErrorDetail(
            code=ErrorCodes.NOT_FOUND,
            message="Phone not valid"
        )

    # normalize
    phone = normalize_phone(phone=phone)

    # 🔥 get user
    user = await UsersRepository().get_by_phone(
        session=session,
        phone=phone
    )

    if not user:  
        if len(phone) == 10:
            phone = "91" + phone
            user = await UsersRepository().get_by_phone(
            session=session,
            phone=phone
        )
        if not user:
            raise ValidationErrorDetail(
                code=ErrorCodes.NOT_FOUND,
                message="User not found"
            )

    # 🔥 resolve chamber (REUSE SAME LOGIC)
    chamber_id = await resolve_user_chamber(
        session=session,
        user_id=user.user_id,
    )

    # 🔥 load full user details
    user_service = UsersService(session=session)
    user_details = await user_service.get_user_full_details(
        user_id=user.user_id,
        chamber_id=chamber_id,
    )

    # 🔥 SET CONTEXT (CRITICAL)
    set_request_context(
        user_id=user.user_id,
        chamber_id=chamber_id,
        user_details=user_details,
    )

    return user_details