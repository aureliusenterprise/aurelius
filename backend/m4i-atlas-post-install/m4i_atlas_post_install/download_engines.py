import json
from pathlib import Path
from elastic_enterprise_search import AppSearch
from update_gov_index import get_all_documents, get_enterprise_api_private_key
import argparse

from app_search_engine_setup import engines


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", "-a", required=True, help="App Search url", type=str)
    parser.add_argument(
        "--username", "-u", default="elastic", help="ES username", type=str
    )
    parser.add_argument("--password", "-p", required=True, help="ES password", type=str)
    return parser.parse_args()


def main():
    args = parse_args()
    app_search_api_key = get_enterprise_api_private_key(
        args.url, args.username, args.password
    )

    app_search_client = AppSearch(args.url, bearer_auth=app_search_api_key)
    for engine in engines:
        documents = get_all_documents(app_search_client, engine["name"])
        with open(Path("data") / f"{engine['name']}.json", "w") as json_file:
            json.dump(documents, json_file, indent=4)


if __name__ == "__main__":
    main()
