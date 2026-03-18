# app/api/v1/routes/users_controller.py


from fastapi import Body, Depends

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_users_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.users_dto import UserCreate
from app.services.users_service import UsersService


class UsersController(BaseController):
    CONTROLLER_NAME = "users"

    # -- USERS --------------------------------------------------------------
    @BaseController.post(
        "/users/add",
        summary="Add user",
        response_model=BaseOutDto[int],
    )
    async def users_add(
        self,
        payload: UserCreate = Body(..., description="New user data"),
        service: UsersService = Depends(get_users_service),
    ) -> BaseOutDto[int]:
        result: int = await service.users_add(payload)
        return self.success(result=result)