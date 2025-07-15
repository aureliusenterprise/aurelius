"""
This module provides auth utilities for the Microsoft Identity Platform.

Note:
    Please install the `msal` extra to use this module.
"""

import httpx
import msal


class MSALOAuthTokenProvider:
    """
    A class to handle OAuth authentication for the Microsoft Identity Platform.

    This class implements the `httpx` authentication provider interface to add an OAuth token
    to HTTP requests.
    """

    def __init__(
        self,
        auth: msal.ConfidentialClientApplication,
        scopes: list[str],
    ) -> None:
        """
        Initialize the MSAL authentication provider.

        Args:
            auth (msal.ConfidentialClientApplication): The MSAL client to acquire tokens.
            scopes (list[str]): The scopes to request.
        """
        self._auth = auth
        self._scopes = scopes

    def __call__(self, request: httpx.Request) -> httpx.Request:
        """
        Add the authorization header to the request.

        Args:
            request (httpx.Request): The request to modify.

        Returns:
            httpx.Request: The modified request.
        """
        response = self._auth.acquire_token_for_client(scopes=self._scopes)

        if response is None or response.get("error"):
            return request

        request.headers["Authorization"] = f"Bearer {response['access_token']}"

        return request
