from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from aurelius_sdk.logger import setup_logger
from fastapi import FastAPI

from aurelius_fastapi_example.globals import LOGGER, METADATA, NAME
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import database, get_broadcaster
from aurelius_fastapi_example.routes import ENTITIES, HEALTH


def make_lifespan(settings: Settings) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    """Return a lifespan context manager configured with the given settings."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        """
        Manages the startup and shutdown of the FastAPI application.

        Starts the shared PostgreSQL listener on startup and shuts it down on exit.

        Args:
            app: The FastAPI application instance.

        Yields:
            None: When the application is running.
        """
        LOGGER.info("Starting %s (%s) 🚀", app.title, app.version)

        if app.debug:
            LOGGER.warning("🚨 Running in development mode. Not for production use! 🚨")

        with get_broadcaster(db_engine=database(settings=settings), settings=settings):
            yield

        LOGGER.info("Stopping %s. Goodbye 👋", app.title)

    return lifespan


def setup_routes(app: FastAPI) -> None:
    """Include API routes in the FastAPI application."""
    app.include_router(
        ENTITIES,
        prefix="/entities",
        tags=["Entities"],
    )

    app.include_router(
        HEALTH,
        prefix="/health",
        tags=["Health"],
        include_in_schema=False,
    )


def create_app(settings: Settings) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(lifespan=make_lifespan(settings))

    app.debug = settings.is_development
    app.description = METADATA.get("Summary", "")
    app.title = NAME
    app.version = f"v{METADATA.get('Version', '')}"

    setup_routes(app)

    LOGGER.debug("Application setup complete. Settings: %s", settings)

    return app


def main(settings: Settings) -> FastAPI:
    """
    Main entry point for the FastAPI application.

    Sets up logging for the app and overrides the default log format for all log handlers.

    Returns:
        FastAPI: The FastAPI application instance.
    """
    setup_logger(level=settings.log_level)

    return create_app(settings)
