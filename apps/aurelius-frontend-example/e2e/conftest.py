import re
from collections.abc import Generator
from pathlib import Path

import dotenv
import pytest
from playwright.sync_api import Page
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, Engine
from sqlmodel import Session, SQLModel, create_engine
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy, HttpWaitStrategy


class Settings(BaseSettings):
    """Test configuration."""

    auth_realm_name: str
    database_name: str
    database_password: SecretStr
    database_port: int
    database_username: str
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
def observability() -> DockerCompose:
    """
    Return a Docker Compose instance for the observability services.

    Note: This fixture starts the observability services if they're not already running, but does not stop them after
    the tests. This allows the services to be reused across multiple test sessions, but may require manual cleanup if
    the services are no longer needed.
    """
    context = Path(__file__).parents[3].absolute() / "dev" / "observability"
    compose = DockerCompose(context=context)

    compose.start()

    return compose


@pytest.fixture(scope="session")
def keycloak(observability: DockerCompose) -> DockerCompose:
    """
    Return a Docker Compose instance for the Keycloak service.

    Note: This fixture starts the Keycloak service if it's not already running, but does not stop it after the tests.
    This allows the service to be reused across multiple test sessions, but may require manual cleanup if the service is
    no longer needed.
    """
    _ = observability  # Ensure that the observability services are started before starting Keycloak

    context = Path(__file__).parents[3].absolute() / "dev" / "keycloak"
    compose = DockerCompose(context=context)

    compose.start()

    return compose.waiting_for(
        {
            "keycloak": HealthcheckWaitStrategy(),
        },
    )


@pytest.fixture(scope="session")
def compose(keycloak: DockerCompose, observability: DockerCompose) -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    _ = keycloak, observability  # Ensure that the auth and observability services are started before starting the app

    context = Path(__file__).parent.absolute()

    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        port = compose.get_service_port("aurelius-frontend-example", 8080)

        if not port:
            message = "aurelius-frontend-example service not found in Docker Compose"
            raise ValueError(message)

        yield compose.waiting_for(
            {
                "aurelius-frontend-example": HttpWaitStrategy(port=port, path="/").for_status_code(200),
            },
        )


@pytest.fixture(scope="session")
def base_url(compose: DockerCompose) -> str:
    """Return the base URL for the application."""
    port = compose.get_service_port("aurelius-frontend-example", 8080)
    return f"http://localhost:{port}"


@pytest.fixture()
def authenticated(page: Page, base_url: str, settings: Settings) -> Page:
    """Authenticate the user and return the page."""
    page.goto(base_url)

    page.wait_for_url(re.compile(f"/realms/{settings.auth_realm_name}/protocol/openid-connect/auth"))

    page.locator("#username").fill(settings.username)
    page.locator("#password").fill(settings.password.get_secret_value())
    page.get_by_role("button", name="Sign in").click()

    page.wait_for_url(re.compile(base_url))

    return page


@pytest.fixture(scope="session", autouse=True)
def database(compose: DockerCompose, settings: Settings) -> Engine:
    """Setup and teardown the database."""
    hostname, port = compose.get_service_host_and_port("postgres-app", settings.database_port)

    if not (hostname and port):
        message = "PostgreSQL service not found in Docker Compose"
        raise ValueError(message)

    url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.database_username,
        password=settings.database_password.get_secret_value(),
        host=hostname,
        port=port,
        database=settings.database_name,
    )

    engine = create_engine(url)

    # Create the database schema
    SQLModel.metadata.create_all(engine)

    return engine


@pytest.fixture
def session(database: Engine) -> Generator[Session]:
    """Return a SQLModel session."""
    with Session(database, expire_on_commit=False) as session:
        yield session
