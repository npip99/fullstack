from collections.abc import Mapping
from typing import final
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, ValidationError

from src.utils import get_client

# ============================
# Exceptions
# ============================


@final
class OAuth2Error(Exception):
    """OAuth 2.0 error exception."""

    def __init__(self, error: str, description: str | None = None) -> None:
        self.error = error
        self.description = description
        message = f"{error}"
        if description:
            message += f": {description}"
        super().__init__(message)


# ============================
# Types
# ============================


class OAuthClientConfig(BaseModel):
    """OAuth 2.0 / OpenID Connect client configuration."""

    server_metadata_url: str
    client_id: str
    client_secret: str
    scope: str


class ProviderMetadata(BaseModel):
    """OpenID Provider Metadata (Discovery Document)."""

    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    issuer: str | None = None
    jwks_uri: str | None = None


class AccessTokenResponse(BaseModel):
    """OAuth 2.0 Access Token Response (RFC 6749 Section 5.1)."""

    access_token: str
    token_type: str
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None
    id_token: str | None = None  # OpenID Connect extension


class UserInfo(BaseModel):
    """OpenID Connect UserInfo claims."""

    sub: str
    email: str | None = None
    email_verified: bool | None = None
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None


# ============================
# Functions
# ============================


async def get_provider_metadata(server_metadata_url: str) -> ProviderMetadata:
    """Fetch OpenID Provider Metadata from discovery endpoint.

    Args:
        server_metadata_url: URL to .well-known/openid-configuration endpoint

    Returns:
        Provider metadata containing authorization, token, and userinfo endpoints

    Raises:
        OAuth2Error: If metadata fetch fails
    """
    try:
        response = await get_client().get(server_metadata_url)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise OAuth2Error("metadata_fetch_failed", str(e)) from e

    try:
        return ProviderMetadata.model_validate(response.json())
    except ValidationError as e:
        raise OAuth2Error("metadata_parse_failed", str(e)) from e


async def exchange_code_for_token(
    token_endpoint: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str,
) -> AccessTokenResponse:
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        response = await get_client().post(
            token_endpoint,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise OAuth2Error("token_exchange_failed", str(e)) from e

    try:
        return AccessTokenResponse.model_validate(response.json())
    except ValidationError as e:
        raise OAuth2Error("token_parse_failed", str(e)) from e


async def fetch_userinfo(userinfo_endpoint: str, access_token: str) -> UserInfo:
    try:
        response = await get_client().get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise OAuth2Error("userinfo_fetch_failed", str(e)) from e

    try:
        return UserInfo.model_validate(response.json())
    except ValidationError as e:
        raise OAuth2Error("userinfo_parse_failed", str(e)) from e


# ============================
# High-level API
# ============================


async def oauth2_authorize_redirect(
    config: OAuthClientConfig,
    redirect_uri: str,
    state: str,
    prompt: str,
) -> str:
    metadata = await get_provider_metadata(config.server_metadata_url)
    params = {
        "client_id": config.client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": config.scope,
        "state": state,
        "prompt": prompt,
        "access_type": "offline",
    }
    return f"{metadata.authorization_endpoint}?{urlencode(params)}"


class AuthorizationResult(BaseModel):
    access_token_response: AccessTokenResponse
    userinfo: UserInfo


async def oauth2_authorize_access_token(
    config: OAuthClientConfig,
    query_params: Mapping[str, str],
    redirect_uri: str,
) -> AuthorizationResult:
    code = query_params.get("code")
    if not isinstance(code, str):
        raise OAuth2Error(
            "code_missing",
            "OAuth 2.0 code is missing from query parameters",
        )
    metadata = await get_provider_metadata(config.server_metadata_url)

    access_token_response = await exchange_code_for_token(
        token_endpoint=metadata.token_endpoint,
        code=code,
        redirect_uri=redirect_uri,
        client_id=config.client_id,
        client_secret=config.client_secret,
    )

    user_info = await fetch_userinfo(
        userinfo_endpoint=metadata.userinfo_endpoint,
        access_token=access_token_response.access_token,
    )

    return AuthorizationResult(
        access_token_response=access_token_response,
        userinfo=user_info,
    )
