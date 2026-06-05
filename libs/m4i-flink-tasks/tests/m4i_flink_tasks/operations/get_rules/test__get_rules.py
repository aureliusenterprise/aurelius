"""Tests for the GetRulesFunction class."""

import json

from m4i_flink_tasks.model.gov_data_quality_document import GovDataQualityDocument
from m4i_flink_tasks.operations.get_rules.get_rules import GetRulesFunction


def delete_message() -> str:
    message = {
        "id": "test-id",
        "value": {
            "typeName": "m4i_data_domain",
            "attributes": {"name": "test domain", "qualifiedName": "e7396419-18e4-4515-a41c-47a993f47175"},
            "createTime": None,
            "displayText": "test domain",
            "guid": "6bcc3041-52d0-4156-8e1a-f3f4c1c919de",
            "updateTime": 1733148346473,
        },
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
                        "uniqueAttributes": {"qualifiedName": "domain qualified name"},
                    }
                ],
                "Definition": None,
                "source": [],
                "parentEntity": [],
                "steward": [],
            },
            "createTime": 1733147899357.0,
            "createdBy": "atlas",
            "guid": "test-id",
            "relationshipAttributes": {
                "steward": [],
                "dataDomain": [{"typeName": "m4i_data_domain", "guid": "domain-id"}],
                "parentEntity": [],
                "childEntity": [],
                "attributes": [],
                "source": [],
                "businessOwner": [],
                "meanings": [],
            },
            "updateTime": 1733147917280,
        },
    }
    return json.dumps(message)


def test__delete_entity():
    """Test Governance Data Quality rules when deleting a data domain."""
    func = GetRulesFunction()

    output = func.map(delete_message())

    assert isinstance(output, list)
    assert len(output) == 4

    for rule in output:
        assert isinstance(rule, tuple)
        assert isinstance(rule[0], str)
        assert rule[1] is None


def test__domain_with_dataentity() -> None:
    """Test Governance Data Quality compliance when updating a data entity."""
    func = GetRulesFunction()

    output = func.map(entity_with_domain_message())

    compliant_list = [1, 0, 0, 0, 1, 0]

    assert isinstance(output, list)
    assert len(output) == len(compliant_list)

    for rule, correct in zip(output, compliant_list):
        assert isinstance(rule, tuple)
        assert type(rule[1]) is GovDataQualityDocument  # type: ignore[arg-type]

        gov_data_quality_result: GovDataQualityDocument = rule[1]

        assert gov_data_quality_result.compliant == correct
