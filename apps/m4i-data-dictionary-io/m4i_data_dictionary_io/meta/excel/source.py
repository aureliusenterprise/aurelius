from typing import Dict, Tuple, Type

from ...entities.json.source.Source import Source
from m4i_atlas_core import ConfigStore
import os


def get_file_details() -> Dict:
    store = ConfigStore.get_instance()
    data_path = store.get("data.dictionary.path").replace("\\", "/")
    filename = os.path.basename(data_path)
    return {"name": filename, "qualifiedName": filename}


def get_source() -> Tuple[Dict, Type[Source]]:
    return get_file_details(), Source
