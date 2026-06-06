#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ssl
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
EXPECTED_HREFLANGS = {"zh-TW", "en", "ja", "ko", "es", "x-default"}
LOCALE_PREFIXES = {"zh-TW": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
CORE_UNIVERSE_ROUTES = (
    "",
    "garden-map",
    "guides",
    "characters",
    "theory",
    "resources",
    "repair-plan",
    "keepsakes",
    "luna-yoga-music",
    "about",
    "contact",
    "privacy",
    "terms",
)
SITEMAP_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}
REQUIRED_GLOBAL_HEADERS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "SAMEORIGIN",
}


@dataclass
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class PageHeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.canonical = ""
        self.html_lang = ""
        self.robots = ""
        self.h1_count = 0
        self.hreflangs: dict[str, str] = {}
        self.duplicate_hreflangs: set[str] = set()
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")
        elif tag == "link" and data.get("rel") == "alternate" and data.get("hreflang"):
            lang = data.get("hreflang", "")
            if lang in self.hreflangs:
                self.duplicate_hreflangs.add(lang)
            self.hreflangs[lang] = data.get("href", "")
        elif tag == "meta" and data.get("name") == "robots":
            self.robots = data.get("content", "")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    context = ssl.create_default_context()
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public sitemap smoke/1.0"})
            with urlopen(request, timeout=20, context=context) as raw:
                headers = {key.lower(): value for key, value in raw.headers.items()}
                return Response(raw.geturl(), raw.status, headers, raw.read())
        except HTTPError as error:
            return Response(error.geturl(), error.code, {key.lower(): value for key, value in error.headers.items()}, error.read())
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def public_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    return path if path.endswith("/") or "." in path.rsplit("/", 1)[-1] else f"{path}/"


def expected_lang(path: str) -> str:
    first = path.strip("/").split("/", 1)[0]
    if first in {"en", "ja", "ko", "es"}:
        return first
    return "zh-TW"


def expected_canonical(canonical_base_url: str, path: str) -> str:
    return urljoin(canonical_base_url + "/", path.lstrip("/"))


def expected_hreflang_map(canonical_base_url: str, path: str) -> dict[str, str]:
    parts = [part for part in path.strip("/").split("/") if part]
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        unlocalized_parts = parts[1:]
    else:
        unlocalized_parts = parts
    suffix = "/".join(unlocalized_parts)
    result: dict[str, str] = {}
    for lang, prefix in LOCALE_PREFIXES.items():
        route = "/".join(part for part in (prefix, suffix) if part)
        result[lang] = urljoin(canonical_base_url + "/", f"{route}/" if route else "")
    result["x-default"] = result["zh-TW"]
    return result


def localized_path(lang: str, route: str) -> str:
    prefix = LOCALE_PREFIXES[lang]
    parts = [part for part in (prefix, route) if part]
    return "/" + "/".join(parts) + "/" if parts else "/"


def expected_core_universe_paths() -> set[str]:
    return {
        localized_path(lang, route)
        for lang in LOCALE_PREFIXES
        for route in CORE_UNIVERSE_ROUTES
    }


def sitemap_paths(base_url: str, canonical_base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    issues: list[str] = []
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [], [f"/sitemap.xml: invalid XML: {error}"]
    paths: list[str] = []
    canonical_host = urlparse(canonical_base_url).netloc
    for node in root.findall("sm:url", SITEMAP_NS):
        loc = (node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) or "").strip()
        if not loc:
            issues.append("/sitemap.xml: url entry missing loc")
            continue
        parsed = urlparse(loc)
        if parsed.scheme != "https" or parsed.netloc != canonical_host:
            issues.append(f"/sitemap.xml: loc should use https {canonical_host}: {loc}")
        paths.append(public_path(loc))
    if len(set(paths)) != len(paths):
        issues.append("/sitemap.xml: duplicate loc values")
    return paths, issues


def check_page(base_url: str, canonical_base_url: str, path: str) -> tuple[list[str], int, int]:
    issues: list[str] = []
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    if response.status != 200:
        issues.append(f"{path}: expected status 200, got {response.status}")
        return issues, 0, 0
    final_path = public_path(response.url)
    if final_path.rstrip("/") != path.rstrip("/"):
        issues.append(f"{path}: expected final path {path}, got {final_path}")
    for header, expected in REQUIRED_GLOBAL_HEADERS.items():
        if response.headers.get(header) != expected:
            issues.append(f"{path}: header {header} should be {expected!r}, got {response.headers.get(header)!r}")

    parser = PageHeadParser()
    parser.feed(response.text)
    if not parser.title.strip():
        issues.append(f"{path}: missing title")
    if parser.h1_count != 1:
        issues.append(f"{path}: expected one h1, got {parser.h1_count}")
    expected_canonical_url = expected_canonical(canonical_base_url, path)
    if parser.canonical != expected_canonical_url:
        issues.append(f"{path}: canonical should be {expected_canonical_url!r}, got {parser.canonical!r}")
    if parser.html_lang != expected_lang(path):
        issues.append(f"{path}: html lang should be {expected_lang(path)!r}, got {parser.html_lang!r}")
    robots_tokens = {token.strip().lower() for token in parser.robots.split(",") if token.strip()}
    if "noindex" in robots_tokens:
        issues.append(f"{path}: sitemap page should not be noindex")
    if "index" not in robots_tokens or "follow" not in robots_tokens:
        issues.append(f"{path}: robots should include index, follow; got {parser.robots!r}")

    expected_hreflangs = expected_hreflang_map(canonical_base_url, path)
    missing = sorted(EXPECTED_HREFLANGS.difference(parser.hreflangs))
    extra = sorted(set(parser.hreflangs).difference(EXPECTED_HREFLANGS))
    if missing:
        issues.append(f"{path}: missing hreflang links {', '.join(missing)}")
    if extra:
        issues.append(f"{path}: unexpected hreflang links {', '.join(extra)}")
    if parser.duplicate_hreflangs:
        issues.append(f"{path}: duplicate hreflang links {', '.join(sorted(parser.duplicate_hreflangs))}")
    checked_hreflangs = 0
    for lang, expected_url in expected_hreflangs.items():
        actual_url = parser.hreflangs.get(lang)
        if actual_url:
            checked_hreflangs += 1
            if actual_url != expected_url:
                issues.append(f"{path}: hreflang {lang} should be {expected_url!r}, got {actual_url!r}")
    return issues, 1, checked_hreflangs


def main() -> int:
    parser = argparse.ArgumentParser(description="Check every public URL listed in sitemap.xml.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Production or preview base URL.")
    parser.add_argument(
        "--canonical-base-url",
        default=DEFAULT_BASE_URL,
        help="Canonical production URL expected inside pages and sitemap.",
    )
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    canonical_base_url = normalize_base_url(args.canonical_base_url)

    paths, issues = sitemap_paths(base_url, canonical_base_url)
    expected_core_paths = expected_core_universe_paths()
    core_paths_present = expected_core_paths.intersection(paths)
    missing_core_paths = sorted(expected_core_paths.difference(paths))
    for path in missing_core_paths:
        issues.append(f"/sitemap.xml: missing core universe route {path}")
    pages_checked = 0
    hreflang_links_checked = 0
    for path in paths:
        page_issues, page_count, hreflang_count = check_page(base_url, canonical_base_url, path)
        issues.extend(page_issues)
        pages_checked += page_count
        hreflang_links_checked += hreflang_count

    print(f"public_sitemap_urls_listed={len(paths)}")
    print(f"public_sitemap_core_universe_routes_expected={len(expected_core_paths)}")
    print(f"public_sitemap_core_universe_routes_checked={len(core_paths_present)}")
    print(f"public_sitemap_pages_checked={pages_checked}")
    print(f"public_sitemap_hreflang_links_checked={hreflang_links_checked}")
    print(f"public_sitemap_issues={len(issues)}")
    for issue in issues[:200]:
        print(issue)
    if len(issues) > 200:
        print(f"... {len(issues) - 200} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
