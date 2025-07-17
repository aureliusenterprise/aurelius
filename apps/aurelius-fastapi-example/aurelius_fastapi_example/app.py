from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aurelius_sdk.logger import setup_logger
from fastapi import FastAPI

from aurelius_fastapi_example.globals import LOGGER, METADATA, NAME, SETTINGS
from aurelius_fastapi_example.routes import ENTITIES


def main() -> FastAPI:
    """
    Main entry point for the FastAPI application.

    Sets up logging for the app and overrides the default log format for all log handlers.

    Returns:
        FastAPI: The FastAPI application instance.
    """
    setup_logger(level=SETTINGS.log_level)

    LOGGER.debug("Application setup complete. Settings: %s", SETTINGS)

    return app


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


# App setup
app = FastAPI(lifespan=lifespan)
app.debug = SETTINGS.is_development
app.description = METADATA.get("Summary", "")
app.title = NAME
app.version = f"v{METADATA.get('Version', '')}"


# Routes setup - Add your API routes here
app.include_router(
    ENTITIES,
    prefix="/entities",
    tags=["Entities"],
)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck() -> None:
    """
    Check the health of the API.

    Returns:
        None: A 200 OK response if the API is healthy.
    """
