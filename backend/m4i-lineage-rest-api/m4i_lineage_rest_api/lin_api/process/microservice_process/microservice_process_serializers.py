from flask_restx import fields

from ...restplus import api

m4i_microservice_process_model = api.model('model_m4i_microservice_process', {
    'qualifiedName': fields.String(required=True),
    'name': fields.String(required=True),
    'description': fields.String(required=False),
    'processOwner': fields.String(required=False, description='Qualified Name of processOwner of Process Entity'),
    'inputs': fields.List(fields.String(), required=True,
                          description='List Qualified Name Inputs  of Microservice Process Entity'),
    'outputs': fields.List(fields.String(), required=True,
                           description='List Qualified Name Outputs of Microservice Entity'),
    'source': fields.List(fields.String(), required=False, min_items=1,
                          description='List Qualified Name Source of Process Entity'),
    'system': fields.String(required=True, description='The system that the microservice runs on')
})
