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
    "/luna-yoga-music/",
    "/keepsakes/",
    "/luna/",
    "/go/luna-starter-click/",
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
    "需要安靜時再買",
    "Healing Vibes Starter Pack",
    "不需要全部購買",
    "不適合購買的時機",
    "衝動下單",
)

FORBIDDEN_RUNTIME_PHRASES = VISIBLE_SALES_PHRASES + (
    "八字愛情合盤報告",
    "2026 流年感情節奏報告",
    "加購 PDF",
)
PUBLIC_SUPPORT_FILES = (
    "robots.txt",
    "sitemap.xml",
    "feed.xml",
    "site.webmanifest",
    "llms.txt",
    "humans.txt",
    "security.txt",
    "ads.txt",
    "site-index.json",
    "guardian-profiles.json",
    "safety-index.json",
)
FORBIDDEN_SUPPORT_TOKENS = (
    "/en/",
    "/ja/",
    "/ko/",
    "/es/",
    "/resources/",
    "/luna-yoga-music/",
    "/keepsakes/",
    "/tools/love-compatibility/",
    "gumroad",
    "amazon.com",
    "amazon.co.jp",
    "books.com.tw",
    "付費報告",
    "八字",
    "bazi",
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
    runtime_artifacts: set[str] = set()

    for page in site_index["pages"]:
        route = page["path"]
        path = page_path(route)
        raw = path.read_text(encoding="utf-8", errors="ignore")
        text = visible_text(raw)
        pages_checked += 1
        runtime_artifacts.update(
            src.lstrip("/")
            for src in re.findall(r'<script[^>]+src=["\']([^"\']+\.js)["\']', raw, flags=re.I)
            if src.startswith("/")
        )

        ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', raw, flags=re.I))
        footer = re.search(r"<footer\b[^>]*>(.*?)</footer>", raw, flags=re.I | re.S)
        footer_markup = footer.group(1) if footer else ""
        footer_links = re.findall(r'href=["\']/resources/(?:#[^"\']*)?["\']', footer_markup, flags=re.I)
        if len(footer_links) != 1 or "延伸資源與商業揭露" not in visible_text(footer_markup):
            issues.append(f"{route}: footer must contain one clear commercial disclosure link")
        for fragment in re.findall(r'\bhref=["\']#([^"\']+)["\']', raw, flags=re.I):
            if not fragment or "${" in fragment:
                continue
            fragments_checked += 1
            if fragment not in ids:
                issues.append(f"{route}: same-page fragment has no target #{fragment}")

        for destination in NOINDEX_DESTINATIONS:
            destinations_checked += 1
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

    about_raw = page_path("/about/").read_text(encoding="utf-8", errors="ignore")
    about_resource_links = len(re.findall(r'href=["\']/resources/(?:#[^"\']*)?["\']', about_raw, re.I))
    if about_resource_links != 1:
        issues.append(f"/about/: expected only the footer disclosure route, got {about_resource_links}")
    start_raw = page_path("/start/").read_text(encoding="utf-8", errors="ignore")
    if "data-conversion-supplies" not in start_raw or "const supplyUrl = `/resources/#supply-${result.slug}`" not in start_raw:
        issues.append("/start/: quiz result must have one guardian-specific supply CTA")
    if start_raw.count("data-conversion-supplies") != 1:
        issues.append("/start/: result-specific supply CTA must appear once")

    for relative in sorted(runtime_artifacts):
        path = ROOT / relative
        if not path.exists():
            issues.append(f"indexed runtime artifact missing: {relative}")
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        for destination in NOINDEX_DESTINATIONS:
            destinations_checked += 1
            if destination in raw:
                issues.append(f"{relative}: indexed runtime data exposes noindex destination {destination}")
        for host in COMMERCE_HOSTS:
            markers_checked += 1
            if host in raw.lower() and relative not in {"resources/index.html", "luna-yoga-music/index.html"}:
                issues.append(f"{relative}: indexed runtime data exposes commerce host {host}")
        for phrase in FORBIDDEN_RUNTIME_PHRASES:
            markers_checked += 1
            if phrase.lower() in raw.lower():
                issues.append(f"{relative}: indexed runtime data exposes sales-oriented copy {phrase}")

    for relative in PUBLIC_SUPPORT_FILES:
        path = ROOT / relative
        if not path.exists():
            issues.append(f"public support file missing: {relative}")
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore").lower()
        for token in FORBIDDEN_SUPPORT_TOKENS:
            markers_checked += 1
            if token.lower() in raw:
                issues.append(f"{relative}: public support data exposes retired or commercial token {token}")

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
