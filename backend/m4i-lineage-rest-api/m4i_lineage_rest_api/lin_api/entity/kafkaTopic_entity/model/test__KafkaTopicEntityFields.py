import pytest

from .KafkaTopicEntityFields import KafkaTopicEntityField


@pytest.fixture
def data():
    return {
        "name": "payload",
        "type": [
            "null",
            {
                "fields": [
                    {
                        "name": "id",
                        "type": "string"
                    },
                    {
                        "name": "date",
                        "type": [
                            "null",
                            "long"
                        ]
                    },
                    {
                        "name": "name",
                        "type": [
                            "null",
                            "string"
                        ]
                    }
                ],
                "name": "payload",
                "type": "record"
            }
        ]
    }


# END data


def test__create_KafkaTopicApiModel(data: dict):
    model = KafkaTopicEntityField.from_dict(data)
    atlas_attributes = model.type[1].fields
    assert isinstance(atlas_attributes, list)
    assert model
# END def
