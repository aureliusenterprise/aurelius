"""The FastAPI application factory."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from aurelius_atlas_store_es.client import create_client
from aurelius_atlas_store_es.settings import ElasticsearchSettings
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI

from aurelius_atlas_server.errors import AtlasError, atlas_error_handler
from aurelius_atlas_server.routes.admin import ADMIN, ATLAS_VERSION
from aurelius_atlas_server.settings import ServerSettings

API_PREFIX = "/api/atlas"


def create_app(
    settings: ServerSettings,
    client_factory: Callable[[ElasticsearchSettings], AsyncElasticsearch] = create_client,
) -> FastAPI:
    """Create the server application.

    The Elasticsearch client is opened when the application starts and closed when it stops.

    Args:
        settings: Server settings.
        client_factory: Creates the store client (replaceable in tests).

    Returns:
        The application.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.store = client_factory(settings.elasticsearch)
        try:
            yield
        finally:
            await app.state.store.close()

    app = FastAPI(
        title="Aurelius Atlas",
        version=ATLAS_VERSION,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/atlas/openapi.json",
    )
    app.state.settings = settings
    app.add_exception_handler(AtlasError, atlas_error_handler)
    app.include_router(ADMIN, prefix=f"{API_PREFIX}/admin", tags=["Admin"])
    return app
