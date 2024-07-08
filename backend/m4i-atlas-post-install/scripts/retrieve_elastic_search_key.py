import os
import requests
from requests.auth import HTTPBasicAuth

enterprise_search_url = os.getenv("ENTERPRISE_SEARCH_URL")
elastic_username = os.getenv("ELASTIC_USERNAME", "elastic")
elastic_password = os.getenv("ELASTIC_PASSWORD", "elastic")

UPLOAD_DATA = os.getenv("UPLOAD_DATA", False)


def get_enterprise_api_search_key(
    enterprise_search_url, elastic_username, elastic_password
):
    key_response = requests.get(
        f"{enterprise_search_url}api/as/v1/credentials/search-key",
        auth=HTTPBasicAuth(elastic_username, elastic_password),
    )
    key_info = key_response.json()
    return key_info["key"]

def main():
    app_search_api_key = get_enterprise_api_search_key(
        enterprise_search_url, elastic_username, elastic_password
    )

    print(app_search_api_key)

if __name__ == "__main__":
    main()
