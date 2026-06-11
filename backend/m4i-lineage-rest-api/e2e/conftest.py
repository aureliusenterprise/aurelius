import pytest
import socket
from urllib.parse import urlparse
from m4i_atlas_core import get_entity_by_qualified_name, delete_entity_soft, delete_entity_hard
from m4i_atlas_core.api.atlas import get_entities_by_attribute
from typing import Generator
from m4i_lineage_rest_api.app import flask_app, init_config


@pytest.fixture(scope="session", autouse=True)
def _init_config() -> None:
    init_config()


@pytest.fixture(scope="session", autouse=True)
def _require_atlas_for_e2e() -> None:
    atlas_url = "http://localhost:21000"
    parsed = urlparse(atlas_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 21000

    try:
        with socket.create_connection((host, port), timeout=1):
            pass
    except OSError:
        pytest.skip(f"Skipping e2e tests: Atlas is not reachable at {atlas_url}.", allow_module_level=True)


@pytest.fixture(scope="session", autouse=True)
def _bypass_auth_for_e2e() -> Generator[None, None, None]:
    """Bypass JWT verification in e2e tests to preserve existing unauthenticated test flows."""
    import importlib

    from _pytest.monkeypatch import MonkeyPatch

    monkeypatch = MonkeyPatch()
    requires_auth_module = importlib.import_module("m4i_backend_core.auth.requires_auth")

    monkeypatch.setattr(requires_auth_module, "get_token_auth_header", lambda: "e2e-test-token")
    monkeypatch.setattr(requires_auth_module, "AUTH_PUBLIC_KEY", "e2e-test-public-key")
    monkeypatch.setattr(requires_auth_module, "AUTH_ISSUER", "https://e2e.local/")
    monkeypatch.setattr(requires_auth_module.jwt, "decode", lambda *args, **kwargs: {"sub": "e2e-test-user"})

    yield

    monkeypatch.undo()


@pytest.fixture
def client():
    app_flask = flask_app()
    app_flask.initialize_app()
    app_flask.app.config["TESTING"] = True
    with app_flask.app.test_client() as client:
        yield client
    # END client


@pytest.fixture
def check_made():
    async def _check_made(entity_qn: str, entity_type: str):
        entity = await get_entity_by_qualified_name(qualified_name=entity_qn, type_name=entity_type)
        assert entity.type_name == entity_type  # type: ignore[reportGeneralTypeIssues]
        assert entity.attributes.unmapped_attributes["qualifiedName"] == entity_qn  # type: ignore[reportGeneralTypeIssues]
        guid = entity.guid  # type: ignore[reportGeneralTypeIssues]
        assert guid is not None

        await get_entities_by_attribute.cache.clear()  # type: ignore[reportGeneralTypeIssues]
        return guid

    # END ASYNC check_made
    return _check_made


# END check_made


@pytest.fixture
def cleanup():
    async def _cleanup(guid: str, entity_qn: str, entity_type: str):
        await delete_entity_soft(guid)

        await delete_entity_hard([guid])

        object_ = await get_entity_by_qualified_name(qualified_name=entity_qn, type_name=entity_type)
        assert object_ is None
        await get_entities_by_attribute.cache.clear()  # type: ignore[reportGeneralTypeIssues]

    # END ASYNC cleanup
    return _cleanup


# END cleanup
