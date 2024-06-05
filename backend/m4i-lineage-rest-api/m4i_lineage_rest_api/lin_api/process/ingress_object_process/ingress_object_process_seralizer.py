from flask_restx import fields

from ...restplus import api
from ...m4i_generic_entity_serializers import m4i_generic_entity_model

m4i_ingress_object_process_model = api.inherit('model_m4i_ingress_object_process', m4i_generic_entity_model, {
    'processOwner': fields.String(required=False, description='Qualified Name of processOwner of Process Entity'),
    'inputs': fields.List(fields.String(), required=True,
                          description='List Qualified Name Inputs  of Ingress Controller Process Entity'),
    'outputs': fields.List(fields.String(), required=True,
                           description='List Qualified Name Outputs of Ingress Controller Entity'),
    'kubernetesService': fields.List(fields.String(), required=True,
                                     description='List Qualified Name kubernetes services known by the Ingress object Entity'),
    'namespace': fields.String(required=True, description='The namespace that the Ingress object is on'),
    'ingressController': fields.String(required=False,
                                       description='The qualified name of the Ingress Controller that know the ingress object')

})
