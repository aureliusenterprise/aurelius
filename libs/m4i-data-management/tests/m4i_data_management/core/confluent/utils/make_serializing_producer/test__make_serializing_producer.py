import importlib
from unittest.mock import MagicMock, patch

from m4i_data_management.core.confluent.utils.make_serializing_producer.make_serializing_producer import (
    make_serializing_producer,
)

# Use importlib to load the actual module file (not through __init__.py which exports function)
producer_module = importlib.import_module(
    "m4i_data_management.core.confluent.utils.make_serializing_producer.make_serializing_producer"
)


def test__make_serializing_producer():
    mock_config = MagicMock()
    mock_config.get_many.return_value = ("http://localhost:8081", "key", "secret")

    mock_sr_client = MagicMock()
    mock_sr_client.get_schema.return_value.schema_str = (
        '{"type": "record", "name": "key", "namespace": "avro.test",'
        ' "fields": [{"name": "name", "type": "string"}]}'
    )

    # Patch the module's config and make_schema_registry_client directly on the module object
    with patch.object(producer_module, "config", mock_config):
        with patch.object(producer_module, "make_schema_registry_client", return_value=mock_sr_client):
            producer = make_serializing_producer(
                key_schema_id="100021",  # avro--test--key
                value_schema_id="100022",  # avro--test--value
            )

            assert producer is not None


# END test__make_serializing_producer


def test__make_serializing_producer_can_push_message():
    mock_config = MagicMock()
    mock_config.get_many.return_value = ("http://localhost:8081", "key", "secret")

    mock_sr_client = MagicMock()
    mock_sr_client.get_schema.return_value.schema_str = (
        '{"type": "record", "name": "test", "namespace": "avro.test",'
        ' "fields": [{"name": "name", "type": "string"}]}'
    )

    mock_producer_class = MagicMock()

    # Patch the module's config, make_schema_registry_client, and SerializingProducer
    with patch.object(producer_module, "config", mock_config):
        with patch.object(producer_module, "make_schema_registry_client", return_value=mock_sr_client):
            with patch.object(producer_module, "SerializingProducer", mock_producer_class):
                make_serializing_producer(key_schema_id="100021", value_schema_id="100022")

                # Verify SerializingProducer was called with proper config
                assert mock_producer_class.called
                call_kwargs = (
                    mock_producer_class.call_args[1]
                    if mock_producer_class.call_args[1]
                    else mock_producer_class.call_args[0][0]
                )
                assert call_kwargs["bootstrap.servers"] == "http://localhost:8081"
                assert call_kwargs["sasl.mechanisms"] == "PLAIN"
                assert call_kwargs["security.protocol"] == "SASL_SSL"


# END test__make_serializing_producer_can_push_message
