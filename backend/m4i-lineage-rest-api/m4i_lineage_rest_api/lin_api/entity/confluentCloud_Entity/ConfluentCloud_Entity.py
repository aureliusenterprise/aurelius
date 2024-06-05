import asyncio
import logging
from flask import request
from flask_restx import Resource
from m4i_atlas_core import create_entities, get_entities_by_type_name
from m4i_backend_core.auth import requires_auth

from .confluentCloud_Model import ConfluentCloud
from .m4i_confluentCloud_entity_serializers import m4i_confluentCloud_entity_model as confluentCloud_entity_serializer
from ... import api, m4i_output_get_model, m4i_output_model, output_filter_functions, authorizations

""" 
Defining confluentCloud_Entity Entity
"""
log = logging.getLogger(__name__)
ns = api.namespace('entity/confluentCloud_entity', description='Operations related to the confluentCloud Entity',
                   security='apikey',
                   authorizations=authorizations
                   )


@ns.route("/")
class confluentCloud_Class(Resource):

    @api.response(200, 'confluentCloud_Entity Entities in Atlas')
    @api.response(400, 'confluentCloud_Entity is not Defined in Atlas')
    @api.doc(id='get_confluentCloud_entities', security='apikey')
    @api.marshal_with(m4i_output_get_model)
    @requires_auth(transparent=True)
    def get(self, access_token=None):
        """
        Returns list of confluentCloud_Entity Entities
        """
        search_result = asyncio.run(get_entities_by_type_name("m4i_confluent_cloud", access_token=access_token))
        transformed_response = output_filter_functions.transform_get_response(search_result)
        return transformed_response, 200

    @api.response(200, 'confluentCloud_Entity Entity successfully created.')
    @api.response(500, "ValueError")
    @api.expect(confluentCloud_entity_serializer, validate=True)
    @api.doc(id='post_confluentCloud_entities', security='apikey')
    @api.marshal_with(m4i_output_model)
    @requires_auth(transparent=True)
    def post(self, access_token=None):
        """
        Creates a new confluentCloud_Entity Entity.
        """
        obj = ConfluentCloud.from_dict(request.json)
        entity = obj.convert_to_atlas()
        data_read_response = asyncio.run(create_entities(entity, access_token=access_token))
        transformed_response = output_filter_functions.transform_post_response(data_read_response)
        return transformed_response, 200
