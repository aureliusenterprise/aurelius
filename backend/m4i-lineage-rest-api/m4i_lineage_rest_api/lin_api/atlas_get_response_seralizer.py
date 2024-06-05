from flask_restx import fields

from .restplus import api

m4i_output_get_model = api.model('model_output', {
    'entities': fields.Integer(required=True),
    'qualifiedNames': fields.List(fields.String(), required=True)
})
