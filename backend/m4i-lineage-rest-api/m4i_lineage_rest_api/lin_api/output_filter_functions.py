from m4i_atlas_core import EntityMutationResponse, EntityHeader
from typing import Dict, List, Any


def transform_post_response(put_response: EntityMutationResponse) -> Dict[str, int]:
    mutated = put_response.mutated_entities if put_response.mutated_entities else {}

    output: Dict[str, int] = {"CREATE": 0, "UPDATE": 0, "DELETE": 0}

    if "CREATE" in mutated:
        output["CREATE"] = len(mutated["CREATE"])
    if "UPDATE" in mutated:
        output["UPDATE"] = len(mutated["UPDATE"])
    if "DELETE" in mutated:
        output["DELETE"] = len(mutated["DELETE"])
    return output


def transform_get_response(entities: List[EntityHeader]) -> Dict[str, Any]:
    qualified_names = []
    if len(entities) > 0:
        qualified_names = [
            header.attributes.unmapped_attributes["qualifiedName"]
            for header in entities
            if header.attributes and header.attributes.unmapped_attributes
        ]
    output: Dict[str, Any] = {"entities": len(entities), "qualifiedNames": qualified_names}
    return output
