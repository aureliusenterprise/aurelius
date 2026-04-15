from collections.abc import Generator

import pytest
from aurelius_fastapi_example.providers import db


@pytest.fixture(autouse=True)
def clear_database_cache() -> Generator[None]:
    """Clear the cached database engine before and after each test."""
    db.database.cache_clear()
    yield
    db.database.cache_clear()
