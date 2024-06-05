from flask_restx import fields

from ...restplus import api
from ...m4i_generic_entity_serializers import m4i_generic_entity_model

m4i_kubernetes_service_process_model = api.inherit('model_m4i_kubernetes_service_process', m4i_generic_entity_model, {
    'processOwner': fields.String(required=False, description='Qualified Name of processOwner of Process Entity'),
    'inputs': fields.List(fields.String(), required=True,
                          description='List Qualified Name Inputs  of Kubernetes Service Process Entity'),
    'outputs': fields.List(fields.String(), required=True,
                           description='List Qualified Name Outputs of Kubernetes Service Entity'),
    'microservice': fields.List(fields.String(), required=True,
                                description='List Qualified Name microservices known by the Kubernetes Service Entity'),
    'namespace': fields.String(required=True, description='The namespace that the Kubernetes Service is on'),
    'ingressObject': fields.String(required=False, description='The ingress object that knows the Kubernetes Service')

})
