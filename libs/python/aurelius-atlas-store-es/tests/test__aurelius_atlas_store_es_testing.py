import pytest
from aurelius_atlas_store_es.testing import DEFAULT_IMAGE, container_environment


@pytest.mark.covers("aurelius_atlas_store_es.testing.container_environment")
def test__container_environment_enables_security() -> None:
    """Test nodes run with security enabled and the given password (DD-003)."""
    environment = container_environment("pw")

    assert environment["xpack.security.enabled"] == "true"
    assert environment["ELASTIC_PASSWORD"] == "pw"  # noqa: S105 - a test value, not a secret
    assert environment["discovery.type"] == "single-node"


@pytest.mark.covers("aurelius_atlas_store_es.testing.elasticsearch_node")
def test__default_image_is_elasticsearch_9() -> None:
    """Component tests run the same major version the system targets."""
    assert DEFAULT_IMAGE.startswith("docker.elastic.co/elasticsearch/elasticsearch:9.")
