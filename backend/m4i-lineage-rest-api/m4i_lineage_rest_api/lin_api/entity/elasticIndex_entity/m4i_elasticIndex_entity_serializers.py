from ...m4i_generic_entity_serializers import *

m4i_elasticIndex_entity_model = api.model('model_m4i_elasticIndex_entity', {
    'name': fields.String(required=True, description='Name of elastic index'),
    'qualifiedName': fields.String(required=True, description='The qualifiedName of the elastic index'),
    'cluster': fields.String(required=True, description='The qualifiedName of elastic cluster the elastic index is on'),
    'environment': fields.String(required=True, description='Name of environment the elastic index is on'),
    'indexTemplate': fields.Nested(
        api.model('maps', {'mappings': fields.Raw()}), required=True,
        description='The template used by the elastic index'
    )
})
