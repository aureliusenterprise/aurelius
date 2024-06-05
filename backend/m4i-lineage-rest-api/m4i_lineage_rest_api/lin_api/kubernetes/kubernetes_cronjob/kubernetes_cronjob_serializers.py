from flask_restx import fields

from ...m4i_generic_entity_serializers import m4i_generic_entity_model
from ...restplus import api

m4i_kubernetes_cronjob_model = api.inherit('model_m4i_kubernetes_cronjob', m4i_generic_entity_model, {
    'kubernetesPod': fields.List(fields.String(), required=True,
                                 description='List of Qualified Names of kubernetes pods on this kubernetes cronjob'),
    'tags': fields.String(required=False,
                          description='The tags of the cronjob'),
    'schedule': fields.String(required=False,
                              description='The schedule of the cronjob'),
    'kubernetesNamespace': fields.String(required=True,
                                         description='The Qualified Names of kubernetes namespace this kubernetes cronjob is on'),
})
