import pytest
from aurelius_atlas_store_es.indices import index_name
from aurelius_atlas_store_es.settings import ElasticsearchSettings


@pytest.mark.covers("aurelius_atlas_store_es.indices.index_name", rules=["ESI-04"])
def test__index_name_joins_prefix_and_kind(settings: ElasticsearchSettings) -> None:
    """Index names are <prefix>-<kind>."""
    assert index_name(settings, "typedefs") == "unit-typedefs"
    assert index_name(settings, "entity_audit") == "unit-entity_audit"


@pytest.mark.covers("aurelius_atlas_store_es.indices.index_name", rules=["ESI-04"])
@pytest.mark.parametrize("kind", ["", "Entities", "1st", "a-b", "a b", "x" * 65])
def test__index_name_rejects_invalid_kind(settings: ElasticsearchSettings, kind: str) -> None:
    """Kinds are lower-case letters, digits and underscores, starting with a letter."""
    with pytest.raises(ValueError, match="invalid index kind"):
        index_name(settings, kind)
