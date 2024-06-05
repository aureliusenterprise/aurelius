import asyncio
import logging
from flask import request
from flask_restx import Resource
from m4i_atlas_core import create_entities, get_entities_by_type_name
from m4i_backend_core.auth import requires_auth

from .confluentEnvironment_Model import ConfluentEnvironment
from .m4i_confluentEnvironment_entity_serializers import \
    m4i_confluentEnvironment_entity_model as confluentEnvironment_entity_serializer
from ... import api, m4i_output_get_model, m4i_output_model, output_filter_functions, authorizations

""" 
Defining confluentEnvironment Entity
"""
log = logging.getLogger(__name__)
ns = api.namespace('entity/confluentEnvironment_entity',
                   description='Operations related to the confluentEnvironment Entity',
                   security='apikey',
                   authorizations=authorizations
                   )


@ns.route("/")
class confluentEnvironment_Class(Resource):

    @api.response(200, 'confluentEnvironment Entities in Atlas')
    @api.response(400, 'confluentEnvironment is not Defined in Atlas')
    @api.doc(id='get_confluentEnvironment_entities', security='apikey')
    @api.marshal_with(m4i_output_get_model)
    @requires_auth(transparent=True)
    def get(self, access_token=None):
        """
        Returns list of confluentEnvironment Entities
        """
        search_result = asyncio.run(get_entities_by_type_name("m4i_confluent_environment", access_token=access_token))
        transformed_response = output_filter_functions.transform_get_response(search_result)
        return transformed_response, 200

    @api.response(200, 'confluentEnvironment Entity successfully created.')
    @api.response(500, "ValueError")
    @api.expect(confluentEnvironment_entity_serializer, validate=True)
    @api.doc(id='post_confluentEnvironment_entities', security='apikey')
    @api.marshal_with(m4i_output_model)
    @requires_auth(transparent=True)
    def post(self, access_token=None):
        """
        Creates a new confluentEnvironment Entity.
        """
        obj = ConfluentEnvironment.from_dict(request.json)
        entity = obj.convert_to_atlas()
        data_read_response = asyncio.run(create_entities(entity, access_token=access_token))
        transformed_response = output_filter_functions.transform_post_response(data_read_response)
        return transformed_response, 200
