import asyncio

import pytest
from m4i_atlas_core import get_entity_audit_events


@pytest.fixture
def request_to_make():
    return {
        "qualifiedName": "testing_m4i_index_pattern",
        "name": "testing_m4i_index_pattern",
        "description": "something",
        "indexPattern": "pattern",
        "updatedAt": "updated at",
        "version": "VERSION",
        "creator": [
            "test_m4i_person"
        ],
        "parentDataset": [
            "test_m4i_visualization"
        ]
    }


path = '/lin_api/entity/indexPattern_entity/'
entity_qn = "testing_m4i_index_pattern"
entity_type = "m4i_index_pattern"


def test_index_pattern_get(client):
    t = client.get(path)
    assert t.status_code == 200
    # END test_index_pattern_get


def test_index_pattern_post(client, request_to_make, check_made, cleanup):
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_index_pattern_post


def test_index_pattern_post_potency_double(client, request_to_make, check_made, cleanup):
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))

    # Run Same request a second time and check it is not recreated.
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 0, 'UPDATE': 0, 'DELETE': 0}
    guid_2 = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))

    ## The audits should be only 1
    assert guid == guid_2
    audits = asyncio.run(get_entity_audit_events(entity_guid=guid))
    assert len(audits) == 1  ## the same should not make new Audits

    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_index_pattern_post_potency_double


def test_index_pattern_post_potency_diff(client, request_to_make, check_made, cleanup):
    request_diff = request_to_make.copy()
    request_diff['description'] = "new_description"
    assert request_to_make != request_diff

    # Run first time and check it creates
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))

    # Run Same request a second time and check it is not recreated.
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_diff)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 0, 'UPDATE': 1, 'DELETE': 0}
    guid_2 = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))

    ## The audits should be 2 since something is different
    assert guid == guid_2
    audits = asyncio.run(get_entity_audit_events(entity_guid=guid))
    assert len(audits) == 2  ## Should be new Audit

    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))
# END test_index_pattern_post_potency_diff
