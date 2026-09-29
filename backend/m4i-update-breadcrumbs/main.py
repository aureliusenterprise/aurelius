"""CLI entry point for the breadcrumb updater tool."""

import asyncio
import logging
import sys
from typing import List, Optional

import click
from elasticsearch import Elasticsearch
from m4i_atlas_core import register_atlas_entity_types
from m4i_atlas_core.entities.atlas.data_dictionary import data_dictionary_entity_types

from m4i_update_breadcrumbs.breadcrumb_updater import BreadcrumbUpdater


# Register entity types so they can be properly deserialized
register_atlas_entity_types(data_dictionary_entity_types)

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--guid",
    multiple=True,
    required=True,
    help="Entity GUID(s) to update breadcrumbs for. Can be specified multiple times.",
)
@click.option(
    "--elastic-url",
    required=True,
    help="Elasticsearch URL (e.g., http://localhost:9200)",
)
@click.option(
    "--index",
    required=True,
    help="Elasticsearch index name",
)
@click.option(
    "--atlas-url",
    required=True,
    help="Atlas API base URL (e.g., https://<your-domain>/<namespace>/atlas2/api/atlas)",
)
@click.option(
    "--access-token",
    default=None,
    help="Access token for Atlas API authentication",
)
@click.option(
    "--atlas-user",
    default=None,
    help="Atlas username for basic authentication (alternative to access token)",
)
@click.option(
    "--atlas-password",
    default=None,
    help="Atlas password for basic authentication (alternative to access token)",
)
@click.option(
    "--keycloak-url",
    default=None,
    help="Keycloak server URL (e.g., https://<your-domain>/<namespace>/auth)",
)
@click.option(
    "--keycloak-client-id",
    default="m4i_public",
    help="Keycloak client ID (default: m4i_public)",
)
@click.option(
    "--keycloak-realm",
    default="m4i",
    help="Keycloak realm name (default: m4i)",
)
@click.option(
    "--keycloak-client-secret",
    default=None,
    help="Keycloak client secret key",
)
@click.option(
    "--include-descendants",
    is_flag=True,
    default=False,
    help="Include all descendants of the specified entities",
)
@click.option(
    "--choose-first-parent",
    is_flag=True,
    default=False,
    help="When an entity has multiple parents, choose the first one (default: raises error)",
)
@click.option(
    "--elastic-user",
    default=None,
    help="Elasticsearch username for basic authentication",
)
@click.option(
    "--elastic-password",
    default=None,
    help="Elasticsearch password for basic authentication",
)
@click.option(
    "--elastic-api-key",
    default=None,
    help="Elasticsearch API key for authentication (alternative to username/password)",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose logging (DEBUG level)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print updates without writing to Elasticsearch",
)
def main(
    guid: tuple,
    elastic_url: str,
    index: str,
    atlas_url: str,
    access_token: Optional[str],
    atlas_user: Optional[str],
    atlas_password: Optional[str],
    keycloak_url: Optional[str],
    keycloak_client_id: str,
    keycloak_realm: str,
    keycloak_client_secret: Optional[str],
    include_descendants: bool,
    choose_first_parent: bool,
    elastic_user: Optional[str],
    elastic_password: Optional[str],
    elastic_api_key: Optional[str],
    verbose: bool,
    dry_run: bool,
):
    """
    Update breadcrumbs in Elasticsearch for Atlas entities.

    This tool retrieves breadcrumbs for one or more entities (and optionally their descendants)
    and updates the breadcrumb information in Elasticsearch.

    Examples:

    \b
    # Update breadcrumbs for a single entity
    python main.py --guid abc-123 --elastic-url http://localhost:9200 --index atlas \\
        --atlas-url https://<your-domain>/<namespace>/atlas2/api/atlas

    \b
    # Update breadcrumbs for an entity and all its descendants
    python main.py --guid abc-123 --elastic-url http://localhost:9200 --index atlas --include-descendants

    \b
    # Update breadcrumbs for multiple entities
    python main.py --guid abc-123 --guid def-456 --elastic-url http://localhost:9200 --index atlas

    \b
    # With Elasticsearch username/password
    python main.py --guid abc-123 --elastic-url http://localhost:9200 --index atlas \\
        --elastic-user elastic --elastic-password <password>
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    entity_guids: List[str] = list(guid)

    logger.info(f"Starting breadcrumb update for {len(entity_guids)} entity/entities")
    logger.info(f"Atlas URL: {atlas_url}")
    logger.info(f"Elasticsearch URL: {elastic_url}")
    logger.info(f"Index: {index}")
    logger.info(f"Include descendants: {include_descendants}")
    logger.info(f"Choose first parent: {choose_first_parent}")
    logger.info(f"Dry run: {dry_run}")

    try:
        if dry_run:
            elastic = None
            logger.info("[DRY RUN] Skipping Elasticsearch connection check")
        else:
            # Create Elasticsearch client
            elastic_kwargs = {"hosts": [elastic_url]}
            if elastic_api_key:
                elastic_kwargs["api_key"] = elastic_api_key
                logger.info("Using Elasticsearch API key authentication")
            elif elastic_user and elastic_password:
                elastic_kwargs["basic_auth"] = (elastic_user, elastic_password)
                logger.info("Using Elasticsearch basic authentication")

            elastic = Elasticsearch(**elastic_kwargs)
            if not elastic.ping():
                logger.error("Failed to connect to Elasticsearch")
                sys.exit(1)
            logger.info("Successfully connected to Elasticsearch")

        updater = BreadcrumbUpdater(
            elastic=elastic,
            index_name=index,
            atlas_url=atlas_url,
            access_token=access_token,
            atlas_username=atlas_user,
            atlas_password=atlas_password,
            keycloak_url=keycloak_url,
            keycloak_client_id=keycloak_client_id,
            keycloak_realm=keycloak_realm,
            keycloak_client_secret=keycloak_client_secret,
            choose_first_parent=choose_first_parent,
            dry_run=dry_run,
        )

        total_updated = asyncio.run(
            updater.update_multiple_entities_breadcrumbs(
                entity_guids=entity_guids,
                include_descendants=include_descendants,
            )
        )

        if dry_run:
            logger.info(f"[DRY RUN] Would have updated {total_updated} documents")
        else:
            elastic.close()
            logger.info(f"Breadcrumb update completed. Total documents updated: {total_updated}")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error during breadcrumb update: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
