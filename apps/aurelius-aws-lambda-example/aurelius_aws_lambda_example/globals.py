import importlib.metadata

from aws_lambda_powertools import Logger

from aurelius_aws_lambda_example.models import Settings

NAME = "aurelius-aws-lambda-example"
METADATA = importlib.metadata.metadata(NAME)

SETTINGS = Settings()  # type: ignore[load settings from environment variables]

LOGGER = Logger(
    level=SETTINGS.log_level,
    log_uncaught_exceptions=True,
    service=NAME,
)
