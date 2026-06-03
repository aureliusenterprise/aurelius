from typing import Protocol

import requests
from cachetools import TTLCache, cached
from requests.auth import HTTPBasicAuth

from m4i_search_api.settings import Settings
import logging

LOGGER = logging.getLogger(__name__)


class KeyProvider(Protocol):
    """Protocol for providing the App Search API key."""

    def get_key(self) -> str:
        """Return the App Search API key."""
        ...


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def fetch_app_search_key(settings: Settings) -> str:
    """Fetch the enterprise search key from the App Search instance."""
    clean_base = str(settings.base_url).rstrip("/")

    key_response = requests.get(
        f"{clean_base}/api/as/v1/credentials/private-key",
        auth=HTTPBasicAuth(
            username=settings.username,
            password=settings.password.get_secret_value(),
        ),
        timeout=settings.timeout_seconds,
        verify=settings.ca_cert_path.as_posix() if settings.ca_cert_path else False,
    )

    key_response.raise_for_status()

    key_info = key_response.json()

    return key_info["key"]


class AppSearchKeyProvider(KeyProvider):
    """Key provider that fetches and caches the App Search API key."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _fetch_key(self) -> str:
        """Fetch the enterprise search key from the App Search instance."""
        return fetch_app_search_key(self._settings)

    def get_key(self) -> str:
        """Return the cached App Search API key."""
        return self._fetch_key()
