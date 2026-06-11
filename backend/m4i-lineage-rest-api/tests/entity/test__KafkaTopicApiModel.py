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
    from m4i_lineage_rest_api.lin_api.entity.kafkaTopic_entity.model.KafkaTopicEntityFields import (
        KafkaTopicEntityField,
        KafkaTopicEntityFieldTypeName,
    )

    model = KafkaTopicApiModel.from_dict(data)

    assert isinstance(model, KafkaTopicApiModel)
    assert model.name == "testing_m4i_kafka_topic"
    assert model.environment == "test_m4i_confluent_environment"
    assert model.cluster == "test_m4i_kafka_cluster"
    value_schema = model.value_schema
    assert not isinstance(value_schema, str)
    # value_schema is a KafkaTopicValueSchemaBase dataclass, not a dict
    template = value_schema.fields[0]
    assert template.doc == "test_m4i_data_attribute"
    assert template.name == "testing_kafka_field_1"
    # type is deserialized as an enum, not a plain string
    assert template.type == KafkaTopicEntityFieldTypeName.STRING
    template = value_schema.fields[1]
    assert template.doc is None
    assert template.name == "testing_kafka_field_2"
    assert isinstance(template.type, list)
    template_parent = template.type
    template = template_parent[0]
    assert template == KafkaTopicEntityFieldTypeName.NULL
    template = template_parent[1]
    assert isinstance(template, KafkaTopicEntityField)
    # nested field is a KafkaTopicEntityField dataclass (not dict) since decoder converts it
    assert template.doc == "test_m4i_data_attribute"
    assert template.name == "testing_kafka_field_2"
    assert template.type == KafkaTopicEntityFieldTypeName.RECORD
    child_template = template.fields[0]
    assert child_template.doc == "test_m4i_data_attribute"
    assert child_template.name == "testing_kafka_field_3"
    assert child_template.type == KafkaTopicEntityFieldTypeName.STRING


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
    # top-level fields are created with parent_field="" so qualified_name resolves to field name
    assert index_field_attribute.qualified_name == "testing_kafka_field_1"
    # When convert_to_atlas is called with parent_field="", datasets gets cleared
    # (condition: if parent_field is not None and self.parent_field is not None)
    assert index_field_attribute.datasets == []
    # doc-based attributes are populated since field 1 has doc="test_m4i_data_attribute"
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"

    index_field_attribute = atlas[0].attributes.fields[1].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_2"
    assert index_field_attribute.qualified_name == "testing_kafka_field_2"
    # field 2 has doc=None, so no attributes are added
    assert index_field_attribute.attributes == []
    assert index_field_attribute.datasets == []

    ref_guid_list = list(atlas_ref.keys())
    index_field_attribute = atlas_ref[ref_guid_list[1]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_1"
    assert index_field_attribute.qualified_name == "testing_kafka_field_1"
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"
    assert index_field_attribute.datasets == []

    index_field_attribute = atlas_ref[ref_guid_list[2]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_2"
    assert index_field_attribute.qualified_name == "testing_kafka_field_2"
    assert index_field_attribute.datasets == []

    index_field_attribute = atlas_ref[ref_guid_list[3]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_2"
    assert index_field_attribute.qualified_name == ("testing_kafka_field_2--testing_kafka_field_2")
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"
    index_field_dataset = index_field_attribute.parent_field[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == "testing_kafka_field_2"

    index_field_attribute = atlas_ref[ref_guid_list[4]].attributes  # type: ignore[reportAttributeAccessIssue]
    assert index_field_attribute.name == "testing_kafka_field_3"
    assert index_field_attribute.qualified_name == (
        "testing_kafka_field_2--testing_kafka_field_2--testing_kafka_field_3"
    )
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == "test_m4i_data_attribute"
    index_field_dataset = index_field_attribute.parent_field[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == (
        "testing_kafka_field_2--testing_kafka_field_2"
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
