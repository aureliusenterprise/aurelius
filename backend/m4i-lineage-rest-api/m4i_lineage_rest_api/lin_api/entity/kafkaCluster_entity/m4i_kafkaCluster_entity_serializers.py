from ...m4i_generic_entity_serializers import *

m4i_kafkaCluster_entity_model = api.model('model_m4i_kafkaCluster_entity', {
    'name': fields.String(required=True, description='The name of the kafka cluster'),
    'confluent_environment': fields.String(required=True,
                                           description='The name of the confluent environment the kafka cluster is on'),
    'kafka_partitions': fields.Integer(required=True, description='The partitions configured for the kafka cluster'),
    'kafka_replicas': fields.Integer(required=True, description='The replica_count configured for the kafka cluster'),
})
