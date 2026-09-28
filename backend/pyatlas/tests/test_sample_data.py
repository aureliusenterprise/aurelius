"""Imports ``sample_data.zip`` (an Apache Atlas export placed in the project folder) and checks that every
entity arrives with the attributes, relationships, direct classifications, labels and business metadata of
the archive.  Skipped when the file is not there.

Propagated classifications are recomputed from the relationship definitions on import (as Apache Atlas
does), so they are not compared with the archive.
"""
import json
import os
import zipfile

import pytest

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PYATLAS_SAMPLE_ZIP, else sample_data.zip next to pyatlas, else the Aurelius sample data of the monorepo
ZIP = next((p for p in (os.environ.get("PYATLAS_SAMPLE_ZIP"), os.path.join(_HERE, "sample_data.zip"),
                        os.path.join(_HERE, "..", "m4i-atlas-post-install", "data", "sample_data.zip"))
            if p and os.path.exists(p)), os.path.join(_HERE, "sample_data.zip"))


def _is_ref(v):
    first = v[0] if isinstance(v, list) and v else v
    return isinstance(first, dict) and "guid" in first


def _rels(e):
    out = {}
    for k, v in (e.get("relationshipAttributes") or {}).items():
        items = v if isinstance(v, list) else ([v] if v else [])
        s = {x["guid"] for x in items if isinstance(x, dict) and x.get("relationshipStatus", "ACTIVE") == "ACTIVE"}
        if s:
            out[k] = s
    return out


@pytest.mark.skipif(not os.path.exists(ZIP), reason="sample_data.zip not present")
def test_sample_data_import(client):
    src = zipfile.ZipFile(ZIP)
    order = json.loads(src.read("atlas-export-order.json"))
    with open(ZIP, "rb") as f:
        r = client.post("/api/atlas/admin/import", files={"data": ("sample_data.zip", f, "application/zip")})
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["operationStatus"] == "SUCCESS", res.get("failures")
    assert set(order) <= set(res["processedEntities"])
    problems = []
    for g in order:
        exp = json.loads(src.read(f"{g}.json"))["entity"]
        got = client.get(f"/api/atlas/v2/entity/guid/{g}").json().get("entity")
        if got is None:
            problems.append((g, "missing"))
            continue
        for k, v in (exp.get("attributes") or {}).items():
            if _is_ref(v):
                continue
            gv = (got.get("attributes") or {}).get(k)
            if v != gv and not (v in (None, [], {}) and gv in (None, [], {})):
                problems.append((g, k, v, gv))
        if _rels(exp) != _rels(got):
            problems.append((g, "relationships"))
        direct = lambda e: sorted(c["typeName"] for c in e.get("classifications") or [] if c.get("entityGuid") in (None, e["guid"]))  # noqa: E731
        if direct(exp) != direct(got):
            problems.append((g, "classifications", direct(exp), direct(got)))
        for k in ("labels", "businessAttributes", "customAttributes", "status"):
            if (exp.get(k) or None) != (got.get(k) or None):
                problems.append((g, k))
    assert not problems, problems[:10]
