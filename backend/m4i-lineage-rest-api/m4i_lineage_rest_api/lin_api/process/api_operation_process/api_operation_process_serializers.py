from flask_restx import fields

from ...restplus import api
from ...m4i_generic_entity_serializers import m4i_generic_entity_model

m4i_api_operation_process_model = api.inherit('model_m4i_api_operation_process', m4i_generic_entity_model, {
    'processOwner': fields.String(required=False, description='Qualified Name of processOwner of Process Entity'),
    'inputs': fields.List(fields.String(), required=True,
                          description='List Qualified Name Inputs  of Api Operation Process Entity'),
    'outputs': fields.List(fields.String(), required=True,
                           description='List Qualified Name Outputs of API Operation Entity'),
    'microservice': fields.String(required=True, description='The microservice that the api operation is on')
})
