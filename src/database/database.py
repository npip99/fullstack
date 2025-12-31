import contextlib
from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.database.models import Base

SHOW_DATABASE_LOGS = False


class DatabaseManager:
    engine: AsyncEngine | None = None
    sessionmaker: async_sessionmaker[AsyncSession] | None
    url: URL | None

    def __init__(self) -> None:
        self.engine = None
        self.sessionmaker = None
        self.url = None

    def init(self, url: URL) -> None:
        self.url = url
        # CAREFUL: Required for naive datetimes to be in UTC
        connect_args: dict[str, str | dict[str, str]] = {}
        if "asyncpg" in url.get_driver_name():
            connect_args = {
                "server_settings": {
                    "timezone": "utc",
                    "lock_timeout": "5s",
                },
            }
        elif "psycopg" in url.get_driver_name():
            connect_args = {
                "options": "-c timezone=utc -c lock_timeout=5s",
            }
        else:
            raise ValueError(f"Invalid driver name: {url.get_driver_name()}")
        # Create the engine
        self.engine = create_async_engine(
            url,
            pool_size=30,
            max_overflow=0,
            pool_pre_ping=True,
            echo=SHOW_DATABASE_LOGS,
            connect_args=connect_args,
        )
        self.sessionmaker = async_sessionmaker(
            self.engine,
            autocommit=False,
            autobegin=False,
        )

    async def close(self) -> None:
        if self.engine is None:
            raise Exception("DatabaseManager is not initialized")
        await self.engine.dispose()
        self.engine = None
        self.sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise Exception("DatabaseManager is not initialized")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self, auto_begin: bool = True) -> AsyncIterator[AsyncSession]:
        if self.sessionmaker is None:
            raise Exception("DatabaseManager is not initialized")

        async with self.sessionmaker() as session:
            assert isinstance(session, AsyncSession)
            if auto_begin:
                async with session.begin():
                    yield session
            else:
                yield session

    # Used for testing
    async def create_all(self, connection: AsyncConnection) -> None:
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection) -> None:
        await connection.run_sync(Base.metadata.drop_all)


async def get_database_manager(request: Request) -> DatabaseManager:
    database_manager = request.app.state.database_manager
    assert isinstance(database_manager, DatabaseManager)
    return database_manager
