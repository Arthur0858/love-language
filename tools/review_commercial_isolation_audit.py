#!/usr/bin/env python3
"""Verify that indexed pages stay focused on free editorial and tool routes."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOINDEX_DESTINATIONS = (
    "/resources/",
    "/luna-yoga-music/",
    "/keepsakes/",
    "/go/luna",
)
COMMERCE_HOSTS = (
    "gumroad.com",
    "amazon.com",
    "amazon.co.jp",
    "books.com.tw",
)
COMMERCIAL_MARKERS = (
    "rel=\"noopener noreferrer sponsored\"",
    "affiliate-disclosure",
    '"@type":"Offer"',
    '"@type":"Product"',
    "data-luna-product=",
)
VISIBLE_SALES_PHRASES = (
    "開啟起手包",
    "Healing Vibes Starter Pack",
    "前往博客來",
    "聯盟行銷連結",
    "付費報告",
)


def visible_text(raw: str) -> str:
    raw = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def page_path(route: str) -> Path:
    clean = route.strip("/")
    return ROOT / clean / "index.html" if clean else ROOT / "index.html"


def main() -> int:
    site_index = json.loads((ROOT / "site-index.json").read_text(encoding="utf-8"))
    issues: list[str] = []
    pages_checked = 0
    destinations_checked = 0
    markers_checked = 0
    fragments_checked = 0

    for page in site_index["pages"]:
        route = page["path"]
        path = page_path(route)
        raw = path.read_text(encoding="utf-8", errors="ignore")
        text = visible_text(raw)
        pages_checked += 1

        ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', raw, flags=re.I))
        for fragment in re.findall(r'\bhref=["\']#([^"\']+)["\']', raw, flags=re.I):
            if not fragment or "${" in fragment:
                continue
            fragments_checked += 1
            if fragment not in ids:
                issues.append(f"{route}: same-page fragment has no target #{fragment}")

        for destination in NOINDEX_DESTINATIONS:
            destinations_checked += 1
            if route == "/about/" and destination == "/resources/":
                continue
            if destination in raw:
                issues.append(f"{route}: indexed page exposes noindex destination {destination}")

        for host in COMMERCE_HOSTS:
            markers_checked += 1
            if host in raw.lower():
                issues.append(f"{route}: indexed page exposes commerce host {host}")

        for marker in COMMERCIAL_MARKERS:
            markers_checked += 1
            if marker.lower() in raw.lower():
                issues.append(f"{route}: indexed page exposes commercial marker {marker}")

        if route not in {"/about/", "/privacy/", "/terms/"}:
            for phrase in VISIBLE_SALES_PHRASES:
                markers_checked += 1
                if phrase.lower() in text.lower():
                    issues.append(f"{route}: indexed page exposes sales-oriented copy {phrase}")

    print(f"review_commercial_pages_checked={pages_checked}")
    print(f"review_commercial_destinations_checked={destinations_checked}")
    print(f"review_commercial_markers_checked={markers_checked}")
    print(f"review_fragment_targets_checked={fragments_checked}")
    print(f"review_commercial_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
