import logging
import os

from m4i_atlas_core import ConfigStore

if __name__ == "__config__":

  logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
  logger = logging.getLogger(__name__)

  store = ConfigStore.get_instance()

  required_config = {
      "atlas.server.url": os.getenv("ATLAS_SERVER_URL"),
      "keycloak.server.url": os.getenv("KEYCLOAK_SERVER_URL"),
      "keycloak.client.id": os.getenv("KEYCLOAK_CLIENT_ID"),
      "keycloak.realm.name": os.getenv("KEYCLOAK_REALM_NAME"),
  }

  missing_keys = [key for key, value in required_config.items() if value is None]

  if any(missing_keys):
      raise ValueError(f"Missing required configuration keys: {missing_keys}")

  optional_config = {}

  store.set_many(**required_config, **optional_config)

  logger.info("Configuration loaded successfully")
