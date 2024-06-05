import asyncio

from aiohttp import ClientResponseError
from flask import Flask, abort, request
from m4i_atlas_core import (ConfigStore, LineageDirection, LineageInfo,
                            LineageRelation, get_lineage_by_guid)
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.shared import register as register_shared
from requests import post

app = Flask(__name__)

# Register the shared core module with the application
register_shared(app)

store = ConfigStore.get_instance()

process_types = [
    "m4i_generic_process", "m4i_api_operation_process", "m4i_connector_process",
    "m4i_ingress_controller_process", "m4i_ingress_object_process", "m4i_kubernetes_service_process", "m4i_microservice_process"
]

rules = {
    "rules": {
        "elements": [
            {
                "id": "5e18c7eb-f4f5-4587-a159-3ac3412080cf",
                "alias": "Element rule for column from_entity_id",
                "description": "This rule generates a new element for every from_entity_id in the dataset",
                "concept_type": "lineage_dataset",
                "id_type": "dynamic",
                "id_key": "from_entity_id",
                "concept_name_key": "from_entity_name",
                "concept_name_prefix": None,
                "concept_label_key": None,
                "concept_label_prefix": None,
                "mapping": [
                    {
                        "key": "Type name",
                        "value": "from_entity_type"
                    }
                ],
                "include": True,
                "type": "element"
            }, {
                "id": "90903dfd-6f1e-4f5f-a174-264524d9e3cc",
                "alias": "Element rule for column to_process_id",
                "description": "This rule generates a new element for every to_process_id in the dataset",
                "concept_type": "lineage_process",
                "id_type": "dynamic",
                "id_key": "to_process_id",
                "concept_name_key": "to_process_name",
                "concept_name_prefix": None,
                "concept_label_key": None,
                "concept_label_prefix": None,
                "mapping": [
                    {
                        "key": "Type name",
                        "value": "to_process_type"
                    }
                ],
                "include": True,
                "type": "element"
            },
            {
                "id": "457c347e-0689-4b65-92db-2f8e23c4fb5f",
                "alias": "Element rule for column from_process_id",
                "description": "This rule generates a new element for every from_process_id in the dataset",
                "concept_type": "lineage_process",
                "id_type": "dynamic",
                "id_key": "from_process_id",
                "concept_name_key": "from_process_name",
                "concept_name_prefix": None,
                "concept_label_key": None,
                "concept_label_prefix": None,
                "mapping": [
                    {
                        "key": "Type name",
                        "value": "from_process_type"
                    }
                ],
                "include": True,
                "type": "element"
            },
            {
                "id": "b85e49ca-9d5a-465b-ada2-7640f370b10a",
                "alias": "Element rule for column to_entity_id",
                "description": "This rule generates a new element for every to_entity_id in the dataset",
                "concept_type": "lineage_dataset",
                "id_type": "dynamic",
                "id_key": "to_entity_id",
                "concept_name_key": "to_entity_name",
                "concept_name_prefix": None,
                "concept_label_key": None,
                "concept_label_prefix": None,
                "mapping": [
                    {
                        "key": "Type name",
                        "value": "to_entity_type"
                    }
                ],
                "include": True,
                "type": "element"
            }
        ],
        "relations": [
            {
                "id": "57aa2001-a458-4cb7-8460-aa4a35ea9b9a",
                "type": "relation",
                "alias": "Relationship rule between from_entity_id and to_process_id",
                "description": "This rule generates a new relationship between from_entity_id and to_process_id",
                "include": True,
                "relationship_type": "lr",
                "id_type": "dynamic",
                "id_key": "id",
                "id_value": [
                    "from_entity_id",
                    "to_process_id"
                ],
                "relationship_name_type": "dynamic",
                "relationship_name_key": "",
                "relationship_label_type": "dynamic",
                "relationship_label_key": "",
                "target": "90903dfd-6f1e-4f5f-a174-264524d9e3cc",
                "source": "5e18c7eb-f4f5-4587-a159-3ac3412080cf"
            },
            {
                "id": "6a57fd4e-243f-4021-a8c5-9a92f212f97a",
                "type": "relation",
                "alias": "Relationship rule between from_process_id and to_entity_id",
                "description": "This rule generates a new relationship between from_process_id and to_entity_id",
                "include": True,
                "relationship_type": "lr",
                "id_type": "dynamic",
                "id_key": "id",
                "id_value": [
                    "from_process_id",
                    "to_entity_id"
                ],
                "relationship_name_type": "dynamic",
                "relationship_name_key": "",
                "relationship_label_type": "dynamic",
                "relationship_label_key": "",
                "target": "b85e49ca-9d5a-465b-ada2-7640f370b10a",
                "source": "457c347e-0689-4b65-92db-2f8e23c4fb5f"
            }

        ],
        "views": [
            {
                "id": "view_6008d024-5a7b-4581-b664-f463ece7a40b",
                "type": "view",
                "alias": "View rule for lineage overview",
                "description": "This rule generates the lineage overview",
                "include": True,
                "id_type": "static",
                "id_key": None,
                "id_value": "lineage_view",
                "view_name_type": "static",
                "view_name_key": None,
                "view_name_value": "Lineage",
                "view_layout": "archimate_process",
                "view_nodes": [
                    {
                        "rule": "457c347e-0689-4b65-92db-2f8e23c4fb5f"
                    },
                    {
                        "rule": "b85e49ca-9d5a-465b-ada2-7640f370b10a"
                    },
                    {
                        "rule": "5e18c7eb-f4f5-4587-a159-3ac3412080cf"
                    },
                    {
                        "rule": "90903dfd-6f1e-4f5f-a174-264524d9e3cc"
                    }
                ],
                "view_edges": []
            }
        ]
    }
}


def fmt_lineage_relation(relation: LineageRelation, lineage: LineageInfo):

    from_entity = lineage.guid_entity_map[relation.from_entity_id]
    to_entity = lineage.guid_entity_map[relation.to_entity_id]

    return {
        "id": relation.relationship_id,
        "from_entity_id": from_entity.guid if from_entity.type_name not in process_types else None,
        "from_entity_name": from_entity.display_text if from_entity.type_name not in process_types else None,
        "from_entity_type": from_entity.type_name if from_entity.type_name not in process_types else None,
        "from_process_id": from_entity.guid if from_entity.type_name in process_types else None,
        "from_process_name": from_entity.display_text if from_entity.type_name in process_types else None,
        "from_process_type": from_entity.type_name if from_entity.type_name in process_types else None,
        "to_entity_id": to_entity.guid if to_entity.type_name not in process_types else None,
        "to_entity_name": to_entity.display_text if to_entity.type_name not in process_types else None,
        "to_entity_type": to_entity.type_name if to_entity.type_name not in process_types else None,
        "to_process_id": to_entity.guid if to_entity.type_name in process_types else None,
        "to_process_name": to_entity.display_text if to_entity.type_name in process_types else None,
        "to_process_type": to_entity.type_name if to_entity.type_name in process_types else None
    }
# END fmt_lineage_relation


@app.route('/', methods=['GET'])
@requires_auth(transparent=True)
def lineage_model(access_token=None):

    params = request.args

    guid = params.get('guid')
    depth = int(params.get('depth', '3'))
    direction = LineageDirection(params.get('direction', 'BOTH'))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        lineage = loop.run_until_complete(get_lineage_by_guid(
            guid=guid,
            depth=depth,
            direction=direction,
            access_token=access_token
        ))
    except ClientResponseError as response_error:
        if response_error.code == 404:
            return ('', 204)
        elif response_error.code == 400:
            abort(400)
        # END IF
    # END TRY

    if len(lineage.relations) == 0:
        return ('', 204)
    # END IF

    lineage_relations = [
        fmt_lineage_relation(relation, lineage)
        for relation in lineage.relations
    ]

    data2model_request_body = {
        "data": lineage_relations,
        **rules
    }

    response = post(
        url=f"{store.get('data2model.server.url')}/extract",
        headers={'Authorization': f'bearer {access_token}'},
        json=data2model_request_body
    )

    response.raise_for_status()

    return response.text
# END lineage_model
