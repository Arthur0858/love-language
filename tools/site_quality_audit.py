#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lovetypes.tw"
CONTACT_EMAIL = "contact@lovetypes.tw"
FORBIDDEN_CONTACT_SNIPPETS = {
    "contact@parenttechchecklist.com",
    "parenttechchecklist.com",
    "s755102@gmail.com",
}
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
EXPECTED_HREFLANGS = {"zh-TW", "en", "ja", "ko", "es", "x-default"}
EXPECTED_OG_LOCALES = {
    "zh-TW": "zh_TW",
    "en": "en_US",
    "ja": "ja_JP",
    "ko": "ko_KR",
    "es": "es_ES",
}
SITEMAP_PATH = ROOT / "sitemap.xml"
ROBOTS_PATH = ROOT / "robots.txt"
FEED_PATH = ROOT / "feed.xml"
MANIFEST_PATH = ROOT / "site.webmanifest"
HEADERS_PATH = ROOT / "_headers"
REDIRECTS_PATH = ROOT / "_redirects"
SECURITY_PATH = ROOT / "security.txt"
WELL_KNOWN_SECURITY_PATH = ROOT / ".well-known" / "security.txt"
SITEMAP_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}
REQUIRED_HEAD_ASSETS = {
    "icon": "/favicon.ico",
    "apple-touch-icon": "/apple-touch-icon.png",
    "manifest": "/site.webmanifest",
}
REQUIRED_MANIFEST_FIELDS = {
    "name",
    "short_name",
    "description",
    "start_url",
    "scope",
    "display",
    "background_color",
    "theme_color",
    "icons",
}
REQUIRED_GLOBAL_HEADERS = {
    "Cache-Control": "public, max-age=600",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "SAMEORIGIN",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Strict-Transport-Security": "max-age=31536000",
}
IMMUTABLE_HEADER_PATHS = {
    "/assets/*",
    "/shared-*.css",
    "/site-interactions-*.js",
    "/deferred-external-*.js",
}
EXPECTED_REDIRECTS = {
    "/.well-known/security.txt": ("/security.txt", "200"),
    "/luna/": ("/luna-yoga-music/", "301"),
    "/en/luna/": ("/en/luna-yoga-music/", "301"),
    "/ja/luna/": ("/ja/luna-yoga-music/", "301"),
    "/ko/luna/": ("/ko/luna-yoga-music/", "301"),
    "/es/luna/": ("/es/luna-yoga-music/", "301"),
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
EXPECTED_ORGANIZATION = {
    "@id": f"{DOMAIN}/#organization",
    "name": "LoveTypes",
    "url": f"{DOMAIN}/",
    "logo": f"{DOMAIN}/apple-touch-icon.png",
    "email": CONTACT_EMAIL,
}
POLICY_PAGE_SLUGS = {"contact", "privacy", "terms"}
LOCALE_PREFIXES = {"zh": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []
        self.anchors: list[dict[str, str]] = []
        self.buttons: list[list[object]] = []
        self.controls: list[tuple[str, dict[str, str]]] = []
        self.headings: list[tuple[int, str, bool]] = []
        self.images: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.mains: list[dict[str, str]] = []
        self.navs: list[dict[str, str]] = []
        self.details: list[dict[str, str]] = []
        self.summaries: list[list[object]] = []
        self.ids: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.tag_counts = Counter()
        self.source = ""
        self.title_parts: list[str] = []
        self.jsonld_blocks: list[str] = []
        self.html_lang: str | None = None
        self._stack: list[tuple[str, dict[str, str], list[str]]] = []
        self._in_title = False
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        self.tag_counts[tag] += 1
        self._stack.append((tag, data, []))
        if tag == "html":
            self.html_lang = data.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "script" and data.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = []
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a":
            self.anchors.append(data)
        if tag == "button":
            self.buttons.append([data, ""])
        if tag == "main":
            self.mains.append(data)
        if tag == "nav":
            self.navs.append(data)
        if tag == "details":
            self.details.append(data)
        if tag == "summary":
            self.summaries.append([data, ""])
        if tag in ("input", "select", "textarea"):
            self.controls.append((tag, data))
        if tag == "img":
            self.images.append(data)
        if tag == "link":
            self.links.append(data)
        if tag == "meta":
            self.metas.append(data)
        for attr in ("href", "src", "poster"):
            if attr in data:
                self.refs.append((tag, attr, data[attr]))
        if tag in ("img", "source") and "srcset" in data:
            self.refs.append((tag, "srcset", data["srcset"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self.jsonld_blocks.append("".join(self._jsonld_buf))
            self._in_jsonld = False
            self._jsonld_buf = []
        if not self._stack:
            return
        current_tag, data, text_parts = self._stack.pop()
        text = "".join(text_parts).strip()
        if current_tag == "button":
            for button in reversed(self.buttons):
                if button[0] is data:
                    button[1] = text
                    break
        if current_tag == "summary":
            for summary in reversed(self.summaries):
                if summary[0] is data:
                    summary[1] = text
                    break
        if current_tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            in_main = any(stack_tag == "main" for stack_tag, _, _ in self._stack)
            self.headings.append((int(current_tag[1]), text, in_main))
        if self._stack and text:
            self._stack[-1][2].append(text)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        if self._stack:
            self._stack[-1][2].append(data)

    def meta_content(self, name: str) -> str:
        for meta in self.metas:
            if meta.get("name") == name or meta.get("property") == name:
                return meta.get("content", "")
        return ""

    def meta_contents(self, name: str) -> list[str]:
        return [
            meta.get("content", "")
            for meta in self.metas
            if meta.get("name") == name or meta.get("property") == name
        ]

    def links_with_rel(self, rel: str) -> list[dict[str, str]]:
        return [link for link in self.links if rel in link.get("rel", "").split()]


def html_pages() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)


def target_for(page: Path, value: str) -> tuple[Path | None, str]:
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        if parsed.netloc not in LOCAL_HOSTS:
            return None, parsed.fragment
        path = parsed.path or "/"
    else:
        if value.startswith("//"):
            return None, parsed.fragment
        path = parsed.path
    if path == "":
        target = page
    elif path.startswith("/"):
        clean = unquote(path.lstrip("/"))
        target = ROOT / "index.html" if clean == "" else ROOT / clean
    else:
        target = page.parent / unquote(path)
    if path.endswith("/") or path == "" or (not target.suffix and not target.exists()):
        if target.is_dir() or not target.suffix:
            target = target / "index.html"
    return target, parsed.fragment


def local_html_target_exists(page: Path, value: str, parsers: dict[Path, PageParser]) -> bool:
    target, fragment = target_for(page, value)
    if target is None:
        return True
    if not target.exists():
        return False
    if fragment and target.suffix == ".html":
        target_parser = parsers.get(target)
        return bool(target_parser and fragment in target_parser.ids)
    return True


def public_url_for_page(page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{DOMAIN}/"
    if rel.endswith("/index.html"):
        return f"{DOMAIN}/{rel[: -len('index.html')]}"
    return f"{DOMAIN}/{rel}"


def is_noindex(parser: PageParser) -> bool:
    return "noindex" in parser.meta_content("robots").lower()


def is_locale_home(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    if relative == Path("index.html"):
        return True
    return len(relative.parts) == 2 and relative.parts[1] == "index.html" and relative.parts[0] in {"en", "ja", "ko", "es"}


def class_tokens(attrs: dict[str, str]) -> set[str]:
    return set(attrs.get("class", "").split())


def jsonld_type_set(item: dict) -> set[str]:
    value = item.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {entry for entry in value if isinstance(entry, str)}
    return set()


def jsonld_entities(data: object) -> list[dict]:
    if isinstance(data, dict):
        graph = data.get("@graph")
        if isinstance(graph, list):
            return [entry for entry in graph if isinstance(entry, dict)]
        return [data]
    if isinstance(data, list):
        return [entry for entry in data if isinstance(entry, dict)]
    return []


def jsonld_target_exists(page: Path, value: object, parsers: dict[Path, PageParser]) -> bool:
    if not isinstance(value, str) or not value.startswith(f"{DOMAIN}/"):
        return False
    return local_html_target_exists(page, value, parsers)


def validate_positioned_items(page: Path, label: str, items: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(items, list) or not items:
        return [f"{page}: {label} should include a non-empty itemListElement list"]
    positions: list[int] = []
    for item in items:
        if not isinstance(item, dict):
            issues.append(f"{page}: {label} entry should be an object")
            continue
        position = item.get("position")
        if not isinstance(position, int):
            issues.append(f"{page}: {label} entry missing numeric position")
            continue
        positions.append(position)
    if positions and positions != list(range(1, len(positions) + 1)):
        issues.append(f"{page}: {label} positions should be contiguous from 1")
    return issues


def validate_jsonld(
    page: Path,
    parser: PageParser,
    page_title: str,
    page_description: str,
    canonical: str,
    entities: list[dict],
    parsers: dict[Path, PageParser],
) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    for item in entities:
        for item_type in jsonld_type_set(item):
            stats[f"jsonld_type_{item_type}"] += 1

    organizations = [item for item in entities if "Organization" in jsonld_type_set(item)]
    if len(organizations) != 1:
        issues.append(f"{page}: expected one Organization JSON-LD entity, found {len(organizations)}")
    elif any(organizations[0].get(key) != value for key, value in EXPECTED_ORGANIZATION.items()):
        issues.append(f"{page}: Organization JSON-LD does not match canonical LoveTypes identity")
    else:
        contact_point = organizations[0].get("contactPoint", {})
        if not isinstance(contact_point, dict) or contact_point.get("email") != EXPECTED_ORGANIZATION["email"]:
            issues.append(f"{page}: Organization contactPoint email should be contact@lovetypes.tw")
        for key in ("logo", "publishingPrinciples", "privacyPolicy"):
            if key in organizations[0] and not jsonld_target_exists(page, organizations[0][key], parsers):
                issues.append(f"{page}: Organization JSON-LD {key} target missing: {organizations[0][key]}")

    primary_entities = [item for item in entities if jsonld_type_set(item).intersection(PAGE_SCHEMA_TYPES)]
    if page.name != "404.html":
        if len(primary_entities) != 1:
            issues.append(f"{page}: expected one primary page JSON-LD entity, found {len(primary_entities)}")
        else:
            primary = primary_entities[0]
            primary_types = jsonld_type_set(primary)
            stats["primary_jsonld_entities"] += 1
            if primary.get("url") != canonical:
                issues.append(f"{page}: primary JSON-LD url should match canonical: {canonical}")
            if parser.html_lang and primary.get("inLanguage") != parser.html_lang:
                issues.append(f"{page}: primary JSON-LD inLanguage should match html lang {parser.html_lang}")
            primary_name = primary.get("headline") if "Article" in primary_types else primary.get("name")
            if not primary_name:
                issues.append(f"{page}: primary JSON-LD missing name/headline")
            if "WebSite" not in primary_types and primary.get("description") != page_description:
                issues.append(f"{page}: primary JSON-LD description should match meta description")
            if "Article" in primary_types:
                if primary.get("headline") not in {page_title, page_title.split(" | ")[0]}:
                    issues.append(f"{page}: Article headline should match page title")
                main_entity = primary.get("mainEntityOfPage", {})
                if not isinstance(main_entity, dict) or main_entity.get("@id") != canonical:
                    issues.append(f"{page}: Article mainEntityOfPage @id should match canonical")
                for role in ("author", "publisher"):
                    role_entity = primary.get(role, {})
                    if not isinstance(role_entity, dict) or role_entity.get("@id") != EXPECTED_ORGANIZATION["@id"]:
                        issues.append(f"{page}: Article {role} should reference LoveTypes organization")
            if "HowTo" in primary_types:
                steps = primary.get("step")
                if not isinstance(steps, list) or len(steps) < 2:
                    issues.append(f"{page}: HowTo JSON-LD should include multiple steps")
                else:
                    positions = []
                    for step in steps:
                        if not isinstance(step, dict):
                            issues.append(f"{page}: HowTo step should be an object")
                            continue
                        if step.get("@type") != "HowToStep":
                            issues.append(f"{page}: HowTo step should use @type=HowToStep")
                        if not step.get("name") or not step.get("text"):
                            issues.append(f"{page}: HowTo step missing name or text")
                        if isinstance(step.get("position"), int):
                            positions.append(step["position"])
                    if positions != list(range(1, len(steps) + 1)):
                        issues.append(f"{page}: HowTo step positions should be contiguous from 1")
            image = primary.get("image")
            if image and not jsonld_target_exists(page, image, parsers):
                issues.append(f"{page}: primary JSON-LD image target missing: {image}")

    breadcrumbs = [item for item in entities if "BreadcrumbList" in jsonld_type_set(item)]
    if not is_locale_home(page) and page.name != "404.html":
        if len(breadcrumbs) != 1:
            issues.append(f"{page}: expected one BreadcrumbList JSON-LD entity, found {len(breadcrumbs)}")
        else:
            elements = breadcrumbs[0].get("itemListElement")
            issues.extend(validate_positioned_items(page, "BreadcrumbList", elements))
            if isinstance(elements, list):
                for entry in elements:
                    if not isinstance(entry, dict):
                        continue
                    if entry.get("@type") != "ListItem" or not entry.get("name"):
                        issues.append(f"{page}: BreadcrumbList entry missing ListItem type or name")
                    if not jsonld_target_exists(page, entry.get("item"), parsers):
                        issues.append(f"{page}: BreadcrumbList target missing: {entry.get('item')}")

    item_lists = [item for item in entities if "ItemList" in jsonld_type_set(item)]
    for item_list in item_lists:
        elements = item_list.get("itemListElement")
        issues.extend(validate_positioned_items(page, "ItemList", elements))
        urls: list[str] = []
        if isinstance(elements, list):
            for entry in elements:
                if not isinstance(entry, dict):
                    continue
                url = entry.get("url")
                if not jsonld_target_exists(page, url, parsers):
                    issues.append(f"{page}: ItemList URL target missing: {url}")
                elif isinstance(url, str):
                    urls.append(url)
        duplicates = [url for url, count in Counter(urls).items() if count > 1]
        if duplicates:
            issues.append(f"{page}: ItemList duplicate URL(s): {', '.join(duplicates[:5])}")

    return issues, stats


def local_path_for_public_url(value: str) -> Path | None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw":
        return None
    clean = unquote(parsed.path.lstrip("/"))
    return ROOT / clean if clean else ROOT / "index.html"


def image_size(path: Path) -> tuple[int, int] | None:
    try:
        with Image.open(path) as image:
            return image.size
    except OSError:
        return None


def parse_manifest() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not MANIFEST_PATH.exists():
        return [f"{MANIFEST_PATH}: missing site.webmanifest"], stats

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_PATH}: invalid JSON: {exc}"], stats

    missing_fields = sorted(field for field in REQUIRED_MANIFEST_FIELDS if not manifest.get(field))
    if missing_fields:
        issues.append(f"{MANIFEST_PATH}: missing required fields {', '.join(missing_fields)}")
    if manifest.get("start_url") != "/":
        issues.append(f"{MANIFEST_PATH}: start_url should be /")
    if manifest.get("scope") != "/":
        issues.append(f"{MANIFEST_PATH}: scope should be /")
    if manifest.get("display") not in {"standalone", "fullscreen", "minimal-ui", "browser"}:
        issues.append(f"{MANIFEST_PATH}: invalid display value {manifest.get('display')}")
    if manifest.get("lang") != "zh-TW":
        issues.append(f"{MANIFEST_PATH}: lang should be zh-TW")

    icons = manifest.get("icons")
    if not isinstance(icons, list) or not icons:
        issues.append(f"{MANIFEST_PATH}: icons should be a non-empty list")
        icons = []
    for icon in icons:
        stats["manifest_icons"] += 1
        if not isinstance(icon, dict):
            issues.append(f"{MANIFEST_PATH}: icon entry should be an object")
            continue
        src = icon.get("src", "")
        sizes = icon.get("sizes", "")
        icon_type = icon.get("type", "")
        if not src or not sizes or not icon_type:
            issues.append(f"{MANIFEST_PATH}: icon missing src, sizes, or type: {icon}")
            continue
        target = ROOT / unquote(src.lstrip("/"))
        if not target.exists():
            issues.append(f"{MANIFEST_PATH}: icon target missing: {src}")
            continue
        if icon_type == "image/png":
            size = image_size(target)
            declared_sizes = [part for part in sizes.split() if "x" in part]
            if not declared_sizes:
                issues.append(f"{MANIFEST_PATH}: png icon missing concrete sizes: {src}")
            for declared in declared_sizes:
                try:
                    declared_width, declared_height = [int(part) for part in declared.split("x", 1)]
                except ValueError:
                    issues.append(f"{MANIFEST_PATH}: invalid icon size {declared}: {src}")
                    continue
                if size and size != (declared_width, declared_height):
                    issues.append(
                        f"{MANIFEST_PATH}: icon size {declared} does not match file {size[0]}x{size[1]}: {src}"
                    )
        elif icon_type == "image/x-icon":
            try:
                with Image.open(target) as image:
                    actual_sizes = image.ico.sizes() if hasattr(image, "ico") else {image.size}
            except OSError:
                issues.append(f"{MANIFEST_PATH}: cannot read icon file: {src}")
                continue
            for declared in [part for part in sizes.split() if "x" in part]:
                try:
                    declared_size = tuple(int(part) for part in declared.split("x", 1))
                except ValueError:
                    issues.append(f"{MANIFEST_PATH}: invalid icon size {declared}: {src}")
                    continue
                if declared_size not in actual_sizes:
                    issues.append(f"{MANIFEST_PATH}: ico missing declared size {declared}: {src}")

    shortcuts = manifest.get("shortcuts", [])
    if shortcuts and not isinstance(shortcuts, list):
        issues.append(f"{MANIFEST_PATH}: shortcuts should be a list")
        shortcuts = []
    for shortcut in shortcuts:
        stats["manifest_shortcuts"] += 1
        if not isinstance(shortcut, dict):
            issues.append(f"{MANIFEST_PATH}: shortcut entry should be an object")
            continue
        if not shortcut.get("name") or not shortcut.get("url"):
            issues.append(f"{MANIFEST_PATH}: shortcut missing name or url: {shortcut}")
            continue
        target, fragment = target_for(ROOT / "index.html", shortcut["url"])
        if target is None or not target.exists():
            issues.append(f"{MANIFEST_PATH}: shortcut target missing: {shortcut['url']}")
        elif fragment and target.suffix == ".html":
            parser = PageParser()
            parser.feed(target.read_text(encoding="utf-8", errors="ignore"))
            if fragment not in parser.ids:
                issues.append(f"{MANIFEST_PATH}: shortcut anchor missing #{fragment}: {shortcut['url']}")

    return issues, stats


def parse_feed(parsers: dict[Path, PageParser], sitemap_urls: set[str]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not FEED_PATH.exists():
        return [f"{FEED_PATH}: missing feed.xml"], stats

    try:
        root = ET.parse(FEED_PATH).getroot()
    except ET.ParseError as exc:
        return [f"{FEED_PATH}: invalid XML: {exc}"], stats
    if root.tag != "rss" or root.attrib.get("version") != "2.0":
        issues.append(f"{FEED_PATH}: expected rss version 2.0")

    channel = root.find("channel")
    if channel is None:
        return [f"{FEED_PATH}: missing channel"], stats
    for tag in ("title", "link", "description", "language", "lastBuildDate"):
        if not (channel.findtext(tag) or "").strip():
            issues.append(f"{FEED_PATH}: channel missing {tag}")
    if channel.findtext("language") != "zh-TW":
        issues.append(f"{FEED_PATH}: channel language should be zh-TW")
    if channel.findtext("link") != f"{DOMAIN}/guides/":
        issues.append(f"{FEED_PATH}: channel link should be {DOMAIN}/guides/")

    seen_links: set[str] = set()
    items = channel.findall("item")
    stats["feed_items"] = len(items)
    if len(items) < 10:
        issues.append(f"{FEED_PATH}: expected at least 10 feed items, found {len(items)}")
    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or "").strip()
        description = (item.findtext("description") or "").strip()
        category = (item.findtext("category") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        if not title or not link or not guid or not description or not category or not pub_date:
            issues.append(f"{FEED_PATH}: feed item missing required fields: {link or title or '<unknown>'}")
        if link in seen_links:
            issues.append(f"{FEED_PATH}: duplicate feed item link: {link}")
        seen_links.add(link)
        guid_node = item.find("guid")
        if guid_node is None or guid_node.attrib.get("isPermaLink") != "true":
            issues.append(f"{FEED_PATH}: guid should use isPermaLink=true: {link}")
        if guid and guid != link:
            issues.append(f"{FEED_PATH}: guid should match link: {link}")
        parsed_link = urlparse(link)
        if parsed_link.scheme != "https" or parsed_link.netloc != "lovetypes.tw":
            issues.append(f"{FEED_PATH}: item link must be absolute https lovetypes.tw URL: {link}")
        target, _ = target_for(ROOT / "index.html", link)
        if target is None or not target.exists():
            issues.append(f"{FEED_PATH}: item link target missing: {link}")
        else:
            target_parser = parsers.get(target)
            if target_parser and is_noindex(target_parser):
                issues.append(f"{FEED_PATH}: feed item should not point to noindex page: {link}")
            canonicals = target_parser.links_with_rel("canonical") if target_parser else []
            if len(canonicals) == 1 and canonicals[0].get("href") != link:
                issues.append(f"{FEED_PATH}: item link should match target canonical: {link}")
        if link and link not in sitemap_urls:
            issues.append(f"{FEED_PATH}: feed item link missing from sitemap: {link}")

    return issues, stats


def parse_headers() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not HEADERS_PATH.exists():
        return [f"{HEADERS_PATH}: missing _headers"], stats

    blocks: dict[str, list[tuple[str, str | None, bool]]] = {}
    current_path = ""
    for lineno, raw_line in enumerate(HEADERS_PATH.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith((" ", "\t")):
            if not current_path:
                issues.append(f"{HEADERS_PATH}:{lineno}: header rule appears before path")
                continue
            line = raw_line.strip()
            remove = line.startswith("!")
            if remove:
                name = line[1:].strip()
                value = None
            elif ":" in line:
                name, value = [part.strip() for part in line.split(":", 1)]
            else:
                issues.append(f"{HEADERS_PATH}:{lineno}: invalid header rule: {line}")
                continue
            if not name:
                issues.append(f"{HEADERS_PATH}:{lineno}: empty header name")
                continue
            blocks.setdefault(current_path, []).append((name, value, remove))
            stats["header_rules"] += 1
        else:
            current_path = raw_line.strip()
            if current_path in blocks:
                issues.append(f"{HEADERS_PATH}:{lineno}: duplicate header path: {current_path}")
            blocks.setdefault(current_path, [])
            stats["header_blocks"] += 1

    global_headers = {
        name: value
        for name, value, remove in blocks.get("/*", [])
        if not remove and value is not None
    }
    for name, expected_value in REQUIRED_GLOBAL_HEADERS.items():
        actual_value = global_headers.get(name)
        if actual_value != expected_value:
            issues.append(f"{HEADERS_PATH}: /* missing {name}: {expected_value}")

    for path in IMMUTABLE_HEADER_PATHS:
        rules = blocks.get(path)
        if not rules:
            issues.append(f"{HEADERS_PATH}: missing immutable cache block for {path}")
            continue
        has_cache_remove = any(name.lower() == "cache-control" and remove for name, _, remove in rules)
        has_immutable = any(
            name.lower() == "cache-control" and value == "public, max-age=31536000, immutable" and not remove
            for name, value, remove in rules
        )
        if not has_cache_remove:
            issues.append(f"{HEADERS_PATH}: {path} should clear inherited Cache-Control before setting immutable cache")
        if not has_immutable:
            issues.append(f"{HEADERS_PATH}: {path} missing immutable Cache-Control")

    for preview_path in ("https://lovetypes.pages.dev/*", "https://:version.lovetypes.pages.dev/*"):
        rules = blocks.get(preview_path)
        if not rules:
            issues.append(f"{HEADERS_PATH}: missing preview noindex block for {preview_path}")
            continue
        if not any(name == "X-Robots-Tag" and value == "noindex" and not remove for name, value, remove in rules):
            issues.append(f"{HEADERS_PATH}: {preview_path} missing X-Robots-Tag: noindex")

    return issues, stats


def parse_redirects(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not REDIRECTS_PATH.exists():
        return [f"{REDIRECTS_PATH}: missing _redirects"], stats

    redirects: dict[str, tuple[str, str]] = {}
    for lineno, raw_line in enumerate(REDIRECTS_PATH.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 3:
            issues.append(f"{REDIRECTS_PATH}:{lineno}: expected source target status")
            continue
        source, target, status = parts
        if source in redirects:
            issues.append(f"{REDIRECTS_PATH}:{lineno}: duplicate redirect source: {source}")
        redirects[source] = (target, status)
        stats["redirect_rules"] += 1

        if status not in {"200", "301", "302", "307", "308"}:
            issues.append(f"{REDIRECTS_PATH}:{lineno}: unexpected redirect status {status}: {source}")
        target_path, target_fragment = target_for(ROOT / "index.html", target)
        if target_path is None or not target_path.exists():
            issues.append(f"{REDIRECTS_PATH}:{lineno}: redirect target missing: {target}")
        elif target_fragment and target_path.suffix == ".html":
            target_parser = parsers.get(target_path)
            if target_parser and target_fragment not in target_parser.ids:
                issues.append(f"{REDIRECTS_PATH}:{lineno}: redirect target anchor missing #{target_fragment}: {target}")

    for source, expected in EXPECTED_REDIRECTS.items():
        actual = redirects.get(source)
        if actual != expected:
            issues.append(f"{REDIRECTS_PATH}: missing redirect {source} {expected[0]} {expected[1]}")

    for source, (target, status) in redirects.items():
        if source.endswith("/luna/"):
            source_path, _ = target_for(ROOT / "index.html", source)
            if source_path is None or not source_path.exists():
                issues.append(f"{REDIRECTS_PATH}: luna alias source page missing: {source}")
            else:
                source_parser = parsers.get(source_path)
                if source_parser and not is_noindex(source_parser):
                    issues.append(f"{REDIRECTS_PATH}: luna alias source should be noindex: {source}")
            if not target.endswith("/luna-yoga-music/") or status != "301":
                issues.append(f"{REDIRECTS_PATH}: luna alias should be a 301 to luna-yoga-music: {source}")

    return issues, stats


def parse_security_txt(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not SECURITY_PATH.exists():
        return [f"{SECURITY_PATH}: missing security.txt"], stats
    if not WELL_KNOWN_SECURITY_PATH.exists():
        issues.append(f"{WELL_KNOWN_SECURITY_PATH}: missing .well-known security.txt")

    security_text = SECURITY_PATH.read_text(encoding="utf-8", errors="ignore").strip()
    stats["security_txt_files"] += 1
    if WELL_KNOWN_SECURITY_PATH.exists():
        well_known_text = WELL_KNOWN_SECURITY_PATH.read_text(encoding="utf-8", errors="ignore").strip()
        stats["security_txt_files"] += 1
        if well_known_text != security_text:
            issues.append(f"{WELL_KNOWN_SECURITY_PATH}: should match root security.txt")

    fields: dict[str, list[str]] = {}
    for lineno, raw_line in enumerate(security_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            issues.append(f"{SECURITY_PATH}:{lineno}: invalid security.txt line")
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        fields.setdefault(key.lower(), []).append(value)
        stats["security_txt_fields"] += 1

    expected_fields = {
        "contact": f"mailto:{CONTACT_EMAIL}",
        "canonical": f"{DOMAIN}/.well-known/security.txt",
        "policy": f"{DOMAIN}/privacy/",
    }
    for key, expected_value in expected_fields.items():
        if expected_value not in fields.get(key, []):
            issues.append(f"{SECURITY_PATH}: missing {key.title()}: {expected_value}")
    if not any("zh-TW" in value and "en" in value for value in fields.get("preferred-languages", [])):
        issues.append(f"{SECURITY_PATH}: Preferred-Languages should include zh-TW and en")
    expires_values = fields.get("expires", [])
    if len(expires_values) != 1:
        issues.append(f"{SECURITY_PATH}: expected one Expires field, found {len(expires_values)}")
    else:
        try:
            expires = datetime.fromisoformat(expires_values[0].replace("Z", "+00:00"))
        except ValueError:
            issues.append(f"{SECURITY_PATH}: invalid Expires timestamp: {expires_values[0]}")
        else:
            if expires <= datetime.now(timezone.utc):
                issues.append(f"{SECURITY_PATH}: Expires timestamp is in the past: {expires_values[0]}")

    policy_path, _ = target_for(ROOT / "index.html", f"{DOMAIN}/privacy/")
    if policy_path is None or policy_path not in parsers:
        issues.append(f"{SECURITY_PATH}: Policy target missing: {DOMAIN}/privacy/")
    return issues, stats


def check_policy_pages(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    for _lang, prefix in LOCALE_PREFIXES.items():
        for slug in POLICY_PAGE_SLUGS:
            path = ROOT / (f"{prefix}/{slug}/index.html" if prefix else f"{slug}/index.html")
            parser = parsers.get(path)
            if parser is None:
                issues.append(f"{path}: missing {slug} policy page")
                continue
            stats["policy_pages"] += 1
            if CONTACT_EMAIL not in parser.source:
                issues.append(f"{path}: policy page missing contact email {CONTACT_EMAIL}")
            for forbidden in FORBIDDEN_CONTACT_SNIPPETS:
                if forbidden.lower() in parser.source.lower():
                    issues.append(f"{path}: forbidden legacy contact reference: {forbidden}")
            if slug == "contact":
                contact_mailtos = [
                    anchor.get("href", "")
                    for anchor in parser.anchors
                    if anchor.get("href", "").lower().startswith(f"mailto:{CONTACT_EMAIL}")
                ]
                if not contact_mailtos:
                    issues.append(f"{path}: contact page missing mailto:{CONTACT_EMAIL}")
    return issues, stats


def check_static_asset_refs(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    referenced: set[str] = set()
    for parser in parsers.values():
        for _tag, attr, raw in parser.refs:
            values = [raw]
            if attr == "srcset":
                values = [part.strip().split()[0] for part in raw.split(",") if part.strip()]
            for value in values:
                parsed = urlparse(value)
                if parsed.scheme in ("http", "https") and parsed.netloc not in LOCAL_HOSTS:
                    continue
                path = parsed.path if parsed.scheme else value
                name = Path(unquote(path)).name
                if name:
                    referenced.add(name)

    patterns = (
        ("shared-", ".css"),
        ("site-interactions-", ".js"),
        ("deferred-external-", ".js"),
    )
    for asset in sorted(ROOT.iterdir()):
        if not asset.is_file():
            continue
        if not any(asset.name.startswith(prefix) and asset.name.endswith(suffix) for prefix, suffix in patterns):
            continue
        stats["versioned_static_assets"] += 1
        if asset.name not in referenced:
            issues.append(f"{asset}: versioned static asset is not referenced by any generated HTML page")
    return issues, stats


def parse_sitemap(parsers: dict[Path, PageParser]) -> tuple[set[str], list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not SITEMAP_PATH.exists():
        return set(), [f"{SITEMAP_PATH}: missing sitemap.xml"], stats

    try:
        root = ET.parse(SITEMAP_PATH).getroot()
    except ET.ParseError as exc:
        return set(), [f"{SITEMAP_PATH}: invalid XML: {exc}"], stats

    if root.tag != f"{{{SITEMAP_NS['sm']}}}urlset":
        issues.append(f"{SITEMAP_PATH}: root element should be urlset")

    urls: set[str] = set()
    for url_node in root.findall("sm:url", SITEMAP_NS):
        loc_nodes = url_node.findall("sm:loc", SITEMAP_NS)
        if len(loc_nodes) != 1:
            issues.append(f"{SITEMAP_PATH}: expected one loc per url entry, found {len(loc_nodes)}")
            continue

        loc = (loc_nodes[0].text or "").strip()
        stats["sitemap_urls"] += 1
        parsed_loc = urlparse(loc)
        if parsed_loc.scheme != "https" or parsed_loc.netloc != "lovetypes.tw":
            issues.append(f"{SITEMAP_PATH}: loc must be absolute https lovetypes.tw URL: {loc}")
        if parsed_loc.fragment:
            issues.append(f"{SITEMAP_PATH}: loc should not contain fragment: {loc}")
        if loc in urls:
            issues.append(f"{SITEMAP_PATH}: duplicate loc: {loc}")
        urls.add(loc)

        target, _ = target_for(ROOT / "index.html", loc)
        if target is None or not target.exists():
            issues.append(f"{SITEMAP_PATH}: loc target missing: {loc}")

        if url_node.find("sm:lastmod", SITEMAP_NS) is None:
            issues.append(f"{SITEMAP_PATH}: missing lastmod for {loc}")
        if url_node.find("sm:changefreq", SITEMAP_NS) is None:
            issues.append(f"{SITEMAP_PATH}: missing changefreq for {loc}")
        priority_node = url_node.find("sm:priority", SITEMAP_NS)
        if priority_node is None:
            issues.append(f"{SITEMAP_PATH}: missing priority for {loc}")
        else:
            try:
                priority = float((priority_node.text or "").strip())
            except ValueError:
                issues.append(f"{SITEMAP_PATH}: invalid priority for {loc}")
            else:
                if not 0 <= priority <= 1:
                    issues.append(f"{SITEMAP_PATH}: priority out of range for {loc}")

        alternates = url_node.findall("xhtml:link", SITEMAP_NS)
        stats["sitemap_alternates"] += len(alternates)
        hreflang_map: dict[str, str] = {}
        for link in alternates:
            if link.attrib.get("rel") != "alternate":
                issues.append(f"{SITEMAP_PATH}: sitemap xhtml link must use rel=alternate for {loc}")
            hreflang = link.attrib.get("hreflang", "")
            href = link.attrib.get("href", "")
            if hreflang in hreflang_map:
                issues.append(f"{SITEMAP_PATH}: duplicate sitemap hreflang {hreflang} for {loc}")
            hreflang_map[hreflang] = href
            parsed_href = urlparse(href)
            if parsed_href.scheme != "https" or parsed_href.netloc != "lovetypes.tw":
                issues.append(f"{SITEMAP_PATH}: alternate href must be absolute https lovetypes.tw URL: {href}")
            href_target, _ = target_for(ROOT / "index.html", href)
            if href_target is None or not href_target.exists():
                issues.append(f"{SITEMAP_PATH}: alternate href target missing: {href}")
            elif href_target.suffix == ".html" and is_noindex(parsers.get(href_target, PageParser())):
                issues.append(f"{SITEMAP_PATH}: alternate href points to noindex page: {href}")

        missing_hreflangs = sorted(EXPECTED_HREFLANGS.difference(hreflang_map))
        extra_hreflangs = sorted(set(hreflang_map).difference(EXPECTED_HREFLANGS))
        if missing_hreflangs:
            issues.append(f"{SITEMAP_PATH}: missing sitemap hreflang alternates for {loc}: {', '.join(missing_hreflangs)}")
        if extra_hreflangs:
            issues.append(f"{SITEMAP_PATH}: unexpected sitemap hreflang alternates for {loc}: {', '.join(extra_hreflangs)}")
        if hreflang_map.get("x-default") and hreflang_map.get("zh-TW") and hreflang_map["x-default"] != hreflang_map["zh-TW"]:
            issues.append(f"{SITEMAP_PATH}: x-default sitemap alternate should match zh-TW for {loc}")

    return urls, issues, stats


def check_robots(sitemap_urls: set[str]) -> list[str]:
    issues: list[str] = []
    if not ROBOTS_PATH.exists():
        return [f"{ROBOTS_PATH}: missing robots.txt"]
    lines = [line.strip() for line in ROBOTS_PATH.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    current_agents: list[str] = []
    current_directives: list[tuple[str, str]] = []
    for line in lines:
        if line.startswith("#") or ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        key = key.lower()
        value_lower = value.lower()
        if key == "user-agent":
            if current_directives:
                groups.append((current_agents, current_directives))
                current_agents = []
                current_directives = []
            current_agents.append(value_lower)
        else:
            current_directives.append((key, value_lower))
    if current_agents or current_directives:
        groups.append((current_agents, current_directives))

    wildcard_directives = [directives for agents, directives in groups if "*" in agents]
    if not wildcard_directives:
        issues.append(f"{ROBOTS_PATH}: missing User-agent: *")
    if not any(("allow", "/") in directives for directives in wildcard_directives):
        issues.append(f"{ROBOTS_PATH}: missing Allow: /")
    if any(("disallow", "/") in directives for directives in wildcard_directives):
        issues.append(f"{ROBOTS_PATH}: User-agent: * should not globally disallow /")
    sitemap_line = f"Sitemap: {DOMAIN}/sitemap.xml"
    if sitemap_line not in lines:
        issues.append(f"{ROBOTS_PATH}: missing exact sitemap declaration {sitemap_line}")
    if not sitemap_urls:
        issues.append(f"{ROBOTS_PATH}: referenced sitemap has no URLs")
    return issues


def main() -> int:
    pages = html_pages()
    parsers: dict[Path, PageParser] = {}
    issues: list[str] = []
    stats = Counter()

    for page in pages:
        parser = PageParser()
        parser.source = page.read_text(encoding="utf-8", errors="ignore")
        parser.feed(parser.source)
        parsers[page] = parser

    for page, parser in parsers.items():
        stats["pages"] += 1
        stats["images"] += len(parser.images)
        stats["jsonld_blocks"] += len(parser.jsonld_blocks)
        stats["h1_tags"] += sum(1 for level, _, _ in parser.headings if level == 1)
        stats["main_landmarks"] += len(parser.mains)
        stats["nav_landmarks"] += len(parser.navs)
        if is_noindex(parser):
            stats["noindex_pages"] += 1
        else:
            stats["indexable_pages"] += 1

        if not "".join(parser.title_parts).strip():
            issues.append(f"{page}: missing <title>")
        if not parser.meta_content("description"):
            issues.append(f"{page}: missing meta description")
        if not parser.meta_content("robots"):
            issues.append(f"{page}: missing robots meta")
        if not parser.html_lang:
            issues.append(f"{page}: missing html lang")

        page_title = "".join(parser.title_parts).strip()
        page_description = parser.meta_content("description")

        if len(parser.mains) != 1:
            issues.append(f"{page}: expected one <main> landmark, found {len(parser.mains)}")
        elif parser.mains[0].get("id") != "main":
            issues.append(f"{page}: <main> should use id=\"main\" for the skip link target")

        skip_links = [anchor for anchor in parser.anchors if "skip-link" in class_tokens(anchor)]
        if not skip_links:
            issues.append(f"{page}: missing skip link")
        for anchor in skip_links:
            href = anchor.get("href", "")
            if not href.startswith("#"):
                issues.append(f"{page}: skip link should point to a same-page anchor: {href}")
            elif href[1:] not in parser.ids:
                issues.append(f"{page}: skip link target missing: {href}")

        h1s = [(text, in_main) for level, text, in_main in parser.headings if level == 1]
        if len(h1s) != 1:
            issues.append(f"{page}: expected one <h1>, found {len(h1s)}")
        elif not h1s[0][1]:
            issues.append(f"{page}: <h1> should be inside <main>")

        previous_level = 0
        for level, text, _ in parser.headings:
            if previous_level and level > previous_level + 1:
                label = text[:60] or f"h{level}"
                issues.append(f"{page}: heading level jumps from h{previous_level} to h{level}: {label}")
            previous_level = level

        primary_navs = [nav for nav in parser.navs if "nav-links" in class_tokens(nav)]
        if len(primary_navs) != 1:
            issues.append(f"{page}: expected one primary navigation, found {len(primary_navs)}")
        elif not primary_navs[0].get("aria-label"):
            issues.append(f"{page}: primary navigation missing aria-label")

        language_details = [details for details in parser.details if "language-menu" in class_tokens(details)]
        if len(language_details) != 1:
            issues.append(f"{page}: expected one language menu, found {len(language_details)}")
        language_summaries = [summary for summary in parser.summaries if summary[0].get("aria-label")]
        if not language_summaries:
            issues.append(f"{page}: language menu summary missing accessible label")
        language_links = [anchor for anchor in parser.anchors if anchor.get("lang") in {code for code in EXPECTED_HREFLANGS if code != "x-default"}]
        stats["language_menu_links"] += len(language_links)
        language_link_codes = [anchor.get("lang", "") for anchor in language_links]
        expected_language_codes = {code for code in EXPECTED_HREFLANGS if code != "x-default"}
        missing_language_codes = sorted(expected_language_codes.difference(language_link_codes))
        duplicate_language_codes = [value for value, count in Counter(language_link_codes).items() if count > 1]
        if missing_language_codes:
            issues.append(f"{page}: language menu missing links for {', '.join(missing_language_codes)}")
        if duplicate_language_codes:
            issues.append(f"{page}: duplicate language menu links for {', '.join(duplicate_language_codes)}")
        current_language_links = [anchor for anchor in language_links if anchor.get("aria-current") == "page"]
        if len(current_language_links) != 1:
            issues.append(f"{page}: expected one current language menu link, found {len(current_language_links)}")
        elif parser.html_lang and current_language_links[0].get("lang") != parser.html_lang:
            issues.append(f"{page}: current language menu link should match html lang {parser.html_lang}")

        breadcrumbs = [nav for nav in parser.navs if "breadcrumb" in class_tokens(nav)]
        if not is_locale_home(page) and page.name != "404.html":
            if len(breadcrumbs) != 1:
                issues.append(f"{page}: expected one breadcrumb navigation, found {len(breadcrumbs)}")
            elif not breadcrumbs[0].get("aria-label"):
                issues.append(f"{page}: breadcrumb navigation missing aria-label")

        for rel, href in REQUIRED_HEAD_ASSETS.items():
            matching_links = [link for link in parser.links_with_rel(rel) if link.get("href") == href]
            if not matching_links:
                issues.append(f"{page}: missing head asset link rel={rel} href={href}")
            else:
                stats["head_asset_links"] += 1
            target, _ = target_for(page, href)
            if target is None or not target.exists():
                issues.append(f"{page}: head asset target missing: {href}")

        rss_links = [
            link
            for link in parser.links_with_rel("alternate")
            if link.get("type") == "application/rss+xml" and link.get("href") == "/feed.xml"
        ]
        if not rss_links:
            issues.append(f"{page}: missing RSS alternate link")
        else:
            stats["rss_head_links"] += 1
            if not rss_links[0].get("title"):
                issues.append(f"{page}: RSS alternate link missing title")
        rss_target, _ = target_for(page, "/feed.xml")
        if rss_target is None or not rss_target.exists():
            issues.append(f"{page}: RSS target missing: /feed.xml")

        canonicals = parser.links_with_rel("canonical")
        canonical_url = canonicals[0].get("href", "") if len(canonicals) == 1 else public_url_for_page(page)
        stats["canonical_links"] += len(canonicals)
        if len(canonicals) != 1:
            issues.append(f"{page}: expected one canonical link, found {len(canonicals)}")
        else:
            canonical = canonicals[0].get("href", "")
            parsed_canonical = urlparse(canonical)
            if parsed_canonical.scheme != "https" or parsed_canonical.netloc != "lovetypes.tw":
                issues.append(f"{page}: canonical must be absolute https lovetypes.tw URL: {canonical}")
            if parsed_canonical.fragment:
                issues.append(f"{page}: canonical should not contain fragment: {canonical}")
            if not local_html_target_exists(page, canonical, parsers):
                issues.append(f"{page}: canonical target missing: {canonical}")
            if parser.meta_content("og:url") != canonical:
                issues.append(f"{page}: og:url does not match canonical")

        social_checks = {
            "og:type": parser.meta_content("og:type"),
            "og:title": parser.meta_content("og:title"),
            "og:description": parser.meta_content("og:description"),
            "og:image": parser.meta_content("og:image"),
            "og:image:width": parser.meta_content("og:image:width"),
            "og:image:height": parser.meta_content("og:image:height"),
            "og:locale": parser.meta_content("og:locale"),
            "twitter:card": parser.meta_content("twitter:card"),
            "twitter:image": parser.meta_content("twitter:image"),
        }
        missing_social = [key for key, value in social_checks.items() if not value]
        if missing_social:
            issues.append(f"{page}: missing social metadata {', '.join(missing_social)}")
        else:
            stats["social_cards"] += 1
            if social_checks["og:title"] != page_title:
                issues.append(f"{page}: og:title does not match <title>")
            if social_checks["og:description"] != page_description:
                issues.append(f"{page}: og:description does not match meta description")
            if social_checks["twitter:card"] != "summary_large_image":
                issues.append(f"{page}: twitter:card should be summary_large_image")
            if social_checks["twitter:image"] != social_checks["og:image"]:
                issues.append(f"{page}: twitter:image does not match og:image")
            expected_og_locale = EXPECTED_OG_LOCALES.get(parser.html_lang or "")
            if social_checks["og:locale"] != expected_og_locale:
                issues.append(f"{page}: og:locale should match html lang {parser.html_lang}: {expected_og_locale}")
            og_locale_alternates = parser.meta_contents("og:locale:alternate")
            stats["social_locale_tags"] += 1 + len(og_locale_alternates)
            expected_alternates = set(EXPECTED_OG_LOCALES.values()) - {expected_og_locale}
            alternate_counts = Counter(og_locale_alternates)
            duplicate_og_alternates = [value for value, count in alternate_counts.items() if count > 1]
            if duplicate_og_alternates:
                issues.append(f"{page}: duplicate og:locale:alternate values {', '.join(duplicate_og_alternates)}")
            if set(og_locale_alternates) != expected_alternates:
                missing = sorted(expected_alternates.difference(og_locale_alternates))
                extra = sorted(set(og_locale_alternates).difference(expected_alternates))
                if missing:
                    issues.append(f"{page}: missing og:locale:alternate values {', '.join(missing)}")
                if extra:
                    issues.append(f"{page}: unexpected og:locale:alternate values {', '.join(extra)}")

            og_image = social_checks["og:image"]
            parsed_og_image = urlparse(og_image)
            if parsed_og_image.scheme != "https" or parsed_og_image.netloc != "lovetypes.tw":
                issues.append(f"{page}: og:image must be absolute https lovetypes.tw URL: {og_image}")
            og_image_path = local_path_for_public_url(og_image)
            if og_image_path is None or not og_image_path.exists():
                issues.append(f"{page}: og:image target missing: {og_image}")
            else:
                stats["social_images"] += 1
                size = image_size(og_image_path)
                try:
                    declared_width = int(social_checks["og:image:width"])
                    declared_height = int(social_checks["og:image:height"])
                except ValueError:
                    issues.append(f"{page}: invalid og:image width/height for {og_image}")
                else:
                    if declared_width <= 0 or declared_height <= 0:
                        issues.append(f"{page}: og:image width/height should be positive for {og_image}")
                    if size and size != (declared_width, declared_height):
                        issues.append(
                            f"{page}: og:image dimensions {declared_width}x{declared_height} do not match file {size[0]}x{size[1]}: {og_image}"
                        )

        alternate_links = parser.links_with_rel("alternate")
        hreflang_links = [link for link in alternate_links if link.get("hreflang")]
        stats["hreflang_links"] += len(hreflang_links)
        hreflangs = [link.get("hreflang", "") for link in hreflang_links]
        missing_hreflangs = sorted(EXPECTED_HREFLANGS.difference(hreflangs))
        duplicate_hreflangs = [value for value, count in Counter(hreflangs).items() if count > 1]
        if missing_hreflangs:
            issues.append(f"{page}: missing hreflang alternates {', '.join(missing_hreflangs)}")
        if duplicate_hreflangs:
            issues.append(f"{page}: duplicate hreflang alternates {', '.join(duplicate_hreflangs)}")
        for link in hreflang_links:
            href = link.get("href", "")
            parsed_href = urlparse(href)
            if parsed_href.scheme != "https" or parsed_href.netloc != "lovetypes.tw":
                issues.append(f"{page}: hreflang must be absolute https lovetypes.tw URL: {href}")
            if not local_html_target_exists(page, href, parsers):
                issues.append(f"{page}: hreflang target missing: {href}")
        hreflang_map = {link.get("hreflang", ""): link.get("href", "") for link in hreflang_links}
        if hreflang_map.get("x-default") and hreflang_map.get("zh-TW") and hreflang_map["x-default"] != hreflang_map["zh-TW"]:
            issues.append(f"{page}: x-default hreflang should match zh-TW alternate")

        duplicate_ids = [value for value, count in Counter(parser.ids).items() if count > 1]
        if duplicate_ids:
            issues.append(f"{page}: duplicate ids {', '.join(duplicate_ids[:10])}")

        jsonld_page_entities: list[dict] = []
        if not parser.jsonld_blocks:
            issues.append(f"{page}: missing JSON-LD")
        for block in parser.jsonld_blocks:
            try:
                data = json.loads(block)
            except json.JSONDecodeError as exc:
                issues.append(f"{page}: invalid JSON-LD: {exc}")
                continue
            entities = jsonld_entities(data)
            if not entities:
                issues.append(f"{page}: JSON-LD block should contain an object or graph")
            jsonld_page_entities.extend(entities)
        jsonld_issues, jsonld_stats = validate_jsonld(
            page,
            parser,
            page_title,
            page_description,
            canonical_url,
            jsonld_page_entities,
            parsers,
        )
        issues.extend(jsonld_issues)
        stats.update(jsonld_stats)

        for image in parser.images:
            src = image.get("src", "")
            if "alt" not in image:
                issues.append(f"{page}: image missing alt: {src}")
            if "guardian-prop" in class_tokens(image) and not image.get("alt", "").strip():
                issues.append(f"{page}: guardian prop image should have descriptive alt: {src}")
            if not image.get("width") or not image.get("height"):
                issues.append(f"{page}: image missing width/height: {src}")
            if not image.get("decoding"):
                issues.append(f"{page}: image missing decoding: {src}")

        for attrs, text in parser.buttons:
            if not (str(text).strip() or attrs.get("aria-label") or attrs.get("title")):
                issues.append(f"{page}: button missing accessible name")

        for tag, attrs in parser.controls:
            input_type = attrs.get("type", "text")
            if input_type in ("hidden", "submit", "button"):
                continue
            if not (attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("placeholder")):
                issues.append(f"{page}: {tag} missing label hint")
            if tag == "textarea" and attrs.get("autocomplete") != "off":
                issues.append(f"{page}: textarea should use autocomplete=off")

        for anchor in parser.anchors:
            href = anchor.get("href", "")
            parsed = urlparse(href)
            if parsed.scheme == "mailto":
                stats["mailto_links"] += 1
                if parsed.path.lower() != CONTACT_EMAIL:
                    issues.append(f"{page}: mailto link should use {CONTACT_EMAIL}: {href}")
            for forbidden in FORBIDDEN_CONTACT_SNIPPETS:
                if forbidden.lower() in href.lower():
                    issues.append(f"{page}: forbidden legacy contact reference in link: {forbidden}")
            if parsed.scheme in ("http", "https") and parsed.netloc not in LOCAL_HOSTS:
                stats["external_links"] += 1
                rel = set(anchor.get("rel", "").split())
                if anchor.get("target") == "_blank" and not {"noopener", "noreferrer"}.issubset(rel):
                    issues.append(f"{page}: external _blank link missing noopener/noreferrer: {href}")
                if "books.com.tw" in parsed.netloc and "sponsored" not in rel:
                    issues.append(f"{page}: affiliate link missing sponsored rel: {href}")

        for tag, attr, raw in parser.refs:
            values = [raw]
            if attr == "srcset":
                values = [part.strip().split()[0] for part in raw.split(",") if part.strip()]
            for value in values:
                if not value or value.startswith(("mailto:", "tel:", "javascript:", "data:")):
                    continue
                target, fragment = target_for(page, value)
                if target is None:
                    continue
                stats["internal_refs"] += 1
                if not target.exists():
                    issues.append(f"{page}: missing target for {value} -> {target}")
                    continue
                if fragment and target.suffix == ".html":
                    target_parser = parsers.get(target)
                    if target_parser and fragment not in target_parser.ids:
                        issues.append(f"{page}: missing anchor #{fragment} in {target}")

    sitemap_urls, sitemap_issues, sitemap_stats = parse_sitemap(parsers)
    issues.extend(sitemap_issues)
    stats.update(sitemap_stats)
    issues.extend(check_robots(sitemap_urls))
    manifest_issues, manifest_stats = parse_manifest()
    issues.extend(manifest_issues)
    stats.update(manifest_stats)
    feed_issues, feed_stats = parse_feed(parsers, sitemap_urls)
    issues.extend(feed_issues)
    stats.update(feed_stats)
    header_issues, header_stats = parse_headers()
    issues.extend(header_issues)
    stats.update(header_stats)
    redirect_issues, redirect_stats = parse_redirects(parsers)
    issues.extend(redirect_issues)
    stats.update(redirect_stats)
    security_issues, security_stats = parse_security_txt(parsers)
    issues.extend(security_issues)
    stats.update(security_stats)
    policy_issues, policy_stats = check_policy_pages(parsers)
    issues.extend(policy_issues)
    stats.update(policy_stats)
    static_asset_issues, static_asset_stats = check_static_asset_refs(parsers)
    issues.extend(static_asset_issues)
    stats.update(static_asset_stats)

    indexable_canonicals: set[str] = set()
    for page, parser in parsers.items():
        canonicals = parser.links_with_rel("canonical")
        if len(canonicals) == 1 and not is_noindex(parser):
            indexable_canonicals.add(canonicals[0].get("href", ""))
        if is_noindex(parser) and public_url_for_page(page) in sitemap_urls:
            issues.append(f"{SITEMAP_PATH}: noindex page should not be listed: {public_url_for_page(page)}")

    missing_sitemap_urls = sorted(indexable_canonicals.difference(sitemap_urls))
    unexpected_sitemap_urls = sorted(sitemap_urls.difference(indexable_canonicals))
    for url in missing_sitemap_urls[:50]:
        issues.append(f"{SITEMAP_PATH}: indexable canonical missing from sitemap: {url}")
    if len(missing_sitemap_urls) > 50:
        issues.append(f"{SITEMAP_PATH}: {len(missing_sitemap_urls) - 50} more indexable canonical URL(s) missing from sitemap")
    for url in unexpected_sitemap_urls[:50]:
        issues.append(f"{SITEMAP_PATH}: sitemap URL is not an indexable canonical: {url}")
    if len(unexpected_sitemap_urls) > 50:
        issues.append(f"{SITEMAP_PATH}: {len(unexpected_sitemap_urls) - 50} more unexpected sitemap URL(s)")

    print(f"pages={stats['pages']}")
    print(f"indexable_pages={stats['indexable_pages']}")
    print(f"noindex_pages={stats['noindex_pages']}")
    print(f"images={stats['images']}")
    print(f"h1_tags={stats['h1_tags']}")
    print(f"main_landmarks={stats['main_landmarks']}")
    print(f"nav_landmarks={stats['nav_landmarks']}")
    print(f"language_menu_links={stats['language_menu_links']}")
    print(f"jsonld_blocks={stats['jsonld_blocks']}")
    print(f"primary_jsonld_entities={stats['primary_jsonld_entities']}")
    print(f"canonical_links={stats['canonical_links']}")
    print(f"hreflang_links={stats['hreflang_links']}")
    print(f"head_asset_links={stats['head_asset_links']}")
    print(f"rss_head_links={stats['rss_head_links']}")
    print(f"social_cards={stats['social_cards']}")
    print(f"social_locale_tags={stats['social_locale_tags']}")
    print(f"social_images={stats['social_images']}")
    print(f"sitemap_urls={stats['sitemap_urls']}")
    print(f"sitemap_alternates={stats['sitemap_alternates']}")
    print(f"manifest_icons={stats['manifest_icons']}")
    print(f"manifest_shortcuts={stats['manifest_shortcuts']}")
    print(f"feed_items={stats['feed_items']}")
    print(f"header_blocks={stats['header_blocks']}")
    print(f"header_rules={stats['header_rules']}")
    print(f"redirect_rules={stats['redirect_rules']}")
    print(f"security_txt_files={stats['security_txt_files']}")
    print(f"security_txt_fields={stats['security_txt_fields']}")
    print(f"policy_pages={stats['policy_pages']}")
    print(f"mailto_links={stats['mailto_links']}")
    print(f"versioned_static_assets={stats['versioned_static_assets']}")
    print(f"internal_refs={stats['internal_refs']}")
    print(f"external_links={stats['external_links']}")
    print(f"issues={len(issues)}")
    for issue in issues[:200]:
        print(issue)
    if len(issues) > 200:
        print(f"... {len(issues) - 200} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
