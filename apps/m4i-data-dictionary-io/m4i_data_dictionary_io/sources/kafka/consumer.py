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
        print(f"Error consuming message from topic {topic}: {msg.error() if msg else 'No message received'}")
        return None
    print(f"Consumed message from topic {topic}: {msg.value()}")
    return msg.value()
