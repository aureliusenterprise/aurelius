"""
This module provides testing utilities for Aurelius applications.

Note:
    Please install the `testing` extra to use this module.
"""

import logging

from testcontainers.compose import DockerCompose


def capture_docker_compose_logs(
    compose: DockerCompose,
    *services: str,
    logger: logging.Logger | None = None,
) -> None:
    """Capture logs from the given Docker Compose services. Omit services to capture all available logs."""
    stdout, stderr = compose.get_logs(*services)

    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info("---------- Docker Compose Logs ----------")

    for line in stdout.splitlines():
        logger.info(line)

    logger.info("---------- Docker Compose Error Logs ----------")

    for line in stderr.splitlines():
        logger.error(line)
