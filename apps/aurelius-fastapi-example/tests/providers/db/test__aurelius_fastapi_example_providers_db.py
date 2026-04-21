import pytest
from aurelius_example import Entity
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import db
from sqlalchemy import Engine, inspect, text
from sqlmodel import Session, SQLModel, select


def get_engine(settings: Settings) -> Engine:
    """Return the database engine for the given settings."""
    return db.database(settings=settings)


def test__database_returns_working_engine(db_settings: Settings) -> None:
    """Database provider should return an engine that can execute SQL against PostgreSQL."""
    engine = get_engine(db_settings)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()

    assert result == 1

    engine.dispose()


def test__database_creates_schema_when_enabled(db_settings: Settings) -> None:
    """Database provider should create the SQLModel schema when auto_create_schema is enabled."""
    pre_engine = get_engine(db_settings.model_copy(update={"auto_create_schema": False}))

    SQLModel.metadata.drop_all(pre_engine)
    pre_engine.dispose()

    db.database.cache_clear()

    engine = get_engine(db_settings.model_copy(update={"auto_create_schema": True}))

    assert inspect(engine).has_table(str(Entity.__tablename__))

    engine.dispose()


def test__database_skips_schema_creation_when_disabled(db_settings: Settings) -> None:
    """Database provider should not create the SQLModel schema when auto_create_schema is disabled."""
    pre_engine = get_engine(db_settings.model_copy(update={"auto_create_schema": True}))

    SQLModel.metadata.drop_all(pre_engine)
    pre_engine.dispose()

    db.database.cache_clear()

    settings = db_settings.model_copy(update={"auto_create_schema": False})
    engine = get_engine(settings)

    try:
        assert not inspect(engine).has_table(str(Entity.__tablename__))
    finally:
        SQLModel.metadata.create_all(engine)
        engine.dispose()


def test__database_returns_cached_engine_for_same_settings(db_settings: Settings) -> None:
    """Database provider should return the same engine instance for repeated calls with the same settings."""
    first_engine = get_engine(db_settings)
    second_engine = get_engine(db_settings)

    assert first_engine is second_engine

    first_engine.dispose()


def test__session_yields_sqlmodel_session(db_settings: Settings) -> None:
    """Session provider should yield a usable SQLModel Session bound to the given engine."""
    engine = get_engine(db_settings)
    session_generator = db.session(engine)
    session = next(session_generator)

    try:
        assert isinstance(session, Session)
        assert session.exec(select(1)).one() == 1
    finally:
        with pytest.raises(StopIteration):
            next(session_generator)

    engine.dispose()


def test__session_persists_changes_without_error(db_settings: Settings) -> None:
    """Session provider should persist committed changes when no error occurs."""
    engine = get_engine(db_settings)
    session_generator = db.session(engine)
    session = next(session_generator)

    created = Entity(name="DB Provider", description="Persisted row")
    session.add(created)
    session.commit()
    session.refresh(created)
    created_guid = created.guid

    with pytest.raises(StopIteration):
        next(session_generator)

    with Session(engine) as verification_session:
        stored = verification_session.get(Entity, created_guid)

    assert stored is not None
    assert stored.guid == created_guid

    with Session(engine) as cleanup_session:
        cleanup_entity = cleanup_session.get(Entity, created_guid)

        if cleanup_entity is not None:
            cleanup_session.delete(cleanup_entity)
            cleanup_session.commit()

    engine.dispose()


def test__session_rolls_back_when_exception_is_raised(db_settings: Settings) -> None:
    """Session provider should rollback uncommitted changes when an exception is thrown into the generator."""
    engine = get_engine(db_settings)
    session_generator = db.session(engine)
    session = next(session_generator)

    pending = Entity(name="Rollback Row", description="Should be rolled back")
    session.add(pending)
    session.flush()
    pending_guid = pending.guid

    with pytest.raises(RuntimeError, match="boom"):
        session_generator.throw(RuntimeError("boom"))

    with Session(engine) as verification_session:
        stored = verification_session.get(Entity, pending_guid)

    assert stored is None

    engine.dispose()
