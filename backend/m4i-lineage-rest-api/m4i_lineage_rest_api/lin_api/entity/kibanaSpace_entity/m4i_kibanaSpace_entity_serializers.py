from ...m4i_generic_entity_serializers import *

m4i_kibanaSpace_entity_model = api.model('model_m4i_kibanaSpace_entity', {
    'name': fields.String(required=True, description='The name of the kibana space'),
    'avatar_color': fields.String(required=True, description='The avatar_color of the kibana space'),
    'avatar_initials': fields.String(required=True, description='The avatar_initials of the kibana space'),
    'elastic_cluster': fields.String(required=True,
                                     description='The qualifiedName of the elastic cluster the kibana space is on'),
    'description': fields.String(required=False, description='The description of the kibana space')
})
