#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
MISSING_PATH = "/definitely-missing-lovetypes-page/"


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict[str, str]
    text: str


@dataclass(frozen=True)
class NoindexCase:
    name: str
    path: str
    expected_status: int
    expected_canonical_path: str | None = None
    expected_location_path: str | None = None


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


class IndexabilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.robots = ""
        self.canonical = ""
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and data.get("name", "").lower() == "robots":
            self.robots = data.get("content", "")
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, *, follow_redirects: bool = True, attempts: int = 3) -> Response:
    opener = build_opener() if follow_redirects else build_opener(NoRedirectHandler)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public indexability smoke/1.0"})
            with opener.open(request, timeout=20) as raw:
                headers = {key.lower(): value for key, value in raw.headers.items()}
                body = raw.read().decode("utf-8", errors="replace")
                return Response(raw.geturl(), raw.status, headers, body)
        except HTTPError as error:
            headers = {key.lower(): value for key, value in error.headers.items()}
            body = error.read().decode("utf-8", errors="replace")
            return Response(error.geturl(), error.code, headers, body)
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def public_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path.endswith("/") or "." in path.rsplit("/", 1)[-1]:
        return path
    return f"{path}/"


def parse_head(html: str) -> IndexabilityParser:
    parser = IndexabilityParser()
    parser.feed(html)
    return parser


def robots_tokens(value: str) -> set[str]:
    return {token.strip().lower() for token in value.split(",") if token.strip()}


def sitemap_locations(base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    issues: list[str] = []
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as error:
        return [], [f"/sitemap.xml: invalid XML: {error}"]
    locations = [
        (node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) or "").strip()
        for node in root.findall("sm:url", SITEMAP_NS)
    ]
    locations = [loc for loc in locations if loc]
    if len(locations) != len(set(locations)):
        issues.append("/sitemap.xml: duplicate loc values")
    return locations, issues


def expected_url(base_url: str, path: str) -> str:
    return urljoin(base_url + "/", path.lstrip("/"))


def indexable_page_issues(base_url: str, loc: str) -> tuple[list[str], int]:
    issues: list[str] = []
    response = request_url(loc)
    path = public_path(loc)
    if response.status != 200:
        return [f"{path}: sitemap page expected status 200, got {response.status}"], 0
    parser = parse_head(response.text)
    tokens = robots_tokens(parser.robots)
    if "noindex" in tokens:
        issues.append(f"{path}: sitemap page should not be noindex")
    if {"index", "follow"}.difference(tokens):
        issues.append(f"{path}: sitemap page robots should include index/follow, got {parser.robots!r}")
    if parser.canonical != loc:
        issues.append(f"{path}: canonical should match sitemap loc {loc!r}, got {parser.canonical!r}")
    if response.headers.get("x-robots-tag", "").lower() == "noindex":
        issues.append(f"{path}: sitemap page should not send X-Robots-Tag noindex")
    if urlparse(loc).netloc != urlparse(base_url).netloc:
        issues.append(f"{path}: sitemap loc should stay on canonical host")
    return issues, 1


def noindex_cases(base_url: str) -> list[NoindexCase]:
    generator = load_module("lovetypes_generator_indexability_smoke", ROOT / "tools" / "generate_multilingual_site.py")
    cases: list[NoindexCase] = [
        NoindexCase("missing-404", MISSING_PATH, 404),
    ]
    for lang, cfg in generator.LANGS.items():
        prefix = cfg["prefix"]
        luna_path = f"/{prefix}/luna/" if prefix else "/luna/"
        target_path = f"/{prefix}/luna-yoga-music/" if prefix else "/luna-yoga-music/"
        cases.append(
            NoindexCase(
                name=f"{lang}-luna-alias",
                path=luna_path,
                expected_status=301,
                expected_canonical_path=target_path,
                expected_location_path=target_path,
            )
        )
    for slug, _title, _desc, target in generator.LEGACY_ZH_GUIDES:
        cases.append(
            NoindexCase(
                name=f"legacy-guide-{slug}",
                path=f"/guides/{slug}/",
                expected_status=200,
                expected_canonical_path=f"/guides/{target}/",
            )
        )
    return cases


def noindex_case_issues(base_url: str, sitemap_set: set[str], case: NoindexCase) -> tuple[list[str], int, int, int]:
    issues: list[str] = []
    checked = 0
    redirects_checked = 0
    sitemap_absence_checked = 0
    url = expected_url(base_url, case.path)
    if url in sitemap_set:
        issues.append(f"{case.path}: noindex/alias route should not be listed in sitemap")
    else:
        sitemap_absence_checked += 1

    follow_redirects = case.expected_status not in {301, 302, 307, 308}
    response = request_url(url, follow_redirects=follow_redirects)
    if response.status != case.expected_status:
        issues.append(f"{case.path}: expected status {case.expected_status}, got {response.status}")
        return issues, checked, redirects_checked, sitemap_absence_checked

    if case.expected_location_path:
        redirects_checked += 1
        expected_location = expected_url(base_url, case.expected_location_path)
        location = response.headers.get("location", "")
        if location != expected_location and public_path(location) != case.expected_location_path:
            issues.append(f"{case.path}: expected redirect to {expected_location!r}, got {location!r}")
        return issues, checked, redirects_checked, sitemap_absence_checked

    parser = parse_head(response.text)
    checked += 1
    tokens = robots_tokens(parser.robots)
    if "noindex" not in tokens or "follow" not in tokens:
        issues.append(f"{case.path}: noindex page robots should include noindex/follow, got {parser.robots!r}")
    if case.expected_canonical_path:
        expected_canonical = expected_url(base_url, case.expected_canonical_path)
        if parser.canonical != expected_canonical:
            issues.append(f"{case.path}: canonical should be {expected_canonical!r}, got {parser.canonical!r}")
    return issues, checked, redirects_checked, sitemap_absence_checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public index/noindex SEO boundaries for LoveTypes.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    locations, issues = sitemap_locations(base_url)
    sitemap_set = set(locations)

    public_indexability_sitemap_pages_checked = 0
    public_indexability_noindex_pages_checked = 0
    public_indexability_redirects_checked = 0
    public_indexability_sitemap_absence_checked = 0

    for loc in locations:
        page_issues, count = indexable_page_issues(base_url, loc)
        issues.extend(page_issues)
        public_indexability_sitemap_pages_checked += count

    for case in noindex_cases(base_url):
        case_issues, checked, redirects_checked, sitemap_absence_checked = noindex_case_issues(base_url, sitemap_set, case)
        issues.extend(case_issues)
        public_indexability_noindex_pages_checked += checked
        public_indexability_redirects_checked += redirects_checked
        public_indexability_sitemap_absence_checked += sitemap_absence_checked

    print(f"public_indexability_sitemap_urls_listed={len(locations)}")
    print(f"public_indexability_sitemap_pages_checked={public_indexability_sitemap_pages_checked}")
    print(f"public_indexability_noindex_pages_checked={public_indexability_noindex_pages_checked}")
    print(f"public_indexability_redirects_checked={public_indexability_redirects_checked}")
    print(f"public_indexability_sitemap_absence_checked={public_indexability_sitemap_absence_checked}")
    print(f"public_indexability_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
