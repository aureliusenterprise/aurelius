from aurelius_example import Entity
from aurelius_fastapi_example.app import create_app
from aurelius_fastapi_example.models import Settings
from sqlalchemy import Engine, inspect
from sqlmodel import SQLModel


async def test__app_creates_schema_on_startup_when_enabled(db_settings: Settings, db_engine: Engine) -> None:
    """Application startup should create the SQLModel schema when auto_create_schema is enabled."""
    # Ensure schema doesn't exist
    SQLModel.metadata.drop_all(db_engine)

    # Create app with auto_create_schema enabled
    settings_with_schema_creation = db_settings.model_copy(update={"auto_create_schema": True})
    app = create_app(settings_with_schema_creation)

    # Trigger the lifespan startup
    lifespan = app.router.lifespan_context

    async with lifespan(app):
        # Within the startup, the schema should have been created
        assert inspect(db_engine).has_table(str(Entity.__tablename__))

    # Cleanup
    SQLModel.metadata.drop_all(db_engine)


async def test__app_skips_schema_creation_on_startup_when_disabled(db_settings: Settings, db_engine: Engine) -> None:
    """Application startup should not create the SQLModel schema when auto_create_schema is disabled."""
    # Ensure schema doesn't exist
    SQLModel.metadata.drop_all(db_engine)

    # Create app with auto_create_schema disabled
    settings_without_schema_creation = db_settings.model_copy(update={"auto_create_schema": False})
    app = create_app(settings_without_schema_creation)

    # Trigger the lifespan startup
    lifespan = app.router.lifespan_context

    async with lifespan(app):
        # The schema should NOT have been created
        assert not inspect(db_engine).has_table(str(Entity.__tablename__))

    # Cleanup
    SQLModel.metadata.drop_all(db_engine)
