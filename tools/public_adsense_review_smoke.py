#!/usr/bin/env python3
"""Read back the production AdSense review surface and fail closed on drift."""

from __future__ import annotations

import html
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from xml.etree import ElementTree as ET

from adsense_review_surface_audit import (
    COMMERCE_HOSTS,
    CORE_EDITORIAL_TRUST,
    FORBIDDEN_COMMERCIAL,
    FORBIDDEN_REVIEW_POSITIONING,
    FORBIDDEN_VISIBLE,
    schema_types,
    schemas,
)
from generate_multilingual_site import (
    CSS_ASSET,
    COMPASS_UPDATED,
    COMPASS_TOOL_ASSET,
    HOME_UPDATED,
    INTERACTIONS_ASSET,
    LEGACY_ZH_GUIDES,
    LONG_TAIL_COMPATIBILITY_PAGES,
    MACHINE_READABLE_UPDATED,
    QUIZ_DATA_ASSETS,
    RETIRED_PUBLIC_ASSET_PATHS,
)


BASE_URL = os.environ.get("LOVETYPES_PUBLIC_BASE_URL", "https://lovetypes.tw").rstrip("/")
CANONICAL_BASE = "https://lovetypes.tw"
EXPECTED_ADS_TXT = "google.com, pub-4093856660317740, DIRECT, f08c47fec0942fa0"
TIMEOUT = 20
ADS_TXT_USER_AGENTS = (
    "LoveTypes-public-review-smoke/1.0",
    "Google-adstxt/1.0",
    "AdsBot-Google (+http://www.google.com/adsbot.html)",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
)
CRAWLER_USER_AGENTS = (
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "AdsBot-Google (+http://www.google.com/adsbot.html)",
)


@dataclass
class Response:
    status: int
    url: str
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def header(self, name: str) -> str:
        expected = name.lower()
        return next((value for key, value in self.headers.items() if key.lower() == expected), "")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def request(path: str, *, follow: bool = True, user_agent: str = "LoveTypes-public-review-smoke/1.0") -> Response:
    url = urljoin(BASE_URL, path)
    opener = build_opener() if follow else build_opener(NoRedirect)
    req = Request(url, headers={"User-Agent": user_agent})
    try:
        with opener.open(req, timeout=TIMEOUT) as result:
            return Response(result.status, result.url, dict(result.headers.items()), result.read())
    except HTTPError as exc:
        return Response(exc.code, exc.url, dict(exc.headers.items()), exc.read())
    except URLError as exc:
        return Response(0, url, {}, str(exc).encode())


def visible_text(raw: str) -> str:
    raw = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def attr(raw: str, tag: str, name: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*\b{name}=[\"']([^\"']+)", raw, re.I)
    return html.unescape(match.group(1)) if match else ""


def page_signature(response: Response) -> dict[str, object]:
    raw = response.text
    canonical = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', raw, re.I)
    robots = re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)', raw, re.I)
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", raw, re.I | re.S)
    main = re.search(r"<main\b[^>]*>(.*?)</main>", raw, re.I | re.S)
    return {
        "status": response.status,
        "path": urlparse(response.url).path,
        "canonical": html.unescape(canonical.group(1)) if canonical else "",
        "robots": robots.group(1).strip().lower() if robots else "",
        "h1": visible_text(h1.group(1)) if h1 else "",
        "main": visible_text(main.group(1)) if main else "",
    }


def crawler_parity_issues(route: str, baseline: Response, crawler: Response, label: str) -> list[str]:
    expected = page_signature(baseline)
    actual = page_signature(crawler)
    issues: list[str] = []
    for field in ("status", "path", "canonical", "robots", "h1", "main"):
        if actual[field] != expected[field]:
            if field == "main":
                issues.append(
                    f"{route} [{label}]: main content differs "
                    f"(browser={len(str(expected[field]))} chars, crawler={len(str(actual[field]))} chars)"
                )
            else:
                issues.append(f"{route} [{label}]: {field} differs from browser response")
    return issues


def page_issues(route: str, response: Response) -> list[str]:
    issues: list[str] = []
    raw = response.text
    text = visible_text(raw)
    if response.status != 200:
        return [f"{route}: expected 200, got {response.status}"]
    if attr(raw, "html", "lang") != "zh-TW":
        issues.append(f"{route}: html lang must be zh-TW")
    canonical = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', raw, re.I)
    expected_canonical = CANONICAL_BASE + route
    if not canonical or html.unescape(canonical.group(1)) != expected_canonical:
        issues.append(f"{route}: canonical must be {expected_canonical}")
    robots = re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)', raw, re.I)
    if not robots or "index" not in robots.group(1).lower() or "noindex" in robots.group(1).lower():
        issues.append(f"{route}: expected indexable robots meta")
    if 'hreflang="zh-TW"' not in raw or 'hreflang="x-default"' not in raw:
        issues.append(f"{route}: missing zh-TW/x-default alternates")
    if "pagead2.googlesyndication.com" in raw or "adsbygoogle" in raw:
        issues.append(f"{route}: full AdSense runtime loaded before approval")
    for phrase in FORBIDDEN_VISIBLE:
        if phrase in text:
            issues.append(f"{route}: forbidden public phrase {phrase!r}")
    for phrase in FORBIDDEN_REVIEW_POSITIONING:
        if phrase in raw:
            issues.append(f"{route}: non-relationship positioning {phrase!r} leaked into indexed page")
    for host in COMMERCE_HOSTS:
        if host in raw.lower():
            issues.append(f"{route}: commerce host leaked outside /resources/: {host}")
    main_match = re.search(r"<main\b[^>]*>(.*?)</main>", raw, re.I | re.S)
    main_raw = main_match.group(1) if main_match else ""
    main_visible = visible_text(main_raw)
    if re.search(r'href="/resources/(?:#[^"]*)?"', main_raw):
        issues.append(f"{route}: retired resources link exposed")
    if re.search(r'href="/(?:luna-yoga-music|keepsakes)/(?:#[^"]*)?"', main_raw):
        issues.append(f"{route}: noindex commercial route linked from indexed main")
    if route != "/contact/" and "mailto:" in main_raw:
        issues.append(f"{route}: mailto leaked into indexed main")
    for phrase in FORBIDDEN_COMMERCIAL:
        if phrase in main_visible:
            issues.append(f"{route}: commercial phrase {phrase!r} leaked into indexed main")
    if "data-footer-safety-support" not in raw or 'href="/contact/#urgent-safety-support"' not in raw:
        issues.append(f"{route}: footer safety support route missing")
    if route == "/" and 'href="/contact/#urgent-safety-support"' not in main_raw:
        issues.append(f"{route}: homepage urgent safety route missing")
    if route == "/contact/":
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
            if marker not in raw:
                issues.append(f"{route}: urgent safety support missing {marker}")
    if route == "/compass/":
        for marker in ("data-compass-editorial-byline", "編輯方法", "工具實測", "內容修正", "羅盤只整理輸入，不替關係評分"):
            if marker not in raw:
                issues.append(f"{route}: missing {marker}")
        if f'"dateModified":"{COMPASS_UPDATED}"' not in raw:
            issues.append(f"{route}: schema dateModified mismatch")
    if route == "/":
        primary = [item for item in schemas(raw) if "WebSite" in schema_types(item)]
        if len(primary) != 1 or primary[0].get("dateModified") != HOME_UPDATED:
            issues.append(f"{route}: WebSite schema dateModified mismatch")
    if route in CORE_EDITORIAL_TRUST:
        updated, marker, expected_type = CORE_EDITORIAL_TRUST[route]
        if marker not in raw:
            issues.append(f"{route}: missing visible editorial identity marker {marker}")
        if f'datetime="{updated}"' not in raw or f"內容更新：{updated}" not in raw:
            issues.append(f"{route}: visible update date mismatch")
        if re.search(r'datetime="\{[^"}]+\}"', raw):
            issues.append(f"{route}: unexpanded datetime template")
        primary = [item for item in schemas(raw) if expected_type in schema_types(item)]
        if len(primary) != 1:
            issues.append(f"{route}: {expected_type} schema missing or duplicated")
        else:
            item = primary[0]
            if item.get("dateModified") != updated:
                issues.append(f"{route}: schema dateModified mismatch")
            for field in ("author", "publisher"):
                if item.get(field, {}).get("@type") != "Organization":
                    issues.append(f"{route}: schema {field} must be Organization")
            if route in {"/about/", "/contact/"} and item.get("mainEntity", {}).get("@type") != "Organization":
                issues.append(f"{route}: schema mainEntity must be Organization")
    if route == "/terms/":
        updated = CORE_EDITORIAL_TRUST[route][0]
        if f"更新日期 {updated}" not in raw or f"更新日期:</strong> {updated}" not in raw:
            issues.append(f"{route}: visible and metadata update dates must agree")
    if 'type="application/ld+json"' not in raw:
        issues.append(f"{route}: JSON-LD missing")
    return issues


def main() -> int:
    issues: list[str] = []
    sitemap = request("/sitemap.xml")
    if sitemap.status != 200:
        print(f"public_review_issues=1\n/sitemap.xml: expected 200, got {sitemap.status}")
        return 1
    try:
        root = ET.fromstring(sitemap.body)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text or "" for node in root.findall("s:url/s:loc", ns)]
        sitemap_lastmods = {
            node.findtext("s:loc", default="", namespaces=ns): node.findtext("s:lastmod", default="", namespaces=ns)
            for node in root.findall("s:url", ns)
        }
    except ET.ParseError as exc:
        print(f"public_review_issues=1\n/sitemap.xml: invalid XML: {exc}")
        return 1
    routes = [urlparse(url).path for url in urls]
    if len(urls) != 30 or len(set(urls)) != 30:
        issues.append(f"/sitemap.xml: expected 30 unique URLs, got {len(urls)}")
    if any(not url.startswith(CANONICAL_BASE + "/") for url in urls):
        issues.append("/sitemap.xml: contains a non-production or non-zh URL")
    if sitemap_lastmods.get(CANONICAL_BASE + "/") != HOME_UPDATED:
        issues.append("/sitemap.xml: homepage lastmod mismatch")

    browser_responses: dict[str, Response] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(request, route): route for route in routes}
        for future in as_completed(futures):
            route = futures[future]
            response = future.result()
            browser_responses[route] = response
            issues.extend(page_issues(route, response))

    crawler_checks = 0
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {
            pool.submit(request, route, user_agent=user_agent): (route, user_agent)
            for route in routes
            for user_agent in CRAWLER_USER_AGENTS
        }
        for future in as_completed(futures):
            route, user_agent = futures[future]
            crawler_checks += 1
            issues.extend(crawler_parity_issues(route, browser_responses[route], future.result(), user_agent))

    site_index = request("/site-index.json")
    try:
        index = json.loads(site_index.text)
        if site_index.status != 200 or index.get("totals", {}).get("pages") != 30:
            issues.append("/site-index.json: expected 30 pages")
        if {page.get("lang") for page in index.get("pages", [])} != {"zh"}:
            issues.append("/site-index.json: expected zh-only pages")
        if index.get("updated") != MACHINE_READABLE_UPDATED or index.get("totals", {}).get("languages") != 1:
            issues.append("/site-index.json: stale date or published language drift")
        if "review surface" in str(index.get("description", "")).lower():
            issues.append("/site-index.json: internal review terminology leaked publicly")
    except json.JSONDecodeError:
        issues.append("/site-index.json: invalid JSON")

    llms = request("/llms.txt")
    if llms.status != 200 or f"更新日期：{MACHINE_READABLE_UPDATED}" not in llms.text:
        issues.append("/llms.txt: stale or unavailable")
    if "/funnel-events.json" in llms.text:
        issues.append("/llms.txt: local funnel catalog advertised publicly")
    for marker in ("/contact/#urgent-safety-support", "110", "113", "1925"):
        if marker not in llms.text:
            issues.append(f"/llms.txt: missing safety marker {marker}")

    humans = request("/humans.txt")
    if humans.status != 200 or f"Updated: {MACHINE_READABLE_UPDATED}" not in humans.text:
        issues.append("/humans.txt: stale or unavailable")

    guardian_response = request("/guardian-profiles.json")
    try:
        guardian_index = json.loads(guardian_response.text)
        if guardian_response.status != 200:
            issues.append("/guardian-profiles.json: expected 200")
        if guardian_index.get("updated") != MACHINE_READABLE_UPDATED:
            issues.append("/guardian-profiles.json: stale date")
        if guardian_index.get("publishedLanguage") != "zh-TW" or guardian_index.get("totals", {}).get("languages") != 1:
            issues.append("/guardian-profiles.json: must be zh-TW only")
        if any("en" in item.get("name", {}) for item in guardian_index.get("guardians", [])):
            issues.append("/guardian-profiles.json: unpublished English copy leaked")
    except json.JSONDecodeError:
        issues.append("/guardian-profiles.json: invalid JSON")

    safety_response = request("/safety-index.json")
    try:
        safety_index = json.loads(safety_response.text)
        if safety_response.status != 200:
            issues.append("/safety-index.json: expected 200")
        if safety_index.get("updated") != MACHINE_READABLE_UPDATED:
            issues.append("/safety-index.json: stale date")
        if safety_index.get("publishedLanguage") != "zh-TW" or safety_index.get("totals", {}).get("languages") != 1:
            issues.append("/safety-index.json: must be zh-TW only")
        support = safety_index.get("officialSupport", [])
        if {item.get("id") for item in support if isinstance(item, dict)} != {"110", "113", "1925"}:
            issues.append("/safety-index.json: official support set must be 110, 113, 1925")
        urgent_routes = [
            route
            for boundary in safety_index.get("boundaries", [])
            if isinstance(boundary, dict) and boundary.get("id") == "urgent_risk_first"
            for route in boundary.get("routes", [])
        ]
        if f"{CANONICAL_BASE}/contact/#urgent-safety-support" not in urgent_routes:
            issues.append("/safety-index.json: urgent support anchor mismatch")
    except json.JSONDecodeError:
        issues.append("/safety-index.json: invalid JSON")

    for route in ("/resources/", "/luna-yoga-music/", "/keepsakes/", "/luna/", "/go/luna-starter-click/"):
        response = request(route)
        if route in {"/resources/", "/luna-yoga-music/", "/keepsakes/"}:
            if response.status != 200:
                issues.append(f"{route}: restored public route expected 200, got {response.status}")
            if "noindex" not in str(page_signature(response)["robots"]):
                issues.append(f"{route}: restored public route must remain noindex")
        elif response.status != 410 or "noindex" not in response.header("X-Robots-Tag").lower():
            issues.append(f"{route}: expected 410 with X-Robots-Tag noindex")

    for prefix in ("en", "ja", "ko", "es"):
        response = request(f"/{prefix}/", follow=False)
        if response.status != 302 or response.header("Location") not in ("/", CANONICAL_BASE + "/"):
            issues.append(f"/{prefix}/: expected 302 to /")

    compatibility = request("/tools/love-compatibility/", follow=False)
    expected_locations = {"/compass/", CANONICAL_BASE + "/compass/", BASE_URL + "/compass/"}
    if compatibility.status != 301 or compatibility.header("Location") not in expected_locations:
        issues.append(f"/tools/love-compatibility/: expected 301 to /compass/, got {compatibility.status}")

    retired_routes = [f"/tools/{slug}/" for slug in LONG_TAIL_COMPATIBILITY_PAGES]
    retired_routes += [f"/guides/{slug}/" for slug, _title, _desc, _target in LEGACY_ZH_GUIDES]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(request, route, follow=False): route for route in retired_routes}
        for future in as_completed(futures):
            route = futures[future]
            status = future.result().status
            if status not in {404, 410}:
                issues.append(f"{route}: expected 404/410, got {status}")

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(request, path, follow=False): path for path in RETIRED_PUBLIC_ASSET_PATHS}
        for future in as_completed(futures):
            path = futures[future]
            response = future.result()
            if path in {
                "/ai-discovery.json",
                "/commerce-catalog.json",
                "/promotion-kit.json",
                "/release.json",
                "/search-indexing.json",
                "/site-health.json",
            }:
                if response.status != 200:
                    issues.append(f"{path}: restored public asset expected 200, got {response.status}")
            elif response.status != 410 or "noindex" not in response.header("X-Robots-Tag").lower():
                issues.append(f"{path}: expected 410 with X-Robots-Tag noindex, got {response.status}")

    for path in (CSS_ASSET, INTERACTIONS_ASSET, QUIZ_DATA_ASSETS["zh"], COMPASS_TOOL_ASSET):
        response = request(path)
        if response.status != 200:
            issues.append(f"{path}: current product asset expected 200, got {response.status}")
        if any(term in path for term in ("review-surface", "compass-tool-review", "funnel-kpi", "quiz-metrics")):
            issues.append(f"{path}: current product asset exposes internal review naming")

    for user_agent in ADS_TXT_USER_AGENTS:
        ads = request("/ads.txt", user_agent=user_agent)
        label = f"/ads.txt [{user_agent}]"
        if ads.status != 200 or ads.text.strip() != EXPECTED_ADS_TXT:
            issues.append(f"{label}: missing or incorrect publisher record")
        normalized_headers = {key.lower(): value for key, value in ads.headers.items()}
        if not normalized_headers.get("content-type", "").lower().startswith("text/plain"):
            issues.append(f"{label}: expected text/plain Content-Type")
        if normalized_headers.get("cache-control", "").lower() != "public, max-age=0, must-revalidate":
            issues.append(f"{label}: expected must-revalidate Cache-Control")
        robots_header = normalized_headers.get("x-robots-tag", "").lower()
        if "noindex" not in robots_header or "follow" not in robots_header:
            issues.append(f"{label}: expected X-Robots-Tag noindex, follow")

    print(f"public_review_pages_checked={len(routes)}")
    print(f"public_review_crawler_agents_checked={len(CRAWLER_USER_AGENTS)}")
    print(f"public_review_crawler_parity_checks={crawler_checks}")
    print(f"public_review_retired_routes_checked={len(retired_routes)}")
    print(f"public_review_retired_assets_checked={len(RETIRED_PUBLIC_ASSET_PATHS)}")
    print(f"public_review_ads_txt_user_agents_checked={len(ADS_TXT_USER_AGENTS)}")
    print(f"public_review_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
