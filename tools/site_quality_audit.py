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
OFFICIAL_YOUTUBE_CHANNEL = "https://www.youtube.com/channel/UCPeQjvN9q2kY2s09PuRSL6w"
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
FORBIDDEN_SPANISH_VISIBLE_SNIPPETS = {
    "Jardin del Corazon",
    "guias, recursos",
    "plan de reparacion",
    "paginas de confianza",
    "a donde ir despues",
    "reparacion pequena",
    "peticion pequena",
    "7 dias",
    "segun tu",
    "mas rapido",
    "Confianza y limites",
    "Sobre el Jardin",
    "Teoria de lenguajes",
    "Privacidad y terminos",
}
FORBIDDEN_NON_EN_UNIVERSE_LABELS = {
    "AFTER THE RITUAL",
    "ABOUT LOVETYPES",
    "BOOK RELICS",
    "404 HEART GARDEN",
    "CALM PATHS",
    "CHOOSE BY CURRENT NEED",
    "DESTINY RITUAL",
    "FIELD GUIDES",
    "FIVE DOMAINS",
    "FIVE GUARDIANS",
    "FIVE-DOMAIN THEORY COMPASS",
    "FULL POLICY NOTES",
    "FUNCTION ROOMS",
    "GARDEN JOURNEY",
    "GARDEN REPAIR DESK",
    "GUARDIAN COMPASS",
    "GUARDIAN FIELD GUIDES",
    "GUARDIAN KEEPSAKE HALL",
    "GUARDIAN KEEPSAKES",
    "GUARDIAN NIGHT SUPPLY",
    "GUARDIAN READING ROUTES",
    "GUARDIAN ROUTES",
    "HEART GARDEN SUPPLIES",
    "HEART GARDEN FIELD GUIDE",
    "HEART GARDEN FIELD NOTES",
    "HEART GARDEN MAP",
    "HEART GARDEN PASS",
    "HEART GARDEN PORTALS",
    "HEART GARDEN TRUST CHARTER",
    "HEART GARDEN ARCHIVE",
    "LOVE LANGUAGE FAQ",
    "LOVE LANGUAGE THEORY",
    "LUNA NIGHT SUPPLY",
    "LUNA SUPPLY ENTRY",
    "MAIN ROUTES",
    "MOONLIGHT SUPPLY",
    "NIGHT HEART SUPPLY",
    "NIGHT SUPPLY PROTOCOL",
    "PRINTABLE WORKSHEET",
    "READING COMPASS",
    "REQUEST COMPASS",
    "RETURN PATH",
    "SAFETY BOUNDARY MAP",
    "SAFE ROUTES",
    "SAVE · BLESS · RETURN",
    "SAVE · SHARE · RETURN",
    "7-DAY HEART-LANGUAGE PLAN",
    "START FROM YOUR RESULT",
    "STARTER KIT",
    "SUPPLY COMPASS",
    "SUPPLY ROUTE",
    "SUPPLY WISHLIST",
    "TRAVELER SUPPLY",
    "RELATED GUIDES",
    "TRUST ROUTES",
    "UNIVERSE PROMISE",
    "WEEK ROUTE",
    "YOUR NIGHT SUPPLY",
}
POLICY_UPDATED_LABELS = {
    "zh": "更新日期:",
    "en": "Updated:",
    "ja": "更新日:",
    "ko": "업데이트:",
    "es": "Actualización:",
}
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
MAX_H2_TEXT_LENGTH = 72
BOOKS_AFFILIATE_HOST = "www.books.com.tw"
BOOKS_AFFILIATE_PATH_PREFIX = "/exep/assp.php/arthur0858/products/"
BOOKS_AFFILIATE_REQUIRED_QUERY = {
    "utm_source": "arthur0858",
    "utm_medium": "ap-books",
    "utm_content": "recommend",
    "utm_campaign": "ap-202604",
}
AMAZON_AFFILIATE_HOST = "www.amazon.com"
AMAZON_ASSOCIATE_TAG = "parenttechche-20"
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
HUMANS_PATH = ROOT / "humans.txt"
MANIFEST_PATH = ROOT / "site.webmanifest"
FUNNEL_EVENTS_PATH = ROOT / "funnel-events.json"
COMMERCE_CATALOG_PATH = ROOT / "commerce-catalog.json"
PROMOTION_KIT_PATH = ROOT / "promotion-kit.json"
SITE_INDEX_PATH = ROOT / "site-index.json"
GUARDIAN_PROFILES_PATH = ROOT / "guardian-profiles.json"
SITE_HEALTH_PATH = ROOT / "site-health.json"
RELEASE_PATH = ROOT / "release.json"
SAFETY_INDEX_PATH = ROOT / "safety-index.json"
AI_DISCOVERY_PATH = ROOT / "ai-discovery.json"
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
EXPECTED_MANIFEST_SHORTCUT_URLS = {
    "/start/",
    "/garden-map/",
    "/characters/",
    "/resources/",
    "/keepsakes/",
    "/luna-yoga-music/",
}
EXPECTED_MANIFEST_SCREENSHOTS = {
    "/assets/lovetypes/pwa/home-desktop-screenshot.webp": (1440, 900),
    "/assets/lovetypes/pwa/home-mobile-screenshot.webp": (390, 844),
}
EXPECTED_APP_META = {
    "theme-color": "#7a4d6d",
    "application-name": "LoveTypes",
    "apple-mobile-web-app-title": "LoveTypes",
    "apple-mobile-web-app-capable": "yes",
    "apple-mobile-web-app-status-bar-style": "default",
    "mobile-web-app-capable": "yes",
}
REQUIRED_GLOBAL_HEADERS = {
    "Cache-Control": "public, max-age=600",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "SAMEORIGIN",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'; form-action 'self' mailto:; upgrade-insecure-requests",
}
IMMUTABLE_HEADER_PATHS = {
    "/assets/*",
    "/shared-*.css",
    "/site-interactions-*.js",
    "/deferred-external-*.js",
    "/quiz-data-*.js",
}
LEGACY_ROOT_STATIC_ASSETS = {
    "shared.css",
    "site-interactions.js",
    "deferred-external.js",
}
LIVE_REGION_DATA_ATTRS = {
    "data-contact-saved",
    "data-garden-map-saved",
    "data-guide-saved",
    "data-guardian-saved",
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
    "/images/characters/iris.webp": ("/assets/lovetypes/guardians/iris.webp", "301"),
    "/images/characters/noah.webp": ("/assets/lovetypes/guardians/noah.webp", "301"),
    "/images/characters/vivian.webp": ("/assets/lovetypes/guardians/vivian.webp", "301"),
    "/images/characters/claire.webp": ("/assets/lovetypes/guardians/claire.webp", "301"),
    "/images/characters/dora.webp": ("/assets/lovetypes/guardians/dora.webp", "301"),
    "/assets/lovetypes/share/iris-story.webp": ("/assets/lovetypes/share/iris-story-zh.webp", "301"),
    "/assets/lovetypes/share/noah-story.webp": ("/assets/lovetypes/share/noah-story-zh.webp", "301"),
    "/assets/lovetypes/share/vivian-story.webp": ("/assets/lovetypes/share/vivian-story-zh.webp", "301"),
    "/assets/lovetypes/share/claire-story.webp": ("/assets/lovetypes/share/claire-story-zh.webp", "301"),
    "/assets/lovetypes/share/dora-story.webp": ("/assets/lovetypes/share/dora-story-zh.webp", "301"),
        "/luna-yoga-music/luna.css": ("/shared-20260605-contrast.css", "301"),
    "/assets/lovetypes/guides/lovetypes-guide-toolkit.webp": ("/assets/lovetypes/share/guide-toolkit-og.jpg", "301"),
    "/assets/lovetypes/backgrounds/quiz-desk.webp": ("/assets/lovetypes/backgrounds/guardian-garden.webp", "301"),
    "/assets/lovetypes/backgrounds/quiz-desk-mobile.webp": ("/assets/lovetypes/backgrounds/guardian-garden-mobile.webp", "301"),
    "/og-cover.webp": ("/og-cover.jpg", "301"),
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
EXPECTED_ORGANIZATION_SAME_AS = {OFFICIAL_YOUTUBE_CHANNEL}
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
EXPECTED_ADS_TXT = f"google.com, {ADSENSE_ACCOUNT}, DIRECT, f08c47fec0942fa0"
FORMAL_GUIDE_GUARDIANS = {guide["slug"]: guide["guardian"] for guide in GENERATOR_CONFIG.GUIDES}
LEGACY_ZH_GUIDE_TARGETS = {slug: target for slug, _title, _desc, target in GENERATOR_CONFIG.LEGACY_ZH_GUIDES}
CURRENT_STATIC_ASSETS = {
    "css": GENERATOR_CONFIG.CSS_ASSET,
    "interactions": GENERATOR_CONFIG.INTERACTIONS_ASSET,
    "affiliate": GENERATOR_CONFIG.AFFILIATE_ASSET,
}
CURRENT_QUIZ_DATA_ASSETS = GENERATOR_CONFIG.QUIZ_DATA_ASSETS
EXPECTED_REDIRECTS["/luna-yoga-music/luna.css"] = (GENERATOR_CONFIG.CSS_ASSET, "301")
CONTACT_REQUEST_SUBJECTS = {
    lang: {
        GENERATOR_CONFIG.CONTACT_REQUESTS[lang]["subject"],
        GENERATOR_CONFIG.CONTACT_REPAIR_REPORTS[lang]["subject"],
    }
    for lang in LOCALE_PREFIXES
}
SUPPLY_WISHLIST_SUBJECTS = {
    lang: GENERATOR_CONFIG.SUPPLY_WISHLIST[lang]["subject"]
    for lang in LOCALE_PREFIXES
}
GUARDIAN_DOMAIN_TITLES = {
    (lang, slug): data[lang][0]
    for slug, data in GENERATOR_CONFIG.GUARDIAN_DOMAINS.items()
    for lang in LOCALE_PREFIXES
}
GUARDIAN_DOMAIN_MOTIFS = {
    data["motif"] for data in GENERATOR_CONFIG.GUARDIAN_DOMAINS.values()
}
REQUIRED_INTERACTION_HASH_SNIPPETS = {
    "samePageHash": "same-page hash link detection",
    "focusHashTarget": "hash target focus handoff",
    "scrollToHashTarget": "hash target scrolling",
    "prefers-reduced-motion: reduce": "reduced motion hash scrolling",
    "window.history.pushState": "same-page hash history update",
    "lovetypes:campaign-attribution:v1": "campaign attribution storage",
    "utm_campaign": "campaign UTM capture",
    "campaign: campaign": "funnel payload campaign attachment",
    "campaign_landing": "campaign landing funnel event",
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
        self.funnel_actions: list[tuple[str, dict[str, str]]] = []
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
        if "data-funnel-event" in data:
            self.funnel_actions.append((tag, data))
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
    if section not in {"garden-map", "guides", "characters", "theory", "resources", "about"}:
        return None
    return f"/{prefix}/{section}/" if prefix else f"/{section}/"


def is_resources_page(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts == ["resources", "index.html"]


def is_garden_map_page(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts == ["garden-map", "index.html"]


def is_guides_index_page(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts == ["guides", "index.html"]


def is_characters_index_page(page: Path) -> bool:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts.pop(0)
    return parts == ["characters", "index.html"]


def is_character_detail_page(page: Path) -> bool:
    parts = normalized_page_parts(page)
    return len(parts) == 3 and parts[0] == "characters" and parts[1] in GUARDIAN_SLUGS and parts[2] == "index.html"


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


def lang_key_for_page(page: Path) -> str:
    relative = page.relative_to(ROOT)
    parts = list(relative.parts)
    return parts[0] if parts and parts[0] in {"en", "ja", "ko", "es"} else "zh"


def class_tokens(attrs: dict[str, str]) -> set[str]:
    return set(attrs.get("class", "").split())


def is_books_affiliate(parsed) -> bool:
    if parsed.scheme != "https" or parsed.hostname != BOOKS_AFFILIATE_HOST:
        return False
    if not parsed.path.startswith(BOOKS_AFFILIATE_PATH_PREFIX):
        return False
    query = parse_qs(parsed.query)
    return all(query.get(key, [""])[0] == value for key, value in BOOKS_AFFILIATE_REQUIRED_QUERY.items())


def is_amazon_affiliate(parsed) -> bool:
    if parsed.scheme != "https" or parsed.hostname != AMAZON_AFFILIATE_HOST:
        return False
    if not parsed.path.startswith("/dp/"):
        return False
    return parse_qs(parsed.query).get("tag", [""])[0] == AMAZON_ASSOCIATE_TAG


def is_affiliate_url_for_lang(value: str, lang: str) -> bool:
    parsed = urlparse(value)
    if lang == "zh":
        return is_books_affiliate(parsed)
    return is_amazon_affiliate(parsed)


def affiliate_provider(parsed) -> str:
    if parsed.hostname == BOOKS_AFFILIATE_HOST:
        return "books"
    if parsed.hostname == AMAZON_AFFILIATE_HOST:
        return "amazon"
    return ""


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
        same_as = organizations[0].get("sameAs", [])
        if not isinstance(same_as, list) or not EXPECTED_ORGANIZATION_SAME_AS.issubset(set(same_as)):
            issues.append(f"{page}: Organization JSON-LD missing official sameAs links")
        knows_about = organizations[0].get("knowsAbout", [])
        if not isinstance(knows_about, list) or len(knows_about) < 3:
            issues.append(f"{page}: Organization JSON-LD should include brand topic coverage")
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


def canonical_url_without_fragment(value: str) -> str:
    parsed = urlparse(value)
    path = parsed.path or "/"
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def walk_index_urls(data: object, path: str = "$") -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            child_path = f"{path}.{key}"
            if isinstance(value, str):
                if value.startswith(DOMAIN) or value.startswith("/"):
                    urls.append((child_path, value))
            else:
                urls.extend(walk_index_urls(value, child_path))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            child_path = f"{path}[{index}]"
            if isinstance(value, str):
                if value.startswith(DOMAIN) or value.startswith("/"):
                    urls.append((child_path, value))
            else:
                urls.extend(walk_index_urls(value, child_path))
    return urls


def validate_index_url(
    source: Path,
    field_path: str,
    value: str,
    parsers: dict[Path, PageParser],
    sitemap_urls: set[str],
    stats: Counter,
) -> list[str]:
    issues: list[str] = []
    stats["discovery_cross_index_urls_checked"] += 1
    url = f"{DOMAIN}{value}" if value.startswith("/") else value
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw":
        issues.append(f"{source}: {field_path} should use https://lovetypes.tw URL or absolute local path: {value}")
        return issues

    target, fragment = target_for(ROOT / "index.html", url)
    if target is None or not target.exists():
        issues.append(f"{source}: {field_path} target missing: {value}")
        return issues
    stats["discovery_cross_index_targets_checked"] += 1

    if target.suffix != ".html":
        return issues

    parser = parsers.get(target)
    if parser and is_noindex(parser):
        issues.append(f"{source}: {field_path} should not point to noindex HTML: {value}")
    if fragment:
        stats["discovery_cross_index_fragments_checked"] += 1
        if parser and fragment not in parser.ids:
            issues.append(f"{source}: {field_path} fragment missing #{fragment}: {value}")
        base_url = canonical_url_without_fragment(url)
        if base_url not in sitemap_urls:
            issues.append(f"{source}: {field_path} fragment base missing from sitemap: {base_url}")
        return issues

    canonical = public_url_for_page(target)
    if canonical not in sitemap_urls:
        issues.append(f"{source}: {field_path} HTML route missing from sitemap: {canonical}")
    elif parser:
        canonicals = parser.links_with_rel("canonical")
        if len(canonicals) == 1 and canonicals[0].get("href") != canonical:
            issues.append(f"{source}: {field_path} target canonical mismatch: {value}")
    return issues


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

    screenshots = manifest.get("screenshots", [])
    if not isinstance(screenshots, list) or len(screenshots) != len(EXPECTED_MANIFEST_SCREENSHOTS):
        issues.append(
            f"{MANIFEST_PATH}: expected {len(EXPECTED_MANIFEST_SCREENSHOTS)} screenshots, "
            f"got {len(screenshots) if isinstance(screenshots, list) else 'invalid'}"
        )
        screenshots = []
    screenshot_srcs = {
        screenshot.get("src")
        for screenshot in screenshots
        if isinstance(screenshot, dict) and isinstance(screenshot.get("src"), str)
    }
    missing_screenshots = sorted(EXPECTED_MANIFEST_SCREENSHOTS.keys() - screenshot_srcs)
    if missing_screenshots:
        issues.append(f"{MANIFEST_PATH}: missing expected screenshots {', '.join(missing_screenshots)}")
    for screenshot in screenshots:
        stats["manifest_screenshots"] += 1
        if not isinstance(screenshot, dict):
            issues.append(f"{MANIFEST_PATH}: screenshot entry should be an object")
            continue
        src = screenshot.get("src", "")
        sizes = screenshot.get("sizes", "")
        image_type = screenshot.get("type", "")
        if not src or not sizes or not image_type:
            issues.append(f"{MANIFEST_PATH}: screenshot missing src, sizes, or type: {screenshot}")
            continue
        if image_type != "image/webp":
            issues.append(f"{MANIFEST_PATH}: screenshot should be image/webp: {src}")
        target = ROOT / unquote(src.lstrip("/"))
        if not target.exists():
            issues.append(f"{MANIFEST_PATH}: screenshot target missing: {src}")
            continue
        expected_size = EXPECTED_MANIFEST_SCREENSHOTS.get(src)
        actual_size = image_size(target)
        if expected_size and actual_size != expected_size:
            issues.append(f"{MANIFEST_PATH}: screenshot {src} should be {expected_size[0]}x{expected_size[1]}, got {actual_size}")
        if actual_size:
            actual_size_label = f"{actual_size[0]}x{actual_size[1]}"
            if sizes != actual_size_label:
                issues.append(f"{MANIFEST_PATH}: screenshot sizes should be {actual_size_label}: {src}")

    shortcuts = manifest.get("shortcuts", [])
    if shortcuts and not isinstance(shortcuts, list):
        issues.append(f"{MANIFEST_PATH}: shortcuts should be a list")
        shortcuts = []
    shortcut_urls = {
        shortcut.get("url")
        for shortcut in shortcuts
        if isinstance(shortcut, dict) and isinstance(shortcut.get("url"), str)
    }
    missing_shortcuts = sorted(EXPECTED_MANIFEST_SHORTCUT_URLS.difference(shortcut_urls))
    if missing_shortcuts:
        issues.append(f"{MANIFEST_PATH}: missing expected shortcut URLs {', '.join(missing_shortcuts)}")
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
        "## AI Discovery Files",
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
        "Traditional Chinese pages use Books.com.tw affiliate URLs": "localized affiliate boundary",
        "Amazon Associates tag parenttechche-20": "Amazon Associates boundary",
        "Generative answer index: /ai-discovery.json": "AI discovery index",
    }
    for snippet, label in required_snippets.items():
        stats["llms_snippets_checked"] += 1
        if snippet not in text:
            issues.append(f"{LLMS_PATH}: missing {label}: {snippet!r}")

    high_value_urls = {
        f"{DOMAIN}/",
        f"{DOMAIN}/garden-map/",
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


def parse_humans_txt(parsers: dict[Path, PageParser], sitemap_urls: set[str]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not HUMANS_PATH.exists():
        return [f"{HUMANS_PATH}: missing humans.txt"], stats

    text = HUMANS_PATH.read_text(encoding="utf-8", errors="ignore")
    stats["humans_files_checked"] = 1
    stats["humans_lines"] = len(text.splitlines())

    required_sections = [
        "/* TEAM */",
        "/* SITE */",
        "/* HIGH-VALUE ROUTES */",
    ]
    for section in required_sections:
        stats["humans_sections_checked"] += 1
        if section not in text:
            issues.append(f"{HUMANS_PATH}: missing required section {section!r}")

    required_snippets = {
        "Site: LoveTypes": "site identity",
        f"Contact: {CONTACT_EMAIL}": "contact email",
        f"Production: {DOMAIN}/": "production URL",
        f"Updated: {GENERATOR_CONFIG.UPDATED}": "generator updated date",
        "Languages: zh-TW, en, ja, ko, es": "language coverage",
        "Generator: tools/generate_multilingual_site.py": "source generator",
        "Hosting: Cloudflare Pages": "hosting platform",
        "Resources may contain localized affiliate links": "affiliate disclosure",
        "Luna packs use Gumroad purchase links": "Luna product disclosure",
        "not therapy, medical, legal, or diagnostic advice": "safety boundary",
    }
    for snippet, label in required_snippets.items():
        stats["humans_snippets_checked"] += 1
        if snippet not in text:
            issues.append(f"{HUMANS_PATH}: missing {label}: {snippet!r}")

    required_urls = {
        f"{DOMAIN}/",
        f"{DOMAIN}/garden-map/",
        f"{DOMAIN}/characters/",
        f"{DOMAIN}/resources/",
        f"{DOMAIN}/keepsakes/",
        f"{DOMAIN}/luna-yoga-music/",
        f"{DOMAIN}/contact/",
    }
    for url in required_urls:
        stats["humans_high_value_urls_checked"] += 1
        if url not in text:
            issues.append(f"{HUMANS_PATH}: missing high-value URL {url}")

    for forbidden in FORBIDDEN_CONTACT_SNIPPETS | FORBIDDEN_ADSENSE_SCRIPT_SNIPPETS:
        if forbidden in text:
            issues.append(f"{HUMANS_PATH}: forbidden snippet should not appear: {forbidden}")

    humans_urls = sorted(set(extract_llms_urls(text)))
    stats["humans_urls_checked"] = len(humans_urls)
    for url in humans_urls:
        target, fragment = target_for(ROOT / "index.html", url)
        if target is None or not target.exists():
            issues.append(f"{HUMANS_PATH}: listed URL target missing: {url}")
            continue
        if fragment and target.suffix == ".html":
            target_parser = parsers.get(target)
            if target_parser and fragment not in target_parser.ids:
                issues.append(f"{HUMANS_PATH}: listed URL missing anchor #{fragment}: {url}")
        if target.suffix == ".html":
            target_parser = parsers.get(target)
            if target_parser and is_noindex(target_parser):
                issues.append(f"{HUMANS_PATH}: listed URL should not point to noindex page: {url}")
        if not fragment and url not in sitemap_urls:
            issues.append(f"{HUMANS_PATH}: listed URL missing from sitemap: {url}")

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


def parse_funnel_event_catalog() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not FUNNEL_EVENTS_PATH.exists():
        return [f"{FUNNEL_EVENTS_PATH}: missing funnel-events.json"], stats
    try:
        data = json.loads(FUNNEL_EVENTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{FUNNEL_EVENTS_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{FUNNEL_EVENTS_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{FUNNEL_EVENTS_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{FUNNEL_EVENTS_PATH}: updated should match generator date")
    if data.get("localStorageKey") != "lovetypes:funnel-events:v1":
        issues.append(f"{FUNNEL_EVENTS_PATH}: localStorageKey should match runtime storage key")
    events = data.get("events")
    if not isinstance(events, list) or not events:
        issues.append(f"{FUNNEL_EVENTS_PATH}: events should be a non-empty list")
        return issues, stats
    stats["funnel_event_catalogs_checked"] = 1
    stats["funnel_events_checked"] = len(events)
    required_events = {
        "quiz_result_supply_route",
        "quiz_result_repair_plan",
        "quiz_result_luna",
        "quiz_result_contact",
        "supply_route_affiliate_book",
        "luna_gumroad_pack_click",
        "luna_hero_listen",
        "contact_supply_mailto",
        "free_keepsake_download",
        "campaign_landing",
    }
    seen: set[str] = set()
    categories: set[str] = set()
    roles: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            issues.append(f"{FUNNEL_EVENTS_PATH}: event entry should be an object")
            continue
        name = event.get("name")
        if not isinstance(name, str) or not re.match(r"^[a-z][a-z0-9_]*$", name):
            issues.append(f"{FUNNEL_EVENTS_PATH}: invalid event name {name!r}")
            continue
        if name in seen:
            issues.append(f"{FUNNEL_EVENTS_PATH}: duplicate event name {name}")
        seen.add(name)
        count = event.get("count")
        if not isinstance(count, int) or count <= 0:
            issues.append(f"{FUNNEL_EVENTS_PATH}: event {name} should include positive count")
        pages = event.get("pages")
        page_count = event.get("pageCount")
        if not isinstance(pages, list) or not pages:
            issues.append(f"{FUNNEL_EVENTS_PATH}: event {name} should include pages")
        if not isinstance(page_count, int) or page_count < len(pages or []):
            issues.append(f"{FUNNEL_EVENTS_PATH}: event {name} should include valid pageCount")
        category = event.get("category")
        role = event.get("role")
        if not isinstance(category, str) or not category:
            issues.append(f"{FUNNEL_EVENTS_PATH}: event {name} missing category")
        else:
            categories.add(category)
        if not isinstance(role, str) or not role:
            issues.append(f"{FUNNEL_EVENTS_PATH}: event {name} missing role")
        else:
            roles.add(role)
        if name == "luna_gumroad_pack_click" and role != "revenue":
            issues.append(f"{FUNNEL_EVENTS_PATH}: luna_gumroad_pack_click should be a revenue event")
    missing = sorted(required_events.difference(seen))
    if missing:
        issues.append(f"{FUNNEL_EVENTS_PATH}: missing core funnel events: {', '.join(missing)}")
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("events") != len(events):
        issues.append(f"{FUNNEL_EVENTS_PATH}: totals.events should match event count")
    stats["funnel_event_categories_checked"] = len(categories)
    stats["funnel_event_roles_checked"] = len(roles)
    if len(events) < 50:
        issues.append(f"{FUNNEL_EVENTS_PATH}: expected at least 50 funnel events, got {len(events)}")
    return issues, stats


def funnel_event_names() -> set[str]:
    if not FUNNEL_EVENTS_PATH.exists():
        return set()
    try:
        data = json.loads(FUNNEL_EVENTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    events = data.get("events", []) if isinstance(data, dict) else []
    return {
        event.get("name")
        for event in events
        if isinstance(event, dict) and isinstance(event.get("name"), str)
    }


def check_funnel_event_markup(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    catalog_names = funnel_event_names()
    seen_event_names: set[str] = set()
    required_markup_events = {
        "supply_route_affiliate_book",
        "luna_gumroad_pack_click",
        "contact_supply_mailto",
        "free_keepsake_download",
    }
    for page, parser in parsers.items():
        for tag, attrs in parser.funnel_actions:
            stats["funnel_markup_actions_checked"] += 1
            event_name = attrs.get("data-funnel-event", "")
            if not re.match(r"^[a-z][a-z0-9_]*$", event_name):
                issues.append(f"{page}: invalid data-funnel-event name {event_name!r}")
            if event_name not in catalog_names:
                issues.append(f"{page}: data-funnel-event missing from funnel-events.json: {event_name}")
            else:
                seen_event_names.add(event_name)
            if tag not in {"a", "button"}:
                issues.append(f"{page}: data-funnel-event should be on a or button, got <{tag}> for {event_name}")

            href = attrs.get("href", "")
            is_copy_action = "copy" in event_name or "data-copy-text" in attrs or "data-route-summary" in attrs
            is_story_action = event_name.endswith("story_generate") or event_name.endswith("story_download")
            is_print_action = "print" in event_name
            if tag == "a":
                if not href:
                    issues.append(f"{page}: link funnel event {event_name} missing href")
                elif href.startswith("#"):
                    target_id = href[1:]
                    if target_id not in parser.ids:
                        issues.append(f"{page}: link funnel event {event_name} points to missing anchor {href}")
                elif href.startswith("mailto:"):
                    pass
                elif href.startswith(("http://", "https://", "/")):
                    target, fragment = target_for(page, href)
                    if target is not None:
                        if not target.exists():
                            issues.append(f"{page}: link funnel event {event_name} target missing: {href}")
                        elif fragment and target.suffix == ".html":
                            target_parser = parsers.get(target)
                            if target_parser and fragment not in target_parser.ids:
                                issues.append(f"{page}: link funnel event {event_name} target missing anchor #{fragment}: {href}")
                else:
                    issues.append(f"{page}: link funnel event {event_name} has unsupported href {href!r}")
            elif tag == "button" and not (is_copy_action or is_story_action or is_print_action):
                issues.append(f"{page}: button funnel event {event_name} should be a copy/story action")

            if "mailto" in event_name:
                if not href.startswith(f"mailto:{CONTACT_EMAIL}"):
                    issues.append(f"{page}: mailto funnel event {event_name} should send to {CONTACT_EMAIL}")
                parsed_mail = urlparse(href)
                query = parse_qs(parsed_mail.query)
                if not query.get("subject") or not query.get("body"):
                    issues.append(f"{page}: mailto funnel event {event_name} should include subject and body")
                stats["funnel_markup_mailtos_checked"] += 1
            if "luna" in event_name and "pack_click" in event_name:
                if not attrs.get("data-luna-product"):
                    issues.append(f"{page}: Luna pack funnel event {event_name} missing data-luna-product")
                stats["funnel_markup_luna_products_checked"] += 1
            if is_copy_action:
                if not (attrs.get("data-copy-text") or attrs.get("data-route-summary")):
                    issues.append(f"{page}: copy funnel event {event_name} missing copy payload")
                stats["funnel_markup_copy_actions_checked"] += 1
            if event_name.endswith("story_generate"):
                required_story_attrs = {
                    "data-story-name",
                    "data-story-title",
                    "data-story-quote",
                    "data-story-image",
                    "data-story-slug",
                    "data-story-cta",
                }
                missing_story_attrs = sorted(attr for attr in required_story_attrs if not attrs.get(attr))
                if missing_story_attrs:
                    issues.append(f"{page}: story funnel event {event_name} missing {', '.join(missing_story_attrs)}")
                stats["funnel_markup_story_actions_checked"] += 1

    stats["funnel_markup_event_names_checked"] = len(seen_event_names)
    missing_required = sorted(required_markup_events.difference(seen_event_names))
    if missing_required:
        issues.append(f"HTML funnel markup missing required events: {', '.join(missing_required)}")
    return issues, stats


def parse_commerce_catalog(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not COMMERCE_CATALOG_PATH.exists():
        return [f"{COMMERCE_CATALOG_PATH}: missing commerce-catalog.json"], stats
    try:
        data = json.loads(COMMERCE_CATALOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{COMMERCE_CATALOG_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{COMMERCE_CATALOG_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{COMMERCE_CATALOG_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{COMMERCE_CATALOG_PATH}: updated should match generator date")
    if data.get("contact") != CONTACT_EMAIL:
        issues.append(f"{COMMERCE_CATALOG_PATH}: contact should be {CONTACT_EMAIL}")
    if data.get("production") != f"{DOMAIN}/":
        issues.append(f"{COMMERCE_CATALOG_PATH}: production should be {DOMAIN}/")
    boundaries = data.get("safetyBoundaries")
    if not isinstance(boundaries, list) or len(boundaries) < 4:
        issues.append(f"{COMMERCE_CATALOG_PATH}: safetyBoundaries should include at least four entries")
    else:
        boundary_text = " ".join(str(item) for item in boundaries)
        for snippet in ("No therapeutic", "Affiliate links", "Email waitlist", "sensitive personal details"):
            stats["commerce_safety_boundaries_checked"] += 1
            if snippet not in boundary_text:
                issues.append(f"{COMMERCE_CATALOG_PATH}: missing safety boundary snippet {snippet!r}")

    items = data.get("items")
    if not isinstance(items, list) or not items:
        issues.append(f"{COMMERCE_CATALOG_PATH}: items should be a non-empty list")
        return issues, stats
    playbook = data.get("revenuePlaybook")
    if not isinstance(playbook, list) or len(playbook) < 4:
        issues.append(f"{COMMERCE_CATALOG_PATH}: revenuePlaybook should include at least four plays")
    else:
        stats["commerce_revenue_playbook_checked"] = len(playbook)
        expected_play_ids = {"identity_retention_first", "owned_supply_lead", "affiliate_book_revenue", "luna_pack_revenue"}
        play_ids = {play.get("id") for play in playbook if isinstance(play, dict)}
        if not expected_play_ids.issubset(play_ids):
            issues.append(f"{COMMERCE_CATALOG_PATH}: revenuePlaybook missing play ids {sorted(expected_play_ids.difference(play_ids))}")
        for play in playbook:
            if not isinstance(play, dict):
                issues.append(f"{COMMERCE_CATALOG_PATH}: revenuePlaybook entries should be objects")
                continue
            for key in ("role", "itemTypes", "recommendedAfter", "primaryEvents", "useWhen", "nextStep", "doNotUseWhen"):
                if not play.get(key):
                    issues.append(f"{COMMERCE_CATALOG_PATH}: revenue play {play.get('id') or '<unknown>'} missing {key}")
    stats["commerce_catalogs_checked"] = 1
    stats["commerce_items_checked"] = len(items)
    if len(items) != 20:
        issues.append(f"{COMMERCE_CATALOG_PATH}: expected 20 commerce items, got {len(items)}")

    expected_type_counts = {
        "free_keepsake": 5,
        "owned_supply_waitlist": 5,
        "affiliate_book": 4,
        "luna_gumroad_pack": 6,
    }
    expected_role_counts = {"lead": 5, "retention": 5, "revenue": 10}
    type_counts = Counter()
    role_counts = Counter()
    seen_ids: set[str] = set()
    guardian_slugs = set(GENERATOR_CONFIG.GUARDIANS)
    playbook_by_type = {
        item_type: play
        for play in (playbook if isinstance(playbook, list) else [])
        if isinstance(play, dict)
        for item_type in play.get("itemTypes", [])
    }
    for item in items:
        if not isinstance(item, dict):
            issues.append(f"{COMMERCE_CATALOG_PATH}: item should be an object")
            continue
        item_id = item.get("id")
        item_type = item.get("type")
        role = item.get("role")
        url = item.get("url")
        if not isinstance(item_id, str) or not item_id:
            issues.append(f"{COMMERCE_CATALOG_PATH}: item missing id")
            continue
        if item_id in seen_ids:
            issues.append(f"{COMMERCE_CATALOG_PATH}: duplicate item id {item_id}")
        seen_ids.add(item_id)
        if item_type not in expected_type_counts:
            issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} unexpected type {item_type!r}")
        else:
            type_counts[item_type] += 1
        if role not in expected_role_counts:
            issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} unexpected role {role!r}")
        else:
            role_counts[role] += 1
        if not isinstance(item.get("title"), dict) or not item["title"].get("zh") or not item["title"].get("en"):
            issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should include zh/en title")
        if not isinstance(item.get("conversion"), str) or not item["conversion"]:
            issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} missing conversion")
        if not isinstance(item.get("disclosure"), str) or not item["disclosure"]:
            issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} missing disclosure")
        play = playbook_by_type.get(item_type)
        if not play:
            issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} missing matching revenue playbook for type {item_type!r}")
        else:
            stats["commerce_item_playbook_links_checked"] += 1
            if item.get("playbookId") != play.get("id"):
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} playbookId should be {play.get('id')}")
            for key in ("recommendedAfter", "primaryEvents"):
                value = item.get(key)
                if not isinstance(value, list) or not value:
                    issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} missing {key}")
            for key in ("nextStep", "doNotUseWhen"):
                if not isinstance(item.get(key), str) or not item[key]:
                    issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} missing {key}")
        if not isinstance(url, str) or not url:
            issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} missing url")
            continue
        parsed = urlparse(url)
        if item_type in {"free_keepsake", "owned_supply_waitlist"}:
            if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw":
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should point to lovetypes.tw")
            target, fragment = target_for(ROOT / "index.html", url)
            if target is None or not target.exists():
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} target missing: {url}")
            elif fragment and target.suffix == ".html":
                target_parser = parsers.get(target)
                if target_parser and fragment not in target_parser.ids:
                    issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} target missing anchor #{fragment}")
            guardian = item.get("guardian")
            if guardian not in guardian_slugs:
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should include a valid guardian slug")
        elif item_type == "affiliate_book":
            if not is_amazon_affiliate(parsed):
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} primary url should be an Amazon Associates URL with tag={AMAZON_ASSOCIATE_TAG}")
            if item.get("amazonAssociateTag") != AMAZON_ASSOCIATE_TAG:
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should include amazonAssociateTag={AMAZON_ASSOCIATE_TAG}")
            if not isinstance(item.get("asin"), str) or not item["asin"]:
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should include asin")
            localized_urls = item.get("localizedUrls")
            if not isinstance(localized_urls, dict):
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should include localizedUrls")
            else:
                for lang in ("zh", "en", "ja", "ko", "es"):
                    localized_url = localized_urls.get(lang)
                    if not isinstance(localized_url, str) or not is_affiliate_url_for_lang(localized_url, lang):
                        expected = "tracked Books.com.tw" if lang == "zh" else f"Amazon Associates tag={AMAZON_ASSOCIATE_TAG}"
                        issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} localizedUrls.{lang} should use {expected}")
            taiwan_url = item.get("taiwanAffiliateUrl")
            if not isinstance(taiwan_url, str) or not is_affiliate_url_for_lang(taiwan_url, "zh"):
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should include a tracked Books.com.tw taiwanAffiliateUrl")
        elif item_type == "luna_gumroad_pack":
            if parsed.netloc != "lunayogamusic.gumroad.com":
                issues.append(f"{COMMERCE_CATALOG_PATH}: {item_id} should be a Luna Gumroad URL")

    stats["commerce_types_checked"] = len(type_counts)
    stats["commerce_roles_checked"] = len(role_counts)
    for item_type, expected in expected_type_counts.items():
        if type_counts[item_type] != expected:
            issues.append(f"{COMMERCE_CATALOG_PATH}: expected {expected} {item_type} items, got {type_counts[item_type]}")
    for role, expected in expected_role_counts.items():
        if role_counts[role] != expected:
            issues.append(f"{COMMERCE_CATALOG_PATH}: expected {expected} {role} items, got {role_counts[role]}")
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("items") != len(items):
        issues.append(f"{COMMERCE_CATALOG_PATH}: totals.items should match item count")
    return issues, stats


def parse_promotion_kit() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not PROMOTION_KIT_PATH.exists():
        return [f"{PROMOTION_KIT_PATH}: missing promotion-kit.json"], stats
    try:
        data = json.loads(PROMOTION_KIT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{PROMOTION_KIT_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{PROMOTION_KIT_PATH}: root should be an object"], stats
    expected_kpi_fields = {
        "views",
        "site_clicks",
        "quiz_starts",
        "quiz_completions",
        "free_keepsake_downloads",
        "supply_lead_requests",
        "luna_pack_clicks",
        "affiliate_book_clicks",
        "contact_requests",
    }
    kpi_fields = data.get("kpiFields")
    if not isinstance(kpi_fields, list) or not expected_kpi_fields.issubset(kpi_fields):
        issues.append(f"{PROMOTION_KIT_PATH}: kpiFields missing revenue bridge fields")
    platform_profile_setup = data.get("platformProfileSetup")
    expected_profile_sources = {
        "youtube_shorts": "youtube",
        "tiktok": "tiktok",
        "instagram_reels": "instagram",
    }
    if not isinstance(platform_profile_setup, list) or len(platform_profile_setup) != len(expected_profile_sources):
        issues.append(f"{PROMOTION_KIT_PATH}: platformProfileSetup should include three platform setups")
        platform_profile_setup = []
    seen_profile_platforms: set[str] = set()
    for item in platform_profile_setup:
        if not isinstance(item, dict):
            issues.append(f"{PROMOTION_KIT_PATH}: platformProfileSetup item should be an object")
            continue
        platform_id = item.get("platformId")
        expected_source = expected_profile_sources.get(platform_id)
        if not expected_source:
            issues.append(f"{PROMOTION_KIT_PATH}: unexpected platformProfileSetup platformId {platform_id!r}")
            continue
        seen_profile_platforms.add(platform_id)
        stats["promotion_platform_profile_setups_checked"] += 1
        parsed = urlparse(item.get("profileLink", ""))
        query = parse_qs(parsed.query)
        expected_query = {
            "utm_source": expected_source,
            "utm_medium": "social_profile",
            "utm_campaign": "first_round_quiz_completion",
            "utm_content": f"{platform_id}_bio",
        }
        if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
            issues.append(f"{PROMOTION_KIT_PATH}: {platform_id} profileLink should point to /start/")
        for key, expected_value in expected_query.items():
            if query.get(key, [""])[0] != expected_value:
                issues.append(f"{PROMOTION_KIT_PATH}: {platform_id} profileLink missing {key}={expected_value}")
        setup_text = f"{item.get('bio', '')} {item.get('pinnedComment', '')}"
        if "完成 15 題測驗" not in setup_text:
            issues.append(f"{PROMOTION_KIT_PATH}: {platform_id} setup copy should include quiz CTA")
        if any(word in setup_text for word in ("診斷", "療效", "保證修復", "必須購買")):
            issues.append(f"{PROMOTION_KIT_PATH}: {platform_id} setup copy should not include unsafe commercial claims")
        kpi_fields_to_fill = item.get("kpiFieldsToFill")
        if not isinstance(kpi_fields_to_fill, list) or not {"profile_clicks", "site_clicks", "quiz_starts", "quiz_completions"}.issubset(kpi_fields_to_fill):
            issues.append(f"{PROMOTION_KIT_PATH}: {platform_id} kpiFieldsToFill missing profile funnel fields")
        else:
            stats["promotion_platform_profile_kpi_fields_checked"] += len(kpi_fields_to_fill)
    if seen_profile_platforms != set(expected_profile_sources):
        issues.append(f"{PROMOTION_KIT_PATH}: platformProfileSetup missing platforms {sorted(set(expected_profile_sources) - seen_profile_platforms)}")
    measurement = data.get("measurementPlan")
    if not isinstance(measurement, dict):
        issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan should be an object")
        measurement = {}
    funnel_events: set[str] = set()
    if FUNNEL_EVENTS_PATH.exists():
        try:
            funnel_data = json.loads(FUNNEL_EVENTS_PATH.read_text(encoding="utf-8"))
            funnel_events = {
                event.get("name")
                for event in funnel_data.get("events", [])
                if isinstance(event, dict) and isinstance(event.get("name"), str)
            }
        except json.JSONDecodeError:
            funnel_events = set()
    bridge_kpis = measurement.get("revenueBridgeKpis")
    if not isinstance(bridge_kpis, list) or len(bridge_kpis) < 5:
        issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.revenueBridgeKpis should include at least five entries")
    else:
        stats["promotion_revenue_bridge_kpis_checked"] = len(bridge_kpis)
        bridge_fields = {item.get("field") for item in bridge_kpis if isinstance(item, dict)}
        expected_bridge_fields = {"free_keepsake_downloads", "supply_lead_requests", "luna_pack_clicks", "affiliate_book_clicks", "contact_requests"}
        if not expected_bridge_fields.issubset(bridge_fields):
            issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.revenueBridgeKpis missing expected fields")
        for item in bridge_kpis:
            if not isinstance(item, dict) or not item.get("playbookId") or not item.get("meaning"):
                issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.revenueBridgeKpis entries should include playbookId and meaning")
                break
    derived_rates = measurement.get("derivedRates")
    if not isinstance(derived_rates, list):
        issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.derivedRates should be a list")
    else:
        expected_rates = {"lead_capture_rate", "revenue_intent_rate", "keepsake_save_rate"}
        rate_ids = {item.get("id") for item in derived_rates if isinstance(item, dict)}
        if not expected_rates.issubset(rate_ids):
            issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.derivedRates missing revenue bridge rates")
    decision_rules = measurement.get("decisionRules")
    if not isinstance(decision_rules, list):
        issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.decisionRules should be a list")
    else:
        rule_ids = {item.get("id") for item in decision_rules if isinstance(item, dict)}
        if not {"build_owned_asset", "test_soft_offer"}.issubset(rule_ids):
            issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.decisionRules missing revenue bridge rules")
    event_kpi_map = measurement.get("eventKpiMap")
    expected_event_kpis = {
        "site_clicks",
        "quiz_starts",
        "quiz_completions",
        "guardian_result_clicks",
        "resources_clicks",
        "repair_plan_clicks",
        "luna_clicks",
        "keepsake_clicks",
        "free_keepsake_downloads",
        "supply_lead_requests",
        "luna_pack_clicks",
        "affiliate_book_clicks",
        "contact_requests",
    }
    if not isinstance(event_kpi_map, list):
        issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.eventKpiMap should be a list")
        event_kpi_map = []
    else:
        stats["promotion_event_kpi_rows_checked"] = len(event_kpi_map)
        seen_kpis: set[str] = set()
        mapped_events: set[str] = set()
        for row in event_kpi_map:
            if not isinstance(row, dict):
                issues.append(f"{PROMOTION_KIT_PATH}: eventKpiMap entries should be objects")
                continue
            kpi = row.get("kpi")
            if kpi in seen_kpis:
                issues.append(f"{PROMOTION_KIT_PATH}: duplicate eventKpiMap KPI {kpi}")
            if isinstance(kpi, str):
                seen_kpis.add(kpi)
            events = row.get("events")
            if not isinstance(events, list) or not events:
                issues.append(f"{PROMOTION_KIT_PATH}: eventKpiMap {kpi or '<unknown>'} should include events")
            else:
                for event_name in events:
                    if not isinstance(event_name, str) or not event_name:
                        issues.append(f"{PROMOTION_KIT_PATH}: eventKpiMap {kpi or '<unknown>'} has invalid event {event_name!r}")
                        continue
                    mapped_events.add(event_name)
                    if funnel_events and event_name not in funnel_events:
                        issues.append(f"{PROMOTION_KIT_PATH}: eventKpiMap {kpi or '<unknown>'} references missing funnel event {event_name}")
            for key in ("label", "countRule", "reviewUse"):
                if not isinstance(row.get(key), str) or not row[key]:
                    issues.append(f"{PROMOTION_KIT_PATH}: eventKpiMap {kpi or '<unknown>'} missing {key}")
            manual_sources = row.get("manualSources")
            if not isinstance(manual_sources, list) or not manual_sources:
                issues.append(f"{PROMOTION_KIT_PATH}: eventKpiMap {kpi or '<unknown>'} should include manualSources")
        stats["promotion_event_kpi_events_checked"] = len(mapped_events)
        missing_event_kpis = sorted(expected_event_kpis.difference(seen_kpis))
        if missing_event_kpis:
            issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.eventKpiMap missing KPI mappings {', '.join(missing_event_kpis)}")
    event_safety = measurement.get("eventKpiSafety")
    if not isinstance(event_safety, dict):
        issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.eventKpiSafety should be an object")
    else:
        for key in ("manualReviewRequired", "doNotInferPurchasesFromClicks", "doNotTreatGuardianAsDiagnosis"):
            if event_safety.get(key) is not True:
                issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.eventKpiSafety.{key} should be true")
        source_order = event_safety.get("sourceOfTruthOrder")
        if not isinstance(source_order, list) or len(source_order) < 4:
            issues.append(f"{PROMOTION_KIT_PATH}: measurementPlan.eventKpiSafety.sourceOfTruthOrder should include source priority")
    tasks = data.get("publishingTasks")
    if not isinstance(tasks, list) or len(tasks) != 15:
        issues.append(f"{PROMOTION_KIT_PATH}: expected 15 publishingTasks")
        return issues, stats

    expected_playbook_sequence = [
        "identity_retention_first",
        "owned_supply_lead",
        "luna_pack_revenue",
        "affiliate_book_revenue",
    ]
    expected_success_events = {
        "quiz_complete",
        "free_keepsake_download",
        "supply_route_asset_request",
        "luna_gumroad_pack_click",
        "supply_route_affiliate_book",
    }
    guardian_slugs = set(GENERATOR_CONFIG.GUARDIANS)
    stats["promotion_tasks_checked"] = len(tasks)
    for task in tasks:
        if not isinstance(task, dict):
            issues.append(f"{PROMOTION_KIT_PATH}: publishing task should be an object")
            continue
        task_id = task.get("taskId") or "<unknown>"
        guardian = task.get("guardianId")
        if guardian not in guardian_slugs:
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} unexpected guardianId {guardian!r}")
        conversion_path = task.get("conversionPath")
        if not isinstance(conversion_path, dict) or not conversion_path:
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} missing conversionPath")
        bridge = task.get("monetizationBridge")
        if not isinstance(bridge, dict):
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} missing monetizationBridge")
            continue
        stats["promotion_monetization_bridges_checked"] += 1
        if bridge.get("playbookSequence") != expected_playbook_sequence:
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} monetizationBridge.playbookSequence mismatch")
        if bridge.get("primaryFreeItemId") != f"free-keepsake-{guardian}":
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} primaryFreeItemId should match guardian")
        if bridge.get("ownedLeadItemId") != f"supply-wishlist-{guardian}":
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} ownedLeadItemId should match guardian")
        luna_products = bridge.get("lunaProductIds")
        if not isinstance(luna_products, list) or len(luna_products) != 6 or not all(isinstance(item, str) and item.startswith("luna-") for item in luna_products):
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} should include six Luna product ids")
        affiliate_items = bridge.get("affiliateItemIds")
        if not isinstance(affiliate_items, list) or len(affiliate_items) != 4 or not all(isinstance(item, str) and item.startswith("affiliate-book-") for item in affiliate_items):
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} should include four affiliate item ids")
        success_events = bridge.get("successEvents")
        if not isinstance(success_events, list) or not expected_success_events.issubset(set(success_events)):
            issues.append(f"{PROMOTION_KIT_PATH}: {task_id} monetizationBridge.successEvents incomplete")
        for key in ("recommendedFirstAction", "safetyNote"):
            if not isinstance(bridge.get(key), str) or not bridge[key]:
                issues.append(f"{PROMOTION_KIT_PATH}: {task_id} monetizationBridge missing {key}")
    return issues, stats


def parse_site_index(parsers: dict[Path, PageParser], sitemap_urls: set[str]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not SITE_INDEX_PATH.exists():
        return [f"{SITE_INDEX_PATH}: missing site-index.json"], stats
    try:
        data = json.loads(SITE_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{SITE_INDEX_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{SITE_INDEX_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{SITE_INDEX_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{SITE_INDEX_PATH}: updated should match generator date")
    if data.get("production") != f"{DOMAIN}/":
        issues.append(f"{SITE_INDEX_PATH}: production should be {DOMAIN}/")
    languages = data.get("languages")
    expected_langs = set(GENERATOR_CONFIG.LANGS)
    if not isinstance(languages, list) or len(languages) != len(expected_langs):
        issues.append(f"{SITE_INDEX_PATH}: expected {len(expected_langs)} languages")
    else:
        seen_langs = {item.get("id") for item in languages if isinstance(item, dict)}
        stats["site_index_languages_checked"] = len(seen_langs)
        if seen_langs != expected_langs:
            issues.append(f"{SITE_INDEX_PATH}: language ids should be {sorted(expected_langs)}, got {sorted(seen_langs)}")
    core_flows = data.get("coreFlows")
    if not isinstance(core_flows, list) or len(core_flows) != 5:
        issues.append(f"{SITE_INDEX_PATH}: expected five core flows")
    else:
        stats["site_index_core_flows_checked"] = len(core_flows)
        expected_flows = {"shorts_to_quiz", "quiz_to_guardian", "guardian_supply", "supply_to_contact", "trust_boundary"}
        seen_flows = {flow.get("id") for flow in core_flows if isinstance(flow, dict)}
        if seen_flows != expected_flows:
            issues.append(f"{SITE_INDEX_PATH}: core flow ids should be {sorted(expected_flows)}, got {sorted(seen_flows)}")
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        issues.append(f"{SITE_INDEX_PATH}: pages should be a non-empty list")
        return issues, stats
    stats["site_index_pages_checked"] = len(pages)
    if len(pages) != len(sitemap_urls):
        issues.append(f"{SITE_INDEX_PATH}: expected {len(sitemap_urls)} pages to match sitemap, got {len(pages)}")
    groups = Counter()
    canonicals: set[str] = set()
    valid_groups = {"home", "content", "guardians", "conversion", "trust"}
    for page in pages:
        if not isinstance(page, dict):
            issues.append(f"{SITE_INDEX_PATH}: page entry should be an object")
            continue
        canonical = page.get("canonical")
        lang = page.get("lang")
        group = page.get("group")
        if lang not in expected_langs:
            issues.append(f"{SITE_INDEX_PATH}: unexpected page language {lang!r}")
        if group not in valid_groups:
            issues.append(f"{SITE_INDEX_PATH}: unexpected page group {group!r}")
        else:
            groups[group] += 1
        if not isinstance(canonical, str) or not canonical:
            issues.append(f"{SITE_INDEX_PATH}: page missing canonical")
            continue
        if canonical in canonicals:
            issues.append(f"{SITE_INDEX_PATH}: duplicate canonical {canonical}")
        canonicals.add(canonical)
        target, fragment = target_for(ROOT / "index.html", canonical)
        if target is None or not target.exists():
            issues.append(f"{SITE_INDEX_PATH}: canonical target missing: {canonical}")
            continue
        if fragment:
            issues.append(f"{SITE_INDEX_PATH}: page canonical should not include fragment: {canonical}")
        parser = parsers.get(target)
        if parser and is_noindex(parser):
            issues.append(f"{SITE_INDEX_PATH}: canonical should not point to noindex page: {canonical}")
    stats["site_index_groups_checked"] = len(groups)
    missing_from_index = sorted(sitemap_urls.difference(canonicals))
    extra_in_index = sorted(canonicals.difference(sitemap_urls))
    for url in missing_from_index[:20]:
        issues.append(f"{SITE_INDEX_PATH}: sitemap URL missing from site index: {url}")
    for url in extra_in_index[:20]:
        issues.append(f"{SITE_INDEX_PATH}: site index canonical missing from sitemap: {url}")
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("pages") != len(pages):
        issues.append(f"{SITE_INDEX_PATH}: totals.pages should match page count")
    if isinstance(totals, dict) and totals.get("languages") != len(expected_langs):
        issues.append(f"{SITE_INDEX_PATH}: totals.languages should match language count")
    return issues, stats


def parse_guardian_profiles(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not GUARDIAN_PROFILES_PATH.exists():
        return [f"{GUARDIAN_PROFILES_PATH}: missing guardian-profiles.json"], stats
    try:
        data = json.loads(GUARDIAN_PROFILES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{GUARDIAN_PROFILES_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{GUARDIAN_PROFILES_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{GUARDIAN_PROFILES_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{GUARDIAN_PROFILES_PATH}: updated should match generator date")
    guardians = data.get("guardians")
    if not isinstance(guardians, list) or not guardians:
        issues.append(f"{GUARDIAN_PROFILES_PATH}: guardians should be a non-empty list")
        return issues, stats
    expected_languages = {
        "iris": ("肯定的言詞", "Words of affirmation"),
        "noah": ("優質的時光", "Quality time"),
        "vivian": ("接受禮物", "Receiving gifts"),
        "claire": ("服務的行動", "Acts of service"),
        "dora": ("身體的接觸", "Physical touch"),
    }
    seen_slugs: set[str] = set()
    stats["guardian_profiles_checked"] = len(guardians)
    if len(guardians) != len(expected_languages):
        issues.append(f"{GUARDIAN_PROFILES_PATH}: expected {len(expected_languages)} guardians, got {len(guardians)}")
    for guardian in guardians:
        if not isinstance(guardian, dict):
            issues.append(f"{GUARDIAN_PROFILES_PATH}: guardian entry should be an object")
            continue
        slug = guardian.get("slug")
        if slug not in expected_languages:
            issues.append(f"{GUARDIAN_PROFILES_PATH}: unexpected guardian slug {slug!r}")
            continue
        if slug in seen_slugs:
            issues.append(f"{GUARDIAN_PROFILES_PATH}: duplicate guardian slug {slug}")
        seen_slugs.add(slug)
        expected_zh, expected_en = expected_languages[slug]
        love_language = guardian.get("loveLanguage", {})
        if love_language.get("zh") != expected_zh or love_language.get("en") != expected_en:
            issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} love language mapping is incorrect")
        domain = guardian.get("domain", {})
        for key in ("motif", "accent", "glow", "name", "signal"):
            if key not in domain:
                issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} domain missing {key}")
        assets = guardian.get("assets", {})
        for key in ("portrait", "card", "prop", "story"):
            value = assets.get(key)
            stats["guardian_profile_assets_checked"] += 1
            if not isinstance(value, str) or not value.startswith("/"):
                issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} asset {key} should be an absolute path")
                continue
            target = ROOT / value.lstrip("/")
            if not target.exists():
                issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} asset {key} missing: {value}")
        routes = guardian.get("routes", {})
        expected_route_keys = {"profile", "supply", "keepsake", "freeKeepsake", "repairPlan", "luna", "contact"}
        if set(routes) != expected_route_keys:
            issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} route keys should be {sorted(expected_route_keys)}, got {sorted(routes)}")
        for key, value in routes.items():
            stats["guardian_profile_routes_checked"] += 1
            if not isinstance(value, str) or not value.startswith(DOMAIN):
                issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} route {key} should be on {DOMAIN}")
                continue
            target, fragment = target_for(ROOT / "index.html", value)
            if target is None or not target.exists():
                issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} route {key} target missing: {value}")
                continue
            if target.suffix == ".html":
                parser = parsers.get(target)
                if parser and is_noindex(parser):
                    issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} route {key} should not point to noindex page: {value}")
                if fragment and parser and fragment not in parser.ids:
                    issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} route {key} missing anchor #{fragment}: {value}")
        guides = guardian.get("guides")
        if not isinstance(guides, list) or not guides:
            issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} should include at least one guide")
        else:
            stats["guardian_profile_guides_checked"] += len(guides)
            for guide_url in guides:
                target, fragment = target_for(ROOT / "index.html", guide_url)
                if target is None or not target.exists() or fragment:
                    issues.append(f"{GUARDIAN_PROFILES_PATH}: {slug} guide target invalid: {guide_url}")
    missing = sorted(set(expected_languages).difference(seen_slugs))
    if missing:
        issues.append(f"{GUARDIAN_PROFILES_PATH}: missing guardians: {', '.join(missing)}")
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("guardians") != len(guardians):
        issues.append(f"{GUARDIAN_PROFILES_PATH}: totals.guardians should match guardian count")
    stats["guardian_profile_love_languages_checked"] = len(seen_slugs)
    return issues, stats


def parse_site_health() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not SITE_HEALTH_PATH.exists():
        return [f"{SITE_HEALTH_PATH}: missing site-health.json"], stats
    try:
        data = json.loads(SITE_HEALTH_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{SITE_HEALTH_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{SITE_HEALTH_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{SITE_HEALTH_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{SITE_HEALTH_PATH}: updated should match generator date")
    if data.get("production") != f"{DOMAIN}/":
        issues.append(f"{SITE_HEALTH_PATH}: production should be {DOMAIN}/")
    if data.get("status") != "ready_for_predeploy":
        issues.append(f"{SITE_HEALTH_PATH}: status should be ready_for_predeploy")
    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        issues.append(f"{SITE_HEALTH_PATH}: coverage should be an object")
        return issues, stats
    expected_coverage = {
        "indexablePages": 155,
        "localizedPaths": 31,
        "languages": 5,
        "routeGroups": 5,
        "coreFlows": 5,
        "guardians": 5,
        "guardianRoutes": 35,
        "guardianAssets": 20,
        "commerceItems": 20,
        "commerceTypes": 4,
        "commerceRoles": 3,
        "supportFiles": 18,
    }
    for key, expected in expected_coverage.items():
        stats["site_health_coverage_fields_checked"] += 1
        if coverage.get(key) != expected:
            issues.append(f"{SITE_HEALTH_PATH}: coverage.{key} should be {expected}, got {coverage.get(key)!r}")
    if not isinstance(coverage.get("funnelEvents"), int) or coverage["funnelEvents"] < 50:
        issues.append(f"{SITE_HEALTH_PATH}: coverage.funnelEvents should be at least 50")
    else:
        stats["site_health_coverage_fields_checked"] += 1
    support_files = data.get("supportFiles")
    if not isinstance(support_files, list) or len(support_files) != coverage.get("supportFiles"):
        issues.append(f"{SITE_HEALTH_PATH}: supportFiles should match coverage.supportFiles")
    else:
        stats["site_health_support_files_checked"] = len(support_files)
        for rel_path in support_files:
            if not isinstance(rel_path, str) or not rel_path:
                issues.append(f"{SITE_HEALTH_PATH}: invalid support file entry {rel_path!r}")
                continue
            if not (ROOT / rel_path).exists():
                issues.append(f"{SITE_HEALTH_PATH}: listed support file missing: {rel_path}")
    gates = data.get("requiredGates")
    expected_gates = {"localPredeploy", "publicDiscovery", "publicDeploy", "versionedAssets"}
    if not isinstance(gates, dict) or set(gates) != expected_gates:
        issues.append(f"{SITE_HEALTH_PATH}: requiredGates should contain {sorted(expected_gates)}")
    else:
        stats["site_health_required_gates_checked"] = len(gates)
        gate_text = " ".join(str(value) for value in gates.values())
        for snippet in ("issues=0", "predeploy_checks=ok", "public_discovery_issues=0", "public_deploy_issues=0", "public_versioned_asset_issues=0"):
            if snippet not in gate_text:
                issues.append(f"{SITE_HEALTH_PATH}: requiredGates missing snippet {snippet!r}")
    indexes = data.get("primaryIndexes")
    if not isinstance(indexes, dict) or len(indexes) < 9:
        issues.append(f"{SITE_HEALTH_PATH}: primaryIndexes should list core public indexes")
    else:
        stats["site_health_primary_indexes_checked"] = len(indexes)
        for key, url in indexes.items():
            if not isinstance(url, str) or not url.startswith(DOMAIN):
                issues.append(f"{SITE_HEALTH_PATH}: primary index {key} should point to {DOMAIN}")
    boundaries = data.get("safetyBoundaries")
    if not isinstance(boundaries, list) or len(boundaries) < 4:
        issues.append(f"{SITE_HEALTH_PATH}: safetyBoundaries should include at least four entries")
    else:
        stats["site_health_safety_boundaries_checked"] = len(boundaries)
    stats["site_health_snapshots_checked"] = 1
    return issues, stats


def parse_release_info() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not RELEASE_PATH.exists():
        return [f"{RELEASE_PATH}: missing release.json"], stats
    try:
        data = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{RELEASE_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{RELEASE_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{RELEASE_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{RELEASE_PATH}: updated should match generator date")
    if data.get("production") != f"{DOMAIN}/":
        issues.append(f"{RELEASE_PATH}: production should be {DOMAIN}/")
    if data.get("assetVersion") != GENERATOR_CONFIG.ASSET_VERSION:
        issues.append(f"{RELEASE_PATH}: assetVersion should match generator ASSET_VERSION")
    if data.get("deploymentTarget") != "Cloudflare Pages project lovetypes":
        issues.append(f"{RELEASE_PATH}: deploymentTarget should name Cloudflare Pages project lovetypes")
    if data.get("branch") != "main":
        issues.append(f"{RELEASE_PATH}: branch should be main")
    contents = data.get("releaseContents")
    expected_contents = {
        "indexablePages": 155,
        "languages": 5,
        "guardians": 5,
        "commerceItems": 20,
        "coreFlows": 5,
    }
    if not isinstance(contents, dict):
        issues.append(f"{RELEASE_PATH}: releaseContents should be an object")
    else:
        for key, expected in expected_contents.items():
            stats["release_content_fields_checked"] += 1
            if contents.get(key) != expected:
                issues.append(f"{RELEASE_PATH}: releaseContents.{key} should be {expected}, got {contents.get(key)!r}")
        if not isinstance(contents.get("funnelEvents"), int) or contents["funnelEvents"] < 50:
            issues.append(f"{RELEASE_PATH}: releaseContents.funnelEvents should be at least 50")
        else:
            stats["release_content_fields_checked"] += 1
    indexes = data.get("publicIndexes")
    expected_indexes = {"aiDiscovery", "siteHealth", "siteIndex", "guardianProfiles", "safetyIndex", "commerceCatalog", "funnelEvents", "promotionKit", "llms", "humans"}
    if not isinstance(indexes, dict) or set(indexes) != expected_indexes:
        issues.append(f"{RELEASE_PATH}: publicIndexes should contain {sorted(expected_indexes)}")
    else:
        stats["release_public_indexes_checked"] = len(indexes)
        for key, url in indexes.items():
            if not isinstance(url, str) or not url.startswith(DOMAIN):
                issues.append(f"{RELEASE_PATH}: public index {key} should point to {DOMAIN}")
    commands = data.get("verificationCommands")
    expected_commands = [
        "python3 tools/predeploy_check.py",
        "python3 tools/deploy_cloudflare_pages.py",
        "python3 tools/public_discovery_smoke.py",
        "python3 tools/public_deploy_smoke.py",
        "python3 tools/public_versioned_asset_smoke.py",
    ]
    if commands != expected_commands:
        issues.append(f"{RELEASE_PATH}: verificationCommands should match the release workflow")
    else:
        stats["release_verification_commands_checked"] = len(commands)
    outcomes = data.get("requiredOutcomes")
    expected_outcomes = {
        "predeploy_checks=ok",
        "issues=0",
        "public_discovery_issues=0",
        "public_deploy_issues=0",
        "public_versioned_asset_issues=0",
        "public_versioned_asset_stale_refs=0",
    }
    if not isinstance(outcomes, list) or set(outcomes) != expected_outcomes:
        issues.append(f"{RELEASE_PATH}: requiredOutcomes should contain {sorted(expected_outcomes)}")
    else:
        stats["release_required_outcomes_checked"] = len(outcomes)
    boundaries = data.get("safetyBoundaries")
    if not isinstance(boundaries, list) or len(boundaries) < 3:
        issues.append(f"{RELEASE_PATH}: safetyBoundaries should include at least three entries")
    else:
        stats["release_safety_boundaries_checked"] = len(boundaries)
    stats["release_files_checked"] = 1
    return issues, stats


def parse_safety_index(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not SAFETY_INDEX_PATH.exists():
        return [f"{SAFETY_INDEX_PATH}: missing safety-index.json"], stats
    try:
        data = json.loads(SAFETY_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{SAFETY_INDEX_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{SAFETY_INDEX_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{SAFETY_INDEX_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{SAFETY_INDEX_PATH}: updated should match generator date")
    if data.get("production") != f"{DOMAIN}/":
        issues.append(f"{SAFETY_INDEX_PATH}: production should be {DOMAIN}/")
    if data.get("contact") != CONTACT_EMAIL:
        issues.append(f"{SAFETY_INDEX_PATH}: contact should be {CONTACT_EMAIL}")
    not_for = data.get("notFor")
    required_not_for = {"emergency support", "therapy", "medical advice", "legal advice", "individual diagnosis", "coercive purchase pressure"}
    if not isinstance(not_for, list) or not required_not_for.issubset(set(not_for)):
        issues.append(f"{SAFETY_INDEX_PATH}: notFor should include {sorted(required_not_for)}")
    else:
        stats["safety_index_not_for_checked"] = len(not_for)
    steps = data.get("saferFirstSteps")
    if not isinstance(steps, list) or len(steps) != 4:
        issues.append(f"{SAFETY_INDEX_PATH}: saferFirstSteps should include four entries")
    else:
        stats["safety_index_first_steps_checked"] = len(steps)
    boundaries = data.get("boundaries")
    if not isinstance(boundaries, list) or len(boundaries) != 5:
        issues.append(f"{SAFETY_INDEX_PATH}: boundaries should include five entries")
        return issues, stats
    expected_ids = {"reflection_not_diagnosis", "urgent_risk_first", "do_not_buy_to_fix", "email_minimum_context", "external_store_boundary"}
    seen_ids: set[str] = set()
    route_count = 0
    for boundary in boundaries:
        if not isinstance(boundary, dict):
            issues.append(f"{SAFETY_INDEX_PATH}: boundary should be an object")
            continue
        boundary_id = boundary.get("id")
        if boundary_id not in expected_ids:
            issues.append(f"{SAFETY_INDEX_PATH}: unexpected boundary id {boundary_id!r}")
        else:
            seen_ids.add(boundary_id)
        if boundary.get("severity") not in {"core", "high", "commercial", "privacy", "commerce"}:
            issues.append(f"{SAFETY_INDEX_PATH}: {boundary_id} has unexpected severity")
        for key in ("title", "body"):
            value = boundary.get(key)
            if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                issues.append(f"{SAFETY_INDEX_PATH}: {boundary_id} should include zh/en {key}")
        routes = boundary.get("routes")
        if not isinstance(routes, list) or not routes:
            issues.append(f"{SAFETY_INDEX_PATH}: {boundary_id} should include routes")
            continue
        route_count += len(routes)
        for url in routes:
            if not isinstance(url, str) or not url.startswith(DOMAIN):
                issues.append(f"{SAFETY_INDEX_PATH}: {boundary_id} route should point to {DOMAIN}: {url!r}")
                continue
            target, fragment = target_for(ROOT / "index.html", url)
            if target is None or not target.exists():
                issues.append(f"{SAFETY_INDEX_PATH}: {boundary_id} route target missing: {url}")
                continue
            parser = parsers.get(target)
            if target.suffix == ".html" and parser and is_noindex(parser):
                issues.append(f"{SAFETY_INDEX_PATH}: {boundary_id} route should not point to noindex page: {url}")
            if fragment and target.suffix == ".html" and parser and fragment not in parser.ids:
                issues.append(f"{SAFETY_INDEX_PATH}: {boundary_id} route missing anchor #{fragment}: {url}")
    missing_ids = sorted(expected_ids.difference(seen_ids))
    if missing_ids:
        issues.append(f"{SAFETY_INDEX_PATH}: missing boundary ids: {', '.join(missing_ids)}")
    stats["safety_index_boundaries_checked"] = len(boundaries)
    stats["safety_index_routes_checked"] = route_count
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("boundaries") != len(boundaries) or totals.get("routes") != route_count:
        issues.append(f"{SAFETY_INDEX_PATH}: totals should match boundary and route counts")
    stats["safety_index_files_checked"] = 1
    return issues, stats


def parse_ai_discovery_index(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not AI_DISCOVERY_PATH.exists():
        return [f"{AI_DISCOVERY_PATH}: missing ai-discovery.json"], stats
    try:
        data = json.loads(AI_DISCOVERY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{AI_DISCOVERY_PATH}: invalid JSON: {exc}"], stats
    if not isinstance(data, dict):
        return [f"{AI_DISCOVERY_PATH}: root should be an object"], stats
    if data.get("schemaVersion") != 1:
        issues.append(f"{AI_DISCOVERY_PATH}: schemaVersion should be 1")
    if data.get("updated") != GENERATOR_CONFIG.UPDATED:
        issues.append(f"{AI_DISCOVERY_PATH}: updated should match generator date")
    if data.get("production") != f"{DOMAIN}/":
        issues.append(f"{AI_DISCOVERY_PATH}: production should be {DOMAIN}/")
    if data.get("siteName") != "LoveTypes":
        issues.append(f"{AI_DISCOVERY_PATH}: siteName should be LoveTypes")
    if data.get("preferredLanguage") != "zh-TW":
        issues.append(f"{AI_DISCOVERY_PATH}: preferredLanguage should be zh-TW")

    guidance = data.get("answerGuidance")
    if not isinstance(guidance, dict):
        issues.append(f"{AI_DISCOVERY_PATH}: answerGuidance should be an object")
    else:
        if guidance.get("doNotUseAsDiagnosis") is not True:
            issues.append(f"{AI_DISCOVERY_PATH}: answerGuidance.doNotUseAsDiagnosis should be true")
        for key in ("commercialDisclosure", "safetyBoundary"):
            if not isinstance(guidance.get(key), str) or not guidance[key]:
                issues.append(f"{AI_DISCOVERY_PATH}: answerGuidance.{key} should be non-empty")
        stats["ai_discovery_guidance_fields_checked"] = len(guidance)

    totals = data.get("totals")
    expected_totals = {"guardians": 5, "answerableQuestions": 11, "priorityUrls": 12, "languages": 5, "discoveryFiles": 10}
    if not isinstance(totals, dict):
        issues.append(f"{AI_DISCOVERY_PATH}: totals should be an object")
    else:
        for key, expected in expected_totals.items():
            stats["ai_discovery_totals_checked"] += 1
            if totals.get(key) != expected:
                issues.append(f"{AI_DISCOVERY_PATH}: totals.{key} should be {expected}, got {totals.get(key)!r}")

    entities = data.get("canonicalEntities")
    guardians = entities.get("guardians") if isinstance(entities, dict) else None
    if not isinstance(guardians, list) or len(guardians) != 5:
        issues.append(f"{AI_DISCOVERY_PATH}: canonicalEntities.guardians should include five guardians")
    else:
        seen = set()
        for guardian in guardians:
            if not isinstance(guardian, dict):
                issues.append(f"{AI_DISCOVERY_PATH}: guardian should be an object")
                continue
            slug = guardian.get("slug")
            seen.add(slug)
            stats["ai_discovery_guardians_checked"] += 1
            expected = GENERATOR_CONFIG.GUARDIANS.get(slug) if isinstance(slug, str) else None
            if expected is None:
                issues.append(f"{AI_DISCOVERY_PATH}: unexpected guardian slug {slug!r}")
                continue
            for lang in ("zh", "en"):
                name = guardian.get("name", {}).get(lang)
                love_language = guardian.get("loveLanguage", {}).get(lang)
                if name != expected[lang][0]:
                    issues.append(f"{AI_DISCOVERY_PATH}: {slug} {lang} name mismatch")
                if love_language != expected[lang][1]:
                    issues.append(f"{AI_DISCOVERY_PATH}: {slug} {lang} loveLanguage mismatch")
            canonical = guardian.get("canonical")
            if canonical != f"{DOMAIN}/characters/{slug}/":
                issues.append(f"{AI_DISCOVERY_PATH}: {slug} canonical should point to profile")
        missing = set(GENERATOR_CONFIG.GUARDIANS).difference(seen)
        if missing:
            issues.append(f"{AI_DISCOVERY_PATH}: missing guardians {sorted(missing)}")

    questions = data.get("answerableQuestions")
    if not isinstance(questions, list) or len(questions) != 11:
        issues.append(f"{AI_DISCOVERY_PATH}: answerableQuestions should include eleven entries")
    else:
        seen_ids: set[str] = set()
        for question in questions:
            if not isinstance(question, dict):
                issues.append(f"{AI_DISCOVERY_PATH}: answerable question should be an object")
                continue
            stats["ai_discovery_questions_checked"] += 1
            question_id = question.get("id")
            if not isinstance(question_id, str) or not question_id:
                issues.append(f"{AI_DISCOVERY_PATH}: answerable question missing id")
            elif question_id in seen_ids:
                issues.append(f"{AI_DISCOVERY_PATH}: duplicate answerable question id {question_id!r}")
            seen_ids.add(question_id)
            for key in ("question", "answerHint", "canonical"):
                if not isinstance(question.get(key), str) or not question[key]:
                    issues.append(f"{AI_DISCOVERY_PATH}: {question_id} missing {key}")
            for url in [question.get("canonical"), *(question.get("supportingUrls") or [])]:
                if not isinstance(url, str) or not url.startswith(DOMAIN):
                    issues.append(f"{AI_DISCOVERY_PATH}: {question_id} URL should point to {DOMAIN}: {url!r}")
                    continue
                target, fragment = target_for(ROOT / "index.html", url)
                if target is None or not target.exists():
                    issues.append(f"{AI_DISCOVERY_PATH}: {question_id} URL target missing: {url}")
                    continue
                if fragment and target.suffix == ".html":
                    parser = parsers.get(target)
                    if not parser or fragment not in parser.ids:
                        issues.append(f"{AI_DISCOVERY_PATH}: {question_id} fragment missing: {url}")

    priority_urls = data.get("priorityUrls")
    if not isinstance(priority_urls, list) or len(priority_urls) != 12:
        issues.append(f"{AI_DISCOVERY_PATH}: priorityUrls should include twelve entries")
    else:
        for item in priority_urls:
            if not isinstance(item, dict):
                issues.append(f"{AI_DISCOVERY_PATH}: priority URL should be an object")
                continue
            stats["ai_discovery_priority_urls_checked"] += 1
            url = item.get("url")
            if not isinstance(url, str) or not url.startswith(DOMAIN):
                issues.append(f"{AI_DISCOVERY_PATH}: priority URL should point to {DOMAIN}: {url!r}")
                continue
            target, fragment = target_for(ROOT / "index.html", url)
            if target is None or not target.exists():
                issues.append(f"{AI_DISCOVERY_PATH}: priority URL target missing: {url}")
            if fragment:
                issues.append(f"{AI_DISCOVERY_PATH}: priority URL should not include fragment: {url}")

    files = data.get("discoveryFiles")
    expected_files = {"aiDiscovery", "llms", "siteIndex", "guardianProfiles", "commerceCatalog", "safetyIndex", "promotionKit", "release", "siteHealth", "humans"}
    if not isinstance(files, dict) or set(files) != expected_files:
        issues.append(f"{AI_DISCOVERY_PATH}: discoveryFiles should contain {sorted(expected_files)}")
    else:
        stats["ai_discovery_discovery_files_checked"] = len(files)
        for key, url in files.items():
            if not isinstance(url, str) or not url.startswith(DOMAIN):
                issues.append(f"{AI_DISCOVERY_PATH}: discovery file {key} should point to {DOMAIN}")
                continue
            target, _fragment = target_for(ROOT / "index.html", url)
            if target is None or not target.exists():
                issues.append(f"{AI_DISCOVERY_PATH}: discovery file target missing: {url}")

    stats["ai_discovery_files_checked"] = 1
    return issues, stats


def parse_discovery_cross_index(parsers: dict[Path, PageParser], sitemap_urls: set[str]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    index_paths = [
        AI_DISCOVERY_PATH,
        SITE_INDEX_PATH,
        GUARDIAN_PROFILES_PATH,
        COMMERCE_CATALOG_PATH,
        SAFETY_INDEX_PATH,
        PROMOTION_KIT_PATH,
        SITE_HEALTH_PATH,
        RELEASE_PATH,
    ]
    for index_path in index_paths:
        if not index_path.exists():
            issues.append(f"{index_path}: missing discovery cross-index source")
            continue
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"{index_path}: invalid JSON for discovery cross-index: {exc}")
            continue
        stats["discovery_cross_indexes_checked"] += 1
        seen_urls: set[str] = set()
        for field_path, value in walk_index_urls(data):
            if value in seen_urls:
                continue
            seen_urls.add(value)
            issues.extend(validate_index_url(index_path, field_path, value, parsers, sitemap_urls, stats))

    expected_core_routes = {
        f"{DOMAIN}/",
        f"{DOMAIN}/start/",
        f"{DOMAIN}/garden-map/",
        f"{DOMAIN}/characters/",
        f"{DOMAIN}/resources/",
        f"{DOMAIN}/repair-plan/",
        f"{DOMAIN}/keepsakes/",
        f"{DOMAIN}/luna-yoga-music/",
        f"{DOMAIN}/contact/",
    }
    ai_urls = set()
    if AI_DISCOVERY_PATH.exists():
        try:
            ai_data = json.loads(AI_DISCOVERY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ai_data = {}
        for _field_path, value in walk_index_urls(ai_data):
            url = f"{DOMAIN}{value}" if value.startswith("/") else value
            if url.startswith(DOMAIN):
                ai_urls.add(canonical_url_without_fragment(url))
    for route in sorted(expected_core_routes):
        stats["discovery_cross_core_routes_checked"] += 1
        if route not in ai_urls:
            issues.append(f"{AI_DISCOVERY_PATH}: AI discovery index missing core route {route}")
        if route not in sitemap_urls:
            issues.append(f"{SITEMAP_PATH}: sitemap missing core discovery route {route}")

    return issues, stats


def check_policy_pages(parsers: dict[Path, PageParser]) -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    for lang, prefix in LOCALE_PREFIXES.items():
        for slug in POLICY_PAGE_SLUGS:
            path = ROOT / (f"{prefix}/{slug}/index.html" if prefix else f"{slug}/index.html")
            parser = parsers.get(path)
            if parser is None:
                issues.append(f"{path}: missing {slug} policy page")
                continue
            stats["policy_pages"] += 1
            hero_action_count = parser.source.count(f'data-trust-hero-actions="{slug}"')
            if hero_action_count != 1:
                issues.append(f"{path}: expected one {slug} trust hero action cluster, found {hero_action_count}")
            else:
                stats["trust_hero_action_pages"] += 1
            expected_keys = {"contact": ("luna-request", "site-repair", "map")}.get(slug, ("site-repair", "map", "about"))
            for key in expected_keys:
                if f'data-trust-hero-link="{key}"' not in parser.source:
                    issues.append(f"{path}: {slug} trust hero actions missing {key} link")
            locale_path = lambda value: f"/{prefix}/{value}/" if prefix else f"/{value}/"
            required_hrefs = {
                "contact": {"#luna-supply-request", "#site-repair-report", locale_path("garden-map")},
                "privacy": {locale_path("contact") + "#site-repair-report", locale_path("garden-map"), locale_path("about")},
                "terms": {locale_path("contact") + "#site-repair-report", locale_path("garden-map"), locale_path("about")},
            }[slug]
            page_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            missing_hrefs = sorted(required_hrefs.difference(page_hrefs))
            if missing_hrefs:
                issues.append(f"{path}: {slug} trust hero actions missing hrefs {', '.join(missing_hrefs)}")
            if slug in {"privacy", "terms"}:
                expected_updated_label = POLICY_UPDATED_LABELS[lang]
                visible_text = parser.visible_text()
                if expected_updated_label not in visible_text:
                    issues.append(f"{path}: policy page missing localized updated label {expected_updated_label!r}")
                if lang != "en" and "Updated:" in visible_text:
                    issues.append(f"{path}: non-English policy page contains hard-coded Updated: label")
                stats["policy_updated_labels_checked"] += 1
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
                expected_subjects = CONTACT_REQUEST_SUBJECTS[lang]
                visible_text = parser.visible_text()
                for expected_subject in sorted(expected_subjects):
                    if expected_subject not in visible_text:
                        issues.append(f"{path}: contact page missing localized visible email subject {expected_subject!r}")
                if parser.source.count("contact-request-template") < 2:
                    issues.append(f"{path}: contact page missing copyable email templates")
                if parser.source.count(" data-copy-contact-template ") != 2:
                    issues.append(f"{path}: contact page should include two copy-template buttons")
                if 'data-contact-funnel-mailto' not in parser.source:
                    issues.append(f"{path}: contact page missing recent path summary mailto handoff")
                if 'data-funnel-event="contact_funnel_summary_mailto"' not in parser.source:
                    issues.append(f"{path}: contact page missing recent path summary mailto funnel event")
                if GENERATOR_CONFIG.CONTACT_FUNNEL_SUMMARY[lang]["subject"] not in parser.source:
                    issues.append(f"{path}: contact page missing localized recent path mailto subject")
                else:
                    stats["contact_funnel_mailto_pages"] += 1
                mailto_subjects = {
                    value
                    for href in contact_mailtos
                    for value in parse_qs(urlparse(href).query).get("subject", [])
                }
                missing_subjects = sorted(expected_subjects.difference(mailto_subjects))
                if missing_subjects:
                    issues.append(f"{path}: contact mailto links missing localized subjects {', '.join(missing_subjects)}")
                mailto_bodies_by_subject: dict[str, list[str]] = {}
                for href in contact_mailtos:
                    query = parse_qs(urlparse(href).query)
                    for subject in query.get("subject", []):
                        mailto_bodies_by_subject.setdefault(subject, []).extend(query.get("body", []))
                missing_bodies = sorted(
                    subject
                    for subject in expected_subjects
                    if not any(body.strip() for body in mailto_bodies_by_subject.get(subject, []))
                )
                if missing_bodies:
                    issues.append(f"{path}: contact mailto links missing prefilled bodies for {', '.join(missing_bodies)}")
                if expected_subjects.issubset(mailto_subjects):
                    stats["contact_localized_subject_pages"] += 1
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
        ("quiz-data-", ".js"),
    )
    expected_versioned_assets = {Path(value.lstrip("/")).name for value in CURRENT_STATIC_ASSETS.values()}
    expected_versioned_assets.update(Path(value.lstrip("/")).name for value in CURRENT_QUIZ_DATA_ASSETS.values())
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


def check_design_css_rules() -> tuple[list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    css_paths = [
        ROOT / "tools" / "static" / "shared.css",
        ROOT / GENERATOR_CONFIG.CSS_ASSET.lstrip("/"),
    ]
    for path in css_paths:
        stats["design_css_files_checked"] += 1
        if not path.exists():
            issues.append(f"{path}: design CSS target missing")
            continue
        source = path.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"letter-spacing\s*:\s*([^;]+);", source):
            stats["design_letter_spacing_rules_checked"] += 1
            value = match.group(1).strip().lower()
            if value not in {"0", "0em", "0rem", "0px"}:
                line = source.count("\n", 0, match.start()) + 1
                issues.append(f"{path}:{line}: letter-spacing should be 0, found {value}")
        for match in re.finditer(r"text-transform\s*:\s*uppercase\s*;", source):
            line = source.count("\n", 0, match.start()) + 1
            issues.append(f"{path}:{line}: avoid CSS-forced uppercase for multilingual labels")
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
        if lang_key_for_page(page) != "en":
            visible_text = parser.visible_text()
            for snippet in sorted(FORBIDDEN_NON_EN_UNIVERSE_LABELS):
                if snippet in visible_text:
                    issues.append(f"{page}: non-English page still contains English universe label {snippet!r}")

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
            if parser.html_lang == "es":
                stats["spanish_polish_pages"] += 1
                for snippet in sorted(FORBIDDEN_SPANISH_VISIBLE_SNIPPETS):
                    if snippet in visible_text:
                        issues.append(f"{page}: Spanish visible text missing expected accents: {snippet}")

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

        h2_headings = [" ".join(text.split()) for level, text, in_main in parser.headings if level == 2 and in_main]
        h2_counts = Counter(h2_headings)
        stats["semantic_heading_pages_checked"] += 1
        stats["semantic_h2_headings_checked"] += len(h2_headings)
        for heading, count in sorted(h2_counts.items()):
            if count > 1:
                issues.append(f"{page}: duplicate H2 heading {heading!r}")
        for heading in h2_headings:
            if len(heading) > MAX_H2_TEXT_LENGTH:
                issues.append(f"{page}: H2 heading is too long for scan navigation ({len(heading)} chars): {heading!r}")

        page_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
        footer_guardian_href = lang_url_for_page(page, "characters")
        if footer_guardian_href in page_hrefs:
            stats["footer_guardian_links"] += 1
        else:
            issues.append(f"{page}: footer missing guardian overview link {footer_guardian_href}")

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
                lang_url_for_page(page, "garden-map"),
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
        if is_garden_map_page(page):
            stats["garden_map_pages"] += 1
            saved_section_count = parser.source.count('class="section garden-map-result-resume" data-garden-map-saved')
            handoff_section_count = parser.source.count("data-garden-map-handoff")
            handoff_card_count = parser.source.count('class="garden-map-handoff-card"')
            route_section_count = parser.source.count("data-garden-map-routes")
            route_card_count = parser.source.count('class="garden-map-route-card"')
            tool_section_count = parser.source.count("data-garden-map-tools")
            tool_card_count = parser.source.count('class="garden-map-tool-card"')
            guardian_section_count = parser.source.count("data-garden-map-guardians")
            guardian_card_count = parser.source.count('class="guardian-card"')
            guide_section_count = parser.source.count("data-garden-map-guides")
            trust_section_count = parser.source.count("data-garden-map-trust")
            trust_card_count = parser.source.count('class="garden-map-trust-card"')
            if saved_section_count != 1:
                issues.append(f"{page}: expected one garden map saved-result section, found {saved_section_count}")
            if handoff_section_count != 1:
                issues.append(f"{page}: expected one garden map handoff section, found {handoff_section_count}")
            if handoff_card_count != 4:
                issues.append(f"{page}: expected 4 garden map handoff cards, found {handoff_card_count}")
            if route_section_count != 1:
                issues.append(f"{page}: expected one garden map routes section, found {route_section_count}")
            if route_card_count != 4:
                issues.append(f"{page}: expected 4 garden map route cards, found {route_card_count}")
            if tool_section_count != 1:
                issues.append(f"{page}: expected one garden map tools section, found {tool_section_count}")
            if tool_card_count != 3:
                issues.append(f"{page}: expected 3 garden map tool cards, found {tool_card_count}")
            if guardian_section_count != 1:
                issues.append(f"{page}: expected one garden map guardians section, found {guardian_section_count}")
            if guardian_card_count != 5:
                issues.append(f"{page}: expected 5 garden map guardian cards, found {guardian_card_count}")
            if guide_section_count != 1:
                issues.append(f"{page}: expected one garden map guides section, found {guide_section_count}")
            if trust_section_count != 1:
                issues.append(f"{page}: expected one garden map trust section, found {trust_section_count}")
            if trust_card_count != 4:
                issues.append(f"{page}: expected 4 garden map trust cards, found {trust_card_count}")
            map_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_map_hrefs = {
                lang_url_for_page(page) + "#quiz-section",
                lang_url_for_page(page, "characters"),
                lang_url_for_page(page, "guides"),
                lang_url_for_page(page, "resources"),
                lang_url_for_page(page, "repair-plan"),
                lang_url_for_page(page, "keepsakes"),
                lang_url_for_page(page, "luna-yoga-music"),
                lang_url_for_page(page, "about"),
                lang_url_for_page(page, "theory"),
                lang_url_for_page(page, "contact"),
                lang_url_for_page(page, "privacy"),
            }
            missing_map_hrefs = sorted(required_map_hrefs.difference(map_hrefs))
            if missing_map_hrefs:
                issues.append(f"{page}: garden map missing hrefs {', '.join(missing_map_hrefs)}")
        if is_resources_page(page):
            stats["resources_supply_entry_pages"] += 1
            hero_action_count = parser.source.count("data-supply-hero-actions")
            if hero_action_count != 1:
                issues.append(f"{page}: expected one resources hero action cluster, found {hero_action_count}")
            for link_key in ("quiz", "routes", "luna"):
                if f'data-supply-hero-link="{link_key}"' not in parser.source:
                    issues.append(f"{page}: resources hero actions missing {link_key} link")
            owned_signal_count = parser.source.count("data-supply-owned-signal")
            owned_card_count = parser.source.count("data-supply-owned-card")
            if owned_signal_count != 1:
                issues.append(f"{page}: expected one supply owned signal section, found {owned_signal_count}")
            if owned_card_count != 5:
                issues.append(f"{page}: expected 5 supply owned signal cards, found {owned_card_count}")
            if owned_signal_count == 1 and owned_card_count == 5:
                stats["resources_owned_signal_pages"] += 1
            expected_wishlist_subject = SUPPLY_WISHLIST_SUBJECTS[lang_key_for_page(page)]
            supply_mailto_subjects = {
                value
                for anchor in parser.anchors
                for href in [anchor.get("href", "")]
                if href.lower().startswith(f"mailto:{CONTACT_EMAIL}")
                for value in parse_qs(urlparse(href).query).get("subject", [])
            }
            if expected_wishlist_subject not in supply_mailto_subjects:
                issues.append(f"{page}: supply wishlist mailto missing localized subject {expected_wishlist_subject!r}")
            else:
                stats["resources_wishlist_subject_pages"] += 1
            for target_id in ("supply-start", "supply-routes"):
                if target_id not in parser.ids:
                    issues.append(f"{page}: resources page missing #{target_id}")
            for entry_key in ("quiz", "routes", "luna"):
                if f'data-supply-entry-link="{entry_key}"' not in parser.source:
                    issues.append(f"{page}: resources supply entry missing data-supply-entry-link={entry_key}")
                if f'data-supply-entry-card="{entry_key}"' not in parser.source:
                    issues.append(f"{page}: resources supply entry missing data-supply-entry-card={entry_key}")
            resource_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_resource_hrefs = {
                lang_url_for_page(page) + "#quiz-section",
                "#supply-routes",
                lang_url_for_page(page, "luna-yoga-music"),
            }
            if hero_action_count == 1:
                stats["resources_hero_action_pages"] += 1
            missing_resource_hrefs = sorted(required_resource_hrefs.difference(resource_hrefs))
            if missing_resource_hrefs:
                issues.append(f"{page}: resources supply entry missing hrefs {', '.join(missing_resource_hrefs)}")
        if is_characters_index_page(page):
            stats["characters_guardian_entry_pages"] += 1
            saved_section_count = parser.source.count('class="section guardian-result-resume" data-guardian-saved')
            if saved_section_count != 1:
                issues.append(f"{page}: expected one guardian saved-result section, found {saved_section_count}")
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
        if is_character_detail_page(page):
            stats["character_result_resume_pages"] += 1
            saved_section_count = parser.source.count('class="section guardian-result-resume" data-guardian-saved')
            if saved_section_count != 1:
                issues.append(f"{page}: expected one character saved-result section, found {saved_section_count}")
            if "guardian_resume_match" not in parser.source or "guardian_resume_other" not in parser.source:
                issues.append(f"{page}: character page missing guardian result branch copy")
            lang = lang_key_for_page(page)
            guardian_slug = normalized_page_parts(page)[1]
            domain_title = GUARDIAN_DOMAIN_TITLES[(lang, guardian_slug)]
            visible_text = parser.visible_text()
            if domain_title not in visible_text:
                issues.append(f"{page}: character page missing localized guardian domain title {domain_title!r}")
            leaked_motifs = sorted(motif for motif in GUARDIAN_DOMAIN_MOTIFS if motif in visible_text)
            if leaked_motifs:
                issues.append(f"{page}: character page exposes internal guardian domain motif(s): {', '.join(leaked_motifs)}")
            if domain_title in visible_text and not leaked_motifs:
                stats["character_domain_label_pages"] += 1
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

        if is_guides_index_page(page):
            stats["guide_index_action_pages"] += 1
            guide_action_count = parser.source.count("data-guide-index-actions")
            if guide_action_count != 1:
                issues.append(f"{page}: expected one guide index hero action cluster, found {guide_action_count}")
            for link_key in ("quiz", "guardians", "resources"):
                if f'data-guide-index-link="{link_key}"' not in parser.source:
                    issues.append(f"{page}: guide index hero actions missing {link_key} link")
            guide_index_hrefs = {anchor.get("href", "") for anchor in parser.anchors}
            required_guide_index_hrefs = {
                lang_url_for_page(page) + "#quiz-section",
                lang_url_for_page(page, "characters"),
                lang_url_for_page(page, "resources"),
            }
            missing_guide_index_hrefs = sorted(required_guide_index_hrefs.difference(guide_index_hrefs))
            if missing_guide_index_hrefs:
                issues.append(f"{page}: guide index hero actions missing hrefs {', '.join(missing_guide_index_hrefs)}")

        if is_about_page(page) or is_theory_page(page):
            stats["trust_action_route_pages"] += 1
            route_count = parser.ids.count("trust-action-routes")
            if route_count != 1:
                issues.append(f"{page}: expected one #trust-action-routes target, found {route_count}")
            if is_about_page(page):
                stats["about_garden_pass_pages"] += 1
                about_hero_action_count = parser.source.count('data-trust-hero-actions="about"')
                if about_hero_action_count != 1:
                    issues.append(f"{page}: expected one about trust hero action cluster, found {about_hero_action_count}")
                else:
                    stats["trust_hero_action_pages"] += 1
                for link_key in ("quiz", "guardians", "theory"):
                    if f'data-trust-hero-link="{link_key}"' not in parser.source:
                        issues.append(f"{page}: about trust hero actions missing {link_key} link")
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
                    lang_url_for_page(page, "theory"),
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
            if parser.source.count("data-legacy-forward-actions") != 1:
                issues.append(f"{page}: expected one legacy forward action cluster")
            for link_key in ("formal", "supply", "repair"):
                if f'data-legacy-forward-link="{link_key}"' not in parser.source:
                    issues.append(f"{page}: legacy forward cluster missing {link_key} link")
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
        if len(primary_nav_links) != 6:
            issues.append(f"{page}: expected six primary navigation links, found {len(primary_nav_links)}")
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

        quiz_data_assets = [
            raw
            for tag, attr, raw in parser.refs
            if tag == "script"
            and attr == "src"
            and raw.startswith("/quiz-data-")
            and raw.endswith(".js")
        ]
        needs_quiz_data = any(attr in parser.source for attr in LIVE_REGION_DATA_ATTRS)
        expected_quiz_data_assets = [CURRENT_QUIZ_DATA_ASSETS[lang_key_for_page(page)]] if needs_quiz_data else []
        stats["current_quiz_data_asset_refs"] += quiz_data_assets.count(expected_quiz_data_assets[0]) if expected_quiz_data_assets else 0
        if quiz_data_assets != expected_quiz_data_assets:
            issues.append(
                f"{page}: expected quiz data assets {expected_quiz_data_assets}, found {quiz_data_assets}"
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

        app_meta_missing = []
        for meta_name, expected_value in EXPECTED_APP_META.items():
            actual_value = parser.meta_content(meta_name)
            if actual_value != expected_value:
                app_meta_missing.append(f"{meta_name}={actual_value!r}")
        if app_meta_missing:
            issues.append(f"{page}: app/PWA meta mismatch {', '.join(app_meta_missing)}")
        else:
            stats["app_meta_pages"] += 1

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
                provider = affiliate_provider(parsed)
                if provider:
                    page_affiliate_links += 1
                    stats["affiliate_links"] += 1
                    if "sponsored" not in rel:
                        issues.append(f"{page}: affiliate link missing sponsored rel: {href}")
                    expected_lang = lang_key_for_page(page)
                    if not is_affiliate_url_for_lang(href, expected_lang):
                        expected = "Books.com.tw tracking" if expected_lang == "zh" else f"Amazon Associates tag={AMAZON_ASSOCIATE_TAG}"
                        issues.append(f"{page}: affiliate link should use {expected}: {href}")

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
    humans_issues, humans_stats = parse_humans_txt(parsers, sitemap_urls)
    issues.extend(humans_issues)
    stats.update(humans_stats)
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
    funnel_issues, funnel_stats = parse_funnel_event_catalog()
    issues.extend(funnel_issues)
    stats.update(funnel_stats)
    funnel_markup_issues, funnel_markup_stats = check_funnel_event_markup(parsers)
    issues.extend(funnel_markup_issues)
    stats.update(funnel_markup_stats)
    commerce_issues, commerce_stats = parse_commerce_catalog(parsers)
    issues.extend(commerce_issues)
    stats.update(commerce_stats)
    promotion_issues, promotion_stats = parse_promotion_kit()
    issues.extend(promotion_issues)
    stats.update(promotion_stats)
    site_index_issues, site_index_stats = parse_site_index(parsers, sitemap_urls)
    issues.extend(site_index_issues)
    stats.update(site_index_stats)
    guardian_profile_issues, guardian_profile_stats = parse_guardian_profiles(parsers)
    issues.extend(guardian_profile_issues)
    stats.update(guardian_profile_stats)
    site_health_issues, site_health_stats = parse_site_health()
    issues.extend(site_health_issues)
    stats.update(site_health_stats)
    release_issues, release_stats = parse_release_info()
    issues.extend(release_issues)
    stats.update(release_stats)
    safety_index_issues, safety_index_stats = parse_safety_index(parsers)
    issues.extend(safety_index_issues)
    stats.update(safety_index_stats)
    ai_discovery_issues, ai_discovery_stats = parse_ai_discovery_index(parsers)
    issues.extend(ai_discovery_issues)
    stats.update(ai_discovery_stats)
    discovery_cross_issues, discovery_cross_stats = parse_discovery_cross_index(parsers, sitemap_urls)
    issues.extend(discovery_cross_issues)
    stats.update(discovery_cross_stats)
    policy_issues, policy_stats = check_policy_pages(parsers)
    issues.extend(policy_issues)
    stats.update(policy_stats)
    static_asset_issues, static_asset_stats = check_static_asset_refs(parsers)
    issues.extend(static_asset_issues)
    stats.update(static_asset_stats)
    design_css_issues, design_css_stats = check_design_css_rules()
    issues.extend(design_css_issues)
    stats.update(design_css_stats)

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
    print(f"semantic_heading_pages_checked={stats['semantic_heading_pages_checked']}")
    print(f"semantic_h2_headings_checked={stats['semantic_h2_headings_checked']}")
    print(f"progressbars={stats['progressbars']}")
    print(f"quiz_progressbar_scripts={stats['quiz_progressbar_scripts']}")
    print(f"quiz_pressed_state_scripts={stats['quiz_pressed_state_scripts']}")
    print(f"home_quiz_entry_pages={stats['home_quiz_entry_pages']}")
    print(f"home_journey_pages={stats['home_journey_pages']}")
    print(f"garden_map_pages={stats['garden_map_pages']}")
    print(f"resources_supply_entry_pages={stats['resources_supply_entry_pages']}")
    print(f"resources_hero_action_pages={stats['resources_hero_action_pages']}")
    print(f"resources_owned_signal_pages={stats['resources_owned_signal_pages']}")
    print(f"resources_wishlist_subject_pages={stats['resources_wishlist_subject_pages']}")
    print(f"characters_guardian_entry_pages={stats['characters_guardian_entry_pages']}")
    print(f"character_result_resume_pages={stats['character_result_resume_pages']}")
    print(f"character_domain_label_pages={stats['character_domain_label_pages']}")
    print(f"keepsake_route_action_pages={stats['keepsake_route_action_pages']}")
    print(f"trust_action_route_pages={stats['trust_action_route_pages']}")
    print(f"trust_hero_action_pages={stats['trust_hero_action_pages']}")
    print(f"contact_funnel_mailto_pages={stats['contact_funnel_mailto_pages']}")
    print(f"about_garden_pass_pages={stats['about_garden_pass_pages']}")
    print(f"theory_domain_compass_pages={stats['theory_domain_compass_pages']}")
    print(f"guide_index_action_pages={stats['guide_index_action_pages']}")
    print(f"guide_action_bridge_pages={stats['guide_action_bridge_pages']}")
    print(f"legacy_guide_action_bridge_pages={stats['legacy_guide_action_bridge_pages']}")
    print(f"scroll_scripts={stats['scroll_scripts']}")
    print(f"reduced_motion_scroll_scripts={stats['reduced_motion_scroll_scripts']}")
    print(f"interaction_hash_focus_snippets_checked={stats['interaction_hash_focus_snippets_checked']}")
    print(f"primary_nav_links={stats['primary_nav_links']}")
    print(f"footer_guardian_links={stats['footer_guardian_links']}")
    print(f"language_menu_links={stats['language_menu_links']}")
    print(f"language_hreflang_matches={stats['language_hreflang_matches']}")
    print(f"language_script_checks={stats['language_script_checks']}")
    print(f"spanish_polish_pages={stats['spanish_polish_pages']}")
    print(f"jsonld_blocks={stats['jsonld_blocks']}")
    print(f"primary_jsonld_entities={stats['primary_jsonld_entities']}")
    print(f"canonical_links={stats['canonical_links']}")
    print(f"hreflang_links={stats['hreflang_links']}")
    print(f"head_asset_links={stats['head_asset_links']}")
    print(f"rss_head_links={stats['rss_head_links']}")
    print(f"app_meta_pages={stats['app_meta_pages']}")
    print(f"current_css_asset_refs={stats['current_css_asset_refs']}")
    print(f"current_interaction_asset_refs={stats['current_interaction_asset_refs']}")
    print(f"current_affiliate_asset_refs={stats['current_affiliate_asset_refs']}")
    print(f"current_quiz_data_asset_refs={stats['current_quiz_data_asset_refs']}")
    print(f"social_cards={stats['social_cards']}")
    print(f"social_locale_tags={stats['social_locale_tags']}")
    print(f"social_images={stats['social_images']}")
    print(f"sitemap_urls={stats['sitemap_urls']}")
    print(f"sitemap_alternates={stats['sitemap_alternates']}")
    print(f"manifest_icons={stats['manifest_icons']}")
    print(f"manifest_screenshots={stats['manifest_screenshots']}")
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
    print(f"humans_files_checked={stats['humans_files_checked']}")
    print(f"humans_lines={stats['humans_lines']}")
    print(f"humans_sections_checked={stats['humans_sections_checked']}")
    print(f"humans_snippets_checked={stats['humans_snippets_checked']}")
    print(f"humans_high_value_urls_checked={stats['humans_high_value_urls_checked']}")
    print(f"humans_urls_checked={stats['humans_urls_checked']}")
    print(f"header_blocks={stats['header_blocks']}")
    print(f"header_rules={stats['header_rules']}")
    print(f"redirect_rules={stats['redirect_rules']}")
    print(f"security_txt_files={stats['security_txt_files']}")
    print(f"security_txt_fields={stats['security_txt_fields']}")
    print(f"ads_txt_records={stats['ads_txt_records']}")
    print(f"funnel_event_catalogs_checked={stats['funnel_event_catalogs_checked']}")
    print(f"funnel_events_checked={stats['funnel_events_checked']}")
    print(f"funnel_event_categories_checked={stats['funnel_event_categories_checked']}")
    print(f"funnel_event_roles_checked={stats['funnel_event_roles_checked']}")
    print(f"funnel_markup_actions_checked={stats['funnel_markup_actions_checked']}")
    print(f"funnel_markup_event_names_checked={stats['funnel_markup_event_names_checked']}")
    print(f"funnel_markup_mailtos_checked={stats['funnel_markup_mailtos_checked']}")
    print(f"funnel_markup_luna_products_checked={stats['funnel_markup_luna_products_checked']}")
    print(f"funnel_markup_copy_actions_checked={stats['funnel_markup_copy_actions_checked']}")
    print(f"funnel_markup_story_actions_checked={stats['funnel_markup_story_actions_checked']}")
    print(f"commerce_catalogs_checked={stats['commerce_catalogs_checked']}")
    print(f"commerce_items_checked={stats['commerce_items_checked']}")
    print(f"commerce_types_checked={stats['commerce_types_checked']}")
    print(f"commerce_roles_checked={stats['commerce_roles_checked']}")
    print(f"commerce_safety_boundaries_checked={stats['commerce_safety_boundaries_checked']}")
    print(f"commerce_revenue_playbook_checked={stats['commerce_revenue_playbook_checked']}")
    print(f"commerce_item_playbook_links_checked={stats['commerce_item_playbook_links_checked']}")
    print(f"promotion_tasks_checked={stats['promotion_tasks_checked']}")
    print(f"promotion_revenue_bridge_kpis_checked={stats['promotion_revenue_bridge_kpis_checked']}")
    print(f"promotion_event_kpi_rows_checked={stats['promotion_event_kpi_rows_checked']}")
    print(f"promotion_event_kpi_events_checked={stats['promotion_event_kpi_events_checked']}")
    print(f"promotion_monetization_bridges_checked={stats['promotion_monetization_bridges_checked']}")
    print(f"promotion_platform_profile_setups_checked={stats['promotion_platform_profile_setups_checked']}")
    print(f"promotion_platform_profile_kpi_fields_checked={stats['promotion_platform_profile_kpi_fields_checked']}")
    print(f"site_index_pages_checked={stats['site_index_pages_checked']}")
    print(f"site_index_languages_checked={stats['site_index_languages_checked']}")
    print(f"site_index_groups_checked={stats['site_index_groups_checked']}")
    print(f"site_index_core_flows_checked={stats['site_index_core_flows_checked']}")
    print(f"guardian_profiles_checked={stats['guardian_profiles_checked']}")
    print(f"guardian_profile_love_languages_checked={stats['guardian_profile_love_languages_checked']}")
    print(f"guardian_profile_assets_checked={stats['guardian_profile_assets_checked']}")
    print(f"guardian_profile_routes_checked={stats['guardian_profile_routes_checked']}")
    print(f"guardian_profile_guides_checked={stats['guardian_profile_guides_checked']}")
    print(f"site_health_snapshots_checked={stats['site_health_snapshots_checked']}")
    print(f"site_health_coverage_fields_checked={stats['site_health_coverage_fields_checked']}")
    print(f"site_health_support_files_checked={stats['site_health_support_files_checked']}")
    print(f"site_health_required_gates_checked={stats['site_health_required_gates_checked']}")
    print(f"site_health_primary_indexes_checked={stats['site_health_primary_indexes_checked']}")
    print(f"site_health_safety_boundaries_checked={stats['site_health_safety_boundaries_checked']}")
    print(f"release_files_checked={stats['release_files_checked']}")
    print(f"release_content_fields_checked={stats['release_content_fields_checked']}")
    print(f"release_public_indexes_checked={stats['release_public_indexes_checked']}")
    print(f"release_verification_commands_checked={stats['release_verification_commands_checked']}")
    print(f"release_required_outcomes_checked={stats['release_required_outcomes_checked']}")
    print(f"release_safety_boundaries_checked={stats['release_safety_boundaries_checked']}")
    print(f"safety_index_files_checked={stats['safety_index_files_checked']}")
    print(f"safety_index_boundaries_checked={stats['safety_index_boundaries_checked']}")
    print(f"safety_index_routes_checked={stats['safety_index_routes_checked']}")
    print(f"safety_index_not_for_checked={stats['safety_index_not_for_checked']}")
    print(f"safety_index_first_steps_checked={stats['safety_index_first_steps_checked']}")
    print(f"ai_discovery_files_checked={stats['ai_discovery_files_checked']}")
    print(f"ai_discovery_guidance_fields_checked={stats['ai_discovery_guidance_fields_checked']}")
    print(f"ai_discovery_totals_checked={stats['ai_discovery_totals_checked']}")
    print(f"ai_discovery_guardians_checked={stats['ai_discovery_guardians_checked']}")
    print(f"ai_discovery_questions_checked={stats['ai_discovery_questions_checked']}")
    print(f"ai_discovery_priority_urls_checked={stats['ai_discovery_priority_urls_checked']}")
    print(f"ai_discovery_discovery_files_checked={stats['ai_discovery_discovery_files_checked']}")
    print(f"discovery_cross_indexes_checked={stats['discovery_cross_indexes_checked']}")
    print(f"discovery_cross_index_urls_checked={stats['discovery_cross_index_urls_checked']}")
    print(f"discovery_cross_index_targets_checked={stats['discovery_cross_index_targets_checked']}")
    print(f"discovery_cross_index_fragments_checked={stats['discovery_cross_index_fragments_checked']}")
    print(f"discovery_cross_core_routes_checked={stats['discovery_cross_core_routes_checked']}")
    print(f"adsense_account_meta_tags={stats['adsense_account_meta_tags']}")
    print(f"policy_pages={stats['policy_pages']}")
    print(f"policy_updated_labels_checked={stats['policy_updated_labels_checked']}")
    print(f"contact_localized_subject_pages={stats['contact_localized_subject_pages']}")
    print(f"mailto_links={stats['mailto_links']}")
    print(f"anchor_accessible_names={stats['anchor_accessible_names']}")
    print(f"versioned_static_assets={stats['versioned_static_assets']}")
    print(f"legacy_static_assets_checked={stats['legacy_static_assets_checked']}")
    print(f"design_css_files_checked={stats['design_css_files_checked']}")
    print(f"design_letter_spacing_rules_checked={stats['design_letter_spacing_rules_checked']}")
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
