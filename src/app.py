import pathlib
import sys
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.constants import ERROR_PATH
from src.database.database import DatabaseManager
from src.logger import get_logger
from src.routes.account import router as account_router
from src.routes.auth import router as auth_router

logger = get_logger()


def register_logging_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Generate a unique request ID and capture start time
        request_id = uuid4()
        start_time = time.time()

        request.state.request_id = request_id
        request.state.request_start_time = start_time
        response = None
        exc_info = None

        try:
            response = await call_next(request)
        except Exception:
            exc_info = sys.exc_info()
            response = JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                },
            )
        finally:
            assert response is not None
            process_time_ms = (time.time() - start_time) * 1000

            # Add request ID to response headers for logging/debugging
            response.headers["X-Request-ID"] = str(request_id)

            # Get organization ID from request state if available
            account_id = getattr(request.state, "account_id", None)
            if account_id is not None:
                assert isinstance(account_id, UUID)

            # Get IP info (Even through proxy)
            if request.client is None:
                ip_msg = "unknown"
            else:
                ip = request.client.host
                port = request.client.port
                if port == 0:
                    # Port is 0 in prod
                    ip_msg = f"{ip}"
                else:
                    ip_msg = f"{ip}:{port}"

            # Render the log message
            log_message = f'{ip_msg} req-{str(request_id)[:16]} account-{account_id} - "{request.method} {request.url.path}{request.url.query and "?" + str(request.url.query) or ""} HTTP/{request.scope.get("http_version", "1.1")}" {response.status_code} - {process_time_ms:.1f}ms'

            # Print the log
            if exc_info is not None:
                logger.error(log_message, exc_info=exc_info)
            else:
                logger.info(log_message)

        return response


def init_app(
    database_manager: DatabaseManager,
    *,
    lifespan: Callable[[FastAPI], AsyncGenerator[None, None]] | None = None,
) -> FastAPI:
    # Initialize the FastAPI app
    app = FastAPI(
        title="Fullstack API",
        description="This API provides access to the backend. Enjoy!",
        lifespan=asynccontextmanager(lifespan) if lifespan is not None else None,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.state.database_manager = database_manager

    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

    # Disable cache, except if ETag matches.
    @app.middleware("http")
    async def no_cache_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"

        # If request has an ETag, return 304 if nothing has changed.
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-None-Match
        if (
            "If-None-Match" in request.headers
            and "etag" in response.headers
            and request.headers["If-None-Match"] == response.headers["etag"]
        ):
            headers_to_preserve: dict[str, str] = {}
            for header in [
                "cache-control",
                "cache-location",
                "date",
                "etag",
                "expires",
                "vary",
            ]:
                if header in response.headers:
                    headers_to_preserve[header] = response.headers[header]
            return Response(status_code=304, headers=headers_to_preserve)

        return response

    frontend_build_dir = pathlib.Path(__file__).parent.parent / "frontend-build"
    assets_dir = frontend_build_dir / "assets"
    app.mount(
        "/assets",
        StaticFiles(directory=assets_dir),
        name="assets",
    )

    app.include_router(auth_router, prefix="/api")
    app.include_router(account_router, prefix="/api")

    @app.get("/api/{full_path:path}")
    async def api_get_missing() -> FileResponse:
        raise HTTPException(
            status_code=404,
            detail="API Endpoint Not Found. GET not allowed, only POST.",
        )

    @app.get("/bundle.js")
    async def bundle() -> FileResponse:
        return FileResponse(frontend_build_dir / "bundle.js")

    @app.get("/")
    async def root() -> FileResponse:
        return FileResponse(frontend_build_dir / "index.html")

    @app.get("/{path}")
    async def any_path() -> FileResponse:
        return FileResponse(frontend_build_dir / "index.html")

    @app.get("/{full_path:path}")
    async def any_full_path() -> RedirectResponse:
        return RedirectResponse(f"{ERROR_PATH}?error_message=Page%20Not%20Found")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc.detail),
            },
        )

    register_logging_middleware(app)

    return app
