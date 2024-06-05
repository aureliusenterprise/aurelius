from flask_restx import fields

from ...m4i_generic_entity_serializers import m4i_generic_entity_model
from ...restplus import api

m4i_kubernetes_environment_model = api.inherit('model_m4i_kubernetes_environment', m4i_generic_entity_model, {
    'kubernetesClusters': fields.List(fields.String(), required=True,
                                      description='List of Qualified Names of kubernetes clusters on this kubernetes environment'),
})
