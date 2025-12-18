import re
from pathlib import Path
from typing import TYPE_CHECKING, cast

import dotenv
import pytest
from aurelius_sdk.testing import capture_docker_compose_logs
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, Engine
from sqlmodel import Session, SQLModel, create_engine
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy

if TYPE_CHECKING:
    from collections.abc import Generator

    from playwright.sync_api import Page
    from pydantic import SecretStr


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
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    context = Path(__file__).parent.absolute()
    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        yield compose.waiting_for(
            {
                "aurelius-frontend-example": HealthcheckWaitStrategy(),
            },
        )
        capture_docker_compose_logs(compose)


@pytest.fixture(scope="session")
def base_url(compose: DockerCompose) -> str:
    """Return the base URL for the application."""
    port = compose.get_service_port("aurelius-frontend-example", 80)
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
        port=cast("int", port),
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
