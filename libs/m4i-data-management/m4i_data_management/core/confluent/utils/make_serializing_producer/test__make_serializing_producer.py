from .make_serializing_producer import make_serializing_producer
from confluent_kafka import KafkaError

def test__make_serializing_producer():
    producer = make_serializing_producer(
        key_schema_id="100021",  # avro--test--key
        value_schema_id="100022"  # avro--test--value
    )

    assert producer is not None
# END test__make_serializing_producer


def test__make_serializing_producer_can_push_message():

    key = {
        "name": "test"
    }

    value = {
        "name": "test"
    }

    topic_name = "avro--test--topic--1"

    producer = make_serializing_producer(
        key_schema_id="100021",
        value_schema_id="100022"
    )

    def evaluate(error: KafkaError, message):
        assert error is None
    # END evaluate

    producer.produce(
        topic=topic_name,
        key=key,
        value=value,
        on_delivery=evaluate
    )

    producer.poll(0)

    producer.flush()
# END test__make_serializing_producer_can_push_message
