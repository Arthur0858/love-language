#!/usr/bin/env python3
"""Fail closed when the AdSense editorial review surface drifts."""

from __future__ import annotations

import html
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from editorial_guides import GUIDE_EDITORIAL_CONTENT
from generate_multilingual_site import LEGACY_ZH_GUIDES, LONG_TAIL_COMPATIBILITY_PAGES
from lab_reports import LAB_REPORTS
import deploy_cloudflare_pages as deploy


ROOT = Path(__file__).resolve().parents[1]
COMMERCE_HOSTS = ("amazon.", "books.com.tw", "gumroad.com")
PRIMARY_SCHEMA_TYPES = {"AboutPage", "Article", "CollectionPage", "ContactPage", "HowTo", "WebPage", "WebSite"}
FORBIDDEN_VISIBLE = ("低價值", "高意圖", "SEO", "搜尋入口", "審核流程", "審核版", "審核面", "AdSense")
FORBIDDEN_COMMERCIAL = ("US$", "付費報告", "八字", "流年", "Love Timing Report")
EXPECTED_CORE = {
    "/", "/start/", "/garden-map/", "/compass/",
    "/guides/", "/characters/", "/theory/", "/repair-plan/",
    "/about/", "/contact/", "/privacy/", "/terms/", "/lab/",
}


def visible_text(raw: str) -> str:
    raw = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def page_file(route: str) -> Path:
    return ROOT / (route.strip("/") or ".") / "index.html"


def main_text(raw: str) -> str:
    match = re.search(r"<main\b[^>]*>(.*?)</main>", raw, re.I | re.S)
    return visible_text(match.group(1)) if match else ""


def schemas(raw: str) -> list[dict]:
    found = []
    for body in re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', raw, re.I | re.S):
        try:
            value = json.loads(html.unescape(body))
        except json.JSONDecodeError:
            continue
        found.extend(value if isinstance(value, list) else [value])
    return [value for value in found if isinstance(value, dict)]


def schema_types(item: dict) -> set[str]:
    value = item.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {entry for entry in value if isinstance(entry, str)}
    return set()


def main() -> int:
    issues: list[str] = []
    index = json.loads((ROOT / "site-index.json").read_text(encoding="utf-8"))
    routes = {page["path"] for page in index["pages"]}
    guide_routes = {f"/guides/{slug}/" for slug in GUIDE_EDITORIAL_CONTENT}
    guardian_routes = {f"/characters/{slug}/" for slug in ("iris", "noah", "vivian", "claire", "dora")}
    lab_routes = {f"/lab/{report['slug']}/" for report in LAB_REPORTS}
    expected = EXPECTED_CORE | guide_routes | guardian_routes | lab_routes

    if routes != expected:
        issues.append(f"site-index routes differ: missing={sorted(expected-routes)} extra={sorted(routes-expected)}")
    if index.get("totals", {}).get("pages") != 38 or len(routes) != 38:
        issues.append(f"site-index must contain 38 unique pages, found {len(routes)}")
    if {page["lang"] for page in index["pages"]} != {"zh"}:
        issues.append("site-index must contain only zh pages")

    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", ns)}
    expected_urls = {"https://lovetypes.tw" + route for route in expected}
    if sitemap_urls != expected_urls:
        issues.append(f"sitemap must match the 40-page review surface, found {len(sitemap_urls)} URLs")

    for route in expected:
        path = page_file(route)
        if not path.exists():
            issues.append(f"missing review page: {route}")
            continue
        raw = path.read_text(encoding="utf-8")
        text = main_text(raw)
        if '<meta name="robots" content="index, follow, max-image-preview:large"' not in raw:
            issues.append(f"indexable robots missing: {route}")
        if f'<link rel="canonical" href="https://lovetypes.tw{route}"' not in raw:
            issues.append(f"canonical mismatch: {route}")
        if 'hreflang="zh-TW"' not in raw or 'hreflang="x-default"' not in raw:
            issues.append(f"zh-only alternates missing: {route}")
        for phrase in FORBIDDEN_VISIBLE:
            if phrase in text:
                issues.append(f"forbidden public phrase {phrase!r}: {route}")
        if 'class="language-menu"' in raw:
            issues.append(f"single-language review page should not expose a language menu: {route}")
        organization_schemas = [item for item in schemas(raw) if item.get("@type") == "Organization"]
        for item in organization_schemas:
            available = item.get("contactPoint", {}).get("availableLanguage")
            if available != ["zh-TW"]:
                issues.append(f"Organization availableLanguage should match the zh-only review surface: {route}")
        primary_schemas = [item for item in schemas(raw) if schema_types(item).intersection(PRIMARY_SCHEMA_TYPES)]
        if len(primary_schemas) != 1:
            issues.append(f"review page should expose exactly one primary schema entity: {route}")
        elif "WebSite" not in schema_types(primary_schemas[0]):
            meta_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', raw, re.I)
            meta_description = html.unescape(meta_match.group(1)) if meta_match else ""
            if primary_schemas[0].get("description") != meta_description:
                issues.append(f"primary schema description should match meta description: {route}")

    lab_index_text = main_text(page_file("/lab/").read_text(encoding="utf-8"))
    lab_index_cjk = len(re.findall(r"[\u3400-\u9fff]", lab_index_text))
    if lab_index_cjk < 1100:
        issues.append(f"lab index needs enough methodology and evidence context: {lab_index_cjk} CJK")

    h2_triplets: dict[tuple[str, str, str], str] = {}
    for slug in GUIDE_EDITORIAL_CONTENT:
        route = f"/guides/{slug}/"
        raw = page_file(route).read_text(encoding="utf-8")
        text = main_text(raw)
        cjk = len(re.findall(r"[\u3400-\u9fff]", text))
        if not 2000 <= cjk <= 2800:
            issues.append(f"guide main CJK count outside 2000-2800: {slug}={cjk}")
        if raw.count("data-guide-example") < 2:
            issues.append(f"guide needs two examples: {slug}")
        if raw.count("data-guide-workbook") < 1:
            issues.append(f"guide needs a dedicated workbook: {slug}")
        for marker in ("data-guide-revision", "data-guide-followup", "data-guide-editorial-byline", "適用", "限制"):
            if marker not in raw:
                issues.append(f"guide missing {marker}: {slug}")
        if raw.count('target="_blank" rel="noopener noreferrer"') < 2 or "data-guide-sources" not in raw:
            issues.append(f"guide needs 2+ visible authoritative sources: {slug}")
        editorial_blocks = re.findall(
            r'<section class="guide-editorial-section"[^>]*>(.*?)</section>', raw, re.I | re.S
        )
        headings = []
        for block in editorial_blocks:
            match = re.search(r"<h2[^>]*>(.*?)</h2>", block, re.I | re.S)
            if match:
                headings.append(visible_text(match.group(1)))
        for pos in range(max(0, len(headings) - 2)):
            triplet = tuple(headings[pos:pos + 3])
            if triplet in h2_triplets:
                issues.append(f"repeated H2 triplet: {slug} and {h2_triplets[triplet]}")
            h2_triplets[triplet] = slug
        article_schemas = [item for item in schemas(raw) if item.get("@type") == "Article"]
        if not article_schemas:
            issues.append(f"Article schema missing: {slug}")
        for item in article_schemas:
            if item.get("author", {}).get("@type") != "Organization" or item.get("publisher", {}).get("@type") != "Organization":
                issues.append(f"Article author/publisher must be Organization: {slug}")
            if json.dumps(item, ensure_ascii=False).find('"@type": "Person"') >= 0:
                issues.append(f"fictional Person schema found: {slug}")

    evidence_hashes: dict[str, str] = {}
    for report in LAB_REPORTS:
        slug = report["slug"]
        path = ROOT / "lab" / slug / "index.html"
        raw = path.read_text(encoding="utf-8")
        report_text = main_text(raw)
        report_cjk = len(re.findall(r"[\u3400-\u9fff]", report_text))
        if not 1200 <= report_cjk <= 1800:
            issues.append(f"lab main CJK count outside 1200-1800: {slug}={report_cjk}")
        for marker in ("data-lab-environment", "data-lab-fixture", "data-lab-steps", "data-lab-results", "data-lab-raw-results", "data-lab-failure", "data-lab-fix", "data-lab-limitations"):
            if marker not in raw:
                issues.append(f"lab report missing {marker}: {slug}")
        image = ROOT / report["screenshot"].lstrip("/")
        if not image.exists() or image.stat().st_size < 1000:
            issues.append(f"lab screenshot missing or empty: {report['screenshot']}")
        detail_image = ROOT / report["secondary_screenshot"].lstrip("/")
        if not detail_image.exists() or detail_image.stat().st_size < 1000:
            issues.append(f"lab secondary screenshot missing or empty: {report['secondary_screenshot']}")
        for evidence_path in (image, detail_image):
            if not evidence_path.exists():
                continue
            digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
            if digest in evidence_hashes:
                issues.append(
                    f"lab evidence image duplicates {evidence_hashes[digest]}: "
                    f"{evidence_path.relative_to(ROOT)}"
                )
            evidence_hashes[digest] = evidence_path.relative_to(ROOT).as_posix()

    for relative in ("resources/index.html", "luna-yoga-music/index.html", "keepsakes/index.html"):
        raw = (ROOT / relative).read_text(encoding="utf-8")
        if '<meta name="robots" content="noindex, follow"' not in raw:
            issues.append(f"noindex missing: {relative}")
        route = "/" + relative.removesuffix("index.html")
        if "https://lovetypes.tw" + route in sitemap_urls:
            issues.append(f"commercial route leaked into sitemap: {route}")

    for route in expected:
        raw = page_file(route).read_text(encoding="utf-8")
        main = re.search(r"<main\b[^>]*>(.*?)</main>", raw, re.I | re.S)
        main_raw = main.group(1) if main else ""
        if route != "/about/" and re.search(r'href="/resources/(?:#[^"]*)?"', main_raw):
            issues.append(f"resources link outside About: {route}")
        if re.search(r'href="/(?:luna-yoga-music|keepsakes)/(?:#[^"]*)?"', main_raw):
            issues.append(f"commercial/noindex route linked from indexed main: {route}")
        if route != "/contact/" and "mailto:" in main_raw:
            issues.append(f"mailto leaked into indexed content: {route}")
        text = visible_text(main_raw)
        for phrase in FORBIDDEN_COMMERCIAL:
            if phrase in text:
                issues.append(f"commercial phrase {phrase!r} leaked into indexed content: {route}")
        for item in schemas(raw):
            if item.get("@type") == "Offer" or "Offer" in item.get("@type", []):
                issues.append(f"Offer schema leaked into indexed page: {route}")
            if route.startswith("/characters/") and item.get("@type") == "ProfilePage":
                issues.append(f"fictional guardian must not use ProfilePage schema: {route}")

    for path in ROOT.rglob("*.html"):
        raw = path.read_text(encoding="utf-8", errors="ignore").lower()
        if any(host in raw for host in COMMERCE_HOSTS) and path != ROOT / "resources" / "index.html":
            issues.append(f"external commerce link outside /resources/: {path.relative_to(ROOT)}")

    manifest = {path.relative_to(ROOT).as_posix() for path in deploy.collect_manifest_paths(ROOT)}
    manifest_html = {path for path in manifest if path.endswith(".html")}
    expected_manifest_html = {
        (route.strip("/") + "/index.html") if route != "/" else "index.html"
        for route in expected
    } | {"404.html", "resources/index.html", "luna-yoga-music/index.html", "keepsakes/index.html"}
    if manifest_html != expected_manifest_html:
        issues.append(
            f"deploy HTML allowlist drift: missing={sorted(expected_manifest_html-manifest_html)} "
            f"extra={sorted(manifest_html-expected_manifest_html)}"
        )
    for lang_prefix in ("", "en", "ja", "ko", "es"):
        for slug in LONG_TAIL_COMPATIBILITY_PAGES:
            path = ROOT / lang_prefix / "tools" / slug / "index.html" if lang_prefix else ROOT / "tools" / slug / "index.html"
            if path.exists():
                issues.append(f"legacy long-tail output still exists: {path.relative_to(ROOT)}")
            if path.relative_to(ROOT).as_posix() in manifest:
                issues.append(f"legacy long-tail route leaked into deploy manifest: {path.relative_to(ROOT)}")
    for report in LAB_REPORTS:
        for relative in (f"lab/{report['slug']}/index.html", report["screenshot"].lstrip("/")):
            if relative not in manifest:
                issues.append(f"lab evidence missing from deploy manifest: {relative}")
    if "lab/index.html" not in manifest:
        issues.append("lab index missing from deploy manifest")

    for slug, _title, _desc, _target in LEGACY_ZH_GUIDES:
        legacy = ROOT / "guides" / slug / "index.html"
        if legacy.exists():
            issues.append(f"legacy zh guide output still exists: {legacy.relative_to(ROOT)}")

    redirects = (ROOT / "_redirects").read_text(encoding="utf-8")
    for cfg_prefix in ("", "en", "ja", "ko", "es"):
        prefix = f"/{cfg_prefix}" if cfg_prefix else ""
        for slug in LONG_TAIL_COMPATIBILITY_PAGES:
            rule = f"{prefix}/tools/{slug}/ /404.html 404"
            if rule not in redirects:
                issues.append(f"explicit legacy 404 rule missing: {rule}")
    for prefix in ("en", "ja", "ko", "es"):
        if f"/{prefix}/ / 302" not in redirects or f"/{prefix}/* /:splat 302" not in redirects:
            issues.append(f"302 language redirect missing: {prefix}")
    if "/tools/love-compatibility/ /compass/ 301" not in redirects:
        issues.append("compatibility consolidation redirect missing")

    print(f"adsense_review_surface_pages={len(routes)}")
    print(f"adsense_review_surface_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
