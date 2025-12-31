import datetime as dt
import json
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from sqlalchemy import select

from src.config import credentials
from src.constants import AUTH_REDIRECT_PATH
from src.database.database import DatabaseManager, get_database_manager
from src.database.models import (
    DBAccount,
)
from src.logger import get_logger
from src.utils.send_email import send_signup_email

logger = get_logger()

JWT_ALGORITHM = "HS256"
MAX_EMAIL_UTF8_LENGTH = 512


class JWTAccountData(BaseModel):
    account_id: UUID


class JWTDecodeError(Exception):
    pass


def decode_jwt_token[T: BaseModel](jwt_token: str, model_type: type[T]) -> T:
    try:
        payload = jwt.decode(
            jwt_token,
            credentials.backend.backend_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
        )
    except JWTError as e:
        raise JWTDecodeError() from e
    try:
        token_info = model_type.model_validate_json(payload.get("sub", ""))
    except ValidationError as e:
        raise JWTDecodeError() from e
    return token_info


def encode_jwt_token(
    token_data: BaseModel,
    expires_delta: dt.timedelta | None = None,
) -> str:
    if expires_delta is None:
        expires_delta = dt.timedelta(days=99999)

    now = dt.datetime.now(dt.UTC)
    payload = {
        "sub": token_data.model_dump_json(),
        "exp": now + expires_delta,
        "iat": now,
    }
    encoded_jwt_token = jwt.encode(
        payload,
        credentials.backend.backend_secret.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )
    return encoded_jwt_token


class AccountLoginInfo(BaseModel):
    account_id: UUID
    first_name: str | None
    last_name: str | None
    email: str | None
    phone: str | None


async def guard_login_optional(
    http_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> AccountLoginInfo | None:
    token = http_credentials.credentials
    try:
        account_info = decode_jwt_token(token, JWTAccountData)
        account_id = account_info.account_id
    except ValueError:
        return None
    async with database_manager.session() as session:
        db_result = await session.execute(
            select(DBAccount).where(DBAccount.id == account_id)
        )
        result = db_result.scalar_one_or_none()
        if result is None:
            return None
        login_info = AccountLoginInfo(
            account_id=account_id,
            first_name=result.first_name,
            last_name=result.last_name,
            email=result.email,
            phone=result.phone,
        )
        return login_info


async def guard_login(
    http_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    database_manager: DatabaseManager = Depends(get_database_manager),
    account_optional: AccountLoginInfo | None = Depends(guard_login_optional),
) -> AccountLoginInfo:
    if account_optional is None:
        raise HTTPException(status_code=401, detail="Invalid Auth Token") from None
    return account_optional


async def admin_guard_login(
    http_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> None:
    token = http_credentials.credentials
    if token != credentials.backend.admin_api_key.get_secret_value():
        raise HTTPException(status_code=401, detail="Invalid Auth Token")


async def login_redirect(
    database_manager: DatabaseManager,
    *,
    first_name: str | None,
    last_name: str | None,
    email: str,
    background_tasks: BackgroundTasks,
    query_params: str = "",
) -> Response:
    # Validate email length before proceeding
    email_bytes_length = len(email.encode(encoding="utf-8"))
    if email_bytes_length > MAX_EMAIL_UTF8_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Email address is too long ({email_bytes_length} UTF-8 bytes). Maximum allowed length is {MAX_EMAIL_UTF8_LENGTH} UTF-8 bytes.",
        )

    # Find/Create a account with provided email
    async with database_manager.session() as session:
        db_result = await session.execute(
            select(DBAccount.id).where(
                DBAccount.email == email,
            )
        )
        account_id = db_result.scalar_one_or_none()

        # If no such account exists, create one
        if account_id is None:
            # Create an account
            account_id = uuid4()
            account = DBAccount(
                id=account_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=None,
            )
            session.add(account)

            background_tasks.add_task(
                send_signup_email,
                user_email=email,
                name=f"{first_name} {last_name}".strip(),
            )

    jwt_token_data = JWTAccountData(account_id=account_id)
    jwt_token = encode_jwt_token(jwt_token_data)
    return HTMLResponse(
        content=f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login</title>
    <script>
      localStorage.setItem("jwt_token", {json.dumps(jwt_token)});
      window.location.href = "{AUTH_REDIRECT_PATH}{query_params}";
    </script>
  </head>
  <body>
    <h2>Logging In...</h2>
  </body>
</html>
""",
    )
