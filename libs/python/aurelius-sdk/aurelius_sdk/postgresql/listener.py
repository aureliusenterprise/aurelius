import logging
from collections.abc import Callable, Generator
from types import TracebackType
from typing import Self

import psycopg
from psycopg.sql import SQL, Identifier

LOGGER = logging.getLogger(__name__)
LISTENER_NOT_RUNNING_ERROR = "PostgreSQL listener is not running; cannot iterate notifications"

type ConsumerCallback = Callable[[psycopg.Notify], None]


class PostgresListener:
    """Provides a simple interface for subscribing to PostgreSQL notifications on a single connection."""

    def __init__(
        self,
        connection: psycopg.Connection,
        channel: str,
    ) -> None:
        self._connection = connection
        self._channel = channel
        self._notifies: Generator[psycopg.Notify] | None = None

    def start(self) -> None:
        """Start LISTEN and initialize the notification generator."""
        if self.is_running:
            return

        LOGGER.debug("Starting PostgreSQL listener for channel '%s'", self._channel)

        try:
            self._connection.execute(SQL("LISTEN {channel};").format(channel=Identifier(self._channel)))
            self._notifies = self._connection.notifies()
        except psycopg.Error:
            LOGGER.exception(
                "Failed to start PostgreSQL listener for channel '%s'; cleaning up partial initialisation",
                self._channel,
            )
            self._cleanup_resources()
            raise

        LOGGER.info("PostgreSQL listener for channel '%s' started", self._channel)

    def stop(self) -> None:
        """Stop listening and release listener resources."""
        LOGGER.debug("Stopping PostgreSQL listener for channel '%s'", self._channel)
        self._cleanup_resources()
        LOGGER.info("PostgreSQL listener for channel '%s' stopped", self._channel)

    @property
    def is_running(self) -> bool:
        """Check if the listener is currently running."""
        return self._notifies is not None

    def _cleanup_resources(self) -> None:
        """Best-effort cleanup for startup failures and normal shutdown."""
        try:
            self._connection.execute(SQL("UNLISTEN {channel};").format(channel=Identifier(self._channel)))
        except psycopg.Error:
            LOGGER.exception("Failed to UNLISTEN from PostgreSQL notification channel '%s'", self._channel)
        try:
            if self._notifies:
                self._notifies.close()
        except psycopg.Error, RuntimeError:
            LOGGER.exception("Failed to close PostgreSQL notification generator for channel '%s'", self._channel)
        finally:
            self._notifies = None

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

    def __iter__(self) -> Generator[psycopg.Notify]:
        """Yield notifications directly from psycopg when the listener is running."""
        if self._notifies is None:
            raise RuntimeError(LISTENER_NOT_RUNNING_ERROR)

        yield from self._notifies
