from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aurelius_sdk.logger import setup_logger
from fastapi import FastAPI

from aurelius_fastapi_example.globals import LOGGER, METADATA, NAME
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.routes import ENTITIES, HEALTH


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Manages the startup and shutdown of the FastAPI application.

    Logs the start and stop of the application.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: When the application is running.
    """
    LOGGER.info("Starting %s (%s) 🚀", app.title, app.version)

    if app.debug:
        LOGGER.warning("🚨 Running in development mode. Not for production use! 🚨")

    yield

    LOGGER.info("Stopping %s. Goodbye 👋", app.title)


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
    app = FastAPI(lifespan=lifespan)

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
