from collections.abc import Generator
from functools import cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel

from aurelius_fastapi_example.globals import LOGGER

from .settings import Settings


@cache
def database(*, settings: Settings) -> Engine:
    """Return a database engine instance."""
    database_url = settings.database_url

    engine = create_engine(database_url)
    LOGGER.info("Connected to database %s", str(database_url).split("@")[-1])

    if settings.auto_create_schema:
        SQLModel.metadata.create_all(engine)
        LOGGER.info("Database schema created successfully")

    return engine


def session(db_engine: Annotated[Engine, Depends(database)]) -> Generator[Session]:
    """Create a database session for executing queries."""
    LOGGER.debug("Creating a new database session")

    with Session(db_engine) as session:
        try:
            yield session
        except Exception:
            LOGGER.error("Rolling back any changes to the database")
            session.rollback()
            raise
