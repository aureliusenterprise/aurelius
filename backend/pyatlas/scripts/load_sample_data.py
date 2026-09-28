"""Load a small sample catalogue (a Hive database, tables, columns, a process and a PII tag).

    python scripts/load_sample_data.py --url http://localhost:21000 --user admin --password admin
"""
import argparse
import os
import sys

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.helpers import create_sales_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:21000")
    ap.add_argument("--user", default="admin")
    ap.add_argument("--password", default="admin")
    a = ap.parse_args()
    c = httpx.Client(base_url=a.url, auth=(a.user, a.password), timeout=60)
    r = c.post("/api/atlas/v2/types/typedefs", json={"classificationDefs": [
        {"name": "PII", "description": "Personally identifiable information",
         "attributeDefs": [{"name": "level", "typeName": "int", "isOptional": True}]}]})
    if r.status_code not in (200, 409):
        r.raise_for_status()
    ga = create_sales_model(c)
    c.post(f"/api/atlas/v2/entity/guid/{ga['-10']}/classifications",
           json=[{"typeName": "PII", "attributes": {"level": 2}}])
    print("sample data loaded; open", a.url, "and search for hive_table")


if __name__ == "__main__":
    main()
