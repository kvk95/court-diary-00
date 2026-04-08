"""app/api/v1/routes/anonymous_controller.py"""

from fastapi import Body, Depends, Query

from app.api.v1.routes.base.base_controller import BaseController
from app.database.cache.refm_cache import RefmData
from app.dependencies import (
    get_anonymous_service
)
from app.dtos.anonymous_dtos import ServerDateTimeOut
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.users_dto import UserCreateBasic, UserEmailIn, UserPasswordIn
from app.services.anonymous_service import AnonymousService


class AnonymousController(BaseController):
    CONTROLLER_NAME = "anonymous"

    @BaseController.get(
        "/server_datetime",
        summary="Get current server date & time",
        description="Returns server UTC datetime – useful for client clock sync",
        response_model=BaseOutDto[ServerDateTimeOut],
    )
    async def get_server_datetime(
        self,
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[ServerDateTimeOut]:
        result: ServerDateTimeOut = await service.get_server_datetime()
        return self.success(result=result)

    @BaseController.get(
        "/refm",
        summary="Get all reference values",
        description="Returns all available refms",
        response_model=BaseOutDto[RefmData],
    )
    async def get_all_refm(
        self,
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[RefmData]:
        result: RefmData = await service.get_all_refm()
        return self.success(result=result)

    @BaseController.post(
        "/createuser",
        summary="create user",
        response_model=BaseOutDto[str],
    )
    async def users_add(
        self,
        payload: UserCreateBasic = Body(..., description="New user data"),
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[str]:
        result: str = await service.users_add(payload)
        return self.success(result=result) 
    @BaseController.put(
        "/resendactivationlink",
        summary="Reactivate the inactive or deleted user",
        response_model=BaseOutDto[str],
    )
    async def resend_activation_linkn(
        self,
        payload: UserEmailIn = Body(..., description="User Email"),
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[str]:
        result: str = await service.resendactivationlink(payload=payload)
        return self.success(result=result)

    @BaseController.put(
        "/activateuser",
        summary="Activate the inactive or deleted user",
        response_model=BaseOutDto[str],
    )    
    async def users_reset(
        self,
        link_id: str = Query(None, description="Link id"),
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[dict[str, str]]:
        result: dict[str, str] = await service.users_reset(link_id)
        return self.success(result=result)

    @BaseController.put(
        "/resetpassword",
        summary="Forgot password",
        response_model=BaseOutDto[str],
    )
    async def users_password_reset(
        self,        
        payload: UserEmailIn = Body(..., description="User Email"),
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[str]:
        result: str = await service.users_password_reset(payload=payload)
        return self.success(result=result)

    @BaseController.put(
        "/new_password",
        summary="set new password",
        response_model=BaseOutDto[str],
    )
    async def users_new_password(
        self,
        link_id: str = Query(None, description="Link id"),
        payload: UserPasswordIn = Body(..., description="New user data"),
        service: AnonymousService = Depends(get_anonymous_service),
    ) -> BaseOutDto[dict[str, str]]:
        result: dict[str, str] = await service.users_new_password(link_id=link_id, payload=payload)
        return self.success(result=result)