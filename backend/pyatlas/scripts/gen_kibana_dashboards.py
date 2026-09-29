"""Writes ``docker/kibana-dashboards.ndjson`` (single-tenant installation, indices ``atlas_*``), imported by
``docker/kibana-setup.sh``.  The objects are defined in ``pyatlas/kibana_objects.py``; multi-tenant installations get
them per Kibana space from ``aurelius-admin``.  Run ``python scripts/gen_kibana_dashboards.py`` after changes."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pyatlas.kibana_objects import ACTIVITY, USAGE, dashboards, ndjson  # noqa: E402

OUT = ROOT / "docker" / "kibana-dashboards.ndjson"
objects = [*ACTIVITY, *USAGE, *dashboards(multi_tenant=False)]
OUT.write_text(ndjson(objects), encoding="utf-8")
print(f"{OUT}: {len(objects)} saved objects")
