"""Component tests: the library against a real Elasticsearch 9 node (needs Docker)."""

import pytest
from aurelius_atlas_store_es.client import StoreUnavailableError, check_health, create_client
from aurelius_atlas_store_es.indices import index_name
from aurelius_atlas_store_es.settings import ElasticsearchSettings
from pydantic import SecretStr

pytestmark = pytest.mark.component


@pytest.mark.covers("aurelius_atlas_store_es.client.check_health", rules=["ESI-06"])
@pytest.mark.covers("aurelius_atlas_store_es.testing.elasticsearch_node")
async def test__component_health_of_real_node(live_settings: ElasticsearchSettings) -> None:
    """A fresh single node reports itself available with one node."""
    client = create_client(live_settings)
    try:
        health = await check_health(client)
    finally:
        await client.close()

    assert health.is_available
    assert health.number_of_nodes == 1


@pytest.mark.covers("aurelius_atlas_store_es.client.check_health", rules=["ESI-08"])
async def test__component_wrong_password_is_unavailable(live_settings: ElasticsearchSettings) -> None:
    """Security is on: a wrong password is refused with HTTP 401."""
    wrong = live_settings.model_copy(update={"password": SecretStr("wrong")})
    client = create_client(wrong)
    try:
        with pytest.raises(StoreUnavailableError, match=r"HTTP 401"):
            await check_health(client)
    finally:
        await client.close()


@pytest.mark.covers("aurelius_atlas_store_es.indices.index_name", rules=["ESI-04"])
async def test__component_index_names_are_accepted_by_elasticsearch(live_settings: ElasticsearchSettings) -> None:
    """Names produced by index_name are valid Elasticsearch index names."""
    client = create_client(live_settings)
    name = index_name(live_settings, "probe_kind")
    try:
        await client.indices.create(index=name)
        assert (await client.indices.exists(index=name)).body
        await client.indices.delete(index=name)
    finally:
        await client.close()
