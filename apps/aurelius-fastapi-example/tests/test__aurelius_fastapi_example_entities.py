from fastapi.testclient import TestClient


def test__find_many_returns_empty_list(authenticated_client: TestClient) -> None:
    """Entities list should be empty when nothing has been created."""
    response = authenticated_client.get("/entities/")

    assert response.status_code == 200
    assert response.json() == []


def test__create_find_and_delete_entity(authenticated_client: TestClient) -> None:
    """Create an entity, retrieve it by GUID, delete it, and verify it is gone."""
    create_response = authenticated_client.put(
        "/entities/",
        json={"name": "Unit Test Entity", "description": "Created by unit test"},
    )

    assert create_response.status_code == 200

    created = create_response.json()
    assert created["guid"]
    assert created["name"] == "Unit Test Entity"

    guid = created["guid"]

    find_response = authenticated_client.get(f"/entities/{guid}")
    assert find_response.status_code == 200
    assert find_response.json()["guid"] == guid

    delete_response = authenticated_client.delete(f"/entities/{guid}")
    assert delete_response.status_code == 200

    not_found_response = authenticated_client.get(f"/entities/{guid}")
    assert not_found_response.status_code == 410


def test__find_many_respects_pagination(authenticated_client: TestClient) -> None:
    """The list endpoint should apply skip and limit pagination values."""
    created_entities = []
    try:
        for i in range(3):
            response = authenticated_client.put(
                "/entities/",
                json={"name": f"Entity {i}", "description": f"Description {i}"},
            )
            assert response.status_code == 200
            created_entities.append(response.json())

        paginated = authenticated_client.get("/entities/?skip=1&limit=2")

        assert paginated.status_code == 200
        assert len(paginated.json()) == 2
    finally:
        # Clean up test entities to ensure isolation
        for entity in created_entities:
            authenticated_client.delete(f"/entities/{entity['guid']}")


def test__find_one_returns_410_for_missing_entity(authenticated_client: TestClient) -> None:
    """Requesting a non-existent entity should return 410 Gone."""
    response = authenticated_client.get("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 410


def test__delete_returns_410_for_missing_entity(authenticated_client: TestClient) -> None:
    """Deleting a non-existent entity should return 410 Gone."""
    response = authenticated_client.delete("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 410


def test__create_entity_with_invalid_data_returns_422(authenticated_client: TestClient) -> None:
    """Creating an entity with data exceeding max_length should return 422 Unprocessable Entity."""
    response = authenticated_client.put(
        "/entities/",
        json={"name": "x" * 101, "description": "Valid description"},
    )

    assert response.status_code == 422


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
    response = unauthenticated_client.put(
        "/entities/",
        json={"name": "Auth Fail", "description": "No token"},
    )

    assert response.status_code == 401


def test__delete_requires_authentication(unauthenticated_client: TestClient) -> None:
    """Delete endpoint should return 401 when no bearer token is provided."""
    response = unauthenticated_client.delete("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 401
