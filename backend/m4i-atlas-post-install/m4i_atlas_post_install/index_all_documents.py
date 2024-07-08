from typing import Any, List, Mapping

from elastic_enterprise_search import AppSearch


def index_all_documents(
    app_search_client: AppSearch,
    engine_name: str,
    documents: List[Mapping[str, Any]],
):
    for i in range(0, len(documents), 100):
        app_search_client.index_documents(
            engine_name=engine_name, documents=documents[i : i + 100]
        )
