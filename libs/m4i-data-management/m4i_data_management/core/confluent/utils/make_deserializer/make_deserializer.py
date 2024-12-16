from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka.serialization import (SerializationContext,
                                           StringDeserializer)

from ..make_schema_registry_client import make_schema_registry_client


def make_deserializer(
    schema_id: str = None,
    schema_type: str = "string",
    schema_registry_client: SchemaRegistryClient = None,
    from_dict=None
) -> SerializationContext:
    """
    Makes an deserializer for the given `schema type` and the given `schema_id`
    """

    if schema_id is None or schema_type == "string":
        return StringDeserializer("utf-8")
    # END IF

    if not schema_registry_client:
        schema_registry_client = make_schema_registry_client()
    # END IF

    schema = schema_registry_client.get_schema(schema_id)

    deserializers = {
        "avro": lambda: AvroDeserializer(
            schema_registry_client=schema_registry_client,
            schema_str=schema.schema_str,
            from_dict=from_dict
        ),
        "json": lambda: JSONDeserializer(
            schema_str=schema.schema_str,
            from_dict=from_dict
        ),
        "string": lambda: StringDeserializer("utf-8")
    }

    deserializer_factory = deserializers.get(
        schema_type,
        deserializers["string"]
    )

    return deserializer_factory()
# END make_deserializer
