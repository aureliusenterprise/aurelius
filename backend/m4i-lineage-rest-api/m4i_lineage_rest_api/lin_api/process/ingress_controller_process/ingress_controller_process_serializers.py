from flask_restx import fields

from ...restplus import api
from ...m4i_generic_entity_serializers import m4i_generic_entity_model

m4i_ingress_controller_process_model = api.inherit('model_m4i_ingress_controller_process', m4i_generic_entity_model, {
    'processOwner': fields.String(required=False, description='Qualified Name of processOwner of Process Entity'),
    'inputs': fields.List(fields.String(), required=True,
                          description='List Qualified Name Inputs  of Ingress Controller Process Entity'),
    'outputs': fields.List(fields.String(), required=True,
                           description='List Qualified Name Outputs of Ingress Controller Entity'),
    'ingressObject': fields.List(fields.String(), required=True,
                                 description='List Qualified Name ingress Objects known by the Ingress Controller Entity'),
    'cluster': fields.String(required=True, description='The cluster that the Ingress Controller is on')
})
