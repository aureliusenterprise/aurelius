from ...m4i_generic_entity_serializers import *

m4i_visualization_entity_model = api.inherit('model_m4i_visualization_entity', m4i_generic_entity_model, {
    'updatedAt': fields.String(required=True,
                               description='The updatedAt in the saved object artifact of the visualization'),
    'version': fields.String(required=True,
                             description='The version in the saved object artifact of the visualization'),
    'creator': fields.List(fields.String(), required=False,
                           description='List of qualifiedName for creators of the visualization'),
    'parentDataset': fields.List(fields.String(),
                                 description='List of qualifiedNames of parentDataset (dashboard) in the visualization'),
    'childDataset': fields.List(fields.String(), required=True,
                                description='List of qualifiedNames of childDataset (index-pattern) in the visualization'),
    'type': fields.String(required=True, description='The type of the visualization'),
    'visualizationType': fields.String(required=False, description='The visualizationType of the visualization lens')

})
