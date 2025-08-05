import re
from collections.abc import Generator
from pathlib import Path

import dotenv
import pytest
from aurelius_sdk.testing import capture_docker_compose_logs
from playwright.sync_api import Page
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready


class Settings(BaseSettings):
    """Test configuration."""

    auth_realm_name: str
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
@wait_container_is_ready()
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    context = Path(__file__).parent.absolute()
    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        yield compose
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
