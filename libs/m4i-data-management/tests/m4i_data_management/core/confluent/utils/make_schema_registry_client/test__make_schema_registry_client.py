import importlib
from unittest.mock import MagicMock, patch

from m4i_data_management.core.confluent.utils.make_schema_registry_client.make_schema_registry_client import (
    make_schema_registry_client,
)

# Use importlib to load the actual module file (not through __init__.py which exports function)
sr_module = importlib.import_module(
    "m4i_data_management.core.confluent.utils.make_schema_registry_client.make_schema_registry_client"
)


def test__make_schema_registry_client():
    mock_config = MagicMock()
    mock_config.get_many.return_value = ("http://localhost:8081", "key", "secret")

    with patch.object(sr_module, "config", mock_config):
        client = make_schema_registry_client()

    assert client is not None


# END test__make_schema_registry_client
