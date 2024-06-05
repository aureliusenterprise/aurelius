from .kafkaCluster_Model import KafkaCluster


def test__create_kafka_cluster_from_dict():
    """
    Tests whether or not a `KafkaCluster` can be created from a dict with its attributes
    """

    kafka_cluster = {
        "name": "Kafka Cluster",
        "kafka_replicas": 1,
        "kafka_partitions": 2,
        "confluent_environment": "dev_env",
        "qualifiedName": "dev_env--kafka-cluster"
    }

    instance = KafkaCluster.from_dict(kafka_cluster)

    assert instance.name == "Kafka Cluster"
    assert instance.kafka_replicas == 1
    assert instance.kafka_partitions == 2
    assert instance._qualified_name() == "dev_env--kafka-cluster"


# END test__create_kafka_cluster_from_dict

def test__create_kafka_cluster_from_json():
    """
    Tests whether or not a `Kafka Cluster` can be created from a json string with its attributes
    """

    kafka_cluster = (
        """
        {
            "name": "Kafka Cluster",
            "kafka_replicas": 1,
            "kafka_partitions": 2,
            "confluent_environment": "dev_env",
            "qualifiedName": "dev_env--kafka-cluster"
        }
        """
    )

    instance = KafkaCluster.from_json(kafka_cluster)

    assert instance.name == "Kafka Cluster"
    assert instance._qualified_name() == "dev_env--kafka-cluster"
    assert instance.kafka_partitions == 2
    assert instance.kafka_replicas == 1


# END test__create_kafka_cluster_from_json


def test__kafka_cluster_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    kafka_cluster = {
        "name": "Kafka Cluster",
        "kafka_replicas": 1,
        "kafka_partitions": 2,
        "confluent_environment": "dev_env",
        "qualifiedName": "dev_env--kafka-cluster"
    }

    instance = KafkaCluster.from_dict(kafka_cluster)

    assert instance._qualified_name() == "dev_env--kafka-cluster"


# END test__kafka_cluster_calculates_correct_qualified_name


def test__kafka_cluster_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    kafka_cluster = {
        "name": "Kafka Cluster",
        "kafka_replicas": 1,
        "kafka_partitions": 2,
        "confluent_environment": "dev_env",
        "qualifiedName": "dev_env--kafka-cluster"
    }

    instance = KafkaCluster.from_dict(kafka_cluster)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.kafka_replicas == instance.kafka_replicas
    assert atlas_attributes.kafka_partitions == instance.kafka_partitions
    assert atlas_attributes.qualified_name == instance._qualified_name()


# END test__kafka_cluster_convert_to_atlas_entity

def test__kafka_cluster_convert_to_atlas_entity_with_dataset():
    """
    Tests whether or not the `Child Dataset` field is correctly converted to the atlas format.
    """

    kafka_cluster = {
        "name": "Kafka Cluster",
        "kafka_replicas": 1,
        "kafka_partitions": 2,
        "confluent_environment": "dev_env",
        "qualifiedName": "dev_env--kafka-cluster"
    }

    instance = KafkaCluster.from_dict(kafka_cluster)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_confluent_environment = atlas_attributes.confluent_environment[0]

    assert atlas_confluent_environment is not None
    assert atlas_confluent_environment.type_name == "m4i_confluent_environment"
    assert getattr(atlas_confluent_environment.unique_attributes,
                   "qualified_name") == instance.confluent_environment
# END test__kafka_cluster_convert_to_atlas_entity_with_dataset
