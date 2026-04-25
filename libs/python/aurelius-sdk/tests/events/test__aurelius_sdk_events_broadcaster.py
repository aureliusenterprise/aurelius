import queue
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from aurelius_sdk.events import Broadcaster


@dataclass
class EventSettings:
    """Typed test settings for event broadcaster tests."""

    cdc_subscriber_queue_maxsize: int = 1


@pytest.fixture
def event_settings() -> EventSettings:
    """Return minimal settings required by Broadcaster."""
    return EventSettings()


def test__broadcaster_subscribe_increments_subscriber_count(event_settings: EventSettings) -> None:
    """subscribe() should add a queue and increment subscriber_count."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)

    subscriber_queue = broadcaster.subscribe()

    assert isinstance(subscriber_queue, queue.Queue)
    assert broadcaster.subscriber_count == 1


def test__broadcaster_unsubscribe_decrements_subscriber_count(event_settings: EventSettings) -> None:
    """unsubscribe() should remove a queue and decrement subscriber_count."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)
    subscriber_queue = broadcaster.subscribe()

    broadcaster.unsubscribe(subscriber_queue)

    assert broadcaster.subscriber_count == 0


def test__broadcaster_unsubscribe_unknown_queue_is_noop(event_settings: EventSettings) -> None:
    """unsubscribe() should be a no-op for a queue that is not subscribed."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)
    known_queue = broadcaster.subscribe()
    unknown_queue: queue.Queue[str] = queue.Queue(maxsize=1)

    broadcaster.unsubscribe(unknown_queue)

    assert broadcaster.subscriber_count == 1
    broadcaster.unsubscribe(known_queue)
    assert broadcaster.subscriber_count == 0


def test__broadcaster_broadcast_fans_out_to_all_subscribers(event_settings: EventSettings) -> None:
    """broadcast() should deliver the event to all currently subscribed queues."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)
    queue_a = broadcaster.subscribe()
    queue_b = broadcaster.subscribe()

    broadcaster.broadcast("test_event")

    assert queue_a.get_nowait() == "test_event"
    assert queue_b.get_nowait() == "test_event"


def test__broadcaster_broadcast_with_no_subscribers_is_noop(event_settings: EventSettings) -> None:
    """broadcast() should safely no-op when there are no subscribers."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)

    broadcaster.broadcast("test_event")

    assert broadcaster.subscriber_count == 0


def test__broadcaster_broadcast_drops_oldest_when_queue_full(event_settings: EventSettings) -> None:
    """broadcast() should evict the oldest item when a subscriber queue is full."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)
    subscriber_queue = broadcaster.subscribe()

    broadcaster.broadcast("old_event")
    broadcaster.broadcast("new_event")

    assert subscriber_queue.get_nowait() == "new_event"


def test__broadcaster_broadcast_drops_event_when_queue_is_empty_after_full(event_settings: EventSettings) -> None:
    """broadcast() should skip a queue when full and unable to evict an event."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)

    class QueueThatCannotAcceptOrEvict(queue.Queue[str]):
        def put_nowait(self, item: str) -> None:
            del item
            raise queue.Full

        def get_nowait(self) -> str:
            raise queue.Empty

    stuck_queue = QueueThatCannotAcceptOrEvict()
    subscribers = broadcaster._subscribers  # noqa: SLF001
    subscribers.add(stuck_queue)

    broadcaster.broadcast("test_event")


def test__broadcaster_broadcast_warns_when_queue_stays_full_after_drop(
    event_settings: EventSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """broadcast() should warn when a queue stays full after dropping oldest event."""
    broadcaster: Broadcaster[str] = Broadcaster(settings=event_settings)

    class QueueThatStaysFull(queue.Queue[str]):
        def __init__(self) -> None:
            self.put_attempts = 0

        def put_nowait(self, item: str) -> None:
            del item
            self.put_attempts += 1
            raise queue.Full

        def get_nowait(self) -> str:
            return "test_event"

    stuck_queue = QueueThatStaysFull()
    subscribers = broadcaster._subscribers  # noqa: SLF001
    subscribers.add(stuck_queue)
    warning_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.events.LOGGER.warning", warning_spy)

    broadcaster.broadcast("test_event")

    assert stuck_queue.put_attempts == 2
    warning_spy.assert_called_once()
