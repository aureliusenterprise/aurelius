import asyncio
import os

from m4i_atlas_core import (ConfigStore, register_atlas_entity_types,
                            AtlasPerson, BusinessDataDomain, BusinessDataEntity, BusinessDataAttribute, BusinessField,
                            BusinessDataset, BusinessCollection, BusinessSystem, BusinessSource, BusinessDataQuality)

from m4i_data_dictionary_io import (create_from_excel, excel_parser_configs)

config = {
    "atlas.credentials.username": os.getenv("ATLAS_USERNAME"),
    "atlas.credentials.password": os.getenv("ATLAS_PASSWORD"),
    "atlas.server.url": os.getenv("ATLAS_SERVER_URL"),
    "data.dictionary.path": os.getenv("DATA_DICTIONARY_PATH"),
    "validate_qualified_name": os.getenv("VALIDATE_QUALIFIED_NAME", "True"),
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
    "m4i_data_quality": BusinessDataQuality
}

register_atlas_entity_types(atlas_entity_types)

asyncio.run(create_from_excel(*excel_parser_configs))

