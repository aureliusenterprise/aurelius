"""Core logic for updating breadcrumbs in Elasticsearch."""

import asyncio
import logging
from typing import Dict, List, Optional

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from m4i_atlas_core.api.atlas import get_entity_by_guid
from m4i_atlas_core.config import ConfigStore
from m4i_atlas_core.entities import Entity
from m4i_atlas_core.functions.atlas import get_breadcrumbs, get_breadcrumbs_for_all_descendants


logger = logging.getLogger(__name__)


class BreadcrumbUpdater:
    """Updates breadcrumbs in Elasticsearch for Atlas entities."""

    def __init__(
        self,
        elastic: Elasticsearch,
        index_name: str,
        atlas_url: str,
        access_token: Optional[str] = None,
        atlas_username: Optional[str] = None,
        atlas_password: Optional[str] = None,
        choose_first_parent: bool = False,
        dry_run: bool = False,
    ):
        """
        Initialize the BreadcrumbUpdater.

        Parameters
        ----------
        elastic : Elasticsearch
            Elasticsearch client instance.
        index_name : str
            Name of the Elasticsearch index to update.
        atlas_url : str
            Atlas API base URL.
        access_token : Optional[str]
            Optional access token for Atlas API authentication.
        atlas_username : Optional[str]
            Optional username for Atlas basic authentication.
        atlas_password : Optional[str]
            Optional password for Atlas basic authentication.
        choose_first_parent : bool
            If True, automatically choose first parent when multiple exist.
        dry_run : bool
            If True, only print the updates without writing to Elasticsearch.
        """
        self.elastic = elastic
        self.index_name = index_name
        self.access_token = access_token
        self.choose_first_parent = choose_first_parent
        self.dry_run = dry_run
        
        # Configure Atlas API
        config = ConfigStore.get_instance()
        config.load({
            "atlas.server.url": atlas_url,
            "atlas.credentials.username": atlas_username or "",
            "atlas.credentials.password": atlas_password or ""
        })

    async def update_entity_breadcrumbs(
        self,
        entity_guid: str,
        include_descendants: bool = False,
    ) -> int:
        """
        Update breadcrumbs for an entity and optionally its descendants.

        Parameters
        ----------
        entity_guid : str
            GUID of the entity to update breadcrumbs for.
        include_descendants : bool
            If True, update breadcrumbs for all descendants as well.

        Returns
        -------
        int
            Number of documents updated in Elasticsearch.
        """
        logger.info(f"Fetching entity {entity_guid}")
        entity = await get_entity_by_guid(
            guid=entity_guid,
            entity_type=Entity,
            access_token=self.access_token,
        )

        if include_descendants:
            logger.info(f"Fetching breadcrumbs for entity {entity_guid} and all descendants")
            breadcrumbs_map = await get_breadcrumbs_for_all_descendants(
                entity=entity,
                choose_first_parent=self.choose_first_parent,
                access_token=self.access_token,
            )
        else:
            logger.info(f"Fetching breadcrumbs for entity {entity_guid}")
            breadcrumbs = await get_breadcrumbs(
                entity=entity,
                choose_first_parent=self.choose_first_parent,
                access_token=self.access_token,
            )
            breadcrumbs_map = {entity_guid: breadcrumbs}

        logger.info(f"Updating breadcrumbs for {len(breadcrumbs_map)} entities in Elasticsearch")
        return self._update_breadcrumbs_in_elasticsearch(breadcrumbs_map)

    def _update_breadcrumbs_in_elasticsearch(
        self,
        breadcrumbs_map: Dict[str, List[Entity]],
    ) -> int:
        """
        Update breadcrumbs in Elasticsearch for the given entities.

        Parameters
        ----------
        breadcrumbs_map : Dict[str, List[Entity]]
            Mapping of entity GUID to its breadcrumb path.

        Returns
        -------
        int
            Number of documents updated.
        """
        actions = []

        for entity_guid, breadcrumb_path in breadcrumbs_map.items():
            # Create breadcrumb lists
            breadcrumb_guids = [entity.guid for entity in breadcrumb_path]
            breadcrumb_names = [entity.attributes.get("name", "") for entity in breadcrumb_path]
            breadcrumb_types = [entity.type_name for entity in breadcrumb_path]

            # Update the entity's document
            logger.debug(f"Updating document for entity {entity_guid}")
            actions.append({
                "_op_type": "update",
                "_index": self.index_name,
                "_id": entity_guid,
                "doc": {
                    "breadcrumbguid": breadcrumb_guids,
                    "breadcrumbname": breadcrumb_names,
                    "breadcrumbtype": breadcrumb_types,
                },
                "doc_as_upsert": False,
            })

        if not actions:
            logger.info("No documents to update")
            return 0

        if self.dry_run:
            logger.info(f"[DRY RUN] Would update {len(actions)} documents:")
            for action in actions:
                entity_guid = action["_id"]
                doc = action["doc"]
                logger.info(f"\n[DRY RUN] Entity: {entity_guid}")
                logger.info(f"  Breadcrumb GUIDs: {doc['breadcrumbguid']}")
                logger.info(f"  Breadcrumb Names: {doc['breadcrumbname']}")
                logger.info(f"  Breadcrumb Types: {doc['breadcrumbtype']}")
            return len(actions)

        logger.info(f"Executing bulk update of {len(actions)} documents")
        success, failed = bulk(
            self.elastic,
            actions,
            raise_on_error=False,
            raise_on_exception=False,
        )

        if failed:
            logger.warning(f"Failed to update {len(failed)} documents")

        logger.info(f"Successfully updated {success} documents")
        return success
