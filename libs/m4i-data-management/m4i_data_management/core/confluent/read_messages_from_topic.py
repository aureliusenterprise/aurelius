import logging
from typing import Generator, Optional, Tuple

from confluent_kafka import Consumer, KafkaError, KafkaException

from .utils import make_deserializing_consumer

_SENTINEL = None


MessageType = Tuple[str, Optional[str]]

logger = logging.getLogger(__name__)


def _listener(consumer: Consumer, timeout: int = -1) -> MessageType:

    # Listen for new messages on the topic
    message = consumer.poll(timeout)

    # On timeout, the consumer returns `None` instead of a message
    # Assume the stream is exhausted when a timeout occurs while polling
    # Return the `SENTINEL` value to stop the listener
    if message is None:
        return _SENTINEL
    # END IF

    # Check if an error occurred
    error = message.error()

    # If no error, return the message key and value
    if error is None:
        logger.debug(f"{message.key()}: {message.value()}")
        return message.key(), message.value()
    # END IF

    # If the stream is exhausted, return the `SENTINEL` value to stop the listener
    if error.code() == KafkaError._PARTITION_EOF:
        return _SENTINEL
    # END IF

    # Else, raise the error as an exception to stop the listener
    raise KafkaException(error)

# END _listener


def read_messages_from_topic(*topic_name: str, timeout: int = -1, consumer: Consumer = None) -> Generator[MessageType, None, None]:
    """
    Returns a generator that continuously reads messages from the specified topic(s) until the topic is depleted, or until a timeout occurs.

    You can specify the topic(s) from which to read the messages by providing a (set of) `topic_name`.

    When a `timeout` is provided, the listener will stop after no messages have been received for the given number of seconds.
    By default, the generator keeps listening for new messages until the topic is depleted.

    Optionally, you can provide a `consumer` instance to specify the listening behaviour.
    If no `consumer` is provided, an instance with default settings is used.
    """

    if consumer is None:
        consumer = make_deserializing_consumer(enable_auto_commit=False)
    # END IF

    # Subscribe to the topic with the given name. A topic name can also be a regex.
    consumer.subscribe(list(topic_name))

    try:
        # Listen for new events from the consumer until the stream is exhausted
        yield from iter(lambda: _listener(consumer, timeout), _SENTINEL)

        # After the stream is exhausted, commit the current partition offset
        consumer.commit(asynchronous=False)

    except KafkaException as e:

        error = e.args[0]

        if error.code() == KafkaError._NO_OFFSET:
            """
            An exception will be raised by `consumer.commit` when the local offset does not need to be committed.
            This can happen when no new messages were retrieved, or when the local offset was already committed previously.
            This can safely be ignored.

            Reference: https://github.com/confluentinc/confluent-kafka-python/issues/71#issuecomment-260368554
            """

            logger.warning(
                "The local offset did not need to be committed. This is most likely because no new messages were retrieved, or because the local offset was already committed previously."
            )

        else:
            raise
        # END IF

    finally:
        consumer.close()
    # END TRY

# END read_messages_from_topic
