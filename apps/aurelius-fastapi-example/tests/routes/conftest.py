from collections.abc import Callable, Generator

import pytest
from aurelius_example import Entity
from aurelius_fastapi_example.app import create_app
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import get_settings
from aurelius_fastapi_example.providers import session as db_provider_session
from aurelius_fastapi_example.providers import user_info as auth_user_info
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session


def _override_session(session: Session) -> Callable[[], Generator[Session]]:
    """Create a database session override compatible with FastAPI dependency injection."""

    def override_session() -> Generator[Session]:
        try:
            yield session
        except Exception:
            session.rollback()
            raise

    return override_session


def _client_with_overrides(
    app: FastAPI,
    db_settings: Settings,
    db_session: Session,
    override_user_info: Callable[[], dict],
) -> Generator[TestClient]:
    """Build a TestClient with auth and database dependency overrides."""
    app.dependency_overrides[get_settings] = lambda: db_settings
    app.dependency_overrides[db_provider_session] = _override_session(db_session)
    app.dependency_overrides[auth_user_info] = override_user_info

    try:
        with TestClient(app, raise_server_exceptions=True) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def app(db_settings: Settings) -> FastAPI:
    """Create a FastAPI app instance for testing."""
    return create_app(db_settings)


@pytest.fixture
def unauthenticated_client(app: FastAPI, db_session: Session, db_settings: Settings) -> Generator[TestClient]:
    """Provide a TestClient that forces authentication failure with a 401 response."""

    def override_user_info() -> dict:
        raise HTTPException(status_code=401)

    yield from _client_with_overrides(app, db_settings, db_session, override_user_info)


@pytest.fixture
def mock_user() -> dict:
    """Return a minimal decoded JWT payload for use in tests."""
    return {"sub": "test-user-id", "preferred_username": "testuser"}


@pytest.fixture
def authenticated_client(
    app: FastAPI,
    mock_user: dict,
    db_session: Session,
    db_settings: Settings,
) -> Generator[TestClient]:
    """Provide a FastAPI TestClient with DB and auth overrides."""

    def override_user_info() -> dict:
        return mock_user

    yield from _client_with_overrides(app, db_settings, db_session, override_user_info)


@pytest.fixture
def entities(db_session: Session) -> Generator[list[Entity]]:
    """Create and return a list of test entities."""
    test_entities = [
        Entity(name="alpha device", description="first result"),
        Entity(name="beta device", description="contains alpha keyword"),
        Entity(name="gamma device", description="unrelated"),
    ]

    db_session.add_all(test_entities)
    db_session.commit()

    for entity in test_entities:
        db_session.refresh(entity)

    yield sorted(test_entities)

    for entity in test_entities:
        db_session.delete(entity)

    db_session.commit()


@pytest.fixture
def entity(db_session: Session) -> Generator[Entity]:
    """Create and return a single test entity."""
    entity = Entity(name="Test Entity", description="A test entity")

    db_session.add(entity)
    db_session.commit()

    db_session.refresh(entity)

    yield entity

    db_session.delete(entity)
    db_session.commit()
