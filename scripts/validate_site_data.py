#!/usr/bin/env python3
"""Validate public-site data files for the GitHub Pages research portal."""

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

DOI_RE = re.compile(r"^10\.5281/zenodo\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STALE_MANUSCRIPT_PATTERNS = [
    "CACM",
    "submitted / under review",
    "under-review manuscript",
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
]


def load_json(path: Path) -> Any:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_absent(text: str, patterns: list[str], label: str) -> None:
    lowered = text.lower()
    for pattern in patterns:
        if pattern.lower() in lowered:
            raise AssertionError(f"{label}: forbidden or stale text found: {pattern}")


def validate_records() -> None:
    records = load_json(DATA_DIR / "records.json")
    assert records.get("schema_version"), "records.json missing schema_version"
    assert records.get("last_structural_update") == "2026-06-19", "records.json last_structural_update must be 2026-06-19"
    assert isinstance(records.get("public_records"), list), "public_records must be a list"
    assert len(records["public_records"]) >= 10, "expected at least 10 public records"
    assert records.get("manuscript_status_policy"), "records.json missing manuscript_status_policy"

    seen_ids: set[str] = set()
    seen_dois: set[str] = set()
    for idx, record in enumerate(records["public_records"], start=1):
        missing = REQUIRED_RECORD_FIELDS - set(record)
        assert not missing, f"record #{idx} missing fields: {sorted(missing)}"

        rid = record["id"]
        assert rid not in seen_ids, f"duplicate record id: {rid}"
        seen_ids.add(rid)

        doi = record["doi"]
        assert doi not in seen_dois, f"duplicate DOI: {doi}"
        seen_dois.add(doi)
        assert DOI_RE.match(doi), f"{rid}: DOI has unexpected format: {doi}"
        assert record["url"] == f"https://doi.org/{doi}", f"{rid}: URL does not match DOI"
        assert_absent(json.dumps(record, ensure_ascii=False), STALE_MANUSCRIPT_PATTERNS, f"record {rid}")

    manuscripts = records.get("manuscripts", [])
    assert isinstance(manuscripts, list), "manuscripts must be a list"
    for manuscript in manuscripts:
        if manuscript.get("display_authorized") is not True:
            raise AssertionError("manuscript entries require display_authorized: true")
        for field in ("status_as_of", "status", "public_note"):
            assert manuscript.get(field), f"authorized manuscript missing {field}"
        assert DATE_RE.match(manuscript["status_as_of"]), "manuscript status_as_of must be YYYY-MM-DD"
        assert_absent(json.dumps(manuscript, ensure_ascii=False), STALE_MANUSCRIPT_PATTERNS, "manuscript")

    assert_absent(json.dumps(records, ensure_ascii=False), ["CACM", "submitted / under review"], "records.json")


def validate_systems() -> None:
    systems = load_json(DATA_DIR / "systems.json")
    assert systems.get("schema_version"), "systems.json missing schema_version"
    assert systems.get("last_structural_update") == "2026-06-19", "systems.json last_structural_update must be 2026-06-19"
    assert isinstance(systems.get("layers"), list), "layers must be a list"
    assert len(systems["layers"]) == 5, "expected five public-safe system layers"

    allowed_titles = {
        "Public Methodology",
        "Measurement and Dataset Layer",
        "Public-Safe Runtime Summary",
        "Withheld Internal Validation and Governance",
        "Protected Internal Infrastructure",
    }
    titles = {layer.get("title") for layer in systems["layers"]}
    assert titles == allowed_titles, f"unexpected systems layer titles: {sorted(titles)}"

    serialized = json.dumps(systems, ensure_ascii=False)
    assert_absent(serialized, PRIVATE_COMPONENT_TERMS, "systems.json")

    for layer in systems["layers"]:
        for field in ("id", "title", "visibility", "systems"):
            assert field in layer, f"layer missing {field}: {layer}"
        assert isinstance(layer["systems"], list), f"{layer['id']}: systems must be a list"
        for item in layer["systems"]:
            for field in ("id", "name", "description", "status"):
                assert field in item, f"{layer['id']}: system missing {field}: {item}"

    boundary = systems.get("public_private_boundary", {})
    assert boundary.get("withheld"), "withheld boundary list must not be empty"


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
