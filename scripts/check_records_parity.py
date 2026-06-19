#!/usr/bin/env python3
"""Check that public DOI records are represented on the homepage."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")


def main() -> int:
    records_path = ROOT / "data" / "records.json"
    index_path = ROOT / "index.html"

    records = json.loads(records_path.read_text(encoding="utf-8"))
    index_text = index_path.read_text(encoding="utf-8")

    dois = [item.get("doi", "") for item in records.get("public_records", [])]
    malformed = [doi for doi in dois if not re.fullmatch(r"10\.5281/zenodo\.\d+", doi)]
    if malformed:
        print(f"FAIL: malformed DOI in records.json: {', '.join(malformed)}", file=sys.stderr)
        return 1

    duplicates = sorted({doi for doi in dois if dois.count(doi) > 1})
    if duplicates:
        print(f"FAIL: duplicate DOI entries in records.json: {', '.join(duplicates)}", file=sys.stderr)
        return 1

    missing = [doi for doi in dois if doi not in index_text]
    if missing:
        print(f"FAIL: DOI missing from index.html: {', '.join(missing)}", file=sys.stderr)
        return 1

    bad_index_dois = sorted(
        doi for doi in set(DOI_RE.findall(index_text)) if not re.fullmatch(r"10\.5281/zenodo\.\d+", doi)
    )
    if bad_index_dois:
        print(f"FAIL: malformed DOI appears in index.html: {', '.join(bad_index_dois)}", file=sys.stderr)
        return 1

    print("PASS: public record DOI parity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
