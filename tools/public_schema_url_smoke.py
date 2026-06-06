#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
URL_KEYS = {
    "@id",
    "contentUrl",
    "embedUrl",
    "image",
    "item",
    "logo",
    "mainEntityOfPage",
    "sameAs",
    "thumbnailUrl",
    "url",
}
IMAGE_KEYS = {"contentUrl", "image", "logo", "thumbnailUrl"}


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int
    content_type: str
    text: str


class JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical = ""
        self.jsonld_blocks: list[str] = []
        self._in_jsonld = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")
        elif tag == "script" and data.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            block = "".join(self._buffer).strip()
            if block:
                self.jsonld_blocks.append(block)


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def fetch(url: str, *, attempts: int = 3, method: str = "GET") -> FetchResult:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                url,
                method=method,
                headers={"User-Agent": "LoveTypes public schema URL smoke/1.0"},
            )
            with urlopen(request, timeout=20) as raw:
                body = raw.read()
                text = "" if method == "HEAD" else body.decode("utf-8", errors="replace")
                return FetchResult(raw.geturl(), raw.status, raw.headers.get("Content-Type", ""), text)
        except HTTPError as error:
            body = error.read()
            text = "" if method == "HEAD" else body.decode("utf-8", errors="replace")
            return FetchResult(error.geturl(), error.code, error.headers.get("Content-Type", ""), text)
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def sitemap_locations(base_url: str) -> tuple[list[str], list[str]]:
    response = fetch(urljoin(base_url + "/", "sitemap.xml"))
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
    issues = []
    if len(locations) != len(set(locations)):
        issues.append("/sitemap.xml: duplicate loc values")
    return locations, issues


def public_path(url: str) -> str:
    path = urlparse(url).path or "/"
    if path.endswith("/") or "." in path.rsplit("/", 1)[-1]:
        return path
    return f"{path}/"


def parse_jsonld(path: str, blocks: list[str]) -> tuple[list[object], list[str], int]:
    parsed: list[object] = []
    issues: list[str] = []
    parsed_count = 0
    for index, block in enumerate(blocks, start=1):
        try:
            parsed.append(json.loads(block))
        except json.JSONDecodeError as error:
            issues.append(f"{path}: JSON-LD block {index} is invalid: {error}")
            continue
        parsed_count += 1
    return parsed, issues, parsed_count


def collect_schema_urls(data: object, *, current_key: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key in URL_KEYS:
                found.extend(extract_url_values(key, value))
            found.extend(collect_schema_urls(value, current_key=key))
    elif isinstance(data, list):
        for value in data:
            found.extend(collect_schema_urls(value, current_key=current_key))
    return found


def extract_url_values(key: str, value: object) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    if isinstance(value, str):
        if value.startswith(("http://", "https://")):
            values.append((key, value))
    elif isinstance(value, list):
        for entry in value:
            values.extend(extract_url_values(key, entry))
    elif isinstance(value, dict):
        if key == "mainEntityOfPage":
            nested_id = value.get("@id")
            if isinstance(nested_id, str) and nested_id.startswith(("http://", "https://")):
                values.append((key, nested_id))
        else:
            for nested_key in URL_KEYS:
                nested_value = value.get(nested_key)
                if nested_value is not None:
                    values.extend(extract_url_values(nested_key, nested_value))
    return values


def defragment(value: str) -> str:
    return urldefrag(value).url


def is_same_origin(value: str, base_url: str) -> bool:
    parsed = urlparse(value)
    base = urlparse(base_url)
    return parsed.scheme in {"http", "https"} and parsed.netloc == base.netloc


def is_html_page_url(value: str) -> bool:
    path = urlparse(defragment(value)).path
    filename = path.rsplit("/", 1)[-1]
    return not filename or "." not in filename


def validate_target(
    *,
    page_path: str,
    key: str,
    value: str,
    base_url: str,
    sitemap_set: set[str],
    cache: dict[tuple[str, str], FetchResult],
) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "internal_urls": 0,
        "image_urls": 0,
        "external_urls": 0,
        "sitemap_page_urls": 0,
    }
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return [f"{page_path}: JSON-LD {key} should use http(s), got {value!r}"], stats

    target = defragment(value)
    if is_same_origin(value, base_url):
        stats["internal_urls"] += 1
        request_key = ("GET", target)
        if request_key not in cache:
            cache[request_key] = fetch(target)
        result = cache[request_key]
        if result.status != 200:
            issues.append(f"{page_path}: JSON-LD {key} target should return 200, got {result.status}: {value}")
        if key in IMAGE_KEYS:
            stats["image_urls"] += 1
            if result.status == 200 and not result.content_type.lower().startswith("image/"):
                issues.append(
                    f"{page_path}: JSON-LD {key} target should be an image, got {result.content_type!r}: {value}"
                )
        elif is_html_page_url(value):
            stats["sitemap_page_urls"] += 1
            normalized = target.rstrip("/") + "/"
            if target not in sitemap_set and normalized not in sitemap_set:
                issues.append(f"{page_path}: JSON-LD {key} page URL should exist in sitemap: {value}")
    else:
        stats["external_urls"] += 1
        request_key = ("HEAD", target)
        if request_key not in cache:
            cache[request_key] = fetch(target, method="HEAD")
        result = cache[request_key]
        if result.status >= 500 or result.status in {404, 410}:
            issues.append(f"{page_path}: JSON-LD {key} external target looks unavailable ({result.status}): {value}")
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public JSON-LD URL targets across LoveTypes sitemap pages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    locations, issues = sitemap_locations(base_url)
    sitemap_set = set(locations)
    pages_checked = 0
    jsonld_blocks_checked = 0
    schema_url_values_checked = 0
    internal_urls_checked = 0
    image_urls_checked = 0
    external_urls_checked = 0
    sitemap_page_urls_checked = 0
    response_cache: dict[tuple[str, str], FetchResult] = {}

    for loc in locations:
        path = public_path(loc)
        response = fetch(loc)
        if response.status != 200:
            issues.append(f"{path}: expected status 200, got {response.status}")
            continue
        page_parser = JsonLdParser()
        page_parser.feed(response.text)
        parsed_blocks, parse_issues, parsed_count = parse_jsonld(path, page_parser.jsonld_blocks)
        issues.extend(parse_issues)
        pages_checked += 1
        jsonld_blocks_checked += parsed_count

        seen_on_page: set[tuple[str, str]] = set()
        for block in parsed_blocks:
            for key, value in collect_schema_urls(block):
                item = (key, value)
                if item in seen_on_page:
                    continue
                seen_on_page.add(item)
                schema_url_values_checked += 1
                target_issues, stats = validate_target(
                    page_path=path,
                    key=key,
                    value=value,
                    base_url=base_url,
                    sitemap_set=sitemap_set,
                    cache=response_cache,
                )
                issues.extend(target_issues)
                internal_urls_checked += stats["internal_urls"]
                image_urls_checked += stats["image_urls"]
                external_urls_checked += stats["external_urls"]
                sitemap_page_urls_checked += stats["sitemap_page_urls"]

    print(f"public_schema_url_pages_checked={pages_checked}")
    print(f"public_schema_url_jsonld_blocks_checked={jsonld_blocks_checked}")
    print(f"public_schema_url_values_checked={schema_url_values_checked}")
    print(f"public_schema_url_internal_urls_checked={internal_urls_checked}")
    print(f"public_schema_url_image_urls_checked={image_urls_checked}")
    print(f"public_schema_url_external_urls_checked={external_urls_checked}")
    print(f"public_schema_url_sitemap_page_urls_checked={sitemap_page_urls_checked}")
    print(f"public_schema_url_unique_targets_checked={len(response_cache)}")
    print(f"public_schema_url_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
