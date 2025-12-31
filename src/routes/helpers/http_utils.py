from typing import Any
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from src.constants import ERROR_PATH
from src.logger import get_logger

logger = get_logger()

http_errors = {
    "400": {
        "description": "Bad Request",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
    "401": {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
    "403": {
        "description": "Forbidden",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
    "404": {
        "description": "Not Found",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
    "406": {
        "description": "Not Acceptable",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
    "409": {
        "description": "Conflict",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
    "410": {
        "description": "Gone",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
    "429": {
        "description": "Too Many Requests",
        "content": {
            "application/json": {"example": {"detail": "Description of Error"}}
        },
    },
}


def get_http_errors(error_list: list[str]) -> dict[str | int, dict[str, Any]]:
    filtered_http_errors: dict[str | int, dict[str, Any]] = {}
    for error in error_list:
        if error in http_errors:
            filtered_http_errors[error] = http_errors[error]
        else:
            raise KeyError(f"HTTP Status Code {error} does not exist in http_errors")
    return filtered_http_errors


class EmptyRequest(BaseModel):
    pass


class GenericMessageResponse(BaseModel):
    message: str = Field(..., description="Description of the result")


def error_redirect(error: str) -> RedirectResponse:
    logger.warning(f"User got an Error: {error}")
    query_params = {"error_message": error[:300]}
    encoded_query_params = urlencode(query_params)
    return RedirectResponse(f"{ERROR_PATH}?{encoded_query_params}")
