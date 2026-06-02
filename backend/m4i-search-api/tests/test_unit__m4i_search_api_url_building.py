from unittest.mock import Mock

from m4i_search_api.app import build_target_url
from m4i_search_api.settings import Settings


def test__build_target_url_with_path(settings: Settings) -> None:
    """URL is correctly constructed with a path."""
    url = build_target_url(settings, "api/as/v1/search")
    assert url == "http://app-search.test/api/as/v1/search"


def test__build_target_url_with_trailing_slash_in_base(settings: Settings) -> None:
    """Trailing slash in base URL is handled correctly."""
    settings_with_slash = Mock(
        spec=Settings,
        base_url="http://app-search.test/",
    )
    url = build_target_url(settings_with_slash, "api/as/v1/search")
    assert url == "http://app-search.test/api/as/v1/search"


def test__build_target_url_with_empty_path(settings: Settings) -> None:
    """Empty path returns just the base URL."""
    url = build_target_url(settings, "")
    assert url == "http://app-search.test"


def test__build_target_url_with_leading_slash_in_path(settings: Settings) -> None:
    """Leading slash in path is handled correctly."""
    url = build_target_url(settings, "/api/as/v1/search")
    assert url == "http://app-search.test/api/as/v1/search"
