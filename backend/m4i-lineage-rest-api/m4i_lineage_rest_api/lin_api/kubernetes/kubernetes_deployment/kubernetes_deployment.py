import asyncio
import logging
from flask import request
from flask_restx import Resource
from m4i_atlas_core import get_entities_by_type_name, create_entities
from m4i_backend_core.auth import requires_auth

from .kubernetes_deployment_model import KubernetesDeployment
from .kubernetes_deployment_serializers import m4i_kubernetes_deployment_model as kubernetes_deployment_serializer
from ... import api, m4i_output_model, m4i_output_get_model, output_filter_functions, authorizations

""" 
Defining kubernetes_deployment, (Python Script) NameSpace
"""
log = logging.getLogger(__name__)
ns = api.namespace('kubernetes/kubernetes_deployment', description='Operations related to Kubernetes Deployment',
                   security='apikey',
                   authorizations=authorizations
                   )


@ns.route("/")
class kubernetes_deployment_Class(Resource):

    @api.response(200, 'Kubernetes Deployment Entities in Atlas')
    @api.response(400, 'Kubernetes Deployment is not Defined in Atlas')
    @api.doc(id='get_kubernetes_deployment_entities', security='apikey')
    @api.marshal_with(m4i_output_get_model)
    @requires_auth(transparent=True)
    def get(self, access_token=None):
        """
        Returns list of Kubernetes Deployment Entities
        """
        search_result = asyncio.run(get_entities_by_type_name("m4i_kubernetes_deployment", access_token=access_token))
        transformed_response = output_filter_functions.transform_get_response(search_result)
        return transformed_response, 200

    @api.response(200, 'Kubernetes Deployment Entity successfully created.')
    @api.response(500, "ValueError")
    @api.expect(kubernetes_deployment_serializer, validate=True)
    @api.doc(id='post_kubernetes_deployment_entities', security='apikey')
    @api.marshal_with(m4i_output_model)
    @requires_auth(transparent=True)
    def post(self, access_token=None):
        """
        Creates a new Kubernetes Deployment Entity.
        """
        obj = KubernetesDeployment.from_dict(request.json)
        entity = obj.convert_to_atlas()
        data_read_response = asyncio.run(create_entities(entity, access_token=access_token))
        transformed_response = output_filter_functions.transform_post_response(data_read_response)
        return transformed_response, 200
