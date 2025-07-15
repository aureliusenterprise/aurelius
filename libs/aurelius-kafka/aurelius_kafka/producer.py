import logging
from collections.abc import Callable, Iterable

from confluent_kafka import KafkaError, Message, Producer

type KafkaProducerCallbackFn = Callable[[KafkaError | None, Message], None]

LOGGER = logging.getLogger("KafkaProducer")


class KafkaProducer:
    """A generic Kafka producer that implements basic control flow for producing messages to a Kafka topic."""

    def __init__(
        self,
        producer: Producer,
        *,
        callback: KafkaProducerCallbackFn | None = None,
    ) -> None:
        """
        Initialize the KafkaProducer with a Producer instance and an optional callback function.

        Args:
            producer (Producer): An instance of confluent_kafka.Producer to send messages.
            callback (KafkaProducerCallbackFn | None): An optional callback function to handle message delivery status.
        """
        self._producer = producer
        self._callback = callback if callback is not None else self._default_callback

    def batch(
        self,
        topic: str,
        messages: Iterable[tuple[bytes | None, bytes | None]],
        *,
        flush: bool = True,
    ) -> None:
        """
        Produce a batch of messages to the Kafka topic.

        This method flushes the producer only after all messages have been produced.

        Args:
            topic: The Kafka topic to produce the messages to.
            messages: An iterable of tuples containing the key and value of each message.
            flush: Whether to flush the producer after sending the messages.
        """
        for message in messages:
            self.produce(topic, message, flush=False)

        if flush:
            self._producer.flush()

    def produce(
        self,
        topic: str,
        message: tuple[bytes | None, bytes | None],
        *,
        flush: bool = True,
    ) -> None:
        """
        Produce the given message to the Kafka topic.

        Args:
            topic: The Kafka topic to produce the message to.
            message: A tuple containing the key and value of the message.
            flush: Whether to flush the producer after sending the message.
        """
        key, value = message

        if value is None:
            LOGGER.info("Producing tombstone message with key %s to topic %s", key, topic)
        else:
            LOGGER.info("Producing message with key %s to topic %s", key, topic)

        self._producer.produce(
            topic,
            key=key,
            value=value,
            callback=self._callback,
        )

        self._producer.poll(0)

        if flush:
            self._producer.flush()

    def flush(self) -> None:
        """Flush the producer to ensure all messages are sent."""
        LOGGER.info("Flushing producer to ensure all messages are sent")
        self._producer.flush()

    def _default_callback(self, err: KafkaError | None, msg: Message) -> None:
        """Callback function to handle message delivery status."""
        if err is not None:
            LOGGER.error("Message delivery failed: %s", err)
        else:
            LOGGER.info("Message delivered to %s [%s]", msg.topic(), msg.partition())
