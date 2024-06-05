from flask_restx import fields
from ...restplus import api

m4i_confluentEnvironment_entity_model = api.model('model_m4i_confluentEnvironment_entity', {
    'name': fields.String(required=True, description='Name of the Confluent Environment'),
    'confluent_cloud': fields.String(required=True,
                                     description='The Qualified name of m4i_confluentCloud entity to which it belongs'),
    'schema_registry': fields.Boolean(required=True,
                                      description='A boolean indicating if there is a schemaRegistry required')
})
