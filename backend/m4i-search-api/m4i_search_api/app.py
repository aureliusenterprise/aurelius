import logging

from flask import Flask
from m4i_backend_core.shared import register as register_shared

from m4i_search_api.providers import (
    AppSearchKeyProvider,
    AuthProvider,
    KeycloakAuthProvider,
    KeyProvider,
)

from .globals import LOGGER, METADATA
from .routes import create_proxy_blueprint, health_bp
from .settings import Settings


def setup_logging(log_level: str) -> None:
    """Configure logging for the application.

    When running under gunicorn, gunicorn manages the root logger, so
    logging.basicConfig() is a no-op.  We explicitly configure our
    application logger with its own handler so that it always emits
    regardless of gunicorn's root logger configuration.
    """
    LOGGER.setLevel(log_level.upper())

    if not LOGGER.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level.upper())
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)


def setup_routes(
    app: Flask,
    auth_provider: AuthProvider,
    key_provider: KeyProvider,
    settings: Settings,
) -> None:
    """Register routes with the Flask application."""
    app.register_blueprint(health_bp)

    app.register_blueprint(
        create_proxy_blueprint(
            auth_provider=auth_provider,
            key_provider=key_provider,
            settings=settings,
        )
    )


def create_app(
    auth_provider: AuthProvider,
    key_provider: KeyProvider,
    settings: Settings,
) -> Flask:
    """
    Factory function to create and configure the Flask application.

    Args:
        auth_provider: Provider for JWT validation. Defaults to KeycloakAuthProvider.
        key_provider: Provider for the App Search API key. Defaults to AppSearchKeyProvider.
        settings: Application settings. Defaults to loading from environment.
    """
    app = Flask(__name__)

    setup_logging(settings.log_level)
    register_shared(app)
    setup_routes(app, auth_provider, key_provider, settings)

    version = f"v{METADATA.get('Version', 'unknown')}"

    LOGGER.info("Started m4i-search-api version %s", version)
    LOGGER.debug("Settings: %s", settings)

    if not settings.ca_cert_path:
        LOGGER.warning(
            "No CA certificate path provided; SSL verification is disabled. This is not recommended for production environments."
        )

    return app


def main() -> Flask:
    """Main entry point for the Flask application."""
    settings = Settings()  # type: ignore[settings are loaded from the environment]

    auth_provider = KeycloakAuthProvider()
    key_provider = AppSearchKeyProvider(settings)

    return create_app(
        auth_provider=auth_provider,
        key_provider=key_provider,
        settings=settings,
    )
