"""
Docstring for app.services.base.secured_base_service
"""

from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_request_context
from app.dtos.oauth_dtos import CurrentUserContext
from app.services.base.base_service import BaseService


class BaseSecuredService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def current_user(self) -> CurrentUserContext:
        ctx = get_request_context()
        return cast(CurrentUserContext, ctx.get("current_user"))

    @property
    def user_id(self) -> str:
        ctx = get_request_context()
        return cast(str, ctx.get("user_id"))

    @property
    def chamber_id(self) -> str:
        ctx = get_request_context()
        return cast(str, ctx.get("chamber_id"))