import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.logger import get_logger
from src.routes.account import GetAccountRequest, GetAccountResponse, get_account
from tests.conftest import ACCOUNT_ID

logger = get_logger()

DEBUG_FILES = False


@pytest.mark.asyncio
async def test_get_account(app: FastAPI, client: AsyncClient) -> None:
    raw_response = await client.post(
        url=app.url_path_for(get_account.__name__),
        json=GetAccountRequest(
            account_id=ACCOUNT_ID,
        ).model_dump(mode="json"),
    )
    assert raw_response.status_code == 200
    response = GetAccountResponse.model_validate(raw_response.json())
    assert response.account.id == ACCOUNT_ID
