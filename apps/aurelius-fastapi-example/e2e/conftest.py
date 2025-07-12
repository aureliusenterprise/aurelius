import http.client
from collections.abc import Generator
from pathlib import Path
from typing import cast

import dotenv
import pytest
from aurelius_testing.testcontainers import capture_docker_compose_logs
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Load the environment variables."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
@wait_container_is_ready()
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    context = Path(__file__).parent.absolute()
    env_file = dotenv.find_dotenv()

    with DockerCompose(context, env_file=env_file) as compose:
        yield compose
        capture_docker_compose_logs(compose)


@pytest.fixture()
def connection(compose: DockerCompose) -> http.client.HTTPConnection:
    """Return an HTTP connection to the API."""
    host, port = compose.get_service_host_and_port("aurelius-fastapi-example", 8000)

    if not (host and port):
        message = "Service not found in Docker Compose"
        raise ValueError(message)

    return http.client.HTTPConnection(host, cast("int", port))
