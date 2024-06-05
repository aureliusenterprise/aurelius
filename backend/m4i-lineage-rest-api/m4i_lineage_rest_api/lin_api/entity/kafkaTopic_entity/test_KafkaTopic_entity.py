import asyncio

import pytest
from m4i_atlas_core import get_entity_audit_events


@pytest.fixture
def request_to_make():
    return {
        "name": "testing_m4i_kafka_topic",
        "cluster": "test_m4i_kafka_cluster",
        "environment": "test_m4i_confluent_environment",
        "partitions": 3,
        "replicas": 2,
        "key_schema": "string",
        "value_schema": {
            "fields": [
                {
                    "name": "testing_kafka_field_1",
                    "doc": "test_m4i_data_attribute",
                    "type": "string"
                },
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
                                    "type": "string"
                                }
                            ],
                            "name": "testing_kafka_field_2",
                            "doc": "test_m4i_data_attribute",
                            "type": "record"
                        }
                    ]
                }
            ],
            "name": "testing_m4i_kafka_topic__value",
            "doc": None,
            "namespace": "namespace",
            "type": "record"
        }
    }


path = '/lin_api/entity/kafkaTopic_entity/'
entity_qn = "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic"
entity_type = "m4i_kafka_topic"
fields_qn = [
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_1",
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_2",
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_2--testing_kafka_field_2",
    "test_m4i_confluent_environment--test_m4i_kafka_cluster--testing_m4i_kafka_topic--testing_kafka_field_2--testing_kafka_field_2--testing_kafka_field_3"
]
collection_qn = "test_m4i_confluent_environment--test_m4i_kafka_cluster--data"


def test_kafka_topic_get(client):
    t = client.get(path)
    assert t.status_code == 200
    # END test_kafka_topic_get


def test_kafka_topic_post(client, request_to_make, check_made, cleanup):
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 6, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))
    for qn in fields_qn:
        guid = asyncio.run(check_made(entity_qn=qn, entity_type="m4i_kafka_field"))
        asyncio.run(cleanup(guid=guid, entity_qn=qn, entity_type="m4i_kafka_field"))
    guid = asyncio.run(check_made(entity_qn=collection_qn, entity_type="m4i_collection"))
    asyncio.run(cleanup(guid=guid, entity_qn=collection_qn, entity_type="m4i_collection"))


# END test_kafka_topic_post


def test_kafka_topic_post_potency_double(client, request_to_make, check_made, cleanup):
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 6, 'UPDATE': 2, 'DELETE': 0}
    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))

    # Run Same request a second time and check that only dataset is updated.
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 0, 'UPDATE': 1, 'DELETE': 0}
    guid_2 = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))

    ## The audits should be only 1
    assert guid == guid_2
    audits = asyncio.run(get_entity_audit_events(entity_guid=guid))
    assert len(audits) == 2  ## the same should not make new Audits

    # Run Same request a third time and check for no updates
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200
    assert t.json == {'CREATE': 0, 'UPDATE': 0, 'DELETE': 0}
    guid_2 = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))

    ## The audits should be only 1
    assert guid == guid_2
    audits = asyncio.run(get_entity_audit_events(entity_guid=guid))
    assert len(audits) == 2  ## the same should not make new Audits

    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))
    for qn in fields_qn:
        guid = asyncio.run(check_made(entity_qn=qn, entity_type="m4i_kafka_field"))
        asyncio.run(cleanup(guid=guid, entity_qn=qn, entity_type="m4i_kafka_field"))
    guid = asyncio.run(check_made(entity_qn=collection_qn, entity_type="m4i_collection"))
    asyncio.run(cleanup(guid=guid, entity_qn=collection_qn, entity_type="m4i_collection"))


# END test_kafka_topic_post_potency_double


def test_kafka_topic_post_potency_diff(client, request_to_make, check_made, cleanup):
    request_diff = request_to_make.copy()
    request_diff['partitions'] = 10
    assert request_to_make != request_diff

    # Run first time and check it creates
    t = client.post(path, headers={"Content-Type": "application/json"}, json=request_to_make)
    assert t.status_code == 200  # Does it claim to have been made?
    assert t.json == {'CREATE': 6, 'UPDATE': 2, 'DELETE': 0}
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

    guid = asyncio.run(check_made(entity_qn=entity_qn, entity_type=entity_type))
    asyncio.run(cleanup(guid=guid, entity_qn=entity_qn, entity_type=entity_type))
    for qn in fields_qn:
        guid = asyncio.run(check_made(entity_qn=qn, entity_type="m4i_kafka_field"))
        asyncio.run(cleanup(guid=guid, entity_qn=qn, entity_type="m4i_kafka_field"))
    guid = asyncio.run(check_made(entity_qn=collection_qn, entity_type="m4i_collection"))
    asyncio.run(cleanup(guid=guid, entity_qn=collection_qn, entity_type="m4i_collection"))
# END test_kafka_topic_post_potency_diff
