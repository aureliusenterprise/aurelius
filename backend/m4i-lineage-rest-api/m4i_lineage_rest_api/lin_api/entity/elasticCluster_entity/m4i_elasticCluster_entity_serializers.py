from flask_restx import fields

from ...restplus import api

m4i_elasticCluster_entity_model = api.model(
    "model_m4i_elasticCluster_entity",
    {
        "name": fields.String(required=True, description="Name of elastic cluster"),
        "replica_count": fields.Integer(
            required=True, description="The replica_count configured for the elastic cluster"
        ),
        "shard_count": fields.Integer(
            required=True, description="The shard_count configured for the elastic cluster"
        ),
    },
)
