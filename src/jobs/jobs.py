import asyncio
from collections.abc import Generator
from contextlib import contextmanager
from multiprocessing import Process

from apscheduler.schedulers.asyncio import (  # pyright: ignore[reportMissingTypeStubs]
    AsyncIOScheduler,
)
from sqlalchemy import URL

from src.database.database import DatabaseManager
from src.logger import get_logger

logger = get_logger()


async def start_jobs(database_manager: DatabaseManager) -> None:
    while True:
        await asyncio.sleep(100)  # Do nothing


# Runs all jobs; this function will be wrapped in a Process
def runner(database_url: URL) -> None:
    database_manager = DatabaseManager()
    database_manager.init(database_url)
    asyncio.run(start_jobs(database_manager))


# ===
# This file contains code for creating a separate background jobs process.
# The purpose of this jobs process is to keep "runner" running always.
# ===

jobs_process: Process | None = None


# Creates and starts the job runner process, if it's not already running
def create_runner_process(
    database_url: URL, expecting_runner_exists: bool = False
) -> None:
    """Create and start a new job process."""
    if not expecting_runner_exists:
        logger.info("Creating and starting a new job process...")
    global jobs_process
    if jobs_process is None or not jobs_process.is_alive():
        if expecting_runner_exists:
            logger.error("Job found dead, restarting it.")
        jobs_process = Process(target=runner, args=(database_url,))
        jobs_process.daemon = True
        jobs_process.start()
        logger.info(f"Job started with PID {jobs_process.pid}")
    elif not expecting_runner_exists:
        logger.error("Job is already running")


def start_jobs_scheduler(database_url: URL) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    create_runner_process(database_url)
    scheduler.add_job(create_runner_process, "cron", [database_url, True], minute="*/1")  # pyright: ignore[reportUnknownMemberType]
    scheduler.start()
    return scheduler


def stop_jobs_scheduler(scheduler: AsyncIOScheduler) -> None:
    global jobs_process
    logger.info("Shutting down jobs...")
    scheduler.pause()
    if jobs_process is not None and jobs_process.is_alive():
        jobs_process.terminate()  # Send SIGTERM to the process
        jobs_process.join(1)  # Wait for the process to exit gracefully
        if jobs_process.is_alive():
            logger.error("Failed to join job, killing it")
            jobs_process.kill()
            jobs_process.join(0.5)
            if jobs_process.is_alive():
                logger.error("Still failed to join job. Job will not be joined.")
        jobs_process = None
    else:
        logger.error("No job is currently running")
    scheduler.shutdown()
    logger.info("Jobs shut down.")


@contextmanager
def run_jobs(database_url: URL) -> Generator[None, None, None]:
    """A contextmanager arounds the jobs runner. For use by a FastAPI lifetime."""
    scheduler = start_jobs_scheduler(database_url)
    try:
        yield
    finally:
        stop_jobs_scheduler(scheduler)
