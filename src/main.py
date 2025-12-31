from collections.abc import AsyncGenerator

from fastapi import FastAPI

from src.app import init_app
from src.config import credentials
from src.database.database import DatabaseManager
from src.jobs.jobs import run_jobs

# CAREFUL: If set true, this will destroy the current database
DROP_CURRENT_DB = False

# Create Database
database_manager = DatabaseManager()
database_manager.init(credentials.database.url())


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Test connection
    async with database_manager.connect() as connection:
        if DROP_CURRENT_DB:
            await database_manager.drop_all(connection)
            await database_manager.create_all(connection)
    assert database_manager.url is not None
    with run_jobs(database_manager.url):
        yield
    await database_manager.close()


# Init the App
app = init_app(database_manager, lifespan=lifespan)
