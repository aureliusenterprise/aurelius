import pytest
from m4i_atlas_core import ElasticIndex, ElasticField

from .ElasticIndexApiModel import ElasticIndexApiModel
from .ElasticIndexTemplateMappings import ElasticIndexTemplateMappings
from .ElasticIndexTemplateMappingsProperty import ElasticIndexTemplateMappingsProperty
from .ElasticIndexTemplateModel import ElasticIndexTemplateModel


@pytest.fixture
def data():
    return {
        "name": "testing_elastic_index",
        "qualifiedName": "testing_elastic_index",
        "cluster": "test_elastic_cluster",
        "environment": "test_elastic_environment",
        "indexTemplate": {
            "mappings": {
                "_meta": {
                    "testing_elastic_field_1": "test_m4i_data_attribute",
                    "testing_elastic_field_2": ["test_m4i_data_attribute"],
                    "testing_elastic_field_3": {
                        "testing_elastic_field_4": "test_m4i_data_attribute"
                    }
                },
                "properties": {
                    "testing_elastic_field_1": {
                        "type": "keyword"
                    },
                    "testing_elastic_field_2": {
                        "type": "text"
                    },
                    "testing_elastic_field_3": {
                        "properties": {
                            "testing_elastic_field_4": {
                                "type": "text"
                            }
                        }
                    }
                }
            }
        }
    }


# END data


def test__ElasticIndexApiModel_from_dict(data: dict):
    model = ElasticIndexApiModel.from_dict(data)

    assert isinstance(model, ElasticIndexApiModel)
    assert model.name == "testing_elastic_index"
    assert model.environment == "test_elastic_environment"
    assert model.cluster == "test_elastic_cluster"
    assert model.qualified_name == "testing_elastic_index"
    template = model.index_template
    assert isinstance(template, ElasticIndexTemplateModel)
    mapping = template.mappings
    assert isinstance(mapping, ElasticIndexTemplateMappings)
    props = mapping.properties

    assert isinstance(props["testing_elastic_field_1"], ElasticIndexTemplateMappingsProperty)
    assert props["testing_elastic_field_1"].type == "keyword"

    assert isinstance(props["testing_elastic_field_2"], ElasticIndexTemplateMappingsProperty)
    assert props["testing_elastic_field_2"].type == "text"

    assert isinstance(props["testing_elastic_field_3"], ElasticIndexTemplateMappingsProperty)
    assert props["testing_elastic_field_3"].type is None

    assert isinstance(props["testing_elastic_field_3"].properties['testing_elastic_field_4'],
                      ElasticIndexTemplateMappingsProperty)
    assert props["testing_elastic_field_3"].properties['testing_elastic_field_4'].type == "text"


# END test__ElasticIndexApiModel_from_dict


def test__ElasticIndexApiModel_convert_to_atlas_entity(data: dict):
    model = ElasticIndexApiModel.from_dict(data)
    atlas, atlas_ref = model.convert_to_atlas()

    assert isinstance(atlas[0], ElasticIndex)
    index_attributes = atlas[0].attributes
    assert index_attributes.name == model.name
    assert index_attributes.qualified_name == model.qualified_name
    index_collection = index_attributes.collections[0]
    assert index_collection is not None
    assert getattr(index_collection.unique_attributes, "qualified_name") == 'test_elastic_cluster--data'

    index_field_attribute = atlas[0].attributes.fields[0].attributes
    assert index_field_attribute.name == 'testing_elastic_field_1'
    assert index_field_attribute.qualified_name == 'testing_elastic_index--testing_elastic_field_1'
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == 'test_m4i_data_attribute'
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == 'testing_elastic_index'

    index_field_attribute = atlas[0].attributes.fields[1].attributes
    assert index_field_attribute.name == 'testing_elastic_field_2'
    assert index_field_attribute.qualified_name == 'testing_elastic_index--testing_elastic_field_2'
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == 'test_m4i_data_attribute'
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == 'testing_elastic_index'

    index_field_attribute = atlas[0].attributes.fields[2].attributes
    assert index_field_attribute.name == 'testing_elastic_field_3'
    assert index_field_attribute.qualified_name == 'testing_elastic_index--testing_elastic_field_3'
    assert index_field_attribute.child_field == []
    index_field_attributes = index_field_attribute.attributes
    assert index_field_attributes == []
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == 'testing_elastic_index'

    ref_guid_list = list(atlas_ref.keys())
    index_field_attribute = atlas_ref[ref_guid_list[1]].attributes
    assert index_field_attribute.name == 'testing_elastic_field_1'
    assert index_field_attribute.qualified_name == 'testing_elastic_index--testing_elastic_field_1'
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == 'test_m4i_data_attribute'
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == 'testing_elastic_index'

    index_field_attribute = atlas_ref[ref_guid_list[2]].attributes
    assert index_field_attribute.name == 'testing_elastic_field_2'
    assert index_field_attribute.qualified_name == 'testing_elastic_index--testing_elastic_field_2'
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == 'test_m4i_data_attribute'
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == 'testing_elastic_index'

    index_field_attribute = atlas_ref[ref_guid_list[3]].attributes
    assert index_field_attribute.name == 'testing_elastic_field_3'
    assert index_field_attribute.qualified_name == 'testing_elastic_index--testing_elastic_field_3'
    assert index_field_attribute.child_field != []
    index_field_attributes = index_field_attribute.attributes
    assert index_field_attributes == []
    index_field_dataset = index_field_attribute.datasets[0]
    assert index_field_dataset is not None
    assert getattr(index_field_dataset.unique_attributes, "qualified_name") == 'testing_elastic_index'

    index_field_attribute = atlas_ref[ref_guid_list[4]].attributes
    assert index_field_attribute.name == 'testing_elastic_field_4'
    assert index_field_attribute.qualified_name == 'testing_elastic_index--testing_elastic_field_3--testing_elastic_field_4'
    index_field_attributes = index_field_attribute.attributes[0]
    assert index_field_attributes is not None
    assert getattr(index_field_attributes.unique_attributes, "qualified_name") == 'test_m4i_data_attribute'
    index_field_dataset = index_field_attribute.datasets
    assert index_field_dataset == None

# END test__ElasticIndexApiModel_convert_to_atlas_entity
