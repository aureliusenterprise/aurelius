from .KSQL_Model import KSQL


def test__create_ksql_from_dict():
    """
    Tests whether or not a `KSQL` can be created from a dict with its attributes
    """

    ksql = {
        "name": "TESTTABLE1",
        "env": "dev",
        "cluster": "cluster1",
        "kafka_topic": "transactions",
        "value_format": "AVRO",
        "query": "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');",
        "properties": "{'ksql.streams.auto.offset.reset': 'earliest'}"

    }

    instance = KSQL.from_dict(ksql)

    assert instance.name == "TESTTABLE1"
    assert instance._qualified_name() == 'dev--cluster1--testtable1'


# END test__create_ksql_from_dict

def test__create_ksql_from_json():
    """
    Tests whether or not a `ksql` can be created from a json string with its attributes
    """

    ksql = (
        """
        {
        "name": "TESTTABLE1",
        "env": "dev",
        "cluster": "cluster1",
        "kafka_topic": "transactions",
        "value_format": "AVRO",
        "query": "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');",
        "properties": "{'ksql.streams.auto.offset.reset': 'earliest'}"

    }
        """
    )

    instance = KSQL.from_json(ksql)

    assert instance.name == "TESTTABLE1"
    assert instance.value_format == "AVRO"
    assert instance.query == "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');"
    assert instance.properties == "{'ksql.streams.auto.offset.reset': 'earliest'}"
    assert instance.kafka_topic == "transactions"
    assert instance._qualified_name() == 'dev--cluster1--testtable1'


# END test__create_ksql_from_json


def test__ksql_calculates_correct_qualified_name():
    """
    Tests whether or not the generated qualified name matches the expected format
    """

    ksql = {
        "name": "TESTTABLE1",
        "env": "dev",
        "cluster": "cluster1",
        "kafka_topic": "transactions",
        "value_format": "AVRO",
        "query": "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');",
        "properties": "{'ksql.streams.auto.offset.reset': 'earliest'}"

    }

    instance = KSQL.from_dict(ksql)

    assert instance._qualified_name() == 'dev--cluster1--testtable1'


# END test__ksql_calculates_correct_qualified_name


def test__ksql_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    ksql = {
        "name": "TESTTABLE1",
        "env": "dev",
        "cluster": "cluster1",
        "kafka_topic": "transactions",
        "value_format": "AVRO",
        "query": "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');",
        "properties": "{'ksql.streams.auto.offset.reset': 'earliest'}"

    }

    instance = KSQL.from_dict(ksql)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert instance.name == "TESTTABLE1"
    assert instance.value_format == "AVRO"
    assert instance.query == "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');"
    assert instance.properties == "{'ksql.streams.auto.offset.reset': 'earliest'}"
    # assert instance.kafka_topic == "transactions"
    assert instance._qualified_name() == 'dev--cluster1--testtable1'


# END test__ksql_convert_to_atlas_entity

def test__ksql_convert_to_atlas_entity_with_kafka_topic():
    """
    Tests whether or not the `Child Dataset` field is correctly converted to the atlas format.
    """

    ksql = {
        "name": "TESTTABLE1",
        "env": "dev",
        "cluster": "cluster1",
        "kafka_topic": "transactions",
        "value_format": "AVRO",
        "query": "CREATE OR REPLACE TABLE IF NOT EXISTS TESTTABLE1 ( ID STRING PRIMARY KEY, AMOUNT DOUBLE ) WITH (KAFKA_TOPIC='transactions', VALUE_FORMAT = 'AVRO');",
        "properties": "{'ksql.streams.auto.offset.reset': 'earliest'}"

    }

    instance = KSQL.from_dict(ksql)

    atlas_instance = instance.convert_to_atlas()
    atlas_attributes = atlas_instance.attributes

    atlas_kafka_topic = atlas_attributes.kafka_topic[0]

    assert atlas_kafka_topic is not None
    assert atlas_kafka_topic.type_name == "m4i_kafka_topic"
    assert getattr(atlas_kafka_topic.unique_attributes,
                   "qualified_name") == instance.kafka_topic
# END test__ksql_convert_to_atlas_entity_with_kafka_topic
