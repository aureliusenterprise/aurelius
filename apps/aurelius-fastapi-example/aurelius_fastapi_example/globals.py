import importlib.metadata
import logging

from aurelius_fastapi_example.models import Settings

NAME = "aurelius-fastapi-example"
METADATA = importlib.metadata.metadata(NAME)

SETTINGS = Settings()  # type: ignore[settings are loaded from environment variables]

LOGGER = logging.getLogger(NAME)
