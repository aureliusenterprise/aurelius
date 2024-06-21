from pathlib import Path
from typing import Any, MutableMapping
from elastic_enterprise_search import AppSearch
from propagate_quality import index_documents, load_documents, parse_args
from update_gov_index import get_enterprise_api_private_key, index_all_documents


def propagate_relationship(
    field_document: MutableMapping[str, Any],
    data_attribute_document: MutableMapping[str, Any],
    atlas_dev_index: MutableMapping[str, Any],
):
    for data_entity_guid in data_attribute_document["deriveddataentityguid"]:
        for dataset_guid in field_document["deriveddatasetguid"]:
            if (
                dataset_guid
                not in atlas_dev_index[data_entity_guid]["deriveddatasetguid"]
            ):
                atlas_dev_index[data_entity_guid]["deriveddatasetguid"].append(
                    dataset_guid
                )
                atlas_dev_index[data_entity_guid]["deriveddataset"].append(
                    atlas_dev_index[dataset_guid]["name"]
                )
            if (
                data_entity_guid
                not in atlas_dev_index[dataset_guid]["deriveddataentityguid"]
            ):
                atlas_dev_index[dataset_guid]["deriveddataentityguid"].append(
                    data_entity_guid
                )
                atlas_dev_index[dataset_guid]["deriveddataentity"].append(
                    atlas_dev_index[data_entity_guid]["name"]
                )


def connect_datasets_with_entities(atlas_dev_index: MutableMapping[str, Any]):
    for document in atlas_dev_index.values():
        if document["typename"] == "m4i_field":
            for attribute_guid in document["deriveddataattributeguid"]:
                data_attribute_document = atlas_dev_index[attribute_guid]
                propagate_relationship(
                    field_document=document,
                    data_attribute_document=data_attribute_document,
                    atlas_dev_index=atlas_dev_index,
                )


def main():
    args = parse_args()
    app_search_api_key = get_enterprise_api_private_key(
        args.url, args.username, args.password
    )
    app_search_client = AppSearch(args.url, bearer_auth=app_search_api_key)
    atlas_dev_documents = load_documents(Path("data/atlas-dev.json"))
    atlas_dev_index = index_documents(atlas_dev_documents)
    connect_datasets_with_entities(atlas_dev_index)
    index_all_documents(
        app_search_client=app_search_client,
        engine_name="atlas-dev",
        documents=list(atlas_dev_index.values()),
    )


if __name__ == "__main__":
    main()
