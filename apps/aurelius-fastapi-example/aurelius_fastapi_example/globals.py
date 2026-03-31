import importlib.metadata
import logging

NAME = "aurelius-fastapi-example"
METADATA = importlib.metadata.metadata(NAME)

LOGGER = logging.getLogger(NAME)
