import pytest

from ..core import ObjectId, Attributes
from .BusinessDataset import BusinessDataset, BusinessDatasetAttributes


@pytest.fixture
def dataset():
    return BusinessDataset(
        attributes=BusinessDatasetAttributes(
            qualified_name='Test Dataset',
            name='Test Dataset',
            definition='A test dataset',
            collections=[
                ObjectId(
                    type_name='m4i_collection',
                    guid="test1",
                    unique_attributes=Attributes()
                )
            ],
            parent_dataset=[
                ObjectId(
                    type_name='m4i_dataset',
                    guid="test2",
                    unique_attributes=Attributes()
                )
            ],
            child_dataset=[
                ObjectId(
                    type_name='m4i_dataset',
                    guid="test3",
                    unique_attributes=Attributes()
                )
            ],
            fields=[
                ObjectId(
                    type_name='m4i_field',
                    guid="test4",
                    unique_attributes=Attributes()
                )
            ],
            source=[
                ObjectId(
                    type_name='m4i_source',
                    guid="test5",
                    unique_attributes=Attributes()
                )
            ]
        ),
    )


def test__from_json(dataset: BusinessDataset):
    # Serialize to JSON
    json_str = dataset.to_json()

    # Deserialize from JSON
    deserialized_dataset: BusinessDataset = BusinessDataset.from_json(json_str)

    # Check that the attributes were initialized correctly
    assert deserialized_dataset.attributes.name == dataset.attributes.name
    assert deserialized_dataset.attributes.definition == dataset.attributes.definition
    assert deserialized_dataset.attributes.collections == dataset.attributes.collections
    assert deserialized_dataset.attributes.parent_dataset == dataset.attributes.parent_dataset
    assert deserialized_dataset.attributes.child_dataset == dataset.attributes.child_dataset
    assert deserialized_dataset.attributes.fields == dataset.attributes.fields
    assert deserialized_dataset.attributes.source == dataset.attributes.source
