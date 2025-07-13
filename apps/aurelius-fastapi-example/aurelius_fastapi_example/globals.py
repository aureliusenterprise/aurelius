import importlib.metadata
import logging

from aurelius_fastapi_example.models import Settings

LOGGER = logging.getLogger("app")
METADATA = importlib.metadata.metadata("aurelius-fastapi-example")
SETTINGS = Settings()
