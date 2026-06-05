from flask_restx import fields

from ...restplus import api

m4i_confluentCloud_entity_model = api.model(
    "model_m4i_confluentCloud_entity",
    {"name": fields.String(required=True, description="The Name of the Confluent Cloud")},
)
