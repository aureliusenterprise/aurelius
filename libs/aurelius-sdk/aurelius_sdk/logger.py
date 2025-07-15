"""
This module provides logging utilities for Aurelius applications.

Note:
    Please install the `logger` extra to use this module.
"""

import logging

import coloredlogs

DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"
DEFAULT_FMT = "{asctime} {levelname:<8} [{name}] {message}"


def setup_logger(level: int | str = logging.INFO) -> None:
    """
    Set up logging for the application with a standardized log output format.

    This function configures the logging system to use the specified logging level, with a custom log format that
    includes the timestamp, log level, logger name, and log message. Log levels can be provided as either an integer or
    a string corresponding to standard logging levels.

    - `CRITICAL`
    - `ERROR`
    - `WARNING`
    - `INFO`
    - `DEBUG`

    Args:
        level (int or str, optional): The logging level to set. Defaults to `logging.INFO`.

    Examples:
        Set up logging with the default level. This will log messages with a level of INFO and above.

        >>> setup_logging()

        Set up logging to show DEBUG-level messages (and above) by providing the logging level's integer value.

        >>> setup_logging(logging.DEBUG)

        Set up logging by specifying the logging level as a string. This is equivalent to the previous example.

        >>> setup_logging("DEBUG")
    """
    coloredlogs.install(
        level=level,
        fmt=DEFAULT_FMT,
        datefmt=DEFAULT_DATEFMT,
        style="{",
        reconfigure=True,
    )

    # Ensure all log handlers use the specified log format
    if default_handler := logging.getLogger().handlers[0]:
        for name in logging.getHandlerNames():
            if handler := logging.getHandlerByName(name):
                handler.setFormatter(default_handler.formatter)
