import asyncio

import pytest
from m4i_atlas_core import get_entity_audit_events


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_kafka_cluster",
        "kafka_replicas": 1,
        "kafka_partitions": 2,
        "confluent_environment": "test_m4i_confluent_environment",
    }


path = '/lin_api/entity/kafkaCluster_entity/'
entity_qn = "test_m4i_confluent_environment--testing_m4i_kafka_cluster"
entity_type = "m4i_kafka_cluster"


def test_kafka_cluster_get(client):
    t = client.get(path)
    assert t.status_code == 200
    # END test_kafka_cluster_get


def test_kafka_cluster_post(client, request_to_make, check_made, cleanup):
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))


# END test_kafka_cluster_post


def test_kafka_cluster_post_potency_double(client, request_to_make, check_made, cleanup):
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
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


# END test_kafka_cluster_post_potency_double


def test_kafka_cluster_post_potency_diff(client, request_to_make, check_made, cleanup):
    request_diff = request_to_make.copy()
    request_diff['kafka_replicas'] = 10
    assert request_to_make != request_diff

    # Run first time and check it creates
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 1, 'UPDATE': 1, 'DELETE': 0}
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
# END test_kafka_cluster_post_potency_diff
