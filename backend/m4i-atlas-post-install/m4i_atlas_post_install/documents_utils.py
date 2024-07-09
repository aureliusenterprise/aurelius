import json
from pathlib import Path
from typing import Any, List, MutableMapping


def load_documents(path: Path):
    with open(path, "r") as json_file:
        documents = json.load(json_file)
    return documents


def index_documents(documents: List[MutableMapping[str, Any]]):
    atlas_dev_index = {}
    for document in documents:
        atlas_dev_index[document["guid"]] = document
    return atlas_dev_index
