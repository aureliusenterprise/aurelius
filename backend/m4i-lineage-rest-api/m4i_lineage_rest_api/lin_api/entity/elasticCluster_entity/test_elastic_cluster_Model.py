import pytest

from .elasticCluster_Model import ElasticCluster


def test__create_elastic_cluster_from_dict():
    """
    Tests whether or not a `ElasticCluster` can be created from a dict with its attributes
    """

    elastic_cluster = {
        "name": "Elastic Cluster",
        "replica_count": 1,
        "shard_count": 2
    }

    instance = ElasticCluster.from_dict(elastic_cluster)

    assert instance.name == "Elastic Cluster"
    assert instance.replica_count == 1
    assert instance.shard_count == 2
    assert instance._qualified_name() == "elastic-cluster"


# END test__create_elastic_cluster_from_dict

def test__create_elastic_cluster_from_json():
    """
    Tests whether or not a `Elastic Cluster` can be created from a json string with its attributes
    """

    elastic_cluster = (
        """
        {
            "name": "Elastic Cluster",
            "replica_count": 1,
            "shard_count": 2
        }
        """
    )

    instance = ElasticCluster.from_json(elastic_cluster)

    assert instance.name == "Elastic Cluster"
    assert instance._qualified_name() == "elastic-cluster"
    assert instance.shard_count == 2
    assert instance.replica_count == 1


# END test__create_elastic_cluster_from_json

def test__elastic_cluster_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    elastic_cluster = {
        "name": "Elastic Cluster",
        "replica_count": 1,
        "shard_count": 2
    }

    instance = ElasticCluster.from_dict(elastic_cluster)

    assert instance._qualified_name() == "elastic-cluster"


# END test__elastic_cluster_calculates_correct_qualified_name


def test__elastic_cluster_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    elastic_cluster = {
        "name": "Elastic Cluster",
        "replica_count": 1,
        "shard_count": 2
    }

    instance = ElasticCluster.from_dict(elastic_cluster)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.replica_count == instance.replica_count
    assert atlas_attributes.shard_count == instance.shard_count
    assert atlas_attributes.qualified_name == instance._qualified_name()

# END test__elastic_cluster_convert_to_atlas_entity
