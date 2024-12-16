import pytest
from confluent_kafka.schema_registry import SchemaRegistryError

from .make_serializer import make_serializer


def test__make_avro_serializer_for_key_schema():
    schama_id = "100021"  # avro--test--key

    serializer = make_serializer(schama_id, schema_type="avro")

    assert serializer._schema_name == 'avro.test.key'
# END test__make_avro_serializer


def test__make_avro_serializer_for_value_schema():
    schema_id = "100022"  # avro--test--value

    serializer = make_serializer(schema_id, schema_type="avro")

    assert serializer._schema_name == 'avro.test.value'
# END test__make_avro_serializer


def test__make_avro_serializer_for_non_existing_schema():
    schema_name = "non_existing"  # avro--test--value

    with pytest.raises(SchemaRegistryError):
        make_serializer(schema_name, schema_type="avro")
    # END WITH
# END test__make_avro_serializer
