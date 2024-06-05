from flask_restx import fields

from .restplus import api

m4i_generic_entity_model = api.model('model_m4i_generic_entity', {
    'qualifiedName': fields.String(required=True, description='qualifiedName of Entity'),
    'name': fields.String(required=True, description='Name of Entity'),
    'description': fields.String(description='Description of Entity'),
})
