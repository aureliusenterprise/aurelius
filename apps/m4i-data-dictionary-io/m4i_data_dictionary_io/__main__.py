import asyncio
import os

from m4i_atlas_core import (ConfigStore, register_atlas_entity_types, get_keycloak_token,
                            AtlasPerson, BusinessDataDomain, BusinessDataEntity, BusinessDataAttribute, BusinessField,
                            BusinessDataset, BusinessCollection, BusinessSystem, BusinessSource, BusinessDataQuality, GenericProcess
                            )

from m4i_data_dictionary_io import (create_from_excel, excel_parser_configs)
from m4i_data_dictionary_io.sources.kafka.create_from_kafka import create_from_kafka

config = {
    "atlas.server.url": os.getenv("ATLAS_SERVER_URL"),
    "keycloak.client.id": os.environ.get("KEYCLOAK_CLIENT_ID"),
    "keycloak.credentials.username": os.environ.get("KEYCLOAK_USERNAME"),
    "keycloak.credentials.password": os.environ.get("KEYCLOAK_ATLAS_ADMIN_PASSWORD"),
    "keycloak.realm.name": os.environ.get("KEYCLOAK_REALM_NAME"),
    "keycloak.client.secret.key": os.environ.get("KEYCLOAK_CLIENT_SECRET_KEY"),
    "keycloak.server.url": os.environ.get("KEYCLOAK_SERVER_URL"),
    "data.dictionary.path": os.getenv("DATA_DICTIONARY_PATH"),
    "validate_qualified_name": os.getenv("VALIDATE_QUALIFIED_NAME", False),
    "source": os.getenv("SOURCE", "excel"),
    "bootstrap_servers": os.getenv("BOOTSTRAP_SERVERS", "localhost:9092"),
    "schema_registry_url": os.getenv("SCHEMA_REGISTRY_URL"),
    "consumer_group_id_prefix": os.getenv("CONSUMER_GROUP_ID_PREFIX", 'check-format-group'),
    "system.name": os.getenv("SYSTEM_NAME", "Kafka Broker"),
    "system.qualified_name": os.getenv("SYSTEM_QUALIFIED_NAME", "kafka-broker"),
    "collection.name": os.getenv("COLLECTION_NAME", "Default Cluster"),
    "collection.qualified_name": os.getenv("COLLECTION_QUALIFIED_NAME", "kafka-broker--default-cluster"),
}

store = ConfigStore.get_instance()
store.load(config)

access_token=get_keycloak_token()

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
    "m4i_generic_process": GenericProcess
}

register_atlas_entity_types(atlas_entity_types)


read_mode = store.get("source", default=True)

if read_mode == "excel":
  asyncio.run(create_from_excel(*excel_parser_configs, access_token=access_token))
elif read_mode == "kafka":
  asyncio.run(create_from_kafka(access_token=access_token, store=store))
