#!/usr/bin/env python3
"""Validate local site links, anchors, and public URL hygiene."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DOI_URL_RE = re.compile(r"^https://doi\.org/10\.5281/zenodo\.\d+$")
FORBIDDEN_RE = re.compile(r"(file://|localhost|D:/|C:/|/mnt/data)", re.IGNORECASE)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if "href" in attr and attr["href"] is not None:
            self.hrefs.append(attr["href"])
        if "id" in attr and attr["id"]:
            self.ids.add(attr["id"])
        if tag == "a" and attr.get("name"):
            self.names.add(attr["name"] or "")


def parse_html(path: Path) -> LinkParser:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def target_for(path: Path, href_path: str) -> Path:
    href_path = unquote(href_path)
    if href_path in ("", "."):
        return ROOT / "index.html"
    if href_path == "./":
        return ROOT / "index.html"
    if href_path.startswith("./"):
        href_path = href_path[2:]
    target = (path.parent / href_path).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError as exc:
        raise AssertionError(f"{path.name}: local link escapes site root: {href_path}") from exc
    if target.is_dir():
        target = target / "index.html"
    return target


def check_anchor(target: Path, anchor: str, label: str) -> None:
    parser = parse_html(target)
    anchors = parser.ids | parser.names
    if anchor not in anchors:
        raise AssertionError(f"{label}: missing anchor #{anchor} in {target.relative_to(ROOT)}")


def main() -> int:
    try:
        html_files = sorted(ROOT.glob("*.html"))
        for path in html_files:
            text = path.read_text(encoding="utf-8")
            if FORBIDDEN_RE.search(text):
                raise AssertionError(f"{path.name}: forbidden local/private path pattern found")

            parser = parse_html(path)
            for href in parser.hrefs:
                if not href.strip():
                    raise AssertionError(f"{path.name}: empty href")
                if FORBIDDEN_RE.search(href):
                    raise AssertionError(f"{path.name}: forbidden href: {href}")

                parsed = urlparse(href)
                if parsed.scheme in ("http", "https"):
                    if parsed.netloc == "doi.org" and not DOI_URL_RE.match(href):
                        raise AssertionError(f"{path.name}: malformed DOI link: {href}")
                    continue
                if parsed.scheme in ("mailto", "tel"):
                    continue

                href_path = parsed.path
                anchor = parsed.fragment

                if not href_path:
                    if not anchor:
                        raise AssertionError(f"{path.name}: empty local anchor href")
                    check_anchor(path, anchor, path.name)
                    continue

                target = target_for(path, href_path)
                if target.suffix in (".html", ".md") or href_path in (".", "./"):
                    if not target.exists():
                        raise AssertionError(f"{path.name}: missing local link target: {href}")
                    if anchor and target.suffix == ".html":
                        check_anchor(target, anchor, f"{path.name} -> {href}")
                elif target.suffix:
                    if not target.exists():
                        raise AssertionError(f"{path.name}: missing local asset: {href}")

    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: local site links and anchors are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
