from confluent_kafka import DeserializingConsumer
from m4i_atlas_core.config.config_store import ConfigStore

from ..make_deserializer import make_deserializer
from ..make_schema_registry_client import make_schema_registry_client

config = ConfigStore.get_instance()


def make_deserializing_consumer(
    value_schema_id: str = None,
    value_schema_type: str = 'string',
    key_schema_id: str = None,
    key_schema_type: str = 'string',
    enable_auto_commit: bool = False
) -> DeserializingConsumer:
    """
    Returns a deserializing consumer for the given `key_schema_id` and `value_schema_id`.

    You can specify the deserialization format by passing `key_schema_type` and `value_schema_type` respectively.

    If no `key_schema_id` or `value_schema_id` are given, the default `StringSerializer` is used for the respective fields.
    """

    schema_registry_client = make_schema_registry_client()

    key_deserializer = make_deserializer(
        schema_id=key_schema_id,
        schema_type=key_schema_type,
        schema_registry_client=schema_registry_client
    )

    value_deserializer = make_deserializer(
        schema_id=value_schema_id,
        schema_type=value_schema_type,
        schema_registry_client=schema_registry_client
    )

    bootstrap_server_url, group_id, username, password = config.get_many(
        "confluent.kafka.bootstrap.servers",
        "confluent.kafka.group.id",
        "confluent.auth.sasl.username",
        "confluent.auth.sasl.password"
    )

    consumer_config = {
        "auto.offset.reset": "earliest",
        "bootstrap.servers": bootstrap_server_url,
        "enable.auto.commit": enable_auto_commit,
        "group.id": group_id,
        "sasl.mechanisms": "PLAIN",
        "sasl.password": password,
        "sasl.username": username,
        "security.protocol": "SASL_SSL",
        "key.deserializer": key_deserializer,
        "value.deserializer": value_deserializer
    }

    return DeserializingConsumer(consumer_config)
# END make_deserializing_consumer
