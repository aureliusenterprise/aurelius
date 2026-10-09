"""``/api/atlas/admin``: version, status, liveness and readiness (Atlas ``AdminResource``)."""

import logging
from typing import Annotated

from aurelius_atlas_store_es.client import StoreUnavailableError, check_health
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from aurelius_atlas_server.errors import INTERNAL_ERROR, AtlasError
from aurelius_atlas_server.settings import ServerSettings

ADMIN = APIRouter()
LOGGER = logging.getLogger(__name__)

#: The Apache Atlas release whose contract this server implements (DD-001, ADR 046).
ATLAS_NAME = "apache-atlas"
ATLAS_VERSION = "2.4.0"
ATLAS_DESCRIPTION = "Metadata Management and Data Governance Platform over Hadoop"
#: This server has no high-availability passive mode, so it is always ACTIVE (ADM-03).
SERVICE_STATE = "ACTIVE"


def get_settings(request: Request) -> ServerSettings:
    """Return the settings the app was created with.

    Args:
        request: The current request.

    Returns:
        The settings.
    """
    return request.app.state.settings


def get_store(request: Request) -> AsyncElasticsearch:
    """Return the Elasticsearch client opened at start-up.

    Args:
        request: The current request.

    Returns:
        The client.
    """
    return request.app.state.store


Settings = Annotated[ServerSettings, Depends(get_settings)]
Store = Annotated[AsyncElasticsearch, Depends(get_store)]


@ADMIN.get("/version")
async def version(settings: Settings) -> dict[str, str]:
    """Return the implemented Atlas version and this build's revision (ADM-01, DV-03).

    Args:
        settings: Server settings (for the build revision).

    Returns:
        ``Version``, ``Revision``, ``Name`` and ``Description`` as Atlas reports them.
    """
    return {
        "Version": ATLAS_VERSION,
        "Revision": settings.build_revision,
        "Name": ATLAS_NAME,
        "Description": ATLAS_DESCRIPTION,
    }


@ADMIN.get("/status")
async def status() -> dict[str, str]:
    """Return the service state (ADM-03).

    Returns:
        ``{"Status": "ACTIVE"}``.
    """
    return {"Status": SERVICE_STATE}


@ADMIN.get("/liveness", response_class=PlainTextResponse)
async def liveness() -> str:
    """Answer while the process serves requests (ADM-04).

    Returns:
        Atlas's liveness text.
    """
    return "Service is live"


@ADMIN.get("/readiness", response_class=PlainTextResponse)
async def readiness(store: Store) -> str:
    """Answer 200 only when the store can serve requests (ADM-05).

    Args:
        store: The Elasticsearch client.

    Returns:
        Atlas's readiness text.

    Raises:
        AtlasError: ``ATLAS-500-00-001`` when the store is unreachable or red.
    """
    try:
        health = await check_health(store, wait_timeout="1s")
        ready = health.is_available
        reason = f"store status {health.status}"
    except StoreUnavailableError as error:
        ready, reason = False, str(error)
    if not ready:
        # Atlas answers without an errorCause here; the reason goes to the log only.
        LOGGER.error("Service is not ready to accept client requests: %s", reason)
        raise AtlasError(INTERNAL_ERROR, "Service not ready to accept client requests")
    return "Service is ready to accept requests"
