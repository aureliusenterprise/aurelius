import logging
import os

if __name__ == "__config__":
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
    logger = logging.getLogger(__name__)

    required = {
        "APP_SEARCH_BASE_URL": os.getenv("APP_SEARCH_BASE_URL"),
        "APP_SEARCH_TOKEN": os.getenv("APP_SEARCH_TOKEN"),
        "AUTH_ISSUER": os.getenv("AUTH_ISSUER"),
        "AUTH_PUBLIC_KEY": os.getenv("AUTH_PUBLIC_KEY"),
    }

    missing_keys = [key for key, value in required.items() if not value]

    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

    logger.info("Configuration loaded successfully")
