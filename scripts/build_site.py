#!/usr/bin/env python3
"""Generate canonical static sections in index.html from public JSON data."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
RECORDS = ROOT / "data" / "records.json"
SYSTEMS = ROOT / "data" / "systems.json"

PUBLIC_RECORDS_START = "<!-- BEGIN GENERATED: PUBLIC_RECORDS -->"
PUBLIC_RECORDS_END = "<!-- END GENERATED: PUBLIC_RECORDS -->"
SYSTEM_MAP_START = "<!-- BEGIN GENERATED: SYSTEM_MAP -->"
SYSTEM_MAP_END = "<!-- END GENERATED: SYSTEM_MAP -->"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_records(records: dict[str, Any]) -> str:
    lines = [
        PUBLIC_RECORDS_START,
        "<!-- Generated from data/records.json. Do not edit this block manually. -->",
        '<ul class="record-list">',
    ]
    for record in records["public_records"]:
        title = esc(record["title"])
        doi = esc(record["doi"])
        url = esc(record["url"])
        public_role = esc(record["public_role"])
        lines.extend(
            [
                '  <li class="record-item">',
                f"    <strong>{title}</strong>",
                f'    <a href="{url}" target="_blank" rel="noopener noreferrer">{doi}</a>',
                f"    <span>{public_role}</span>",
                "  </li>",
            ]
        )
    lines.extend(["</ul>", PUBLIC_RECORDS_END])
    return "\n".join(lines)


def render_system_map(systems: dict[str, Any]) -> str:
    lines = [
        SYSTEM_MAP_START,
        "<!-- Generated from data/systems.json. Do not edit this block manually. -->",
        '<div class="stack-map">',
    ]
    for layer in systems["layers"]:
        title = esc(layer["title"])
        summaries = []
        for item in layer["systems"]:
            name = esc(item["name"])
            status = esc(item["status"])
            summaries.append(f"{name} ({status})")
        summary = " · ".join(summaries)
        protected_class = " protected" if str(layer.get("visibility", "")).lower() == "withheld" else ""
        lines.extend(
            [
                f'  <div class="stack-node{protected_class}">',
                f"    <strong>{title}</strong>",
                f"    <span>{summary}</span>",
                "  </div>",
            ]
        )
    lines.extend(["</div>", SYSTEM_MAP_END])
    return "\n".join(lines)


def replace_block(text: str, start: str, end: str, replacement: str) -> str:
    start_index = text.find(start)
    end_index = text.find(end)
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise AssertionError(f"Generated block markers missing or invalid: {start} / {end}")
    end_index += len(end)
    return text[:start_index] + replacement + text[end_index:]


def generate_index() -> str:
    text = INDEX.read_text(encoding="utf-8")
    records = load_json(RECORDS)
    systems = load_json(SYSTEMS)
    text = replace_block(text, PUBLIC_RECORDS_START, PUBLIC_RECORDS_END, render_records(records))
    text = replace_block(text, SYSTEM_MAP_START, SYSTEM_MAP_END, render_system_map(systems))
    if not text.endswith("\n"):
        text += "\n"
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated sections are stale")
    args = parser.parse_args()

    try:
        generated = generate_index()
        current = INDEX.read_text(encoding="utf-8")
        if args.check:
            if generated != current:
                print("FAIL: generated site sections are stale.", file=sys.stderr)
                return 1
            print("PASS: generated site sections are current.")
            return 0
        INDEX.write_text(generated, encoding="utf-8", newline="\n")
        print("PASS: generated site sections updated.")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
