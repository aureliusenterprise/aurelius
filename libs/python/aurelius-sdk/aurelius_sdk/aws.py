"""
This module provides AWS utilities for Aurelius applications.

Note:
    Please install the `aws` extra to use this module.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_boto3_secretsmanager import SecretsManagerClient


def get_secret(client: SecretsManagerClient, secret_name: str) -> str:
    """
    Get the secret value from AWS Secrets Manager.

    Args:
        client (SecretsManagerClient): The Secrets Manager client.
        secret_name (str): The name of the secret.

    Returns:
        str: The secret value.
    """
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    return get_secret_value_response["SecretString"]
