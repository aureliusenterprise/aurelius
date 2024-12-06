from confluent_kafka.schema_registry import SchemaRegistryClient
from m4i_atlas_core.config.config_store import ConfigStore

config = ConfigStore.get_instance()


def make_schema_registry_client() -> SchemaRegistryClient:
    """
    Returns a connection to Confluent Kafka Schema Registry in the Data Management Platform that can be used to define and retrieve schema definitions.
    """

    url, key, secret = config.get_many(
        "confluent.schema.registry.url",
        "confluent.schema.registry.key",
        "confluent.schema.registry.secret"
    )

    basic_auth = f"{key}:{secret}"

    schema_registry_config = {
        "url": url,
        "basic.auth.user.info": basic_auth
    }

    return SchemaRegistryClient(schema_registry_config)
# END make_schema_registry_client
