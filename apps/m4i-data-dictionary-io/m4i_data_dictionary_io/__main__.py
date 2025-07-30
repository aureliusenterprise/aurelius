import asyncio
import os

from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient
from confluent_kafka.schema_registry import SchemaRegistryClient
from m4i_atlas_core import (
    AtlasPerson,
    BusinessCollection,
    BusinessDataAttribute,
    BusinessDataDomain,
    BusinessDataEntity,
    BusinessDataQuality,
    BusinessDataset,
    BusinessField,
    BusinessSource,
    BusinessSystem,
    ConfigStore,
    GenericProcess,
    get_keycloak_token,
    register_atlas_entity_types,
)

from m4i_data_dictionary_io import create_from_excel, excel_parser_configs
from m4i_data_dictionary_io.sources.kafka.create_from_kafka import create_from_kafka

config = {
    "atlas.server.url": os.getenv("ATLAS_SERVER_URL"),
    "keycloak.client.id": os.environ.get("KEYCLOAK_CLIENT_ID", "m4i_atlas"),
    "keycloak.credentials.username": os.environ.get("KEYCLOAK_USERNAME"),
    "keycloak.credentials.password": os.environ.get("KEYCLOAK_ATLAS_ADMIN_PASSWORD"),
    "keycloak.realm.name": os.environ.get("KEYCLOAK_REALM_NAME", "m4i"),
    "keycloak.client.secret.key": os.environ.get("KEYCLOAK_CLIENT_SECRET_KEY"),
    "keycloak.server.url": os.environ.get("KEYCLOAK_SERVER_URL"),
    "data.dictionary.path": os.getenv("DATA_DICTIONARY_PATH"),
    "validate_qualified_name": os.getenv("VALIDATE_QUALIFIED_NAME", False),
    "source": os.getenv("SOURCE", "excel"),
    "bootstrap_servers": os.getenv("BOOTSTRAP_SERVERS"),
    "schema_registry_url": os.getenv("SCHEMA_REGISTRY_URL"),
    "consumer_group_id_prefix": os.getenv(
        "CONSUMER_GROUP_ID_PREFIX", "check-format-group"
    ),
    "system_name": os.getenv("SYSTEM_NAME", "Kafka Broker"),
    "system_qualified_name": os.getenv("SYSTEM_QUALIFIED_NAME", "kafka-broker"),
    "collection_name": os.getenv("COLLECTION_NAME", "Default Cluster"),
    "collection_qualified_name": os.getenv(
        "COLLECTION_QUALIFIED_NAME", "kafka-broker--default-cluster"
    ),
}

store = ConfigStore.get_instance()
store.load(config)

access_token = get_keycloak_token()

atlas_entity_types = {
    "m4i_source": BusinessSource,
    "m4i_person": AtlasPerson,
    "m4i_data_domain": BusinessDataDomain,
    "m4i_data_entity": BusinessDataEntity,
    "m4i_data_attribute": BusinessDataAttribute,
    "m4i_field": BusinessField,
    "m4i_dataset": BusinessDataset,
    "m4i_collection": BusinessCollection,
    "m4i_system": BusinessSystem,
    "m4i_data_quality": BusinessDataQuality,
    "m4i_generic_process": GenericProcess,
}

register_atlas_entity_types(atlas_entity_types)


read_mode = store.get("source", default="excel")

if read_mode == "excel":
    asyncio.run(create_from_excel(*excel_parser_configs, access_token=access_token))
elif read_mode == "kafka":
    admin_client = AdminClient(
        {
            "bootstrap.servers": store.get("bootstrap_servers"),
        }
    )

    consumer = Consumer(
        {
            "bootstrap.servers": store.get("bootstrap_servers"),
            "group.id": f"{store.get('consumer_group_id_prefix', 'data-dictionary-io')}-group",
            "auto.offset.reset": "earliest",
        }
    )

    schema_registry_client = (
        SchemaRegistryClient(
            {
                "url": schema_registry_url,
            }
        )
        if (schema_registry_url := store.get("schema_registry_url"))
        else None
    )

    asyncio.run(
        create_from_kafka(
            admin_client=admin_client,
            consumer=consumer,
            schema_registry_client=schema_registry_client,
            access_token=access_token,
            system_name=store.get("system_name"),
        )
    )
