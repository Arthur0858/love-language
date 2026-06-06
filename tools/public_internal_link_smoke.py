#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ssl
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse, unquote
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
SKIPPED_SCHEMES = {"mailto", "tel", "javascript", "data", "blob"}
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


@dataclass
class Response:
    requested_url: str
    final_url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


@dataclass(frozen=True)
class InternalLink:
    url: str
    source_paths: tuple[str, ...]


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if "id" in data and data["id"]:
            self.ids.add(data["id"])
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    context = ssl.create_default_context()
    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "LoveTypes public internal link smoke/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            with urlopen(request, timeout=20, context=context) as raw:
                headers = {key.lower(): value for key, value in raw.headers.items()}
                return Response(url, raw.geturl(), raw.status, headers, raw.read())
        except HTTPError as error:
            headers = {key.lower(): value for key, value in error.headers.items()}
            return Response(url, error.geturl(), error.code, headers, error.read())
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


def strip_fragment(url: str) -> str:
    base, _fragment = urldefrag(url)
    return base


def normalize_check_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    query = parsed.query
    return urlunparse((parsed.scheme, parsed.netloc, path, "", query, parsed.fragment))


def sitemap_urls(base_url: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [], [f"/sitemap.xml: invalid XML: {error}"]

    urls: list[str] = []
    for node in root.findall("sm:url", SITEMAP_NS):
        loc = (node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) or "").strip()
        if not loc:
            issues.append("/sitemap.xml: url entry missing loc")
            continue
        parsed = urlparse(loc)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in LOCAL_HOSTS:
            issues.append(f"/sitemap.xml: loc should be a LoveTypes URL: {loc}")
            continue
        urls.append(normalize_check_url(loc))
    return sorted(set(urls)), issues


def parse_html(response: Response) -> AnchorParser:
    parser = AnchorParser()
    parser.feed(response.text)
    return parser


def is_html(response: Response) -> bool:
    content_type = response.headers.get("content-type", "")
    return "text/html" in content_type or "application/xhtml+xml" in content_type


def should_skip_href(href: str) -> bool:
    href = href.strip()
    if not href:
        return True
    parsed = urlparse(href)
    if parsed.scheme.lower() in SKIPPED_SCHEMES:
        return True
    if parsed.path.startswith("/cdn-cgi/"):
        return True
    return False


def collect_internal_links(base_url: str, page_urls: list[str]) -> tuple[list[InternalLink], dict[str, AnchorParser], list[str], int]:
    issues: list[str] = []
    sources_by_url: dict[str, set[str]] = {}
    page_parsers: dict[str, AnchorParser] = {}
    links_seen = 0

    for page_url in page_urls:
        try:
            response = request_url(page_url)
        except RuntimeError as error:
            issues.append(f"{public_path(page_url)}: request failed: {error}")
            continue
        if response.status != 200:
            issues.append(f"{public_path(page_url)}: expected status 200, got {response.status}")
            continue
        if not is_html(response):
            issues.append(f"{public_path(page_url)}: expected HTML, got {response.headers.get('content-type', '')!r}")
            continue

        parser = parse_html(response)
        page_parsers[strip_fragment(normalize_check_url(response.final_url))] = parser
        source_path = public_path(response.final_url)
        for href in parser.hrefs:
            if should_skip_href(href):
                continue
            absolute = normalize_check_url(urljoin(response.final_url, href))
            parsed = urlparse(absolute)
            if parsed.scheme not in {"http", "https"} or parsed.hostname not in LOCAL_HOSTS:
                continue
            if parsed.path.startswith("/cdn-cgi/"):
                continue
            links_seen += 1
            sources_by_url.setdefault(absolute, set()).add(source_path)

    links = [
        InternalLink(url=url, source_paths=tuple(sorted(source_paths)))
        for url, source_paths in sorted(sources_by_url.items())
    ]
    return links, page_parsers, issues, links_seen


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that public internal LoveTypes links and anchors are reachable.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    page_urls, sitemap_issues = sitemap_urls(base_url)
    issues.extend(sitemap_issues)

    links, page_parsers, collect_issues, links_seen = collect_internal_links(base_url, page_urls)
    issues.extend(collect_issues)

    response_cache: dict[str, Response] = {}
    parser_cache: dict[str, AnchorParser] = dict(page_parsers)
    redirects_followed = 0
    anchor_targets_checked = 0

    for link in links:
        target_without_fragment, fragment = urldefrag(link.url)
        target_without_fragment = normalize_check_url(target_without_fragment)
        try:
            if target_without_fragment not in response_cache:
                response_cache[target_without_fragment] = request_url(target_without_fragment)
            response = response_cache[target_without_fragment]
        except RuntimeError as error:
            issues.append(f"{link.url}: request failed from {', '.join(link.source_paths)}: {error}")
            continue

        if response.status >= 400:
            issues.append(f"{link.url}: expected reachable status, got {response.status} final={response.final_url}")
            continue
        final_host = urlparse(response.final_url).hostname
        if final_host not in LOCAL_HOSTS:
            issues.append(f"{link.url}: redirected outside LoveTypes to {response.final_url}")
            continue
        if strip_fragment(normalize_check_url(response.final_url)) != target_without_fragment:
            redirects_followed += 1

        if fragment and is_html(response):
            final_base = strip_fragment(normalize_check_url(response.final_url))
            if final_base not in parser_cache:
                parser_cache[final_base] = parse_html(response)
            ids = parser_cache[final_base].ids
            anchor_targets_checked += 1
            decoded_fragment = unquote(fragment)
            if decoded_fragment not in ids and fragment not in ids:
                sources = ", ".join(link.source_paths)
                issues.append(f"{link.url}: missing anchor target #{fragment} from {sources}")

    print(f"public_internal_link_pages_checked={len(page_urls)}")
    print(f"public_internal_links_seen={links_seen}")
    print(f"public_internal_unique_links_checked={len(links)}")
    print(f"public_internal_anchor_targets_checked={anchor_targets_checked}")
    print(f"public_internal_redirects_followed={redirects_followed}")
    print(f"public_internal_link_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
