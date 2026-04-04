# HTTP client timeout configuration (in seconds)
from collections.abc import Generator

import httpx
from fastapi import HTTPException

from aurelius_fastapi_example.globals import LOGGER

HTTP_TIMEOUT = 5.0


def http_client() -> Generator[httpx.Client]:
    """Return an HTTP client for making requests to external services."""
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        try:
            yield client
        except httpx.HTTPError as e:
            LOGGER.error("HTTP error occurred: %s", e)
            raise HTTPException(status_code=503) from e
