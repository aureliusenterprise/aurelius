import logging
import select
import threading
from collections.abc import Callable, Sequence
from types import TracebackType
from typing import Protocol, Self

import psycopg2
from psycopg2.sql import SQL, Identifier

LOGGER = logging.getLogger(__name__)

type ConsumerCallback = Callable[[psycopg2.extensions.Notify], None]


class PostgresListenerSettings(Protocol):
    """Settings required by PostgresListener."""

    cdc_epoll_timeout: float
    cdc_shutdown_join_timeout: float


class PostgresListener:
    """Provides a simple interface for subscribing to PostgreSQL notifications on a single connection."""

    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        channel: str,
        settings: PostgresListenerSettings,
    ) -> None:
        self._connection = connection
        self._channel = channel
        self._consumers: set[ConsumerCallback] = set()
        self._settings = settings
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._consumers_lock = threading.Lock()
        self._cursor: psycopg2.extensions.cursor | None = None
        self._epoll: select.epoll | None = None

    def start(self) -> None:
        """Open the shared database connection and start the background polling thread."""
        LOGGER.debug("Starting PostgreSQL listener for channel '%s'", self._channel)

        if self._thread is not None and self._cursor is not None and self._epoll is not None:
            LOGGER.debug("PostgreSQL listener for channel '%s' is already started", self._channel)
            return

        try:
            cursor = self._connection.cursor()

            cursor.execute(SQL("LISTEN {channel};").format(channel=Identifier(self._channel)))

            epoll = select.epoll()
            epoll.register(self._connection, select.EPOLLIN)

            self._cursor = cursor
            self._epoll = epoll

            self._stop_event.clear()
            thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread = thread
            thread.start()
        except (OSError, psycopg2.Error, RuntimeError):
            LOGGER.exception(
                "Failed to start PostgreSQL listener for channel '%s'; cleaning up partial initialisation",
                self._channel,
            )
            self._stop_event.set()
            self._cleanup_resources()
            raise

        LOGGER.info("PostgreSQL listener for channel '%s' started", self._channel)

    def subscribe(self, consumer: ConsumerCallback) -> None:
        """Add a consumer callback to receive notifications from the poll loop."""
        with self._consumers_lock:
            self._consumers.add(consumer)

        LOGGER.debug(
            "Consumer subscribed to PostgreSQL listener for channel '%s' (total=%d)",
            self._channel,
            len(self._consumers),
        )

    def stop(self) -> None:
        """Signal the polling thread to stop and release all resources."""
        LOGGER.debug("Stopping PostgreSQL listener for channel '%s'", self._channel)

        if self._thread is None and self._cursor is None and self._epoll is None:
            LOGGER.debug("PostgreSQL listener for channel '%s' is already stopped", self._channel)
            return

        self._stop_event.set()
        self._cleanup_resources()

        LOGGER.info("PostgreSQL listener for channel '%s' stopped", self._channel)

    def unsubscribe(self, consumer: ConsumerCallback) -> None:
        """Remove a consumer callback from the notification set."""
        with self._consumers_lock:
            self._consumers.discard(consumer)

        LOGGER.debug(
            "Consumer unsubscribed from PostgreSQL listener for channel '%s' (total=%d)",
            self._channel,
            len(self._consumers),
        )

    def _cleanup_resources(self) -> None:
        """Best-effort cleanup for both startup failures and normal shutdown."""
        self._close_epoll()
        self._join_thread()
        self._close_cursor()

    def _join_thread(self) -> None:
        """Join the polling thread with timeout to avoid hanging shutdown."""
        if self._thread is not None:
            try:
                self._thread.join(timeout=self._settings.cdc_shutdown_join_timeout)
            except RuntimeError:
                LOGGER.exception("Failed to join PostgreSQL listener polling thread for channel '%s'", self._channel)
            else:
                if self._thread.is_alive():
                    LOGGER.warning(
                        "PostgreSQL listener polling thread for channel '%s' did not stop before timeout",
                        self._channel,
                    )
            finally:
                self._thread = None

    def _close_cursor(self) -> None:
        """Best-effort close of the LISTEN cursor."""
        if self._cursor is not None:
            try:
                self._cursor.execute(SQL("UNLISTEN {channel};").format(channel=Identifier(self._channel)))
            except psycopg2.Error:
                LOGGER.exception("Failed to UNLISTEN from PostgreSQL notification channel '%s'", self._channel)
            try:
                self._cursor.close()
            except psycopg2.Error:
                LOGGER.exception("Failed to close PostgreSQL listener cursor for channel '%s'", self._channel)
            finally:
                self._cursor = None

    def _close_epoll(self) -> None:
        """Best-effort close of epoll to wake/stop the polling thread quickly."""
        if self._epoll is not None:
            try:
                self._epoll.close()
            except OSError:
                LOGGER.exception("Failed to close PostgreSQL listener epoll instance for channel '%s'", self._channel)
            finally:
                self._epoll = None

    def __enter__(self) -> Self:
        """Start the listener when entering a context manager block."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the listener when exiting a context manager block."""
        self.stop()

    def _poll_loop(self) -> None:
        """Background thread: poll epoll and fan out notifications to all subscriber callbacks."""
        epoll = self._epoll
        connection = self._connection

        if epoll is None or connection is None:
            LOGGER.error("PostgreSQL listener poll loop started without proper initialisation")
            return

        while not self._stop_event.is_set():
            if not self._handle_poll_cycle(epoll, connection):
                break

    def _handle_poll_cycle(
        self,
        epoll: select.epoll,
        connection: psycopg2.extensions.connection,
    ) -> bool:
        """Handle a single poll cycle. Returns False if polling should stop."""
        try:
            events = epoll.poll(timeout=self._settings.cdc_epoll_timeout)
        except (OSError, ValueError):
            LOGGER.exception("epoll error in PostgreSQL listener; stopping poll loop")
            return False

        if not events:
            return True

        try:
            connection.poll()
        except psycopg2.Error:
            LOGGER.exception(
                "psycopg2 poll error in PostgreSQL listener for channel '%s'; stopping poll loop",
                self._channel,
            )
            return False

        with self._consumers_lock:
            consumers = tuple(self._consumers)

        self._process_notifications(connection, consumers)

        return True

    def _process_notifications(
        self,
        connection: psycopg2.extensions.connection,
        consumers: Sequence[ConsumerCallback],
    ) -> None:
        """Process all pending notifications and fan out to subscribers."""
        while connection.notifies:
            notify = connection.notifies.pop(0)
            LOGGER.debug("PostgreSQL listener received notification for channel '%s': %s", self._channel, notify)

            for consumer in consumers:
                try:
                    consumer(notify)
                except Exception:
                    LOGGER.exception(
                        "Consumer callback failed while handling PostgreSQL notification for channel '%s': %r",
                        self._channel,
                        consumer,
                    )
