from ..generic_process.generic_process_serializers import *

m4i_connector_process_model = api.inherit('attributes_m4i_connector_process', m4i_generic_process_model, {
    'connectorType': fields.String(required=True, description='ConnectorType of process Entity'),
    'server': fields.String(required=True, description='Server to which this connector runs')
})
