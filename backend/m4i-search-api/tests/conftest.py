from collections.abc import Callable
from functools import wraps
from typing import Any
from unittest.mock import Mock

import pytest
from flask import abort, request, Flask
from flask.testing import FlaskClient
from m4i_search_api.app import create_app
from m4i_search_api.providers import AuthProvider, KeyProvider
from m4i_search_api.settings import Settings
import secrets


class MockAuthProvider(AuthProvider):
    """Test auth provider that only checks for an Authorization header (no OIDC calls)."""

    def requires_auth(self) -> Callable:
        """Return a decorator that validates the Authorization header is present."""

        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated(*args: Any, **kwargs: Any) -> Any:
                auth = request.headers.get("Authorization", None)
                if not auth:
                    abort(401, description="Authorization header is expected.")

                parts = auth.split()
                if parts[0].lower() != "bearer" or len(parts) != 2:
                    abort(
                        401,
                        description='Authorization header must be "Bearer <token>".',
                    )

                token = parts[1]
                return f(access_token=token, *args, **kwargs)

            return decorated

        return decorator


class MockKeyProvider(KeyProvider):
    """Test key provider that returns a fixed key without making HTTP calls."""

    def __init__(self, key: str = "test-search-key") -> None:
        self._key = key

    def get_key(self) -> str:
        return self._key


@pytest.fixture(scope="session")
def auth_provider() -> MockAuthProvider:
    """Return a mock auth provider (no OIDC calls)."""
    return MockAuthProvider()


@pytest.fixture(scope="session")
def key_provider() -> MockKeyProvider:
    """Return a mock key provider."""
    return MockKeyProvider()


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Return test settings."""
    return Mock(
        spec=Settings,
        base_url="http://app-search.test",
        password=secrets.token_bytes(16),
        timeout_seconds=5,
        username="test-user",
        ca_cert_path=None,
        log_level="INFO",
    )


@pytest.fixture(scope="session")
def app(
    auth_provider: MockAuthProvider,
    key_provider: MockKeyProvider,
    settings: Settings,
) -> Flask:
    """Create the Flask app with test dependencies."""
    return create_app(
        auth_provider=auth_provider,
        key_provider=key_provider,
        settings=settings,
    )


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a Flask test client."""
    return app.test_client()
