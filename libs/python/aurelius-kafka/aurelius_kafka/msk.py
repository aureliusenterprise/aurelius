"""
This module provides auth utilities for Amazon MSK (Managed Streaming for Apache Kafka).

Note:
    Please install the `msk` extra to use this module.
"""

from aws_msk_iam_sasl_signer import MSKAuthTokenProvider


class MSKOAuthTokenProvider:
    """
    A class to handle OAuth authentication for Amazon MSK (Managed Streaming for Apache Kafka).

    This class generates OAuth tokens for MSK. It implements the signature required by `confluent_kafka` clients for
    OAUTHBEARER authentication.
    """

    def __init__(self, aws_region: str) -> None:
        """
        Initialize the MSKOAuthTokenProvider instance with the specified AWS region.

        Args:
            aws_region (str): The AWS region to use for token generation.
        """
        self.aws_region = aws_region

    def __call__(self, _: dict) -> tuple[str, float]:
        """
        Generate an OAuth token for MSK using the stored AWS region.

        Args:
            _: dict: A configuration dictionary (unused).

        Returns:
            tuple[str, float]: A tuple containing the OAuth token and its expiry time in seconds.
        """
        auth_token, expiry_ms = MSKAuthTokenProvider.generate_auth_token(self.aws_region)
        return auth_token, expiry_ms / 1000
