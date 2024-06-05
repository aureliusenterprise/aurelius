from ...m4i_generic_entity_serializers import *

m4i_ksql_entity_model = api.model('model_m4i_ksql_entity', {
    'name': fields.String(required=True, description='The name of ksql'),
    'env': fields.String(required=True, description='The confluent environment  ksql is run on'),
    'cluster': fields.String(required=True, description='The kafka cluster ksql is on'),
    'kafka_topic': fields.String(required=True, description='The kafka_topic ksql queries'),
    'value_format': fields.String(required=True, description='The value_format of the ksql'),
    'query': fields.String(required=True, description='The query of the ksql'),
    'properties': fields.String(required=True, description='The properties of the ksql')
})
