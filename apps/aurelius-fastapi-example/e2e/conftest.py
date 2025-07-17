import http.client
from collections.abc import Generator
from pathlib import Path
from typing import cast

import dotenv
import pytest
from aurelius_sdk.testing import capture_docker_compose_logs
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, Engine, create_engine
from sqlmodel import Session, SQLModel
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready


class Settings(BaseSettings):
    """Test configuration."""

    postgres_db: str
    postgres_password: SecretStr
    postgres_user: str

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv(),
        extra="ignore",
    )


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Return the test configuration."""
    return Settings()  # type: ignore[values are loaded from the environment]


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Load the environment variables."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
@wait_container_is_ready()
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    context = Path(__file__).parents[1].absolute()
    with DockerCompose(context=context, profiles=["e2e"]) as compose:
        yield compose
        capture_docker_compose_logs(compose)


@pytest.fixture(scope="session", autouse=True)
def database(compose: DockerCompose, settings: Settings) -> Generator[Engine]:
    """Setup and teardown the database."""
    hostname, port = compose.get_service_host_and_port("postgres-e2e", 5432)

    if not (hostname and port):
        message = "PostgreSQL service not found in Docker Compose"
        raise ValueError(message)

    url = URL.create(
        drivername="postgresql",
        username=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        host=hostname,
        port=cast("int", port),
        database=settings.postgres_db,
    )

    engine = create_engine(url)

    # Create the database schema
    SQLModel.metadata.create_all(engine)

    yield engine

    # Drop the database schema
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def session(database: Engine) -> Generator[Session]:
    """Return a SQLModel session."""
    with Session(database, expire_on_commit=False) as session:
        yield session


@pytest.fixture()
def connection(compose: DockerCompose) -> http.client.HTTPConnection:
    """Return an HTTP connection to the API."""
    host, port = compose.get_service_host_and_port("aurelius-fastapi-example", 8000)

    if not (host and port):
        message = "Service not found in Docker Compose"
        raise ValueError(message)

    return http.client.HTTPConnection(host, cast("int", port))
