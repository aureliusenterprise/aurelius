"""Creates all types required for Aurelius Atlas."""

import asyncio
import logging
import os
import sys

import aiohttp
from m4i_atlas_core import (
    ConfigStore,
    create_type_defs,
    data_dictionary_types_def,
    get_keycloak_token,
)


async def main(access_token: str | None = None) -> None:
    """Create the types in Atlas."""
    if not access_token:
        access_token = get_keycloak_token()

    for types_def in [data_dictionary_types_def]:
        try:
            response = await create_type_defs(types_def, access_token)
            logging.info("Types created: %s", response.to_json())
        except aiohttp.ClientResponseError as err:  # noqa: PERF203
            if err.status == 409:  # noqa: PLR2004
                logging.warning("Types already exist. Skipping creation.")
            else:
                raise


if __name__ == "__main__":
    store = ConfigStore.get_instance()

    store.load(
        {
            "atlas.server.url": os.environ.get("ATLAS_SERVER_URL"),
            "keycloak.client.id": os.environ.get("KEYCLOAK_CLIENT_ID"),
            "keycloak.credentials.username": os.environ.get("KEYCLOAK_USERNAME"),
            "keycloak.credentials.password": os.environ.get("KEYCLOAK_ATLAS_ADMIN_PASSWORD"),
            "keycloak.realm.name": os.environ.get("KEYCLOAK_REALM_NAME"),
            "keycloak.client.secret.key": os.environ.get("KEYCLOAK_CLIENT_SECRET_KEY"),
            "keycloak.server.url": os.environ.get("KEYCLOAK_SERVER_URL"),
        },
    )

    access_token = sys.argv[1] if len(sys.argv) > 1 else None

    asyncio.run(main(access_token))
