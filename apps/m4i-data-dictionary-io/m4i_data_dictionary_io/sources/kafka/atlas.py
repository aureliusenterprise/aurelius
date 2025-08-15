from typing import Union

from m4i_data_dictionary_io.entities.json import (
    Collection,
    DataField,
    Dataset,
    System,
    get_qualified_name,
)


def build_system(name: str) -> System:
    """Build a System instance with the provided name."""
    return System.from_dict(
        {
            "name": name,
            "qualifiedName": get_qualified_name(name),
        }
    )


def build_collection(
    name: str,
    system_qualified_name: str,
) -> Collection:
    """Build a Collection instance with the provided name and system qualified name."""
    return Collection.from_dict(
        {
            "name": name,
            "system": system_qualified_name,
            "qualifiedName": f"{system_qualified_name}--{get_qualified_name(name)}",
        }
    )


def build_dataset(topic: str, collection_qualified_name: str) -> Dataset:
    """Process each topic by creating dataset and field instances."""
    dataset_qualified_name = (
        collection_qualified_name + "--" + get_qualified_name(topic)
    )

    return Dataset.from_dict(
        {
            "name": topic,
            "collection": collection_qualified_name,
            "qualifiedName": dataset_qualified_name,
        }
    )


def build_field(
    name: str,
    dataset_qualified_name: str,
    type_name: str,
    *,
    definition: Union[str, None] = None,
    parent_field: Union[str, None] = None
) -> DataField:
    """Build a DataField instance with the provided parameters."""
    return DataField.from_dict(
        {
            "name": name,
            "dataset": dataset_qualified_name,
            "definition": definition,
            "qualifiedName": f"{parent_field if parent_field else dataset_qualified_name}--{get_qualified_name(name)}",
            "fieldType": type_name,
            "parentField": parent_field,
        }
    )
