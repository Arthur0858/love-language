#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
EXPECTED_ORGANIZATION = {
    "@id": "https://lovetypes.tw/#organization",
    "name": "LoveTypes",
    "url": "https://lovetypes.tw/",
    "logo": "https://lovetypes.tw/apple-touch-icon.png",
    "email": "contact@lovetypes.tw",
}
LOCALE_PREFIXES = {"zh-TW": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
CORE_PAGE_SCHEMA_TYPES = {
    "": "WebSite",
    "garden-map": "CollectionPage",
    "guides": "CollectionPage",
    "characters": "CollectionPage",
    "theory": "WebPage",
    "resources": "CollectionPage",
    "repair-plan": "HowTo",
    "keepsakes": "CollectionPage",
    "luna-yoga-music": "WebPage",
    "about": "AboutPage",
    "contact": "ContactPage",
    "privacy": "WebPage",
    "terms": "WebPage",
}
PAGE_SCHEMA_TYPES = {
    "AboutPage",
    "Article",
    "CollectionPage",
    "ContactPage",
    "HowTo",
    "ProfilePage",
    "WebPage",
    "WebSite",
}
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    text: str


class SchemaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.jsonld_blocks: list[str] = []
        self._in_title = False
        self._in_jsonld = False
        self._jsonld_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and data.get("name", "").lower() == "description":
            self.description = data.get("content", "")
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")
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
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public schema smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                return Response(raw.geturl(), raw.status, raw.read().decode("utf-8", errors="replace"))
        except HTTPError as error:
            return Response(error.geturl(), error.code, error.read().decode("utf-8", errors="replace"))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def public_path(url: str) -> str:
    path = urlparse(url).path or "/"
    if path.endswith("/") or "." in path.rsplit("/", 1)[-1]:
        return path
    return f"{path}/"


def is_locale_home(path: str) -> bool:
    return path in {"/", "/en/", "/ja/", "/ko/", "/es/"}


def localized_path(lang: str, route: str) -> str:
    prefix = LOCALE_PREFIXES[lang]
    parts = [part for part in (prefix, route) if part]
    return "/" + "/".join(parts) + "/" if parts else "/"


def expected_core_page_schema_types() -> dict[str, str]:
    return {
        localized_path(lang, route): schema_type
        for lang in LOCALE_PREFIXES
        for route, schema_type in CORE_PAGE_SCHEMA_TYPES.items()
    }


def expected_guardian_profile_paths() -> set[str]:
    return {
        localized_path(lang, f"characters/{slug}")
        for lang in LOCALE_PREFIXES
        for slug in GUARDIAN_SLUGS
    }


def sitemap_locations(base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
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


def parse_jsonld_blocks(path: str, blocks: list[str]) -> tuple[list[dict], list[str], int]:
    entities: list[dict] = []
    issues: list[str] = []
    parsed_blocks = 0
    if not blocks:
        return entities, [f"{path}: missing JSON-LD"], parsed_blocks
    for index, block in enumerate(blocks, start=1):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as error:
            issues.append(f"{path}: JSON-LD block {index} is invalid: {error}")
            continue
        parsed_blocks += 1
        block_entities = jsonld_entities(data)
        if not block_entities:
            issues.append(f"{path}: JSON-LD block {index} should contain an object or @graph")
        entities.extend(block_entities)
    return entities, issues, parsed_blocks


def jsonld_entities(data: object) -> list[dict]:
    if isinstance(data, dict):
        graph = data.get("@graph")
        if isinstance(graph, list):
            return [entry for entry in graph if isinstance(entry, dict)]
        return [data]
    if isinstance(data, list):
        return [entry for entry in data if isinstance(entry, dict)]
    return []


def type_set(item: dict) -> set[str]:
    value = item.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {entry for entry in value if isinstance(entry, str)}
    return set()


def primary_schema_types(entities: list[dict]) -> set[str]:
    primary_entities = [entity for entity in entities if type_set(entity).intersection(PAGE_SCHEMA_TYPES)]
    if len(primary_entities) != 1:
        return set()
    return type_set(primary_entities[0])


def validate_positions(path: str, label: str, items: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(items, list) or not items:
        return [f"{path}: {label} should include itemListElement"]
    positions: list[int] = []
    for item in items:
        if not isinstance(item, dict):
            issues.append(f"{path}: {label} entry should be an object")
            continue
        position = item.get("position")
        if not isinstance(position, int):
            issues.append(f"{path}: {label} entry missing numeric position")
        else:
            positions.append(position)
    if positions and positions != list(range(1, len(positions) + 1)):
        issues.append(f"{path}: {label} positions should be contiguous from 1")
    return issues


def validate_schema(path: str, parser: SchemaParser, entities: list[dict], sitemap_set: set[str]) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "organizations": 0,
        "primary_entities": 0,
        "date_modified": 0,
        "breadcrumbs": 0,
        "article_entities": 0,
        "howto_entities": 0,
        "itemlists": 0,
    }
    canonical = parser.canonical

    for entity in entities:
        for schema_type in type_set(entity):
            if schema_type == "ItemList":
                stats["itemlists"] += 1

    organizations = [entity for entity in entities if "Organization" in type_set(entity)]
    stats["organizations"] = len(organizations)
    if len(organizations) != 1:
        issues.append(f"{path}: expected one Organization entity, found {len(organizations)}")
    else:
        organization = organizations[0]
        for key, expected in EXPECTED_ORGANIZATION.items():
            if organization.get(key) != expected:
                issues.append(f"{path}: Organization {key} should be {expected!r}, got {organization.get(key)!r}")
        contact_point = organization.get("contactPoint", {})
        if not isinstance(contact_point, dict) or contact_point.get("email") != EXPECTED_ORGANIZATION["email"]:
            issues.append(f"{path}: Organization contactPoint email should be contact@lovetypes.tw")

    primary_entities = [entity for entity in entities if type_set(entity).intersection(PAGE_SCHEMA_TYPES)]
    stats["primary_entities"] = len(primary_entities)
    if len(primary_entities) != 1:
        issues.append(f"{path}: expected one primary page entity, found {len(primary_entities)}")
    else:
        primary = primary_entities[0]
        primary_types = type_set(primary)
        if primary.get("url") != canonical:
            issues.append(f"{path}: primary entity url should match canonical {canonical!r}, got {primary.get('url')!r}")
        if parser.html_lang and primary.get("inLanguage") != parser.html_lang:
            issues.append(f"{path}: primary entity inLanguage should match html lang {parser.html_lang!r}")
        date_modified = primary.get("dateModified")
        if not isinstance(date_modified, str) or not date_modified:
            issues.append(f"{path}: primary entity missing dateModified")
        else:
            try:
                parsed_date_modified = date.fromisoformat(date_modified)
            except ValueError:
                issues.append(f"{path}: primary entity dateModified should be ISO date, got {date_modified!r}")
            else:
                stats["date_modified"] += 1
                if parsed_date_modified > date.today():
                    issues.append(f"{path}: primary entity dateModified should not be in the future: {date_modified}")
        if "WebSite" not in primary_types and primary.get("description") != parser.description:
            issues.append(f"{path}: primary entity description should match meta description")
        primary_name = primary.get("headline") if "Article" in primary_types else primary.get("name")
        if not primary_name:
            issues.append(f"{path}: primary entity missing name/headline")
        if "Article" in primary_types:
            stats["article_entities"] += 1
            headline = primary.get("headline")
            if headline not in {parser.title.strip(), parser.title.strip().split(" | ")[0]}:
                issues.append(f"{path}: Article headline should match page title")
            main_entity = primary.get("mainEntityOfPage")
            if not isinstance(main_entity, dict) or main_entity.get("@id") != canonical:
                issues.append(f"{path}: Article mainEntityOfPage @id should match canonical")
            for role in ("author", "publisher"):
                role_entity = primary.get(role)
                if not isinstance(role_entity, dict) or role_entity.get("@id") != EXPECTED_ORGANIZATION["@id"]:
                    issues.append(f"{path}: Article {role} should reference LoveTypes organization")
        if "HowTo" in primary_types:
            stats["howto_entities"] += 1
            steps = primary.get("step")
            issues.extend(validate_positions(path, "HowTo", steps))
            if isinstance(steps, list) and len(steps) < 2:
                issues.append(f"{path}: HowTo should include multiple steps")

    breadcrumbs = [entity for entity in entities if "BreadcrumbList" in type_set(entity)]
    stats["breadcrumbs"] = len(breadcrumbs)
    if not is_locale_home(path):
        if len(breadcrumbs) != 1:
            issues.append(f"{path}: expected one BreadcrumbList entity, found {len(breadcrumbs)}")
        else:
            items = breadcrumbs[0].get("itemListElement")
            issues.extend(validate_positions(path, "BreadcrumbList", items))
            if isinstance(items, list):
                for entry in items:
                    if not isinstance(entry, dict):
                        continue
                    if entry.get("@type") != "ListItem" or not entry.get("name"):
                        issues.append(f"{path}: BreadcrumbList entry missing ListItem type or name")
                    item_url = entry.get("item")
                    if not isinstance(item_url, str) or not item_url.startswith(DEFAULT_BASE_URL + "/"):
                        issues.append(f"{path}: BreadcrumbList item should be a LoveTypes URL, got {item_url!r}")
                    elif item_url not in sitemap_set:
                        issues.append(f"{path}: BreadcrumbList item should exist in sitemap: {item_url}")
                if items and isinstance(items[-1], dict) and items[-1].get("item") != canonical:
                    issues.append(f"{path}: BreadcrumbList final item should match canonical")
    elif breadcrumbs:
        issues.append(f"{path}: locale home should not need BreadcrumbList")
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public JSON-LD schema structure across LoveTypes sitemap pages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    locations, issues = sitemap_locations(base_url)
    sitemap_set = set(locations)
    pages_checked = 0
    jsonld_blocks_checked = 0
    organization_entities_checked = 0
    primary_entities_checked = 0
    breadcrumb_entities_checked = 0
    date_modified_entities_checked = 0
    article_entities_checked = 0
    howto_entities_checked = 0
    itemlist_entities_checked = 0
    core_page_schema_types_checked = 0
    guardian_profile_schema_types_checked = 0
    expected_core_types = expected_core_page_schema_types()
    expected_guardian_profiles = expected_guardian_profile_paths()

    for loc in locations:
        path = public_path(loc)
        response = request_url(loc)
        if response.status != 200:
            issues.append(f"{path}: expected status 200, got {response.status}")
            continue
        page_parser = SchemaParser()
        page_parser.feed(response.text)
        if page_parser.canonical != loc:
            issues.append(f"{path}: canonical should be {loc!r}, got {page_parser.canonical!r}")
        entities, parse_issues, parsed_blocks = parse_jsonld_blocks(path, page_parser.jsonld_blocks)
        issues.extend(parse_issues)
        schema_issues, stats = validate_schema(path, page_parser, entities, sitemap_set)
        issues.extend(schema_issues)
        primary_types = primary_schema_types(entities)
        expected_core_type = expected_core_types.get(path)
        if expected_core_type:
            if expected_core_type in primary_types:
                core_page_schema_types_checked += 1
            else:
                issues.append(f"{path}: primary schema type should include {expected_core_type}, got {sorted(primary_types)}")
        if path in expected_guardian_profiles:
            if "ProfilePage" in primary_types:
                guardian_profile_schema_types_checked += 1
            else:
                issues.append(f"{path}: guardian page primary schema type should include ProfilePage, got {sorted(primary_types)}")
        pages_checked += 1
        jsonld_blocks_checked += parsed_blocks
        organization_entities_checked += stats["organizations"]
        primary_entities_checked += stats["primary_entities"]
        date_modified_entities_checked += stats["date_modified"]
        breadcrumb_entities_checked += stats["breadcrumbs"]
        article_entities_checked += stats["article_entities"]
        howto_entities_checked += stats["howto_entities"]
        itemlist_entities_checked += stats["itemlists"]

    print(f"public_schema_pages_checked={pages_checked}")
    print(f"public_schema_jsonld_blocks_checked={jsonld_blocks_checked}")
    print(f"public_schema_organization_entities_checked={organization_entities_checked}")
    print(f"public_schema_primary_entities_checked={primary_entities_checked}")
    print(f"public_schema_date_modified_entities_checked={date_modified_entities_checked}")
    print(f"public_schema_breadcrumb_entities_checked={breadcrumb_entities_checked}")
    print(f"public_schema_article_entities_checked={article_entities_checked}")
    print(f"public_schema_howto_entities_checked={howto_entities_checked}")
    print(f"public_schema_itemlist_entities_checked={itemlist_entities_checked}")
    print(f"public_schema_core_page_types_checked={core_page_schema_types_checked}")
    print(f"public_schema_guardian_profile_types_checked={guardian_profile_schema_types_checked}")
    print(f"public_schema_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
