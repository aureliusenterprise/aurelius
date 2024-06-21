#!/usr/bin/env python3
from typing import Any, Mapping, MutableMapping, List
import requests
from requests.auth import HTTPBasicAuth
import argparse
from pathlib import Path

from elastic_enterprise_search import AppSearch

from export_diff import (
    drop_non_entities,
    extract,
    cleanup,
    index_entities,
    update_types,
)


def get_enterprise_api_private_key(
    enterprise_search_url: str, elastic_username: str, elastic_password: str
) -> str:
    key_response = requests.get(
        f"{enterprise_search_url}api/as/v1/credentials/private-key",
        auth=HTTPBasicAuth(elastic_username, elastic_password),
    )
    key_info = key_response.json()
    return key_info["key"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", "-e", required=True, help="Export zip", type=Path)
    parser.add_argument("--url", "-a", required=True, help="App Search url", type=str)
    parser.add_argument(
        "--username", "-u", default="elastic", help="ES username", type=str
    )
    parser.add_argument("--password", "-p", required=True, help="ES password", type=str)
    return parser.parse_args()


def get_all_documents(
    app_search_client: AppSearch, engine_name: str
) -> List[MutableMapping[str, Any]]:
    response = app_search_client.list_documents(
        engine_name=engine_name, page_size=1000, current_page=1
    )
    documents = response.raw["results"]
    for page in range(2, response.raw["meta"]["page"]["total_pages"] + 1):
        response = app_search_client.list_documents(
            engine_name=engine_name, page_size=1000, current_page=page
        )
        documents.extend(response.raw["results"])
    return documents


def index_all_documents(
    app_search_client: AppSearch,
    engine_name: str,
    documents: List[Mapping[str, Any]],
):
    for i in range(0, len(documents), 100):
        app_search_client.index_documents(
            engine_name=engine_name, documents=documents[i : i + 100]
        )


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
    app_search_api_key = get_enterprise_api_private_key(
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
        documents=list[Mapping[str, Any]](documents),
    )
    cleanup(extracted)


if __name__ == "__main__":
    main()
