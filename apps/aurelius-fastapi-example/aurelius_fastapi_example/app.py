import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import logfire
from fastapi import FastAPI
from opentelemetry.sdk._logs import LoggingHandler
from sqlmodel import SQLModel

from aurelius_fastapi_example.globals import LOGGER, METADATA, NAME
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import database, get_broadcaster
from aurelius_fastapi_example.routes import ENTITIES, HEALTH


def _ensure_logfire_handler(logger: logging.Logger) -> None:
    """Ensure a logger has exactly one OTEL logging handler attached."""
    logger_provider = logfire.DEFAULT_LOGFIRE_INSTANCE.config.get_logger_provider()
    logger.handlers = [handler for handler in logger.handlers if not isinstance(handler, LoggingHandler)]
    logger.addHandler(LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider))


def setup_logging(level: str) -> None:
    """Configure application and uvicorn loggers for OTEL log export."""
    log_level = level.upper()

    for logger_name in (NAME, "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        _ensure_logfire_handler(logger)
        logger.setLevel(log_level)
        logger.propagate = False


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
        LOGGER.debug("Application settings: %s", settings)

        if app.debug:
            LOGGER.warning("🚨 Running in development mode. Not for production use! 🚨")

        if settings.auto_create_schema:
            LOGGER.info("Auto-creating database schema...")
            db_engine = database(settings=settings)
            SQLModel.metadata.create_all(db_engine)
            LOGGER.info("Database schema created successfully")

        with get_broadcaster(settings=settings):
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
    app = FastAPI(
        lifespan=make_lifespan(settings),
        debug=settings.is_development,
        description=METADATA.get("Summary", ""),
        title=NAME,
        version=f"v{METADATA.get('Version', '')}",
    )

    setup_routes(app)

    logfire.configure(
        send_to_logfire=False,
        service_name=app.title,
        service_version=app.version,
        min_level=settings.log_level,
        console=logfire.ConsoleOptions(min_log_level=settings.log_level),
    )

    logfire.instrument_fastapi(app)
    logfire.instrument_httpx()
    logfire.instrument_psycopg()

    setup_logging(settings.log_level)

    return app


def main(settings: Settings) -> FastAPI:
    """
    Main entry point for the FastAPI application.

    Returns:
        FastAPI: The FastAPI application instance.
    """
    return create_app(settings)
