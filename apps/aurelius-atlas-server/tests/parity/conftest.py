from collections.abc import Iterator
from pathlib import Path

import pytest
from aurelius_atlas_parity.pytest_support import ParityLog
from aurelius_atlas_parity.results import PARITY_FILENAME
from aurelius_atlas_server.app import create_app
from aurelius_atlas_server.settings import ServerSettings
from aurelius_atlas_store_es.settings import ElasticsearchSettings
from fastapi.testclient import TestClient

PARITY = Path(__file__).parent
PROJECT = PARITY.parents[1]
REFERENCE = "Apache Atlas 2.4.0"


@pytest.fixture(scope="session")
def live_es() -> Iterator[ElasticsearchSettings]:
    """Start one Elasticsearch node for the parity session."""
    from aurelius_atlas_store_es.testing import elasticsearch_node  # noqa: PLC0415 - needs Docker

    with elasticsearch_node(index_prefix="parity") as settings:
        yield settings


@pytest.fixture(scope="session")
def atlas(live_es: ElasticsearchSettings) -> Iterator[TestClient]:
    """Return a client for the server running against the live node."""
    settings = ServerSettings(elasticsearch=live_es, build_revision="parity", _env_file=None)  # type: ignore[call-arg]
    with TestClient(create_app(settings), base_url="http://atlas") as client:
        yield client


@pytest.fixture(scope="session")
def parity_log() -> Iterator[ParityLog]:
    """Collect every scenario's results and write them for the test report at the end."""
    log = ParityLog(project="apps/aurelius-atlas-server", reference=REFERENCE)
    yield log
    log.write(PROJECT / PARITY_FILENAME)
