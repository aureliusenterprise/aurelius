"""Test support: a disposable Elasticsearch 9 node for component tests.

Requires the ``testing`` extra (``testcontainers``) and a Docker daemon.
"""

import secrets
import time
from collections.abc import Iterator
from contextlib import contextmanager

from pydantic import AnyHttpUrl, SecretStr

from aurelius_atlas_store_es.settings import ElasticsearchSettings

try:
    from testcontainers.core.container import DockerContainer
except ImportError as error:  # pragma: no cover - exercised only without the extra
    msg = "aurelius_atlas_store_es.testing needs the 'testing' extra: aurelius-atlas-store-es[testing]"
    raise ImportError(msg) from error

DEFAULT_IMAGE = "docker.elastic.co/elasticsearch/elasticsearch:9.1.5"
_PORT = 9200
_STABLE_AUTHENTICATIONS = 3


def container_environment(password: str) -> dict[str, str]:
    """Return the environment for a single-node test cluster with security on.

    Args:
        password: Password of the ``elastic`` user.

    Returns:
        Environment variables for the Elasticsearch container (see DD-003).
    """
    return {
        "discovery.type": "single-node",
        "ELASTIC_PASSWORD": password,
        "xpack.security.enabled": "true",
        "xpack.security.http.ssl.enabled": "false",
        "xpack.security.transport.ssl.enabled": "false",
        "cluster.routing.allocation.disk.threshold_enabled": "false",
        "ES_JAVA_OPTS": "-Xms512m -Xmx512m",
    }


@contextmanager
def elasticsearch_node(
    image: str = DEFAULT_IMAGE,
    *,
    index_prefix: str = "test",
    startup_timeout: float = 180.0,
) -> Iterator[ElasticsearchSettings]:
    """Start an Elasticsearch node and yield settings that reach it.

    Args:
        image: The Elasticsearch image to run.
        index_prefix: Index prefix for the yielded settings.
        startup_timeout: Seconds to wait for the node to accept authenticated requests.

    Yields:
        Settings pointing at the running node, with a random ``elastic`` password.

    Raises:
        TimeoutError: If the node does not become ready in time.
    """
    password = secrets.token_urlsafe(16)
    container = DockerContainer(image).with_exposed_ports(_PORT)
    for key, value in container_environment(password).items():
        container = container.with_env(key, value)
    with container:
        url = f"http://{container.get_container_host_ip()}:{container.get_exposed_port(_PORT)}"
        settings = ElasticsearchSettings(
            hosts=(AnyHttpUrl(url),),
            username="elastic",
            password=SecretStr(password),
            index_prefix=index_prefix,
            request_timeout=30.0,
        )
        _wait_until_ready(settings, startup_timeout)
        yield settings


def _wait_until_ready(settings: ElasticsearchSettings, timeout: float) -> None:
    """Block until the node is green and authentication is stable.

    Right after start-up Elasticsearch authenticates ``elastic`` from its bootstrap
    password, then switches to the security index once that index exists; requests in
    between can fail with HTTP 401. Waiting for a green cluster and several consecutive
    successful authentications avoids that window (DD-003).
    """
    import httpx  # noqa: PLC0415 - only needed while starting a container

    deadline = time.monotonic() + timeout
    base = settings.host_urls[0]
    auth = settings.basic_auth
    streak = 0
    while time.monotonic() < deadline and streak < _STABLE_AUTHENTICATIONS:
        try:
            health = httpx.get(f"{base}/_cluster/health?wait_for_status=green&timeout=1s", auth=auth, timeout=5.0)
            who = httpx.get(f"{base}/_security/_authenticate", auth=auth, timeout=5.0)
            ok = health.status_code == httpx.codes.OK and who.status_code == httpx.codes.OK
            ok = ok and health.json().get("status") == "green"
        except httpx.HTTPError:
            ok = False
        streak = streak + 1 if ok else 0
        time.sleep(1.0)
    if streak < _STABLE_AUTHENTICATIONS:
        msg = f"Elasticsearch did not become ready within {timeout} seconds"
        raise TimeoutError(msg)
