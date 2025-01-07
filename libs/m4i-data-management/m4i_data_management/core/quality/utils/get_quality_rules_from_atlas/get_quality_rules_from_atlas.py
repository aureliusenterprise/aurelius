import asyncio
from typing import List, Optional

from m4i_atlas_core import (BusinessDataQuality, BusinessDataset,
                            BusinessField, ConfigStore,
                            get_entities_by_attribute, get_entity_by_guid)
from pandas import DataFrame


def atlas_get_quality_rules_dataframe(data: List[BusinessDataQuality] = []):
    """
    :return:  Empty DataFrame with column names as expected for data quality rules based of the data dictionary
    """
    columns_names = [
        "id",
        "data_field_qualified_name",
        "business_rule_description",
        "data_quality_rule_description",
        "data_quality_rule_dimension",
        "filter",
        "expression",
        "active",
        "expression_version"
    ]
    data_details = [
        get_data_quality_rule_details(rule)
        for rule in data
    ]
    data = DataFrame(data_details, columns=columns_names)

    return data
# END atlas_get_quality_rules_dataframe


def get_data_quality_rule_details(quality_rule_entity: BusinessDataQuality) -> dict:
    """
     Create attribute dictionary for the given data-quality-rule
    :param quality_rule_entity: The data quality rule entity
    :return: a dictionary with required attributes describing data quality rule
    """
    rule_attributes = quality_rule_entity.attributes

    rule = {
        "id": rule_attributes.id,
        "data_field_qualified_name": rule_attributes.qualified_name,
        "business_rule_description": rule_attributes.business_rule_description,
        "data_quality_rule_description": rule_attributes.rule_description,
        "data_quality_rule_dimension": rule_attributes.quality_dimension,
        "filter": rule_attributes.filter_required,
        "expression": rule_attributes.expression,
        "active": rule_attributes.active,
        "expression_version": rule_attributes.expression_version
    }

    return rule
# END get_data_quality_rule_details


async def get_dataset(dataset_name: str, access_token: str, dataset_atlas_guid: Optional[str] = None) -> BusinessDataset:

    if dataset_atlas_guid is None:

        search_results = await get_entities_by_attribute(
            attribute_name='name',
            attribute_value=dataset_name,
            type_name='m4i_dataset',
            access_token=access_token
        )

        dataset_entity_headers = search_results.entities

        if len(dataset_entity_headers) > 1:
            print(
                f"More then one dataset with the name '{dataset_name}' was found, please provide the atlas guid of the dataset as well.")
            exit(1)
        if len(dataset_entity_headers) == 0:
            print(
                f"No dataset entity with the name '{dataset_name}' was found. Please provide the atlas guid of the dataset as well.")
            exit(1)

        dataset_atlas_guid = dataset_entity_headers[0].guid

    return await get_entity_by_guid(guid=dataset_atlas_guid, entity_type=BusinessDataset, access_token=access_token)
# END get_dataset


async def get_fields(dataset: BusinessDataset, access_token: str) -> List[BusinessField]:

    fields = [
        get_entity_by_guid(guid=field.guid, entity_type=BusinessField, access_token=access_token)
        for field in dataset.attributes.fields
    ]

    return await asyncio.gather(*fields)
# END get_fields


async def get_quality_rules(fields: List[BusinessField], access_token: str) -> List[BusinessDataQuality]:

    quality_rules = [
        get_entity_by_guid(guid=quality_rule['guid'], entity_type=BusinessDataQuality, access_token=access_token)
        for field in fields
        for quality_rule in field.relationship_attributes['dataQuality']
    ]

    return await asyncio.gather(*quality_rules)
# END get_quality_rules


async def get_quality_rules_from_atlas(dataset_name: str, dataset_atlas_guid: Optional[str] = None) -> DataFrame:
    """
    Given a dataset_name or dataset_atlas_guid gets all data quality rules associated to it and return them as a dataframe.

    To use this function the following keys need to be in the config store:
    "atlas.server.url" : REQUIRED

    "access_token" or "atlas.credentials.username" and "atlas.credentials.password" : REQUIRED
    """
    store = ConfigStore.get_instance()

    access_token = store.get('access_token', default=None)

    dataset = await get_dataset(dataset_name, access_token, dataset_atlas_guid)
    fields = await get_fields(dataset, access_token)
    quality_rules = await get_quality_rules(fields, access_token)

    return atlas_get_quality_rules_dataframe(quality_rules)
# END get_quality_rules_from_atlas
