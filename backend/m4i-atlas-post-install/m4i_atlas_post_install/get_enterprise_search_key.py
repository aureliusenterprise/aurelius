import requests
from requests.auth import HTTPBasicAuth


def get_enterprise_search_key(
    enterprise_search_url: str, elastic_username: str, elastic_password: str
) -> str:
    key_response = requests.get(
        f"{enterprise_search_url}api/as/v1/credentials/private-key",
        auth=HTTPBasicAuth(elastic_username, elastic_password),
    )
    key_info = key_response.json()
    return key_info["key"]
