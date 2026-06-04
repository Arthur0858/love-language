#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lovetypes.tw"
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
EXPECTED_HREFLANGS = {"zh-TW", "en", "ja", "ko", "es", "x-default"}
SITEMAP_PATH = ROOT / "sitemap.xml"
ROBOTS_PATH = ROOT / "robots.txt"
FEED_PATH = ROOT / "feed.xml"
MANIFEST_PATH = ROOT / "site.webmanifest"
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


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []
        self.anchors: list[dict[str, str]] = []
        self.buttons: list[list[object]] = []
        self.controls: list[tuple[str, dict[str, str]]] = []
        self.images: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.ids: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.title_parts: list[str] = []
        self.jsonld_blocks: list[str] = []
        self.html_lang: str | None = None
        self._stack: list[tuple[str, dict[str, str], list[str]]] = []
        self._in_title = False
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
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
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        parsers[page] = parser

    for page, parser in parsers.items():
        stats["pages"] += 1
        stats["images"] += len(parser.images)
        stats["jsonld_blocks"] += len(parser.jsonld_blocks)
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

        if not parser.jsonld_blocks:
            issues.append(f"{page}: missing JSON-LD")
        for block in parser.jsonld_blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                issues.append(f"{page}: invalid JSON-LD: {exc}")

        for image in parser.images:
            src = image.get("src", "")
            if "alt" not in image:
                issues.append(f"{page}: image missing alt: {src}")
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
    print(f"jsonld_blocks={stats['jsonld_blocks']}")
    print(f"canonical_links={stats['canonical_links']}")
    print(f"hreflang_links={stats['hreflang_links']}")
    print(f"head_asset_links={stats['head_asset_links']}")
    print(f"rss_head_links={stats['rss_head_links']}")
    print(f"social_cards={stats['social_cards']}")
    print(f"social_images={stats['social_images']}")
    print(f"sitemap_urls={stats['sitemap_urls']}")
    print(f"sitemap_alternates={stats['sitemap_alternates']}")
    print(f"manifest_icons={stats['manifest_icons']}")
    print(f"manifest_shortcuts={stats['manifest_shortcuts']}")
    print(f"feed_items={stats['feed_items']}")
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
