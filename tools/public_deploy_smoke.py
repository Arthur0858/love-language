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
]
EXPECTED_TEXT = {
    "/": "LoveTypes 情感守護者宇宙",
    "/characters/": "五位情感守護者總覽",
    "/resources/": "旅人補給",
    "/repair-plan/": "7 日心語修復計畫",
    "/luna-yoga-music/": "Luna Yoga Music",
    "/contact/": "contact@lovetypes.tw",
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "link" and data.get("rel") == "stylesheet" and data.get("href"):
            self.stylesheets.append(data["href"])
        if tag == "link" and data.get("rel") == "canonical" and data.get("href"):
            self.canonical = data["href"]
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
    for expected in ("https://lovetypes.tw/", "https://lovetypes.tw/resources/", "https://lovetypes.tw/characters/iris/"):
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
    first_page_assets: HeadAssetParser | None = None

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
        if not assets.canonical.startswith("https://lovetypes.tw/"):
            issues.append(f"{path}: canonical should use https://lovetypes.tw, got {assets.canonical!r}")
        if path == "/":
            first_page_assets = assets

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

    if first_page_assets is None:
        issues.append("/: could not inspect head assets")
    else:
        for asset in unique_assets([*first_page_assets.stylesheets, *first_page_assets.scripts]):
            if not re.search(r"/(?:shared|site-interactions|deferred-external)-", asset):
                continue
            response = request_url(urljoin(base_url, asset))
            immutable_assets_checked += 1
            cache_control = response.headers.get("cache-control", "")
            if response.status != 200:
                issues.append(f"{asset}: expected status 200, got {response.status}")
            if not IMMUTABLE_CACHE_RE.search(cache_control):
                issues.append(f"{asset}: expected immutable cache header, got {cache_control!r}")

    print(f"public_pages_checked={pages_checked}")
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
