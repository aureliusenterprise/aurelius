"""Core logic for updating breadcrumbs in Elasticsearch."""

import asyncio
import logging
from typing import Dict, List, Optional

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from m4i_atlas_core.api.atlas import get_entity_by_guid
from m4i_atlas_core.api.auth import get_keycloak_token
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
        keycloak_url: Optional[str] = None,
        keycloak_client_id: str = "m4i_public",
        keycloak_realm: str = "m4i",
        keycloak_client_secret: Optional[str] = None,
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
            Optional username for Atlas/Keycloak authentication.
        atlas_password : Optional[str]
            Optional password for Atlas/Keycloak authentication.
        keycloak_url : Optional[str]
            Optional Keycloak server URL (e.g., https://domain/namespace/auth).
        keycloak_client_id : str
            Keycloak client ID (default: m4i_public).
        keycloak_realm : str
            Keycloak realm name (default: m4i).
        keycloak_client_secret : Optional[str]
            Optional Keycloak client secret key.
        choose_first_parent : bool
            If True, automatically choose first parent when multiple exist.
        dry_run : bool
            If True, only print the updates without writing to Elasticsearch.
        """
        self.elastic = elastic
        self.index_name = index_name
        self.choose_first_parent = choose_first_parent
        self.dry_run = dry_run
        
        # Configure Atlas API
        config = ConfigStore.get_instance()
        config_dict = {
            "atlas.server.url": atlas_url,
            "atlas.credentials.username": atlas_username or "",
            "atlas.credentials.password": atlas_password or ""
        }
        
        if keycloak_url:
            config_dict.update({
                "keycloak.server.url": keycloak_url,
                "keycloak.client.id": keycloak_client_id,
                "keycloak.realm.name": keycloak_realm,
                "keycloak.client.secret.key": keycloak_client_secret or "",
                "keycloak.credentials.username": atlas_username or "",
                "keycloak.credentials.password": atlas_password or ""
            })
        
        config.load(config_dict)
        
        if access_token:
            self.access_token = access_token
        elif atlas_username and atlas_password and keycloak_url:
            # Try to get Keycloak token
            try:
                logger.info("Attempting to get Keycloak access token")
                self.access_token = get_keycloak_token(credentials=(atlas_username, atlas_password))
                logger.info("Successfully obtained Keycloak access token")
            except Exception as e:
                logger.warning(f"Failed to get Keycloak token: {e}. Will try basic auth.")
                self.access_token = None
        else:
            self.access_token = None

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

    async def update_multiple_entities_breadcrumbs(
        self,
        entity_guids: List[str],
        include_descendants: bool = False,
    ) -> int:
        """
        Update breadcrumbs for multiple entities and optionally their descendants.

        Parameters
        ----------
        entity_guids : List[str]
            List of entity GUIDs to update breadcrumbs for.
        include_descendants : bool
            If True, update breadcrumbs for all descendants as well.

        Returns
        -------
        int
            Total number of documents updated in Elasticsearch.
        """
        # Collect all breadcrumbs first, avoiding duplicates
        all_breadcrumbs_map: Dict[str, List[Entity]] = {}
        
        for entity_guid in entity_guids:
            try:
                # Skip if breadcrumbs already collected (e.g., as a descendant)
                if entity_guid in all_breadcrumbs_map:
                    logger.debug(f"Breadcrumbs for {entity_guid} already collected, skipping")
                    continue
                
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
                
                for guid, breadcrumbs in breadcrumbs_map.items():
                    if guid not in all_breadcrumbs_map:
                        all_breadcrumbs_map[guid] = breadcrumbs
                    
            except Exception as e:
                logger.error(f"Failed to fetch breadcrumbs for entity {entity_guid}: {e}")
                raise
        
        if all_breadcrumbs_map:
            logger.info(f"Updating breadcrumbs for {len(all_breadcrumbs_map)} unique entities in Elasticsearch")
            return self._update_breadcrumbs_in_elasticsearch(all_breadcrumbs_map)
        else:
            logger.info("No breadcrumbs to update")
            return 0

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
            breadcrumb_guids = [entity.guid for entity in breadcrumb_path]
            breadcrumb_names = [
                getattr(entity.attributes, 'name', None) or 
                entity.attributes.unmapped_attributes.get("name", "") 
                if entity.attributes else ""
                for entity in breadcrumb_path
            ]
            breadcrumb_types = [entity.type_name for entity in breadcrumb_path]

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
                "doc_as_upsert": True,
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
            # Log first few failures for debugging
            for i, error in enumerate(failed[:5]):
                logger.error(f"Failed document {i+1}: {error}")

        logger.info(f"Successfully updated {success} documents")
        return success
