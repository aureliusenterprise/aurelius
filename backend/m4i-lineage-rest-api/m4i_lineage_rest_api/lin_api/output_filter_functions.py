from m4i_atlas_core import EntityMutationResponse, EntityHeader
from typing import List


def transform_post_response(put_response: EntityMutationResponse):
    put_response = put_response.mutated_entities

    output = {"CREATE": 0,
              "UPDATE": 0,
              "DELETE": 0}

    if "CREATE" in put_response:
        output["CREATE"] = len(put_response["CREATE"])
    if "UPDATE" in put_response:
        output["UPDATE"] = len(put_response["UPDATE"])
    if "DELETE" in put_response:
        output["DELETE"] = len(put_response["DELETE"])
    return output


def transform_get_response(entities: List[EntityHeader]):
    qualified_names = []
    if len(entities) > 0:
        qualified_names = [header.attributes.unmapped_attributes["qualifiedName"] for header in entities]
    output = {
        "entities": len(entities),
        "qualifiedNames": qualified_names
    }
    return output
