import requests
import argparse
from urlpath import URL


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token", "-t", required=True, help="Atlas access token", type=str
    )
    parser.add_argument(
        "--base-url",
        "-u",
        default="https://aureliusdev.westeurope.cloudapp.azure.com/demo/atlas2/api/atlas",
        help="Apache Atlas base url",
        type=URL,
    )
    parser.add_argument(
        "--output", "-o", default="out.zip", help="Output zip file", type=str
    )
    parser.add_argument(
        "--import-data",
        "-i",
        action="store_true",
        help="When passed, the script will perform import of data (export by default)",
    )
    return parser.parse_args()


def get_entity_types(base_url, base_headers={}):
    url = base_url / "v2/types/typedefs"
    response = requests.get(url.as_uri(), headers=base_headers)
    data = response.json()
    return [
        entity["name"]
        for entity in data["entityDefs"]
        if entity["category"] == "ENTITY"
    ]


def export(entity_types, base_url, output, base_headers={}):
    headers = base_headers.copy()
    body = {"itemsToExport": []}
    for entity in entity_types:
        body["itemsToExport"].append(
            {"typeName": entity, "uniqueAttributes": {"qualifiedName": ".*"}}
        )

    body["options"] = {"matchType": "matches"}
    headers["Content-Type"] = "application/json"
    headers["Cache-Control"] = "no-cache"
    url = base_url / "admin/export"

    response = requests.post(url.as_uri(), json=body, headers=headers)
    with open(output, "wb") as handler:
        handler.write(response.content)


def import_data(base_url, export_output, base_headers):
    headers = base_headers.copy()

    headers["Cache-Control"] = "no-cache"
    url = base_url / "admin/import"
    files = {"data": open(export_output, "rb")}

    response = requests.post(url.as_uri(), files=files, headers=headers)
    print(str(response.content))


def main():
    args = parse_args()
    base_url = args.base_url
    headers = {"Authorization": f"Bearer {args.token}"}
    if args.import_data:
        print("Importing entities")
        import_data(base_url, args.output, headers)
    else:
        print("Getting all entity types")
        entity_types = get_entity_types(base_url, headers)
        print("Exporting entities")
        export(entity_types, base_url, args.output, headers)
    print("Done!")


if __name__ == "__main__":
    main()
