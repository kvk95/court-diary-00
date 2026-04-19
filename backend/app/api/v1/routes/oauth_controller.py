import base64
from datetime import datetime, timezone
import uuid

from fastapi import Body, Depends, Path, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import requests

from app.api.v1.routes.base.base_controller import BaseController
from app.auth.csrf_token_util import generate_csrf_token
from app.core.config import settings
from app.database.models.base.session import AsyncSession
from app.dtos.oauth_dtos import LoginRequest, OAuthLoginRequest, RefreshRequest, TokenOut
from app.dependencies import get_anonymous_service, get_auth_service, get_session
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.users_dto import UserCreateoAuth
from app.services.anonymous_service import AnonymousService
from app.services.auth_service import AuthService

from app.validators import (
    ErrorCodes,
    ValidationErrorDetail,
)
from app.validators.validation_errors import ApplicationError


class OAuthController(BaseController):
    CONTROLLER_NAME = "oauth"

    @BaseController.post("/token", include_in_schema=False, response_model=TokenOut)
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

        try:
            token_out: TokenOut = await service.login(login_request, is_regular=False)
        except ValidationErrorDetail as e:
            raise ValidationErrorDetail(
                code=ErrorCodes.PERMISSION_DENIED,
                message=e.message,
            )

        self.set_token_expiry(token_out)

        return token_out

    @BaseController.post(
        "/login",
        summary="Login and get tokens",
        response_model=BaseOutDto[TokenOut],
    )
    async def login(
        self,
        request: Request,
        response: Response,
        loginRequest: LoginRequest = Body(..., description="Login credentials"),
        service: AuthService = Depends(get_auth_service),
    ) -> BaseOutDto[TokenOut]:
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")

        loginRequest.ip_address = ip
        loginRequest.user_agent = ua

        token_out: TokenOut = await service.login(loginRequest)

        # ✅ Set cookies (single call)
        await self.set_auth_cookies(response, token_out)
        token_out = self.clear_tokens_from_response(token_out)
        return self.success(result=token_out)

    @BaseController.post(
        "/refresh",
        summary="Refresh access token",
        response_model=BaseOutDto[TokenOut],
    )
    async def refresh_token(
        self,
        response: Response,
        payload: RefreshRequest = Body(...),
        session: AsyncSession = Depends(get_session),
        service: AuthService = Depends(get_auth_service),
    ) -> BaseOutDto[TokenOut]:

        token_out = await service.refresh(session, payload)

        await self.set_auth_cookies(response, token_out)
        self.clear_tokens_from_response(token_out)

        return self.success(result=token_out) 

    @BaseController.post(
        "/{provider}/login",
        summary="Login through oAuth",
        response_model=BaseOutDto[TokenOut],
    )
    async def oauth_login(
        self,
        response: Response,
        service: AuthService = Depends(get_auth_service),
        anonymous_service: AnonymousService = Depends(get_anonymous_service),
        provider: str = Path(description="oAuth Token"),
        loginRequest: OAuthLoginRequest = Body(..., description="Login credentials"),
        ):

        provider = provider.lower()
        # github_token = request.json.get("access_token")
        code = loginRequest.code
        if not code:
            # return jsonify({"error": "code is required"}), 400
            raise ApplicationError(
                    code=ErrorCodes.FAILURE,
                    message="code is required",
            )

        user_data = {}

        if provider == "github":
            # user_data = OauthController.__github_user_info(code)
            pass
        elif provider == "google":
            user_data = self.__google_user_info(code)
        elif provider == "linkedin":
            # user_data = OauthController.__linkedin_user_info(code)
            pass

        user_data["provider"] = provider

        payload = UserCreateoAuth(
            email = user_data.get("email"),
            first_name = user_data.get("first_name"),
            last_name = user_data.get("last_name"),
            image_data = user_data.get("image_data", None),
        )

        is_exists, email = await anonymous_service.is_oauth_user_exists(payload=payload)

        if not is_exists:
            email = await anonymous_service.oauth_users_add(payload=payload)

        login_request = LoginRequest(
            email=email or '',
            password=str(uuid.uuid4()),
            chamber_id=loginRequest.chamber_id
        )
        token_out: TokenOut = await service.login(login_request, is_oAuth=True)
        await self.set_auth_cookies(response, token_out)
        self.clear_tokens_from_response(token_out)

        return self.success(result=token_out)

    def __google_user_info(self,code):
        # Retrieve the environment variable
        clock_skew = settings.GOOGLE_OAUTH_CLOCK_SKEW_IN_SECONDS
        clock_skew = f"{clock_skew}"

        # Check and convert if the value is a string
        if isinstance(clock_skew, str):
            try:
                clock_skew = int(clock_skew)
            except ValueError:
                clock_skew = 0  # or handle the error as needed

        # Ensure it is an integer
        if not isinstance(clock_skew, int):
            clock_skew = 0  # or set a default value

        request_instance = google_requests.Request()
        user_info = id_token.verify_oauth2_token(
            code,
            request_instance,
            clock_skew_in_seconds=clock_skew,
        )

        # Initialize avatar as an empty bytes object
        avatar = b""

        # Fetch the profile image from Google and store it as a binary blob
        avatar_url = user_info.get("picture")
        if avatar_url:
            image_response = requests.get(avatar_url, stream=True)
            if image_response.status_code == 200:
                # Store the binary content of the image in avatar
                avatar_bytes = image_response.content
        
                # Detect MIME type from headers (fallback to png if missing)
                content_type = image_response.headers.get("Content-Type", "image/png")
                
                # Convert to Base64
                avatar_base64 = base64.b64encode(avatar_bytes).decode("utf-8")
                
                # Build full data URI
                avatar_data_uri = f"data:{content_type};base64,{avatar_base64}"

        user_data = {
            "email": user_info.get("email"),
            "first_name": user_info.get("given_name", "Name Unknown"),
            "last_name": user_info.get("family_name", ""),
            "image_data": avatar_data_uri,
        }
        return user_data

    @BaseController.post(
        "/logout",
        summary="Logout of application",
        response_model=BaseOutDto[TokenOut],
    )
    async def logout(
        self,
        response: Response,
    ) -> BaseOutDto[str]:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("csrf_token")
        return self.success("Logged out")

    def set_token_expiry(self, token_out):
        access_token = token_out.access_token
        claims = jwt.get_unverified_claims(access_token)
        token_out.expires_in = claims["exp"] - int(datetime.now(timezone.utc).timestamp())


    async def set_auth_cookies(self, response: Response, token_out) -> None:
        """
        Sets access + refresh tokens as cookies.
        Uses ONLY Max-Age to avoid proxy/header merging issues with Expires.
        """

        now_ts = int(datetime.now(timezone.utc).timestamp())

        # Decode tokens
        access_claims = jwt.get_unverified_claims(token_out.access_token)
        access_exp = access_claims["exp"]
        access_max_age = max(access_exp - now_ts, 1)

        secure_flag = settings.APP_ENV == "prod"

        # ✅ Access token cookie
        response.headers.append(
            "Set-Cookie",
            (
                f"access_token={token_out.access_token}; "
                f"Path=/; "
                f"HttpOnly; "
                f"SameSite=Lax; "
                f"Max-Age={access_max_age}"
                f"{'; Secure' if secure_flag else ''}"
            ),
        )
        
        refresh_claims = jwt.get_unverified_claims(token_out.refresh_token)
        refresh_exp = refresh_claims["exp"]
        refresh_max_age = max(refresh_exp - now_ts, 1)

        response.headers.append(
            "Set-Cookie",
            (
                f"refresh_token={token_out.refresh_token}; "
                f"Path=/; "
                f"HttpOnly; "
                f"SameSite=Lax; "
                f"Max-Age={refresh_max_age}"
                f"{'; Secure' if secure_flag else ''}"
            ),
        )

        csrf_token = generate_csrf_token()

        response.headers.append(
            "Set-Cookie",
            (
                f"csrf_token={csrf_token}; "
                f"Path=/; "
                f"SameSite=Lax; "
                f"Max-Age={access_max_age}"
                # ❗ NOT HttpOnly (frontend must read it)
                f"{'; Secure' if secure_flag else ''}"
            ),
        )

    def clear_tokens_from_response(self, token_out):
        token_out.access_token = ""
        token_out.refresh_token = ""
        return token_out
