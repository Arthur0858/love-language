#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lovetypes.tw"
CONTACT_EMAIL = "contact@lovetypes.tw"
ADS_TXT_PATH = ROOT / "ads.txt"
FORBIDDEN_ADSENSE_SCRIPT_SNIPPETS = {
    "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js",
    "adsbygoogle",
}
FORBIDDEN_CONTACT_SNIPPETS = {
    "contact@parenttechchecklist.com",
    "parenttechchecklist.com",
    "s755102@gmail.com",
}
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
AFFILIATE_HOST = "www.books.com.tw"
AFFILIATE_PATH_PREFIX = "/exep/assp.php/arthur0858/products/"
AFFILIATE_REQUIRED_QUERY = {
    "utm_source": "arthur0858",
    "utm_medium": "ap-books",
    "utm_content": "recommend",
    "utm_campaign": "ap-202604",
}
AFFILIATE_DISCLOSURE_SNIPPETS = {
    "聯盟行銷",
    "affiliate links",
    "アフィリエイト",
    "제휴",
    "afiliado",
}
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
LLMS_PATH = ROOT / "llms.txt"
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
LEGACY_ROOT_STATIC_ASSETS = {
    "shared.css",
    "site-interactions.js",
    "deferred-external.js",
}
LIVE_REGION_DATA_ATTRS = {
    "data-guide-saved",
    "data-keepsake-saved",
    "data-luna-saved",
    "data-quiz-box",
    "data-quiz-result",
    "data-quiz-saved",
    "data-repair-saved",
    "data-supply-saved",
}
EXPECTED_REDIRECTS = {
    "/.well-known/security.txt": ("/security.txt", "200"),
    "/luna/": ("/luna-yoga-music/", "301"),
    "/en/luna/": ("/en/luna-yoga-music/", "301"),
    "/ja/luna/": ("/ja/luna-yoga-music/", "301"),
    "/ko/luna/": ("/ko/luna-yoga-music/", "301"),
    "/es/luna/": ("/es/luna-yoga-music/", "301"),
}
NOT_FOUND_SAFE_ROUTE_HREFS = {
    "/#quiz-section",
    "/characters/",
    "/resources/",
    "/contact/",
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
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LLMS_URL_RE = re.compile(r"https://lovetypes\.tw/[^\s)>,]+")
HANGUL_RE = re.compile(r"[\uac00-\ud7af]")
KANA_RE = re.compile(r"[\u3040-\u30ff]")
UNEXPECTED_SCRIPT_CHECKS = {
    "en": {"CJK": CJK_RE, "Hangul": HANGUL_RE, "Kana": KANA_RE},
    "es": {"CJK": CJK_RE, "Hangul": HANGUL_RE, "Kana": KANA_RE},
    "ja": {"Hangul": HANGUL_RE},
    "ko": {"Kana": KANA_RE},
}


def load_generator_config():
    generator_path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_site_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load generator config from {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR_CONFIG = load_generator_config()
ADSENSE_ACCOUNT = GENERATOR_CONFIG.ADSENSE_ACCOUNT
EXPECTED_ADS_TXT = f"google.com, {ADSENSE_ACCOUNT.removeprefix('ca-')}, DIRECT, f08c47fec0942fa0"
FORMAL_GUIDE_GUARDIANS = {guide["slug"]: guide["guardian"] for guide in GENERATOR_CONFIG.GUIDES}
LEGACY_ZH_GUIDE_TARGETS = {slug: target for slug, _title, _desc, target in GENERATOR_CONFIG.LEGACY_ZH_GUIDES}
CURRENT_STATIC_ASSETS = {
    "css": GENERATOR_CONFIG.CSS_ASSET,
    "interactions": GENERATOR_CONFIG.INTERACTIONS_ASSET,
    "affiliate": GENERATOR_CONFIG.AFFILIATE_ASSET,
}
REQUIRED_INTERACTION_HASH_SNIPPETS = {
    "samePageHash": "same-page hash link detection",
    "focusHashTarget": "hash target focus handoff",
    "scrollToHashTarget": "hash target scrolling",
    "prefers-reduced-motion: reduce": "reduced motion hash scrolling",
    "window.history.pushState": "same-page hash history update",
}


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
        self.live_regions: list[dict[str, str]] = []
        self.dynamic_regions: list[dict[str, str]] = []
        self.progressbars: list[dict[str, str]] = []
        self.ids: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.tag_counts = Counter()
        self.source = ""
        self.title_parts: list[str] = []
        self.visible_text_parts: list[str] = []
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
            data["_text"] = ""
            data["_image_alt"] = ""
            if any(stack_tag == "nav" and "nav-links" in class_tokens(stack_attrs) for stack_tag, stack_attrs, _ in self._stack):
                data["_primary_nav"] = "1"
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
        if data.get("aria-live") or data.get("role") == "status":
            self.live_regions.append(data)
        if data.get("role") == "progressbar":
            self.progressbars.append(data)
        if any(attr in data for attr in LIVE_REGION_DATA_ATTRS):
            self.dynamic_regions.append(data)
        if tag in ("input", "select", "textarea"):
            self.controls.append((tag, data))
        if tag == "img":
            self.images.append(data)
            alt = data.get("alt", "")
            if alt:
                for stack_tag, stack_attrs, _ in reversed(self._stack):
                    if stack_tag == "a":
                        stack_attrs["_image_alt"] = f"{stack_attrs.get('_image_alt', '')} {alt}".strip()
                        break
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
        if current_tag == "a":
            data["_text"] = text
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
        if self._stack and data.strip() and not self._should_ignore_visible_text():
            self.visible_text_parts.append(data)
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

    def visible_text(self) -> str:
        return " ".join(" ".join(self.visible_text_parts).split())

    def _should_ignore_visible_text(self) -> bool:
        for tag, attrs, _ in self._stack:
            if tag in {"script", "style"}:
                return True
            if tag == "details" and "language-menu" in class_tokens(attrs):
                return True
        return False


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


def public_url_for_href(page: Path, href: str) -> str:
    parsed = urlparse(href)
    if parsed.scheme in ("http", "https"):
        return href
    if href.startswith("//"):
        return href
    target, _ = target_for(page, href)
    if target is None:
        return href
    return public_url_for_page(target)


def is_noindex(parser: PageParser) -> bool:
    return "noindex" in parser.meta_content("robots").lower()


def is_locale_home(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    if relative == Path("index.html"):
        return True
    return len(relative.parts) == 2 and relative.parts[1] == "index.html" and relative.parts[0] in {"en", "ja", "ko", "es"}


def expected_primary_nav_href(page: Path) -> str | None:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts == ["index.html"]:
        return None
    prefix = ""
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        prefix = parts.pop(0)
    if len(parts) == 1 and parts[0] == "index.html":
        return None
    section = parts[0] if parts else ""
    section = {
        "keepsakes": "resources",
        "luna": "resources",
        "luna-yoga-music": "resources",
    }.get(section, section)
    if section not in {"guides", "characters", "theory", "resources", "about"}:
        return None
    return f"/{prefix}/{section}/" if prefix else f"/{section}/"


def is_resources_page(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts == ["resources", "index.html"]


def is_characters_index_page(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts == ["characters", "index.html"]


def is_keepsakes_page(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts == ["keepsakes", "index.html"]


def normalized_page_parts(page: Path) -> list[str]:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts


def is_about_page(page: Path) -> bool:
    return normalized_page_parts(page) == ["about", "index.html"]


def is_theory_page(page: Path) -> bool:
    return normalized_page_parts(page) == ["theory", "index.html"]


def formal_guide_slug_for_page(page: Path) -> str:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    if len(parts) == 3 and parts[0] == "guides" and parts[2] == "index.html" and parts[1] in FORMAL_GUIDE_GUARDIANS:
        return parts[1]
    return ""


def legacy_zh_guide_target_for_page(page: Path) -> str:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if len(parts) == 3 and parts[0] == "guides" and parts[2] == "index.html" and parts[1] in LEGACY_ZH_GUIDE_TARGETS:
        return LEGACY_ZH_GUIDE_TARGETS[parts[1]]
    return ""


def lang_url_for_page(page: Path, target: str = "") -> str:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    prefix = parts[0] if parts and parts[0] in {"en", "ja", "ko", "es"} else ""
    if not target:
        return f"/{prefix}/" if prefix else "/"
    return f"/{prefix}/{target}/" if prefix else f"/{target}/"


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


def extract_llms_urls(text: str) -> list[str]:
    return [match.group(0).rstrip(".,;") for match in LLMS_URL_RE.finditer(text)]


def parse_llms_txt(parsers: dict[Path, PageParser], sitemap_urls: set[str]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not LLMS_PATH.exists():
        return [f"{LLMS_PATH}: missing llms.txt"], stats

    text = LLMS_PATH.read_text(encoding="utf-8", errors="ignore")
    stats["llms_files_checked"] = 1
    stats["llms_lines"] = len(text.splitlines())

    required_sections = [
        "# LoveTypes - Heart Garden Emotion Guardians",
        "## Canonical Site",
        "## Core Concept",
        "## Five Guardians",
        "## High-Value Pages",
        "## Guide Index",
        "## Commercial and Safety Boundaries",
    ]
    for section in required_sections:
        stats["llms_sections_checked"] += 1
        if section not in text:
            issues.append(f"{LLMS_PATH}: missing required section {section!r}")

    required_snippets = {
        f"Production: {DOMAIN}/": "production URL",
        f"Last updated: {GENERATOR_CONFIG.UPDATED}": "generator updated date",
        f"Contact email: {CONTACT_EMAIL}": "contact email",
        "relationship reflection and practical repair support": "safety positioning",
        "No full-site advertising script is enabled": "ad approval boundary",
        "Affiliate links are kept on the Resources page": "affiliate boundary",
    }
    for snippet, label in required_snippets.items():
        stats["llms_snippets_checked"] += 1
        if snippet not in text:
            issues.append(f"{LLMS_PATH}: missing {label}: {snippet!r}")

    high_value_urls = {
        f"{DOMAIN}/",
        f"{DOMAIN}/characters/",
        f"{DOMAIN}/guides/",
        f"{DOMAIN}/resources/",
        f"{DOMAIN}/repair-plan/",
        f"{DOMAIN}/keepsakes/",
        f"{DOMAIN}/luna-yoga-music/",
        f"{DOMAIN}/about/",
        f"{DOMAIN}/theory/",
        f"{DOMAIN}/contact/",
        f"{DOMAIN}/privacy/",
        f"{DOMAIN}/terms/",
    }
    for url in high_value_urls:
        stats["llms_high_value_urls_checked"] += 1
        if url not in text:
            issues.append(f"{LLMS_PATH}: missing high-value URL {url}")

    for slug, data in GENERATOR_CONFIG.GUARDIANS.items():
        zh_name, zh_language, _ = data["zh"]
        en_name, en_language, _ = data["en"]
        guardian_url = f"{DOMAIN}/characters/{slug}/"
        stats["llms_guardians_checked"] += 1
        for value, label in (
            (zh_name, "zh guardian name"),
            (en_name, "en guardian name"),
            (zh_language, "zh love language"),
            (en_language, "en love language"),
            (guardian_url, "guardian URL"),
        ):
            if value not in text:
                issues.append(f"{LLMS_PATH}: {slug} missing {label}: {value}")

    for guide in GENERATOR_CONFIG.GUIDES:
        title, description = guide["zh"]
        guide_url = f"{DOMAIN}/guides/{guide['slug']}/"
        stats["llms_guides_checked"] += 1
        for value, label in ((title, "guide title"), (description, "guide description"), (guide_url, "guide URL")):
            if value not in text:
                issues.append(f"{LLMS_PATH}: {guide['slug']} missing {label}: {value}")

    for forbidden in FORBIDDEN_CONTACT_SNIPPETS | FORBIDDEN_ADSENSE_SCRIPT_SNIPPETS:
        if forbidden in text:
            issues.append(f"{LLMS_PATH}: forbidden snippet should not appear: {forbidden}")

    llms_urls = sorted(set(extract_llms_urls(text)))
    stats["llms_urls_checked"] = len(llms_urls)
    for url in llms_urls:
        target, fragment = target_for(ROOT / "index.html", url)
        if target is None or not target.exists():
            issues.append(f"{LLMS_PATH}: listed URL target missing: {url}")
            continue
        if fragment:
            issues.append(f"{LLMS_PATH}: listed URL should not include fragment: {url}")
        if target.suffix == ".html":
            target_parser = parsers.get(target)
            if target_parser and is_noindex(target_parser):
                issues.append(f"{LLMS_PATH}: listed URL should not point to noindex page: {url}")
            canonicals = target_parser.links_with_rel("canonical") if target_parser else []
            if len(canonicals) == 1 and canonicals[0].get("href") != url:
                issues.append(f"{LLMS_PATH}: listed URL should match target canonical: {url}")
        if url not in sitemap_urls:
            issues.append(f"{LLMS_PATH}: listed URL missing from sitemap: {url}")

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


def parse_ads_txt() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not ADS_TXT_PATH.exists():
        return [f"{ADS_TXT_PATH}: missing ads.txt"], stats
    lines = [
        line.strip()
        for line in ADS_TXT_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    stats["ads_txt_records"] = len(lines)
    if lines != [EXPECTED_ADS_TXT]:
        issues.append(f"{ADS_TXT_PATH}: expected exact AdSense seller record {EXPECTED_ADS_TXT!r}, found {lines}")
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

    for name in sorted(LEGACY_ROOT_STATIC_ASSETS):
        stats["legacy_static_assets_checked"] += 1
        if (ROOT / name).exists():
            issues.append(f"{ROOT / name}: legacy unversioned root asset should not be deployed")

    patterns = (
        ("shared-", ".css"),
        ("site-interactions-", ".js"),
        ("deferred-external-", ".js"),
    )
    expected_versioned_assets = {Path(value.lstrip("/")).name for value in CURRENT_STATIC_ASSETS.values()}
    for asset in sorted(ROOT.iterdir()):
        if not asset.is_file():
            continue
        if not any(asset.name.startswith(prefix) and asset.name.endswith(suffix) for prefix, suffix in patterns):
            continue
        stats["versioned_static_assets"] += 1
        if asset.name not in expected_versioned_assets:
            issues.append(f"{asset}: unexpected root versioned static asset")
        if asset.name not in referenced:
            issues.append(f"{asset}: versioned static asset is not referenced by any generated HTML page")

    interaction_asset = ROOT / CURRENT_STATIC_ASSETS["interactions"].lstrip("/")
    stats["interaction_hash_focus_snippets_checked"] = len(REQUIRED_INTERACTION_HASH_SNIPPETS)
    if not interaction_asset.exists():
        issues.append(f"{interaction_asset}: current interaction asset missing")
    else:
        interaction_source = interaction_asset.read_text(encoding="utf-8", errors="ignore")
        for snippet, label in REQUIRED_INTERACTION_HASH_SNIPPETS.items():
            if snippet not in interaction_source:
                issues.append(f"{interaction_asset}: missing {label}: {snippet}")
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
    stats["generator_config_loaded"] = 1

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
        stats["live_regions"] += len(parser.live_regions)
        stats["dynamic_live_regions"] += len(parser.dynamic_regions)
        stats["progressbars"] += len(parser.progressbars)
        if is_noindex(parser):
            stats["noindex_pages"] += 1
        else:
            stats["indexable_pages"] += 1

        if page.name == "404.html":
            stats["not_found_pages"] += 1
            if not is_noindex(parser):
                issues.append(f"{page}: 404 page should be noindex")
            if "404 HEART GARDEN" not in parser.source:
                issues.append(f"{page}: custom 404 page missing Heart Garden marker")
            not_found_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            missing_safe_routes = sorted(NOT_FOUND_SAFE_ROUTE_HREFS.difference(not_found_hrefs))
            if missing_safe_routes:
                issues.append(f"{page}: custom 404 page missing safe route links {', '.join(missing_safe_routes)}")

        if not "".join(parser.title_parts).strip():
            issues.append(f"{page}: missing <title>")
        if not parser.meta_content("description"):
            issues.append(f"{page}: missing meta description")
        if not parser.meta_content("robots"):
            issues.append(f"{page}: missing robots meta")
        if not parser.html_lang:
            issues.append(f"{page}: missing html lang")
        else:
            script_checks = UNEXPECTED_SCRIPT_CHECKS.get(parser.html_lang, {})
            stats["language_script_checks"] += len(script_checks)
            visible_text = parser.visible_text()
            for script_name, script_pattern in script_checks.items():
                script_match = script_pattern.search(visible_text)
                if script_match:
                    start = max(0, script_match.start() - 32)
                    end = min(len(visible_text), script_match.end() + 32)
                    excerpt = visible_text[start:end]
                    issues.append(f"{page}: unexpected {script_name} text outside language menu: {excerpt}")

        adsense_metas = [meta for meta in parser.metas if meta.get("name") == "google-adsense-account"]
        stats["adsense_account_meta_tags"] += len(adsense_metas)
        if len(adsense_metas) != 1:
            issues.append(f"{page}: expected one google-adsense-account meta tag, found {len(adsense_metas)}")
        elif adsense_metas[0].get("content") != ADSENSE_ACCOUNT:
            issues.append(f"{page}: google-adsense-account should be {ADSENSE_ACCOUNT}")
        for forbidden in FORBIDDEN_ADSENSE_SCRIPT_SNIPPETS:
            if forbidden in parser.source:
                issues.append(f"{page}: full AdSense script should not load before approval: {forbidden}")

        page_title = "".join(parser.title_parts).strip()
        page_description = parser.meta_content("description")

        if len(parser.mains) != 1:
            issues.append(f"{page}: expected one <main> landmark, found {len(parser.mains)}")
        elif parser.mains[0].get("id") != "main":
            issues.append(f"{page}: <main> should use id=\"main\" for the skip link target")
        elif parser.mains[0].get("tabindex") != "-1":
            issues.append(f"{page}: <main> should use tabindex=\"-1\" so skip links can move focus")

        if is_locale_home(page):
            stats["home_quiz_entry_pages"] += 1
            journey_section_count = parser.source.count("data-home-journey")
            journey_card_count = parser.source.count('class="home-journey-card"')
            if journey_section_count != 1:
                issues.append(f"{page}: expected one home journey section, found {journey_section_count}")
            if journey_card_count != 4:
                issues.append(f"{page}: expected 4 home journey cards, found {journey_card_count}")
            if journey_section_count == 1 and journey_card_count == 4:
                stats["home_journey_pages"] += 1
            home_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_home_hrefs = {
                "#quiz-section",
                lang_url_for_page(page, "characters"),
                lang_url_for_page(page, "resources"),
                lang_url_for_page(page, "repair-plan"),
            }
            missing_home_hrefs = sorted(required_home_hrefs.difference(home_hrefs))
            if missing_home_hrefs:
                issues.append(f"{page}: home journey missing hrefs {', '.join(missing_home_hrefs)}")
            quiz_section_count = parser.ids.count("quiz-section")
            if quiz_section_count != 1:
                issues.append(f"{page}: expected one #quiz-section target, found {quiz_section_count}")
            elif 'id="quiz-section" tabindex="-1"' not in parser.source:
                issues.append(f"{page}: #quiz-section should use tabindex=\"-1\" for hash focus")
            if 'data-quiz-root' not in parser.source:
                issues.append(f"{page}: home page missing quiz root")
            if 'class="primary-btn" href="#quiz-section"' not in parser.source:
                issues.append(f"{page}: home hero primary CTA should point to #quiz-section")
        if is_resources_page(page):
            stats["resources_supply_entry_pages"] += 1
            owned_signal_count = parser.source.count("data-supply-owned-signal")
            owned_card_count = parser.source.count("data-supply-owned-card")
            if owned_signal_count != 1:
                issues.append(f"{page}: expected one supply owned signal section, found {owned_signal_count}")
            if owned_card_count != 5:
                issues.append(f"{page}: expected 5 supply owned signal cards, found {owned_card_count}")
            if owned_signal_count == 1 and owned_card_count == 5:
                stats["resources_owned_signal_pages"] += 1
            for target_id in ("supply-start", "supply-routes"):
                if target_id not in parser.ids:
                    issues.append(f"{page}: resources page missing #{target_id}")
            resource_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_resource_hrefs = {
                lang_url_for_page(page) + "#quiz-section",
                "#supply-routes",
                lang_url_for_page(page, "luna-yoga-music"),
            }
            missing_resource_hrefs = sorted(required_resource_hrefs.difference(resource_hrefs))
            if missing_resource_hrefs:
                issues.append(f"{page}: resources supply entry missing hrefs {', '.join(missing_resource_hrefs)}")
        if is_characters_index_page(page):
            stats["characters_guardian_entry_pages"] += 1
            for target_id in ("guardian-start", "guardian-map"):
                if target_id not in parser.ids:
                    issues.append(f"{page}: characters page missing #{target_id}")
            character_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_character_hrefs = {
                lang_url_for_page(page) + "#quiz-section",
                "#guardian-map",
                lang_url_for_page(page, "resources"),
            }
            missing_character_hrefs = sorted(required_character_hrefs.difference(character_hrefs))
            if missing_character_hrefs:
                issues.append(f"{page}: characters guardian entry missing hrefs {', '.join(missing_character_hrefs)}")
        if is_keepsakes_page(page):
            stats["keepsake_route_action_pages"] += 1
            keepsake_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            for slug in GUARDIAN_SLUGS:
                card_id = f"keepsake-card-{slug}"
                if card_id not in parser.ids:
                    issues.append(f"{page}: keepsakes page missing #{card_id}")
            required_keepsake_hrefs = {
                target
                for slug in GUARDIAN_SLUGS
                for target in (
                    f"{lang_url_for_page(page, 'resources')}#supply-{slug}",
                    f"{lang_url_for_page(page, 'repair-plan')}#plan-{slug}",
                )
            }
            missing_keepsake_hrefs = sorted(required_keepsake_hrefs.difference(keepsake_hrefs))
            if missing_keepsake_hrefs:
                issues.append(f"{page}: keepsake cards missing continuation hrefs {', '.join(missing_keepsake_hrefs)}")

        if is_about_page(page) or is_theory_page(page):
            stats["trust_action_route_pages"] += 1
            route_count = parser.ids.count("trust-action-routes")
            if route_count != 1:
                issues.append(f"{page}: expected one #trust-action-routes target, found {route_count}")
            if is_about_page(page):
                stats["about_garden_pass_pages"] += 1
                pass_section_count = parser.source.count("data-about-garden-pass")
                pass_card_count = parser.source.count('class="garden-pass-card"')
                if pass_section_count != 1:
                    issues.append(f"{page}: expected one about garden pass section, found {pass_section_count}")
                if pass_card_count != 3:
                    issues.append(f"{page}: expected 3 about garden pass cards, found {pass_card_count}")
            if is_theory_page(page):
                stats["theory_domain_compass_pages"] += 1
                compass_section_count = parser.source.count("data-theory-domain-compass")
                compass_card_count = parser.source.count('class="theory-domain-card"')
                if compass_section_count != 1:
                    issues.append(f"{page}: expected one theory domain compass section, found {compass_section_count}")
                if compass_card_count != 5:
                    issues.append(f"{page}: expected 5 theory domain compass cards, found {compass_card_count}")
            trust_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_trust_hrefs = {
                lang_url_for_page(page) + "#quiz-section",
                lang_url_for_page(page, "characters"),
            }
            if is_about_page(page):
                required_trust_hrefs.update({
                    lang_url_for_page(page, "guides"),
                    lang_url_for_page(page, "contact"),
                })
            else:
                required_trust_hrefs.update({
                    lang_url_for_page(page, "repair-plan"),
                    lang_url_for_page(page, "resources"),
                })
            missing_trust_hrefs = sorted(required_trust_hrefs.difference(trust_hrefs))
            if missing_trust_hrefs:
                issues.append(f"{page}: trust action route missing hrefs {', '.join(missing_trust_hrefs)}")

        guide_slug = formal_guide_slug_for_page(page)
        if guide_slug:
            stats["guide_action_bridge_pages"] += 1
            guardian_slug = FORMAL_GUIDE_GUARDIANS[guide_slug]
            bridge_count = parser.ids.count("guide-action-bridge")
            if bridge_count != 1:
                issues.append(f"{page}: expected one #guide-action-bridge target, found {bridge_count}")
            guide_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_guide_hrefs = {
                lang_url_for_page(page, f"characters/{guardian_slug}"),
                f"{lang_url_for_page(page, 'resources')}#supply-{guardian_slug}",
                f"{lang_url_for_page(page, 'repair-plan')}#plan-{guardian_slug}",
            }
            missing_guide_hrefs = sorted(required_guide_hrefs.difference(guide_hrefs))
            if missing_guide_hrefs:
                issues.append(f"{page}: guide action bridge missing continuation hrefs {', '.join(missing_guide_hrefs)}")

        legacy_target = legacy_zh_guide_target_for_page(page)
        if legacy_target:
            stats["legacy_guide_action_bridge_pages"] += 1
            if not is_noindex(parser):
                issues.append(f"{page}: legacy guide page should remain noindex")
            if "archive-forward" not in parser.source:
                issues.append(f"{page}: legacy guide missing archive-forward notice")
            guardian_slug = FORMAL_GUIDE_GUARDIANS[legacy_target]
            bridge_count = parser.ids.count("guide-action-bridge")
            if bridge_count != 1:
                issues.append(f"{page}: expected one legacy #guide-action-bridge target, found {bridge_count}")
            legacy_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_legacy_hrefs = {
                lang_url_for_page(page, f"guides/{legacy_target}"),
                lang_url_for_page(page, f"characters/{guardian_slug}"),
                f"{lang_url_for_page(page, 'resources')}#supply-{guardian_slug}",
                f"{lang_url_for_page(page, 'repair-plan')}#plan-{guardian_slug}",
            }
            missing_legacy_hrefs = sorted(required_legacy_hrefs.difference(legacy_hrefs))
            if missing_legacy_hrefs:
                issues.append(f"{page}: legacy guide bridge missing continuation hrefs {', '.join(missing_legacy_hrefs)}")

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
        primary_nav_links = [anchor for anchor in parser.anchors if anchor.get("_primary_nav") == "1"]
        stats["primary_nav_links"] += len(primary_nav_links)
        if len(primary_nav_links) != 5:
            issues.append(f"{page}: expected five primary navigation links, found {len(primary_nav_links)}")
        primary_current_links = [anchor for anchor in primary_nav_links if anchor.get("aria-current") == "page"]
        primary_active_links = [anchor for anchor in primary_nav_links if "active" in class_tokens(anchor)]
        expected_nav_href = expected_primary_nav_href(page)
        if expected_nav_href:
            if len(primary_current_links) != 1:
                issues.append(f"{page}: expected one current primary navigation link, found {len(primary_current_links)}")
            elif primary_current_links[0].get("href") != expected_nav_href:
                issues.append(f"{page}: current primary navigation link should be {expected_nav_href}: {primary_current_links[0].get('href', '')}")
            if len(primary_active_links) != 1:
                issues.append(f"{page}: expected one active primary navigation link, found {len(primary_active_links)}")
            elif primary_active_links[0].get("href") != expected_nav_href:
                issues.append(f"{page}: active primary navigation link should be {expected_nav_href}: {primary_active_links[0].get('href', '')}")
        elif primary_current_links or primary_active_links:
            issues.append(f"{page}: primary navigation should not mark a current section")

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

        css_assets = [
            link.get("href", "")
            for link in parser.links_with_rel("stylesheet")
            if link.get("href", "").startswith("/shared-") and link.get("href", "").endswith(".css")
        ]
        stats["current_css_asset_refs"] += css_assets.count(CURRENT_STATIC_ASSETS["css"])
        if css_assets != [CURRENT_STATIC_ASSETS["css"]]:
            issues.append(f"{page}: expected current CSS asset {CURRENT_STATIC_ASSETS['css']}, found {css_assets}")

        interaction_assets = [
            raw
            for tag, attr, raw in parser.refs
            if tag == "script"
            and attr == "src"
            and raw.startswith("/site-interactions-")
            and raw.endswith(".js")
        ]
        stats["current_interaction_asset_refs"] += interaction_assets.count(CURRENT_STATIC_ASSETS["interactions"])
        if interaction_assets != [CURRENT_STATIC_ASSETS["interactions"]]:
            issues.append(
                f"{page}: expected current interaction asset {CURRENT_STATIC_ASSETS['interactions']}, found {interaction_assets}"
            )

        affiliate_assets = [
            raw
            for tag, attr, raw in parser.refs
            if tag == "script"
            and attr == "src"
            and raw.startswith("/deferred-external-")
            and raw.endswith(".js")
        ]
        stats["current_affiliate_asset_refs"] += affiliate_assets.count(CURRENT_STATIC_ASSETS["affiliate"])
        expected_affiliate_assets = [CURRENT_STATIC_ASSETS["affiliate"]] if is_resources_page(page) else []
        if affiliate_assets != expected_affiliate_assets:
            issues.append(
                f"{page}: expected affiliate script assets {expected_affiliate_assets}, found {affiliate_assets}"
            )

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
        for anchor in language_links:
            lang = anchor.get("lang", "")
            menu_href = public_url_for_href(page, anchor.get("href", ""))
            hreflang_href = hreflang_map.get(lang)
            stats["language_hreflang_matches"] += 1
            if hreflang_href != menu_href:
                issues.append(f"{page}: language menu link for {lang} should match hreflang {hreflang_href}: {menu_href}")

        duplicate_ids = [value for value, count in Counter(parser.ids).items() if count > 1]
        if duplicate_ids:
            issues.append(f"{page}: duplicate ids {', '.join(duplicate_ids[:10])}")

        page_affiliate_links = 0
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

        for attrs in parser.dynamic_regions:
            matching_attrs = sorted(attr for attr in LIVE_REGION_DATA_ATTRS if attr in attrs)
            if not attrs.get("aria-live"):
                issues.append(f"{page}: dynamic region missing aria-live: {','.join(matching_attrs)}")

        if "data-quiz-root" in parser.source:
            if "role=\"progressbar\"" not in parser.source or "aria-valuenow" not in parser.source:
                issues.append(f"{page}: quiz progress should expose role=progressbar with aria-valuenow")
            else:
                stats["quiz_progressbar_scripts"] += 1
            if "aria-pressed=\"false\"" not in parser.source or "setAttribute('aria-pressed', 'true')" not in parser.source:
                issues.append(f"{page}: quiz options should expose aria-pressed selected state")
            else:
                stats["quiz_pressed_state_scripts"] += 1
            if 'class="quiz-options" role="group" aria-labelledby="${questionId}"' not in parser.source:
                issues.append(f"{page}: quiz options should be grouped and labelled by the current question")
            expected_quiz_live_regions = {
                "data-quiz-saved": "quiz saved result",
                "data-quiz-box": "quiz question stage",
                "data-quiz-result": "quiz result",
            }
            for data_attr, label in expected_quiz_live_regions.items():
                if data_attr in parser.source and f"{data_attr} hidden aria-live=\"polite\"" not in parser.source:
                    issues.append(f"{page}: {label} should use aria-live=polite")

        if "data-worksheet-status" in parser.source:
            if 'data-worksheet-status role="status" aria-live="polite"' not in parser.source:
                issues.append(f"{page}: worksheet status should use role=status and aria-live=polite")

        if "scrollIntoView" in parser.source:
            stats["scroll_scripts"] += 1
            if "scrollBehavior" in parser.source and "prefers-reduced-motion: reduce" in parser.source:
                stats["reduced_motion_scroll_scripts"] += 1
            if "behavior: 'smooth'" in parser.source or 'behavior: "smooth"' in parser.source:
                issues.append(f"{page}: scrollIntoView should not hard-code smooth behavior")
            if "behavior: scrollBehavior" in parser.source and "prefers-reduced-motion: reduce" not in parser.source:
                issues.append(f"{page}: variable scroll behavior should respect prefers-reduced-motion")

        for anchor in parser.anchors:
            href = anchor.get("href", "")
            parsed = urlparse(href)
            if href:
                accessible_name = " ".join(
                    part.strip()
                    for part in (
                        anchor.get("aria-label", ""),
                        anchor.get("aria-labelledby", ""),
                        anchor.get("title", ""),
                        anchor.get("_text", ""),
                        anchor.get("_image_alt", ""),
                    )
                    if part.strip()
                )
                if accessible_name:
                    stats["anchor_accessible_names"] += 1
                elif not href.startswith("#"):
                    issues.append(f"{page}: link missing accessible name: {href}")
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
                if parsed.netloc == AFFILIATE_HOST:
                    page_affiliate_links += 1
                    stats["affiliate_links"] += 1
                    if "sponsored" not in rel:
                        issues.append(f"{page}: affiliate link missing sponsored rel: {href}")
                    if not parsed.path.startswith(AFFILIATE_PATH_PREFIX):
                        issues.append(f"{page}: affiliate link should use tracking path {AFFILIATE_PATH_PREFIX}: {href}")
                    query = parse_qs(parsed.query)
                    for key, expected_value in AFFILIATE_REQUIRED_QUERY.items():
                        if query.get(key, [""])[0] != expected_value:
                            issues.append(f"{page}: affiliate link missing {key}={expected_value}: {href}")

        if page_affiliate_links:
            stats["affiliate_pages"] += 1
            has_disclosure_class = 'class="affiliate-disclosure"' in parser.source
            has_disclosure_text = any(snippet in parser.source for snippet in AFFILIATE_DISCLOSURE_SNIPPETS)
            if not has_disclosure_class and not has_disclosure_text:
                issues.append(f"{page}: affiliate links require a visible affiliate disclosure")

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
    llms_issues, llms_stats = parse_llms_txt(parsers, sitemap_urls)
    issues.extend(llms_issues)
    stats.update(llms_stats)
    header_issues, header_stats = parse_headers()
    issues.extend(header_issues)
    stats.update(header_stats)
    redirect_issues, redirect_stats = parse_redirects(parsers)
    issues.extend(redirect_issues)
    stats.update(redirect_stats)
    security_issues, security_stats = parse_security_txt(parsers)
    issues.extend(security_issues)
    stats.update(security_stats)
    ads_issues, ads_stats = parse_ads_txt()
    issues.extend(ads_issues)
    stats.update(ads_stats)
    policy_issues, policy_stats = check_policy_pages(parsers)
    issues.extend(policy_issues)
    stats.update(policy_stats)
    static_asset_issues, static_asset_stats = check_static_asset_refs(parsers)
    issues.extend(static_asset_issues)
    stats.update(static_asset_stats)

    indexable_canonicals: set[str] = set()
    indexable_titles: dict[str, list[Path]] = {}
    indexable_descriptions: dict[str, list[Path]] = {}
    for page, parser in parsers.items():
        canonicals = parser.links_with_rel("canonical")
        if not is_noindex(parser):
            if len(canonicals) == 1:
                indexable_canonicals.add(canonicals[0].get("href", ""))
            page_title = "".join(parser.title_parts).strip()
            page_description = parser.meta_content("description")
            indexable_titles.setdefault(page_title, []).append(page)
            indexable_descriptions.setdefault(page_description, []).append(page)
        if is_noindex(parser) and public_url_for_page(page) in sitemap_urls:
            issues.append(f"{SITEMAP_PATH}: noindex page should not be listed: {public_url_for_page(page)}")

    stats["indexable_unique_titles"] = len(indexable_titles)
    stats["indexable_unique_descriptions"] = len(indexable_descriptions)
    for value, duplicate_pages in sorted(indexable_titles.items()):
        if len(duplicate_pages) > 1:
            issue_pages = ", ".join(str(item) for item in duplicate_pages[:5])
            issues.append(f"indexable pages share duplicate <title> {value!r}: {issue_pages}")
    for value, duplicate_pages in sorted(indexable_descriptions.items()):
        if len(duplicate_pages) > 1:
            issue_pages = ", ".join(str(item) for item in duplicate_pages[:5])
            issues.append(f"indexable pages share duplicate meta description {value!r}: {issue_pages}")

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
    print(f"generator_config_loaded={stats['generator_config_loaded']}")
    print(f"indexable_pages={stats['indexable_pages']}")
    print(f"noindex_pages={stats['noindex_pages']}")
    print(f"not_found_pages={stats['not_found_pages']}")
    print(f"indexable_unique_titles={stats['indexable_unique_titles']}")
    print(f"indexable_unique_descriptions={stats['indexable_unique_descriptions']}")
    print(f"images={stats['images']}")
    print(f"h1_tags={stats['h1_tags']}")
    print(f"main_landmarks={stats['main_landmarks']}")
    print(f"nav_landmarks={stats['nav_landmarks']}")
    print(f"live_regions={stats['live_regions']}")
    print(f"dynamic_live_regions={stats['dynamic_live_regions']}")
    print(f"progressbars={stats['progressbars']}")
    print(f"quiz_progressbar_scripts={stats['quiz_progressbar_scripts']}")
    print(f"quiz_pressed_state_scripts={stats['quiz_pressed_state_scripts']}")
    print(f"home_quiz_entry_pages={stats['home_quiz_entry_pages']}")
    print(f"home_journey_pages={stats['home_journey_pages']}")
    print(f"resources_supply_entry_pages={stats['resources_supply_entry_pages']}")
    print(f"resources_owned_signal_pages={stats['resources_owned_signal_pages']}")
    print(f"characters_guardian_entry_pages={stats['characters_guardian_entry_pages']}")
    print(f"keepsake_route_action_pages={stats['keepsake_route_action_pages']}")
    print(f"trust_action_route_pages={stats['trust_action_route_pages']}")
    print(f"about_garden_pass_pages={stats['about_garden_pass_pages']}")
    print(f"theory_domain_compass_pages={stats['theory_domain_compass_pages']}")
    print(f"guide_action_bridge_pages={stats['guide_action_bridge_pages']}")
    print(f"legacy_guide_action_bridge_pages={stats['legacy_guide_action_bridge_pages']}")
    print(f"scroll_scripts={stats['scroll_scripts']}")
    print(f"reduced_motion_scroll_scripts={stats['reduced_motion_scroll_scripts']}")
    print(f"interaction_hash_focus_snippets_checked={stats['interaction_hash_focus_snippets_checked']}")
    print(f"primary_nav_links={stats['primary_nav_links']}")
    print(f"language_menu_links={stats['language_menu_links']}")
    print(f"language_hreflang_matches={stats['language_hreflang_matches']}")
    print(f"language_script_checks={stats['language_script_checks']}")
    print(f"jsonld_blocks={stats['jsonld_blocks']}")
    print(f"primary_jsonld_entities={stats['primary_jsonld_entities']}")
    print(f"canonical_links={stats['canonical_links']}")
    print(f"hreflang_links={stats['hreflang_links']}")
    print(f"head_asset_links={stats['head_asset_links']}")
    print(f"rss_head_links={stats['rss_head_links']}")
    print(f"current_css_asset_refs={stats['current_css_asset_refs']}")
    print(f"current_interaction_asset_refs={stats['current_interaction_asset_refs']}")
    print(f"current_affiliate_asset_refs={stats['current_affiliate_asset_refs']}")
    print(f"social_cards={stats['social_cards']}")
    print(f"social_locale_tags={stats['social_locale_tags']}")
    print(f"social_images={stats['social_images']}")
    print(f"sitemap_urls={stats['sitemap_urls']}")
    print(f"sitemap_alternates={stats['sitemap_alternates']}")
    print(f"manifest_icons={stats['manifest_icons']}")
    print(f"manifest_shortcuts={stats['manifest_shortcuts']}")
    print(f"feed_items={stats['feed_items']}")
    print(f"llms_files_checked={stats['llms_files_checked']}")
    print(f"llms_lines={stats['llms_lines']}")
    print(f"llms_sections_checked={stats['llms_sections_checked']}")
    print(f"llms_snippets_checked={stats['llms_snippets_checked']}")
    print(f"llms_high_value_urls_checked={stats['llms_high_value_urls_checked']}")
    print(f"llms_guardians_checked={stats['llms_guardians_checked']}")
    print(f"llms_guides_checked={stats['llms_guides_checked']}")
    print(f"llms_urls_checked={stats['llms_urls_checked']}")
    print(f"header_blocks={stats['header_blocks']}")
    print(f"header_rules={stats['header_rules']}")
    print(f"redirect_rules={stats['redirect_rules']}")
    print(f"security_txt_files={stats['security_txt_files']}")
    print(f"security_txt_fields={stats['security_txt_fields']}")
    print(f"ads_txt_records={stats['ads_txt_records']}")
    print(f"adsense_account_meta_tags={stats['adsense_account_meta_tags']}")
    print(f"policy_pages={stats['policy_pages']}")
    print(f"mailto_links={stats['mailto_links']}")
    print(f"anchor_accessible_names={stats['anchor_accessible_names']}")
    print(f"versioned_static_assets={stats['versioned_static_assets']}")
    print(f"legacy_static_assets_checked={stats['legacy_static_assets_checked']}")
    print(f"internal_refs={stats['internal_refs']}")
    print(f"external_links={stats['external_links']}")
    print(f"affiliate_pages={stats['affiliate_pages']}")
    print(f"affiliate_links={stats['affiliate_links']}")
    print(f"issues={len(issues)}")
    for issue in issues[:200]:
        print(issue)
    if len(issues) > 200:
        print(f"... {len(issues) - 200} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
