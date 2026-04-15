import secrets
from collections.abc import Generator
from unittest.mock import Mock

import httpx
import pytest
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import auth
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

KEYCLOAK_REALM = "master"


@pytest.fixture(scope="session")
def keycloak_admin_credentials() -> dict[str, str]:
    """Return generated admin credentials for the Keycloak testcontainer."""
    return {
        "username": "admin",
        "password": secrets.token_urlsafe(16),
    }


@pytest.fixture(scope="session")
def keycloak_container(keycloak_admin_credentials: dict[str, str]) -> Generator[DockerContainer]:
    """Start a Keycloak container to act as a real OIDC provider for auth tests."""
    with (
        DockerContainer("keycloak/keycloak:latest")
        .with_env("KEYCLOAK_ADMIN", keycloak_admin_credentials["username"])
        .with_env("KEYCLOAK_ADMIN_PASSWORD", keycloak_admin_credentials["password"])
        .with_env("KC_HEALTH_ENABLED", "true")
        .with_exposed_ports(8080, 9000)
        .with_command("start-dev --http-port=8080")
        # Keycloak can be slow to start, especially on CI, so we use a long timeout and check the health endpoint
        .waiting_for(HttpWaitStrategy(port=9000, path="/health/ready").for_status_code(200).with_startup_timeout(300))
    ) as container:
        yield container


@pytest.fixture(scope="session")
def auth_settings(keycloak_container: DockerContainer) -> Settings:
    """Return settings pointing auth_* fields at the Keycloak testcontainer."""
    host = keycloak_container.get_container_host_ip()
    port = keycloak_container.get_exposed_port(8080)

    return Mock(
        auth_realm_name=KEYCLOAK_REALM,
        auth_server_url=f"http://{host}:{port}/",
        spec=Settings,
    )


@pytest.fixture(scope="session")
def auth_base_url(auth_settings: Settings) -> str:
    """Return the base URL for the authentication server."""
    return f"{auth_settings.auth_server_url}realms/{auth_settings.auth_realm_name}"


@pytest.fixture()
def http_client() -> Generator[httpx.Client]:
    """Provide a shared HTTP client for auth provider tests."""
    with httpx.Client(timeout=5.0) as client:
        yield client


@pytest.fixture()
def keycloak_access_token(
    auth_base_url: str,
    keycloak_admin_credentials: dict[str, str],
    http_client: httpx.Client,
) -> str:
    """Return a real bearer token from Keycloak using admin-cli password grant."""
    token_url = f"{auth_base_url}/protocol/openid-connect/token"

    response = http_client.post(
        token_url,
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": keycloak_admin_credentials["username"],
            "password": keycloak_admin_credentials["password"],
        },
    )

    response.raise_for_status()

    return response.json()["access_token"]


@pytest.fixture(autouse=True)
def clear_auth_caches() -> Generator[None]:
    """Clear auth provider caches before and after each test for deterministic behavior."""
    auth.auth_base_url.cache_clear()
    auth.auth_provider.cache_clear()
    auth.openid_configuration.cache_clear()
    auth.jwks.cache_clear()

    yield

    auth.auth_base_url.cache_clear()
    auth.auth_provider.cache_clear()
    auth.openid_configuration.cache_clear()
    auth.jwks.cache_clear()
