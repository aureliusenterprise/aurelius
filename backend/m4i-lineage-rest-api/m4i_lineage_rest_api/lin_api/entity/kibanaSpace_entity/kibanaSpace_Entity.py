import asyncio
import logging
from flask import request
from flask_restx import Resource
from m4i_atlas_core import (create_entities, get_entities_by_type_name)
from m4i_backend_core.auth import requires_auth

from .kibanaSpace_Model import KibanaSpace
from .m4i_kibanaSpace_entity_serializers import \
    m4i_kibanaSpace_entity_model as kibanaSpace_entity_serializer
from ... import output_filter_functions, api, m4i_output_model, m4i_output_get_model,authorizations

""" 
Defining kibanaSpace_entity Entity
"""
log = logging.getLogger(__name__)
ns = api.namespace('entity/kibanaSpace_entity', description='Operations related to the kibanaSpace_entity Entity',
                   security='apikey',
                   authorizations=authorizations
                   )


@ns.route("/")
class kibanaSpace_Class(Resource):

    @api.response(200, 'kibanaSpace Entities in Atlas')
    @api.response(400, 'kibanaSpace is not Defined in Atlas')
    @api.doc(id='get_kibanaSpace_entities', security='apikey')
    @api.marshal_with(m4i_output_get_model)
    @requires_auth(transparent=True)
    def get(self, access_token=None):
        """
        Returns list of kibanaSpace_entity Entities
        """
        search_result = asyncio.run(get_entities_by_type_name("m4i_kibana_space", access_token=access_token))
        transformed_response = output_filter_functions.transform_get_response(search_result)
        return transformed_response, 200

    @api.response(201, 'kibanaSpace Entity successfully created.')
    @api.response(500, "ValueError")
    @api.expect(kibanaSpace_entity_serializer, validate=True)
    @api.doc(id='post_kibanaSpace_entities', security='apikey')
    @api.marshal_with(m4i_output_model)
    @requires_auth(transparent=True)
    def post(self, access_token=None):
        """
        Creates a new kibanaSpace_entity Entity.
        """
        obj = KibanaSpace.from_dict(request.json)
        entity = obj.convert_to_atlas()
        data_read_response = asyncio.run(create_entities(entity, access_token=access_token))
        transformed_response = output_filter_functions.transform_post_response(data_read_response)
        return transformed_response, 200
