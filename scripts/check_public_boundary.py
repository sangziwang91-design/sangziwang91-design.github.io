#!/usr/bin/env python3
"""Check public-facing boundary language and forbidden claim patterns."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATTERNS = [
    "validated benchmark",
    "peer-reviewed standard",
    "accepted by CACM",
    "alignment solution",
    "production-grade benchmark",
    "regulatory-grade standard",
    "file://",
    "localhost",
    "D:/",
    "C:/",
    "/mnt/data",
]

PRIVATE_CORE_TERMS = [
    "SignalBus",
    "CandidatePool",
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
]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: missing required text: {needle}")


def has_boundary_language(text: str) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in BOUNDARY_MARKERS)


def main() -> int:
    try:
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        require(index, "Claim Ceiling", "index.html")
        require(index, "Disclosure Boundary", "index.html")
        require(index, "Next Research Gate", "index.html")

        all_public_files = [
            ROOT / "index.html",
            ROOT / "reality-check.html",
            ROOT / "article-ai-projects-die.html",
            ROOT / "cards.html",
        ]
        for path in all_public_files:
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.lower() in lowered:
                    raise AssertionError(f"{path.name}: forbidden public pattern found: {pattern}")

        for term in PRIVATE_CORE_TERMS:
            if re.search(re.escape(term), index, re.IGNORECASE):
                raise AssertionError(f"index.html: overly specific private-core term remains: {term}")

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
