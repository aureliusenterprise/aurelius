import pytest

from .generic_process_model import GenericProcess


@pytest.fixture
def generic_process():
    return {
        "qualifiedName": "test_m4i_generic_process",
        "name": "test_m4i_generic_process",
        "processOwner": "test_m4i_person",
        "description": "something",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "source": [
            "test_m4i_source"
        ]
    }


def test__create_data_attribute_from_dict(generic_process):
    """
    Tests whether or not a `generic process` can be created from a dict with its attributes
    """

    instance = GenericProcess.from_dict(generic_process)

    assert instance.qualified_name == "test_m4i_generic_process"
    assert instance.name == "test_m4i_generic_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "something"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.source == ["test_m4i_source"]


# END test__create_data_attribute_from_dict


def test__create_data_attribute_from_json(generic_process):
    """
    Tests whether or not a `generic process` can be created from a dict with its attributes
    """

    generic_process = (
        """{
        "qualifiedName": "test_m4i_generic_process",
        "name": "test_m4i_generic_process",
        "processOwner": "test_m4i_person",
        "description": "something",
        "inputs": [
            "test_m4i_dataset"
        ],
        "outputs": [
            "test_m4i_dataset"
        ],
        "source": [
            "test_m4i_source"
        ]
    }"""
    )

    instance = GenericProcess.from_json(generic_process)

    assert instance.qualified_name == "test_m4i_generic_process"
    assert instance.name == "test_m4i_generic_process"
    assert instance.process_owner == "test_m4i_person"
    assert instance.description == "something"
    assert instance.inputs == ["test_m4i_dataset"]
    assert instance.outputs == ["test_m4i_dataset"]
    assert instance.source == ["test_m4i_source"]


# END test__create_data_attribute_from_json


def test__data_attribute_convert_to_atlas_entity(generic_process):
    """
    Tests whether or not all fields are correctly converted to the atlas format.
    """

    instance = GenericProcess.from_dict(generic_process)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes
    assert atlas_attributes.qualified_name == instance.qualified_name
    assert atlas_attributes.name == instance.name
    assert atlas_attributes.description == instance.description

    atlas_process_owner = atlas_attributes.process_owner[0]
    assert atlas_process_owner is not None
    assert getattr(atlas_process_owner.unique_attributes, "qualified_name") == instance.process_owner

    atlas_inputs = atlas_attributes.inputs[0]
    assert atlas_inputs is not None
    assert getattr(atlas_inputs.unique_attributes, "qualified_name") == instance.inputs[0]

    atlas_outputs = atlas_attributes.outputs[0]
    assert atlas_outputs is not None
    assert getattr(atlas_outputs.unique_attributes, "qualified_name") == instance.outputs[0]

    atlas_source = atlas_attributes.source[0]
    assert atlas_source is not None
    assert getattr(atlas_source.unique_attributes, "qualified_name") == instance.source[0]

# END test__data_attribute_convert_to_atlas_entity
