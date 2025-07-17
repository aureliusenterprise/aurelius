"""
This module provides testing utilities for Aurelius applications.

Note:
    Please install the `testing` extra to use this module.
"""

import logging

from testcontainers.compose import DockerCompose

DEFAULT_LOGGER = logging.getLogger()


def capture_docker_compose_logs(
    compose: DockerCompose,
    *services: str,
    logger: logging.Logger = DEFAULT_LOGGER,
) -> None:
    """Capture logs from the given Docker Compose services. Omit services to capture all available logs."""
    stdout, stderr = compose.get_logs(*services)

    logger.info("---------- Docker Compose Logs ----------")

    for line in stdout.splitlines():
        logger.info(line)

    logger.info("---------- Docker Compose Error Logs ----------")

    for line in stderr.splitlines():
        logger.error(line)
