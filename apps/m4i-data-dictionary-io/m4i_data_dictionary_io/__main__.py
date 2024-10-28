import asyncio
import os

from m4i_atlas_core import (ConfigStore, register_atlas_entity_types,
                            AtlasPerson, BusinessDataDomain, BusinessDataEntity, BusinessDataAttribute, BusinessField,
                            BusinessDataset, BusinessCollection, BusinessSystem, BusinessSource, BusinessDataQuality, GenericProcess
                            )

from m4i_data_dictionary_io import (create_from_excel, excel_parser_configs)

config = {
    "atlas.credentials.username": os.getenv("KEYCLOAK_ATLAS_USER_USERNAME"),
    "atlas.credentials.password": os.getenv("KEYCLOAK_ATLAS_USER_PASSWORD"),
    "atlas.server.url": os.getenv("ATLAS_SERVER_URL"),
    "data.dictionary.path": os.getenv("DATA_DICTIONARY_PATH"),
    "validate_qualified_name": os.getenv("VALIDATE_QUALIFIED_NAME", False),
    "keycloak.client.id": os.environ.get("KEYCLOAK_CLIENT_ID"),
    "keycloak.credentials.username": os.environ.get("KEYCLOAK_USERNAME"),
    "keycloak.credentials.password": os.environ.get("KEYCLOAK_ATLAS_ADMIN_PASSWORD"),
    "keycloak.realm.name": os.environ.get("KEYCLOAK_REALM_NAME"),
    "keycloak.client.secret.key": os.environ.get("KEYCLOAK_CLIENT_SECRET_KEY"),
    "keycloak.server.url": os.environ.get("KEYCLOAK_SERVER_URL"),
}

store = ConfigStore.get_instance()
store.load(config)

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

asyncio.run(create_from_excel(*excel_parser_configs))

