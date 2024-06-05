from flask_restx import fields

from ...restplus import api

m4i_generic_process_model = api.model('model_m4i_generic_process', {
    'qualifiedName': fields.String(required=True, description='The qualifiedName of the process'),
    'name': fields.String(required=True, description='The name of the process'),
    'description': fields.String(required=False, description='The description of the process'),
    'processOwner': fields.String(required=False, description='Qualified Name of processOwner of Process Entity'),
    'inputs': fields.List(fields.String(), required=True, min_items=1,
                          description='List Qualified Name Inputs  of Process Entity'),
    'outputs': fields.List(fields.String(), required=True, min_items=1,
                           description='List Qualified Name Outputs of Process Entity'),
    'source': fields.List(fields.String(), required=False, min_items=1,
                          description='List Qualified Name Source of Process Entity'),
})
