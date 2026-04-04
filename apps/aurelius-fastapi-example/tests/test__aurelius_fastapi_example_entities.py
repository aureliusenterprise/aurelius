from collections.abc import Generator

import pytest
from aurelius_example import Entity
from fastapi.testclient import TestClient
from sqlmodel import Session


def test__find_many_returns_empty_list(authenticated_client: TestClient) -> None:
    """Entities list should be empty when nothing has been created."""
    response = authenticated_client.get("/entities/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.fixture()
def entities(session: Session) -> Generator[list[Entity]]:
    """Create and return a list of test entities."""
    test_entities = [
        Entity(name="Test Entity 1", description="First test entity"),
        Entity(name="Test Entity 2", description="Second test entity"),
        Entity(name="Test Entity 3", description="Third test entity"),
    ]

    session.add_all(test_entities)
    session.commit()

    for entity in test_entities:
        session.refresh(entity)

    yield test_entities

    for entity in test_entities:
        session.delete(entity)

    session.commit()


def test__find_many_returns_entities(authenticated_client: TestClient, entities: list[Entity]) -> None:
    """Entities list should return created entities."""
    response = authenticated_client.get("/entities/")

    assert response.status_code == 200

    actual = [Entity.model_validate(entity) for entity in response.json()]

    assert entities == actual


def test__find_many_respects_pagination(authenticated_client: TestClient, entities: list[Entity]) -> None:
    """The list endpoint should apply skip and limit pagination values."""
    response = authenticated_client.get("/entities/?skip=1&limit=1")

    assert response.status_code == 200

    actual = [Entity.model_validate(entity) for entity in response.json()]

    assert actual == [entities[1]]


def test__find_many_rejects_limit_over_max(authenticated_client: TestClient) -> None:
    """The list endpoint should return 422 when given a limit value over the maximum."""
    response = authenticated_client.get("/entities/?limit=1001")

    assert response.status_code == 422


def test__find_many_rejects_negative_limit(authenticated_client: TestClient) -> None:
    """The list endpoint should return 422 when given a negative limit value."""
    response = authenticated_client.get("/entities/?limit=-1")

    assert response.status_code == 422


def test__find_many_rejects_negative_skip(authenticated_client: TestClient) -> None:
    """The list endpoint should return 422 when given a negative skip value."""
    response = authenticated_client.get("/entities/?skip=-1")

    assert response.status_code == 422


def test__find_many_rejects_non_integer_limit(authenticated_client: TestClient) -> None:
    """The list endpoint should return 422 when given a non-integer limit value."""
    response = authenticated_client.get("/entities/?limit=abc")

    assert response.status_code == 422


def test__find_many_rejects_non_integer_skip(authenticated_client: TestClient) -> None:
    """The list endpoint should return 422 when given a non-integer skip value."""
    response = authenticated_client.get("/entities/?skip=abc")

    assert response.status_code == 422


def test__create_entity(authenticated_client: TestClient, session: Session) -> None:
    """Creating an entity should return the created entity with a GUID."""
    entity = Entity(name="New Entity", description="A newly created entity")

    response = authenticated_client.put(
        "/entities/",
        json=entity.model_dump(mode="json"),
    )

    assert response.status_code == 200

    actual = Entity.model_validate(response.json())

    assert entity == actual

    stored = session.get(Entity, actual.guid)

    assert stored == actual


@pytest.fixture()
def entity(session: Session) -> Generator[Entity]:
    """Create and return a single test entity."""
    entity = Entity(name="Test Entity", description="A test entity")

    session.add(entity)
    session.commit()

    session.refresh(entity)

    yield entity

    session.delete(entity)
    session.commit()


def test__update_entity(authenticated_client: TestClient, session: Session, entity: Entity) -> None:
    """Updating an entity should change its values but keep the same GUID."""
    updated = entity.model_copy(update={"name": "Updated Name", "description": "Updated description"})

    response = authenticated_client.put(
        "/entities/",
        json=updated.model_dump(mode="json"),
    )

    assert response.status_code == 200

    actual = Entity.model_validate(response.json())

    assert updated == actual

    stored = session.get(Entity, entity.guid)

    assert stored == actual


def test__delete_entity(authenticated_client: TestClient, session: Session, entity: Entity) -> None:
    """Deleting an entity should remove it from the database."""
    response = authenticated_client.delete(f"/entities/{entity.guid}")

    assert response.status_code == 200

    stored = session.get(Entity, entity.guid)

    assert stored is None


def test__find_one_returns_410_for_missing_entity(authenticated_client: TestClient) -> None:
    """Requesting a non-existent entity should return 410 Gone."""
    response = authenticated_client.get("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 410


def test__delete_returns_410_for_missing_entity(authenticated_client: TestClient) -> None:
    """Deleting a non-existent entity should return 410 Gone."""
    response = authenticated_client.delete("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 410


def test__find_many_requires_authentication(unauthenticated_client: TestClient) -> None:
    """List endpoint should return 401 when no bearer token is provided."""
    response = unauthenticated_client.get("/entities/")

    assert response.status_code == 401


def test__find_one_requires_authentication(unauthenticated_client: TestClient) -> None:
    """Find-one endpoint should return 401 when no bearer token is provided."""
    response = unauthenticated_client.get("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 401


def test__create_requires_authentication(unauthenticated_client: TestClient) -> None:
    """Create/update endpoint should return 401 when no bearer token is provided."""
    entity = Entity(name="Auth Fail", description="No token")
    response = unauthenticated_client.put("/entities/", json=entity.model_dump(mode="json"))

    assert response.status_code == 401


def test__delete_requires_authentication(unauthenticated_client: TestClient) -> None:
    """Delete endpoint should return 401 when no bearer token is provided."""
    response = unauthenticated_client.delete("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 401
