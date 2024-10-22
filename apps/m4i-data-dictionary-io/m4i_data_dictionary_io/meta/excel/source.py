from typing import Dict, Union, Type

from ...entities.json.source.Source import Source
from ...functions.get_info_from_git import get_info_from_git
from m4i_atlas_core import ConfigStore
from ...entities import T, ToAtlasConvertible


def get_file_details() -> Dict:
    store = ConfigStore.get_instance()
    data_path = store.get("data.dictionary.path").replace('\\', '/')
    branch, hash_code = get_info_from_git(data_path.split('data_governance')[0])
    filename = data_path.split('data_governance')[-1]
    qualified_name = f"{filename}@{branch}@{hash_code}"
    return {
        "branch": branch,
        "hashCode": hash_code,
        "name": filename,
        "qualifiedName": qualified_name
    }


def get_source() -> Union[Dict, Type[ToAtlasConvertible[T]]]:
    return get_file_details(), Source