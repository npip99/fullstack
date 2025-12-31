from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from src.database.database import DatabaseManager, get_database_manager
from src.database.models import DBAccount
from src.routes.helpers.auth import (
    AccountLoginInfo,
    guard_login_optional,
)
from src.routes.helpers.http_utils import (
    get_http_errors,
)

# ============================
# Models
# ============================


class APIAccount(BaseModel):
    id: UUID
    first_name: str | None
    last_name: str | None
    email: str | None
    phone: str | None


# ============================
# Endpoints
# ============================

router = APIRouter(prefix="/accounts", tags=["Accounts"])


class GetAccountRequest(BaseModel):
    account_id: UUID | None = Field(
        None,
        description="The Account ID to request information about. If `null`, will request the currently logged-in user (If `null`, status code `401` will be returned if no user is logged in).",
    )


class GetAccountResponse(BaseModel):
    account: APIAccount = Field(..., description="The currently logged in Account.")


@router.post(
    "/get-account", response_model=GetAccountResponse, responses=get_http_errors([])
)
async def get_account(
    request: GetAccountRequest,
    database_manager: DatabaseManager = Depends(get_database_manager),
    login_info: AccountLoginInfo | None = Depends(guard_login_optional),
) -> GetAccountResponse:
    """
    Gets the requested account's information
    """
    request_account_id = request.account_id
    if request_account_id is None:
        if login_info is None:
            raise HTTPException(status_code=401, detail="Invalid Auth Token") from None
        request_account_id = login_info.account_id

    # Fetch account's associated organizations
    async with database_manager.session() as session:
        # Query to get organizations and permissions associated with the account
        db_result = await session.execute(
            select(DBAccount).where(DBAccount.id == request_account_id)
        )
        account = db_result.scalar_one_or_none()
        if account is None:
            raise HTTPException(status_code=404, detail="Account Not Found")

        return GetAccountResponse(
            account=APIAccount(
                id=account.id,
                first_name=account.first_name,
                last_name=account.last_name,
                email=account.email,
                phone=account.phone,
            ),
        )
