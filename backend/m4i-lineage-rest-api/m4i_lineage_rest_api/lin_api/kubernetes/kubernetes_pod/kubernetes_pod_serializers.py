from flask_restx import fields

from ...m4i_generic_entity_serializers import m4i_generic_entity_model
from ...restplus import api

m4i_kubernetes_pod_model = api.inherit('model_m4i_kubernetes_pod', m4i_generic_entity_model, {
    'kubernetesCronjob': fields.String(required=False,
                                       description='Qualified Name of kubernetes Cronjob this pod is based off'),
    'kubernetesDeployment': fields.String(required=False,
                                          description=' Qualified Name of kubernetes Deployment this pod is based off'),
    'replicas': fields.String(required=False,
                              description='The number of relicas pods'),
})
