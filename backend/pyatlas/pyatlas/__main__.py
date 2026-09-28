"""``python -m pyatlas`` starts the server."""
from __future__ import annotations

import argparse
import logging
import os


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="pyatlas metadata server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=21000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--in-memory", action="store_true",
                        help="use a throw-away in-memory store instead of Elasticsearch (demo/development only)")
    parser.add_argument("--import-zip", action="append", default=[], metavar="ZIP",
                        help="import an Atlas export ZIP at start-up (once; may be repeated)")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.log_level.lower() != "debug":
        logging.getLogger("elastic_transport").setLevel(logging.WARNING)   # one line per ES request otherwise
    if args.in_memory:
        os.environ["PYATLAS_IN_MEMORY"] = "true"
    if args.import_zip:
        existing = [p for p in os.environ.get("PYATLAS_IMPORT_ON_START", "").split(",") if p.strip()]
        os.environ["PYATLAS_IMPORT_ON_START"] = ",".join(existing + [os.path.abspath(p) for p in args.import_zip])
    uvicorn.run("pyatlas.main:app_factory", factory=True, host=args.host, port=args.port, reload=args.reload,
                log_level=args.log_level)


if __name__ == "__main__":
    main()
