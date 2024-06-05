from flask_restx import fields

from ...m4i_generic_entity_serializers import m4i_generic_entity_model
from ...restplus import api

m4i_kubernetes_namespace_model = api.inherit('model_m4i_kubernetes_namespace', m4i_generic_entity_model, {
    'kubernetesCronjob': fields.List(fields.String(), required=True,
                                     description='List of Qualified Names of kubernetes Cronjob on this kubernetes namespace'),
    'kubernetesDeployment': fields.List(fields.String(), required=True,
                                        description='List of Qualified Names of kubernetes Deployment on this kubernetes namespace'),
    'kubernetesCluster': fields.String(required=True,
                                       description='The Qualified Names of kubernetes cluster this kubernetes namespace is on'),
})
