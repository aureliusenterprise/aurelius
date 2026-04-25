import logging
import queue
import threading
from typing import Protocol

LOGGER = logging.getLogger(__name__)


class BroadcasterSettings(Protocol):
    """Settings required by Broadcaster."""

    cdc_subscriber_queue_maxsize: int


class Broadcaster[T]:
    """Multiple subscribers can register to receive events."""

    def __init__(self, settings: BroadcasterSettings) -> None:
        self._settings = settings
        self._subscribers: set[queue.Queue[T]] = set()
        self._subscribers_lock = threading.Lock()

    def subscribe(self) -> queue.Queue[T]:
        """Register a new subscriber and return its event queue."""
        subscriber_queue: queue.Queue[T] = queue.Queue(
            maxsize=self._settings.cdc_subscriber_queue_maxsize,
        )
        with self._subscribers_lock:
            self._subscribers.add(subscriber_queue)
            subscriber_count = len(self._subscribers)
        LOGGER.debug("Subscriber added (total=%d)", subscriber_count)
        return subscriber_queue

    def unsubscribe(self, subscriber_queue: queue.Queue[T]) -> None:
        """Remove a subscriber's queue from the broadcast set."""
        with self._subscribers_lock:
            self._subscribers.discard(subscriber_queue)
            subscriber_count = len(self._subscribers)
        LOGGER.debug("Subscriber removed (total=%d)", subscriber_count)

    @property
    def subscriber_count(self) -> int:
        """Return the number of currently-subscribed clients."""
        with self._subscribers_lock:
            return len(self._subscribers)

    def broadcast(self, event: T) -> None:
        """Deliver an event to every currently-subscribed queue."""
        with self._subscribers_lock:
            subscribers = tuple(self._subscribers)

        for subscriber_queue in subscribers:
            try:
                subscriber_queue.put_nowait(event)
            except queue.Full:
                # Drop the oldest event for slow subscribers so queue growth is bounded.
                try:
                    subscriber_queue.get_nowait()
                except queue.Empty:
                    continue

                try:
                    subscriber_queue.put_nowait(event)
                except queue.Full:
                    LOGGER.warning("Dropping event for slow subscriber; queue remains full")
