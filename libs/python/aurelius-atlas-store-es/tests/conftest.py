from collections.abc import Iterator

import pytest
from aurelius_atlas_store_es.settings import ElasticsearchSettings
from pydantic import SecretStr


@pytest.fixture
def settings() -> ElasticsearchSettings:
    """Return settings for a cluster that is never contacted."""
    return ElasticsearchSettings(password=SecretStr("secret"), index_prefix="unit")


@pytest.fixture(scope="session")
def live_settings() -> Iterator[ElasticsearchSettings]:
    """Start one Elasticsearch node for all component tests in the session."""
    from aurelius_atlas_store_es.testing import elasticsearch_node  # noqa: PLC0415 - needs Docker

    with elasticsearch_node(index_prefix="component") as live:
        yield live
