import pytest
from unittest.mock import MagicMock
from confluent_kafka.schema_registry import SchemaRegistryError

from m4i_data_management.core.confluent.utils.make_serializer.make_serializer import make_serializer


def test__make_avro_serializer_for_key_schema():
    mock_sr_client = MagicMock()
    mock_sr_client.get_schema.return_value.schema_str = (
        '{"type": "record", "name": "key", "namespace": "avro.test", "fields": []}'
    )

    schama_id = "100021"  # avro--test--key

    serializer = make_serializer(schama_id, schema_type="avro", schema_registry_client=mock_sr_client)

    assert serializer._schema_name == "avro.test.key"


# END test__make_avro_serializer


def test__make_avro_serializer_for_value_schema():
    mock_sr_client = MagicMock()
    mock_sr_client.get_schema.return_value.schema_str = (
        '{"type": "record", "name": "value", "namespace": "avro.test", "fields": []}'
    )

    schema_id = "100022"  # avro--test--value

    serializer = make_serializer(schema_id, schema_type="avro", schema_registry_client=mock_sr_client)

    assert serializer._schema_name == "avro.test.value"


# END test__make_avro_serializer


def test__make_avro_serializer_for_non_existing_schema():
    mock_sr_client = MagicMock()
    mock_sr_client.get_schema.side_effect = SchemaRegistryError(
        http_status_code=404, error_code=40401, error_message="Schema not found"
    )

    schema_name = "non_existing"  # avro--test--value

    with pytest.raises(SchemaRegistryError):
        make_serializer(schema_name, schema_type="avro", schema_registry_client=mock_sr_client)
    # END WITH


# END test__make_avro_serializer
