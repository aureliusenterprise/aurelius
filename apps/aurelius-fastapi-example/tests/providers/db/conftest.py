from collections.abc import Generator

import pytest
from aurelius_fastapi_example.providers import EntityNotificationBroadcaster, db, get_broadcaster


@pytest.fixture(autouse=True)
def clear_database_cache() -> Generator[None]:
    """Clear the cached database engine before and after each test."""
    db.database.cache_clear()
    yield
    db.database.cache_clear()


@pytest.fixture()
def broadcaster(db_settings: db.Settings) -> Generator[EntityNotificationBroadcaster]:
    """Provide a started Broadcaster instance for tests that need it."""
    get_broadcaster.cache_clear()

    broadcaster = get_broadcaster(settings=db_settings)

    with broadcaster:
        yield broadcaster

    get_broadcaster.cache_clear()
