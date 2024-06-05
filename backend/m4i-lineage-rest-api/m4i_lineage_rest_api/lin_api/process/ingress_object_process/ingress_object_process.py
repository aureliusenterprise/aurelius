import asyncio
import logging
from flask import request
from flask_restx import Resource
from m4i_atlas_core import create_entities, get_entities_by_type_name
from m4i_backend_core.auth import requires_auth

from .ingress_object_process_model import IngressObjectProcess
from .ingress_object_process_seralizer import m4i_ingress_object_process_model as ingress_object_process_serializer
from ... import output_filter_functions, m4i_output_model, m4i_output_get_model, api, authorizations

"""
Defining ingress_object_process, (Kafka to Elastic) NameSpace
"""
log = logging.getLogger(__name__)
ns = api.namespace('process/ingress_object_process', description='Ingress Object Process',
                   security='apikey',
                   authorizations=authorizations
                   )


@ns.route("/")
class ingress_object_process_Class(Resource):

    @api.response(200, 'Ingress Object Process Entities in Atlas')
    @api.response(400, 'Ingress Object Process is not Defined in Atlas')
    @api.doc(id='get_ingress_object_process_entities', security='apikey')
    @api.marshal_with(m4i_output_get_model)
    @requires_auth(transparent=True)
    def get(self, access_token=None):
        """
        Returns list of Ingress Object Entities
        """
        search_result = asyncio.run(get_entities_by_type_name("m4i_ingress_object_process", access_token=access_token))
        transformed_response = output_filter_functions.transform_get_response(search_result)
        return transformed_response, 200

    @api.response(200, 'Ingress Object Process Entity successfully created.')
    @api.response(500, "ValueError")
    @api.expect(ingress_object_process_serializer, validate=True)
    @api.doc(id='post_ingress_object_process_entities', security='apikey')
    @api.marshal_with(m4i_output_model)
    @requires_auth(transparent=True)
    def post(self, access_token=None):
        """
        Creates a new Ingress Object Process Entity.
        """
        obj = IngressObjectProcess.from_dict(request.json)
        entity = obj.convert_to_atlas()
        data_read_response = asyncio.run(create_entities(entity, access_token=access_token))
        transformed_response = output_filter_functions.transform_post_response(data_read_response)
        return transformed_response, 200
