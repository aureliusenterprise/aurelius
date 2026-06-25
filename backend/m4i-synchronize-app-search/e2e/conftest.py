import subprocess
import time
from pathlib import Path
from typing import Generator, List

import aiohttp
import dotenv
import pytest
import pytest_asyncio
import requests
from m4i_atlas_core import (
    ConfigStore,
    create_type_defs,
    data_dictionary_entity_type_mapping,
    data_dictionary_types_def,
    register_atlas_entity_types,
)
from m4i_atlas_core.api.atlas.create_entities import create_entities
from m4i_atlas_core.api.atlas.delete_entity_hard import delete_entity_hard
from m4i_atlas_core.api.atlas.delete_entity_soft import delete_entity_soft
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests_toolbelt.sessions import BaseUrlSession
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy


class Settings(BaseSettings):
    """Settings for e2e tests, loaded from the .env file."""

    model_config = SettingsConfigDict(env_file=dotenv.find_dotenv(), extra="ignore")

    app_search_base_url: str
    app_search_key_name: str
    elasticsearch_password: SecretStr
    elasticsearch_username: str
    keycloak_password: SecretStr
    keycloak_realm_name: str
    keycloak_username: str


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Return the settings for e2e tests."""
    return Settings()  # type: ignore[settings are loaded from the environment]


@pytest.fixture(scope="session")
def dev() -> DockerCompose:
    """
    Return a Docker Compose instance for the dev stack.

    Note: While this fixture spins up the dev stack, it does not tear it down. This is intentional, as the dev
    stack is expected to be long-running and shared across multiple test sessions.
    """
    context = Path(__file__).parents[3] / "dev"
    env_file = context / ".env"

    compose = DockerCompose(
        context, env_file=env_file.as_posix(), profiles=["atlas", "kafka", "keycloak", "elastic"]
    )

    try:
        compose.start()
    except subprocess.CalledProcessError as e:
        # The setup jobs for Keycloak and Elasticsearch exit after completing its one-time setup,
        # which causes docker compose to return a non-zero exit code.
        # Docker Compose may report this in various ways depending on the version:
        #   - "setup-1 exited" (older format)
        #   - "dependency failed to start: container ...-setup-1 exited (0)" (newer format)
        stderr = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else str(e.stderr)
        if "setup" not in stderr or "exited" not in stderr:
            raise

    return compose.waiting_for(
        {
            "atlas": HealthcheckWaitStrategy(),
            "enterprisesearch": HealthcheckWaitStrategy(),
            "kafka": HealthcheckWaitStrategy(),
            "keycloak": HealthcheckWaitStrategy(),
        }
    )


def wait_for_flink_job_running(flink_rest_url: str, timeout: float = 60, poll_interval: float = 3.0) -> None:
    """Poll the Flink Job Manager REST API until a job has running tasks."""
    deadline = time.monotonic() + timeout
    jobs_overview_url = f"{flink_rest_url.rstrip('/')}/v1/jobs/overview"

    while time.monotonic() < deadline:
        try:
            response = requests.get(jobs_overview_url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check if any job has all tasks fully running (no transitional states)
                jobs = data.get("jobs", [])
                for job in jobs:
                    tasks = job.get("tasks", {})

                    # At least one task must be running for the job to be considered fully started
                    running_tasks = tasks.get("running", 0)

                    # Tasks in transitional states that should be 0 for a fully started job
                    initializing = tasks.get("initializing", 0)
                    deploying = tasks.get("deploying", 0)
                    scheduled = tasks.get("scheduled", 0)
                    reconciling = tasks.get("reconciling", 0)

                    if running_tasks > 0 and not (initializing or deploying or scheduled or reconciling):
                        return

        except requests.exceptions.RequestException:
            continue

        time.sleep(poll_interval)

    raise TimeoutError(f"No Flink jobs with running tasks found at {flink_rest_url} within {timeout}s.")


def wait_for_atlas_ready(atlas_url: str, timeout: float = 120, poll_interval: float = 3.0) -> None:
    """Poll the Atlas REST API until it responds to a health check."""
    deadline = time.monotonic() + timeout
    health_url = f"{atlas_url.rstrip('/')}/v2/healthcheck"

    while time.monotonic() < deadline:
        try:
            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                return

        except requests.exceptions.RequestException:
            pass

        time.sleep(poll_interval)

    raise TimeoutError(f"Atlas not ready at {atlas_url} within {timeout}s.")


@pytest.fixture(scope="session")
def keycloak_url(dev: DockerCompose) -> str:
    """Return the Keycloak base URL."""
    port = dev.get_service_port("keycloak", 8180)
    return f"http://keycloak.localhost:{port}"


@pytest.fixture(scope="session")
def auth_token(keycloak_url: str, settings: Settings) -> str:
    """Obtain a JWT Bearer token."""
    resp = requests.post(
        f"{keycloak_url}/realms/{settings.keycloak_realm_name}/protocol/openid-connect/token",
        data={
            "client_id": "m4i_atlas",
            "username": settings.keycloak_username,
            "password": settings.keycloak_password.get_secret_value(),
            "grant_type": "password",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _init_atlas(dev: DockerCompose, auth_token: str) -> None:
    """Fixture to initialize the Atlas configuration."""
    store = ConfigStore.get_instance()

    atlas_port = dev.get_service_port("atlas", 21000)
    atlas_url = f"http://localhost:{atlas_port}/api/atlas"

    # Wait for Atlas to be ready before attempting any API calls
    wait_for_atlas_ready(atlas_url)

    store.load({"atlas.server.url": atlas_url})

    register_atlas_entity_types(data_dictionary_entity_type_mapping)

    try:
        await create_type_defs(data_dictionary_types_def, access_token=auth_token)
    except aiohttp.ClientResponseError as e:
        if e.status != 409:  # 409 Conflict is expected if types are already registered
            raise


@pytest.fixture(scope="session", autouse=True)
def kafka_connect(dev: DockerCompose) -> Generator[DockerCompose, None, None]:
    """Spin up the kafka connector via Docker Compose."""
    context = Path(__file__).parents[3] / "connectors/kafka-connect"
    env_file = context / ".env"

    with DockerCompose(context, env_file=str(env_file)) as compose:
        yield compose.waiting_for({"kafka-connect": HealthcheckWaitStrategy()})


@pytest.fixture(scope="session", autouse=True)
def publish_state(dev: DockerCompose) -> Generator[DockerCompose, None, None]:
    """Spin up the publish state stack via Docker Compose."""
    context = Path(__file__).parents[2].absolute() / "m4i-publish-state"
    env_file = context / ".env"

    with DockerCompose(context, env_file=str(env_file)) as compose:
        flink_port = compose.get_service_port("jobmanager", 18083)
        flink_rest_url = f"http://localhost:{flink_port}"

        wait_for_flink_job_running(flink_rest_url)

        yield compose


@pytest.fixture(scope="session", autouse=True)
def synchronize_app_search(dev: DockerCompose) -> Generator[DockerCompose, None, None]:
    """Spin up the synchronize app search stack via Docker Compose."""
    context = Path(__file__).parents[1].absolute()
    env_file = context / ".env"

    with DockerCompose(context, env_file=str(env_file)) as compose:
        flink_port = compose.get_service_port("jobmanager", 18081)
        flink_rest_url = f"http://localhost:{flink_port}"

        wait_for_flink_job_running(flink_rest_url)

        yield compose


@pytest.fixture(scope="session")
def app_search_key(settings: Settings) -> str:
    """Fetch the App Search API key from the App Search instance."""
    clean_base = str(settings.app_search_base_url).rstrip("/")

    key_response = requests.get(
        f"{clean_base}/api/as/v1/credentials/{settings.app_search_key_name}",
        auth=(settings.elasticsearch_username, settings.elasticsearch_password.get_secret_value()),
        verify=False,
    )

    key_response.raise_for_status()

    key_info = key_response.json()

    return key_info["key"]


@pytest.fixture(scope="session")
def app_search_session(app_search_key: str, settings: Settings) -> BaseUrlSession:
    """Create a requests session for App Search with the provided API key."""
    session = BaseUrlSession(base_url=settings.app_search_base_url)
    session.headers.update({"Authorization": f"Bearer {app_search_key}"})
    session.verify = False
    return session


# ---------------------------------------------------------------------------
# Helper fixtures for test cases
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def create_atlas_entity():
    """
    Factory fixture to create Atlas entities and return their GUIDs.

    Usage:
        guid = await create_atlas_entity(BusinessDataDomain, attributes, auth_token)
    """

    async def _create(entity_class, attributes, access_token: str):
        entity = entity_class(attributes=attributes)
        response = await create_entities(entity, access_token=access_token)
        return response.guid_assignments[entity.guid]

    return _create


@pytest_asyncio.fixture(scope="session")
async def delete_atlas_entity():
    """
    Factory fixture to hard-delete Atlas entities by GUID.

    Usage:
        await delete_atlas_entity([guid], auth_token)
    """

    async def _delete(guids: List[str], access_token: str):
        response = await delete_entity_hard(guids, access_token=access_token)
        print(response)

    return _delete


@pytest_asyncio.fixture(scope="session")
async def soft_delete_atlas_entity():
    """
    Factory fixture to soft-delete Atlas entities by GUID.

    Usage:
        await soft_delete_atlas_entity([guid], auth_token)
    """

    async def _soft_delete(guids: List[str], access_token: str):
        for guid in guids:
            await delete_entity_soft(guid, access_token=access_token)

    return _soft_delete


@pytest.fixture(scope="session")
def get_app_search_document():
    """
    Factory fixture to fetch a single document from App Search by GUID.

    Usage:
        doc = get_app_search_document(app_search_session, guid)
        Returns dict or None if not found.
    """

    def _get(session: BaseUrlSession, guid: str):
        response = session.get("/api/as/v1/engines/atlas-dev/documents", json=[guid])

        response.raise_for_status()

        documents = response.json()

        if not documents:
            return None

        matches = [doc for doc in documents if doc and doc.get("guid") == guid]

        if not matches:
            return None

        return matches[0]

    return _get


@pytest.fixture(scope="session")
def wait_for_sync():
    """
    Factory fixture to poll App Search until a document appears or disappears.

    Usage:
        doc = wait_for_sync(app_search_session, guid, expected_exists=True)
        doc = wait_for_sync(app_search_session, guid, expected_exists=False)  # for deletion
    """

    def _wait(
        session: BaseUrlSession,
        guid: str,
        expected_exists: bool = True,
        max_attempts: int = 12,
        wait_seconds: int = 5,
    ):
        for _ in range(1, max_attempts + 1):
            response = session.get("/api/as/v1/engines/atlas-dev/documents", json=[guid])

            response.raise_for_status()

            documents = response.json()
            matches = [doc for doc in documents if doc and doc.get("guid") == guid]

            if not matches and not expected_exists:
                return None

            if not matches and expected_exists:
                time.sleep(wait_seconds)
                continue

            document = matches[0]

            if document and expected_exists:
                return document

            if document and not expected_exists:
                time.sleep(wait_seconds)
                continue

            time.sleep(wait_seconds)

        raise TimeoutError(
            f"Document with GUID {guid} did not reach the expected state (exists={expected_exists}) after "
            f"{max_attempts} attempts."
        )

    return _wait
