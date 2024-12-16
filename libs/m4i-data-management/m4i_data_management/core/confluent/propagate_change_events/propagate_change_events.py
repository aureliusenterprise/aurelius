import logging
from typing import Any

from confluent_kafka import SerializingProducer
from pandas import Series
from typing_extensions import Literal

from ..utils import make_serializing_producer

log = logging.getLogger(__name__)


def produce_message(producer: SerializingProducer, topic_name: str, key: Any, value: Any, poll_duration: int = 0):
    producer.poll(poll_duration)
    producer.produce(
        topic=topic_name,
        key=key,
        value=value
    )
# END produce_message


def propagate_change_events(
    changes: Series,
    topic_name: str,
    key_schema_type: Literal['avro', 'json', 'string'] = 'string',
    value_schema_type: Literal['avro', 'json', 'string'] = 'string',
    key_schema_id: str = None,
    value_schema_id: str = None
):

    producer = make_serializing_producer(
        value_schema_id=value_schema_id,
        value_schema_type=value_schema_type,
        key_schema_id=key_schema_id,
        key_schema_type=key_schema_type
    )

    try:
        for index, change in changes.iteritems():
            try:
                produce_message(producer, topic_name, index, change)
            except BufferError:
                log.warning("The producer queue is full. Retrying...")
                produce_message(producer, topic_name, index, change, 10)
            # END TRY
        # END LOOP
    finally:
        producer.flush()
    # END TRY
# END propagate_change_events
