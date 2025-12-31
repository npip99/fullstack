import asyncio
from pathlib import Path

import httpx

ROOT = f"{Path(__file__).resolve().parent.parent.parent}"


def unwrap_or[T](inp: T | None, default: T) -> T:
    if inp is None:
        return default
    return inp


client_connections: dict[asyncio.AbstractEventLoop, httpx.AsyncClient] = {}


def get_client() -> httpx.AsyncClient:
    event_loop = asyncio.get_event_loop()
    if event_loop not in client_connections:
        client_connections[event_loop] = httpx.AsyncClient()
    return client_connections[event_loop]
