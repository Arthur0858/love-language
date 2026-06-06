#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
LOCALE_PREFIXES = {"zh-TW": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
HTML_LANG_TO_HREFLANG = {"zh-TW": "zh-TW", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
PRIMARY_ROUTES = ("garden-map", "guides", "characters", "theory", "resources", "about")
FOOTER_ROUTES = ("garden-map", "characters", "resources", "guides", "repair-plan", "privacy", "terms", "contact")


@dataclass
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


@dataclass(frozen=True)
class Anchor:
    href: str
    lang: str
    aria_current: str


class LocaleRouteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.primary_nav_links: list[Anchor] = []
        self.language_links: list[Anchor] = []
        self.footer_links: list[Anchor] = []
        self._context_stack: list[str] = []
        self._in_primary_nav = 0
        self._in_language_menu = 0
        self._in_footer = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
        context = ""
        if tag == "html":
            self.html_lang = data.get("lang", "")
        if tag == "nav" and "nav-links" in classes:
            self._in_primary_nav += 1
            context = "primary_nav"
        elif tag == "details" and "language-menu" in classes:
            self._in_language_menu += 1
            context = "language_menu"
        elif tag == "footer" and "site-footer" in classes:
            self._in_footer += 1
            context = "footer"

        if tag == "a" and data.get("href"):
            anchor = Anchor(
                href=data.get("href", ""),
                lang=data.get("lang", ""),
                aria_current=data.get("aria-current", ""),
            )
            if self._in_primary_nav:
                self.primary_nav_links.append(anchor)
            if self._in_language_menu:
                self.language_links.append(anchor)
            if self._in_footer:
                self.footer_links.append(anchor)
        self._context_stack.append(context)

    def handle_endtag(self, tag: str) -> None:
        context = self._context_stack.pop() if self._context_stack else ""
        if context == "primary_nav":
            self._in_primary_nav -= 1
        elif context == "language_menu":
            self._in_language_menu -= 1
        elif context == "footer":
            self._in_footer -= 1


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public locale route smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                headers = {key.lower(): value for key, value in raw.headers.items()}
                return Response(raw.geturl(), raw.status, headers, raw.read())
        except HTTPError as error:
            headers = {key.lower(): value for key, value in error.headers.items()}
            return Response(error.geturl(), error.code, headers, error.read())
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def sitemap_locations(base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [], [f"/sitemap.xml: invalid XML: {error}"]
    locations = [
        (node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) or "").strip()
        for node in root.findall("sm:url", SITEMAP_NS)
    ]
    locations = [loc for loc in locations if loc]
    issues = []
    if len(locations) != len(set(locations)):
        issues.append("/sitemap.xml: duplicate loc values")
    return sorted(set(locations)), issues


def public_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    return path if path.endswith("/") or "." in path.rsplit("/", 1)[-1] else f"{path}/"


def split_locale_path(path: str) -> tuple[str, str]:
    parts = [part for part in path.strip("/").split("/") if part]
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        return parts[0], "/".join(parts[1:])
    return "zh-TW", "/".join(parts)


def localized_route(lang: str, route: str) -> str:
    prefix = LOCALE_PREFIXES[lang]
    parts = [part for part in (prefix, route) if part]
    return "/" + "/".join(parts) + "/" if parts else "/"


def href_path(href: str, page_url: str) -> str:
    parsed = urlparse(urljoin(page_url, href))
    path = parsed.path or "/"
    return path if path.endswith("/") or "." in path.rsplit("/", 1)[-1] else f"{path}/"


def expected_language_href_map(current_path: str) -> dict[str, str]:
    _current_lang, unlocalized_route = split_locale_path(current_path)
    return {lang: localized_route(lang, unlocalized_route) for lang in LOCALE_PREFIXES}


def expected_route_set(lang: str, routes: tuple[str, ...]) -> set[str]:
    return {localized_route(lang, route) for route in routes}


def check_page(url: str) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "pages": 0,
        "primary_nav_links": 0,
        "footer_links": 0,
        "language_links": 0,
        "language_route_matches": 0,
        "localized_nav_route_matches": 0,
        "localized_footer_route_matches": 0,
        "localized_footer_exact_matches": 0,
    }
    response = request_url(url)
    path = public_path(response.url)
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    parser = LocaleRouteParser()
    parser.feed(response.text)
    stats["pages"] = 1

    page_lang, _unlocalized_route = split_locale_path(path)
    expected_html_lang = "zh-TW" if page_lang == "zh-TW" else page_lang
    if parser.html_lang != expected_html_lang:
        issues.append(f"{path}: html lang should be {expected_html_lang}, got {parser.html_lang!r}")

    primary_paths = [href_path(anchor.href, response.url) for anchor in parser.primary_nav_links]
    stats["primary_nav_links"] = len(primary_paths)
    expected_primary = expected_route_set(page_lang, PRIMARY_ROUTES)
    if set(primary_paths) != expected_primary or len(primary_paths) != len(PRIMARY_ROUTES):
        issues.append(f"{path}: primary nav routes should be {sorted(expected_primary)}, got {primary_paths}")
    else:
        stats["localized_nav_route_matches"] = len(primary_paths)

    footer_paths = [href_path(anchor.href, response.url) for anchor in parser.footer_links]
    stats["footer_links"] = len(footer_paths)
    expected_footer = expected_route_set(page_lang, FOOTER_ROUTES)
    missing_footer = sorted(expected_footer.difference(footer_paths))
    extra_footer = sorted(set(footer_paths).difference(expected_footer))
    duplicate_footer = sorted(item for item in set(footer_paths) if footer_paths.count(item) > 1)
    if set(footer_paths) != expected_footer or len(footer_paths) != len(FOOTER_ROUTES):
        issues.append(
            f"{path}: footer routes should be exactly {sorted(expected_footer)}, got {footer_paths}"
        )
        if missing_footer:
            issues.append(f"{path}: footer missing localized routes {missing_footer}")
        if extra_footer:
            issues.append(f"{path}: footer has unexpected localized routes {extra_footer}")
        if duplicate_footer:
            issues.append(f"{path}: footer has duplicate localized routes {duplicate_footer}")
    else:
        stats["localized_footer_route_matches"] = len(expected_footer)
        stats["localized_footer_exact_matches"] = 1

    expected_language_hrefs = expected_language_href_map(path)
    language_by_lang = {anchor.lang: href_path(anchor.href, response.url) for anchor in parser.language_links}
    stats["language_links"] = len(parser.language_links)
    expected_language_codes = set(expected_language_hrefs)
    if set(language_by_lang) != expected_language_codes:
        issues.append(f"{path}: language menu langs should be {sorted(expected_language_codes)}, got {sorted(language_by_lang)}")
    for lang, expected_href in expected_language_hrefs.items():
        actual_href = language_by_lang.get(lang)
        if actual_href == expected_href:
            stats["language_route_matches"] += 1
        elif actual_href:
            issues.append(f"{path}: language menu {lang} should be {expected_href}, got {actual_href}")

    current_language_links = [anchor for anchor in parser.language_links if anchor.aria_current == "page"]
    expected_current_lang = HTML_LANG_TO_HREFLANG.get(parser.html_lang, parser.html_lang)
    if len(current_language_links) != 1:
        issues.append(f"{path}: expected one active language menu link, got {len(current_language_links)}")
    elif current_language_links[0].lang != expected_current_lang:
        issues.append(f"{path}: active language menu link should be {expected_current_lang}, got {current_language_links[0].lang}")

    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public localized nav, footer, and language-route consistency.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    locations, issues = sitemap_locations(base_url)
    totals = {
        "pages": 0,
        "primary_nav_links": 0,
        "footer_links": 0,
        "language_links": 0,
        "language_route_matches": 0,
        "localized_nav_route_matches": 0,
        "localized_footer_route_matches": 0,
        "localized_footer_exact_matches": 0,
    }
    for loc in locations:
        page_issues, page_stats = check_page(loc)
        issues.extend(page_issues)
        for key, value in page_stats.items():
            totals[key] += value

    print(f"public_locale_route_pages_checked={totals['pages']}")
    print(f"public_locale_route_primary_nav_links_checked={totals['primary_nav_links']}")
    print(f"public_locale_route_footer_links_checked={totals['footer_links']}")
    print(f"public_locale_route_language_links_checked={totals['language_links']}")
    print(f"public_locale_route_language_matches_checked={totals['language_route_matches']}")
    print(f"public_locale_route_nav_matches_checked={totals['localized_nav_route_matches']}")
    print(f"public_locale_route_footer_matches_checked={totals['localized_footer_route_matches']}")
    print(f"public_locale_route_footer_exact_pages_checked={totals['localized_footer_exact_matches']}")
    print(f"public_locale_route_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
