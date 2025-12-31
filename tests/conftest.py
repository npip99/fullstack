from collections.abc import AsyncGenerator
from contextlib import ExitStack
from typing import Any, cast
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest_postgresql import factories
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy.engine import URL

from src.app import init_app
from src.config import credentials
from src.database.database import DatabaseManager
from src.database.models import DBAccount
from src.jobs.jobs import run_jobs
from src.logger import get_logger
from src.routes.helpers.auth import JWTAccountData, encode_jwt_token

logger = get_logger()

# Globals must be constant, e.g. uuid4() would be recalculated on each test run
ADMIN_TOKEN = credentials.backend.admin_api_key.get_secret_value()
ACCOUNT_ID = UUID("dd8678fa-44fe-455d-9b69-8cf9ae556ebc")
ACCOUNT_TOKEN = encode_jwt_token(JWTAccountData(account_id=ACCOUNT_ID))

test_db = factories.postgresql_proc(port=None, dbname="test_db")  # pyright: ignore[reportUnknownMemberType]


@pytest.fixture(scope="session")
async def initialize_database_manager(
    test_db: PostgreSQLExecutor,
) -> AsyncGenerator[DatabaseManager, None]:
    database_manager = DatabaseManager()
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    # Incorrect type annotation for test_db.password
    pg_password = cast(str | None, test_db.password)
    assert pg_password is None

    with DatabaseJanitor(
        user=pg_user,
        host=pg_host,
        port=pg_port,
        dbname=pg_db,
        version=test_db.version,
        password=pg_password,
    ):
        database_url = URL.create(
            drivername="postgresql+psycopg",
            username=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port,
            database=pg_db,
        )
        database_manager.init(database_url)
        yield database_manager
        await database_manager.close()


@pytest.fixture
async def app(
    initialize_database_manager: DatabaseManager,
) -> AsyncGenerator[FastAPI, None]:
    # Reset the database
    async with initialize_database_manager.connect() as connection:
        await initialize_database_manager.drop_all(connection)
        await initialize_database_manager.create_all(connection)

    async with initialize_database_manager.session() as session:
        session.add(
            DBAccount(
                id=ACCOUNT_ID,
                first_name="Testing",
                last_name="Accounts",
                email="testing@example.com",
                phone=None,
            )
        )

    with ExitStack():
        # Run background jobs,
        assert initialize_database_manager.url is not None
        with run_jobs(initialize_database_manager.url):
            yield init_app(initialize_database_manager)


@pytest.fixture
async def client(
    app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=cast(Any, app)),
        base_url="http://test",
        headers={
            "Authorization": f"Bearer {ACCOUNT_TOKEN}",
        },
    ) as client:
        yield client
