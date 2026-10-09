import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest
from aurelius_atlas_parity.normalise import NormalisationRules

GUID_A = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
GUID_B = "11111111-2222-3333-4444-555555555555"
GUID_C = "99999999-8888-7777-6666-555555555555"

SCENARIO = """
name: entity-roundtrip
description: Create an entity and read it back.
steps:
  - name: create
    request:
      method: POST
      path: /api/atlas/v2/entity
      json: {entity: {typeName: DataSet, attributes: {qualifiedName: "q-${run}"}}}
    capture: {guid: "$.mutatedEntities.CREATE[0].guid"}
  - name: read
    request: {method: GET, path: "/api/atlas/v2/entity/guid/${guid}", query: {minExtInfo: "true"}}
    ignore: ["$.entity.version"]
    unordered: ["$.entity.labels"]
    deviations:
      - {path: "$.entity.attributes.owner", id: DV-01}
"""


def atlas_like(
    *, guid: str = GUID_A, owner: str = "alice", labels: tuple[str, ...] = ("b", "a"), status: int = 200
) -> Callable[[httpx.Request], httpx.Response]:
    """Return a handler that behaves like a tiny Atlas for the sample scenario."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            body = json.loads(request.content)
            name = body["entity"]["attributes"]["qualifiedName"]
            if not name.startswith("q-"):  # the scenario's ${run} substitution must have happened
                return httpx.Response(400, json={"error": name})
            return httpx.Response(200, json={"mutatedEntities": {"CREATE": [{"guid": guid, "createTime": 1}]}})
        if request.url.path != f"/api/atlas/v2/entity/guid/{guid}" or request.url.params.get("minExtInfo") != "true":
            return httpx.Response(404, json={"error": str(request.url)})
        return httpx.Response(
            status,
            json={
                "entity": {
                    "guid": guid,
                    "version": 7,
                    "updateTime": 1720000000,
                    "labels": list(labels),
                    "attributes": {"owner": owner},
                },
                "referredEntities": {GUID_B: {"guid": GUID_B}},
            },
        )

    return handler


@pytest.fixture
def workspace_root() -> Path:
    """Return the root of the real workspace."""
    return Path(__file__).resolve().parents[4]


@pytest.fixture
def scenario_dir(tmp_path: Path) -> Path:
    """Return a directory holding the sample scenario."""
    directory = tmp_path / "scenarios"
    directory.mkdir()
    (directory / "entity-roundtrip.yaml").write_text(SCENARIO)
    return directory


@pytest.fixture
def rules() -> NormalisationRules:
    """Return default normalisation rules."""
    return NormalisationRules()


def client_for(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    """Return a client whose requests go to the handler."""
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://atlas")
