"""Collects the findings of one parity check and writes ``report.json`` + ``report.md``."""
from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .diff import Difference, format_path


@dataclass
class Finding:
    item: str                       # e.g. an entity guid, a request, a document id
    kind: str                       # "missing", "extra", "different", "error"
    details: List[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"item": self.item, "kind": self.kind, "details": self.details}


class Report:
    def __init__(self, check: str, left: str, right: str):
        self.check = check
        self.left = left
        self.right = right
        self.started = time.strftime("%Y-%m-%d %H:%M:%S")
        self.checked = 0
        self.findings: List[Finding] = []
        self.stats: Dict[str, Any] = {}
        self.notes: List[str] = []

    # ------------------------------------------------------------------ collecting
    def ok(self, n: int = 1) -> None:
        self.checked += n

    def missing(self, item: str, detail: Optional[str] = None) -> None:
        self.checked += 1
        self.findings.append(Finding(item, "missing", [{"note": detail}] if detail else []))

    def extra(self, item: str, detail: Optional[str] = None) -> None:
        self.findings.append(Finding(item, "extra", [{"note": detail}] if detail else []))

    def different(self, item: str, diffs: List[Difference], prefix: str = "") -> bool:
        self.checked += 1
        if not diffs:
            return False
        details = [d.as_dict() for d in diffs]
        if prefix:
            for d in details:
                d["path"] = f"{prefix}.{d['path']}" if d["path"] != "<root>" else prefix
        self.findings.append(Finding(item, "different", details))
        return True

    def error(self, item: str, message: str) -> None:
        self.checked += 1
        self.findings.append(Finding(item, "error", [{"note": message}]))

    # ------------------------------------------------------------------ results
    @property
    def passed(self) -> bool:
        return not self.findings

    def summary(self) -> dict:
        kinds = Counter(f.kind for f in self.findings)
        paths = Counter()
        for f in self.findings:
            for d in f.details:
                if "path" in d:
                    paths[_generalize(d["path"])] += 1
        return {"check": self.check, "left": self.left, "right": self.right, "started": self.started,
                "checked": self.checked, "passed": self.passed, "findings": dict(kinds),
                "top_paths": paths.most_common(15), "stats": self.stats, "notes": self.notes}

    def write(self, out_dir: Path, max_md_findings: int = 200) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "report.json").write_text(json.dumps(
            {"summary": self.summary(), "findings": [f.as_dict() for f in self.findings]},
            indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        s = self.summary()
        lines = [f"# Parity check: {self.check}", "",
                 f"- left: `{self.left}`", f"- right: `{self.right}`", f"- started: {self.started}",
                 f"- items checked: {self.checked}",
                 f"- result: **{'PASS' if self.passed else 'FAIL'}** "
                 + (", ".join(f"{v} {k}" for k, v in s["findings"].items()) if self.findings else ""), ""]
        if self.stats:
            lines += ["## Statistics", "", "| | |", "| --- | --- |"]
            lines += [f"| {k} | {v} |" for k, v in self.stats.items()] + [""]
        if self.notes:
            lines += ["## Notes", ""] + [f"- {n}" for n in self.notes] + [""]
        if s["top_paths"]:
            lines += ["## Most frequent differences", "", "| path | count |", "| --- | --- |"]
            lines += [f"| `{p}` | {c} |" for p, c in s["top_paths"]] + [""]
        if self.findings:
            lines += ["## Findings", ""]
            for f in self.findings[:max_md_findings]:
                lines.append(f"### {f.kind}: `{f.item}`")
                for d in f.details[:20]:
                    if "path" in d:
                        lines.append(f"- `{d['path']}`: `{_short(d['left'])}` vs `{_short(d['right'])}`")
                    else:
                        lines.append(f"- {d.get('note')}")
                lines.append("")
            if len(self.findings) > max_md_findings:
                lines.append(f"... {len(self.findings) - max_md_findings} more in report.json")
        (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return out_dir

    def print_summary(self) -> None:
        s = self.summary()
        print(f"{self.check}: {'PASS' if self.passed else 'FAIL'} - {self.checked} checked, "
              f"findings {s['findings'] or 0}")
        for p, c in s["top_paths"][:8]:
            print(f"    {c:6d}  {p}")


def _generalize(path: str) -> str:
    import re
    return re.sub(r"\[\d+\]", "[]", path)


def _short(v: Any, n: int = 120) -> str:
    s = json.dumps(v, ensure_ascii=False, default=str) if not isinstance(v, str) else v
    s = s.replace("`", "'").replace("\n", " ")
    return s if len(s) <= n else s[:n] + "..."


def default_out_dir(base: Path, check: str) -> Path:
    return base / f"{time.strftime('%Y%m%d-%H%M%S')}-{check}"


__all__ = ["Report", "Finding", "default_out_dir", "format_path"]
