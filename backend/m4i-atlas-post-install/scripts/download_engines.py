import argparse
import json
from pathlib import Path

from elastic_enterprise_search import AppSearch

from m4i_atlas_post_install.app_search_engine_setup import engines
from m4i_atlas_post_install.get_all_documents import get_all_documents
from m4i_atlas_post_install.get_enterprise_search_key import get_enterprise_search_key


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", "-a", required=True, help="App Search url", type=str)
    parser.add_argument(
        "--username", "-u", default="elastic", help="ES username", type=str
    )
    parser.add_argument("--password", "-p", required=True, help="ES password", type=str)
    parser.add_argument(
        "--target-dir",
        default=Path("data"),
        type=Path,
        help="Target directory for the output",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    app_search_api_key = get_enterprise_search_key(
        args.url, args.username, args.password
    )

    app_search_client = AppSearch(args.url, bearer_auth=app_search_api_key)
    for engine in engines:
        documents = get_all_documents(app_search_client, engine["name"])
        with open(args.target_dir / f"{engine['name']}.json", "w") as json_file:
            json.dump(documents, json_file, indent=4)
        print(f"{engine['name']} downloaded")


if __name__ == "__main__":
    main()
