"""End-to-end tests for m4i-synchronize-app-search Flink task."""

from uuid import uuid4

import pytest
import requests
from m4i_atlas_core.api.atlas.create_entities import create_entities
from m4i_atlas_core.entities.atlas.core.object_id.ObjectId import ObjectId
from m4i_atlas_core.entities.atlas.data_dictionary.BusinessDataDomain import (
    BusinessDataDomain,
    BusinessDataDomainAttributes,
)
from m4i_atlas_core.entities.atlas.data_dictionary.BusinessDataEntity import (
    BusinessDataEntity,
    BusinessDataEntityAttributes,
)
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_fixed

# ============================================================================
# Section A: Entity Creation & Sync
# ============================================================================


@pytest.mark.asyncio
async def test_create_business_data_domain_syncs_to_app_search(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """A1: Creating a BusinessDataDomain in Atlas should sync to App Search."""
    entity_name = f"domain_a1_{uuid4().hex[:8]}"

    guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=entity_name, qualified_name=entity_name),
        auth_token,
    )

    try:
        doc = wait_for_sync(app_search_session, guid)
        assert doc["name"] == entity_name
    finally:
        await delete_atlas_entity([guid], auth_token)


@pytest.mark.asyncio
async def test_create_business_data_entity_syncs_with_breadcrumbs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """A2: Creating a BusinessDataEntity should generate breadcrumbs with domain and entity name."""
    domain_name = f"domain_a2_{uuid4().hex[:8]}"
    entity_name = f"entity_a2_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        entity_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=entity_name,
                qualified_name=entity_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
            ),
            auth_token,
        )

        try:
            doc = wait_for_sync(app_search_session, entity_guid)

            breadcrumb_names = doc.get("breadcrumbname", [])

            assert domain_name in breadcrumb_names, (
                f"Domain '{domain_name}' not found in breadcrumbnames: {breadcrumb_names}"
            )
            assert doc["name"] == entity_name, f"Entity name not synced correctly: {doc}"
        finally:
            await delete_atlas_entity([entity_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


@pytest.mark.asyncio
async def test_create_derived_data_entity_syncs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """A3: Derived entities (m4i_data_domain_data, m4i_data_entity_data) should sync."""
    domain_name = f"domain_a3_{uuid4().hex[:8]}"
    entity_name = f"entity_a3_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        entity_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=entity_name,
                qualified_name=entity_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
            ),
            auth_token,
        )

        try:
            for attempt in Retrying(
                stop=stop_after_attempt(10),
                wait=wait_fixed(5),
                retry=retry_if_exception_type(AssertionError),
                reraise=True,
            ):
                with attempt:
                    doc = wait_for_sync(app_search_session, domain_guid)

                    derived_data_entities = doc.get("deriveddataentityguid", [])

                    assert entity_guid in derived_data_entities, (
                        f"Entity GUID '{entity_guid}' not found in deriveddataentityguid: "
                        f"{derived_data_entities}"
                    )
        finally:
            await delete_atlas_entity([entity_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


@pytest.mark.asyncio
async def test_create_person_with_email_syncs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """A4: AtlasPerson with email should sync to App Search."""
    from m4i_atlas_core.entities.atlas.data_dictionary.AtlasPerson import AtlasPerson, AtlasPersonAttributes

    person_name = f"person_a4_{uuid4().hex[:8]}"
    person_email = f"{person_name}@test.com"

    guid = await create_atlas_entity(
        AtlasPerson,
        AtlasPersonAttributes(name=person_name, email=person_email, qualified_name=person_name),
        auth_token,
    )

    try:
        doc = wait_for_sync(app_search_session, guid)
        assert doc["name"] == person_name
        # Email should be present in the synced document
        assert person_email in str(doc.get("email", "")) or person_email in str(doc), (
            f"Email '{person_email}' not found in document: {doc}"
        )
    finally:
        await delete_atlas_entity([guid], auth_token)


@pytest.mark.asyncio
async def test_create_multi_level_hierarchy_syncs_breadcrumbs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """A5: Multi-level hierarchy should generate proper breadcrumbs.

    Domain -> Parent Entity -> Child Entity breadcrumb chain verification.
    """
    domain_name = f"domain_a5_{uuid4().hex[:8]}"
    parent_name = f"parent_a5_{uuid4().hex[:8]}"
    child_name = f"child_a5_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        parent_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=parent_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                qualified_name=parent_name,
            ),
            auth_token,
        )

        try:
            child_guid = await create_atlas_entity(
                BusinessDataEntity,
                BusinessDataEntityAttributes(
                    name=child_name,
                    parent_entity=[ObjectId(guid=parent_guid, type_name="m4i_data_entity")],
                    qualified_name=child_name,
                ),
                auth_token,
            )

            try:
                doc = wait_for_sync(app_search_session, child_guid)
                breadcrumb_names = doc.get("breadcrumbname", [])
                breadcrumb_texts = " ".join(breadcrumb_names)

                # Breadcrumbs should contain the ancestor chain only.
                assert domain_name.lower() in breadcrumb_texts.lower(), (
                    f"Domain '{domain_name}' not in breadcrumbnames: {breadcrumb_names}"
                )
                assert parent_name.lower() in breadcrumb_texts.lower(), (
                    f"Parent '{parent_name}' not in breadcrumbnames: {breadcrumb_names}"
                )
                assert doc["name"] == child_name, f"Child name not synced correctly: {doc}"

                # Verify hierarchy order (domain should come before parent)
                domain_pos = breadcrumb_texts.lower().find(domain_name.lower())
                parent_pos = breadcrumb_texts.lower().find(parent_name.lower())
                assert domain_pos < parent_pos, f"Breadcrumb order incorrect: {breadcrumb_names}"
            finally:
                await delete_atlas_entity([child_guid], auth_token)
        finally:
            await delete_atlas_entity([parent_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


# ============================================================================
# Section B: Entity Deletion & Cleanup
# ============================================================================


@pytest.mark.asyncio
async def test_delete_entity_removes_from_app_search(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    soft_delete_atlas_entity,
    wait_for_sync,
):
    """B1: Deleting an entity in Atlas should remove it from App Search (tombstone propagation)."""
    domain_name = f"domain_b1_{uuid4().hex[:8]}"

    guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=f"domain_b1_{uuid4().hex[:8]}"),
        auth_token,
    )

    # Verify it exists first
    doc = wait_for_sync(app_search_session, guid)
    assert doc["name"] == domain_name

    # Delete the entity
    await soft_delete_atlas_entity([guid], auth_token)

    # Wait for removal from App Search
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_fixed(5),
        retry=retry_if_exception_type(AssertionError),
        reraise=True,
    ):
        with attempt:
            result = wait_for_sync(app_search_session, guid, expected_exists=False)
            assert result is None


@pytest.mark.asyncio
async def test_delete_domain_removes_breadcrumbs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    soft_delete_atlas_entity,
    wait_for_sync,
):
    """B2: Deleting a domain should update breadcrumbs in child entities."""
    domain_name = f"domain_b2_{uuid4().hex[:8]}"
    entity_name = f"entity_b2_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    entity_guid = await create_atlas_entity(
        BusinessDataEntity,
        BusinessDataEntityAttributes(
            name=entity_name,
            qualified_name=entity_name,
            data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
        ),
        auth_token,
    )

    try:
        # Verify breadcrumb exists initially
        doc = wait_for_sync(app_search_session, entity_guid)
        breadcrumb_names = doc.get("breadcrumbname", [])
        assert domain_name in breadcrumb_names, (
            f"Domain '{domain_name}' not in breadcrumbnames: {breadcrumb_names}"
        )

        # Delete the domain
        await soft_delete_atlas_entity([domain_guid], auth_token)

        # The domain reference should evenutally be removed from breadcrumbs
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_fixed(5),
            retry=retry_if_exception_type(AssertionError),
            reraise=True,
        ):
            with attempt:
                doc = wait_for_sync(app_search_session, entity_guid)
                breadcrumb_names = doc.get("breadcrumbname", [])
                assert domain_name not in breadcrumb_names, (
                    f"Domain '{domain_name}' still in breadcrumbnames after deletion: {breadcrumb_names}"
                )
    finally:
        await delete_atlas_entity([entity_guid], auth_token)


@pytest.mark.asyncio
async def test_delete_parent_removes_grandchild_breadcrumbs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    soft_delete_atlas_entity,
    wait_for_sync,
):
    """B3: Deleting a parent entity should update breadcrumbs in grandchildren."""
    domain_name = f"domain_b3_{uuid4().hex[:8]}"
    parent_name = f"parent_b3_{uuid4().hex[:8]}"
    child_name = f"child_b3_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    parent_guid = await create_atlas_entity(
        BusinessDataEntity,
        BusinessDataEntityAttributes(
            name=parent_name,
            qualified_name=parent_name,
            data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
        ),
        auth_token,
    )

    try:
        child_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=child_name,
                qualified_name=child_name,
                parent_entity=[ObjectId(guid=parent_guid, type_name="m4i_data_entity")],
            ),
            auth_token,
        )

        try:
            # Verify breadcrumb exists initially
            doc = wait_for_sync(app_search_session, child_guid)
            breadcrumb_names = doc.get("breadcrumbname", [])
            assert domain_name in breadcrumb_names, (
                f"Domain '{domain_name}' not in breadcrumbnames: {breadcrumb_names}"
            )

            # Delete the domain
            await soft_delete_atlas_entity([domain_guid], auth_token)

            # Wait for breadcrumb update - domain should no longer be present in child breadcrumbs
            for attempt in Retrying(
                stop=stop_after_attempt(10),
                wait=wait_fixed(5),
                retry=retry_if_exception_type(AssertionError),
                reraise=True,
            ):
                with attempt:
                    doc = wait_for_sync(app_search_session, child_guid)
                    breadcrumb_names = doc.get("breadcrumbname", [])
                    assert domain_name not in breadcrumb_names, (
                        f"Domain '{domain_name}' still in breadcrumbnames after deletion: {breadcrumb_names}"
                    )
                    assert parent_name in breadcrumb_names, (
                        f"Parent '{parent_name}' not in breadcrumbnames after domain deletion: "
                        f"{breadcrumb_names}"
                    )
        finally:
            await delete_atlas_entity([child_guid], auth_token)
    finally:
        await delete_atlas_entity([parent_guid], auth_token)


@pytest.mark.asyncio
async def test_delete_entity_removes_derived_entities(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    soft_delete_atlas_entity,
    wait_for_sync,
):
    """B4: Deleting an entity should remove associated derived entities from App Search."""
    domain_name = f"domain_b4_{uuid4().hex[:8]}"
    entity_name = f"entity_b4_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    entity_guid = await create_atlas_entity(
        BusinessDataEntity,
        BusinessDataEntityAttributes(
            name=entity_name,
            qualified_name=entity_name,
            data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
        ),
        auth_token,
    )

    try:
        # Verify derived entity reference exists initially
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_fixed(5),
            retry=retry_if_exception_type(AssertionError),
            reraise=True,
        ):
            with attempt:
                doc = wait_for_sync(app_search_session, domain_guid)
                derived_entities = doc.get("deriveddataentityguid", [])
                assert entity_guid in derived_entities, (
                    f"Entity '{entity_guid}' not in derived entities: {derived_entities}"
                )

        # Delete the entity
        await soft_delete_atlas_entity([entity_guid], auth_token)

        # The entity reference should eventually be removed from derived entities
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_fixed(5),
            retry=retry_if_exception_type(AssertionError),
            reraise=True,
        ):
            with attempt:
                doc = wait_for_sync(app_search_session, domain_guid)
                derived_entities = doc.get("deriveddataentityguid", [])
                assert entity_guid not in derived_entities, (
                    f"Entity '{entity_guid}' still in derived entities after deletion: {derived_entities}"
                )
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


# ============================================================================
# Section C: Attribute Updates & Propagation
# ============================================================================


@pytest.mark.asyncio
async def test_update_whitelisted_attribute_syncs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """C1: Updating whitelisted attributes should sync to App Search."""
    domain_name = f"domain_c1_{uuid4().hex[:8]}"
    new_definition = f"Updated definition {uuid4().hex[:8]}"

    guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        # Verify initial sync
        doc = wait_for_sync(app_search_session, guid)
        assert doc["name"] == domain_name

        # Update the entity definition attribute using create_entities (handles updates)
        updated_entity = BusinessDataDomain(
            guid=guid,
            attributes=BusinessDataDomainAttributes(
                name=domain_name, definition=new_definition, qualified_name=domain_name
            ),
        )

        await create_entities(updated_entity, access_token=auth_token)

        # Wait for the update to sync
        for attempt in Retrying(
            stop=stop_after_attempt(10),
            wait=wait_fixed(5),
            retry=retry_if_exception_type(AssertionError),
            reraise=True,
        ):
            with attempt:
                doc = wait_for_sync(app_search_session, guid)
                assert doc.get("definition", "") == new_definition, f"Definition not updated: {doc}"
    finally:
        await delete_atlas_entity([guid], auth_token)


@pytest.mark.asyncio
async def test_update_name_propagates_to_breadcrumbs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """C2: Updating entity name should propagate to breadcrumbs in related entities."""
    domain_name = f"domain_c2_{uuid4().hex[:8]}"
    new_domain_name = f"new_{domain_name}"
    entity_name = f"entity_c2_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        entity_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=entity_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                qualified_name=entity_name,
            ),
            auth_token,
        )

        try:
            # Verify initial breadcrumb
            doc = wait_for_sync(app_search_session, entity_guid)
            breadcrumb_names = doc.get("breadcrumbname", [])
            assert domain_name in breadcrumb_names, (
                f"Domain '{domain_name}' not in breadcrumbnames: {breadcrumb_names}"
            )

            # Update the domain name using create_entities (handles updates via guid match)
            updated_domain = BusinessDataDomain(
                guid=domain_guid,
                attributes=BusinessDataDomainAttributes(name=new_domain_name, qualified_name=domain_name),
            )

            # Update the entity name using create_entities (handles updates)
            await create_entities(updated_domain, access_token=auth_token)

            # Wait for breadcrumb update with new name
            # Wait for the update to sync
            for attempt in Retrying(
                stop=stop_after_attempt(10),
                wait=wait_fixed(5),
                retry=retry_if_exception_type(AssertionError),
                reraise=True,
            ):
                with attempt:
                    doc = wait_for_sync(app_search_session, entity_guid)
                    breadcrumb_names = doc.get("breadcrumbname", [])
                    assert new_domain_name in breadcrumb_names, (
                        f"New domain name '{new_domain_name}' not in breadcrumbnames: {breadcrumb_names}"
                    )
        finally:
            await delete_atlas_entity([entity_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


@pytest.mark.asyncio
async def test_update_parent_entity_name_propagates(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """C3: Updating parent entity name should propagate to child breadcrumbs."""
    domain_name = f"domain_c3_{uuid4().hex[:8]}"
    new_domain_name = f"new_{domain_name}"
    parent_name = f"parent_c3_{uuid4().hex[:8]}"
    child_name = f"child_c3_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        parent_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=parent_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                qualified_name=parent_name,
            ),
            auth_token,
        )

        try:
            child_guid = await create_atlas_entity(
                BusinessDataEntity,
                BusinessDataEntityAttributes(
                    name=child_name,
                    parent_entity=[ObjectId(guid=parent_guid, type_name="m4i_data_entity")],
                    qualified_name=child_name,
                ),
                auth_token,
            )

            try:
                # Verify initial breadcrumb has parent name
                doc = wait_for_sync(app_search_session, child_guid)
                breadcrumb_names = doc.get("breadcrumbname", [])
                assert domain_name in breadcrumb_names, (
                    f"Domain '{domain_name}' not in breadcrumbnames: {breadcrumb_names}"
                )

                # Update the domain name using create_entities (handles updates via guid)
                updated_domain = BusinessDataDomain(
                    guid=domain_guid,
                    attributes=BusinessDataDomainAttributes(
                        name=new_domain_name,
                        qualified_name=domain_name,  # qualified name should not change on name update
                    ),
                )
                await create_entities(updated_domain, access_token=auth_token)

                # Wait for breadcrumb update with new domain name
                # Wait for the update to sync
                for attempt in Retrying(
                    stop=stop_after_attempt(10),
                    wait=wait_fixed(5),
                    retry=retry_if_exception_type(AssertionError),
                    reraise=True,
                ):
                    with attempt:
                        doc = wait_for_sync(app_search_session, child_guid)
                        breadcrumb_names = doc.get("breadcrumbname", [])
                        assert new_domain_name in breadcrumb_names, (
                            f"New domain name '{new_domain_name}' not in breadcrumbnames: {breadcrumb_names}"
                        )
                        assert domain_name not in breadcrumb_names, (
                            f"Old domain name '{domain_name}' still in breadcrumbnames after update: "
                            f"{breadcrumb_names}"
                        )
            finally:
                await delete_atlas_entity([child_guid], auth_token)
        finally:
            await delete_atlas_entity([parent_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


# ============================================================================
# Section D: Relationship Operations ⭐ Priority
# ============================================================================


@pytest.mark.asyncio
async def test_add_relationship_syncs_to_app_search_a(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """D1A: Adding a relationship between entities should sync to App Search."""

    domain_name = f"domain_d1a_{uuid4().hex[:8]}"
    entity_name = f"entity_d1a_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        # Create entity without relationship first
        entity_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(name=entity_name, qualified_name=entity_name),
            auth_token,
        )

        try:
            # Verify initial sync (no domain relationship)
            doc = wait_for_sync(app_search_session, entity_guid)
            assert doc["name"] == entity_name

            # Add relationship by updating entity with data_domain
            # Using create_entities (handles updates via guid)
            updated_entity = BusinessDataEntity(
                guid=entity_guid,
                attributes=BusinessDataEntityAttributes(
                    name=entity_name,
                    data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                    qualified_name=entity_name,
                ),
            )

            await create_entities(updated_entity, access_token=auth_token)

            # Wait for relationship to sync - breadcrumbs should now include domain
            for attempt in Retrying(
                stop=stop_after_attempt(10),
                wait=wait_fixed(5),
                retry=retry_if_exception_type(AssertionError),
                reraise=True,
            ):
                with attempt:
                    doc = wait_for_sync(app_search_session, entity_guid)
                    breadcrumb_names = doc.get("breadcrumbname", [])
                    assert domain_name in breadcrumb_names, (
                        f"Domain '{domain_name}' not added to breadcrumbnames after relationship: "
                        f"{breadcrumb_names}"
                    )
        finally:
            await delete_atlas_entity([entity_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


@pytest.mark.asyncio
async def test_add_relationship_syncs_to_app_search_b(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """D1B: Adding a relationship between entities should sync to App Search."""

    domain_name = f"domain_d1b_{uuid4().hex[:8]}"
    entity_name = f"entity_d1b_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        # Create entity without relationship first
        entity_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(name=entity_name, qualified_name=entity_name),
            auth_token,
        )

        try:
            # Verify initial sync (no domain relationship)
            doc = wait_for_sync(app_search_session, entity_guid)
            assert doc["name"] == entity_name

            # Add relationship by updating entity with data_domain
            # Using create_entities (handles updates via guid)
            updated_entity = BusinessDataDomain(
                guid=domain_guid,
                attributes=BusinessDataDomainAttributes(
                    name=domain_name,
                    data_entity=[ObjectId(guid=entity_guid, type_name="m4i_data_entity")],
                    qualified_name=domain_name,
                ),
            )

            await create_entities(updated_entity, access_token=auth_token)

            # Wait for relationship to sync - breadcrumbs should now include domain
            for attempt in Retrying(
                stop=stop_after_attempt(10),
                wait=wait_fixed(5),
                retry=retry_if_exception_type(AssertionError),
                reraise=True,
            ):
                with attempt:
                    doc = wait_for_sync(app_search_session, entity_guid)
                    breadcrumb_names = doc.get("breadcrumbname", [])
                    assert domain_name in breadcrumb_names, (
                        f"Domain '{domain_name}' not added to breadcrumbnames after relationship: "
                        f"{breadcrumb_names}"
                    )
        finally:
            await delete_atlas_entity([entity_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


@pytest.mark.asyncio
async def test_remove_relationship_syncs_to_app_search(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """D2: Removing a relationship should update App Search."""

    domain_name = f"domain_d2_{uuid4().hex[:8]}"
    entity_name = f"entity_d2_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        # Create entity with relationship
        entity_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=entity_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                qualified_name=entity_name,
            ),
            auth_token,
        )

        try:
            # Verify relationship exists in breadcrumbs
            doc = wait_for_sync(app_search_session, entity_guid)
            breadcrumb_names = doc.get("breadcrumbname", [])
            assert domain_name in breadcrumb_names, (
                f"Domain '{domain_name}' not in breadcrumbnames before removal: {breadcrumb_names}"
            )

            # Remove relationship by clearing data_domain attribute
            # Using create_entities (handles updates via guid)
            updated_entity = BusinessDataEntity(
                guid=entity_guid,
                attributes=BusinessDataEntityAttributes(
                    name=entity_name, qualified_name=f"entity_d2_{uuid4().hex[:8]}"
                ),
            )

            await create_entities(updated_entity, access_token=auth_token)

            # Wait for relationship removal to sync - domain should no longer be in breadcrumbs
            for attempt in Retrying(
                stop=stop_after_attempt(10),
                wait=wait_fixed(5),
                retry=retry_if_exception_type(AssertionError),
                reraise=True,
            ):
                with attempt:
                    doc = wait_for_sync(app_search_session, entity_guid)
                    breadcrumb_names = doc.get("breadcrumbname", [])
                    assert domain_name not in breadcrumb_names, (
                        f"Domain '{domain_name}' still in breadcrumbnames after removal: {breadcrumb_names}"
                    )
        finally:
            await delete_atlas_entity([entity_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


@pytest.mark.asyncio
async def test_reparent_entity_updates_breadcrumbs(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """D3: Changing parent entity should update breadcrumbs."""

    old_parent_name = f"old_parent_d3_{uuid4().hex[:8]}"
    new_parent_name = f"new_parent_d3_{uuid4().hex[:8]}"
    child_name = f"child_d3_{uuid4().hex[:8]}"
    domain_name = f"domain_d3_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    try:
        old_parent_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=old_parent_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                qualified_name=old_parent_name,
            ),
            auth_token,
        )

        try:
            new_parent_guid = await create_atlas_entity(
                BusinessDataEntity,
                BusinessDataEntityAttributes(
                    name=new_parent_name,
                    data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                    qualified_name=new_parent_name,
                ),
                auth_token,
            )

            try:
                child_guid = await create_atlas_entity(
                    BusinessDataEntity,
                    BusinessDataEntityAttributes(
                        name=child_name,
                        parent_entity=[ObjectId(guid=old_parent_guid, type_name="m4i_data_entity")],
                        qualified_name=child_name,
                    ),
                    auth_token,
                )

                try:
                    # Verify initial breadcrumb has old parent
                    doc = wait_for_sync(app_search_session, child_guid)
                    breadcrumb_names = doc.get("breadcrumbname", [])
                    assert domain_name in breadcrumb_names, (
                        f"Domain '{domain_name}' not in breadcrumbnames before removal: {breadcrumb_names}"
                    )
                    assert old_parent_name in breadcrumb_names, (
                        f"Old parent '{old_parent_name}' not in breadcrumbnames before removal: "
                        f"{breadcrumb_names}"
                    )

                    # Reparent to new parent using create_entities (handles updates via guid)
                    updated_child = BusinessDataEntity(
                        guid=child_guid,
                        attributes=BusinessDataEntityAttributes(
                            name=child_name,
                            parent_entity=[ObjectId(guid=new_parent_guid, type_name="m4i_data_entity")],
                            qualified_name=child_name,
                        ),
                    )
                    await create_entities(updated_child, access_token=auth_token)

                    # Wait for breadcrumb update - should have new parent instead of old
                    for attempt in Retrying(
                        stop=stop_after_attempt(10),
                        wait=wait_fixed(5),
                        retry=retry_if_exception_type(AssertionError),
                        reraise=True,
                    ):
                        with attempt:
                            doc = wait_for_sync(app_search_session, child_guid)
                            breadcrumb_names = doc.get("breadcrumbname", [])

                            assert domain_name in breadcrumb_names, (
                                f"Domain '{domain_name}' not in breadcrumbnames after reparenting: "
                                f"{breadcrumb_names}"
                            )
                            assert new_parent_name in breadcrumb_names, (
                                f"New parent '{new_parent_name}' not in breadcrumbs after reparenting: "
                                f"{breadcrumb_names}"
                            )
                            assert old_parent_name not in breadcrumb_names, (
                                f"Old parent '{old_parent_name}' still in breadcrumbs after reparenting: "
                                f"{breadcrumb_names}"
                            )
                finally:
                    await delete_atlas_entity([child_guid], auth_token)
            finally:
                await delete_atlas_entity([new_parent_guid], auth_token)
        finally:
            await delete_atlas_entity([old_parent_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)


# ============================================================================
# Section E: Edge Cases & Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_create_then_delete_entity(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    soft_delete_atlas_entity,
    wait_for_sync,
):
    """E1: Creating then immediately deleting an entity should handle gracefully."""
    domain_name = f"domain_e1_{uuid4().hex[:8]}"

    guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    # Ensure the entity is synced to App Search before deletion
    doc = wait_for_sync(app_search_session, guid)
    assert doc is not None, f"Entity '{guid}' not found in App Search after creation."

    # Delete immediately without waiting for sync
    await soft_delete_atlas_entity([guid], auth_token)

    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_fixed(5),
        retry=retry_if_exception_type(AssertionError),
        reraise=True,
    ):
        with attempt:
            # Check if the entity still exists in App Search
            doc = wait_for_sync(app_search_session, guid, expected_exists=False)
            assert doc is None, f"Entity '{guid}' still exists in App Search after deletion."


@pytest.mark.asyncio
async def test_concurrent_changes(
    auth_token: str,
    app_search_session: requests.Session,
    create_atlas_entity,
    delete_atlas_entity,
    wait_for_sync,
):
    """E2: Concurrent changes should eventually sync correctly."""
    domain_name = f"domain_e3_{uuid4().hex[:8]}"
    entity_name = f"entity_e3_{uuid4().hex[:8]}"

    domain_guid = await create_atlas_entity(
        BusinessDataDomain,
        BusinessDataDomainAttributes(name=domain_name, qualified_name=domain_name),
        auth_token,
    )

    n = 3  # Number of concurrent updates to simulate

    try:
        # Create entity with relationship to domain
        entity_guid = await create_atlas_entity(
            BusinessDataEntity,
            BusinessDataEntityAttributes(
                name=entity_name,
                data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                qualified_name=entity_name,
            ),
            auth_token,
        )

        try:
            # Verify initial state
            doc = wait_for_sync(app_search_session, entity_guid)
            assert doc["name"] == entity_name

            # Make multiple updates in sequence (simulating concurrent changes)
            for i in range(n):
                updated_entity = BusinessDataEntity(
                    guid=entity_guid,
                    attributes=BusinessDataEntityAttributes(
                        name=f"{entity_name}_v{i + 1}",
                        data_domain=[ObjectId(guid=domain_guid, type_name="m4i_data_domain")],
                        qualified_name=entity_name,
                    ),
                )
                await create_entities(updated_entity, access_token=auth_token)

            # Wait for final state to sync
            for attempt in Retrying(
                stop=stop_after_attempt(10),
                wait=wait_fixed(5),
                retry=retry_if_exception_type(AssertionError),
                reraise=True,
            ):
                with attempt:
                    doc = wait_for_sync(app_search_session, entity_guid)
                    # The final name should be the last update applied
                    assert doc["name"] == f"{entity_name}_v{n}", f"Final name not synced correctly: {doc}"
        finally:
            await delete_atlas_entity([entity_guid], auth_token)
    finally:
        await delete_atlas_entity([domain_guid], auth_token)
