#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from io import BytesIO
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

from PIL import Image


DEFAULT_BASE_URL = "https://lovetypes.tw"
CANONICAL_HOST = "lovetypes.tw"
EXPECTED_FEED_ITEMS = 12
EXPECTED_MANIFEST_LANG = "zh-TW"
EXPECTED_MANIFEST_SHORTCUTS = 6
EXPECTED_MANIFEST_SHORTCUT_URLS = (
    "/start/",
    "/garden-map/",
    "/characters/",
    "/resources/",
    "/keepsakes/",
    "/luna-yoga-music/",
)
EXPECTED_MANIFEST_SCREENSHOTS = {
    "/assets/lovetypes/pwa/home-desktop-screenshot.webp": (1440, 900),
    "/assets/lovetypes/pwa/home-mobile-screenshot.webp": (390, 844),
}
EXPECTED_ADS_RECORD = "google.com, ca-pub-4093856660317740, DIRECT, f08c47fec0942fa0"
EXPECTED_SUPPORT_FILES = {
    "robots.txt",
    "sitemap.xml",
    "feed.xml",
    "site.webmanifest",
    "llms.txt",
    "humans.txt",
    "security.txt",
    ".well-known/security.txt",
    "ads.txt",
    "funnel-events.json",
    "commerce-catalog.json",
    "site-index.json",
    "guardian-profiles.json",
    "safety-index.json",
    "ai-discovery.json",
    "promotion-kit.json",
    "release.json",
    "site-health.json",
}
EXPECTED_SUPPORT_FILE_COUNT = len(EXPECTED_SUPPORT_FILES)
REQUIRED_LLMS_SECTIONS = (
    "# LoveTypes - Heart Garden Emotion Guardians",
    "## Canonical Site",
    "## Core Concept",
    "## Five Guardians",
    "## High-Value Pages",
    "## AI Discovery Files",
    "## Guide Index",
    "## Commercial and Safety Boundaries",
)
REQUIRED_LLMS_SNIPPETS = (
    "Production: https://lovetypes.tw/",
    "Primary language: Traditional Chinese",
    "Traditional Chinese pages use Books.com.tw affiliate URLs",
    "Amazon Associates tag parenttechche-20",
    "No full-site advertising script is enabled",
    "Generative answer index: /ai-discovery.json",
    "Contact email: contact@lovetypes.tw",
)
REQUIRED_LLMS_HIGH_VALUE_URLS = (
    "https://lovetypes.tw/start/",
    "https://lovetypes.tw/",
    "https://lovetypes.tw/garden-map/",
    "https://lovetypes.tw/characters/",
    "https://lovetypes.tw/guides/",
    "https://lovetypes.tw/resources/",
    "https://lovetypes.tw/repair-plan/",
    "https://lovetypes.tw/keepsakes/",
    "https://lovetypes.tw/luna-yoga-music/",
    "https://lovetypes.tw/about/",
    "https://lovetypes.tw/theory/",
    "https://lovetypes.tw/contact/",
    "https://lovetypes.tw/privacy/",
    "https://lovetypes.tw/terms/",
)
REQUIRED_SECURITY_FIELDS = (
    "Contact: mailto:contact@lovetypes.tw",
    "Policy: https://lovetypes.tw/privacy/",
    "Canonical: https://lovetypes.tw/.well-known/security.txt",
)
REQUIRED_HUMANS_SNIPPETS = (
    "/* TEAM */",
    "Site: LoveTypes",
    "Contact: contact@lovetypes.tw",
    "Production: https://lovetypes.tw/",
    "Generator: tools/generate_multilingual_site.py",
    "Hosting: Cloudflare Pages",
    "Resources may contain localized affiliate links",
    "Luna packs use Gumroad purchase links",
    "not therapy, medical, legal, or diagnostic advice",
)
REQUIRED_ROBOTS_LINES = (
    "User-agent: *",
    "Allow: /",
    "Sitemap: https://lovetypes.tw/sitemap.xml",
)
REQUIRED_ROBOTS_SITEMAP_URLS = (
    "https://lovetypes.tw/",
    "https://lovetypes.tw/start/",
    "https://lovetypes.tw/characters/",
    "https://lovetypes.tw/resources/",
    "https://lovetypes.tw/contact/",
    "https://lovetypes.tw/privacy/",
    "https://lovetypes.tw/terms/",
)
URL_RE = re.compile(r"https://lovetypes\.tw/[^\s),]+")
REQUIRED_FUNNEL_EVENTS = {
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
EXPECTED_RUNTIME_PACK_EVENT_ROLES = {
    "home_saved_pack_free_keepsake": "retention",
    "home_saved_pack_owned_request": "lead",
    "home_saved_pack_luna": "navigation",
    "home_saved_pack_contact": "lead",
    "home_saved_pack_link": "navigation",
    "supply_pack_free_keepsake": "retention",
    "supply_pack_owned_request": "lead",
    "supply_pack_luna": "navigation",
    "supply_pack_contact": "lead",
    "supply_pack_link": "navigation",
}
EXPECTED_COMMERCE_TYPE_COUNTS = {
    "free_keepsake": 5,
    "owned_supply_waitlist": 5,
    "affiliate_book": 4,
    "luna_gumroad_pack": 6,
}
EXPECTED_COMMERCE_ROLE_COUNTS = {"lead": 5, "retention": 5, "revenue": 10}
EXPECTED_AFFILIATE_LOCALE_POLICY = {
    "zh": {"provider": "books.com.tw", "host": "www.books.com.tw"},
    "en": {"provider": "amazon", "host": "www.amazon.com", "tag": "parenttechche-20"},
    "ja": {"provider": "amazon", "host": "www.amazon.com", "tag": "parenttechche-20"},
    "ko": {"provider": "amazon", "host": "www.amazon.com", "tag": "parenttechche-20"},
    "es": {"provider": "amazon", "host": "www.amazon.com", "tag": "parenttechche-20"},
}
EXPECTED_AMAZON_ASSOCIATE_TAG = "parenttechche-20"
EXPECTED_BOOKS_AFFILIATE_HOST = "www.books.com.tw"
EXPECTED_AMAZON_AFFILIATE_HOST = "www.amazon.com"
EXPECTED_SITE_INDEX_LANGS = {"zh", "en", "ja", "ko", "es"}
EXPECTED_SITE_INDEX_FLOWS = {"shorts_to_quiz", "quiz_to_guardian", "guardian_supply", "supply_to_contact", "trust_boundary"}
EXPECTED_GUARDIAN_LANGUAGES = {
    "iris": "Words of affirmation",
    "noah": "Quality time",
    "vivian": "Receiving gifts",
    "claire": "Acts of service",
    "dora": "Physical touch",
}


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical = ""
        self.description = ""
        self.ids: set[str] = set()
        self.robots = ""
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "title":
            self._in_title = True
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")
        elif tag == "meta" and data.get("name", "").lower() == "description":
            self.description = data.get("content", "")
        elif tag == "meta" and data.get("name", "").lower() == "robots":
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
            request = Request(url, headers={"User-Agent": "LoveTypes public discovery smoke/1.0"})
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


def is_lovetypes_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.netloc == CANONICAL_HOST


def route_url(value: str, base_url: str) -> str:
    url = urljoin(base_url + "/", value.lstrip("/")) if value.startswith("/") else value
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path or '/'}"


def canonical_route_for_url(value: str, base_url: str) -> str:
    url = urljoin(base_url + "/", value.lstrip("/")) if value.startswith("/") else value
    parsed = urlparse(url)
    return f"https://{CANONICAL_HOST}{parsed.path or '/'}"


def walk_index_urls(data: object, path: str = "$") -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            child_path = f"{path}.{key}"
            if isinstance(value, str):
                if value.startswith("https://lovetypes.tw") or value.startswith("/"):
                    urls.append((child_path, value))
            else:
                urls.extend(walk_index_urls(value, child_path))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            child_path = f"{path}[{index}]"
            if isinstance(value, str):
                if value.startswith("https://lovetypes.tw") or value.startswith("/"):
                    urls.append((child_path, value))
            else:
                urls.extend(walk_index_urls(value, child_path))
    return urls


def cache_is_reasonable(path: str, response: Response) -> list[str]:
    issues: list[str] = []
    host = urlparse(response.url).netloc
    if host.startswith(("127.0.0.1", "localhost")):
        return issues
    cache_control = response.headers.get("cache-control", "")
    if "max-age=600" not in cache_control:
        issues.append(f"{path}: expected short HTML/XML discovery cache, got {cache_control!r}")
    return issues


def page_title_without_brand(title: str) -> str:
    return title.strip().split(" | ", 1)[0].split("｜", 1)[0].strip()


def check_feed(base_url: str) -> tuple[list[str], int, int, int, int]:
    path = "/feed.xml"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0
    if "xml" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected XML content type, got {response.headers.get('content-type')!r}")
    issues.extend(cache_is_reasonable(path, response))
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [f"{path}: invalid XML: {error}"], 0, 0, 0, 0
    if root.tag != "rss" or root.attrib.get("version") != "2.0":
        issues.append(f"{path}: expected RSS 2.0 root")
    channel = root.find("channel")
    if channel is None:
        return [f"{path}: missing channel"], 0, 0, 0, 0
    site_index_issues, site_index_canonicals = load_site_index_canonicals(base_url, path)
    issues.extend(site_index_issues)
    for tag in ("title", "link", "description", "language", "lastBuildDate"):
        if not (channel.findtext(tag) or "").strip():
            issues.append(f"{path}: channel missing {tag}")
    if channel.findtext("language") != "zh-TW":
        issues.append(f"{path}: channel language should be zh-TW")
    if channel.findtext("link") != "https://lovetypes.tw/guides/":
        issues.append(f"{path}: channel link should be https://lovetypes.tw/guides/")
    last_build = (channel.findtext("lastBuildDate") or "").strip()
    try:
        parsedate_to_datetime(last_build)
    except (TypeError, ValueError):
        issues.append(f"{path}: invalid lastBuildDate {last_build!r}")

    items = channel.findall("item")
    if len(items) != EXPECTED_FEED_ITEMS:
        issues.append(f"{path}: expected {EXPECTED_FEED_ITEMS} items, found {len(items)}")
    seen_links: set[str] = set()
    links_checked = 0
    item_metadata_checked = 0
    site_index_links_checked = 0
    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or "").strip()
        description = (item.findtext("description") or "").strip()
        category = (item.findtext("category") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        if not title or not link or not guid or not description or not category or not pub_date:
            issues.append(f"{path}: feed item missing required fields: {link or title or '<unknown>'}")
        if link in seen_links:
            issues.append(f"{path}: duplicate feed item link: {link}")
        seen_links.add(link)
        guid_node = item.find("guid")
        if guid_node is None or guid_node.attrib.get("isPermaLink") != "true" or guid != link:
            issues.append(f"{path}: guid should be permalink matching link: {link}")
        if not is_lovetypes_url(link):
            issues.append(f"{path}: feed item link should be absolute production URL: {link}")
            continue
        if link in site_index_canonicals:
            site_index_links_checked += 1
        else:
            issues.append(f"{path}: feed item link missing from site-index.json: {link}")
        try:
            parsedate_to_datetime(pub_date)
        except (TypeError, ValueError):
            issues.append(f"{path}: invalid pubDate for {link}: {pub_date!r}")
        item_response = request_url(link)
        links_checked += 1
        if item_response.status != 200:
            issues.append(f"{path}: item link {link} expected status 200, got {item_response.status}")
            continue
        head = HeadParser()
        head.feed(item_response.text)
        robots_tokens = {token.strip().lower() for token in head.robots.split(",") if token.strip()}
        if "noindex" in robots_tokens:
            issues.append(f"{path}: item link should not point to noindex page: {link}")
        if head.canonical != link:
            issues.append(f"{path}: item link {link} canonical should match, got {head.canonical!r}")
        else:
            item_metadata_checked += 1
        page_title = page_title_without_brand(head.title)
        if page_title != title:
            issues.append(f"{path}: item title {title!r} should match page title {page_title!r} for {link}")
        if description and head.description and not description.startswith(head.description):
            issues.append(f"{path}: item description should start with page description for {link}")
    return issues, len(items), links_checked, item_metadata_checked, site_index_links_checked


def parse_icon_sizes(value: str) -> set[tuple[int, int]]:
    sizes: set[tuple[int, int]] = set()
    for token in value.split():
        if token.lower() == "any":
            continue
        match = re.fullmatch(r"(\d+)x(\d+)", token.lower())
        if match:
            sizes.add((int(match.group(1)), int(match.group(2))))
    return sizes


def image_declared_sizes(body: bytes) -> set[tuple[int, int]]:
    with Image.open(BytesIO(body)) as image:
        ico_sizes = getattr(getattr(image, "ico", None), "sizes", None)
        if callable(ico_sizes):
            return {(int(width), int(height)) for width, height in ico_sizes()}
        return {(int(image.size[0]), int(image.size[1]))}


def check_manifest(base_url: str) -> tuple[list[str], int, int, int, int, int, int, int, int, int]:
    path = "/site.webmanifest"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", "") and "manifest" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected manifest/json content type, got {response.headers.get('content-type')!r}")
    issues.extend(cache_is_reasonable(path, response))
    try:
        manifest = json.loads(response.text)
    except json.JSONDecodeError as error:
        return [f"{path}: invalid JSON: {error}"], 0, 0, 0, 0, 0, 0, 0, 0, 0
    for field in ("name", "short_name", "description", "start_url", "scope", "display", "theme_color", "icons"):
        if not manifest.get(field):
            issues.append(f"{path}: missing required field {field}")
    if manifest.get("start_url") != "/" or manifest.get("scope") != "/":
        issues.append(f"{path}: start_url and scope should both be /")
    if manifest.get("lang") != EXPECTED_MANIFEST_LANG:
        issues.append(f"{path}: lang should be {EXPECTED_MANIFEST_LANG}")
    shortcuts = manifest.get("shortcuts", [])
    if not isinstance(shortcuts, list) or len(shortcuts) != EXPECTED_MANIFEST_SHORTCUTS:
        issues.append(f"{path}: expected {EXPECTED_MANIFEST_SHORTCUTS} shortcuts, got {len(shortcuts) if isinstance(shortcuts, list) else 'invalid'}")
        shortcuts = []
    shortcut_urls = {
        shortcut.get("url")
        for shortcut in shortcuts
        if isinstance(shortcut, dict) and isinstance(shortcut.get("url"), str)
    }
    manifest_expected_shortcuts_checked = 0
    for expected_url in EXPECTED_MANIFEST_SHORTCUT_URLS:
        if expected_url in shortcut_urls:
            manifest_expected_shortcuts_checked += 1
        else:
            issues.append(f"{path}: missing expected shortcut URL {expected_url}")
    shortcut_links_checked = 0
    shortcut_icons_checked = 0
    shortcut_icon_dimensions_checked = 0
    for shortcut in shortcuts:
        url = shortcut.get("url") if isinstance(shortcut, dict) else ""
        name = shortcut.get("name") if isinstance(shortcut, dict) else ""
        if not name or not url:
            issues.append(f"{path}: shortcut missing name or url: {shortcut!r}")
            continue
        target = request_url(urljoin(base_url + "/", url.lstrip("/")))
        shortcut_links_checked += 1
        if target.status != 200:
            issues.append(f"{path}: shortcut {url} expected status 200, got {target.status}")
        shortcut_icons = shortcut.get("icons", []) if isinstance(shortcut, dict) else []
        if not isinstance(shortcut_icons, list) or not shortcut_icons:
            issues.append(f"{path}: shortcut {url} should include icons")
            continue
        for shortcut_icon in shortcut_icons:
            src = shortcut_icon.get("src") if isinstance(shortcut_icon, dict) else ""
            sizes = shortcut_icon.get("sizes") if isinstance(shortcut_icon, dict) else ""
            icon_type = shortcut_icon.get("type") if isinstance(shortcut_icon, dict) else ""
            if not src or not sizes or not icon_type:
                issues.append(f"{path}: shortcut {url} icon missing src, sizes, or type: {shortcut_icon!r}")
                continue
            if icon_type != "image/png":
                issues.append(f"{path}: shortcut {url} icon should be image/png: {src}")
            icon_response = request_url(urljoin(base_url + "/", src.lstrip("/")))
            shortcut_icons_checked += 1
            if icon_response.status != 200:
                issues.append(f"{path}: shortcut {url} icon {src} expected status 200, got {icon_response.status}")
                continue
            content_type = icon_response.headers.get("content-type", "")
            if icon_type not in content_type:
                issues.append(f"{path}: shortcut {url} icon {src} expected content type containing {icon_type!r}, got {content_type!r}")
            expected_sizes = parse_icon_sizes(sizes)
            if not expected_sizes:
                issues.append(f"{path}: shortcut {url} icon {src} should declare concrete sizes, got {sizes!r}")
                continue
            try:
                actual_sizes = image_declared_sizes(icon_response.body)
            except OSError as error:
                issues.append(f"{path}: shortcut {url} icon {src} could not be decoded: {error}")
                continue
            shortcut_icon_dimensions_checked += 1
            if not expected_sizes.issubset(actual_sizes):
                issues.append(
                    f"{path}: shortcut {url} icon {src} declared sizes {sorted(expected_sizes)} "
                    f"should exist in file sizes {sorted(actual_sizes)}"
                )
    icons = manifest.get("icons", [])
    if not isinstance(icons, list) or not icons:
        issues.append(f"{path}: icons should be a non-empty list")
        icons = []
    icons_checked = 0
    icon_dimensions_checked = 0
    for icon in icons:
        src = icon.get("src") if isinstance(icon, dict) else ""
        sizes = icon.get("sizes") if isinstance(icon, dict) else ""
        icon_type = icon.get("type") if isinstance(icon, dict) else ""
        if not src or not sizes or not icon_type:
            issues.append(f"{path}: icon missing src, sizes, or type: {icon!r}")
            continue
        icon_response = request_url(urljoin(base_url + "/", src.lstrip("/")))
        icons_checked += 1
        if icon_response.status != 200:
            issues.append(f"{path}: icon {src} expected status 200, got {icon_response.status}")
        content_type = icon_response.headers.get("content-type", "")
        if icon_type not in content_type:
            issues.append(f"{path}: icon {src} expected content type containing {icon_type!r}, got {content_type!r}")
        expected_sizes = parse_icon_sizes(sizes)
        if not expected_sizes:
            issues.append(f"{path}: icon {src} should declare concrete sizes, got {sizes!r}")
            continue
        try:
            actual_sizes = image_declared_sizes(icon_response.body)
        except OSError as error:
            issues.append(f"{path}: icon {src} could not be decoded: {error}")
            continue
        icon_dimensions_checked += 1
        if not expected_sizes.issubset(actual_sizes):
            issues.append(
                f"{path}: icon {src} declared sizes {sorted(expected_sizes)} should exist in file sizes {sorted(actual_sizes)}"
            )

    screenshots = manifest.get("screenshots", [])
    if not isinstance(screenshots, list) or len(screenshots) != len(EXPECTED_MANIFEST_SCREENSHOTS):
        issues.append(
            f"{path}: expected {len(EXPECTED_MANIFEST_SCREENSHOTS)} screenshots, "
            f"got {len(screenshots) if isinstance(screenshots, list) else 'invalid'}"
        )
        screenshots = []
    screenshot_urls = {
        screenshot.get("src")
        for screenshot in screenshots
        if isinstance(screenshot, dict) and isinstance(screenshot.get("src"), str)
    }
    for expected_src in EXPECTED_MANIFEST_SCREENSHOTS:
        if expected_src not in screenshot_urls:
            issues.append(f"{path}: missing expected screenshot {expected_src}")
    screenshots_checked = 0
    screenshot_dimensions_checked = 0
    for screenshot in screenshots:
        src = screenshot.get("src") if isinstance(screenshot, dict) else ""
        sizes = screenshot.get("sizes") if isinstance(screenshot, dict) else ""
        image_type = screenshot.get("type") if isinstance(screenshot, dict) else ""
        label = screenshot.get("label") if isinstance(screenshot, dict) else ""
        if not src or not sizes or not image_type or not label:
            issues.append(f"{path}: screenshot missing src, sizes, type, or label: {screenshot!r}")
            continue
        screenshot_response = request_url(urljoin(base_url + "/", src.lstrip("/")))
        screenshots_checked += 1
        if screenshot_response.status != 200:
            issues.append(f"{path}: screenshot {src} expected status 200, got {screenshot_response.status}")
            continue
        content_type = screenshot_response.headers.get("content-type", "")
        if image_type not in content_type:
            issues.append(f"{path}: screenshot {src} expected content type containing {image_type!r}, got {content_type!r}")
        host = urlparse(base_url).hostname or ""
        cache_control = screenshot_response.headers.get("cache-control", "").lower()
        if host not in {"127.0.0.1", "localhost"} and ("max-age=31536000" not in cache_control or "immutable" not in cache_control):
            issues.append(f"{path}: screenshot {src} should be immutable cached, got {cache_control!r}")
        expected_size = EXPECTED_MANIFEST_SCREENSHOTS.get(src)
        expected_sizes = parse_icon_sizes(sizes)
        try:
            actual_sizes = image_declared_sizes(screenshot_response.body)
        except OSError as error:
            issues.append(f"{path}: screenshot {src} could not be decoded: {error}")
            continue
        screenshot_dimensions_checked += 1
        if expected_size and expected_size not in actual_sizes:
            issues.append(f"{path}: screenshot {src} should be {expected_size[0]}x{expected_size[1]}, got {sorted(actual_sizes)}")
        if expected_sizes and not expected_sizes.issubset(actual_sizes):
            issues.append(f"{path}: screenshot {src} declared sizes {sorted(expected_sizes)} should exist in file sizes {sorted(actual_sizes)}")
    return (
        issues,
        icons_checked,
        icon_dimensions_checked,
        len(shortcuts),
        shortcut_links_checked,
        manifest_expected_shortcuts_checked,
        shortcut_icons_checked,
        shortcut_icon_dimensions_checked,
        screenshots_checked,
        screenshot_dimensions_checked,
    )


def check_llms(base_url: str) -> tuple[list[str], int, int, int, int, int]:
    path = "/llms.txt"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0
    if not response.headers.get("content-type", "").startswith("text/plain"):
        issues.append(f"{path}: expected text/plain content type, got {response.headers.get('content-type')!r}")
    issues.extend(cache_is_reasonable(path, response))
    text = response.text
    sections_checked = 0
    for section in REQUIRED_LLMS_SECTIONS:
        sections_checked += 1
        if section not in text:
            issues.append(f"{path}: missing required section {section!r}")
    snippets_checked = 0
    for snippet in REQUIRED_LLMS_SNIPPETS:
        snippets_checked += 1
        if snippet not in text:
            issues.append(f"{path}: missing required snippet {snippet!r}")
    high_value_urls_checked = 0
    for url in REQUIRED_LLMS_HIGH_VALUE_URLS:
        if url in text:
            high_value_urls_checked += 1
        else:
            issues.append(f"{path}: missing high-value URL {url}")
    urls = sorted(set(match.group(0).rstrip(".,;") for match in URL_RE.finditer(text)))
    urls_checked = 0
    url_canonicals_checked = 0
    for url in urls:
        target = request_url(url)
        urls_checked += 1
        if target.status != 200:
            issues.append(f"{path}: listed URL {url} expected status 200, got {target.status}")
            continue
        head = HeadParser()
        head.feed(target.text)
        robots_tokens = {token.strip().lower() for token in head.robots.split(",") if token.strip()}
        if "noindex" in robots_tokens:
            issues.append(f"{path}: listed URL should not point to noindex page: {url}")
        if head.canonical:
            url_canonicals_checked += 1
            if head.canonical != url:
                issues.append(f"{path}: listed URL {url} canonical should match, got {head.canonical!r}")
        else:
            issues.append(f"{path}: listed URL {url} missing canonical")
    return issues, sections_checked, snippets_checked, urls_checked, high_value_urls_checked, url_canonicals_checked


def parse_security_fields(text: str) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        fields.setdefault(key.lower(), []).append(value)
    return fields


def check_security_date_fields(path: str, text: str) -> tuple[list[str], int]:
    issues: list[str] = []
    checked = 0
    fields = parse_security_fields(text)
    preferred_languages = fields.get("preferred-languages", [])
    checked += 1
    if not any("zh-TW" in value and "en" in value for value in preferred_languages):
        issues.append(f"{path}: Preferred-Languages should include zh-TW and en")
    expires_values = fields.get("expires", [])
    checked += 1
    if len(expires_values) != 1:
        issues.append(f"{path}: expected one Expires field, found {len(expires_values)}")
    else:
        try:
            expires = datetime.fromisoformat(expires_values[0].replace("Z", "+00:00"))
        except ValueError:
            issues.append(f"{path}: invalid Expires timestamp: {expires_values[0]}")
        else:
            if expires <= datetime.now(timezone.utc):
                issues.append(f"{path}: Expires timestamp is in the past: {expires_values[0]}")
    return issues, checked


def load_site_index_canonicals(base_url: str, source_path: str) -> tuple[list[str], set[str]]:
    response = request_url(urljoin(base_url + "/", "site-index.json"))
    if response.status != 200:
        return [f"{source_path}: site-index.json expected status 200, got {response.status}"], set()
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as error:
        return [f"{source_path}: site-index.json invalid JSON: {error}"], set()
    pages = data.get("pages") if isinstance(data, dict) else None
    if not isinstance(pages, list):
        return [f"{source_path}: site-index.json pages should be a list"], set()
    return [], {
        page.get("canonical")
        for page in pages
        if isinstance(page, dict) and isinstance(page.get("canonical"), str) and page.get("canonical")
    }


def check_text_files(base_url: str) -> tuple[list[str], int, int, int, int, int, int]:
    issues: list[str] = []
    text_files_checked = 0
    security_fields_checked = 0
    security_date_fields_checked = 0
    humans_snippets_checked = 0
    humans_urls_checked = 0
    humans_site_index_urls_checked = 0
    security = request_url(urljoin(base_url + "/", "security.txt"))
    well_known = request_url(urljoin(base_url + "/", ".well-known/security.txt"))
    for path, response in (("/security.txt", security), ("/.well-known/security.txt", well_known)):
        text_files_checked += 1
        if response.status != 200:
            issues.append(f"{path}: expected status 200, got {response.status}")
            continue
        if not response.headers.get("content-type", "").startswith("text/plain"):
            issues.append(f"{path}: expected text/plain content type, got {response.headers.get('content-type')!r}")
        issues.extend(cache_is_reasonable(path, response))
        for field in REQUIRED_SECURITY_FIELDS:
            security_fields_checked += 1
            if field not in response.text:
                issues.append(f"{path}: missing required field {field!r}")
        date_issues, date_fields_checked = check_security_date_fields(path, response.text)
        issues.extend(date_issues)
        security_date_fields_checked += date_fields_checked
    if security.status == 200 and well_known.status == 200 and security.text != well_known.text:
        issues.append("/.well-known/security.txt: body should match /security.txt")

    ads = request_url(urljoin(base_url + "/", "ads.txt"))
    text_files_checked += 1
    if ads.status != 200:
        issues.append(f"/ads.txt: expected status 200, got {ads.status}")
    else:
        if not ads.headers.get("content-type", "").startswith("text/plain"):
            issues.append(f"/ads.txt: expected text/plain content type, got {ads.headers.get('content-type')!r}")
        issues.extend(cache_is_reasonable("/ads.txt", ads))
        records = [line.strip() for line in ads.text.splitlines() if line.strip() and not line.strip().startswith("#")]
        if records != [EXPECTED_ADS_RECORD]:
            issues.append(f"/ads.txt: expected only {EXPECTED_ADS_RECORD!r}, got {records!r}")

    humans = request_url(urljoin(base_url + "/", "humans.txt"))
    text_files_checked += 1
    if humans.status != 200:
        issues.append(f"/humans.txt: expected status 200, got {humans.status}")
    else:
        if not humans.headers.get("content-type", "").startswith("text/plain"):
            issues.append(f"/humans.txt: expected text/plain content type, got {humans.headers.get('content-type')!r}")
        issues.extend(cache_is_reasonable("/humans.txt", humans))
        for snippet in REQUIRED_HUMANS_SNIPPETS:
            humans_snippets_checked += 1
            if snippet not in humans.text:
                issues.append(f"/humans.txt: missing required snippet {snippet!r}")
        site_index_issues, site_index_canonicals = load_site_index_canonicals(base_url, "/humans.txt")
        issues.extend(site_index_issues)
        humans_urls = sorted(set(match.group(0).rstrip(".,;") for match in URL_RE.finditer(humans.text)))
        for url in humans_urls:
            humans_urls_checked += 1
            if url in site_index_canonicals:
                humans_site_index_urls_checked += 1
            else:
                issues.append(f"/humans.txt: listed URL missing from site-index.json: {url}")
            target = request_url(url)
            if target.status != 200:
                issues.append(f"/humans.txt: listed URL {url} expected status 200, got {target.status}")
                continue
            head = HeadParser()
            head.feed(target.text)
            robots_tokens = {token.strip().lower() for token in head.robots.split(",") if token.strip()}
            if "noindex" in robots_tokens:
                issues.append(f"/humans.txt: listed URL should not point to noindex page: {url}")
            if head.canonical != url:
                issues.append(f"/humans.txt: listed URL {url} canonical should match, got {head.canonical!r}")
    return (
        issues,
        text_files_checked,
        security_fields_checked,
        security_date_fields_checked,
        humans_snippets_checked,
        humans_urls_checked,
        humans_site_index_urls_checked,
    )


def check_robots(base_url: str) -> tuple[list[str], int, int, int]:
    path = "/robots.txt"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    robots_lines_checked = 0
    sitemap_links_checked = 0
    sitemap_core_urls_checked = 0
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], robots_lines_checked, sitemap_links_checked, sitemap_core_urls_checked
    if not response.headers.get("content-type", "").startswith("text/plain"):
        issues.append(f"{path}: expected text/plain content type, got {response.headers.get('content-type')!r}")

    lines = [line.strip() for line in response.text.splitlines() if line.strip() and not line.strip().startswith("#")]
    for required_line in REQUIRED_ROBOTS_LINES:
        robots_lines_checked += 1
        if required_line not in lines:
            issues.append(f"{path}: missing required line {required_line!r}")
    wildcard_directives: list[str] = []
    in_wildcard_group = False
    for line in lines:
        key = line.split(":", 1)[0].strip().lower() if ":" in line else ""
        value = line.split(":", 1)[1].strip().lower() if ":" in line else ""
        if key == "user-agent":
            in_wildcard_group = value == "*"
            continue
        if in_wildcard_group and key in {"allow", "disallow"}:
            wildcard_directives.append(f"{key}: {value}")
    if "allow: /" not in wildcard_directives:
        issues.append(f"{path}: User-agent * should allow /")
    if "disallow: /" in wildcard_directives:
        issues.append(f"{path}: User-agent * should not disallow /")

    sitemap_urls = [line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("sitemap:")]
    for sitemap_url in sitemap_urls:
        sitemap_links_checked += 1
        if sitemap_url != DEFAULT_BASE_URL + "/sitemap.xml":
            issues.append(f"{path}: sitemap should be {DEFAULT_BASE_URL}/sitemap.xml, got {sitemap_url!r}")
            continue
        sitemap_response = request_url(sitemap_url)
        if sitemap_response.status != 200:
            issues.append(f"{path}: sitemap {sitemap_url} expected status 200, got {sitemap_response.status}")
            continue
        if "xml" not in sitemap_response.headers.get("content-type", ""):
            issues.append(f"{path}: sitemap {sitemap_url} expected XML content type, got {sitemap_response.headers.get('content-type')!r}")
        try:
            root = ET.fromstring(sitemap_response.text)
        except ET.ParseError as error:
            issues.append(f"{path}: sitemap {sitemap_url} should be parseable XML: {error}")
            continue
        sitemap_locs = {element.text.strip() for element in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if element.text}
        if not sitemap_locs:
            issues.append(f"{path}: sitemap {sitemap_url} should contain URL loc entries")
        for required_url in REQUIRED_ROBOTS_SITEMAP_URLS:
            if required_url in sitemap_locs:
                sitemap_core_urls_checked += 1
            else:
                issues.append(f"{path}: sitemap {sitemap_url} missing core URL {required_url}")
    if not sitemap_urls:
        issues.append(f"{path}: missing Sitemap directive")
    return issues, robots_lines_checked, sitemap_links_checked, sitemap_core_urls_checked


def check_funnel_events(base_url: str) -> tuple[list[str], int, int, int, int]:
    path = "/funnel-events.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0
    events = data.get("events", [])
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("localStorageKey") != "lovetypes:funnel-events:v1":
        issues.append(f"{path}: localStorageKey should match runtime storage key")
    if not isinstance(events, list) or not events:
        return [f"{path}: events should be a non-empty list"], 0, 0, 0, 0
    names: set[str] = set()
    event_by_name: dict[str, dict] = {}
    categories: set[str] = set()
    roles: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            issues.append(f"{path}: event entry should be an object")
            continue
        name = event.get("name")
        if not isinstance(name, str) or not re.match(r"^[a-z][a-z0-9_]*$", name):
            issues.append(f"{path}: invalid event name {name!r}")
            continue
        if name in names:
            issues.append(f"{path}: duplicate event name {name}")
        names.add(name)
        event_by_name[name] = event
        count = event.get("count")
        if not isinstance(count, int) or count <= 0:
            issues.append(f"{path}: event {name} should include positive count")
        pages = event.get("pages")
        page_count = event.get("pageCount")
        if not isinstance(pages, list) or not pages:
            issues.append(f"{path}: event {name} should include pages")
        if not isinstance(page_count, int) or page_count < len(pages or []):
            issues.append(f"{path}: event {name} should include valid pageCount")
        category = event.get("category")
        role = event.get("role")
        if not isinstance(category, str) or not category:
            issues.append(f"{path}: event {name} missing category")
        else:
            categories.add(category)
        if not isinstance(role, str) or not role:
            issues.append(f"{path}: event {name} missing role")
        else:
            roles.add(role)
    missing = sorted(REQUIRED_FUNNEL_EVENTS.difference(names))
    if missing:
        issues.append(f"{path}: missing core funnel events {', '.join(missing)}")
    gumroad_event = event_by_name.get("luna_gumroad_pack_click", {})
    if gumroad_event.get("role") != "revenue":
        issues.append(f"{path}: luna_gumroad_pack_click should be a revenue event")
    runtime_pack_events_checked = 0
    for name, expected_role in EXPECTED_RUNTIME_PACK_EVENT_ROLES.items():
        event = event_by_name.get(name)
        if not event:
            issues.append(f"{path}: missing runtime pack event {name}")
            continue
        runtime_pack_events_checked += 1
        if event.get("role") != expected_role:
            issues.append(f"{path}: {name} should be a {expected_role} event")
    if len(events) < 50:
        issues.append(f"{path}: expected at least 50 funnel events, got {len(events)}")
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("events") != len(events):
        issues.append(f"{path}: totals.events should match event count")
    return issues, len(events), len(categories), len(roles), runtime_pack_events_checked


def check_promotion_event_kpi_alignment(base_url: str) -> tuple[list[str], int, int, int, int, int, int]:
    issues: list[str] = []
    funnel_response = request_url(urljoin(base_url + "/", "funnel-events.json"))
    kit_response = request_url(urljoin(base_url + "/", "promotion-kit.json"))
    if funnel_response.status != 200:
        return [f"/funnel-events.json: expected status 200, got {funnel_response.status}"], 0, 0, 0, 0, 0, 0
    if kit_response.status != 200:
        return [f"/promotion-kit.json: expected status 200, got {kit_response.status}"], 0, 0, 0, 0, 0, 0
    try:
        funnel = json.loads(funnel_response.text)
        kit = json.loads(kit_response.text)
    except json.JSONDecodeError as exc:
        return [f"promotion/funnel alignment: invalid JSON: {exc}"], 0, 0, 0, 0, 0, 0
    funnel_names = {
        event.get("name")
        for event in funnel.get("events", [])
        if isinstance(event, dict) and isinstance(event.get("name"), str)
    }
    measurement = kit.get("measurementPlan", {}) if isinstance(kit, dict) else {}
    if not isinstance(measurement, dict):
        return ["/promotion-kit.json: measurementPlan should be an object"], 0, 0, 0, 0, 0, 0
    event_kpi_map = measurement.get("eventKpiMap", [])
    if not isinstance(event_kpi_map, list) or not event_kpi_map:
        return ["/promotion-kit.json: measurementPlan.eventKpiMap should be a non-empty list"], 0, 0, 0, 0, 0, 0
    mapped_events: set[str] = set()
    seen_kpis: set[str] = set()
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
    required_runtime_pack_kpi_events = set(EXPECTED_RUNTIME_PACK_EVENT_ROLES)
    for row in event_kpi_map:
        if not isinstance(row, dict):
            issues.append("/promotion-kit.json: eventKpiMap entries should be objects")
            continue
        kpi = row.get("kpi")
        if not isinstance(kpi, str) or not kpi:
            issues.append("/promotion-kit.json: eventKpiMap entry missing kpi")
        elif kpi in seen_kpis:
            issues.append(f"/promotion-kit.json: duplicate eventKpiMap KPI {kpi}")
        else:
            seen_kpis.add(kpi)
        events = row.get("events")
        if not isinstance(events, list) or not events:
            issues.append(f"/promotion-kit.json: eventKpiMap {kpi or '<unknown>'} should include events")
            continue
        for event_name in events:
            if not isinstance(event_name, str) or not event_name:
                issues.append(f"/promotion-kit.json: eventKpiMap {kpi or '<unknown>'} has invalid event {event_name!r}")
                continue
            mapped_events.add(event_name)
            if event_name not in funnel_names:
                issues.append(f"/promotion-kit.json: eventKpiMap {kpi or '<unknown>'} references missing funnel event {event_name}")
        for key in ("label", "countRule", "reviewUse"):
            if not isinstance(row.get(key), str) or not row[key]:
                issues.append(f"/promotion-kit.json: eventKpiMap {kpi or '<unknown>'} missing {key}")
        manual_sources = row.get("manualSources")
        if not isinstance(manual_sources, list) or not manual_sources:
            issues.append(f"/promotion-kit.json: eventKpiMap {kpi or '<unknown>'} should include manualSources")
    missing_kpis = sorted(expected_event_kpis.difference(seen_kpis))
    if missing_kpis:
        issues.append(f"/promotion-kit.json: measurementPlan.eventKpiMap missing KPI mappings {', '.join(missing_kpis)}")
    missing_runtime_pack_events = sorted(required_runtime_pack_kpi_events.difference(mapped_events))
    if missing_runtime_pack_events:
        issues.append(
            "/promotion-kit.json: eventKpiMap missing runtime pack events "
            f"{', '.join(missing_runtime_pack_events)}"
        )

    bridge_kpis = measurement.get("revenueBridgeKpis")
    bridge_checked = 0
    if not isinstance(bridge_kpis, list) or len(bridge_kpis) < 5:
        issues.append("/promotion-kit.json: measurementPlan.revenueBridgeKpis should include at least five entries")
    else:
        bridge_checked = len(bridge_kpis)
        bridge_fields = {item.get("field") for item in bridge_kpis if isinstance(item, dict)}
        expected_bridge_fields = {"free_keepsake_downloads", "supply_lead_requests", "luna_pack_clicks", "affiliate_book_clicks", "contact_requests"}
        if not expected_bridge_fields.issubset(bridge_fields):
            issues.append("/promotion-kit.json: measurementPlan.revenueBridgeKpis missing expected fields")
        for item in bridge_kpis:
            if not isinstance(item, dict) or not item.get("playbookId") or not item.get("meaning"):
                issues.append("/promotion-kit.json: measurementPlan.revenueBridgeKpis entries should include playbookId and meaning")
                break

    derived_rates = measurement.get("derivedRates")
    derived_rates_checked = 0
    if not isinstance(derived_rates, list):
        issues.append("/promotion-kit.json: measurementPlan.derivedRates should be a list")
    else:
        derived_rates_checked = len(derived_rates)
        expected_rates = {"lead_capture_rate", "revenue_intent_rate", "keepsake_save_rate"}
        rate_ids = {item.get("id") for item in derived_rates if isinstance(item, dict)}
        if not expected_rates.issubset(rate_ids):
            issues.append("/promotion-kit.json: measurementPlan.derivedRates missing revenue bridge rates")

    decision_rules = measurement.get("decisionRules")
    decision_rules_checked = 0
    if not isinstance(decision_rules, list):
        issues.append("/promotion-kit.json: measurementPlan.decisionRules should be a list")
    else:
        decision_rules_checked = len(decision_rules)
        rule_ids = {item.get("id") for item in decision_rules if isinstance(item, dict)}
        if not {"build_owned_asset", "test_soft_offer"}.issubset(rule_ids):
            issues.append("/promotion-kit.json: measurementPlan.decisionRules missing revenue bridge rules")

    event_safety = measurement.get("eventKpiSafety")
    safety_fields_checked = 0
    if not isinstance(event_safety, dict):
        issues.append("/promotion-kit.json: measurementPlan.eventKpiSafety should be an object")
    else:
        for key in ("manualReviewRequired", "doNotInferPurchasesFromClicks", "doNotTreatGuardianAsDiagnosis"):
            safety_fields_checked += 1
            if event_safety.get(key) is not True:
                issues.append(f"/promotion-kit.json: measurementPlan.eventKpiSafety.{key} should be true")
        source_order = event_safety.get("sourceOfTruthOrder")
        if not isinstance(source_order, list) or len(source_order) < 4:
            issues.append("/promotion-kit.json: measurementPlan.eventKpiSafety.sourceOfTruthOrder should include source priority")
        else:
            safety_fields_checked += 1
    return issues, len(event_kpi_map), len(mapped_events), bridge_checked, derived_rates_checked, decision_rules_checked, safety_fields_checked


def is_expected_commerce_affiliate_url(lang: str, value: str) -> bool:
    parsed = urlparse(value)
    if lang == "zh":
        return (
            parsed.scheme == "https"
            and parsed.hostname == EXPECTED_BOOKS_AFFILIATE_HOST
            and parsed.path.startswith("/exep/assp.php/")
            and "arthur0858" in parsed.path
        )
    return (
        parsed.scheme == "https"
        and parsed.hostname == EXPECTED_AMAZON_AFFILIATE_HOST
        and parsed.path.startswith("/dp/")
        and parse_qs(parsed.query).get("tag", [""])[0] == EXPECTED_AMAZON_ASSOCIATE_TAG
    )


def check_commerce_catalog(base_url: str) -> tuple[list[str], int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]:
    path = "/commerce-catalog.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("contact") != "contact@lovetypes.tw":
        issues.append(f"{path}: contact should be contact@lovetypes.tw")
    boundaries = " ".join(str(item) for item in data.get("safetyBoundaries", []))
    for snippet in ("No therapeutic", "Affiliate links", "Email waitlist", "sensitive personal details"):
        if snippet not in boundaries:
            issues.append(f"{path}: missing safety boundary snippet {snippet!r}")
    affiliate_policy_checked = 0
    affiliate_policy = data.get("affiliateLocalePolicy")
    if not isinstance(affiliate_policy, dict):
        issues.append(f"{path}: affiliateLocalePolicy should be an object")
    else:
        for lang, expected in EXPECTED_AFFILIATE_LOCALE_POLICY.items():
            policy = affiliate_policy.get(lang)
            if not isinstance(policy, dict):
                issues.append(f"{path}: affiliateLocalePolicy.{lang} should be an object")
                continue
            affiliate_policy_checked += 1
            for key, expected_value in expected.items():
                if policy.get(key) != expected_value:
                    issues.append(f"{path}: affiliateLocalePolicy.{lang}.{key} should be {expected_value}")
            if not isinstance(policy.get("rule"), str) or not policy["rule"]:
                issues.append(f"{path}: affiliateLocalePolicy.{lang}.rule should explain the locale rule")
    playbook = data.get("revenuePlaybook")
    revenue_playbook_checked = 0
    if not isinstance(playbook, list) or len(playbook) < 4:
        issues.append(f"{path}: revenuePlaybook should include at least four plays")
    else:
        revenue_playbook_checked = len(playbook)
        expected_play_ids = {"identity_retention_first", "owned_supply_lead", "affiliate_book_revenue", "luna_pack_revenue"}
        play_ids = {play.get("id") for play in playbook if isinstance(play, dict)}
        missing_play_ids = sorted(expected_play_ids.difference(play_ids))
        if missing_play_ids:
            issues.append(f"{path}: revenuePlaybook missing play ids {', '.join(missing_play_ids)}")
        for play in playbook:
            if not isinstance(play, dict) or not play.get("primaryEvents") or not play.get("doNotUseWhen"):
                issues.append(f"{path}: revenuePlaybook entries should include primaryEvents and doNotUseWhen")
                break
    items = data.get("items", [])
    if not isinstance(items, list):
        return [f"{path}: items should be a list"], 0, 0, 0, 0, 0, 0, 0, 0, affiliate_policy_checked, 0, 0, 0, 0, 0, 0, revenue_playbook_checked, 0
    if len(items) != 20:
        issues.append(f"{path}: expected 20 commerce items, got {len(items)}")
    type_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    ids: set[str] = set()
    free_keepsake_urls_checked = 0
    owned_supply_urls_checked = 0
    free_keepsake_guardians_checked = 0
    owned_supply_guardians_checked = 0
    owned_supply_contacts_checked = 0
    amazon_associate_tags_checked = 0
    affiliate_asins_checked = 0
    primary_affiliate_urls_checked = 0
    affiliate_localized_urls_checked = 0
    taiwan_affiliate_urls_checked = 0
    luna_gumroad_urls_checked = 0
    item_playbook_links_checked = 0
    playbook_by_type = {
        item_type: play
        for play in (playbook if isinstance(playbook, list) else [])
        if isinstance(play, dict)
        for item_type in play.get("itemTypes", [])
    }
    for item in items:
        if not isinstance(item, dict):
            issues.append(f"{path}: item should be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            issues.append(f"{path}: item missing id")
        elif item_id in ids:
            issues.append(f"{path}: duplicate item id {item_id}")
        else:
            ids.add(item_id)
        item_type = item.get("type")
        role = item.get("role")
        if isinstance(item_type, str):
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        if isinstance(role, str):
            role_counts[role] = role_counts.get(role, 0) + 1
        if item_type in {"free_keepsake", "owned_supply_waitlist"}:
            guardian = item.get("guardian")
            if guardian not in EXPECTED_GUARDIAN_LANGUAGES:
                issues.append(f"{path}: {item_id or '<unknown>'} should include a valid guardian slug")
            elif item_type == "free_keepsake":
                free_keepsake_guardians_checked += 1
            else:
                owned_supply_guardians_checked += 1
            if item_type == "owned_supply_waitlist":
                if item.get("contact") != "contact@lovetypes.tw":
                    issues.append(f"{path}: {item_id or '<unknown>'} contact should be contact@lovetypes.tw")
                else:
                    owned_supply_contacts_checked += 1
            item_url = item.get("url")
            parsed_item_url = urlparse(item_url) if isinstance(item_url, str) else urlparse("")
            if parsed_item_url.scheme != "https" or parsed_item_url.netloc != CANONICAL_HOST:
                issues.append(f"{path}: {item_id or '<unknown>'} should point to https://{CANONICAL_HOST}/")
            else:
                url_without_fragment, _fragment = urldefrag(item_url)
                try:
                    item_response = request_url(url_without_fragment)
                except RuntimeError as exc:
                    issues.append(f"{path}: {item_id or '<unknown>'} target request failed: {exc}")
                else:
                    if item_response.status != 200:
                        issues.append(f"{path}: {item_id or '<unknown>'} target should return 200, got {item_response.status}")
                    elif item_type == "free_keepsake":
                        free_keepsake_urls_checked += 1
                    else:
                        owned_supply_urls_checked += 1
        if item_type == "affiliate_book":
            primary_url = item.get("url")
            if not isinstance(primary_url, str) or not is_expected_commerce_affiliate_url("en", primary_url):
                issues.append(f"{path}: {item_id or '<unknown>'} primary url should use Amazon Associates tag={EXPECTED_AMAZON_ASSOCIATE_TAG}")
            else:
                primary_affiliate_urls_checked += 1
            if item.get("amazonAssociateTag") != EXPECTED_AMAZON_ASSOCIATE_TAG:
                issues.append(f"{path}: {item_id or '<unknown>'} should include amazonAssociateTag={EXPECTED_AMAZON_ASSOCIATE_TAG}")
            else:
                amazon_associate_tags_checked += 1
            if not isinstance(item.get("asin"), str) or not item["asin"]:
                issues.append(f"{path}: {item_id or '<unknown>'} should include asin")
            else:
                affiliate_asins_checked += 1
            localized_urls = item.get("localizedUrls")
            if not isinstance(localized_urls, dict):
                issues.append(f"{path}: {item_id or '<unknown>'} should include localizedUrls")
            else:
                for lang in EXPECTED_AFFILIATE_LOCALE_POLICY:
                    localized_url = localized_urls.get(lang)
                    if not isinstance(localized_url, str) or not localized_url:
                        issues.append(f"{path}: {item_id or '<unknown>'} localizedUrls.{lang} should be a URL")
                        continue
                    affiliate_localized_urls_checked += 1
                    if not is_expected_commerce_affiliate_url(lang, localized_url):
                        expected = "Books.com.tw affiliate URL" if lang == "zh" else f"Amazon Associates tag={EXPECTED_AMAZON_ASSOCIATE_TAG}"
                        issues.append(f"{path}: {item_id or '<unknown>'} localizedUrls.{lang} should use {expected}")
            taiwan_url = item.get("taiwanAffiliateUrl")
            if not isinstance(taiwan_url, str) or not is_expected_commerce_affiliate_url("zh", taiwan_url):
                issues.append(f"{path}: {item_id or '<unknown>'} should include taiwanAffiliateUrl using Books.com.tw")
            else:
                taiwan_affiliate_urls_checked += 1
        if item_type == "luna_gumroad_pack":
            product_url = item.get("url")
            parsed_product_url = urlparse(product_url) if isinstance(product_url, str) else urlparse("")
            if parsed_product_url.scheme != "https" or parsed_product_url.netloc != "lunayogamusic.gumroad.com":
                issues.append(f"{path}: {item_id or '<unknown>'} should use a Luna Gumroad URL")
            else:
                luna_gumroad_urls_checked += 1
        if not isinstance(item.get("conversion"), str) or not item["conversion"]:
            issues.append(f"{path}: {item_id or '<unknown>'} missing conversion")
        if not isinstance(item.get("disclosure"), str) or not item["disclosure"]:
            issues.append(f"{path}: {item_id or '<unknown>'} missing disclosure")
        play = playbook_by_type.get(item_type)
        if not play:
            issues.append(f"{path}: {item_id or '<unknown>'} missing matching revenue playbook")
        else:
            item_playbook_links_checked += 1
            if item.get("playbookId") != play.get("id"):
                issues.append(f"{path}: {item_id or '<unknown>'} playbookId should be {play.get('id')}")
            for key in ("recommendedAfter", "primaryEvents"):
                if not isinstance(item.get(key), list) or not item[key]:
                    issues.append(f"{path}: {item_id or '<unknown>'} missing {key}")
            for key in ("nextStep", "doNotUseWhen"):
                if not isinstance(item.get(key), str) or not item[key]:
                    issues.append(f"{path}: {item_id or '<unknown>'} missing {key}")
    for item_type, expected in EXPECTED_COMMERCE_TYPE_COUNTS.items():
        if type_counts.get(item_type) != expected:
            issues.append(f"{path}: expected {expected} {item_type} items, got {type_counts.get(item_type, 0)}")
    for role, expected in EXPECTED_COMMERCE_ROLE_COUNTS.items():
        if role_counts.get(role) != expected:
            issues.append(f"{path}: expected {expected} {role} items, got {role_counts.get(role, 0)}")
    return (
        issues,
        len(items),
        len(type_counts),
        len(role_counts),
        free_keepsake_urls_checked,
        owned_supply_urls_checked,
        free_keepsake_guardians_checked,
        owned_supply_guardians_checked,
        owned_supply_contacts_checked,
        affiliate_policy_checked,
        amazon_associate_tags_checked,
        affiliate_asins_checked,
        primary_affiliate_urls_checked,
        affiliate_localized_urls_checked,
        taiwan_affiliate_urls_checked,
        luna_gumroad_urls_checked,
        revenue_playbook_checked,
        item_playbook_links_checked,
    )


def check_site_index(base_url: str) -> tuple[list[str], int, int, int, int]:
    path = "/site-index.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("production") != "https://lovetypes.tw/":
        issues.append(f"{path}: production should be https://lovetypes.tw/")
    pages = data.get("pages", [])
    languages = data.get("languages", [])
    core_flows = data.get("coreFlows", [])
    if not isinstance(pages, list):
        return [f"{path}: pages should be a list"], 0, 0, 0, 0
    if len(pages) != 155:
        issues.append(f"{path}: expected 155 pages, got {len(pages)}")
    seen_langs = {item.get("id") for item in languages if isinstance(item, dict)}
    if seen_langs != EXPECTED_SITE_INDEX_LANGS:
        issues.append(f"{path}: language ids should be {sorted(EXPECTED_SITE_INDEX_LANGS)}, got {sorted(seen_langs)}")
    flow_ids = {item.get("id") for item in core_flows if isinstance(item, dict)}
    if flow_ids != EXPECTED_SITE_INDEX_FLOWS:
        issues.append(f"{path}: core flow ids should be {sorted(EXPECTED_SITE_INDEX_FLOWS)}, got {sorted(flow_ids)}")
    groups = {page.get("group") for page in pages if isinstance(page, dict) and page.get("group")}
    canonicals = {page.get("canonical") for page in pages if isinstance(page, dict) and page.get("canonical")}
    for required_url in (
        "https://lovetypes.tw/",
        "https://lovetypes.tw/start/",
        "https://lovetypes.tw/characters/iris/",
        "https://lovetypes.tw/en/resources/",
        "https://lovetypes.tw/ja/luna-yoga-music/",
        "https://lovetypes.tw/es/contact/",
    ):
        if required_url not in canonicals:
            issues.append(f"{path}: missing canonical {required_url}")
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("pages") != len(pages):
        issues.append(f"{path}: totals.pages should match page count")
    return issues, len(pages), len(seen_langs), len(groups), len(flow_ids)


def check_guardian_profiles(base_url: str) -> tuple[list[str], int, int, int, int]:
    path = "/guardian-profiles.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    guardians = data.get("guardians", [])
    if not isinstance(guardians, list):
        return [f"{path}: guardians should be a list"], 0, 0, 0, 0
    if len(guardians) != 5:
        issues.append(f"{path}: expected five guardians, got {len(guardians)}")
    route_count = 0
    asset_count = 0
    guide_count = 0
    seen: set[str] = set()
    for guardian in guardians:
        if not isinstance(guardian, dict):
            issues.append(f"{path}: guardian should be an object")
            continue
        slug = guardian.get("slug")
        if slug not in EXPECTED_GUARDIAN_LANGUAGES:
            issues.append(f"{path}: unexpected guardian slug {slug!r}")
            continue
        seen.add(slug)
        if guardian.get("loveLanguage", {}).get("en") != EXPECTED_GUARDIAN_LANGUAGES[slug]:
            issues.append(f"{path}: {slug} love language mapping is incorrect")
        routes = guardian.get("routes", {})
        assets = guardian.get("assets", {})
        guides = guardian.get("guides", [])
        route_count += len(routes) if isinstance(routes, dict) else 0
        asset_count += len(assets) if isinstance(assets, dict) else 0
        guide_count += len(guides) if isinstance(guides, list) else 0
        for key in ("profile", "supply", "keepsake", "freeKeepsake", "repairPlan", "luna", "contact"):
            value = routes.get(key) if isinstance(routes, dict) else ""
            if not isinstance(value, str) or not value.startswith("https://lovetypes.tw/"):
                issues.append(f"{path}: {slug} route {key} should point to lovetypes.tw")
        for key in ("portrait", "card", "prop", "story"):
            value = assets.get(key) if isinstance(assets, dict) else ""
            if not isinstance(value, str) or not value.startswith("/assets/lovetypes/"):
                issues.append(f"{path}: {slug} asset {key} should point to /assets/lovetypes/")
        if not isinstance(guides, list) or not guides:
            issues.append(f"{path}: {slug} should include guide URLs")
    missing = sorted(set(EXPECTED_GUARDIAN_LANGUAGES).difference(seen))
    if missing:
        issues.append(f"{path}: missing guardians {', '.join(missing)}")
    return issues, len(guardians), route_count, asset_count, guide_count


def check_promotion_profile_verification(source_path: str, data: dict) -> tuple[list[str], int, int, int]:
    issues: list[str] = []
    verification = data.get("promotionProfileVerification")
    if not isinstance(verification, dict):
        return [f"{source_path}: promotionProfileVerification should be an object"], 0, 0, 0
    expected_counters = {
        "public_promotion_kit_platform_profile_writeback_checked=3",
        "public_promotion_kit_platform_profile_verification_steps_checked=12",
        "public_promotion_kit_platform_profile_publish_gates_checked=9",
        "public_promotion_kit_issues=0",
        "public_discovery_commerce_revenue_playbook_checked=4",
        "public_discovery_commerce_item_playbook_links_checked=20",
    }
    if verification.get("source") != "https://lovetypes.tw/promotion-kit.json#platformProfileSetup":
        issues.append(f"{source_path}: promotionProfileVerification.source should point to promotion kit platformProfileSetup")
    if verification.get("platforms") != 3:
        issues.append(f"{source_path}: promotionProfileVerification.platforms should be 3")
    writeback_fields = verification.get("writebackFields")
    expected_fields = {"status", "profile_link_set_date", "profile_link", "notes"}
    if not isinstance(writeback_fields, list) or set(writeback_fields) != expected_fields:
        issues.append(f"{source_path}: promotionProfileVerification.writebackFields should contain {sorted(expected_fields)}")
    if verification.get("verificationStepsPerPlatform") != 4:
        issues.append(f"{source_path}: promotionProfileVerification.verificationStepsPerPlatform should be 4")
    if verification.get("doNotPublishGatesPerPlatform") != 3:
        issues.append(f"{source_path}: promotionProfileVerification.doNotPublishGatesPerPlatform should be 3")
    counters = verification.get("publicSmokeCounters")
    if not isinstance(counters, list) or not expected_counters.issubset(set(counters)):
        issues.append(f"{source_path}: promotionProfileVerification.publicSmokeCounters missing required counters")
    checked_by = verification.get("checkedBy")
    expected_tools = {"tools/site_quality_audit.py", "tools/public_promotion_kit_smoke.py", "tools/public_discovery_smoke.py"}
    if not isinstance(checked_by, list) or not expected_tools.issubset(set(checked_by)):
        issues.append(f"{source_path}: promotionProfileVerification.checkedBy missing required tools")
    return (
        issues,
        len(writeback_fields) if isinstance(writeback_fields, list) else 0,
        len(counters) if isinstance(counters, list) else 0,
        len(checked_by) if isinstance(checked_by, list) else 0,
    )


def check_site_health(base_url: str) -> tuple[list[str], int, int, int, int, int, int]:
    path = "/site-health.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0, 0, 0
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("status") != "ready_for_predeploy":
        issues.append(f"{path}: status should be ready_for_predeploy")
    coverage = data.get("coverage", {})
    expected = {
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
        "supportFiles": EXPECTED_SUPPORT_FILE_COUNT,
    }
    coverage_checked = 0
    for key, value in expected.items():
        coverage_checked += 1
        if coverage.get(key) != value:
            issues.append(f"{path}: coverage.{key} should be {value}, got {coverage.get(key)!r}")
    if not isinstance(coverage.get("funnelEvents"), int) or coverage["funnelEvents"] < 50:
        issues.append(f"{path}: coverage.funnelEvents should be at least 50")
    else:
        coverage_checked += 1
    support_files = data.get("supportFiles", [])
    gates = data.get("requiredGates", {})
    if not isinstance(support_files, list) or len(support_files) != EXPECTED_SUPPORT_FILE_COUNT:
        issues.append(f"{path}: expected {EXPECTED_SUPPORT_FILE_COUNT} support files")
    elif set(support_files) != EXPECTED_SUPPORT_FILES:
        missing = sorted(EXPECTED_SUPPORT_FILES.difference(support_files))
        extra = sorted(set(support_files).difference(EXPECTED_SUPPORT_FILES))
        issues.append(f"{path}: supportFiles mismatch missing={missing} extra={extra}")
    expected_gates = {"localPredeploy", "localizedAffiliateLinks", "promotionWritebackFlow", "publicDiscovery", "publicDeploy", "versionedAssets"}
    if not isinstance(gates, dict) or set(gates) != expected_gates:
        issues.append(f"{path}: requiredGates should list six gate names")
    else:
        gate_text = " ".join(str(value) for value in gates.values())
        for snippet in ("affiliate_locale_issues=0", "promotion_writeback_issues=0", "promotion_writeback_stale_phrase_hits=0"):
            if snippet not in gate_text:
                issues.append(f"{path}: requiredGates missing snippet {snippet!r}")
    local_audits = data.get("localAuditCoverage", {})
    if not isinstance(local_audits, dict) or set(local_audits) != {"structure", "conversion", "promotion", "experience"}:
        issues.append(f"{path}: localAuditCoverage should list four audit groups")
    else:
        audit_text = json.dumps(local_audits, ensure_ascii=False)
        for snippet in ("affiliate_locale", "promotion_writeback_flow", "platform_kpi_tracker", "performance_budget"):
            if snippet not in audit_text:
                issues.append(f"{path}: localAuditCoverage missing snippet {snippet!r}")
    indexes = data.get("primaryIndexes", {})
    if not isinstance(indexes, dict) or len(indexes) < 10:
        issues.append(f"{path}: primaryIndexes should list at least ten entries")
    profile_issues, _writeback_fields, profile_smoke_counters, _checked_by = check_promotion_profile_verification(path, data)
    issues.extend(profile_issues)
    return issues, coverage_checked, len(support_files) if isinstance(support_files, list) else 0, len(gates) if isinstance(gates, dict) else 0, len(local_audits) if isinstance(local_audits, dict) else 0, len(indexes) if isinstance(indexes, dict) else 0, profile_smoke_counters


def check_release_info(base_url: str) -> tuple[list[str], int, int, int, int, int, int]:
    path = "/release.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0, 0, 0
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("deploymentTarget") != "Cloudflare Pages project lovetypes":
        issues.append(f"{path}: deploymentTarget should name Cloudflare Pages project lovetypes")
    if data.get("branch") != "main":
        issues.append(f"{path}: branch should be main")
    contents = data.get("releaseContents", {})
    expected_contents = {"indexablePages": 155, "languages": 5, "guardians": 5, "commerceItems": 20, "coreFlows": 5}
    content_checked = 0
    for key, expected in expected_contents.items():
        content_checked += 1
        if contents.get(key) != expected:
            issues.append(f"{path}: releaseContents.{key} should be {expected}, got {contents.get(key)!r}")
    if not isinstance(contents.get("funnelEvents"), int) or contents["funnelEvents"] < 50:
        issues.append(f"{path}: releaseContents.funnelEvents should be at least 50")
    else:
        content_checked += 1
    indexes = data.get("publicIndexes", {})
    commands = data.get("verificationCommands", [])
    outcomes = data.get("requiredOutcomes", [])
    local_audits = data.get("localAuditCoverage", {})
    expected_indexes = {
        "aiDiscovery",
        "siteHealth",
        "siteIndex",
        "guardianProfiles",
        "safetyIndex",
        "commerceCatalog",
        "funnelEvents",
        "promotionKit",
        "llms",
        "humans",
    }
    if not isinstance(indexes, dict) or set(indexes) != expected_indexes:
        issues.append(f"{path}: publicIndexes should contain {sorted(expected_indexes)}")
    else:
        for key, url in indexes.items():
            if not isinstance(url, str) or not url.startswith(f"https://{CANONICAL_HOST}"):
                issues.append(f"{path}: public index {key} should point to https://{CANONICAL_HOST}")
    expected_commands = [
        "python3 tools/predeploy_check.py",
        "python3 tools/deploy_cloudflare_pages.py",
        "python3 tools/public_discovery_smoke.py",
        "python3 tools/public_deploy_smoke.py",
        "python3 tools/public_versioned_asset_smoke.py",
    ]
    if commands != expected_commands:
        issues.append(f"{path}: verificationCommands should match the release workflow")
    expected_outcomes = {
        "predeploy_checks=ok",
        "issues=0",
        "public_discovery_issues=0",
        "public_deploy_issues=0",
        "public_versioned_asset_issues=0",
        "public_versioned_asset_stale_refs=0",
    }
    if not isinstance(outcomes, list) or set(outcomes) != expected_outcomes:
        issues.append(f"{path}: requiredOutcomes should contain {sorted(expected_outcomes)}")
    if not isinstance(local_audits, dict) or set(local_audits) != {"contentStructure", "conversionAndCommerce", "promotionOperations", "experienceQuality"}:
        issues.append(f"{path}: localAuditCoverage should list four audit groups")
    else:
        audit_text = json.dumps(local_audits, ensure_ascii=False)
        for snippet in ("tools/affiliate_locale_audit.py", "tools/promotion_writeback_flow_audit.py", "tools/promotion_platform_kpi_tracker.py", "tools/performance_budget_audit.py"):
            if snippet not in audit_text:
                issues.append(f"{path}: localAuditCoverage missing snippet {snippet!r}")
    profile_issues, _writeback_fields, profile_smoke_counters, _checked_by = check_promotion_profile_verification(path, data)
    issues.extend(profile_issues)
    return issues, content_checked, len(indexes) if isinstance(indexes, dict) else 0, len(commands) if isinstance(commands, list) else 0, len(local_audits) if isinstance(local_audits, dict) else 0, len(outcomes) if isinstance(outcomes, list) else 0, profile_smoke_counters


def check_safety_index(base_url: str) -> tuple[list[str], int, int, int, int, int, int]:
    path = "/safety-index.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0, 0, 0
    expected_ids = {"reflection_not_diagnosis", "urgent_risk_first", "do_not_buy_to_fix", "email_minimum_context", "external_store_boundary"}
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("contact") != "contact@lovetypes.tw":
        issues.append(f"{path}: contact should be contact@lovetypes.tw")
    not_for = set(data.get("notFor", [])) if isinstance(data.get("notFor"), list) else set()
    for snippet in ("emergency support", "therapy", "medical advice", "legal advice", "coercive purchase pressure"):
        if snippet not in not_for:
            issues.append(f"{path}: notFor missing {snippet!r}")
    steps = data.get("saferFirstSteps", [])
    boundaries = data.get("boundaries", [])
    if not isinstance(steps, list) or len(steps) != 4:
        issues.append(f"{path}: expected four saferFirstSteps")
    first_step_urls_checked = 0
    response_cache: dict[str, Response] = {}
    for step in steps if isinstance(steps, list) else []:
        if not isinstance(step, dict):
            issues.append(f"{path}: saferFirstSteps entries should be objects")
            continue
        step_id = step.get("id") or "<unknown>"
        url = step.get("url")
        if not isinstance(url, str) or not url.startswith(base_url.rstrip("/") + "/"):
            issues.append(f"{path}: saferFirstStep {step_id} url should point to {base_url}: {url!r}")
            continue
        route_url_without_fragment, fragment = urldefrag(url)
        if route_url_without_fragment not in response_cache:
            response_cache[route_url_without_fragment] = request_url(route_url_without_fragment)
        target_response = response_cache[route_url_without_fragment]
        if target_response.status != 200:
            issues.append(f"{path}: saferFirstStep {step_id} target should return 200, got {target_response.status}: {url}")
            continue
        if fragment and fragment not in target_response.text:
            issues.append(f"{path}: saferFirstStep {step_id} target missing anchor #{fragment}: {url}")
            continue
        first_step_urls_checked += 1
    if not isinstance(boundaries, list) or len(boundaries) != 5:
        issues.append(f"{path}: expected five boundaries")
        return issues, len(boundaries) if isinstance(boundaries, list) else 0, 0, 0, len(not_for), len(steps) if isinstance(steps, list) else 0, first_step_urls_checked
    route_count = 0
    route_targets_checked = 0
    seen_ids = set()
    for boundary in boundaries:
        if not isinstance(boundary, dict):
            issues.append(f"{path}: boundary should be an object")
            continue
        boundary_id = boundary.get("id")
        seen_ids.add(boundary_id)
        routes = boundary.get("routes", [])
        route_count += len(routes) if isinstance(routes, list) else 0
        if not isinstance(routes, list) or not routes:
            issues.append(f"{path}: {boundary_id} should include routes")
            continue
        for url in routes:
            if not isinstance(url, str) or not url.startswith(base_url.rstrip("/") + "/"):
                issues.append(f"{path}: {boundary_id} route should point to {base_url}: {url!r}")
                continue
            route_url_without_fragment, fragment = urldefrag(url)
            if route_url_without_fragment not in response_cache:
                response_cache[route_url_without_fragment] = request_url(route_url_without_fragment)
            target_response = response_cache[route_url_without_fragment]
            if target_response.status != 200:
                issues.append(f"{path}: {boundary_id} route target should return 200, got {target_response.status}: {url}")
                continue
            if fragment and fragment not in target_response.text:
                issues.append(f"{path}: {boundary_id} route target missing anchor #{fragment}: {url}")
                continue
            route_targets_checked += 1
        for key in ("title", "body"):
            value = boundary.get(key)
            if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                issues.append(f"{path}: {boundary_id} should include zh/en {key}")
    missing = sorted(expected_ids.difference(seen_ids))
    if missing:
        issues.append(f"{path}: missing boundary ids {', '.join(missing)}")
    totals = data.get("totals", {})
    if not isinstance(totals, dict) or totals.get("boundaries") != len(boundaries) or totals.get("routes") != route_count:
        issues.append(f"{path}: totals should match boundary and route counts")
    return issues, len(boundaries), route_count, route_targets_checked, len(not_for), len(steps) if isinstance(steps, list) else 0, first_step_urls_checked


def check_ai_discovery(base_url: str) -> tuple[list[str], int, int, int, int, int, int, int, int]:
    path = "/ai-discovery.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0, 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0, 0, 0, 0, 0
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("siteName") != "LoveTypes":
        issues.append(f"{path}: siteName should be LoveTypes")
    if data.get("preferredLanguage") != "zh-TW":
        issues.append(f"{path}: preferredLanguage should be zh-TW")
    guidance = data.get("answerGuidance", {})
    if not isinstance(guidance, dict) or guidance.get("doNotUseAsDiagnosis") is not True:
        issues.append(f"{path}: answerGuidance.doNotUseAsDiagnosis should be true")
    for key in ("commercialDisclosure", "safetyBoundary"):
        if not isinstance(guidance.get(key), str) or not guidance[key]:
            issues.append(f"{path}: answerGuidance.{key} should be non-empty")
    totals = data.get("totals", {})
    expected_totals = {"guardians": 5, "answerableQuestions": 11, "priorityUrls": 12, "languages": 5, "discoveryFiles": 10}
    for key, expected in expected_totals.items():
        if not isinstance(totals, dict) or totals.get(key) != expected:
            got = totals.get(key) if isinstance(totals, dict) else None
            issues.append(f"{path}: totals.{key} should be {expected}, got {got!r}")
    expected_languages = {
        "zh": {"hreflang": "zh-TW", "prefix": "/", "name": "繁體中文"},
        "en": {"hreflang": "en", "prefix": "en", "name": "English"},
        "ja": {"hreflang": "ja", "prefix": "ja", "name": "日本語"},
        "ko": {"hreflang": "ko", "prefix": "ko", "name": "한국어"},
        "es": {"hreflang": "es", "prefix": "es", "name": "Español"},
    }
    languages = data.get("availableLanguages")
    languages_checked = 0
    if not isinstance(languages, list) or len(languages) != len(expected_languages):
        issues.append(f"{path}: availableLanguages should include five locales")
    else:
        seen_langs: set[str] = set()
        for language in languages:
            if not isinstance(language, dict):
                issues.append(f"{path}: availableLanguages entries should be objects")
                continue
            lang_id = language.get("id")
            seen_langs.add(lang_id)
            expected = expected_languages.get(lang_id)
            if expected is None:
                issues.append(f"{path}: unexpected availableLanguages id {lang_id!r}")
                continue
            languages_checked += 1
            for key, expected_value in expected.items():
                if language.get(key) != expected_value:
                    issues.append(f"{path}: availableLanguages.{lang_id}.{key} should be {expected_value!r}")
        missing_langs = sorted(set(expected_languages).difference(seen_langs))
        if missing_langs:
            issues.append(f"{path}: availableLanguages missing {', '.join(missing_langs)}")
    guardians = data.get("canonicalEntities", {}).get("guardians", []) if isinstance(data.get("canonicalEntities"), dict) else []
    expected_guardians = {
        "iris": "Words of affirmation",
        "noah": "Quality time",
        "vivian": "Receiving gifts",
        "claire": "Acts of service",
        "dora": "Physical touch",
    }
    seen = set()
    for guardian in guardians if isinstance(guardians, list) else []:
        if not isinstance(guardian, dict):
            issues.append(f"{path}: guardian should be an object")
            continue
        slug = guardian.get("slug")
        seen.add(slug)
        love_language = guardian.get("loveLanguage", {}).get("en") if isinstance(guardian.get("loveLanguage"), dict) else None
        if expected_guardians.get(slug) != love_language:
            issues.append(f"{path}: {slug} should map to {expected_guardians.get(slug)!r}, got {love_language!r}")
    missing = sorted(set(expected_guardians).difference(seen))
    if missing:
        issues.append(f"{path}: missing guardians {', '.join(missing)}")
    canonical_base_url = base_url.rstrip("/")
    expected_core_concepts = {
        "heart_garden": f"{canonical_base_url}/about/",
        "guardian_recognition_ritual": f"{canonical_base_url}/start/",
        "five_love_languages": f"{canonical_base_url}/theory/",
        "misfrequency_repair": f"{canonical_base_url}/repair-plan/",
        "traveler_supplies": f"{canonical_base_url}/resources/",
        "luna_night_support": f"{canonical_base_url}/luna-yoga-music/",
    }
    core_concepts = data.get("canonicalEntities", {}).get("coreConcepts", []) if isinstance(data.get("canonicalEntities"), dict) else []
    core_concepts_checked = 0
    if not isinstance(core_concepts, list) or len(core_concepts) != len(expected_core_concepts):
        issues.append(f"{path}: canonicalEntities.coreConcepts should include six concepts")
    else:
        seen_concepts: set[str] = set()
        for concept in core_concepts:
            if not isinstance(concept, dict):
                issues.append(f"{path}: core concept should be an object")
                continue
            concept_id = concept.get("id")
            seen_concepts.add(concept_id)
            expected_canonical = expected_core_concepts.get(concept_id)
            if expected_canonical is None:
                issues.append(f"{path}: unexpected core concept id {concept_id!r}")
                continue
            core_concepts_checked += 1
            label = concept.get("label")
            if not isinstance(label, dict) or not label.get("zh") or not label.get("en"):
                issues.append(f"{path}: core concept {concept_id} should include zh/en label")
            if concept.get("canonical") != expected_canonical:
                issues.append(f"{path}: core concept {concept_id} canonical should be {expected_canonical}")
        missing_concepts = sorted(set(expected_core_concepts).difference(seen_concepts))
        if missing_concepts:
            issues.append(f"{path}: missing core concepts {', '.join(missing_concepts)}")
    questions = data.get("answerableQuestions", [])
    if not isinstance(questions, list) or len(questions) != 11:
        issues.append(f"{path}: answerableQuestions should include eleven entries")
    else:
        for snippet in ("LoveTypes 是什麼？", "LoveTypes 能取代諮商、醫療或緊急求助嗎？", "LoveTypes 是否包含聯盟連結或購買入口？"):
            if not any(isinstance(item, dict) and item.get("question") == snippet for item in questions):
                issues.append(f"{path}: answerableQuestions missing {snippet!r}")
    priority_urls = data.get("priorityUrls", [])
    if not isinstance(priority_urls, list) or len(priority_urls) != 12:
        issues.append(f"{path}: priorityUrls should include twelve entries")
    files = data.get("discoveryFiles", {})
    expected_files = {"aiDiscovery", "llms", "siteIndex", "guardianProfiles", "commerceCatalog", "safetyIndex", "promotionKit", "release", "siteHealth", "humans"}
    if not isinstance(files, dict) or set(files) != expected_files:
        issues.append(f"{path}: discoveryFiles should contain {sorted(expected_files)}")
    profile_issues, _writeback_fields, profile_smoke_counters, _checked_by = check_promotion_profile_verification(path, data)
    issues.extend(profile_issues)
    return (
        issues,
        len(guardians) if isinstance(guardians, list) else 0,
        languages_checked,
        core_concepts_checked,
        len(questions) if isinstance(questions, list) else 0,
        len(priority_urls) if isinstance(priority_urls, list) else 0,
        len(files) if isinstance(files, dict) else 0,
        len(guidance) if isinstance(guidance, dict) else 0,
        profile_smoke_counters,
    )


def public_sitemap_urls(base_url: str) -> tuple[list[str], set[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    if response.status != 200:
        return [f"/sitemap.xml: expected status 200, got {response.status}"], set()
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as exc:
        return [f"/sitemap.xml: invalid XML for discovery cross-index: {exc}"], set()
    urls = {
        node.text.strip()
        for node in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if node.text and node.text.strip()
    }
    return [], urls


def validate_public_index_url(
    source_path: str,
    field_path: str,
    value: str,
    base_url: str,
    sitemap_urls: set[str],
    response_cache: dict[str, Response],
) -> tuple[list[str], int, int, int]:
    issues: list[str] = []
    urls_checked = 1
    targets_checked = 0
    fragments_checked = 0
    is_relative_route = value.startswith("/")
    url = urljoin(base_url + "/", value.lstrip("/")) if is_relative_route else value
    parsed = urlparse(url)
    if not is_relative_route and (parsed.scheme != "https" or parsed.netloc != CANONICAL_HOST):
        return [f"{source_path}: {field_path} should point to https://lovetypes.tw or a site-relative path: {value}"], urls_checked, 0, 0
    check_url = route_url(url, base_url)
    canonical_url = canonical_route_for_url(url, base_url)
    path = urlparse(check_url).path
    looks_like_html_route = path.endswith("/") or "." not in path.rsplit("/", 1)[-1]
    if looks_like_html_route and not parsed.fragment:
        if canonical_url not in sitemap_urls:
            issues.append(f"{source_path}: {field_path} HTML route missing from sitemap: {canonical_url}")
        else:
            targets_checked += 1
        return issues, urls_checked, targets_checked, fragments_checked

    if not parsed.fragment:
        targets_checked += 1
        return issues, urls_checked, targets_checked, fragments_checked

    if check_url not in response_cache:
        response_cache[check_url] = request_url(check_url)
    response = response_cache[check_url]
    if response.status != 200:
        return [f"{source_path}: {field_path} target {check_url} expected status 200, got {response.status}"], urls_checked, 0, 0
    targets_checked += 1
    content_type = response.headers.get("content-type", "")
    if "html" not in content_type:
        return issues, urls_checked, targets_checked, fragments_checked
    head = HeadParser()
    head.feed(response.text)
    if "noindex" in head.robots.lower():
        issues.append(f"{source_path}: {field_path} should not point to noindex HTML: {value}")
    if parsed.fragment:
        fragments_checked += 1
        if parsed.fragment not in head.ids:
            issues.append(f"{source_path}: {field_path} fragment missing #{parsed.fragment}: {value}")
        if canonical_url not in sitemap_urls:
            issues.append(f"{source_path}: {field_path} fragment base missing from sitemap: {canonical_url}")
        return issues, urls_checked, targets_checked, fragments_checked
    if canonical_url not in sitemap_urls:
        issues.append(f"{source_path}: {field_path} HTML route missing from sitemap: {canonical_url}")
    if head.canonical and head.canonical != canonical_url:
        issues.append(f"{source_path}: {field_path} target canonical mismatch: {value} -> {head.canonical}")
    return issues, urls_checked, targets_checked, fragments_checked


def check_discovery_cross_index(base_url: str) -> tuple[list[str], int, int, int, int, int]:
    issues, sitemap_urls = public_sitemap_urls(base_url)
    response_cache: dict[str, Response] = {}
    index_paths = (
        "/ai-discovery.json",
        "/funnel-events.json",
        "/site-index.json",
        "/guardian-profiles.json",
        "/commerce-catalog.json",
        "/safety-index.json",
        "/promotion-kit.json",
        "/site-health.json",
        "/release.json",
    )
    indexes_checked = 0
    urls_checked = 0
    targets_checked = 0
    fragments_checked = 0
    for index_path in index_paths:
        response = request_url(urljoin(base_url + "/", index_path.lstrip("/")))
        if response.status != 200:
            issues.append(f"{index_path}: expected status 200, got {response.status}")
            continue
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            issues.append(f"{index_path}: invalid JSON for discovery cross-index: {exc}")
            continue
        indexes_checked += 1
        seen_values: set[str] = set()
        for field_path, value in walk_index_urls(data):
            if value in seen_values:
                continue
            seen_values.add(value)
            value_issues, checked, targets, fragments = validate_public_index_url(
                index_path,
                field_path,
                value,
                base_url,
                sitemap_urls,
                response_cache,
            )
            issues.extend(value_issues)
            urls_checked += checked
            targets_checked += targets
            fragments_checked += fragments

    core_routes = {
        f"{DEFAULT_BASE_URL}/",
        f"{DEFAULT_BASE_URL}/start/",
        f"{DEFAULT_BASE_URL}/garden-map/",
        f"{DEFAULT_BASE_URL}/characters/",
        f"{DEFAULT_BASE_URL}/resources/",
        f"{DEFAULT_BASE_URL}/repair-plan/",
        f"{DEFAULT_BASE_URL}/keepsakes/",
        f"{DEFAULT_BASE_URL}/luna-yoga-music/",
        f"{DEFAULT_BASE_URL}/contact/",
    }
    core_routes_checked = 0
    for route in sorted(core_routes):
        core_routes_checked += 1
        if route not in sitemap_urls:
            issues.append(f"/sitemap.xml: missing core discovery route {route}")
    return issues, indexes_checked, urls_checked, targets_checked, fragments_checked, core_routes_checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public feed, manifest, llms, security, and ads discovery files.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Production or preview base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    issues: list[str] = []
    feed_issues, feed_items, feed_links_checked, feed_item_metadata_checked, feed_site_index_links_checked = check_feed(base_url)
    (
        manifest_issues,
        manifest_icons_checked,
        manifest_icon_dimensions_checked,
        manifest_shortcuts,
        manifest_shortcut_links_checked,
        manifest_expected_shortcuts_checked,
        manifest_shortcut_icons_checked,
        manifest_shortcut_icon_dimensions_checked,
        manifest_screenshots_checked,
        manifest_screenshot_dimensions_checked,
    ) = check_manifest(base_url)
    (
        llms_issues,
        llms_sections_checked,
        llms_snippets_checked,
        llms_urls_checked,
        llms_high_value_urls_checked,
        llms_url_canonicals_checked,
    ) = check_llms(base_url)
    (
        text_issues,
        text_files_checked,
        security_fields_checked,
        security_date_fields_checked,
        humans_snippets_checked,
        humans_urls_checked,
        humans_site_index_urls_checked,
    ) = check_text_files(base_url)
    robots_issues, robots_lines_checked, robots_sitemap_links_checked, robots_sitemap_core_urls_checked = check_robots(base_url)
    (
        funnel_issues,
        funnel_events_checked,
        funnel_categories_checked,
        funnel_roles_checked,
        runtime_pack_events_checked,
    ) = check_funnel_events(base_url)
    (
        promotion_event_issues,
        promotion_event_kpi_rows_checked,
        promotion_event_kpi_events_checked,
        promotion_revenue_bridge_kpis_checked,
        promotion_derived_rates_checked,
        promotion_decision_rules_checked,
        promotion_event_safety_fields_checked,
    ) = check_promotion_event_kpi_alignment(base_url)
    (
        commerce_issues,
        commerce_items_checked,
        commerce_types_checked,
        commerce_roles_checked,
        commerce_free_keepsake_urls_checked,
        commerce_owned_supply_urls_checked,
        commerce_free_keepsake_guardians_checked,
        commerce_owned_supply_guardians_checked,
        commerce_owned_supply_contacts_checked,
        commerce_affiliate_locale_policies_checked,
        commerce_amazon_associate_tags_checked,
        commerce_affiliate_asins_checked,
        commerce_primary_affiliate_urls_checked,
        commerce_affiliate_localized_urls_checked,
        commerce_taiwan_affiliate_urls_checked,
        commerce_luna_gumroad_urls_checked,
        commerce_revenue_playbook_checked,
        commerce_item_playbook_links_checked,
    ) = check_commerce_catalog(base_url)
    site_index_issues, site_index_pages_checked, site_index_languages_checked, site_index_groups_checked, site_index_flows_checked = check_site_index(base_url)
    guardian_profile_issues, guardian_profiles_checked, guardian_profile_routes_checked, guardian_profile_assets_checked, guardian_profile_guides_checked = check_guardian_profiles(base_url)
    site_health_issues, site_health_coverage_checked, site_health_support_files_checked, site_health_gates_checked, site_health_local_audit_groups_checked, site_health_indexes_checked, site_health_profile_smoke_counters_checked = check_site_health(base_url)
    release_issues, release_content_checked, release_indexes_checked, release_commands_checked, release_local_audit_groups_checked, release_outcomes_checked, release_profile_smoke_counters_checked = check_release_info(base_url)
    (
        safety_index_issues,
        safety_index_boundaries_checked,
        safety_index_routes_checked,
        safety_index_route_targets_checked,
        safety_index_not_for_checked,
        safety_index_steps_checked,
        safety_index_first_step_urls_checked,
    ) = check_safety_index(base_url)
    (
        ai_discovery_issues,
        ai_discovery_guardians_checked,
        ai_discovery_languages_checked,
        ai_discovery_core_concepts_checked,
        ai_discovery_questions_checked,
        ai_discovery_priority_urls_checked,
        ai_discovery_discovery_files_checked,
        ai_discovery_guidance_fields_checked,
        ai_discovery_profile_smoke_counters_checked,
    ) = check_ai_discovery(base_url)
    discovery_cross_issues, discovery_cross_indexes_checked, discovery_cross_urls_checked, discovery_cross_targets_checked, discovery_cross_fragments_checked, discovery_cross_core_routes_checked = check_discovery_cross_index(base_url)
    issues.extend(feed_issues)
    issues.extend(manifest_issues)
    issues.extend(llms_issues)
    issues.extend(text_issues)
    issues.extend(robots_issues)
    issues.extend(funnel_issues)
    issues.extend(promotion_event_issues)
    issues.extend(commerce_issues)
    issues.extend(site_index_issues)
    issues.extend(guardian_profile_issues)
    issues.extend(site_health_issues)
    issues.extend(release_issues)
    issues.extend(safety_index_issues)
    issues.extend(ai_discovery_issues)
    issues.extend(discovery_cross_issues)

    print(f"public_discovery_feed_items={feed_items}")
    print(f"public_discovery_feed_links_checked={feed_links_checked}")
    print(f"public_discovery_feed_item_metadata_checked={feed_item_metadata_checked}")
    print(f"public_discovery_feed_site_index_links_checked={feed_site_index_links_checked}")
    print(f"public_discovery_manifest_icons_checked={manifest_icons_checked}")
    print(f"public_discovery_manifest_icon_dimensions_checked={manifest_icon_dimensions_checked}")
    print(f"public_discovery_manifest_shortcuts={manifest_shortcuts}")
    print(f"public_discovery_manifest_shortcut_links_checked={manifest_shortcut_links_checked}")
    print(f"public_discovery_manifest_expected_shortcuts_checked={manifest_expected_shortcuts_checked}")
    print(f"public_discovery_manifest_shortcut_icons_checked={manifest_shortcut_icons_checked}")
    print(f"public_discovery_manifest_shortcut_icon_dimensions_checked={manifest_shortcut_icon_dimensions_checked}")
    print(f"public_discovery_manifest_screenshots_checked={manifest_screenshots_checked}")
    print(f"public_discovery_manifest_screenshot_dimensions_checked={manifest_screenshot_dimensions_checked}")
    print(f"public_discovery_llms_sections_checked={llms_sections_checked}")
    print(f"public_discovery_llms_snippets_checked={llms_snippets_checked}")
    print(f"public_discovery_llms_high_value_urls_checked={llms_high_value_urls_checked}")
    print(f"public_discovery_llms_urls_checked={llms_urls_checked}")
    print(f"public_discovery_llms_url_canonicals_checked={llms_url_canonicals_checked}")
    print(f"public_discovery_text_files_checked={text_files_checked}")
    print(f"public_discovery_security_fields_checked={security_fields_checked}")
    print(f"public_discovery_security_date_fields_checked={security_date_fields_checked}")
    print(f"public_discovery_humans_snippets_checked={humans_snippets_checked}")
    print(f"public_discovery_humans_urls_checked={humans_urls_checked}")
    print(f"public_discovery_humans_site_index_urls_checked={humans_site_index_urls_checked}")
    print(f"public_discovery_robots_lines_checked={robots_lines_checked}")
    print(f"public_discovery_robots_sitemap_links_checked={robots_sitemap_links_checked}")
    print(f"public_discovery_robots_sitemap_core_urls_checked={robots_sitemap_core_urls_checked}")
    print(f"public_discovery_funnel_events_checked={funnel_events_checked}")
    print(f"public_discovery_funnel_event_categories_checked={funnel_categories_checked}")
    print(f"public_discovery_funnel_event_roles_checked={funnel_roles_checked}")
    print(f"public_discovery_runtime_pack_events_checked={runtime_pack_events_checked}")
    print(f"public_discovery_promotion_event_kpi_rows_checked={promotion_event_kpi_rows_checked}")
    print(f"public_discovery_promotion_event_kpi_events_checked={promotion_event_kpi_events_checked}")
    print(f"public_discovery_promotion_revenue_bridge_kpis_checked={promotion_revenue_bridge_kpis_checked}")
    print(f"public_discovery_promotion_derived_rates_checked={promotion_derived_rates_checked}")
    print(f"public_discovery_promotion_decision_rules_checked={promotion_decision_rules_checked}")
    print(f"public_discovery_promotion_event_safety_fields_checked={promotion_event_safety_fields_checked}")
    print(f"public_discovery_commerce_items_checked={commerce_items_checked}")
    print(f"public_discovery_commerce_types_checked={commerce_types_checked}")
    print(f"public_discovery_commerce_roles_checked={commerce_roles_checked}")
    print(f"public_discovery_commerce_free_keepsake_urls_checked={commerce_free_keepsake_urls_checked}")
    print(f"public_discovery_commerce_owned_supply_urls_checked={commerce_owned_supply_urls_checked}")
    print(f"public_discovery_commerce_free_keepsake_guardians_checked={commerce_free_keepsake_guardians_checked}")
    print(f"public_discovery_commerce_owned_supply_guardians_checked={commerce_owned_supply_guardians_checked}")
    print(f"public_discovery_commerce_owned_supply_contacts_checked={commerce_owned_supply_contacts_checked}")
    print(f"public_discovery_commerce_affiliate_locale_policies_checked={commerce_affiliate_locale_policies_checked}")
    print(f"public_discovery_commerce_amazon_associate_tags_checked={commerce_amazon_associate_tags_checked}")
    print(f"public_discovery_commerce_affiliate_asins_checked={commerce_affiliate_asins_checked}")
    print(f"public_discovery_commerce_primary_affiliate_urls_checked={commerce_primary_affiliate_urls_checked}")
    print(f"public_discovery_commerce_affiliate_localized_urls_checked={commerce_affiliate_localized_urls_checked}")
    print(f"public_discovery_commerce_taiwan_affiliate_urls_checked={commerce_taiwan_affiliate_urls_checked}")
    print(f"public_discovery_commerce_luna_gumroad_urls_checked={commerce_luna_gumroad_urls_checked}")
    print(f"public_discovery_commerce_revenue_playbook_checked={commerce_revenue_playbook_checked}")
    print(f"public_discovery_commerce_item_playbook_links_checked={commerce_item_playbook_links_checked}")
    print(f"public_discovery_site_index_pages_checked={site_index_pages_checked}")
    print(f"public_discovery_site_index_languages_checked={site_index_languages_checked}")
    print(f"public_discovery_site_index_groups_checked={site_index_groups_checked}")
    print(f"public_discovery_site_index_flows_checked={site_index_flows_checked}")
    print(f"public_discovery_guardian_profiles_checked={guardian_profiles_checked}")
    print(f"public_discovery_guardian_profile_routes_checked={guardian_profile_routes_checked}")
    print(f"public_discovery_guardian_profile_assets_checked={guardian_profile_assets_checked}")
    print(f"public_discovery_guardian_profile_guides_checked={guardian_profile_guides_checked}")
    print(f"public_discovery_site_health_coverage_checked={site_health_coverage_checked}")
    print(f"public_discovery_site_health_support_files_checked={site_health_support_files_checked}")
    print(f"public_discovery_site_health_gates_checked={site_health_gates_checked}")
    print(f"public_discovery_site_health_profile_smoke_counters_checked={site_health_profile_smoke_counters_checked}")
    print(f"public_discovery_site_health_local_audit_groups_checked={site_health_local_audit_groups_checked}")
    print(f"public_discovery_site_health_indexes_checked={site_health_indexes_checked}")
    print(f"public_discovery_release_content_checked={release_content_checked}")
    print(f"public_discovery_release_indexes_checked={release_indexes_checked}")
    print(f"public_discovery_release_commands_checked={release_commands_checked}")
    print(f"public_discovery_release_local_audit_groups_checked={release_local_audit_groups_checked}")
    print(f"public_discovery_release_outcomes_checked={release_outcomes_checked}")
    print(f"public_discovery_release_profile_smoke_counters_checked={release_profile_smoke_counters_checked}")
    print(f"public_discovery_safety_index_boundaries_checked={safety_index_boundaries_checked}")
    print(f"public_discovery_safety_index_routes_checked={safety_index_routes_checked}")
    print(f"public_discovery_safety_index_route_targets_checked={safety_index_route_targets_checked}")
    print(f"public_discovery_safety_index_not_for_checked={safety_index_not_for_checked}")
    print(f"public_discovery_safety_index_steps_checked={safety_index_steps_checked}")
    print(f"public_discovery_safety_index_first_step_urls_checked={safety_index_first_step_urls_checked}")
    print(f"public_discovery_ai_guardians_checked={ai_discovery_guardians_checked}")
    print(f"public_discovery_ai_languages_checked={ai_discovery_languages_checked}")
    print(f"public_discovery_ai_core_concepts_checked={ai_discovery_core_concepts_checked}")
    print(f"public_discovery_ai_questions_checked={ai_discovery_questions_checked}")
    print(f"public_discovery_ai_priority_urls_checked={ai_discovery_priority_urls_checked}")
    print(f"public_discovery_ai_discovery_files_checked={ai_discovery_discovery_files_checked}")
    print(f"public_discovery_ai_guidance_fields_checked={ai_discovery_guidance_fields_checked}")
    print(f"public_discovery_ai_profile_smoke_counters_checked={ai_discovery_profile_smoke_counters_checked}")
    print(f"public_discovery_cross_indexes_checked={discovery_cross_indexes_checked}")
    print(f"public_discovery_cross_index_urls_checked={discovery_cross_urls_checked}")
    print(f"public_discovery_cross_index_targets_checked={discovery_cross_targets_checked}")
    print(f"public_discovery_cross_index_fragments_checked={discovery_cross_fragments_checked}")
    print(f"public_discovery_cross_core_routes_checked={discovery_cross_core_routes_checked}")
    print(f"public_discovery_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
