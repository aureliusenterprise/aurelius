import importlib.metadata

from aws_lambda_powertools import Logger

NAME = "aurelius-aws-lambda-example"
METADATA = importlib.metadata.metadata(NAME)

LOGGER: Logger = Logger(
    log_uncaught_exceptions=True,
    service=NAME,
)
