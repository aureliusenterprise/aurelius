import http.client
from collections.abc import Generator
from pathlib import Path

import dotenv
import pytest
from aurelius_sdk.testing import capture_docker_compose_logs
from keycloak import KeycloakOpenID
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, Engine, create_engine
from sqlmodel import Session, SQLModel
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy


class Settings(BaseSettings):
    """Test configuration."""

    auth_client_id: str
    auth_realm_name: str
    database_name: str
    database_password: SecretStr
    database_port: int
    database_username: str
    keycloak_port: int
    password: SecretStr
    username: str

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
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    context = Path(__file__).parent.absolute()
    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        yield compose.waiting_for(
            {
                "aurelius-fastapi-example": HealthcheckWaitStrategy(),
            },
        )
        capture_docker_compose_logs(compose)


@pytest.fixture(scope="session", autouse=True)
def database(compose: DockerCompose, settings: Settings) -> Generator[Engine]:
    """Setup and teardown the database."""
    hostname, port = compose.get_service_host_and_port("postgres-app", settings.database_port)

    if not (hostname and port):
        message = "PostgreSQL service not found in Docker Compose"
        raise ValueError(message)

    url = URL.create(
        drivername="postgresql",
        username=settings.database_username,
        password=settings.database_password.get_secret_value(),
        host=hostname,
        port=port,
        database=settings.database_name,
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
def connection(compose: DockerCompose) -> Generator[http.client.HTTPConnection]:
    """Return an HTTP connection to the API."""
    host, port = compose.get_service_host_and_port("aurelius-fastapi-example", 8000)

    if not (host and port):
        message = "Service not found in Docker Compose"
        raise ValueError(message)

    connection = http.client.HTTPConnection(host, port)

    yield connection

    connection.close()


@pytest.fixture(scope="session")
def keycloak_client(settings: Settings) -> KeycloakOpenID:
    """Return a Keycloak client."""
    return KeycloakOpenID(
        server_url=f"http://keycloak.localhost:{settings.keycloak_port}",
        client_id=settings.auth_client_id,
        realm_name=settings.auth_realm_name,
    )


@pytest.fixture()
def token(keycloak_client: KeycloakOpenID, settings: Settings) -> str:
    """Return a valid access token."""
    return keycloak_client.token(
        settings.username,
        settings.password.get_secret_value(),
    )["access_token"]
