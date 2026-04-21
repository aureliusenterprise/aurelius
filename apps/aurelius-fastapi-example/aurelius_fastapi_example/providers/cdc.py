import asyncio
import queue
import select
import threading
from collections.abc import AsyncGenerator, Callable
from functools import cache, partial
from types import TracebackType
from typing import Annotated, Self

import psycopg2
from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, EntityNotification
from fastapi import Depends, Request

from aurelius_fastapi_example.globals import LOGGER

from .settings import Settings


class Broadcaster:
    """A singleton that holds a single PostgreSQL LISTEN connection and multicasts notifications to all subscribers."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._subscribers: set[queue.Queue[psycopg2.extensions.Notify]] = set()
        self._subscribers_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._connection: psycopg2.extensions.connection | None = None
        self._cursor: psycopg2.extensions.cursor | None = None
        self._epoll: select.epoll | None = None

    def start(self) -> None:
        """Open the shared database connection and start the background polling thread."""
        LOGGER.debug("Starting CDC broadcaster")

        if self.is_connected:
            LOGGER.debug("CDC broadcaster is already started")
            return

        try:
            connection = psycopg2.connect(
                host=self._settings.database_host,
                port=self._settings.database_port,
                dbname=self._settings.database_name,
                user=self._settings.database_username,
                password=self._settings.database_password.get_secret_value(),
            )
            connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

            cursor = connection.cursor()
            cursor.execute(f"LISTEN {PG_NOTIFY_ENTITY_CHANNEL};")

            epoll = select.epoll()
            epoll.register(connection, select.EPOLLIN)

            self._connection = connection
            self._cursor = cursor
            self._epoll = epoll

            self._stop_event.clear()
            thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread = thread
            thread.start()
        except (OSError, psycopg2.Error, RuntimeError):
            LOGGER.exception("Failed to start CDC broadcaster; cleaning up partial initialisation")
            self._stop_event.set()
            self._cleanup_resources()
            raise

        LOGGER.info("CDC broadcaster started")

    def stop(self) -> None:
        """Signal the polling thread to stop and release all resources."""
        LOGGER.debug("Stopping CDC broadcaster")

        if not self.is_connected and self._thread is None and self._cursor is None and self._epoll is None:
            LOGGER.debug("CDC broadcaster is already stopped")
            return

        self._stop_event.set()
        self._close_epoll()
        self._join_thread()
        self._close_cursor()
        self._close_connection()

        LOGGER.info("CDC broadcaster stopped")

    def _cleanup_resources(self) -> None:
        """Best-effort cleanup for both startup failures and normal shutdown."""
        self._close_epoll()
        self._join_thread()
        self._close_cursor()
        self._close_connection()

    def _join_thread(self) -> None:
        """Join the polling thread with timeout to avoid hanging shutdown."""
        if self._thread is not None:
            try:
                self._thread.join(timeout=self._settings.cdc_shutdown_join_timeout)
            except RuntimeError:
                LOGGER.exception("Failed to join CDC broadcaster polling thread")
            else:
                if self._thread.is_alive():
                    LOGGER.warning("CDC broadcaster polling thread did not stop before timeout")
            finally:
                self._thread = None

    def _close_cursor(self) -> None:
        """Best-effort close of the LISTEN cursor."""
        if self._cursor is not None:
            try:
                self._cursor.execute(f"UNLISTEN {PG_NOTIFY_ENTITY_CHANNEL};")
            except psycopg2.Error:
                LOGGER.exception("Failed to UNLISTEN from PostgreSQL notification channel")
            try:
                self._cursor.close()
            except psycopg2.Error:
                LOGGER.exception("Failed to close CDC broadcaster cursor")
            finally:
                self._cursor = None

    def _close_epoll(self) -> None:
        """Best-effort close of epoll to wake/stop the polling thread quickly."""
        if self._epoll is not None:
            try:
                self._epoll.close()
            except OSError:
                LOGGER.exception("Failed to close CDC broadcaster epoll instance")
            finally:
                self._epoll = None

    def _close_connection(self) -> None:
        """Best-effort close of the database connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            except psycopg2.Error:
                LOGGER.exception("Failed to close CDC broadcaster database connection")
            finally:
                self._connection = None

    def __enter__(self) -> Self:
        """Start the broadcaster when entering a context manager block."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the broadcaster when exiting a context manager block."""
        self.stop()

    def subscribe(self) -> queue.Queue[psycopg2.extensions.Notify]:
        """Register a new subscriber and return its notification queue."""
        subscriber_queue: queue.Queue[psycopg2.extensions.Notify] = queue.Queue(
            maxsize=self._settings.cdc_subscriber_queue_maxsize,
        )
        with self._subscribers_lock:
            self._subscribers.add(subscriber_queue)
            subscriber_count = len(self._subscribers)
        LOGGER.debug("Subscriber added (total=%d)", subscriber_count)
        return subscriber_queue

    def unsubscribe(self, subscriber_queue: queue.Queue[psycopg2.extensions.Notify]) -> None:
        """Remove a subscriber's queue from the broadcast set."""
        with self._subscribers_lock:
            self._subscribers.discard(subscriber_queue)
            subscriber_count = len(self._subscribers)
        LOGGER.debug("Subscriber removed (total=%d)", subscriber_count)

    @property
    def is_connected(self) -> bool:
        """Return True if the shared database connection is open."""
        return self._connection is not None and self._connection.closed == 0

    @property
    def subscriber_count(self) -> int:
        """Return the number of currently-subscribed clients."""
        with self._subscribers_lock:
            return len(self._subscribers)

    def _poll_loop(self) -> None:
        """Background thread: poll epoll and fan out notifications to all subscriber queues."""
        epoll = self._epoll
        connection = self._connection

        if epoll is None or connection is None:
            LOGGER.error("CDC broadcaster poll loop started without proper initialisation")
            return

        while not self._stop_event.is_set():
            try:
                events = epoll.poll(timeout=self._settings.cdc_epoll_timeout)
            except (OSError, ValueError):
                LOGGER.exception("epoll error in CDC broadcaster; stopping poll loop")
                break

            if not events:
                continue

            try:
                connection.poll()
            except psycopg2.Error:
                LOGGER.exception("psycopg2 poll error in CDC broadcaster; stopping poll loop")
                break

            while connection.notifies:
                notify = connection.notifies.pop(0)
                LOGGER.debug("CDC broadcaster received notification: %s", notify)
                self._broadcast(notify)

    def _broadcast(self, notify: psycopg2.extensions.Notify) -> None:
        """Deliver a notification to every currently-subscribed queue."""
        with self._subscribers_lock:
            subscribers = tuple(self._subscribers)

        for subscriber_queue in subscribers:
            try:
                subscriber_queue.put_nowait(notify)
            except queue.Full:
                # Drop the oldest event for slow subscribers so queue growth is bounded.
                try:
                    subscriber_queue.get_nowait()
                except queue.Empty:
                    continue

                try:
                    subscriber_queue.put_nowait(notify)
                except queue.Full:
                    LOGGER.warning("Dropping CDC event for slow subscriber; queue remains full")


@cache
def get_broadcaster(*, settings: Settings) -> Broadcaster:
    """Return a singleton Broadcaster instance for the application."""
    return Broadcaster(settings=settings)


def notifications(
    broadcaster: Annotated[Broadcaster, Depends(get_broadcaster)],
    request: Request,
    settings: Settings,
) -> Callable[[], AsyncGenerator[EntityNotification]]:
    """Return a factory that streams PostgreSQL notifications via the shared broadcaster."""

    async def listener() -> AsyncGenerator[EntityNotification]:
        """Subscribe to the broadcaster and yield notifications until the client disconnects."""
        subscriber_queue = broadcaster.subscribe()

        try:
            while not (await request.is_disconnected()):
                try:
                    notify = await asyncio.to_thread(
                        partial(
                            subscriber_queue.get,
                            timeout=settings.cdc_disconnect_poll_timeout,
                        ),
                    )
                except asyncio.CancelledError:
                    LOGGER.debug("SSE notification listener cancelled")
                    raise
                except queue.Empty:
                    continue

                LOGGER.debug("SSE listener received notification: %s", notify)
                yield EntityNotification.model_validate_json(notify.payload)
        finally:
            broadcaster.unsubscribe(subscriber_queue)

    return listener
