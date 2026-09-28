"""Parity checks between the current Aurelius stack (Apache Atlas + Flink + App Search) and pyatlas.

    python -m parity store    --zip export.zip            --right http://localhost:21000 --right-user admin
    python -m parity store    --left https://old/atlas2   --right http://localhost:21000 ...
    python -m parity dump     --source appsearch:https://old-ent-search#atlas-dev --out atlas-dev.json
    python -m parity indices  --left file:atlas-dev.json  --right es:http://localhost:9200#atlas_search \\
                              --engine atlas-dev [--by-qualified-name]
    python -m parity mutate   --right http://localhost:21000 --out new.json   (and --right <old> --out old.json)
    python -m parity compare-mutations old.json new.json
    python -m parity replay   --recording session.har --right http://localhost:21000 --rewrite aurelius

Every check writes ``report.md`` + ``report.json`` to ``parity-reports/<time>-<check>/`` and exits with 1 when
it finds differences (0 = pass), so it can gate CI.  Credentials can also come from the environment:
``PARITY_LEFT_USER`` / ``_PASSWORD`` / ``_TOKEN`` and ``PARITY_RIGHT_...``.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .client import HttpClient
from .report import Report, default_out_dir


def _client(args, side: str) -> HttpClient:
    url = getattr(args, side)
    env = f"PARITY_{side.upper()}_"
    return HttpClient(url, user=getattr(args, f"{side}_user") or os.environ.get(env + "USER"),
                      password=getattr(args, f"{side}_password") or os.environ.get(env + "PASSWORD"),
                      token=getattr(args, f"{side}_token") or os.environ.get(env + "TOKEN"),
                      name=f"{side}:{url}", verify_tls=not args.insecure,
                      api_prefix=getattr(args, f"{side}_api_prefix", None))


def _server_args(p: argparse.ArgumentParser, side: str, required: bool) -> None:
    p.add_argument(f"--{side}", required=required, help=f"{side} server root URL")
    p.add_argument(f"--{side}-user")
    p.add_argument(f"--{side}-password")
    p.add_argument(f"--{side}-token", help="bearer token (Keycloak)")
    p.add_argument(f"--{side}-api-prefix", help="path that replaces /api/atlas, e.g. /aurelius/atlas/atlas")


def _finish(report: Report, args) -> int:
    out = report.write(default_out_dir(Path(args.out_dir), report.check))
    report.print_summary()
    print(f"report: {out / 'report.md'}")
    return 0 if report.passed else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m parity", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default="parity-reports", help="where reports are written")
    ap.add_argument("--insecure", action="store_true", help="do not verify TLS certificates")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("store", help="check 1: stored data (export ZIP or old Atlas vs pyatlas)")
    p.add_argument("--zip", help="Atlas export ZIP as the expected data")
    _server_args(p, "left", False)
    _server_args(p, "right", True)
    p.add_argument("--types", help="comma separated entity types (live left side only; default all)")
    p.add_argument("--limit", type=int, help="compare at most N entities")
    p.add_argument("--typedefs", choices=["custom", "all", "none"], default="custom",
                   help="custom: types that are not Apache Atlas built-ins (default); all; none")

    p = sub.add_parser("dump", help="save a document set (App Search engine / ES index) to a JSON file")
    p.add_argument("--source", required=True, help="appsearch:<url>#<engine> | es:<url>#<index> | file:<path>")
    p.add_argument("--out", required=True)
    p.add_argument("--appsearch-key")
    p.add_argument("--es-user")
    p.add_argument("--es-password")

    p = sub.add_parser("indices", help="check 2: search / quality documents")
    p.add_argument("--left", required=True)
    p.add_argument("--right", required=True)
    p.add_argument("--engine", default="atlas-dev", help="atlas-dev | atlas-dev-quality | atlas-dev-gov-quality")
    p.add_argument("--allowlist", help="JSON allow-list (default parity/allowlists/<engine>)")
    p.add_argument("--by-qualified-name", action="store_true",
                   help="match documents by qualified name and compare guid-free (after 'mutate')")
    p.add_argument("--only-tag", help="only documents whose qualified name contains parity<TAG>")
    p.add_argument("--appsearch-key")
    p.add_argument("--es-user")
    p.add_argument("--es-password")

    p = sub.add_parser("mutate", help="check 3: apply the scripted changes to one server, save a manifest")
    _server_args(p, "right", True)
    p.add_argument("--tag", help="run tag used in qualified names (default random)")
    p.add_argument("--pause", type=float, default=0.0, help="seconds to wait after each step")
    p.add_argument("--out", required=True, help="manifest JSON")

    p = sub.add_parser("compare-mutations", help="check 3: compare two manifests of 'mutate'")
    p.add_argument("left")
    p.add_argument("right")

    p = sub.add_parser("replay", help="check 4: replay recorded frontend requests")
    p.add_argument("--recording", required=True, action="append", help=".har, .jsonl or access log (repeatable)")
    _server_args(p, "left", False)
    _server_args(p, "right", True)
    p.add_argument("--rewrite", action="append", default=[],
                   help="'aurelius' (proxy routes -> pyatlas paths) or regex=replacement; for the right side")
    p.add_argument("--allow-writes", action="store_true")
    p.add_argument("--min-overlap", type=float, default=0.8)
    p.add_argument("--allowlist")

    p = sub.add_parser("rules", help="phase 0: do all quality rule expressions fit the safe (eval-free) grammar?")
    p.add_argument("--definitions", action="append", default=[], help="folder with rule JSON files")
    p.add_argument("--documents", action="append", default=[], help="App Search dump / golden JSON file")
    p.add_argument("--zip", action="append", default=[], help="Atlas export ZIP (m4i_*data_quality entities)")
    _server_args(p, "left", False)
    p.add_argument("--repo-defaults", action="store_true",
                   help="also check the rules and sample data that ship in the monorepo")

    args = ap.parse_args(argv)

    if args.cmd == "store":
        from .store import LiveSource, ZipSource, compare_store
        if bool(args.zip) == bool(args.left):
            ap.error("store: give either --zip or --left")
        source = ZipSource(args.zip) if args.zip else LiveSource(
            _client(args, "left"), args.types.split(",") if args.types else None)
        return _finish(compare_store(source, _client(args, "right"), with_typedefs=args.typedefs != "none",
                                     limit=args.limit, typedef_scope=args.typedefs), args)

    if args.cmd == "dump":
        from .indices import load_documents
        docs = load_documents(args.source, args.appsearch_key, args.es_user, args.es_password, not args.insecure)
        Path(args.out).write_text(json.dumps(docs, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{len(docs)} documents -> {args.out}")
        return 0

    if args.cmd == "indices":
        from .canon import canonicalize, guid_map_from_documents
        from .indices import allowlist_for, compare_documents, load_documents
        kw = dict(appsearch_key=args.appsearch_key, es_user=args.es_user, es_password=args.es_password,
                  verify_tls=not args.insecure)
        left, right = load_documents(args.left, **kw), load_documents(args.right, **kw)
        key = "id"
        if args.by_qualified_name:
            left = canonicalize(left, guid_map_from_documents(left))
            right = canonicalize(right, guid_map_from_documents(right))
            key = "referenceablequalifiedname" if args.engine == "atlas-dev" else "id"
        if args.only_tag:
            needle = f"parity{args.only_tag}"
            left = [d for d in left if needle in json.dumps(d)]
            right = [d for d in right if needle in json.dumps(d)]
        report = compare_documents(left, right, allowlist_for(args.engine, args.allowlist),
                                   left_name=args.left, right_name=args.right, key=key)
        return _finish(report, args)

    if args.cmd == "mutate":
        from .mutations import run_scenario
        manifest = run_scenario(_client(args, "right"), args.tag, args.pause)
        Path(args.out).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"tag {manifest['tag']}: {len(manifest['entities'])} entities -> {args.out}")
        return 0

    if args.cmd == "compare-mutations":
        from .mutations import compare_manifests
        a = json.loads(Path(args.left).read_text(encoding="utf-8"))
        b = json.loads(Path(args.right).read_text(encoding="utf-8"))
        return _finish(compare_manifests(a, b), args)

    if args.cmd == "replay":
        from .diff import Rules
        from .replay import AURELIUS_REWRITES, read_recording, replay
        rewrites = []
        for r in args.rewrite:
            if r == "aurelius":
                rewrites += AURELIUS_REWRITES
            else:
                pat, _, rep = r.partition("=")
                rewrites.append((pat, rep))
        records = [rec for f in args.recording for rec in read_recording(f)]
        report = replay(records, _client(args, "right"), _client(args, "left") if args.left else None,
                        rewrites, allow_writes=args.allow_writes, min_overlap=args.min_overlap,
                        rules=Rules.load(args.allowlist) if args.allowlist else None)
        return _finish(report, args)
    if args.cmd == "rules":
        from itertools import chain
        from .rules_check import check, rules_from_definitions, rules_from_documents, rules_from_export, rules_from_server
        defs, docs, zips = list(args.definitions), list(args.documents), list(args.zip)
        if args.repo_defaults:
            repo = Path(__file__).resolve().parents[3]
            defs.append(Path(os.environ.get("PARITY_RULES_DIR") or repo /
                             "libs/m4i-governance-data-quality/m4i_governance_data_quality/rules/definitions"))
            data = Path(os.environ.get("PARITY_AURELIUS_DATA") or repo / "backend/m4i-atlas-post-install/data")
            docs += [data / "atlas-dev-quality.json", data / "atlas-dev-gov-quality.json"]
            zips += [data / "sample_data.zip"]
        sources = [rules_from_definitions(Path(d)) for d in defs] + [rules_from_documents(Path(d)) for d in docs] \
            + [rules_from_export(Path(z)) for z in zips if Path(z).exists()]
        if args.left:
            sources.append(rules_from_server(_client(args, "left")))
        return _finish(check(chain(*sources)), args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
