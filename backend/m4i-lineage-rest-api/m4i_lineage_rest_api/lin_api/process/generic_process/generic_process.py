import asyncio
import logging
from flask import request
from flask_restx import Resource
from m4i_atlas_core import get_entities_by_type_name, create_entities
from m4i_backend_core.auth import requires_auth

from .generic_process_model import GenericProcess
from .generic_process_serializers import m4i_generic_process_model as generic_process_serializer
from ... import output_filter_functions, m4i_output_model, m4i_output_get_model, api, authorizations

""" 
Defining generic_process, (Python Script) NameSpace
"""
log = logging.getLogger(__name__)
ns = api.namespace('process/generic_process', description='Operations related to "Generic" Process',
                   security='apikey',
                   authorizations=authorizations
                   )


@ns.route("/")
class generic_process_Class(Resource):

    @api.response(200, 'Generic Process Entities in Atlas')
    @api.response(400, 'Generic Process is not Defined in Atlas')
    @api.doc(id='get_generic_process_entities', security='apikey')
    @api.marshal_with(m4i_output_get_model)
    @requires_auth(transparent=True)
    def get(self, access_token=None):
        """
        Returns list of Generic Process Entities
        """
        search_result = asyncio.run(get_entities_by_type_name("m4i_generic_process", access_token=access_token))
        transformed_response = output_filter_functions.transform_get_response(search_result)
        return transformed_response, 200

    @api.response(200, 'Generic Process Entity successfully created.')
    @api.response(500, "ValueError")
    @api.expect(generic_process_serializer, validate=True)
    @api.doc(id='post_generic_process_entities', security='apikey')
    @api.marshal_with(m4i_output_model)
    @requires_auth(transparent=True)
    def post(self, access_token=None):
        """
        Creates a new Generic Process Entity.
        """
        obj = GenericProcess.from_dict(request.json)
        entity = obj.convert_to_atlas()
        data_read_response = asyncio.run(create_entities(entity, access_token=access_token))
        transformed_response = output_filter_functions.transform_post_response(data_read_response)
        return transformed_response, 200
