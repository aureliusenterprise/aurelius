from flask_restx import fields

from .restplus import api

m4i_output_model = api.model('model_output', {
    'CREATE': fields.Integer(required=True),
    'UPDATE': fields.Integer(required=True),
    'DELETE': fields.Integer(required=True)})
