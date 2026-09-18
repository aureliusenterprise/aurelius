from collections.abc import Generator
from functools import cache
from typing import Annotated

from fastapi import Depends, HTTPException
from pybreaker import CircuitBreaker, CircuitBreakerError, CircuitBreakerListener, CircuitBreakerState
from sqlalchemy import Engine, create_engine
from sqlmodel import Session

from aurelius_fastapi_example.globals import LOGGER

from .settings import Settings


@cache
def db_circuit_breaker(*, settings: Settings) -> CircuitBreaker:
    """Return a circuit breaker instance for requests to the database."""

    class DbCircuitBreakerListener(CircuitBreakerListener):
        def state_change(
            self,
            cb: CircuitBreaker,
            old_state: CircuitBreakerState | None,
            new_state: CircuitBreakerState | None,
        ) -> None:
            LOGGER.debug("Circuit breaker %s state changed from %s to %s", cb.name, old_state, new_state)

    return CircuitBreaker(
        fail_max=settings.db_fail_max,
        listeners=[DbCircuitBreakerListener()],
        name="db_circuit_breaker",
        reset_timeout=settings.db_reset_timeout,
    )


@cache
def database(*, settings: Settings) -> Engine:
    """Return a database engine instance."""
    database_url = settings.database_url

    engine = create_engine(database_url)
    LOGGER.info("Connected to database %s", str(database_url).split("@")[-1])

    return engine


def session(
    db_circuit_breaker: Annotated[CircuitBreaker, Depends(db_circuit_breaker)],
    db_engine: Annotated[Engine, Depends(database)],
) -> Generator[Session]:
    """Create a database session for executing queries."""
    LOGGER.debug("Creating a new database session")

    try:
        with db_circuit_breaker.calling(), Session(db_engine) as session:
            try:
                yield session
            except Exception:
                LOGGER.error("Rolling back any changes to the database")
                session.rollback()
                raise
    except CircuitBreakerError as e:
        LOGGER.error("Circuit breaker is open for database service")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable") from e
