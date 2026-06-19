from uuid import uuid4

import pytest
import requests
from m4i_atlas_core import BusinessDataDomain, BusinessDataDomainAttributes, create_entities
from tenacity import Retrying, stop_after_attempt, wait_fixed


@pytest.mark.asyncio
async def test__m4i_synchronize_app_search_create_entity(
    auth_token: str, app_search_session: requests.Session
) -> None:
    """
    Test that a newly created entity in Atlas is synchronized to App Search.

    Asserts:
        - An entity created in Atlas is present in App Search after synchronization.
    """
    name = "Test Domain"
    qualified_name = f"test-domain-{uuid4()}"

    entity = BusinessDataDomain(
        attributes=BusinessDataDomainAttributes(name=name, qualified_name=qualified_name)
    )

    response = await create_entities(entity, access_token=auth_token)
    guid = response.guid_assignments[entity.guid]

    for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(5), reraise=True):
        with attempt:
            response = app_search_session.get("/api/as/v1/engines/atlas-dev/documents", json=[guid])
            assert response.status_code == 200

            documents = response.json()

            assert len(documents) == 1, f"Expected 1 document for {guid}, got {len(documents)}"

            document = documents[0]

            assert document is not None, f"Document {guid} not found in App Search"

            assert document["name"] == name
            assert document["referenceablequalifiedname"] == qualified_name
            assert document["typename"] == BusinessDataDomain.type_name
