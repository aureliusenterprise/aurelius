from m4i_flink_tasks.model.gov_data_quality_document import GovDataQualityDocument
from m4i_flink_tasks.operations.get_rules.get_rules import GetRules
import pytest
from pyflink.datastream import StreamExecutionEnvironment
import json

def delete_message() -> str:
    message = {
      "id": "test-id",
      "value": {
        "typeName": "m4i_data_domain",
        "attributes": {
          "name": "test domain",
          "qualifiedName": "e7396419-18e4-4515-a41c-47a993f47175"
        },
        "createTime": None,
        "displayText": "test domain",
        "guid": "6bcc3041-52d0-4156-8e1a-f3f4c1c919de",
        "updateTime": 1733148346473,
      }
    }
    return json.dumps(message)


def entity_with_domain_message() -> str:
    message = {
        "id": "test-id",
        "value": {
          "typeName": "m4i_data_entity",
          "attributes": {
            "qualifiedName": "295c0c83-daac-4042-8b70-b60fab42063b",
            "name": "test entity",
            "unmappedAttributes": {},
            "attributes": [],
            "businessOwner": [],
            "childEntity": [],
            "dataDomain": [
              {
                "typeName": "m4i_data_domain",
                "guid": "domain-id",
                "uniqueAttributes": {
                  "qualifiedName": "domain qualified name"
                }
              }
            ],
            "definition": None,
            "source": [],
            "parentEntity": [],
            "steward": []
          },
          "createTime": 1733147899357.0,
          "createdBy": "atlas",
          "guid": "test-id",
          "relationshipAttributes": {
            "steward": [],
            "dataDomain": [
              {
                "typeName": "m4i_data_domain",
                "guid": "domain-id",
              }
            ],
            "parentEntity": [],
            "childEntity": [],
            "attributes": [],
            "source": [],
            "businessOwner": [],
            "meanings": []
          },
          "updateTime": 1733147917280,
        }
    }
    return json.dumps(message)

@pytest.fixture()
def environment() -> StreamExecutionEnvironment:
    """
    Provide a StreamExecutionEnvironment for testing.

    This fixture initializes a Flink StreamExecutionEnvironment
    with a parallelism of 1 for consistent testing.
    """
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    return env


def test__delete_entity(
    environment: StreamExecutionEnvironment
):
    """Test Governance Data Quality rules when deleting a data domain."""

    data_stream = environment.from_collection([delete_message()])

    get_rules = GetRules(data_stream)

    output = list(get_rules.main.execute_and_collect())

    assert len(output) == 4

    for rule in output:
        assert isinstance(rule, tuple)
        assert isinstance(rule[0], str)
        assert rule[1] is None

def test__domain_with_dataentity(
    environment: StreamExecutionEnvironment
) -> None:
    """Test Governance Data Quality compliance when updating a data entity."""

    data_stream = environment.from_collection([entity_with_domain_message()])

    get_rules = GetRules(data_stream)

    output = list(get_rules.main.execute_and_collect())

    compliant_list = [1, 0, 0, 0, 1, 0]

    assert len(output) == len(compliant_list)

    for rule, correct in zip(output, compliant_list):

        assert isinstance(rule, tuple)
        assert type(rule[1]) is GovDataQualityDocument

        gov_data_quality_result = rule[1]

        assert gov_data_quality_result.compliant == correct
