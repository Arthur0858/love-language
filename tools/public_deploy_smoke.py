#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import ssl
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
PUBLIC_PATHS = [
    "/",
    "/characters/",
    "/characters/iris/",
    "/resources/",
    "/repair-plan/",
    "/keepsakes/",
    "/luna-yoga-music/",
    "/guides/",
    "/about/",
    "/theory/",
    "/contact/",
    "/en/",
    "/ja/",
    "/ko/",
    "/es/",
    "/en/characters/",
    "/ja/resources/",
    "/ko/repair-plan/",
    "/es/guides/",
]
EXPECTED_TEXT = {
    "/": "LoveTypes 情感守護者宇宙",
    "/characters/": "五位情感守護者總覽",
    "/resources/": "旅人補給",
    "/repair-plan/": "7 日心語修復計畫",
    "/luna-yoga-music/": "Luna Yoga Music",
    "/contact/": "contact@lovetypes.tw",
    "/en/": "LoveTypes Emotion Guardians",
    "/ja/": "LoveTypes 感情の守護者",
    "/ko/": "LoveTypes 감정 수호자",
    "/es/": "LoveTypes Guardianas Emocionales",
    "/en/characters/": "Five Emotion Guardians Overview",
    "/ja/resources/": "リソース",
    "/ko/repair-plan/": "7일 마음 언어 회복 계획",
    "/es/guides/": "Guías de Guardianas LoveTypes",
}
REDIRECTS = {
    "/luna/": "/luna-yoga-music/",
    "/en/luna/": "/en/luna-yoga-music/",
    "/ja/luna/": "/ja/luna-yoga-music/",
    "/ko/luna/": "/ko/luna-yoga-music/",
    "/es/luna/": "/es/luna-yoga-music/",
}
SUPPORT_FILES = {
    "/robots.txt": ["User-agent: *", "Allow: /", "Sitemap: https://lovetypes.tw/sitemap.xml"],
    "/ads.txt": ["google.com", "DIRECT", "f08c47fec0942fa0"],
    "/security.txt": ["Contact: mailto:contact@lovetypes.tw", "Policy: https://lovetypes.tw/privacy/"],
    "/.well-known/security.txt": ["Contact: mailto:contact@lovetypes.tw", "Policy: https://lovetypes.tw/privacy/"],
    "/llms.txt": [
        "# LoveTypes - Heart Garden Emotion Guardians",
        "Production: https://lovetypes.tw/",
        "## Five Guardians",
        "## Guide Index",
        "## Commercial and Safety Boundaries",
        "https://lovetypes.tw/resources/",
        "https://lovetypes.tw/luna-yoga-music/",
        "Contact email: contact@lovetypes.tw",
    ],
}
NOT_FOUND_PATH = "/__lovetypes_missing_smoke__/"
NOT_FOUND_REQUIRED_TEXT = [
    "404 HEART GARDEN",
    "這盞燈暫時不在地圖上",
    "/#quiz-section",
    "/characters/",
    "/resources/",
    "/contact/",
]
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
REQUIRED_GLOBAL_HEADERS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "SAMEORIGIN",
}
IMMUTABLE_CACHE_RE = re.compile(r"max-age=31536000.*immutable", re.I)
VERSIONED_CSS_RE = re.compile(r"^/shared-[^/]+\.css$")
VERSIONED_INTERACTIONS_RE = re.compile(r"^/site-interactions-[^/]+\.js$")
VERSIONED_AFFILIATE_RE = re.compile(r"^/deferred-external-[^/]+\.js$")


@dataclass
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class HeadAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stylesheets: list[str] = []
        self.scripts: list[str] = []
        self.canonical = ""
        self.html_lang = ""
        self.robots = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "")
        if tag == "link" and data.get("rel") == "stylesheet" and data.get("href"):
            self.stylesheets.append(data["href"])
        if tag == "link" and data.get("rel") == "canonical" and data.get("href"):
            self.canonical = data["href"]
        if tag == "meta" and data.get("name") == "robots":
            self.robots = data.get("content", "")
        if tag == "script" and data.get("src"):
            self.scripts.append(data["src"])


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url_once(url: str, *, follow_redirects: bool = True) -> Response:
    request = Request(url, headers={"User-Agent": "LoveTypes public deploy smoke/1.0"})
    context = ssl.create_default_context()
    try:
        opener = None
        if not follow_redirects:
            from urllib.request import HTTPSHandler, HTTPRedirectHandler, build_opener

            class NoRedirect(HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = build_opener(NoRedirect, HTTPSHandler(context=context))
        if opener:
            raw = opener.open(request, timeout=20)
        else:
            raw = urlopen(request, timeout=20, context=context)
        with raw:
            return Response(raw.geturl(), raw.status, {key.lower(): value for key, value in raw.headers.items()}, raw.read())
    except HTTPError as error:
        return Response(error.geturl(), error.code, {key.lower(): value for key, value in error.headers.items()}, error.read())
    except URLError as error:
        raise RuntimeError(f"failed to request {url}: {error}") from error


def request_url(url: str, *, follow_redirects: bool = True, attempts: int = 3) -> Response:
    last_error: RuntimeError | None = None
    for attempt in range(1, attempts + 1):
        try:
            return request_url_once(url, follow_redirects=follow_redirects)
        except RuntimeError as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.75 * attempt)
    assert last_error is not None
    raise last_error


def path_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path or "/"


def expected_html_lang(path: str) -> str:
    for prefix, lang in (
        ("/en/", "en"),
        ("/ja/", "ja"),
        ("/ko/", "ko"),
        ("/es/", "es"),
    ):
        if path.startswith(prefix):
            return lang
    return "zh-TW"


def expected_canonical(path: str) -> str:
    return urljoin(DEFAULT_BASE_URL, path)


def header_matches(headers: dict[str, str], name: str, expected: str) -> bool:
    return headers.get(name, "") == expected


def check_global_headers(path: str, response: Response) -> list[str]:
    issues: list[str] = []
    for name, expected in REQUIRED_GLOBAL_HEADERS.items():
        if not header_matches(response.headers, name, expected):
            issues.append(f"{path}: header {name} should be {expected!r}, got {response.headers.get(name, '')!r}")
    return issues


def check_text_support_file(path: str, response: Response, required_snippets: list[str]) -> list[str]:
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"]
    if path != "/robots.txt":
        issues.extend(check_global_headers(path, response))
    for snippet in required_snippets:
        if snippet not in response.text:
            issues.append(f"{path}: missing required text {snippet!r}")
    return issues


def check_sitemap(response: Response) -> list[str]:
    path = "/sitemap.xml"
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"]
    issues.extend(check_global_headers(path, response))
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [f"{path}: invalid XML: {error}"]
    urls = root.findall("sm:url", SITEMAP_NS)
    locs = [node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) for node in urls]
    if len(locs) < 140:
        issues.append(f"{path}: expected at least 140 sitemap URLs, found {len(locs)}")
    for expected in (
        "https://lovetypes.tw/",
        "https://lovetypes.tw/en/",
        "https://lovetypes.tw/ja/",
        "https://lovetypes.tw/ko/",
        "https://lovetypes.tw/es/",
        "https://lovetypes.tw/resources/",
        "https://lovetypes.tw/characters/iris/",
    ):
        if expected not in locs:
            issues.append(f"{path}: missing sitemap URL {expected}")
    return issues


def check_feed(response: Response) -> list[str]:
    path = "/feed.xml"
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"]
    issues.extend(check_global_headers(path, response))
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [f"{path}: invalid XML: {error}"]
    if root.tag != "rss" or root.attrib.get("version") != "2.0":
        issues.append(f"{path}: expected RSS 2.0 root")
    items = root.findall("./channel/item")
    if len(items) < 10:
        issues.append(f"{path}: expected at least 10 feed items, found {len(items)}")
    channel_link = root.findtext("./channel/link", default="")
    if channel_link != "https://lovetypes.tw/guides/":
        issues.append(f"{path}: channel link should be https://lovetypes.tw/guides/, got {channel_link!r}")
    return issues


def extract_head_assets(html: str) -> HeadAssetParser:
    parser = HeadAssetParser()
    parser.feed(html)
    return parser


def unique_assets(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke check a deployed LoveTypes public site.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    pages_checked = 0
    redirects_checked = 0
    not_found_checked = 0
    support_files_checked = 0
    immutable_assets_checked = 0
    public_canonicals_checked = 0
    public_robots_checked = 0
    public_lang_checked = 0
    public_versioned_asset_refs_checked = 0
    page_asset_refs: list[str] = []

    for path in PUBLIC_PATHS:
        response = request_url(urljoin(base_url, path))
        pages_checked += 1
        if response.status != 200:
            issues.append(f"{path}: expected status 200, got {response.status}")
            continue
        final_path = path_from_url(response.url)
        if final_path.rstrip("/") != path.rstrip("/"):
            issues.append(f"{path}: expected final path {path}, got {final_path}")
        issues.extend(check_global_headers(path, response))
        expected_text = EXPECTED_TEXT.get(path)
        if expected_text and expected_text not in response.text:
            issues.append(f"{path}: missing expected text {expected_text!r}")
        assets = extract_head_assets(response.text)
        public_canonicals_checked += 1
        expected_canonical_url = expected_canonical(path)
        if assets.canonical != expected_canonical_url:
            issues.append(f"{path}: canonical should be {expected_canonical_url!r}, got {assets.canonical!r}")
        public_robots_checked += 1
        robots_tokens = {token.strip().lower() for token in assets.robots.split(",") if token.strip()}
        if "noindex" in robots_tokens:
            issues.append(f"{path}: public smoke page should not be noindex")
        if "index" not in robots_tokens or "follow" not in robots_tokens:
            issues.append(f"{path}: robots should include index, follow; got {assets.robots!r}")
        public_lang_checked += 1
        expected_lang = expected_html_lang(path)
        if assets.html_lang != expected_lang:
            issues.append(f"{path}: html lang should be {expected_lang!r}, got {assets.html_lang!r}")

        versioned_stylesheets = [href for href in assets.stylesheets if VERSIONED_CSS_RE.match(href)]
        versioned_interactions = [src for src in assets.scripts if VERSIONED_INTERACTIONS_RE.match(src)]
        versioned_affiliate = [src for src in assets.scripts if VERSIONED_AFFILIATE_RE.match(src)]
        public_versioned_asset_refs_checked += len(versioned_stylesheets) + len(versioned_interactions) + len(versioned_affiliate)
        if len(versioned_stylesheets) != 1:
            issues.append(f"{path}: expected one versioned shared CSS asset, found {versioned_stylesheets}")
        if len(versioned_interactions) != 1:
            issues.append(f"{path}: expected one versioned interaction JS asset, found {versioned_interactions}")
        expected_affiliate_count = 1 if path.endswith("/resources/") else 0
        if len(versioned_affiliate) != expected_affiliate_count:
            issues.append(f"{path}: expected {expected_affiliate_count} versioned affiliate JS asset(s), found {versioned_affiliate}")
        page_asset_refs.extend([*versioned_stylesheets, *versioned_interactions, *versioned_affiliate])

    for source, target in REDIRECTS.items():
        response = request_url(urljoin(base_url, source), follow_redirects=False)
        redirects_checked += 1
        location = response.headers.get("location", "")
        expected_location = urljoin(base_url, target)
        if response.status != 301:
            issues.append(f"{source}: expected 301 redirect, got {response.status}")
        if location not in {target, expected_location}:
            issues.append(f"{source}: expected redirect to {target}, got {location!r}")

    not_found_response = request_url(urljoin(base_url, NOT_FOUND_PATH))
    not_found_checked += 1
    if not_found_response.status != 404:
        issues.append(f"{NOT_FOUND_PATH}: expected custom 404 status, got {not_found_response.status}")
    issues.extend(check_global_headers(NOT_FOUND_PATH, not_found_response))
    for snippet in NOT_FOUND_REQUIRED_TEXT:
        if snippet not in not_found_response.text:
            issues.append(f"{NOT_FOUND_PATH}: custom 404 missing required text {snippet!r}")

    for path, snippets in SUPPORT_FILES.items():
        response = request_url(urljoin(base_url, path))
        support_files_checked += 1
        issues.extend(check_text_support_file(path, response, snippets))

    sitemap_response = request_url(urljoin(base_url, "/sitemap.xml"))
    support_files_checked += 1
    issues.extend(check_sitemap(sitemap_response))

    feed_response = request_url(urljoin(base_url, "/feed.xml"))
    support_files_checked += 1
    issues.extend(check_feed(feed_response))

    security_response = request_url(urljoin(base_url, "/security.txt"))
    well_known_security_response = request_url(urljoin(base_url, "/.well-known/security.txt"))
    if security_response.status == 200 and well_known_security_response.status == 200:
        if security_response.text != well_known_security_response.text:
            issues.append("/.well-known/security.txt: body should match /security.txt")

    for asset in unique_assets(page_asset_refs):
        response = request_url(urljoin(base_url, asset))
        immutable_assets_checked += 1
        cache_control = response.headers.get("cache-control", "")
        if response.status != 200:
            issues.append(f"{asset}: expected status 200, got {response.status}")
        if not IMMUTABLE_CACHE_RE.search(cache_control):
            issues.append(f"{asset}: expected immutable cache header, got {cache_control!r}")

    print(f"public_pages_checked={pages_checked}")
    print(f"public_canonicals_checked={public_canonicals_checked}")
    print(f"public_robots_checked={public_robots_checked}")
    print(f"public_lang_checked={public_lang_checked}")
    print(f"public_versioned_asset_refs_checked={public_versioned_asset_refs_checked}")
    print(f"public_redirects_checked={redirects_checked}")
    print(f"public_not_found_checked={not_found_checked}")
    print(f"public_support_files_checked={support_files_checked}")
    print(f"public_immutable_assets_checked={immutable_assets_checked}")
    print(f"public_deploy_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
