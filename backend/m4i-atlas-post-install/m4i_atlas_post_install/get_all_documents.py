from typing import Any, List, MutableMapping

from elastic_enterprise_search import AppSearch


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
