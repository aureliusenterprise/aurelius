import pytest
from m4i_atlas_core import KafkaTopic

from m4i_lineage_rest_api.lin_api.entity.kafkaTopic_entity.model.KafkaTopicApiModel import KafkaTopicApiModel


@pytest.fixture
def data():
    return {
        "name": "testing_m4i_kafka_topic",
        "cluster": "test_m4i_kafka_cluster",
        "environment": "test_m4i_confluent_environment",
        "partitions": 3,
        "replicas": 2,
        "key_schema": "string",
        "value_schema": {
            "fields": [
                {"name": "testing_kafka_field_1", "doc": "test_m4i_data_attribute", "type": "string"},
                {
                    "name": "testing_kafka_field_2",
                    "doc": None,
                    "type": [
                        "null",
                        {
                            "fields": [
                                {
                                    "name": "testing_kafka_field_3",
                                    "doc": "test_m4i_data_attribute",
                                    "type": "string",
                                }
                            ],
                            "name": "testing_kafka_field_2",
                            "doc": "test_m4i_data_attribute",
                            "type": "record",
                        },
                    ],
                },
            ],
            "name": "testing_m4i_kafka_topic__value",
            "doc": None,
            "namespace": "namespace",
            "type": "record",
        },
    }


# END data


def test__KafkaTopicApiModel_from_dict(data: dict):
    model = KafkaTopicApiModel.from_dict(data)

    assert isinstance(model, KafkaTopicApiModel)
    assert model.name == "testing_m4i_kafka_topic"
    assert model.environment == "test_m4i_confluent_environment"
    assert model.cluster == "test_m4i_kafka_cluster"
    value_schema = model.value_schema
    template = value_schema["fields"][0]  # type: ignore[reportArgumentType, reportGeneralTypeIssues]
    assert template["doc"] == "test_m4i_data_attribute"  # type: ignore[reportArgumentType]
    assert template["name"] == "testing_kafka_field_1"  # type: ignore[reportArgumentType]
    assert template["type"] == "string"  # type: ignore[reportArgumentType]
    template = value_schema["fields"][1]  # type: ignore[reportArgumentType, reportGeneralTypeIssues]
    assert template["doc"] is None  # type: ignore[reportArgumentType]
    assert template["name"] == "testing_kafka_field_2"  # type: ignore[reportArgumentType]
    assert isinstance(template["type"], list)  # type: ignore[reportArgumentType]
    template_parent = template["type"]  # type: ignore[reportArgumentType]
    template = template_parent[0]
    assert template == "null"
    template = template_parent[1]
    assert template["doc"] == "test_m4i_data_attribute"  # type: ignore[reportArgumentType]
    assert template["name"] == "testing_kafka_field_2"  # type: ignore[reportArgumentType]
    assert template["type"] == "record"  # type: ignore[reportArgumentType]
    template = template["fields"][0]  # type: ignore[reportArgumentType]
    assert template["doc"] == "test_m4i_data_attribute"  # type: ignore[reportArgumentType]
    assert template["name"] == "testing_kafka_field_3"  # type: ignore[reportArgumentType]
    assert template["type"] == "string"  # type: ignore[reportArgumentType]


# END test__KafkaTopicApiModel_from_dict


def test__KafkaTopicApiModel_convert_to_atlas_entity(data: dict):
    model = KafkaTopicApiModel.from_dict(data)
    atlas, atlas_ref = model.convert_to_atlas()

    assert isinstance(atlas[0], KafkaTopic)
    index_attributes = atlas[0].attributes
    assert index_attributes.name == model.name
    assert (
        index_attributes.qualified_name
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
    )
    index_collection = index_attributes.collections[0]
    assert index_collection is not None
    assert (
        getattr(index_collection.unique_attributes, "qualified_name")
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--data"
    )

    index_field_attribute = atlas[0].attributes.fields[0].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_1"
    assert index_field_attribute.qualified_name == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_1"
    )
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert (
        getattr(index_field_dataset.unique_attributes, "qualified_name")
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
    )

    index_field_attribute = atlas[0].attributes.fields[1].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_2"
    assert index_field_attribute.qualified_name == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_2"
    )
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert (
        getattr(index_field_dataset.unique_attributes, "qualified_name")
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
    )

    ref_guid_list = list(atlas_ref.keys())
    index_field_attribute = atlas_ref[ref_guid_list[1]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_1"
    assert index_field_attribute.qualified_name == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_1"
    )
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert (
        getattr(index_field_dataset.unique_attributes, "qualified_name")
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
    )

    index_field_attribute = atlas_ref[ref_guid_list[2]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_2"
    assert index_field_attribute.qualified_name == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_2"
    )
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert (
        getattr(index_field_dataset.unique_attributes, "qualified_name")
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
    )

    index_field_attribute = atlas_ref[ref_guid_list[3]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_2"
    assert index_field_attribute.qualified_name == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_2"
        "--testing_kafka_field_2"
    )
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"
    index_field_dataset = index_field_attribute.parent_field[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_2"
    )

    index_field_attribute = atlas_ref[ref_guid_list[4]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_3"
    assert index_field_attribute.qualified_name == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_2"
        "--testing_kafka_field_2--testing_kafka_field_3"
    )
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"
    index_field_dataset = index_field_attribute.parent_field[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == (
        "test_m4i_confluent_environment--test_m4i_kafka_cluster"
        "--testing_m4i_kafka_topic--testing_kafka_field_2"
        "--testing_kafka_field_2"
    )


# END test__KafkaTopicApiModel_convert_to_atlas_entity


def test__KafkaTopicApiModel_convert_to_atlas_entity_wild(data: dict):
    data["value_schema"] = "string"
    model = KafkaTopicApiModel.from_dict(data)
    atlas, atlas_ref = model.convert_to_atlas()

    assert isinstance(atlas[0], KafkaTopic)
    index_attributes = atlas[0].attributes
    assert index_attributes.name == model.name
    assert (
        index_attributes.qualified_name
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
    )
    index_collection = index_attributes.collections[0]
    assert index_collection is not None
    assert (
        getattr(index_collection.unique_attributes, "qualified_name")
        == "test_m4i_confluent_environment--test_m4i_kafka_cluster--data"
    )


# END test__KafkaTopicApiModel_convert_to_atlas_entity_wild
