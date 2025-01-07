from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import (SerializationContext,
                                           StringSerializer)

from ..make_schema_registry_client import make_schema_registry_client


def make_serializer(schema_id: str, schema_type: str = "string", schema_registry_client: SchemaRegistryClient = None, to_dict=None, conf=None) -> SerializationContext:
    """
    Makes a serializer for the given `schema_type` and the given `schema_id`
    """

    if schema_id is None or schema_type == "string":
        return StringSerializer("utf-8")
    # END IF

    if not schema_registry_client:
        schema_registry_client = make_schema_registry_client()
    # END IF

    schema = schema_registry_client.get_schema(schema_id)

    serializers = {
        "avro": lambda: AvroSerializer(
            schema_str=schema.schema_str,
            schema_registry_client=schema_registry_client,
            to_dict=to_dict,
            conf=conf
        ),
        "json": lambda: JSONSerializer(
            schema_str=schema.schema_str,
            schema_registry_client=schema_registry_client,
            to_dict=to_dict,
            conf=conf
        ),
        "string": lambda: StringSerializer("utf-8")
    }

    serializer_factory = serializers.get(schema_type, serializers["string"])

    return serializer_factory()
# END make_serializer
