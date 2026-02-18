from datetime import datetime, timezone

from fastapi import Body, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from app.api.v1.routes.base.base_controller import BaseController
from app.auth.schemas import Token as SwaggerToken
from app.database.models.base.session import AsyncSession
from app.dtos.oauth_dtos import LoginRequest, RefreshRequest, TokenOut
from app.dependencies import get_auth_service, get_session
from app.dtos.base.base_out_dto import BaseOutDto
from app.services.auth_service import AuthService


class OAuthController(BaseController):
    CONTROLLER_NAME = "oauth"

    @BaseController.post("/token", include_in_schema=False, response_model=SwaggerToken)
    async def login_for_swagger(
        self,
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AuthService = Depends(get_auth_service),
    ):
        """Special endpoint ONLY for Swagger UI OAuth2 login — returns raw token (no envelope)"""
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")

        login_request = LoginRequest(
            email=form_data.username,
            password=form_data.password,
            ip_address=ip,
            user_agent=ua,
        )

        token_out: TokenOut = await service.login(login_request)

        access_token = token_out.access_token
        claims = jwt.get_unverified_claims(access_token)
        expires_in = claims["exp"] - int(datetime.now(timezone.utc).timestamp())

        return SwaggerToken(
            access_token=access_token,
            refresh_token=token_out.refresh_token,
            token_type=token_out.token_type.lower(),
            expires_in=expires_in,
        )

    @BaseController.post(
        "/login",
        summary="Login and get tokens",
        response_model=BaseOutDto[TokenOut],
    )
    async def login(
        self,
        request: Request,
        loginRequest: LoginRequest = Body(..., description="Login credentials"),
        service: AuthService = Depends(get_auth_service),
    ) -> BaseOutDto[TokenOut]:
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")

        loginRequest.ip_address = ip
        loginRequest.user_agent = ua

        output: TokenOut = await service.login(loginRequest)
        return self.success(result=output)

    @BaseController.post(
        "/refresh",
        summary="Refresh access token",
        response_model=BaseOutDto[TokenOut],
    )
    async def refresh_token(
        self,
        payload: RefreshRequest = Body(..., description="Refresh token payload"),
        session: AsyncSession = Depends(get_session),
        service: AuthService = Depends(get_auth_service),
    ) -> BaseOutDto[TokenOut]:
        output: TokenOut = await service.refresh(session, payload)
        return self.success(result=output)
