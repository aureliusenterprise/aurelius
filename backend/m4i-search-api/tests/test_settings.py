from m4i_search_api.settings import build_target_url


def test_build_target_url_trims_slashes():
    assert (
        build_target_url("https://search.example.com/", "/api/as/v1/engines/atlas-dev/search.json")
        == "https://search.example.com/api/as/v1/engines/atlas-dev/search.json"
    )


def test_build_target_url_handles_root():
    assert build_target_url("https://search.example.com/", "/") == "https://search.example.com"
