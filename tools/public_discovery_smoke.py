#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from io import BytesIO
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from PIL import Image


DEFAULT_BASE_URL = "https://lovetypes.tw"
CANONICAL_HOST = "lovetypes.tw"
EXPECTED_FEED_ITEMS = 12
EXPECTED_MANIFEST_LANG = "zh-TW"
EXPECTED_MANIFEST_SHORTCUTS = 6
EXPECTED_MANIFEST_SHORTCUT_URLS = (
    "/#quiz-section",
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
    "Affiliate links are kept on the Resources page",
    "No full-site advertising script is enabled",
    "Generative answer index: /ai-discovery.json",
    "Contact email: contact@lovetypes.tw",
)
REQUIRED_LLMS_HIGH_VALUE_URLS = (
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
    "Resources may contain affiliate links",
    "Luna packs use Gumroad purchase links",
    "not therapy, medical, legal, or diagnostic advice",
)
REQUIRED_ROBOTS_LINES = (
    "User-agent: *",
    "Allow: /",
    "Sitemap: https://lovetypes.tw/sitemap.xml",
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
}
EXPECTED_COMMERCE_TYPE_COUNTS = {
    "free_keepsake": 5,
    "owned_supply_waitlist": 5,
    "affiliate_book": 4,
    "luna_gumroad_pack": 6,
}
EXPECTED_COMMERCE_ROLE_COUNTS = {"lead": 5, "retention": 5, "revenue": 10}
EXPECTED_SITE_INDEX_LANGS = {"zh", "en", "ja", "ko", "es"}
EXPECTED_SITE_INDEX_FLOWS = {"quiz_to_guardian", "guardian_supply", "supply_to_contact", "trust_boundary"}
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
        self.robots = ""
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
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


def check_feed(base_url: str) -> tuple[list[str], int, int, int]:
    path = "/feed.xml"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0
    if "xml" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected XML content type, got {response.headers.get('content-type')!r}")
    issues.extend(cache_is_reasonable(path, response))
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [f"{path}: invalid XML: {error}"], 0, 0, 0
    if root.tag != "rss" or root.attrib.get("version") != "2.0":
        issues.append(f"{path}: expected RSS 2.0 root")
    channel = root.find("channel")
    if channel is None:
        return [f"{path}: missing channel"], 0, 0, 0
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
    return issues, len(items), links_checked, item_metadata_checked


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


def check_manifest(base_url: str) -> tuple[list[str], int, int, int, int, int, int, int]:
    path = "/site.webmanifest"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", "") and "manifest" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected manifest/json content type, got {response.headers.get('content-type')!r}")
    issues.extend(cache_is_reasonable(path, response))
    try:
        manifest = json.loads(response.text)
    except json.JSONDecodeError as error:
        return [f"{path}: invalid JSON: {error}"], 0, 0, 0, 0, 0, 0, 0
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


def check_text_files(base_url: str) -> tuple[list[str], int, int, int]:
    issues: list[str] = []
    text_files_checked = 0
    security_fields_checked = 0
    humans_snippets_checked = 0
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
    return issues, text_files_checked, security_fields_checked, humans_snippets_checked


def check_robots(base_url: str) -> tuple[list[str], int, int]:
    path = "/robots.txt"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    robots_lines_checked = 0
    sitemap_links_checked = 0
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], robots_lines_checked, sitemap_links_checked
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
        if "xml" not in sitemap_response.headers.get("content-type", ""):
            issues.append(f"{path}: sitemap {sitemap_url} expected XML content type, got {sitemap_response.headers.get('content-type')!r}")
    if not sitemap_urls:
        issues.append(f"{path}: missing Sitemap directive")
    return issues, robots_lines_checked, sitemap_links_checked


def check_funnel_events(base_url: str) -> tuple[list[str], int, int, int]:
    path = "/funnel-events.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0
    events = data.get("events", []) if isinstance(data, dict) else []
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("localStorageKey") != "lovetypes:funnel-events:v1":
        issues.append(f"{path}: localStorageKey should match runtime storage key")
    names = {event.get("name") for event in events if isinstance(event, dict)}
    event_by_name = {event.get("name"): event for event in events if isinstance(event, dict)}
    missing = sorted(REQUIRED_FUNNEL_EVENTS.difference(names))
    if missing:
        issues.append(f"{path}: missing core funnel events {', '.join(missing)}")
    gumroad_event = event_by_name.get("luna_gumroad_pack_click", {})
    if gumroad_event.get("role") != "revenue":
        issues.append(f"{path}: luna_gumroad_pack_click should be a revenue event")
    if len(events) < 50:
        issues.append(f"{path}: expected at least 50 funnel events, got {len(events)}")
    categories = {event.get("category") for event in events if isinstance(event, dict) and event.get("category")}
    roles = {event.get("role") for event in events if isinstance(event, dict) and event.get("role")}
    return issues, len(events), len(categories), len(roles)


def check_commerce_catalog(base_url: str) -> tuple[list[str], int, int, int]:
    path = "/commerce-catalog.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0
    if data.get("schemaVersion") != 1:
        issues.append(f"{path}: schemaVersion should be 1")
    if data.get("contact") != "contact@lovetypes.tw":
        issues.append(f"{path}: contact should be contact@lovetypes.tw")
    boundaries = " ".join(str(item) for item in data.get("safetyBoundaries", []))
    for snippet in ("No therapeutic", "Affiliate links", "Email waitlist", "sensitive personal details"):
        if snippet not in boundaries:
            issues.append(f"{path}: missing safety boundary snippet {snippet!r}")
    items = data.get("items", [])
    if not isinstance(items, list):
        return [f"{path}: items should be a list"], 0, 0, 0
    if len(items) != 20:
        issues.append(f"{path}: expected 20 commerce items, got {len(items)}")
    type_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    ids: set[str] = set()
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
        if not isinstance(item.get("conversion"), str) or not item["conversion"]:
            issues.append(f"{path}: {item_id or '<unknown>'} missing conversion")
        if not isinstance(item.get("disclosure"), str) or not item["disclosure"]:
            issues.append(f"{path}: {item_id or '<unknown>'} missing disclosure")
    for item_type, expected in EXPECTED_COMMERCE_TYPE_COUNTS.items():
        if type_counts.get(item_type) != expected:
            issues.append(f"{path}: expected {expected} {item_type} items, got {type_counts.get(item_type, 0)}")
    for role, expected in EXPECTED_COMMERCE_ROLE_COUNTS.items():
        if role_counts.get(role) != expected:
            issues.append(f"{path}: expected {expected} {role} items, got {role_counts.get(role, 0)}")
    return issues, len(items), len(type_counts), len(role_counts)


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
    if len(pages) != 150:
        issues.append(f"{path}: expected 150 pages, got {len(pages)}")
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


def check_site_health(base_url: str) -> tuple[list[str], int, int, int, int]:
    path = "/site-health.json"
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
    if data.get("status") != "ready_for_predeploy":
        issues.append(f"{path}: status should be ready_for_predeploy")
    coverage = data.get("coverage", {})
    expected = {
        "indexablePages": 150,
        "localizedPaths": 30,
        "languages": 5,
        "routeGroups": 5,
        "coreFlows": 4,
        "guardians": 5,
        "guardianRoutes": 35,
        "guardianAssets": 20,
        "commerceItems": 20,
        "commerceTypes": 4,
        "commerceRoles": 3,
        "supportFiles": 17,
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
    if not isinstance(support_files, list) or len(support_files) != 17:
        issues.append(f"{path}: expected 17 support files")
    if not isinstance(gates, dict) or set(gates) != {"localPredeploy", "publicDiscovery", "publicDeploy", "versionedAssets"}:
        issues.append(f"{path}: requiredGates should list four gate names")
    indexes = data.get("primaryIndexes", {})
    if not isinstance(indexes, dict) or len(indexes) < 9:
        issues.append(f"{path}: primaryIndexes should list at least nine entries")
    return issues, coverage_checked, len(support_files) if isinstance(support_files, list) else 0, len(gates) if isinstance(gates, dict) else 0, len(indexes) if isinstance(indexes, dict) else 0


def check_release_info(base_url: str) -> tuple[list[str], int, int, int, int]:
    path = "/release.json"
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
    if data.get("deploymentTarget") != "Cloudflare Pages project lovetypes":
        issues.append(f"{path}: deploymentTarget should name Cloudflare Pages project lovetypes")
    if data.get("branch") != "main":
        issues.append(f"{path}: branch should be main")
    contents = data.get("releaseContents", {})
    expected_contents = {"indexablePages": 150, "languages": 5, "guardians": 5, "commerceItems": 20, "coreFlows": 4}
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
    if not isinstance(indexes, dict) or len(indexes) != 9:
        issues.append(f"{path}: publicIndexes should contain nine entries")
    if not isinstance(commands, list) or len(commands) != 5:
        issues.append(f"{path}: verificationCommands should contain five commands")
    if not isinstance(outcomes, list) or "public_versioned_asset_stale_refs=0" not in outcomes:
        issues.append(f"{path}: requiredOutcomes should include public_versioned_asset_stale_refs=0")
    return issues, content_checked, len(indexes) if isinstance(indexes, dict) else 0, len(commands) if isinstance(commands, list) else 0, len(outcomes) if isinstance(outcomes, list) else 0


def check_safety_index(base_url: str) -> tuple[list[str], int, int, int, int]:
    path = "/safety-index.json"
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
    if not isinstance(boundaries, list) or len(boundaries) != 5:
        issues.append(f"{path}: expected five boundaries")
        return issues, len(boundaries) if isinstance(boundaries, list) else 0, 0, len(not_for), len(steps) if isinstance(steps, list) else 0
    route_count = 0
    seen_ids = set()
    for boundary in boundaries:
        if not isinstance(boundary, dict):
            issues.append(f"{path}: boundary should be an object")
            continue
        boundary_id = boundary.get("id")
        seen_ids.add(boundary_id)
        routes = boundary.get("routes", [])
        route_count += len(routes) if isinstance(routes, list) else 0
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
    return issues, len(boundaries), route_count, len(not_for), len(steps) if isinstance(steps, list) else 0


def check_ai_discovery(base_url: str) -> tuple[list[str], int, int, int, int, int]:
    path = "/ai-discovery.json"
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0, 0, 0
    if "json" not in response.headers.get("content-type", ""):
        issues.append(f"{path}: expected JSON content type, got {response.headers.get('content-type')!r}")
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"], 0, 0, 0, 0, 0
    if not isinstance(data, dict):
        return [f"{path}: root should be an object"], 0, 0, 0, 0, 0
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
    expected_totals = {"guardians": 5, "answerableQuestions": 10, "priorityUrls": 11, "languages": 5, "discoveryFiles": 9}
    for key, expected in expected_totals.items():
        if not isinstance(totals, dict) or totals.get(key) != expected:
            got = totals.get(key) if isinstance(totals, dict) else None
            issues.append(f"{path}: totals.{key} should be {expected}, got {got!r}")
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
    questions = data.get("answerableQuestions", [])
    if not isinstance(questions, list) or len(questions) != 10:
        issues.append(f"{path}: answerableQuestions should include ten entries")
    else:
        for snippet in ("LoveTypes 是什麼？", "LoveTypes 能取代諮商、醫療或緊急求助嗎？", "LoveTypes 是否包含聯盟連結或購買入口？"):
            if not any(isinstance(item, dict) and item.get("question") == snippet for item in questions):
                issues.append(f"{path}: answerableQuestions missing {snippet!r}")
    priority_urls = data.get("priorityUrls", [])
    if not isinstance(priority_urls, list) or len(priority_urls) != 11:
        issues.append(f"{path}: priorityUrls should include eleven entries")
    files = data.get("discoveryFiles", {})
    expected_files = {"aiDiscovery", "llms", "siteIndex", "guardianProfiles", "commerceCatalog", "safetyIndex", "release", "siteHealth", "humans"}
    if not isinstance(files, dict) or set(files) != expected_files:
        issues.append(f"{path}: discoveryFiles should contain {sorted(expected_files)}")
    return (
        issues,
        len(guardians) if isinstance(guardians, list) else 0,
        len(questions) if isinstance(questions, list) else 0,
        len(priority_urls) if isinstance(priority_urls, list) else 0,
        len(files) if isinstance(files, dict) else 0,
        len(guidance) if isinstance(guidance, dict) else 0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public feed, manifest, llms, security, and ads discovery files.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Production or preview base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    issues: list[str] = []
    feed_issues, feed_items, feed_links_checked, feed_item_metadata_checked = check_feed(base_url)
    (
        manifest_issues,
        manifest_icons_checked,
        manifest_icon_dimensions_checked,
        manifest_shortcuts,
        manifest_shortcut_links_checked,
        manifest_expected_shortcuts_checked,
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
    text_issues, text_files_checked, security_fields_checked, humans_snippets_checked = check_text_files(base_url)
    robots_issues, robots_lines_checked, robots_sitemap_links_checked = check_robots(base_url)
    funnel_issues, funnel_events_checked, funnel_categories_checked, funnel_roles_checked = check_funnel_events(base_url)
    commerce_issues, commerce_items_checked, commerce_types_checked, commerce_roles_checked = check_commerce_catalog(base_url)
    site_index_issues, site_index_pages_checked, site_index_languages_checked, site_index_groups_checked, site_index_flows_checked = check_site_index(base_url)
    guardian_profile_issues, guardian_profiles_checked, guardian_profile_routes_checked, guardian_profile_assets_checked, guardian_profile_guides_checked = check_guardian_profiles(base_url)
    site_health_issues, site_health_coverage_checked, site_health_support_files_checked, site_health_gates_checked, site_health_indexes_checked = check_site_health(base_url)
    release_issues, release_content_checked, release_indexes_checked, release_commands_checked, release_outcomes_checked = check_release_info(base_url)
    safety_index_issues, safety_index_boundaries_checked, safety_index_routes_checked, safety_index_not_for_checked, safety_index_steps_checked = check_safety_index(base_url)
    ai_discovery_issues, ai_discovery_guardians_checked, ai_discovery_questions_checked, ai_discovery_priority_urls_checked, ai_discovery_discovery_files_checked, ai_discovery_guidance_fields_checked = check_ai_discovery(base_url)
    issues.extend(feed_issues)
    issues.extend(manifest_issues)
    issues.extend(llms_issues)
    issues.extend(text_issues)
    issues.extend(robots_issues)
    issues.extend(funnel_issues)
    issues.extend(commerce_issues)
    issues.extend(site_index_issues)
    issues.extend(guardian_profile_issues)
    issues.extend(site_health_issues)
    issues.extend(release_issues)
    issues.extend(safety_index_issues)
    issues.extend(ai_discovery_issues)

    print(f"public_discovery_feed_items={feed_items}")
    print(f"public_discovery_feed_links_checked={feed_links_checked}")
    print(f"public_discovery_feed_item_metadata_checked={feed_item_metadata_checked}")
    print(f"public_discovery_manifest_icons_checked={manifest_icons_checked}")
    print(f"public_discovery_manifest_icon_dimensions_checked={manifest_icon_dimensions_checked}")
    print(f"public_discovery_manifest_shortcuts={manifest_shortcuts}")
    print(f"public_discovery_manifest_shortcut_links_checked={manifest_shortcut_links_checked}")
    print(f"public_discovery_manifest_expected_shortcuts_checked={manifest_expected_shortcuts_checked}")
    print(f"public_discovery_manifest_screenshots_checked={manifest_screenshots_checked}")
    print(f"public_discovery_manifest_screenshot_dimensions_checked={manifest_screenshot_dimensions_checked}")
    print(f"public_discovery_llms_sections_checked={llms_sections_checked}")
    print(f"public_discovery_llms_snippets_checked={llms_snippets_checked}")
    print(f"public_discovery_llms_high_value_urls_checked={llms_high_value_urls_checked}")
    print(f"public_discovery_llms_urls_checked={llms_urls_checked}")
    print(f"public_discovery_llms_url_canonicals_checked={llms_url_canonicals_checked}")
    print(f"public_discovery_text_files_checked={text_files_checked}")
    print(f"public_discovery_security_fields_checked={security_fields_checked}")
    print(f"public_discovery_humans_snippets_checked={humans_snippets_checked}")
    print(f"public_discovery_robots_lines_checked={robots_lines_checked}")
    print(f"public_discovery_robots_sitemap_links_checked={robots_sitemap_links_checked}")
    print(f"public_discovery_funnel_events_checked={funnel_events_checked}")
    print(f"public_discovery_funnel_event_categories_checked={funnel_categories_checked}")
    print(f"public_discovery_funnel_event_roles_checked={funnel_roles_checked}")
    print(f"public_discovery_commerce_items_checked={commerce_items_checked}")
    print(f"public_discovery_commerce_types_checked={commerce_types_checked}")
    print(f"public_discovery_commerce_roles_checked={commerce_roles_checked}")
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
    print(f"public_discovery_site_health_indexes_checked={site_health_indexes_checked}")
    print(f"public_discovery_release_content_checked={release_content_checked}")
    print(f"public_discovery_release_indexes_checked={release_indexes_checked}")
    print(f"public_discovery_release_commands_checked={release_commands_checked}")
    print(f"public_discovery_release_outcomes_checked={release_outcomes_checked}")
    print(f"public_discovery_safety_index_boundaries_checked={safety_index_boundaries_checked}")
    print(f"public_discovery_safety_index_routes_checked={safety_index_routes_checked}")
    print(f"public_discovery_safety_index_not_for_checked={safety_index_not_for_checked}")
    print(f"public_discovery_safety_index_steps_checked={safety_index_steps_checked}")
    print(f"public_discovery_ai_guardians_checked={ai_discovery_guardians_checked}")
    print(f"public_discovery_ai_questions_checked={ai_discovery_questions_checked}")
    print(f"public_discovery_ai_priority_urls_checked={ai_discovery_priority_urls_checked}")
    print(f"public_discovery_ai_discovery_files_checked={ai_discovery_discovery_files_checked}")
    print(f"public_discovery_ai_guidance_fields_checked={ai_discovery_guidance_fields_checked}")
    print(f"public_discovery_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
