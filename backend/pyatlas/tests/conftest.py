"""Test fixtures.

By default the tests run against the in-memory Elasticsearch stand-in (``pyatlas/store/memory.py``).
Set ``PYATLAS_TEST_ES_HOSTS`` to run the very same tests against a real Elasticsearch cluster, e.g.::

    PYATLAS_TEST_ES_HOSTS=http://localhost:9200 pytest
    # optional: PYATLAS_TEST_ES_USERNAME / PYATLAS_TEST_ES_PASSWORD / PYATLAS_TEST_ES_VERIFY_CERTS=false

Every test then gets its own index prefix (``pytest_<random>_*``); the indices are deleted afterwards.
"""
import os
import sys
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyatlas.config import Settings  # noqa: E402
from pyatlas.main import create_app  # noqa: E402
from tests.fake_es import FakeElasticsearch  # noqa: E402

REAL_ES = os.environ.get("PYATLAS_TEST_ES_HOSTS")
_CACHE = {}


def _real_es_kwargs():
    kw = {}
    if os.environ.get("PYATLAS_TEST_ES_USERNAME"):
        kw["basic_auth"] = (os.environ["PYATLAS_TEST_ES_USERNAME"], os.environ.get("PYATLAS_TEST_ES_PASSWORD", ""))
    if os.environ.get("PYATLAS_TEST_ES_VERIFY_CERTS", "true").lower() == "false":
        kw["verify_certs"] = False
    return kw


def _drop_indices(prefix: str) -> None:
    from elasticsearch import Elasticsearch
    es = Elasticsearch([h.strip() for h in REAL_ES.split(",")], **_real_es_kwargs())
    try:
        names = list(es.indices.get(index=f"{prefix}_*", expand_wildcards="all").keys())
        for i in range(0, len(names), 20):
            es.indices.delete(index=",".join(names[i:i + 20]))
    finally:
        es.close()


class _Client(TestClient):
    es_prefix = None

    def __exit__(self, *exc):
        try:
            return super().__exit__(*exc)
        finally:
            if self.es_prefix and REAL_ES:
                _drop_indices(self.es_prefix)


def _fresh_client(auth_enabled=True, **overrides):
    settings_kw = dict(auth_enabled=auth_enabled, typedef_cache_check_secs=0,
                       download_dir=tempfile.mkdtemp(prefix="pyatlas-dl-"))
    if REAL_ES:
        prefix = f"pytest_{uuid.uuid4().hex[:10]}"
        settings_kw.update(es_hosts=REAL_ES, es_index_prefix=prefix,
                           es_username=os.environ.get("PYATLAS_TEST_ES_USERNAME"),
                           es_password=os.environ.get("PYATLAS_TEST_ES_PASSWORD"),
                           es_verify_certs=os.environ.get("PYATLAS_TEST_ES_VERIFY_CERTS", "true").lower() != "false")
        settings_kw.update(overrides)
        app = create_app(Settings(**settings_kw))
        fake = None
    else:
        prefix = None
        settings_kw.update(es_index_prefix="test")
        settings_kw.update(overrides)
        fake = FakeElasticsearch()
        # loading the bundled models takes a moment; reuse the typedef documents between tests
        if "typedefs" in _CACHE:
            fake.data.update({k: {i: dict(v) for i, v in d.items()} for k, d in _CACHE["typedefs"].items()})
        app = create_app(Settings(**settings_kw), es_client=fake)
    client = _Client(app)
    client.es_prefix = prefix
    try:
        client.__enter__()
    except BaseException:
        if prefix:
            _drop_indices(prefix)
        raise
    if fake is not None and "typedefs" not in _CACHE:
        _CACHE["typedefs"] = {k: {i: dict(v) for i, v in d.items()} for k, d in fake.data.items()
                              if k in ("test_typedefs", "test_meta")}
    client.auth = ("admin", "admin")
    client.fake = fake
    return client


@pytest.fixture
def client():
    c = _fresh_client()
    yield c
    c.__exit__(None, None, None)


@pytest.fixture
def anon_client():
    c = _fresh_client()
    c.auth = None
    yield c
    c.__exit__(None, None, None)
