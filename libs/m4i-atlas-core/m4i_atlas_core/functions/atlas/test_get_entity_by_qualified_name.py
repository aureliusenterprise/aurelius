from unittest.mock import AsyncMock, patch

import pytest

from ...entities import (BusinessDataDomain, BusinessDataDomainAttributes,
                         EntityHeader, QueryType, SearchResult)
from .get_entity_by_qualified_name import get_entity_by_qualified_name


@pytest.mark.asyncio
async def test__get_entity_by_qualified_name_single_search_result():
    qualified_name = "test_domain"
    type_name = "m4i_data_domain"

    search_result = SearchResult(
        approximate_count=1,
        entities=[
            EntityHeader(
                guid="12345",
                type_name=type_name
            )
        ],
        query_type=QueryType.ATTRIBUTE
    )

    entity_details = BusinessDataDomain(
        attributes=BusinessDataDomainAttributes(
            name="test",
            qualified_name=qualified_name
        )
    )

    with patch("m4i_atlas_core.functions.atlas.get_entity_by_qualified_name.get_entities_by_attribute", new_callable=AsyncMock) as mock_get_entities_by_attribute, \
            patch("m4i_atlas_core.functions.atlas.get_entity_by_qualified_name.resolve_entity_header", new_callable=AsyncMock) as mock_get_entity_by_guid:

        mock_get_entities_by_attribute.return_value = search_result
        mock_get_entity_by_guid.return_value = entity_details

        entity = await get_entity_by_qualified_name(qualified_name=qualified_name, type_name=type_name)

        assert entity.type_name == type_name
        assert entity.attributes.qualified_name == qualified_name
    # END WITH mock_get_entities_by_attribute, mock_resolve_entity_header

# END test__get_entity_by_qualified_name_single_search_result


@pytest.mark.asyncio
async def test__get_entity_by_qualified_name_no_search_results():
    qualified_name = "test_domain"
    type_name = "m4i_data_domain"

    search_result = SearchResult(
        approximate_count=0,
        entities=[],
        query_type=QueryType.ATTRIBUTE
    )

    entity_details = BusinessDataDomain(
        attributes=BusinessDataDomainAttributes(
            name="test",
            qualified_name=qualified_name
        )
    )

    with patch("m4i_atlas_core.functions.atlas.get_entity_by_qualified_name.get_entities_by_attribute", new_callable=AsyncMock) as mock_get_entities_by_attribute, \
            patch("m4i_atlas_core.functions.atlas.get_entity_by_qualified_name.resolve_entity_header", new_callable=AsyncMock) as mock_resolve_entity_header:

        mock_get_entities_by_attribute.return_value = search_result
        mock_resolve_entity_header.return_value = entity_details

        entity = await get_entity_by_qualified_name(qualified_name=qualified_name, type_name=type_name)

        assert entity is None
    # END WITH mock_get_entities_by_attribute, mock_resolve_entity_header

# END test__get_entity_by_qualified_name_single_search_result


@pytest.mark.asyncio
async def test__get_entity_by_qualified_name_multiple_search_results():
    qualified_name = "test_domain"
    type_name = "m4i_data_domain"

    search_result = SearchResult(
        approximate_count=2,
        entities=[
            EntityHeader(
                guid="12345",
                type_name=type_name
            ),
            EntityHeader(
                guid="23456",
                type_name=type_name
            )
        ],
        query_type=QueryType.ATTRIBUTE
    )

    entity_details = BusinessDataDomain(
        attributes=BusinessDataDomainAttributes(
            name="test",
            qualified_name=qualified_name
        )
    )

    with patch("m4i_atlas_core.functions.atlas.get_entity_by_qualified_name.get_entities_by_attribute", new_callable=AsyncMock) as mock_get_entities_by_attribute, \
            patch("m4i_atlas_core.functions.atlas.get_entity_by_qualified_name.resolve_entity_header", new_callable=AsyncMock) as mock_resolve_entity_header:

        mock_get_entities_by_attribute.return_value = search_result
        mock_resolve_entity_header.return_value = entity_details

        with pytest.raises(ValueError):
            await get_entity_by_qualified_name(qualified_name=qualified_name, type_name=type_name)
        # END WITH
    # END WITH mock_get_entities_by_attribute, mock_resolve_entity_header

# END test__get_entity_by_qualified_name_multiple_search_result
