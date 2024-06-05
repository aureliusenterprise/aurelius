from ...m4i_generic_entity_serializers import *

m4i_indexPattern_entity_model = api.inherit('model_m4i_indexPattern_entity', m4i_generic_entity_model, {
    'indexPattern': fields.String(required=True, description='The indexPattern used by the save object index-pattern'),
    'updatedAt': fields.String(required=True,
                               description='The updatedAt in the saved object artifact of the index-pattern'),
    'version': fields.String(required=True,
                             description='The version in the saved object artifact of the index-pattern'),
    'creator': fields.List(fields.String(), description='List of qualifiedName for creators of the index-pattern'),
    'parentDataset': fields.List(fields.String(),
                                 description='List of qualifiedNames of parent dataset (visualization) that the index-pattern is used')
})
