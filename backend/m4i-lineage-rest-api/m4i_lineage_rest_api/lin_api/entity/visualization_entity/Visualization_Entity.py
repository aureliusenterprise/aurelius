import asyncio
import logging
from flask import request
from flask_restx import Resource
from m4i_atlas_core import (create_entities, get_entities_by_type_name)
from m4i_backend_core.auth import requires_auth

from .m4i_visualization_entity_serializers import m4i_visualization_entity_model as visualization_entity_serializer
from .visualization_Model import Visualization
from ... import output_filter_functions, api, m4i_output_model, m4i_output_get_model, authorizations

""" 
Defining Visualization Entity
"""
log = logging.getLogger(__name__)
ns = api.namespace('entity/visualization_entity', description='Operations related to the Visualization Entity',
                   security='apikey',
                   authorizations=authorizations
                   )


@ns.route("/")
class visualization_Class(Resource):

    @api.response(200, 'Visualization Entities in Atlas')
    @api.response(400, 'Visualization is not Defined in Atlas')
    @api.doc(id='get_visualization_entities', security='apikey')
    @api.marshal_with(m4i_output_get_model)
    @requires_auth(transparent=True)
    def get(self, access_token=None):
        """
        Returns list of Visualization Entities
        """
        search_result = asyncio.run(get_entities_by_type_name("m4i_visualization", access_token=access_token))
        transformed_response = output_filter_functions.transform_get_response(search_result)
        return transformed_response, 200

    @api.response(200, 'Visualization Entity successfully created.')
    @api.response(500, "ValueError")
    @api.expect(visualization_entity_serializer, validate=True)
    @api.doc(id='post_visualization_entities', security='apikey')
    @api.marshal_with(m4i_output_model)
    @requires_auth(transparent=True)
    def post(self, access_token=None):
        """
        Creates a new Visualization Entity.
        """
        obj = Visualization.from_dict(request.json)
        entity = obj.convert_to_atlas()
        data_read_response = asyncio.run(create_entities(entity, access_token=access_token))
        transformed_response = output_filter_functions.transform_post_response(data_read_response)
        return transformed_response, 200
