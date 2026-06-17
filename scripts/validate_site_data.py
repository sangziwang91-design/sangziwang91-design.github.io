#!/usr/bin/env python3
"""
Validate public-site data files for the GitHub Pages research portal.

This script is intentionally lightweight and dependency-free. It validates:
- JSON syntax
- required fields for public records
- DOI URL consistency
- public/private boundary guard terms in records
- layer structure in systems.json

It does not validate external link availability; add link checking separately.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

REQUIRED_RECORD_FIELDS = {
    "id",
    "title",
    "type",
    "doi",
    "url",
    "layer",
    "public_role",
    "evidence_level",
    "claim_level",
}

WITHHELD_TERMS = [
    "private workspace link",
    "raw private log",
    "unpublished experiment detail",
    "private automation chain",
]

DOI_RE = re.compile(r"^10\.5281/zenodo\.\d+$")


def load_json(path: Path) -> Any:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def assert_no_withheld_terms(text: str, label: str) -> None:
    lowered = text.lower()
    for term in WITHHELD_TERMS:
        if term.lower() in lowered:
            raise AssertionError(f"{label}: contains withheld term: {term}")


def validate_records() -> None:
    records = load_json(DATA_DIR / "records.json")
    assert records.get("schema_version"), "records.json missing schema_version"
    assert isinstance(records.get("public_records"), list), "public_records must be a list"
    assert len(records["public_records"]) >= 10, "expected at least 10 public records"

    seen_ids: set[str] = set()
    for idx, record in enumerate(records["public_records"], start=1):
        missing = REQUIRED_RECORD_FIELDS - set(record)
        assert not missing, f"record #{idx} missing fields: {sorted(missing)}"

        rid = record["id"]
        assert rid not in seen_ids, f"duplicate record id: {rid}"
        seen_ids.add(rid)

        doi = record["doi"]
        url = record["url"]
        assert DOI_RE.match(doi), f"{rid}: DOI has unexpected format: {doi}"
        assert url == f"https://doi.org/{doi}", f"{rid}: URL does not match DOI"

        assert_no_withheld_terms(json.dumps(record, ensure_ascii=False), f"record {rid}")

    for manuscript in records.get("manuscripts", []):
        public_note = manuscript.get("public_note", "")
        assert "No acceptance" in public_note, (
            f"manuscript {manuscript.get('id', '<unknown>')} must keep no-acceptance wording"
        )


def validate_systems() -> None:
    systems = load_json(DATA_DIR / "systems.json")
    assert systems.get("schema_version"), "systems.json missing schema_version"
    assert isinstance(systems.get("layers"), list), "layers must be a list"
    assert len(systems["layers"]) >= 4, "expected at least four system layers"

    for layer in systems["layers"]:
        for field in ("id", "title", "visibility", "systems"):
            assert field in layer, f"layer missing {field}: {layer}"
        assert isinstance(layer["systems"], list), f"{layer['id']}: systems must be a list"
        for item in layer["systems"]:
            for field in ("id", "name", "description", "status"):
                assert field in item, f"{layer['id']}: system missing {field}: {item}"
            assert_no_withheld_terms(json.dumps(item, ensure_ascii=False), f"system {item['id']}")

    boundary = systems.get("public_private_boundary", {})
    withheld = boundary.get("withheld", [])
    assert withheld, "withheld boundary list must not be empty"


def main() -> int:
    try:
        validate_records()
        validate_systems()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: site data files are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
