#!/usr/bin/env python3
"""Check public-facing boundary language and forbidden claim patterns."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_FILES = [
    ROOT / "index.html",
    ROOT / "reality-check.html",
    ROOT / "cards.html",
    ROOT / "article-ai-projects-die.html",
    ROOT / "evidence" / "full1000-pilot-note.md",
    ROOT / "evidence" / "full1000-pilot-note.html",
    ROOT / "data" / "records.json",
    ROOT / "data" / "systems.json",
]

FORBIDDEN_PATTERNS = [
    "CACM",
    "submitted / under review",
    "under-review manuscript",
    "accepted by CACM",
    "validated benchmark",
    "peer-reviewed standard",
    "alignment solution",
    "regulatory-grade",
    "production-grade benchmark",
    "file://",
    "localhost",
    "D:/",
    "C:/",
    "/mnt/data",
    "private workspace link",
    "raw private logs",
    "raw private log",
    "hidden scoring weights",
    "exact operational trigger",
    "private routing logic",
    "full private task bank",
    "private task packs",
    "intervention templates",
]

PRIVATE_COMPONENT_TERMS = [
    "SignalBus",
    "CandidatePool",
    "MST",
    "VB3",
    "IGS",
    "GVOS",
    "IFCE",
    "IDFS",
    "GDS-5",
    "GEO-RECYCLE",
    "GLOBAL-VECTOR",
    "Seed System",
    "private Notion architecture",
    "full coupling",
    "perturbation sequences",
]

BOUNDARY_MARKERS = [
    "not peer",
    "不是同行评审",
    "不是商业审计",
    "claim ceiling",
    "边界声明",
    "withheld",
]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: missing required text: {needle}")


def has_boundary_language(text: str) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in BOUNDARY_MARKERS)


def assert_absent(text: str, patterns: list[str], label: str) -> None:
    lowered = text.lower()
    for pattern in patterns:
        if pattern.lower() in lowered:
            raise AssertionError(f"{label}: forbidden public pattern found: {pattern}")


def main() -> int:
    try:
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        require(index, "Claim Ceiling", "index.html")
        require(index, "Disclosure Boundary", "index.html")
        require(index, "Next Research Gate", "index.html")
        require(index, 'id="evidence-package"', "index.html")

        for path in PUBLIC_FILES:
            if not path.exists():
                raise AssertionError(f"missing public file: {path.relative_to(ROOT)}")
            text = path.read_text(encoding="utf-8")
            label = str(path.relative_to(ROOT))
            assert_absent(text, FORBIDDEN_PATTERNS, label)
            assert_absent(text, PRIVATE_COMPONENT_TERMS, label)

        for name in ("reality-check.html", "article-ai-projects-die.html", "cards.html"):
            text = (ROOT / name).read_text(encoding="utf-8")
            if not has_boundary_language(text):
                raise AssertionError(f"{name}: missing public boundary language")

    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: public boundary checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
