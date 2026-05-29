from pathlib import Path
from typing import Generator

import dotenv
import pytest
import requests
from pydantic_settings import BaseSettings, SettingsConfigDict
from tenacity import Retrying, stop_after_attempt, wait_exponential
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready


class E2ESettings(BaseSettings):
    """Settings for e2e tests, loaded from the .env file."""

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv(),
        extra="ignore",
    )

    # Keycloak
    keycloak_username: str
    keycloak_password: str
    keycloak_realm_name: str
    keycloak_bootstrap_admin_username: str
    keycloak_bootstrap_admin_password: str

    # App Search
    app_search_username: str
    app_search_password: str


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Load the .env file for the e2e tests."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
@wait_container_is_ready()  # type: ignore
def compose() -> Generator[DockerCompose, None, None]:
    """Spin up the full e2e stack via Docker Compose."""
    with DockerCompose(
        Path(__file__).parent.absolute(),
        env_file=dotenv.find_dotenv(),
    ) as compose:
        yield compose


@pytest.fixture(scope="session")
def e2e_settings() -> E2ESettings:
    """Return e2e test settings loaded from the .env file."""
    return E2ESettings()  # type: ignore[settings are loaded from the environment]


@pytest.fixture(scope="session")
def keycloak_url(compose: DockerCompose) -> str:
    """Return the Keycloak base URL."""
    host = compose.get_service_host("keycloak", 8180)
    port = compose.get_service_port("keycloak", 8180)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def api_base_url(compose: DockerCompose) -> str:
    """Return the m4i-search-api base URL."""
    host = compose.get_service_host("m4i-search-api", 8531)
    port = compose.get_service_port("m4i-search-api", 8531)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def es_base_url(compose: DockerCompose) -> str:
    """Return the Enterprise Search base URL."""
    host = compose.get_service_host("enterprisesearch", 3002)
    port = compose.get_service_port("enterprisesearch", 3002)
    return f"https://{host}:{port}"


@pytest.fixture(scope="session", autouse=True)
def _setup_keycloak_user(
    compose: DockerCompose,
    e2e_settings: E2ESettings,
    keycloak_url: str,
) -> None:
    """Create a test user in Keycloak via the Admin REST API."""

    def _get_admin_token() -> str:
        """Obtain an admin token from the master realm."""
        resp = requests.post(
            f"{keycloak_url}/realms/master/protocol/openid-connect/token",
            data={
                "client_id": "admin-cli",
                "username": e2e_settings.keycloak_bootstrap_admin_username,
                "password": e2e_settings.keycloak_bootstrap_admin_password,
                "grant_type": "password",
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def _create_user_if_not_exists(admin_token: str) -> None:
        """Create the test user if it doesn't already exist."""
        # Check if user exists
        resp = requests.get(
            f"{keycloak_url}/admin/realms/{e2e_settings.keycloak_realm_name}/users",
            params={"username": e2e_settings.keycloak_username},
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=30,
            verify=False,
        )
        resp.raise_for_status()
        users = resp.json()

        if users:
            # User already exists, nothing to do
            return

        # Create user
        resp = requests.post(
            f"{keycloak_url}/admin/realms/{e2e_settings.keycloak_realm_name}/users",
            json={
                "username": e2e_settings.keycloak_username,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": e2e_settings.keycloak_password,
                        "temporary": False,
                    }
                ],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=30,
        )
        resp.raise_for_status()

    # Wait for Keycloak Admin API to be ready, then create user
    for attempt in Retrying(
        stop=stop_after_attempt(15),
        wait=wait_exponential(multiplier=1, min=2, max=15),
    ):
        with attempt:
            admin_token = _get_admin_token()
            _create_user_if_not_exists(admin_token)


@pytest.fixture(scope="session")
def auth_token(
    keycloak_url: str,
    e2e_settings: E2ESettings,
) -> str:
    """Obtain a JWT Bearer token for the test user."""

    def _get_token() -> str:
        resp = requests.post(
            f"{keycloak_url}/realms/{e2e_settings.keycloak_realm_name}/protocol/openid-connect/token",
            data={
                "client_id": "m4i_atlas",
                "username": e2e_settings.keycloak_username,
                "password": e2e_settings.keycloak_password,
                "grant_type": "password",
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    # Retry in case Keycloak is still initializing
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            return _get_token()

    raise RuntimeError("Failed to obtain auth token from Keycloak")


@pytest.fixture(scope="session")
def api_session(auth_token: str) -> requests.Session:
    """Return a requests.Session pre-configured with the auth token."""
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {auth_token}"})
    return session


@pytest.fixture(scope="session")
def es_private_key(
    es_base_url: str,
    e2e_settings: E2ESettings,
) -> str:
    """Fetch the App Search private API key from Enterprise Search."""
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            key_resp = requests.get(
                f"{es_base_url}/api/as/v1/credentials/private-key",
                auth=(
                    e2e_settings.app_search_username,
                    e2e_settings.app_search_password,
                ),
                timeout=30,
                verify=False,
            )
            key_resp.raise_for_status()
            return key_resp.json()["key"]

    raise RuntimeError("Failed to fetch App Search private key")


@pytest.fixture(scope="session", autouse=True)
def _setup_app_search_engine(
    es_base_url: str,
    es_private_key: str,
) -> None:
    """Create a minimal test engine in Enterprise Search.

    This ensures there is at least one engine for proxy tests to target.
    """
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            # Create test engine (idempotent — ignore 409 if it already exists)
            requests.post(
                f"{es_base_url}/api/as/v1/engines",
                json={
                    "name": "test-engine",
                    "type": "default",
                },
                headers={"Authorization": f"Bearer {es_private_key}"},
                timeout=30,
                verify=False,
            )
            break
