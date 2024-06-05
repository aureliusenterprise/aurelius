from ...m4i_generic_entity_serializers import *

m4i_dashboard_entity_model = api.inherit('model_m4i_dashboard_entity', m4i_generic_entity_model, {
    'updatedAt': fields.String(required=True,
                               description='The updatedAt in the saved object artifact of the dashboard'),
    'version': fields.String(required=True, description='The version in the saved object artifact of the dashboard'),
    'kibanaSpace': fields.String(required=True,
                                 description='The qualifiedNmae of the kibana Space the dashboard is on'),
    'creator': fields.List(fields.String(), description='List of qualifiedName for creators of the dashboard'),
    'child_dataset': fields.List(fields.String(required=False), required=True,
                                 description='List of qualifiedNames of childDataset (visualizations) in the dashboard')
})
