#!/usr/bin/env python3
"""Check exact DOI and title parity in the generated public records block."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")
DOI_URL_RE = re.compile(r"^https://doi\.org/10\.5281/zenodo\.\d+$")
START = "<!-- BEGIN GENERATED: PUBLIC_RECORDS -->"
END = "<!-- END GENERATED: PUBLIC_RECORDS -->"


class RecordsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_strong = False
        self.in_link = False
        self.current_strong: list[str] = []
        self.current_link: list[str] = []
        self.titles: list[str] = []
        self.dois: list[str] = []
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "strong":
            self.in_strong = True
            self.current_strong = []
        if tag == "a":
            self.in_link = True
            self.current_link = []
            self.urls.append(attr.get("href") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "strong" and self.in_strong:
            self.titles.append("".join(self.current_strong).strip())
            self.in_strong = False
        if tag == "a" and self.in_link:
            self.dois.append("".join(self.current_link).strip())
            self.in_link = False

    def handle_data(self, data: str) -> None:
        if self.in_strong:
            self.current_strong.append(data)
        if self.in_link:
            self.current_link.append(data)


def generated_block(index_text: str) -> str:
    start = index_text.find(START)
    end = index_text.find(END)
    if start == -1 or end == -1 or end < start:
        raise AssertionError("generated Public Records block markers are missing")
    return index_text[start + len(START):end]


def main() -> int:
    try:
        records = json.loads((ROOT / "data" / "records.json").read_text(encoding="utf-8"))
        index_text = (ROOT / "index.html").read_text(encoding="utf-8")
        block = generated_block(index_text)

        expected = [(item["title"], item["doi"], item["url"]) for item in records.get("public_records", [])]
        expected_dois = [doi for _, doi, _ in expected]
        if len(expected_dois) != len(set(expected_dois)):
            raise AssertionError("duplicate DOI entries in records.json")
        for _, doi, url in expected:
            if not re.fullmatch(r"10\.5281/zenodo\.\d+", doi):
                raise AssertionError(f"malformed DOI in records.json: {doi}")
            if not DOI_URL_RE.match(url):
                raise AssertionError(f"malformed DOI URL in records.json: {url}")

        parser = RecordsParser()
        parser.feed(block)
        actual = list(zip(parser.titles, parser.dois, parser.urls))

        if actual != expected:
            raise AssertionError("generated Public Records block does not match records.json title/DOI/url order")

        block_dois = parser.dois
        extras = sorted(set(block_dois) - set(expected_dois))
        if extras:
            raise AssertionError(f"generated block contains DOI not present in records.json: {', '.join(extras)}")

    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: index public record block matches data/records.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
