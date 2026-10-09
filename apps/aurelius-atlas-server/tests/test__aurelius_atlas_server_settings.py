import os
from pathlib import Path

import pytest
from aurelius_atlas_server.settings import ENV_PREFIX, ServerSettings, load_settings


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove server variables a runner may have exported (Nx loads the project's .env)."""
    for name in list(os.environ):
        if name.startswith(ENV_PREFIX):
            monkeypatch.delenv(name)


@pytest.mark.covers("aurelius_atlas_server.settings.load_settings", rules=["ADM-06"])
def test__load_settings_from_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Prefixed variables, with __ for nested values, configure the server."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AURELIUS_ATLAS_SERVER_PORT", "8080")
    monkeypatch.setenv("AURELIUS_ATLAS_SERVER_ELASTICSEARCH__PASSWORD", "pw")
    monkeypatch.setenv("AURELIUS_ATLAS_SERVER_ELASTICSEARCH__INDEX_PREFIX", "dev")

    settings = load_settings()

    assert settings.port == 8080
    assert settings.elasticsearch.basic_auth == ("elastic", "pw")
    assert settings.elasticsearch.index_prefix == "dev"
    assert settings.build_revision == "unknown"


@pytest.mark.covers("aurelius_atlas_server.settings.load_settings", rules=["ADM-06"])
def test__load_settings_reads_dotenv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A .env file in the working directory is read; the environment wins over it."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "AURELIUS_ATLAS_SERVER_PORT=9000\nAURELIUS_ATLAS_SERVER_BUILD_REVISION=f00\n"
        "AURELIUS_ATLAS_SERVER_ELASTICSEARCH__PASSWORD=pw\n"
    )
    monkeypatch.setenv("AURELIUS_ATLAS_SERVER_PORT", "9001")

    settings = load_settings()

    assert (settings.port, settings.build_revision) == (9001, "f00")


@pytest.mark.covers("aurelius_atlas_server.settings.load_settings", rules=["ADM-06"])
def test__load_settings_fails_loudly(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Invalid or missing settings stop the process with every problem listed."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AURELIUS_ATLAS_SERVER_PORT", "0")

    with pytest.raises(SystemExit, match=r"(?s)2 validation errors.*port.*elasticsearch"):
        load_settings()


@pytest.mark.covers("aurelius_atlas_server.settings.load_settings")
def test__defaults_match_atlas(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Without configuration the server listens locally on Atlas's port 21000."""
    monkeypatch.chdir(tmp_path)

    settings = ServerSettings(elasticsearch={"password": "pw"}, _env_file=None)  # type: ignore[call-arg, arg-type]

    assert (settings.host, settings.port) == ("127.0.0.1", 21000)
