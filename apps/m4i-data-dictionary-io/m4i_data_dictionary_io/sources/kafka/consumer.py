from typing import Union

from confluent_kafka import Consumer



def consume_message(topic: str, consumer: Consumer) -> Union[bytes, None]:
    """Consume a single message from the provided topic."""
    try:
        consumer.subscribe([topic])
        msg = consumer.poll(5)
    finally:
        consumer.unsubscribe()

    if msg is None or msg.error():
        return None

    return msg.value()
