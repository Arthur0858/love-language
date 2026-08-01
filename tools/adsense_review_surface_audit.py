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
from generate_multilingual_site import (
    GUARDIAN_UPDATED,
    COMPASS_UPDATED,
    CORE_EDITORIAL_UPDATED,
    DOMAIN,
    GARDEN_MAP_UPDATED,
    HOME_UPDATED,
    LAB_INDEX_UPDATED,
    LEGACY_ZH_GUIDES,
    LONG_TAIL_COMPATIBILITY_PAGES,
    MACHINE_READABLE_UPDATED,
    RETIRED_PUBLIC_ASSET_PATHS,
    REPAIR_PLAN_UPDATED,
    START_UPDATED,
    THEORY_UPDATED,
    UPDATED,
    PRIVACY_UPDATED,
)
from lab_reports import LAB_REPORTS
import deploy_cloudflare_pages as deploy


ROOT = Path(__file__).resolve().parents[1]
COMMERCE_HOSTS = ("amazon.", "books.com.tw", "gumroad.com")
PRIMARY_SCHEMA_TYPES = {"AboutPage", "Article", "CollectionPage", "ContactPage", "HowTo", "WebPage", "WebSite"}
FORBIDDEN_VISIBLE = ("低價值", "高意圖", "SEO", "搜尋入口", "審核流程", "審核版", "審核面", "AdSense", "命運儀式")
FORBIDDEN_COMMERCIAL = ("US$", "付費報告", "八字", "流年", "Love Timing Report")
FORBIDDEN_REVIEW_POSITIONING = ("命理", "命盤", "出生節奏", "生日節奏", "出生時間", "出生日期")
EXPECTED_CORE = {
    "/", "/start/", "/garden-map/", "/compass/",
    "/guides/", "/characters/", "/theory/", "/repair-plan/",
    "/about/", "/contact/", "/privacy/", "/terms/", "/lab/",
}
CORE_EDITORIAL_TRUST = {
    "/start/": (START_UPDATED, "data-start-editorial-byline", "WebPage"),
    "/garden-map/": (GARDEN_MAP_UPDATED, "data-garden-map-editorial-byline", "CollectionPage"),
    "/compass/": (COMPASS_UPDATED, "data-compass-editorial-byline", "WebApplication"),
    "/guides/": (CORE_EDITORIAL_UPDATED, "data-guides-editorial-byline", "CollectionPage"),
    "/characters/": (CORE_EDITORIAL_UPDATED, "data-characters-editorial-byline", "CollectionPage"),
    "/theory/": (THEORY_UPDATED, "data-theory-editorial-byline", "WebPage"),
    "/repair-plan/": (REPAIR_PLAN_UPDATED, "data-repair-editorial-byline", "HowTo"),
    "/about/": (CORE_EDITORIAL_UPDATED, "data-about-editorial-byline", "AboutPage"),
    "/contact/": (CORE_EDITORIAL_UPDATED, "data-contact-editorial-byline", "ContactPage"),
    "/privacy/": (PRIVACY_UPDATED, "data-privacy-editorial-byline", "WebPage"),
    "/terms/": (CORE_EDITORIAL_UPDATED, "data-terms-editorial-byline", "WebPage"),
    "/lab/": (LAB_INDEX_UPDATED, "data-lab-editorial-byline", "CollectionPage"),
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


def main_text_markup(raw: str) -> str:
    match = re.search(r"<main\b[^>]*>(.*?)</main>", raw, re.I | re.S)
    return match.group(1) if match else ""


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
    if index.get("updated") != MACHINE_READABLE_UPDATED:
        issues.append("site-index machine-readable update date mismatch")
    if index.get("totals", {}).get("languages") != 1:
        issues.append("site-index must declare one published language")
    if "review surface" in str(index.get("description", "")).lower():
        issues.append("site-index exposes internal review terminology")

    expected_public_support = {
        "robots.txt", "sitemap.xml", "feed.xml", "site.webmanifest", "llms.txt",
        "humans.txt", "security.txt", "ads.txt", "site-index.json",
        "guardian-profiles.json", "safety-index.json",
    }
    if deploy.PUBLIC_SUPPORT_FILES != expected_public_support:
        issues.append(
            "public support allowlist drift: "
            f"missing={sorted(expected_public_support-deploy.PUBLIC_SUPPORT_FILES)} "
            f"extra={sorted(deploy.PUBLIC_SUPPORT_FILES-expected_public_support)}"
        )
    if "funnel-events.json" in deploy.PUBLIC_SUPPORT_FILES:
        issues.append("funnel-events.json must remain local and must not be publicly deployed")
    if "/funnel-events.json" not in RETIRED_PUBLIC_ASSET_PATHS:
        issues.append("funnel-events.json must be covered by the public 410 retirement worker")

    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    humans_text = (ROOT / "humans.txt").read_text(encoding="utf-8")
    if f"更新日期：{MACHINE_READABLE_UPDATED}" not in llms_text:
        issues.append("llms.txt machine-readable update date mismatch")
    if "/funnel-events.json" in llms_text:
        issues.append("llms.txt must not advertise the local funnel catalog")
    for marker in ("/contact/#urgent-safety-support", "110", "113", "1925"):
        if marker not in llms_text:
            issues.append(f"llms.txt missing public safety marker {marker}")
    if f"Updated: {MACHINE_READABLE_UPDATED}" not in humans_text:
        issues.append("humans.txt machine-readable update date mismatch")

    guardian_index = json.loads((ROOT / "guardian-profiles.json").read_text(encoding="utf-8"))
    if guardian_index.get("updated") != MACHINE_READABLE_UPDATED:
        issues.append("guardian-profiles update date mismatch")
    if guardian_index.get("publishedLanguage") != "zh-TW" or guardian_index.get("totals", {}).get("languages") != 1:
        issues.append("guardian-profiles must declare zh-TW as its only published language")
    if any("en" in item.get("name", {}) or "en" in item.get("loveLanguage", {}) for item in guardian_index.get("guardians", [])):
        issues.append("guardian-profiles contains unpublished English profile copy")

    safety_index = json.loads((ROOT / "safety-index.json").read_text(encoding="utf-8"))
    if safety_index.get("updated") != MACHINE_READABLE_UPDATED:
        issues.append("safety-index update date mismatch")
    if safety_index.get("publishedLanguage") != "zh-TW" or safety_index.get("totals", {}).get("languages") != 1:
        issues.append("safety-index must declare zh-TW as its only published language")
    official_support = safety_index.get("officialSupport", [])
    if {item.get("id") for item in official_support if isinstance(item, dict)} != {"110", "113", "1925"}:
        issues.append("safety-index officialSupport must contain exactly 110, 113, and 1925")
    for item in official_support:
        if not item.get("telephone", "").startswith("tel:") or not item.get("source", "").startswith("https://"):
            issues.append(f"safety-index official support entry is incomplete: {item.get('id')}")
    if not any(
        f"{DOMAIN}/contact/#urgent-safety-support" in boundary.get("routes", [])
        for boundary in safety_index.get("boundaries", [])
        if isinstance(boundary, dict) and boundary.get("id") == "urgent_risk_first"
    ):
        issues.append("safety-index urgent risk route must point to the public safety support anchor")
    if any("en" in boundary.get("title", {}) or "en" in boundary.get("body", {}) for boundary in safety_index.get("boundaries", [])):
        issues.append("safety-index contains unpublished English safety copy")

    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", ns)}
    sitemap_lastmods = {
        node.findtext("s:loc", default="", namespaces=ns): node.findtext("s:lastmod", default="", namespaces=ns)
        for node in sitemap_root.findall("s:url", ns)
    }
    expected_urls = {"https://lovetypes.tw" + route for route in expected}
    if sitemap_urls != expected_urls:
        issues.append(f"sitemap must match the 38-page review surface, found {len(sitemap_urls)} URLs")
    if sitemap_lastmods.get("https://lovetypes.tw/") != HOME_UPDATED:
        issues.append("homepage sitemap lastmod mismatch")
    for slug in ("iris", "noah", "vivian", "claire", "dora"):
        url = f"https://lovetypes.tw/characters/{slug}/"
        if sitemap_lastmods.get(url) != GUARDIAN_UPDATED:
            issues.append(f"guardian sitemap lastmod mismatch: {slug}")
    for route, (updated, _marker, _schema_type) in CORE_EDITORIAL_TRUST.items():
        url = f"https://lovetypes.tw{route}"
        if sitemap_lastmods.get(url) != updated:
            issues.append(f"{route} sitemap lastmod mismatch")

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
        if route == "/":
            website_schemas = [item for item in primary_schemas if "WebSite" in schema_types(item)]
            if len(website_schemas) != 1 or website_schemas[0].get("dateModified") != HOME_UPDATED:
                issues.append("homepage WebSite schema dateModified mismatch")
        if "data-footer-safety-support" not in raw or 'href="/contact/#urgent-safety-support"' not in raw:
            issues.append(f"footer safety support route missing: {route}")

    home_raw = page_file("/").read_text(encoding="utf-8")
    if 'href="/contact/#urgent-safety-support"' not in main_text_markup(home_raw):
        issues.append("homepage urgent safety route missing")

    contact_raw = page_file("/contact/").read_text(encoding="utf-8")
    for marker in (
        "data-urgent-safety-support",
        'data-safety-route="110"',
        'data-safety-route="113"',
        'data-safety-route="1925"',
        'href="tel:110"',
        'href="tel:113"',
        'href="tel:1925"',
        "https://www.npa.gov.tw/ch/app/artwebsite/view",
        "https://dep.mohw.gov.tw/DOPs/cp-1183-6499-105.html",
        "https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html",
    ):
        if marker not in contact_raw:
            issues.append(f"contact urgent safety support missing {marker}")

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

    for slug in ("iris", "noah", "vivian", "claire", "dora"):
        route = f"/characters/{slug}/"
        raw = page_file(route).read_text(encoding="utf-8")
        text = main_text(raw)
        cjk = len(re.findall(r"[\u3400-\u9fff]", text))
        if not 2000 <= cjk <= 2600:
            issues.append(f"guardian main CJK count outside 2000-2600: {slug}={cjk}")
        if raw.count("data-guardian-example") != 2:
            issues.append(f"guardian needs exactly two labeled examples: {slug}")
        for marker in (
            "data-guardian-editorial",
            "data-guardian-editorial-byline",
            "data-guardian-workbook",
            "適合使用",
            "不適用與限制",
        ):
            if marker not in raw:
                issues.append(f"guardian missing {marker}: {slug}")
        if f'<time datetime="{GUARDIAN_UPDATED}">' not in raw:
            issues.append(f"guardian update date mismatch: {slug}")
        web_schemas = [item for item in schemas(raw) if item.get("@type") == "WebPage"]
        if len(web_schemas) != 1:
            issues.append(f"guardian WebPage schema missing or duplicated: {slug}")
        else:
            item = web_schemas[0]
            if item.get("dateModified") != GUARDIAN_UPDATED:
                issues.append(f"guardian schema dateModified mismatch: {slug}")
            for field in ("author", "publisher"):
                if item.get(field, {}).get("@type") != "Organization":
                    issues.append(f"guardian schema {field} must be Organization: {slug}")

    start_raw = page_file("/start/").read_text(encoding="utf-8")
    start_cjk = len(re.findall(r"[\u3400-\u9fff]", main_text(start_raw)))
    if not 900 <= start_cjk <= 1300:
        issues.append(f"start main CJK count outside 900-1300: {start_cjk}")
    for marker in ("data-start-method", "data-start-editorial-byline", "編輯方法", "內容修正"):
        if marker not in start_raw:
            issues.append(f"start missing {marker}")
    start_schemas = [item for item in schemas(start_raw) if item.get("@type") == "WebPage"]
    if len(start_schemas) != 1:
        issues.append("start WebPage schema missing or duplicated")
    else:
        item = start_schemas[0]
        if item.get("dateModified") != START_UPDATED:
            issues.append("start schema dateModified mismatch")
        for field in ("author", "publisher"):
            if item.get(field, {}).get("@type") != "Organization":
                issues.append(f"start schema {field} must be Organization")

    repair_raw = page_file("/repair-plan/").read_text(encoding="utf-8")
    repair_cjk = len(re.findall(r"[\u3400-\u9fff]", main_text(repair_raw)))
    if not 2000 <= repair_cjk <= 2800:
        issues.append(f"repair plan main CJK count outside 2000-2800: {repair_cjk}")
    if repair_raw.count("data-repair-example") != 2:
        issues.append("repair plan needs exactly two labeled examples")
    for marker in (
        "data-repair-method",
        "data-repair-editorial-byline",
        "data-repair-decision",
        "data-repair-sources",
        "方法來源與限制",
    ):
        if marker not in repair_raw:
            issues.append(f"repair plan missing {marker}")
    if repair_raw.count('target="_blank" rel="noopener noreferrer"') < 2:
        issues.append("repair plan needs two visible authoritative sources")
    repair_schemas = [item for item in schemas(repair_raw) if item.get("@type") == "HowTo"]
    if len(repair_schemas) != 1:
        issues.append("repair plan HowTo schema missing or duplicated")
    else:
        item = repair_schemas[0]
        if item.get("dateModified") != REPAIR_PLAN_UPDATED:
            issues.append("repair plan schema dateModified mismatch")
        for field in ("author", "publisher"):
            if item.get(field, {}).get("@type") != "Organization":
                issues.append(f"repair plan schema {field} must be Organization")

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
        for phrase in FORBIDDEN_REVIEW_POSITIONING:
            if phrase in raw:
                issues.append(f"non-relationship positioning {phrase!r} leaked into indexed page: {route}")
        for phrase in FORBIDDEN_COMMERCIAL:
            if phrase in text:
                issues.append(f"commercial phrase {phrase!r} leaked into indexed content: {route}")
        for item in schemas(raw):
            if item.get("@type") == "Offer" or "Offer" in item.get("@type", []):
                issues.append(f"Offer schema leaked into indexed page: {route}")
            if route.startswith("/characters/") and item.get("@type") == "ProfilePage":
                issues.append(f"fictional guardian must not use ProfilePage schema: {route}")

    for route, (updated, marker, expected_type) in CORE_EDITORIAL_TRUST.items():
        raw = page_file(route).read_text(encoding="utf-8")
        if marker not in raw:
            issues.append(f"{route} missing visible editorial identity marker {marker}")
        if f'datetime="{updated}"' not in raw or f"內容更新：{updated}" not in raw:
            issues.append(f"{route} visible update date mismatch")
        if re.search(r'datetime="\{[^"}]+\}"', raw):
            issues.append(f"{route} contains an unexpanded datetime template")
        primary = [item for item in schemas(raw) if expected_type in schema_types(item)]
        if len(primary) != 1:
            issues.append(f"{route} {expected_type} schema missing or duplicated")
            continue
        item = primary[0]
        if item.get("dateModified") != updated:
            issues.append(f"{route} schema dateModified mismatch")
        for field in ("author", "publisher"):
            if item.get(field, {}).get("@type") != "Organization":
                issues.append(f"{route} schema {field} must be Organization")
    for route in ("/about/", "/contact/"):
        expected_type = CORE_EDITORIAL_TRUST[route][2]
        item = next(item for item in schemas(page_file(route).read_text(encoding="utf-8")) if expected_type in schema_types(item))
        if item.get("mainEntity", {}).get("@type") != "Organization":
            issues.append(f"{route} schema mainEntity must be Organization")
    terms_raw = page_file("/terms/").read_text(encoding="utf-8")
    if f"更新日期 {CORE_EDITORIAL_UPDATED}" not in terms_raw or f"更新日期:</strong> {CORE_EDITORIAL_UPDATED}" not in terms_raw:
        issues.append("/terms/ visible and metadata update dates must agree")
    if UPDATED != CORE_EDITORIAL_UPDATED and UPDATED in terms_raw:
        issues.append("/terms/ contains stale previous update date")

    compass_raw = page_file("/compass/").read_text(encoding="utf-8")
    compass_cjk = len(re.findall(r"[\u3400-\u9fff]", main_text(compass_raw)))
    if not 2800 <= compass_cjk <= 3600:
        issues.append(f"compass main CJK count outside 2800-3600: {compass_cjk}")
    for marker in ("data-compass-editorial-byline", "編輯方法", "工具實測", "內容修正", "羅盤只整理輸入，不替關係評分"):
        if marker not in compass_raw:
            issues.append(f"compass missing {marker}")
    compass_schemas = [item for item in schemas(compass_raw) if "WebApplication" in schema_types(item)]
    if len(compass_schemas) != 1:
        issues.append("compass WebApplication schema missing or duplicated")
    else:
        item = compass_schemas[0]
        if item.get("dateModified") != COMPASS_UPDATED:
            issues.append("compass schema dateModified mismatch")
        for field in ("author", "publisher"):
            if item.get(field, {}).get("@type") != "Organization":
                issues.append(f"compass schema {field} must be Organization")

    garden_raw = page_file("/garden-map/").read_text(encoding="utf-8")
    guide_index_raw = page_file("/guides/").read_text(encoding="utf-8")
    garden_cjk = len(re.findall(r"[\u3400-\u9fff]", main_text(garden_raw)))
    if not 1100 <= garden_cjk <= 1700:
        issues.append(f"garden-map main CJK count outside 1100-1700: {garden_cjk}")
    if garden_raw.count("garden-map-decision-card") != 5:
        issues.append("garden-map needs exactly five state decision cards")
    if garden_raw.count('class="garden-map-tool-card"') != 2:
        issues.append("garden-map needs exactly two review-safe interactive tools")
    for marker in ("data-garden-map-editorial-byline", "data-garden-map-decisions", "編輯方法", "內容修正", "兩個互動工具"):
        if marker not in garden_raw:
            issues.append(f"garden-map missing {marker}")
    if "data-garden-map-guides" in garden_raw:
        issues.append("garden-map must not duplicate the full guide index")
    garden_schemas = [item for item in schemas(garden_raw) if item.get("@type") == "CollectionPage"]
    if len(garden_schemas) != 1:
        issues.append("garden-map CollectionPage schema missing or duplicated")
    else:
        item = garden_schemas[0]
        if item.get("dateModified") != GARDEN_MAP_UPDATED:
            issues.append("garden-map schema dateModified mismatch")
        for field in ("author", "publisher"):
            if item.get(field, {}).get("@type") != "Organization":
                issues.append(f"garden-map schema {field} must be Organization")

    def cjk_trigrams(raw: str) -> set[str]:
        text = "".join(re.findall(r"[\u3400-\u9fff]", main_text(raw)))
        return {text[index:index + 3] for index in range(max(0, len(text) - 2))}

    garden_grams = cjk_trigrams(garden_raw)
    guide_grams = cjk_trigrams(guide_index_raw)
    shared = garden_grams & guide_grams
    garden_guide_jaccard = len(shared) / len(garden_grams | guide_grams)
    garden_guide_containment = max(len(shared) / len(garden_grams), len(shared) / len(guide_grams))
    if garden_guide_jaccard > 0.25 or garden_guide_containment > 0.45:
        issues.append(
            f"garden-map/guide-index overlap too high: jaccard={garden_guide_jaccard:.3f} "
            f"containment={garden_guide_containment:.3f}"
        )

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
    print(f"core_editorial_trust_pages={len(CORE_EDITORIAL_TRUST)}")
    print(f"garden_map_main_cjk={garden_cjk}")
    print(f"garden_map_guide_jaccard={garden_guide_jaccard:.3f}")
    print(f"garden_map_guide_containment={garden_guide_containment:.3f}")
    print(f"adsense_review_surface_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
