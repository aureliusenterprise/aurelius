#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Any, List, Mapping, MutableMapping

from elastic_enterprise_search import AppSearch
from m4i_atlas_post_install import (
    cleanup,
    drop_non_entities,
    extract,
    get_all_documents,
    get_enterprise_search_key,
    index_all_documents,
    index_entities,
    update_types,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", "-e", required=True, help="Export zip", type=Path)
    parser.add_argument("--url", "-a", required=True, help="App Search url", type=str)
    parser.add_argument(
        "--username", "-u", default="elastic", help="ES username", type=str
    )
    parser.add_argument("--password", "-p", required=True, help="ES password", type=str)
    return parser.parse_args()


def update_types_in_documents(
    documents: List[MutableMapping[str, Any]],
) -> List[MutableMapping[str, Any]]:
    return [update_types(document) for document in documents]


def index_by_qualified_name(entities: Mapping[str, Any]) -> Mapping[str, Any]:
    qualified_name_index = {}
    for value in entities.values():
        qualified_name = value["entity"]["attributes"].get("qualifiedName")
        if not qualified_name:
            continue
        qualified_name_index[qualified_name] = value["entity"]["guid"]
    return qualified_name_index


def substitute_quality_guid(
    documents: List[MutableMapping[str, Any]], qualified_name_index: Mapping[str, Any]
) -> None:
    for document in documents:
        qualified_name = document["qualityqualifiedname"]
        correct_guid = qualified_name_index[qualified_name]
        document["guid"] = correct_guid


def main() -> None:
    args = parse_args()
    app_search_api_key = get_enterprise_search_key(
        args.url, args.username, args.password
    )

    app_search_client = AppSearch(args.url, bearer_auth=app_search_api_key)
    engine_name = "atlas-dev-gov-quality"
    documents = get_all_documents(app_search_client, engine_name)
    extracted = extract(args.export)
    entities = index_entities(extracted)
    drop_non_entities(entities)
    qualified_name_index = index_by_qualified_name(entities)
    documents = update_types_in_documents(documents)
    substitute_quality_guid(documents, qualified_name_index)
    index_all_documents(
        app_search_client=app_search_client,
        engine_name=engine_name,
        documents=list(documents),
    )
    cleanup(extracted)


if __name__ == "__main__":
    main()
