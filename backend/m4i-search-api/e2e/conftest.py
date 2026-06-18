import os
import subprocess
from pathlib import Path
from typing import Generator

import dotenv
import pytest
import requests
from pydantic_settings import BaseSettings, SettingsConfigDict
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy, HttpWaitStrategy


class E2ESettings(BaseSettings):
    """Settings for e2e tests, loaded from the .env file."""

    model_config = SettingsConfigDict(env_file=dotenv.find_dotenv(), extra="ignore")

    # App
    wsgi_port: int

    # Keycloak
    keycloak_username: str
    keycloak_password: str
    keycloak_realm_name: str

    # App Search
    app_search_username: str
    app_search_password: str


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Load the .env file for the e2e tests."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
def e2e_settings() -> E2ESettings:
    """Return e2e test settings loaded from the .env file."""
    return E2ESettings()  # type: ignore[settings are loaded from the environment]


@pytest.fixture(scope="session")
def dev() -> DockerCompose:
    """
    Return a Docker Compose instance for the dev stack.

    Note: While this fixture spins up the dev stack, it does not tear it down. This is intentional, as the dev
    stack is expected to be long-running and shared across multiple test sessions.
    """
    context = Path(__file__).parents[3] / "dev"
    env_file = context / ".env"

    compose = DockerCompose(context, env_file=env_file.as_posix(), profiles=["elastic", "keycloak"])

    try:
        compose.start()
    except subprocess.CalledProcessError as e:
        # The setup jobs for Keycloak and Elasticsearch exit after completing its one-time setup,
        # which causes docker compose to return a non-zero exit code.
        if b"setup-1 exited" not in e.stderr:
            raise

    return compose.waiting_for(
        {"keycloak": HealthcheckWaitStrategy(), "enterprisesearch": HealthcheckWaitStrategy()}
    )


@pytest.fixture(scope="session")
def compose(dev: DockerCompose, e2e_settings: E2ESettings) -> Generator[DockerCompose, None, None]:
    """Spin up the full e2e stack via Docker Compose."""
    os.environ["KEYCLOAK_HTTP_PORT"] = str(dev.get_service_port("keycloak", 8180))
    os.environ["ENTERPRISE_SEARCH_PORT"] = str(dev.get_service_port("enterprisesearch", 3002))

    with DockerCompose(Path(__file__).parent.absolute(), env_file=dotenv.find_dotenv()) as compose:
        yield compose.waiting_for(
            {"m4i-search-api": HttpWaitStrategy(path="/health", port=e2e_settings.wsgi_port)}
        )


@pytest.fixture(scope="session")
def keycloak_url(dev: DockerCompose) -> str:
    """Return the Keycloak base URL."""
    host = dev.get_service_host("keycloak", 8180)
    port = dev.get_service_port("keycloak", 8180)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def api_base_url(compose: DockerCompose) -> str:
    """Return the m4i-search-api base URL."""
    host = compose.get_service_host("m4i-search-api", 8531)
    port = compose.get_service_port("m4i-search-api", 8531)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def es_base_url(dev: DockerCompose) -> str:
    """Return the Enterprise Search base URL."""
    host = dev.get_service_host("enterprisesearch", 3002)
    port = dev.get_service_port("enterprisesearch", 3002)
    return f"https://{host}:{port}"


@pytest.fixture(scope="session")
def auth_token(keycloak_url: str, e2e_settings: E2ESettings) -> str:
    """Obtain a JWT Bearer token."""

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


@pytest.fixture(scope="session")
def api_session(auth_token: str) -> requests.Session:
    """Return a requests.Session pre-configured with the auth token."""
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {auth_token}"})
    return session


@pytest.fixture(scope="session")
def es_private_key(es_base_url: str, e2e_settings: E2ESettings) -> str:
    """Fetch the App Search private API key from Enterprise Search."""
    key_resp = requests.get(
        f"{es_base_url}/api/as/v1/credentials/private-key",
        auth=(e2e_settings.app_search_username, e2e_settings.app_search_password),
        timeout=30,
        verify=False,
    )
    key_resp.raise_for_status()
    return key_resp.json()["key"]


@pytest.fixture(scope="session")
def app_search_engine(es_base_url: str, es_private_key: str) -> Generator[str, None, None]:
    """
    Create a minimal test engine in Enterprise Search.

    This ensures there is at least one engine for proxy tests to target.
    """
    name = "test-engine"

    requests.post(
        f"{es_base_url}/api/as/v1/engines",
        json={"name": name, "type": "default"},
        headers={"Authorization": f"Bearer {es_private_key}"},
        timeout=30,
        verify=False,
    )

    yield name

    requests.delete(
        f"{es_base_url}/api/as/v1/engines/{name}",
        headers={"Authorization": f"Bearer {es_private_key}"},
        timeout=30,
        verify=False,
    )
