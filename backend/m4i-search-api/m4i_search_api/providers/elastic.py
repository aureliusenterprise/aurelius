from functools import lru_cache
from typing import Protocol

import requests
from requests.auth import HTTPBasicAuth

from m4i_search_api.settings import Settings


class KeyProvider(Protocol):
    """Protocol for providing the App Search API key."""

    def get_key(self) -> str:
        """Return the App Search API key."""
        ...


class AppSearchKeyProvider(KeyProvider):
    """Key provider that fetches and caches the App Search API key."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @lru_cache()
    def _fetch_key(self) -> str:
        """Fetch the enterprise search key from the App Search instance."""
        clean_base = str(self._settings.base_url).rstrip("/")

        # SSL verification: use CA cert if provided, otherwise disable verification
        verify = self._settings.ca_cert_path if self._settings.ca_cert_path else False

        key_response = requests.get(
            f"{clean_base}/api/as/v1/credentials/private-key",
            auth=HTTPBasicAuth(
                username=self._settings.username,
                password=self._settings.password.get_secret_value(),
            ),
            timeout=self._settings.timeout_seconds,
            verify=verify,
        )

        key_response.raise_for_status()

        key_info = key_response.json()

        return key_info["key"]

    def get_key(self) -> str:
        """Return the cached App Search API key."""
        return self._fetch_key()
