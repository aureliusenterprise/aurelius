from flask_restx import fields

from ...m4i_generic_entity_serializers import m4i_generic_entity_model
from ...restplus import api

m4i_kubernetes_cluster_model = api.inherit('model_m4i_kubernetes_cluster', m4i_generic_entity_model, {
    'kubernetesNamespace': fields.List(fields.String(), required=True,
                                       description='List of Qualified Names of kubernetes Namespace on this kubernetes cluster'),
    'kubernetesEnvironment': fields.String(required=True,
                                           description='The Qualified Names of kubernetes environment this kubernetes cluster is on'),
})
