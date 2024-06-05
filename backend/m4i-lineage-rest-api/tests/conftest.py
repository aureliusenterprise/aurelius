import pytest
from m4i_atlas_core import get_entity_by_qualified_name, delete_entity_soft, delete_entity_hard
from m4i_atlas_core.api.atlas import get_entities_by_attribute

from m4i_lineage_rest_api.app import flask_app, init_config

init_config()


@pytest.fixture
def client():
    app_flask = flask_app()
    app_flask.initialize_app()
    app_flask.app.config['TESTING'] = True
    with app_flask.app.test_client() as client:
        yield client
    # END client


@pytest.fixture
def check_made():
    async def _check_made(entity_qn: str, entity_type: str):
        entity = await get_entity_by_qualified_name(qualified_name=entity_qn, type_name=entity_type)
        assert entity.type_name == entity_type
        # assert entity.attributes.qualified_name == entity_qn
        assert entity.attributes.unmapped_attributes['qualifiedName'] == entity_qn
        guid = entity.guid
        assert guid is not None

        await get_entities_by_attribute.cache.clear()
        return guid
    # END ASYNC check_made
    return _check_made

# END check_made

@pytest.fixture
def cleanup():
    async def _cleanup(guid: str, entity_qn: str, entity_type: str):
        await delete_entity_soft(guid)

        await delete_entity_hard([guid])

        object = await get_entity_by_qualified_name(qualified_name=entity_qn, type_name=entity_type)
        assert object is None
        await get_entities_by_attribute.cache.clear()

    # END ASYNC cleanup
    return _cleanup
# END cleanup
