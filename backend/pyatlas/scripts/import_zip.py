"""Import an Atlas export ZIP (Apache Atlas or pyatlas) into a running server.

    python scripts/import_zip.py sample_data.zip --url http://localhost:21000 --user admin --password admin
    python scripts/import_zip.py export.zip --options '{"replicatedFrom": "dc1$prod"}'
"""
import argparse
import json
import time

import httpx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip")
    ap.add_argument("--url", default="http://localhost:21000")
    ap.add_argument("--user", default="admin")
    ap.add_argument("--password", default="admin")
    ap.add_argument("--options", default="{}", help="import options as JSON (transforms, startGuid, ...)")
    a = ap.parse_args()
    t0 = time.time()
    with open(a.zip, "rb") as f, httpx.Client(base_url=a.url, auth=(a.user, a.password), timeout=3600) as c:
        r = c.post("/api/atlas/admin/import", files={"data": (a.zip, f, "application/zip")},
                   data={"request": json.dumps({"options": json.loads(a.options)})})
    r.raise_for_status()
    res = r.json()
    print(f"{res['operationStatus']}: {len(res.get('processedEntities') or [])} entities in {time.time() - t0:.1f}s")
    for k, v in sorted((res.get("metrics") or {}).items()):
        print(f"  {k}: {v}")
    for g, msg in list((res.get("failures") or {}).items())[:20]:
        print(f"  FAILED {g}: {msg}")


if __name__ == "__main__":
    main()
