#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import ssl
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from io import BytesIO
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from PIL import Image


DEFAULT_BASE_URL = "https://lovetypes.tw"
EXPECTED_HREFLANGS = {"zh-TW", "en", "ja", "ko", "es", "x-default"}
EXPECTED_OG_LOCALES = {"zh_TW", "en_US", "ja_JP", "ko_KR", "es_ES"}
LOCALE_PREFIXES = {"zh-TW": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
SITEMAP_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}
MAX_TITLE_LENGTH = 90
DESCRIPTION_LENGTH_LIMITS = {
    "zh-TW": (24, 95),
    "ja": (28, 105),
    "ko": (32, 125),
    "en": (50, 170),
    "es": (50, 170),
}
IMAGE_SAMPLE_LIMIT = 24


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.title = ""
        self.description = ""
        self.robots = ""
        self.canonical = ""
        self.hreflangs: dict[str, str] = {}
        self.duplicate_hreflangs: set[str] = set()
        self.meta_name: dict[str, str] = {}
        self.meta_property: dict[str, list[str]] = {}
        self.jsonld_blocks: list[str] = []
        self._in_title = False
        self._in_jsonld = False
        self._jsonld_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = data.get("name", "").lower()
            prop = data.get("property", "").lower()
            content = data.get("content", "")
            if name:
                self.meta_name[name] = content
            if prop:
                self.meta_property.setdefault(prop, []).append(content)
            if name == "description":
                self.description = content
            elif name == "robots":
                self.robots = content
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")
        elif tag == "link" and data.get("rel") == "alternate" and data.get("hreflang"):
            lang = data.get("hreflang", "")
            if lang in self.hreflangs:
                self.duplicate_hreflangs.add(lang)
            self.hreflangs[lang] = data.get("href", "")
        elif tag == "script" and data.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_jsonld:
            self._jsonld_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            block = "".join(self._jsonld_buffer).strip()
            if block:
                self.jsonld_blocks.append(block)


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    context = ssl.create_default_context()
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public metadata smoke/1.0"})
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
    return first if first in {"en", "ja", "ko", "es"} else "zh-TW"


def description_limits(path: str) -> tuple[int, int]:
    return DESCRIPTION_LENGTH_LIMITS[expected_lang(path)]


def expected_canonical(canonical_base_url: str, path: str) -> str:
    return urljoin(canonical_base_url + "/", path.lstrip("/"))


def expected_hreflang_map(canonical_base_url: str, path: str) -> dict[str, str]:
    parts = [part for part in path.strip("/").split("/") if part]
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        suffix_parts = parts[1:]
    else:
        suffix_parts = parts
    suffix = "/".join(suffix_parts)
    result: dict[str, str] = {}
    for lang, prefix in LOCALE_PREFIXES.items():
        route = "/".join(part for part in (prefix, suffix) if part)
        result[lang] = urljoin(canonical_base_url + "/", f"{route}/" if route else "")
    result["x-default"] = result["zh-TW"]
    return result


def sitemap_paths(base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    issues: list[str] = []
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [], [f"/sitemap.xml: invalid XML: {error}"]
    paths = [public_path((node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) or "").strip()) for node in root.findall("sm:url", SITEMAP_NS)]
    paths = [path for path in paths if path]
    if len(paths) != len(set(paths)):
        issues.append("/sitemap.xml: duplicate loc values")
    return paths, issues


def first(values: list[str] | None) -> str:
    return values[0] if values else ""


def check_jsonld(path: str, parser: MetadataParser) -> tuple[list[str], int]:
    issues: list[str] = []
    parsed_count = 0
    if not parser.jsonld_blocks:
        return [f"{path}: missing JSON-LD"], 0
    for index, block in enumerate(parser.jsonld_blocks, start=1):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as error:
            issues.append(f"{path}: JSON-LD block {index} is invalid: {error}")
            continue
        parsed_count += 1
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                issues.append(f"{path}: JSON-LD block {index} should contain objects")
                continue
            if item.get("@context") != "https://schema.org":
                issues.append(f"{path}: JSON-LD block {index} missing schema.org context")
            if not item.get("@type"):
                issues.append(f"{path}: JSON-LD block {index} missing @type")
    return issues, parsed_count


def check_page(base_url: str, canonical_base_url: str, path: str) -> tuple[list[str], MetadataParser, int]:
    issues: list[str] = []
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    parser = MetadataParser()
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], parser, 0
    parser.feed(response.text)

    title = parser.title.strip()
    if not title:
        issues.append(f"{path}: missing title")
    elif len(title) > MAX_TITLE_LENGTH:
        issues.append(f"{path}: title too long ({len(title)} > {MAX_TITLE_LENGTH})")

    min_description_length, max_description_length = description_limits(path)
    if len(parser.description) < min_description_length:
        issues.append(f"{path}: description too short ({len(parser.description)} < {min_description_length})")
    if len(parser.description) > max_description_length:
        issues.append(f"{path}: description too long ({len(parser.description)} > {max_description_length})")

    expected_url = expected_canonical(canonical_base_url, path)
    if parser.canonical != expected_url:
        issues.append(f"{path}: canonical should be {expected_url!r}, got {parser.canonical!r}")
    if parser.meta_property.get("og:url") != [expected_url]:
        issues.append(f"{path}: og:url should be exactly {expected_url!r}, got {parser.meta_property.get('og:url')!r}")
    if parser.html_lang != expected_lang(path):
        issues.append(f"{path}: html lang should be {expected_lang(path)!r}, got {parser.html_lang!r}")

    robots_tokens = {token.strip().lower() for token in parser.robots.split(",") if token.strip()}
    if {"index", "follow"}.difference(robots_tokens) or "noindex" in robots_tokens:
        issues.append(f"{path}: robots should include index/follow and not noindex, got {parser.robots!r}")

    if first(parser.meta_property.get("og:title")) != title:
        issues.append(f"{path}: og:title should match title")
    if first(parser.meta_property.get("og:description")) != parser.description:
        issues.append(f"{path}: og:description should match description")
    if first(parser.meta_property.get("og:type")) not in {"website", "article", "profile"}:
        issues.append(f"{path}: missing or unsupported og:type {first(parser.meta_property.get('og:type'))!r}")
    if first(parser.meta_name.get("twitter:card", "").splitlines()) != "summary_large_image":
        issues.append(f"{path}: twitter:card should be summary_large_image")

    og_image = first(parser.meta_property.get("og:image"))
    twitter_image = parser.meta_name.get("twitter:image", "")
    if not og_image.startswith(canonical_base_url + "/"):
        issues.append(f"{path}: og:image should be a production LoveTypes URL, got {og_image!r}")
    if twitter_image != og_image:
        issues.append(f"{path}: twitter:image should match og:image")
    if first(parser.meta_property.get("og:image:width")) != "1200":
        issues.append(f"{path}: og:image:width should be 1200")
    if first(parser.meta_property.get("og:image:height")) != "630":
        issues.append(f"{path}: og:image:height should be 630")

    og_locale = first(parser.meta_property.get("og:locale"))
    og_alternates = set(parser.meta_property.get("og:locale:alternate", []))
    if og_locale not in EXPECTED_OG_LOCALES:
        issues.append(f"{path}: unexpected og:locale {og_locale!r}")
    expected_alternates = EXPECTED_OG_LOCALES.difference({og_locale})
    if og_alternates != expected_alternates:
        issues.append(f"{path}: og:locale:alternate should be {sorted(expected_alternates)}, got {sorted(og_alternates)}")

    expected_hreflangs = expected_hreflang_map(canonical_base_url, path)
    if set(parser.hreflangs) != EXPECTED_HREFLANGS:
        issues.append(f"{path}: hreflangs should be {sorted(EXPECTED_HREFLANGS)}, got {sorted(parser.hreflangs)}")
    if parser.duplicate_hreflangs:
        issues.append(f"{path}: duplicate hreflangs {sorted(parser.duplicate_hreflangs)}")
    for lang, expected_href in expected_hreflangs.items():
        if parser.hreflangs.get(lang) != expected_href:
            issues.append(f"{path}: hreflang {lang} should be {expected_href!r}, got {parser.hreflangs.get(lang)!r}")

    jsonld_issues, jsonld_count = check_jsonld(path, parser)
    issues.extend(jsonld_issues)
    return issues, parser, jsonld_count


def check_images(image_urls: list[str], canonical_base_url: str) -> tuple[list[str], int, int]:
    issues: list[str] = []
    checked = 0
    dimensions_checked = 0
    for image_url in image_urls[:IMAGE_SAMPLE_LIMIT]:
        response = request_url(image_url)
        checked += 1
        if response.status != 200:
            issues.append(f"{image_url}: expected status 200, got {response.status}")
            continue
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            issues.append(f"{image_url}: expected image content-type, got {content_type!r}")
        if not response.url.startswith(canonical_base_url + "/"):
            issues.append(f"{image_url}: should stay on canonical host, got {response.url}")
        try:
            with Image.open(BytesIO(response.body)) as image:
                width, height = image.size
        except OSError as error:
            issues.append(f"{image_url}: could not read image dimensions: {error}")
            continue
        dimensions_checked += 1
        if (width, height) != (1200, 630):
            issues.append(f"{image_url}: social image should be 1200x630, got {width}x{height}")
    return issues, checked, dimensions_checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public SEO and social metadata across sitemap pages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Production or preview base URL.")
    parser.add_argument(
        "--canonical-base-url",
        default=DEFAULT_BASE_URL,
        help="Canonical production URL expected inside metadata.",
    )
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    canonical_base_url = normalize_base_url(args.canonical_base_url)

    paths, issues = sitemap_paths(base_url)
    pages_checked = 0
    jsonld_blocks_checked = 0
    social_cards_checked = 0
    hreflang_links_checked = 0
    image_urls: list[str] = []

    for path in paths:
        page_issues, page_parser, jsonld_count = check_page(base_url, canonical_base_url, path)
        issues.extend(page_issues)
        pages_checked += 1
        jsonld_blocks_checked += jsonld_count
        social_cards_checked += 1 if page_parser.meta_property.get("og:image") else 0
        hreflang_links_checked += len(page_parser.hreflangs)
        og_image = first(page_parser.meta_property.get("og:image"))
        if og_image and og_image not in image_urls:
            image_urls.append(og_image)

    image_issues, images_checked, image_dimensions_checked = check_images(image_urls, canonical_base_url)
    issues.extend(image_issues)

    print(f"public_metadata_pages_checked={pages_checked}")
    print(f"public_metadata_social_cards_checked={social_cards_checked}")
    print(f"public_metadata_hreflang_links_checked={hreflang_links_checked}")
    print(f"public_metadata_jsonld_blocks_checked={jsonld_blocks_checked}")
    print(f"public_metadata_images_checked={images_checked}")
    print(f"public_metadata_image_dimensions_checked={image_dimensions_checked}")
    print(f"public_metadata_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
