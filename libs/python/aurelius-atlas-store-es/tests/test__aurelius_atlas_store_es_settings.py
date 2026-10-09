import pytest
from aurelius_atlas_store_es.settings import ElasticsearchSettings
from pydantic import AnyHttpUrl, SecretStr, ValidationError

TARGET = "aurelius_atlas_store_es.settings.ElasticsearchSettings"


@pytest.mark.covers(TARGET, rules=["ESI-01"])
def test__settings_defaults_point_at_local_dev_cluster() -> None:
    """Defaults reach the local dev node as user elastic with prefix atlas."""
    settings = ElasticsearchSettings(password=SecretStr("changeme"))

    assert settings.host_urls == ["http://localhost:9200"]
    assert settings.username == "elastic"
    assert settings.index_prefix == "atlas"


@pytest.mark.covers(TARGET, rules=["ESI-02"])
@pytest.mark.parametrize(
    ("username", "password"),
    [("elastic", None), (None, SecretStr("x"))],
)
def test__settings_reject_half_credentials(username: str | None, password: SecretStr | None) -> None:
    """A username without a password, or the reverse, is a configuration error."""
    with pytest.raises(ValidationError, match="username and password must be set together"):
        ElasticsearchSettings(username=username, password=password)


@pytest.mark.covers(f"{TARGET}.basic_auth", rules=["ESI-02"])
def test__settings_basic_auth_is_none_without_credentials() -> None:
    """Without credentials the client gets no basic-auth header."""
    assert ElasticsearchSettings(username=None, password=None).basic_auth is None


@pytest.mark.covers(f"{TARGET}.basic_auth")
def test__settings_basic_auth_reveals_password_only_to_client() -> None:
    """The pair carries the clear password, while the model's repr keeps it hidden."""
    settings = ElasticsearchSettings(password=SecretStr("s3cret"))

    assert settings.basic_auth == ("elastic", "s3cret")
    assert "s3cret" not in repr(settings)


@pytest.mark.covers(f"{TARGET}.host_urls")
def test__settings_host_urls_strip_trailing_slash() -> None:
    """Several hosts are kept in order, as strings without a trailing slash."""
    settings = ElasticsearchSettings(
        hosts=(AnyHttpUrl("http://es-1:9200/"), AnyHttpUrl("https://es-2:9243")),
        password=SecretStr("x"),
    )

    assert settings.host_urls == ["http://es-1:9200", "https://es-2:9243"]


@pytest.mark.covers(TARGET, rules=["ESI-03"])
@pytest.mark.parametrize("prefix", ["", "Atlas", "1atlas", "atlas prod", "a" * 33])
def test__settings_reject_invalid_index_prefix(prefix: str) -> None:
    """Index prefixes are lower-case, start with a letter and have at most 32 characters."""
    with pytest.raises(ValidationError):
        ElasticsearchSettings(password=SecretStr("x"), index_prefix=prefix)


@pytest.mark.covers(TARGET)
def test__settings_reject_empty_hosts_and_non_positive_timeout() -> None:
    """At least one host and a positive timeout are required."""
    with pytest.raises(ValidationError):
        ElasticsearchSettings(hosts=(), password=SecretStr("x"))
    with pytest.raises(ValidationError):
        ElasticsearchSettings(request_timeout=0, password=SecretStr("x"))
