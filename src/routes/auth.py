import base64
import datetime as dt
import secrets
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ValidationError

from src.config import credentials
from src.database.database import DatabaseManager, get_database_manager
from src.logger import get_logger
from src.routes.helpers.auth import (
    JWTDecodeError,
    decode_jwt_token,
    encode_jwt_token,
    login_redirect,
)
from src.routes.helpers.http_utils import error_redirect
from src.routes.helpers.oauth2 import (
    OAuth2Error,
    OAuthClientConfig,
    oauth2_authorize_access_token,
    oauth2_authorize_redirect,
)

logger = get_logger()


class OAuthState(BaseModel):
    csrf_token: str


# ============================
# Endpoints
# ============================

router = APIRouter(prefix="/auth", tags=["Auth"])

if credentials.google_auth is None:
    oauth_google = None
else:
    oauth_google = OAuthClientConfig(
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=credentials.google_auth.google_client_id.get_secret_value(),
        client_secret=credentials.google_auth.google_client_secret.get_secret_value(),
        scope="openid email profile",
    )


@router.get("/{provider}/login")
async def auth_login(
    request: Request,
    provider: Literal["google"],
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> RedirectResponse:
    # Load OAuth config based on provider
    match provider:
        case "google":
            oauth_client = oauth_google
    if oauth_client is None:
        return error_redirect(f"{provider} login is disabled, please contact support.")

    # Prepare OAuth state
    csrf_token = secrets.token_urlsafe(32)
    state = OAuthState(
        csrf_token=csrf_token,
    )
    state_string = base64.urlsafe_b64encode(
        encode_jwt_token(state, dt.timedelta(minutes=5)).encode()
    ).decode()

    # Redirect to OAuth, setting cookie in the process
    response = RedirectResponse(
        url=await oauth2_authorize_redirect(
            oauth_client,
            str(request.url_for(auth_auth.__name__, provider=provider)),
            state=state_string,
            # https://stackoverflow.com/questions/47150564/how-to-log-user-out-of-an-app-that-uses-google-oauth2-sign-in
            prompt="consent" if provider == "google" else "login",
        ),
        status_code=302,
    )
    response.set_cookie(
        key="oauth_csrf_token",
        value=csrf_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=300,
    )
    return response


@router.get("/{provider}/auth")
async def auth_auth(
    request: Request,
    provider: Literal["google"],
    background_tasks: BackgroundTasks,
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> Response:
    # Decode state
    state_string = request.query_params.get("state")
    if state_string is None:
        return error_redirect("Failed to Login")
    try:
        state = decode_jwt_token(
            base64.urlsafe_b64decode(state_string).decode(),
            OAuthState,
        )
    except (ValidationError, JWTDecodeError):
        return error_redirect("Failed to Login")
    cookie_csrf_token = request.cookies.get("oauth_csrf_token")
    if cookie_csrf_token != state.csrf_token:
        return error_redirect("Invalid OAuth state")

    # Load OAuth config based on provider
    match provider:
        case "google":
            oauth_client = oauth_google

    if oauth_client is None:
        return error_redirect(f"{provider} login is disabled, please contact support.")

    # Authorize the access token
    try:
        token = await oauth2_authorize_access_token(
            oauth_client,
            request.query_params,
            str(request.url_for(auth_auth.__name__, provider=provider)),
        )
    except OAuth2Error as e:
        return error_redirect(str(e.error))
    user_info = token.userinfo
    if user_info.name is None or user_info.email is None:
        return error_redirect("Failed to Login")
    if user_info.email_verified is not True:
        return error_redirect("Your email has not been verified yet")

    # Redirect
    return await login_redirect(
        database_manager,
        first_name=user_info.given_name,
        last_name=user_info.family_name,
        email=user_info.email,
        background_tasks=background_tasks,
        query_params="",
    )
