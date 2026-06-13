#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import socket
import ssl
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
EXPECTED_HREFLANGS = ("zh-TW", "en", "ja", "ko", "es", "x-default")
LOCALE_PREFIXES = {"zh-TW": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
AFFILIATE_DISCLOSURE_SNIPPET = "本頁部分連結為聯盟行銷連結"
BOOKS_AFFILIATE_HOST = "www.books.com.tw"
AMAZON_AFFILIATE_HOST = "www.amazon.com"
AMAZON_ASSOCIATE_TAG = "parenttechche-20"
PUBLIC_PATHS = [
    "/",
    "/start/",
    "/characters/",
    "/characters/iris/",
    "/resources/",
    "/repair-plan/",
    "/keepsakes/",
    "/luna-yoga-music/",
    "/guides/",
    "/guides/words-of-affirmation-scripts/",
    "/about/",
    "/theory/",
    "/contact/",
    "/garden-map/",
    "/en/",
    "/en/start/",
    "/en/guides/words-of-affirmation-scripts/",
    "/en/resources/",
    "/en/characters/",
    "/en/garden-map/",
    "/ja/",
    "/ja/start/",
    "/ja/characters/",
    "/ja/garden-map/",
    "/ko/",
    "/ko/start/",
    "/ko/characters/",
    "/ko/garden-map/",
    "/ko/resources/",
    "/es/",
    "/es/start/",
    "/es/characters/",
    "/es/garden-map/",
    "/es/resources/",
    "/ja/resources/",
    "/ko/repair-plan/",
    "/es/guides/",
]
EXPECTED_TEXT = {
    "/": "LoveTypes 情感守護者宇宙",
    "/start/": "五種愛之語測驗入口",
    "/characters/": "五位情感守護者總覽",
    "/resources/": "旅人補給",
    "/repair-plan/": "7 日心語修復計畫",
    "/luna-yoga-music/": "Luna Yoga Music",
    "/guides/words-of-affirmation-scripts/": "肯定言詞的具體句型",
    "/en/guides/words-of-affirmation-scripts/": "Practical Scripts for Words of Affirmation",
    "/keepsakes/": "守護者收藏室",
    "/contact/": "contact@lovetypes.tw",
    "/garden-map/": "心語庭園地圖",
    "/en/": "LoveTypes Emotion Guardians",
    "/en/start/": "Five Love Languages Quiz Entrance",
    "/en/resources/": "Resources",
    "/en/garden-map/": "Heart Garden Map",
    "/ja/": "LoveTypes 感情の守護者",
    "/ja/start/": "5つの愛の言語 診断入口",
    "/ja/garden-map/": "心語の庭マップ",
    "/ko/": "LoveTypes 감정 수호자",
    "/ko/start/": "다섯 가지 사랑의 언어 테스트 입구",
    "/ko/garden-map/": "마음의 정원 지도",
    "/ko/resources/": "자료",
    "/es/": "LoveTypes Guardianas Emocionales",
    "/es/start/": "Entrada al test de los cinco lenguajes del amor",
    "/es/garden-map/": "Mapa del Jardín del Corazón",
    "/es/resources/": "Recursos",
    "/en/characters/": "Five Emotion Guardians Overview",
    "/ja/characters/": "五人の感情の守護者一覧",
    "/ko/characters/": "다섯 감정 수호자 한눈에 보기",
    "/es/characters/": "Resumen de las Cinco Guardianas Emocionales",
    "/en/keepsakes/": "Guardian Keepsake Hall",
    "/ja/resources/": "リソース",
    "/ko/repair-plan/": "7일 마음 언어 회복 계획",
    "/es/guides/": "Guías de Guardianas LoveTypes",
}
EXPECTED_ANCHOR_TARGETS = {
    "/characters/": ("guardian-start", "guardian-map"),
    "/en/characters/": ("guardian-start", "guardian-map"),
    "/ja/characters/": ("guardian-start", "guardian-map"),
    "/ko/characters/": ("guardian-start", "guardian-map"),
    "/es/characters/": ("guardian-start", "guardian-map"),
    "/keepsakes/": tuple(f"keepsake-card-{slug}" for slug in GUARDIAN_SLUGS),
    "/en/keepsakes/": tuple(f"keepsake-card-{slug}" for slug in GUARDIAN_SLUGS),
    "/resources/": ("supply-start", "supply-routes", *(f"supply-{slug}" for slug in GUARDIAN_SLUGS)),
    "/repair-plan/": tuple(f"plan-{slug}" for slug in GUARDIAN_SLUGS),
    "/guides/words-of-affirmation-scripts/": ("guide-action-bridge",),
    "/en/guides/words-of-affirmation-scripts/": ("guide-action-bridge",),
    "/about/": ("trust-action-routes",),
    "/theory/": ("trust-action-routes",),
}
EXPECTED_HREF_TARGETS = {
    "/characters/": ("/#quiz-section", "#guardian-map", "/resources/"),
    "/en/characters/": ("/en/#quiz-section", "#guardian-map", "/en/resources/"),
    "/ja/characters/": ("/ja/#quiz-section", "#guardian-map", "/ja/resources/"),
    "/ko/characters/": ("/ko/#quiz-section", "#guardian-map", "/ko/resources/"),
    "/es/characters/": ("/es/#quiz-section", "#guardian-map", "/es/resources/"),
    "/keepsakes/": tuple(
        target
        for slug in GUARDIAN_SLUGS
        for target in (f"/resources/#supply-{slug}", f"/repair-plan/#plan-{slug}")
    ),
    "/en/keepsakes/": tuple(
        target
        for slug in GUARDIAN_SLUGS
        for target in (f"/en/resources/#supply-{slug}", f"/en/repair-plan/#plan-{slug}")
    ),
    "/resources/": ("/#quiz-section", "#supply-routes", "/luna-yoga-music/", *(f"#supply-{slug}" for slug in GUARDIAN_SLUGS)),
    "/repair-plan/": tuple(f"/resources/#supply-{slug}" for slug in GUARDIAN_SLUGS),
    "/luna-yoga-music/": tuple(
        target
        for slug in GUARDIAN_SLUGS
        for target in (f"/repair-plan/#plan-{slug}", f"/resources/#supply-{slug}")
    ),
    "/guides/words-of-affirmation-scripts/": (
        "/characters/iris/",
        "/resources/#supply-iris",
        "/repair-plan/#plan-iris",
    ),
    "/en/guides/words-of-affirmation-scripts/": (
        "/en/characters/iris/",
        "/en/resources/#supply-iris",
        "/en/repair-plan/#plan-iris",
    ),
    "/about/": (
        "/#quiz-section",
        "/characters/",
        "/guides/",
        "/contact/",
    ),
    "/theory/": (
        "/#quiz-section",
        "/characters/",
        "/repair-plan/",
        "/resources/",
    ),
    "/garden-map/": (
        "/#quiz-section",
        "/characters/",
        "/resources/",
        "/repair-plan/",
        "/keepsakes/",
        "/luna-yoga-music/",
        "/guides/",
        "/about/",
        "/theory/",
        "/contact/",
        "/privacy/",
    ),
    "/en/garden-map/": (
        "/en/#quiz-section",
        "/en/characters/",
        "/en/resources/",
        "/en/repair-plan/",
        "/en/keepsakes/",
        "/en/luna-yoga-music/",
        "/en/guides/",
        "/en/about/",
        "/en/theory/",
        "/en/contact/",
        "/en/privacy/",
    ),
    "/ja/garden-map/": (
        "/ja/#quiz-section",
        "/ja/characters/",
        "/ja/resources/",
        "/ja/repair-plan/",
        "/ja/keepsakes/",
        "/ja/luna-yoga-music/",
        "/ja/guides/",
        "/ja/about/",
        "/ja/theory/",
        "/ja/contact/",
        "/ja/privacy/",
    ),
    "/ko/garden-map/": (
        "/ko/#quiz-section",
        "/ko/characters/",
        "/ko/resources/",
        "/ko/repair-plan/",
        "/ko/keepsakes/",
        "/ko/luna-yoga-music/",
        "/ko/guides/",
        "/ko/about/",
        "/ko/theory/",
        "/ko/contact/",
        "/ko/privacy/",
    ),
    "/es/garden-map/": (
        "/es/#quiz-section",
        "/es/characters/",
        "/es/resources/",
        "/es/repair-plan/",
        "/es/keepsakes/",
        "/es/luna-yoga-music/",
        "/es/guides/",
        "/es/about/",
        "/es/theory/",
        "/es/contact/",
        "/es/privacy/",
    ),
}
REDIRECTS = {
    "/luna/": "/luna-yoga-music/",
    "/images/characters/iris.webp": "/assets/lovetypes/guardians/iris.webp",
    "/images/characters/noah.webp": "/assets/lovetypes/guardians/noah.webp",
    "/images/characters/vivian.webp": "/assets/lovetypes/guardians/vivian.webp",
    "/images/characters/claire.webp": "/assets/lovetypes/guardians/claire.webp",
    "/images/characters/dora.webp": "/assets/lovetypes/guardians/dora.webp",
    "/assets/lovetypes/share/iris-story.webp": "/assets/lovetypes/share/iris-story-zh.webp",
    "/assets/lovetypes/share/noah-story.webp": "/assets/lovetypes/share/noah-story-zh.webp",
    "/assets/lovetypes/share/vivian-story.webp": "/assets/lovetypes/share/vivian-story-zh.webp",
    "/assets/lovetypes/share/claire-story.webp": "/assets/lovetypes/share/claire-story-zh.webp",
    "/assets/lovetypes/share/dora-story.webp": "/assets/lovetypes/share/dora-story-zh.webp",
        "/luna-yoga-music/luna.css": "/shared-20260605-contrast.css",
    "/assets/lovetypes/guides/lovetypes-guide-toolkit.webp": "/assets/lovetypes/share/guide-toolkit-og.jpg",
    "/assets/lovetypes/backgrounds/guardian-garden.webp": "/assets/lovetypes/backgrounds/guardian-garden-desktop.webp",
    "/assets/lovetypes/backgrounds/quiz-desk.webp": "/assets/lovetypes/backgrounds/guardian-garden-desktop.webp",
    "/assets/lovetypes/backgrounds/quiz-desk-mobile.webp": "/assets/lovetypes/backgrounds/guardian-garden-mobile.webp",
    "/og-cover.webp": "/og-cover.jpg",
    "/en/luna/": "/en/luna-yoga-music/",
    "/ja/luna/": "/ja/luna-yoga-music/",
    "/ko/luna/": "/ko/luna-yoga-music/",
    "/es/luna/": "/es/luna-yoga-music/",
}
SUPPORT_FILES = {
    "/robots.txt": ["User-agent: *", "Allow: /", "Sitemap: https://lovetypes.tw/sitemap.xml"],
    "/ads.txt": ["google.com", "DIRECT", "f08c47fec0942fa0"],
    "/security.txt": ["Contact: mailto:contact@lovetypes.tw", "Policy: https://lovetypes.tw/privacy/"],
    "/.well-known/security.txt": ["Contact: mailto:contact@lovetypes.tw", "Policy: https://lovetypes.tw/privacy/"],
    "/llms.txt": [
        "# LoveTypes - Heart Garden Emotion Guardians",
        "Production: https://lovetypes.tw/",
        "## Five Guardians",
        "## Guide Index",
        "## Commercial and Safety Boundaries",
        "https://lovetypes.tw/resources/",
        "https://lovetypes.tw/luna-yoga-music/",
        "Contact email: contact@lovetypes.tw",
    ],
    "/humans.txt": [
        "/* TEAM */",
        "Site: LoveTypes",
        "Contact: contact@lovetypes.tw",
        "Production: https://lovetypes.tw/",
        "Generator: tools/generate_multilingual_site.py",
        "Hosting: Cloudflare Pages",
        "Resources may contain localized affiliate links",
        "Luna packs use Gumroad purchase links",
        "not therapy, medical, legal, or diagnostic advice",
    ],
    "/funnel-events.json": [
        '"schemaVersion": 1',
        '"localStorageKey": "lovetypes:funnel-events:v1"',
        '"quiz_result_supply_route"',
        '"supply_route_affiliate_book"',
        '"luna_hero_listen"',
        '"contact_supply_mailto"',
        '"campaign_landing"',
    ],
    "/commerce-catalog.json": [
        '"schemaVersion": 1',
        '"contact": "contact@lovetypes.tw"',
        '"free_keepsake"',
        '"owned_supply_waitlist"',
        '"affiliate_book"',
        '"luna_gumroad_pack"',
        '"luna_gumroad_pack_click"',
        '"No therapeutic, medical, legal, diagnostic, or guaranteed outcome claims."',
    ],
    "/site-index.json": [
        '"schemaVersion": 1',
        '"production": "https://lovetypes.tw/"',
        '"shorts_to_quiz"',
        '"quiz_to_guardian"',
        '"guardian_supply"',
        '"supply_to_contact"',
        '"trust_boundary"',
        '"canonical": "https://lovetypes.tw/start/"',
        '"canonical": "https://lovetypes.tw/characters/iris/"',
        '"canonical": "https://lovetypes.tw/en/resources/"',
    ],
    "/guardian-profiles.json": [
        '"schemaVersion": 1',
        '"slug": "iris"',
        '"slug": "noah"',
        '"slug": "vivian"',
        '"slug": "claire"',
        '"slug": "dora"',
        '"Words of affirmation"',
        '"Quality time"',
        '"Receiving gifts"',
        '"Acts of service"',
        '"Physical touch"',
        '"profile": "https://lovetypes.tw/characters/iris/"',
    ],
    "/site-health.json": [
        '"schemaVersion": 1',
        '"status": "ready_for_predeploy"',
        '"indexablePages": 155',
        '"guardians": 5',
        '"commerceItems": 20',
        '"supportFiles": 18',
        '"localPredeploy"',
        '"publicDiscovery"',
        '"publicDeploy"',
        '"versionedAssets"',
    ],
    "/release.json": [
        '"schemaVersion": 1',
        '"assetVersion":',
        '"deploymentTarget": "Cloudflare Pages project lovetypes"',
        '"branch": "main"',
        '"indexablePages": 155',
        '"guardians": 5',
        '"commerceItems": 20',
        '"python3 tools/predeploy_check.py"',
        '"public_versioned_asset_stale_refs=0"',
    ],
    "/safety-index.json": [
        '"schemaVersion": 1',
        '"contact": "contact@lovetypes.tw"',
        '"reflection_not_diagnosis"',
        '"urgent_risk_first"',
        '"do_not_buy_to_fix"',
        '"email_minimum_context"',
        '"external_store_boundary"',
        '"emergency support"',
        '"coercive purchase pressure"',
    ],
    "/ai-discovery.json": [
        '"schemaVersion": 1',
        '"siteName": "LoveTypes"',
        '"preferredLanguage": "zh-TW"',
        '"doNotUseAsDiagnosis": true',
        '"answerableQuestions"',
        '"canonical": "https://lovetypes.tw/start/"',
        '"LoveTypes 是什麼？"',
        '"guardian_mapping"',
        '"commercialDisclosure"',
        '"safetyBoundary"',
        '"aiDiscovery"',
    ],
}
NOT_FOUND_PATH = "/__lovetypes_missing_smoke__/"
NOT_FOUND_REQUIRED_TEXT = [
    "404 HEART GARDEN",
    "這盞燈暫時不在地圖上",
    "/#quiz-section",
    "/characters/",
    "/resources/",
    "/contact/",
]
SITEMAP_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}
REQUIRED_GLOBAL_HEADERS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "SAMEORIGIN",
}
IMMUTABLE_CACHE_RE = re.compile(r"max-age=31536000.*immutable", re.I)
VERSIONED_CSS_RE = re.compile(r"^/shared-[^/]+\.css$")
VERSIONED_INTERACTIONS_RE = re.compile(r"^/site-interactions-[^/]+\.js$")
VERSIONED_AFFILIATE_RE = re.compile(r"^/deferred-external-[^/]+\.js$")
VERSIONED_QUIZ_DATA_RE = re.compile(r"^/quiz-data-(zh|en|ja|ko|es)-[^/]+\.js$")
QUIZ_DATA_REQUIRED_MARKERS = (
    "data-quiz-root",
    "data-supply-saved",
    "data-repair-saved",
    "data-keepsake-saved",
    "data-luna-saved",
    "data-guardian-saved",
    "data-guide-saved",
    "data-garden-map-saved",
    "data-contact-saved",
)
CONTACT_FUNNEL_MARKERS = (
    "data-contact-resume-send",
    "data-contact-resume-copy",
    "data-contact-resume-route",
    "data-contact-resume-luna",
    "data-contact-resume-keepsake",
    "data-contact-resume-plan",
)
RESOURCE_SUPPLY_SAFETY_MARKERS = (
    ("supply compass", 'class="section supply-compass"'),
    ("starter kit", 'class="section starter-kit-section"'),
    ("owned supply signal", "data-supply-owned-signal"),
)
RESOURCE_EXPECTED_STARTER_CARDS = 4
RESOURCE_EXPECTED_WISHLIST_CARDS = len(GUARDIAN_SLUGS)
HOME_EXPECTED_UNIVERSE_GATE_CARDS = len(GUARDIAN_SLUGS)
CHARACTERS_EXPECTED_UNIVERSE_MAP_CARDS = len(GUARDIAN_SLUGS)
GARDEN_MAP_PATHS = {"/garden-map/", "/en/garden-map/", "/ja/garden-map/", "/ko/garden-map/", "/es/garden-map/"}
GARDEN_MAP_SECTION_MARKERS = (
    "data-garden-map-handoff",
    "data-garden-map-routes",
    "data-garden-map-tools",
    "data-garden-map-guardians",
    "data-garden-map-guides",
    "data-garden-map-trust",
)
GARDEN_MAP_EXPECTED_GUARDIAN_CARDS = len(GUARDIAN_SLUGS)
GARDEN_MAP_EXPECTED_GUIDE_CARDS = 12
GARDEN_MAP_EXPECTED_ROUTE_CARDS = 4


def load_generator_config():
    generator_path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_site_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load generator config from {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR_CONFIG = load_generator_config()
CURRENT_STATIC_ASSETS = {
    "css": GENERATOR_CONFIG.CSS_ASSET,
    "interactions": GENERATOR_CONFIG.INTERACTIONS_ASSET,
    "affiliate": GENERATOR_CONFIG.AFFILIATE_ASSET,
}
CURRENT_QUIZ_DATA_ASSETS = GENERATOR_CONFIG.QUIZ_DATA_ASSETS
REDIRECTS["/luna-yoga-music/luna.css"] = GENERATOR_CONFIG.CSS_ASSET


@dataclass
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class HeadAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stylesheets: list[str] = []
        self.scripts: list[str] = []
        self.canonical = ""
        self.html_lang = ""
        self.robots = ""
        self.hreflang_links: list[tuple[str, str]] = []
        self.metas: list[dict[str, str]] = []
        self.jsonld_blocks: list[str] = []
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.anchors: list[dict[str, str]] = []
        self._in_jsonld_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "html":
            self.html_lang = data.get("lang", "")
        if tag == "link" and data.get("rel") == "stylesheet" and data.get("href"):
            self.stylesheets.append(data["href"])
        if tag == "link" and data.get("rel") == "canonical" and data.get("href"):
            self.canonical = data["href"]
        if tag == "link" and data.get("rel") == "alternate" and data.get("hreflang") and data.get("href"):
            self.hreflang_links.append((data["hreflang"], data["href"]))
        if tag == "meta" and data.get("name") == "robots":
            self.robots = data.get("content", "")
        if tag == "meta":
            self.metas.append(data)
        if tag == "script" and data.get("src"):
            self.scripts.append(data["src"])
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])
            self.anchors.append(data)
        if tag == "script" and data.get("type") == "application/ld+json":
            self._in_jsonld_script = True
            self.jsonld_blocks.append("")

    def handle_data(self, data: str) -> None:
        if self._in_jsonld_script and self.jsonld_blocks:
            self.jsonld_blocks[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_jsonld_script = False

    def meta_content(self, key: str) -> str:
        for meta in self.metas:
            if meta.get("property") == key or meta.get("name") == key:
                return meta.get("content", "")
        return ""


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url_once(url: str, *, follow_redirects: bool = True) -> Response:
    request = Request(url, headers={"User-Agent": "LoveTypes public deploy smoke/1.0"})
    context = ssl.create_default_context()
    try:
        opener = None
        if not follow_redirects:
            from urllib.request import HTTPSHandler, HTTPRedirectHandler, build_opener

            class NoRedirect(HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = build_opener(NoRedirect, HTTPSHandler(context=context))
        if opener:
            raw = opener.open(request, timeout=20)
        else:
            raw = urlopen(request, timeout=20, context=context)
        with raw:
            return Response(raw.geturl(), raw.status, {key.lower(): value for key, value in raw.headers.items()}, raw.read())
    except HTTPError as error:
        return Response(error.geturl(), error.code, {key.lower(): value for key, value in error.headers.items()}, error.read())
    except (TimeoutError, socket.timeout, URLError) as error:
        raise RuntimeError(f"failed to request {url}: {error}") from error


def request_url(url: str, *, follow_redirects: bool = True, attempts: int = 3) -> Response:
    last_error: RuntimeError | None = None
    for attempt in range(1, attempts + 1):
        try:
            return request_url_once(url, follow_redirects=follow_redirects)
        except RuntimeError as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.75 * attempt)
    assert last_error is not None
    raise last_error


def path_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path or "/"


def expected_html_lang(path: str) -> str:
    for prefix, lang in (
        ("/en/", "en"),
        ("/ja/", "ja"),
        ("/ko/", "ko"),
        ("/es/", "es"),
    ):
        if path.startswith(prefix):
            return lang
    return "zh-TW"


def expected_quiz_lang(path: str) -> str:
    html_lang = expected_html_lang(path)
    return "zh" if html_lang == "zh-TW" else html_lang


def expected_canonical(path: str) -> str:
    return urljoin(DEFAULT_BASE_URL, path)


def public_url_for_path(path: str) -> str:
    return DEFAULT_BASE_URL + (path if path != "/" else "/")


def localized_path(path: str, lang: str) -> str:
    parts = [part for part in path.split("/") if part]
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts = parts[1:]
    prefix = LOCALE_PREFIXES[lang]
    localized_parts = ([prefix] if prefix else []) + parts
    if not localized_parts:
        return "/"
    return "/" + "/".join(localized_parts) + "/"


def expected_hreflang_map(path: str) -> dict[str, str]:
    values = {lang: public_url_for_path(localized_path(path, lang)) for lang in LOCALE_PREFIXES}
    values["x-default"] = values["zh-TW"]
    return values


def jsonld_entities(data: object) -> list[dict]:
    if isinstance(data, dict):
        graph = data.get("@graph")
        if isinstance(graph, list):
            return [item for item in graph if isinstance(item, dict)]
        return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def check_social_metadata(path: str, assets: HeadAssetParser, canonical_url: str) -> tuple[list[str], list[str], int]:
    issues: list[str] = []
    social_image_urls: list[str] = []
    required_keys = (
        "og:type",
        "og:title",
        "og:description",
        "og:image",
        "og:url",
        "twitter:card",
        "twitter:image",
    )
    checked = 0
    values = {key: assets.meta_content(key) for key in required_keys}
    for key, value in values.items():
        checked += 1
        if not value:
            issues.append(f"{path}: missing social metadata {key}")
    if values["og:url"] and values["og:url"] != canonical_url:
        issues.append(f"{path}: og:url should match canonical {canonical_url!r}, got {values['og:url']!r}")
    if values["twitter:card"] and values["twitter:card"] != "summary_large_image":
        issues.append(f"{path}: twitter:card should be summary_large_image, got {values['twitter:card']!r}")
    if values["twitter:image"] and values["og:image"] and values["twitter:image"] != values["og:image"]:
        issues.append(f"{path}: twitter:image should match og:image")
    if values["og:image"]:
        social_image_urls.append(values["og:image"])
        if not values["og:image"].startswith(f"{DEFAULT_BASE_URL}/"):
            issues.append(f"{path}: og:image should use {DEFAULT_BASE_URL}, got {values['og:image']!r}")
    return issues, social_image_urls, checked


def check_jsonld(path: str, assets: HeadAssetParser) -> tuple[list[str], int, int]:
    issues: list[str] = []
    entities_checked = 0
    if not assets.jsonld_blocks:
        return [f"{path}: missing JSON-LD"], 0, 0
    for block in assets.jsonld_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as error:
            issues.append(f"{path}: invalid JSON-LD: {error}")
            continue
        entities = jsonld_entities(data)
        if not entities:
            issues.append(f"{path}: JSON-LD block should contain an object or graph")
            continue
        for entity in entities:
            entities_checked += 1
            if not entity.get("@type"):
                issues.append(f"{path}: JSON-LD entity missing @type")
            if entity.get("@context") and entity.get("@context") != "https://schema.org":
                issues.append(f"{path}: JSON-LD @context should be https://schema.org")
    return issues, len(assets.jsonld_blocks), entities_checked


def is_resources_path(path: str) -> bool:
    return bool(re.fullmatch(r"/(?:(?:en|ja|ko|es)/)?resources/", path))


def lang_for_path(path: str) -> str:
    match = re.match(r"^/(en|ja|ko|es)(?:/|$)", path)
    return match.group(1) if match else "zh"


def is_expected_affiliate_link(path: str, href: str) -> bool:
    parsed = urlparse(href)
    lang = lang_for_path(path)
    if lang == "zh":
        return (
            parsed.scheme == "https"
            and parsed.hostname == BOOKS_AFFILIATE_HOST
            and "/exep/assp.php/arthur0858/" in parsed.path
            and "utm_campaign=ap-202604" in parsed.query
        )
    return (
        parsed.scheme == "https"
        and parsed.hostname == AMAZON_AFFILIATE_HOST
        and parsed.path.startswith("/dp/")
        and parse_qs(parsed.query).get("tag", [""])[0] == AMAZON_ASSOCIATE_TAG
    )


def is_affiliate_host(hostname: str | None) -> bool:
    return hostname in {BOOKS_AFFILIATE_HOST, AMAZON_AFFILIATE_HOST}


def check_external_links(path: str, assets: HeadAssetParser, html: str) -> tuple[list[str], int, int]:
    issues: list[str] = []
    external_links_checked = 0
    affiliate_links_checked = 0
    resources_page = is_resources_path(path)
    for anchor in assets.anchors:
        href = anchor.get("href", "")
        parsed = urlparse(href)
        if parsed.scheme not in {"http", "https"} or parsed.hostname in LOCAL_HOSTS:
            continue
        external_links_checked += 1
        rel_tokens = set(anchor.get("rel", "").split())
        if anchor.get("target") == "_blank" and not {"noopener", "noreferrer"}.issubset(rel_tokens):
            issues.append(f"{path}: external _blank link missing noopener/noreferrer: {href}")
        if is_affiliate_host(parsed.hostname):
            affiliate_links_checked += 1
            if "sponsored" not in rel_tokens:
                issues.append(f"{path}: affiliate link missing sponsored rel: {href}")
            if not is_expected_affiliate_link(path, href):
                expected = "Books.com.tw tracking" if lang_for_path(path) == "zh" else f"Amazon tag={AMAZON_ASSOCIATE_TAG}"
                issues.append(f"{path}: affiliate link should use {expected}: {href}")
    if affiliate_links_checked:
        if AFFILIATE_DISCLOSURE_SNIPPET not in html and 'class="affiliate-disclosure"' not in html:
            issues.append(f"{path}: missing affiliate disclosure")
    if resources_page:
        if affiliate_links_checked < len(GUARDIAN_SLUGS):
            issues.append(f"{path}: expected at least {len(GUARDIAN_SLUGS)} affiliate links, found {affiliate_links_checked}")
    return issues, external_links_checked, affiliate_links_checked


def header_matches(headers: dict[str, str], name: str, expected: str) -> bool:
    return headers.get(name, "") == expected


def check_global_headers(path: str, response: Response) -> list[str]:
    issues: list[str] = []
    for name, expected in REQUIRED_GLOBAL_HEADERS.items():
        if not header_matches(response.headers, name, expected):
            issues.append(f"{path}: header {name} should be {expected!r}, got {response.headers.get(name, '')!r}")
    return issues


def content_type(response: Response) -> str:
    return response.headers.get("content-type", "").split(";", 1)[0].strip().lower()


def expected_asset_content_type(path: str) -> str | None:
    if path.endswith(".css"):
        return "text/css"
    if path.endswith(".js"):
        return "javascript"
    return None


def check_static_asset_response(path: str, response: Response) -> list[str]:
    issues: list[str] = []
    expected = expected_asset_content_type(path)
    actual = content_type(response)
    if expected == "javascript":
        if actual not in {"text/javascript", "application/javascript"}:
            issues.append(f"{path}: expected JavaScript content type, got {response.headers.get('content-type', '')!r}")
    elif expected and actual != expected:
        issues.append(f"{path}: expected content type {expected!r}, got {response.headers.get('content-type', '')!r}")
    return issues


def check_social_image_response(image_url: str, response: Response) -> tuple[list[str], bool]:
    issues: list[str] = []
    actual = content_type(response)
    if not actual.startswith("image/"):
        issues.append(f"{image_url}: expected image content type, got {response.headers.get('content-type', '')!r}")
    parsed = urlparse(image_url)
    requires_immutable = parsed.path.startswith("/assets/")
    if requires_immutable:
        cache_control = response.headers.get("cache-control", "")
        if not IMMUTABLE_CACHE_RE.search(cache_control):
            issues.append(f"{image_url}: expected immutable cache header, got {cache_control!r}")
    return issues, requires_immutable


def check_text_support_file(path: str, response: Response, required_snippets: list[str]) -> list[str]:
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"]
    if path != "/robots.txt":
        issues.extend(check_global_headers(path, response))
    for snippet in required_snippets:
        if snippet not in response.text:
            issues.append(f"{path}: missing required text {snippet!r}")
    return issues


def check_sitemap(response: Response) -> tuple[list[str], int, int, int]:
    path = "/sitemap.xml"
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], 0, 0, 0
    issues.extend(check_global_headers(path, response))
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [f"{path}: invalid XML: {error}"], 0, 0, 0
    urls = root.findall("sm:url", SITEMAP_NS)
    locs = [node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) for node in urls]
    url_nodes_by_loc = {loc: node for loc, node in zip(locs, urls)}
    if len(locs) < 140:
        issues.append(f"{path}: expected at least 140 sitemap URLs, found {len(locs)}")
    total_alternates = sum(len(node.findall("xhtml:link", SITEMAP_NS)) for node in urls)
    checked_alternates = 0
    for expected in (public_url_for_path(path) for path in PUBLIC_PATHS):
        if expected not in locs:
            issues.append(f"{path}: missing sitemap URL {expected}")
            continue
        url_node = url_nodes_by_loc[expected]
        alternates = url_node.findall("xhtml:link", SITEMAP_NS)
        checked_alternates += len(alternates)
        alternate_map: dict[str, str] = {}
        duplicate_hreflangs: list[str] = []
        for alternate in alternates:
            if alternate.attrib.get("rel") != "alternate":
                issues.append(f"{path}: sitemap alternate rel should be alternate for {expected}")
            lang = alternate.attrib.get("hreflang", "")
            href = alternate.attrib.get("href", "")
            if lang in alternate_map:
                duplicate_hreflangs.append(lang)
            alternate_map[lang] = href
        expected_hreflangs = expected_hreflang_map(path_from_url(expected))
        missing_hreflangs = sorted(set(EXPECTED_HREFLANGS).difference(alternate_map))
        extra_hreflangs = sorted(set(alternate_map).difference(EXPECTED_HREFLANGS))
        if missing_hreflangs:
            issues.append(f"{path}: {expected} missing sitemap hreflang links {', '.join(missing_hreflangs)}")
        if extra_hreflangs:
            issues.append(f"{path}: {expected} unexpected sitemap hreflang links {', '.join(extra_hreflangs)}")
        if duplicate_hreflangs:
            issues.append(f"{path}: {expected} duplicate sitemap hreflang links {', '.join(sorted(set(duplicate_hreflangs)))}")
        for lang, expected_href in expected_hreflangs.items():
            actual_href = alternate_map.get(lang)
            if actual_href and actual_href != expected_href:
                issues.append(f"{path}: {expected} sitemap hreflang {lang} should be {expected_href!r}, got {actual_href!r}")
    return issues, len(locs), total_alternates, checked_alternates


def check_feed(response: Response) -> list[str]:
    path = "/feed.xml"
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"]
    issues.extend(check_global_headers(path, response))
    try:
        root = ET.fromstring(response.body)
    except ET.ParseError as error:
        return [f"{path}: invalid XML: {error}"]
    if root.tag != "rss" or root.attrib.get("version") != "2.0":
        issues.append(f"{path}: expected RSS 2.0 root")
    items = root.findall("./channel/item")
    if len(items) < 10:
        issues.append(f"{path}: expected at least 10 feed items, found {len(items)}")
    channel_link = root.findtext("./channel/link", default="")
    if channel_link != "https://lovetypes.tw/guides/":
        issues.append(f"{path}: channel link should be https://lovetypes.tw/guides/, got {channel_link!r}")
    return issues


def extract_head_assets(html: str) -> HeadAssetParser:
    parser = HeadAssetParser()
    parser.feed(html)
    return parser


def unique_assets(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def localized_page_from_home(home_path: str, route: str) -> str:
    prefix = home_path.strip("/")
    route = route.strip("/")
    return f"/{prefix}/{route}/" if prefix else f"/{route}/"


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke check a deployed LoveTypes public site.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    pages_checked = 0
    redirects_checked = 0
    not_found_checked = 0
    support_files_checked = 0
    immutable_assets_checked = 0
    public_canonicals_checked = 0
    public_robots_checked = 0
    public_lang_checked = 0
    public_hreflang_sets_checked = 0
    public_hreflang_links_checked = 0
    public_social_meta_checked = 0
    public_jsonld_blocks_checked = 0
    public_jsonld_entities_checked = 0
    public_versioned_asset_refs_checked = 0
    public_current_asset_refs_checked = 0
    public_quiz_data_asset_refs_checked = 0
    public_sitemap_urls_checked = 0
    public_sitemap_alternates_total = 0
    public_sitemap_alternates_checked = 0
    public_anchor_targets_checked = 0
    public_conversion_hrefs_checked = 0
    public_external_links_checked = 0
    public_affiliate_links_checked = 0
    public_home_universe_gate_sections_checked = 0
    public_home_universe_gate_cards_checked = 0
    public_home_safety_sections_checked = 0
    public_home_safety_links_checked = 0
    public_characters_universe_map_sections_checked = 0
    public_characters_universe_map_cards_checked = 0
    public_garden_map_sections_checked = 0
    public_garden_map_guardian_cards_checked = 0
    public_garden_map_guide_cards_checked = 0
    public_garden_map_route_cards_checked = 0
    public_supply_safety_sections_checked = 0
    public_supply_starter_cards_checked = 0
    public_supply_wishlist_cards_checked = 0
    public_social_images_checked = 0
    public_social_immutable_images_checked = 0
    page_asset_refs: list[str] = []
    social_image_urls: list[str] = []

    for path in PUBLIC_PATHS:
        response = request_url(urljoin(base_url, path))
        pages_checked += 1
        if response.status != 200:
            issues.append(f"{path}: expected status 200, got {response.status}")
            continue
        final_path = path_from_url(response.url)
        if final_path.rstrip("/") != path.rstrip("/"):
            issues.append(f"{path}: expected final path {path}, got {final_path}")
        issues.extend(check_global_headers(path, response))
        expected_text = EXPECTED_TEXT.get(path)
        if expected_text and expected_text not in response.text:
            issues.append(f"{path}: missing expected text {expected_text!r}")
        if path in {"/", "/en/", "/ja/", "/ko/", "/es/"}:
            public_home_universe_gate_sections_checked += 1
            if "data-universe-gates" not in response.text:
                issues.append(f"{path}: missing home five-domain universe gate section")
            universe_gate_count = response.text.count('class="universe-gate-card"')
            public_home_universe_gate_cards_checked += universe_gate_count
            if universe_gate_count != HOME_EXPECTED_UNIVERSE_GATE_CARDS:
                issues.append(
                    f"{path}: expected {HOME_EXPECTED_UNIVERSE_GATE_CARDS} universe gate cards, found {universe_gate_count}"
                )
            public_home_safety_sections_checked += 1
            if "data-home-safety-compass" not in response.text:
                issues.append(f"{path}: missing home safety compass")
            for expected_href in (
                localized_page_from_home(path, "privacy"),
                localized_page_from_home(path, "terms"),
                localized_page_from_home(path, "contact") + "#site-repair-report",
            ):
                public_home_safety_links_checked += 1
                if f'href="{expected_href}"' not in response.text:
                    issues.append(f"{path}: home safety compass missing {expected_href}")
        if path in {"/characters/", "/en/characters/", "/ja/characters/", "/ko/characters/", "/es/characters/"}:
            public_characters_universe_map_sections_checked += 1
            if "data-universe-map" not in response.text:
                issues.append(f"{path}: missing characters five-domain universe map section")
            guardian_card_count = response.text.count('class="guardian-card"')
            public_characters_universe_map_cards_checked += guardian_card_count
            if guardian_card_count != CHARACTERS_EXPECTED_UNIVERSE_MAP_CARDS:
                issues.append(
                    f"{path}: expected {CHARACTERS_EXPECTED_UNIVERSE_MAP_CARDS} guardian map cards, found {guardian_card_count}"
                )
        if path in GARDEN_MAP_PATHS:
            for marker in GARDEN_MAP_SECTION_MARKERS:
                public_garden_map_sections_checked += 1
                if marker not in response.text:
                    issues.append(f"{path}: missing garden map section marker {marker}")
            garden_guardian_card_count = response.text.count('class="guardian-card"')
            public_garden_map_guardian_cards_checked += garden_guardian_card_count
            if garden_guardian_card_count != GARDEN_MAP_EXPECTED_GUARDIAN_CARDS:
                issues.append(
                    f"{path}: expected {GARDEN_MAP_EXPECTED_GUARDIAN_CARDS} garden map guardian cards, found {garden_guardian_card_count}"
                )
            garden_guide_card_count = response.text.count('class="content-card"')
            public_garden_map_guide_cards_checked += garden_guide_card_count
            if garden_guide_card_count != GARDEN_MAP_EXPECTED_GUIDE_CARDS:
                issues.append(
                    f"{path}: expected {GARDEN_MAP_EXPECTED_GUIDE_CARDS} garden map guide cards, found {garden_guide_card_count}"
                )
            garden_route_card_count = response.text.count('class="garden-map-route-card"')
            public_garden_map_route_cards_checked += garden_route_card_count
            if garden_route_card_count != GARDEN_MAP_EXPECTED_ROUTE_CARDS:
                issues.append(
                    f"{path}: expected {GARDEN_MAP_EXPECTED_ROUTE_CARDS} garden map route cards, found {garden_route_card_count}"
                )
        if path.endswith("/resources/"):
            for label, marker in RESOURCE_SUPPLY_SAFETY_MARKERS:
                public_supply_safety_sections_checked += 1
                if marker not in response.text:
                    issues.append(f"{path}: missing resource conversion safety marker {label}")
            starter_card_count = response.text.count('class="starter-kit-card"')
            public_supply_starter_cards_checked += starter_card_count
            if starter_card_count != RESOURCE_EXPECTED_STARTER_CARDS:
                issues.append(
                    f"{path}: expected {RESOURCE_EXPECTED_STARTER_CARDS} starter kit cards, found {starter_card_count}"
                )
            wishlist_card_count = response.text.count("data-supply-owned-card")
            public_supply_wishlist_cards_checked += wishlist_card_count
            if wishlist_card_count != RESOURCE_EXPECTED_WISHLIST_CARDS:
                issues.append(
                    f"{path}: expected {RESOURCE_EXPECTED_WISHLIST_CARDS} owned supply wishlist cards, found {wishlist_card_count}"
                )
        assets = extract_head_assets(response.text)
        external_issues, external_links_checked, affiliate_links_checked = check_external_links(path, assets, response.text)
        issues.extend(external_issues)
        public_external_links_checked += external_links_checked
        public_affiliate_links_checked += affiliate_links_checked
        for target_id in EXPECTED_ANCHOR_TARGETS.get(path, ()):
            public_anchor_targets_checked += 1
            if target_id not in assets.ids:
                issues.append(f"{path}: missing expected anchor target #{target_id}")
        for href in EXPECTED_HREF_TARGETS.get(path, ()):
            public_conversion_hrefs_checked += 1
            if href not in assets.hrefs:
                issues.append(f"{path}: missing expected conversion href {href}")
        public_canonicals_checked += 1
        expected_canonical_url = expected_canonical(path)
        if assets.canonical != expected_canonical_url:
            issues.append(f"{path}: canonical should be {expected_canonical_url!r}, got {assets.canonical!r}")
        social_issues, page_social_images, social_checked = check_social_metadata(path, assets, expected_canonical_url)
        issues.extend(social_issues)
        social_image_urls.extend(page_social_images)
        public_social_meta_checked += social_checked
        jsonld_issues, jsonld_blocks_checked, jsonld_entities_checked = check_jsonld(path, assets)
        issues.extend(jsonld_issues)
        public_jsonld_blocks_checked += jsonld_blocks_checked
        public_jsonld_entities_checked += jsonld_entities_checked
        public_robots_checked += 1
        robots_tokens = {token.strip().lower() for token in assets.robots.split(",") if token.strip()}
        if "noindex" in robots_tokens:
            issues.append(f"{path}: public smoke page should not be noindex")
        if "index" not in robots_tokens or "follow" not in robots_tokens:
            issues.append(f"{path}: robots should include index, follow; got {assets.robots!r}")
        public_lang_checked += 1
        expected_lang = expected_html_lang(path)
        if assets.html_lang != expected_lang:
            issues.append(f"{path}: html lang should be {expected_lang!r}, got {assets.html_lang!r}")

        public_hreflang_sets_checked += 1
        hreflang_map: dict[str, str] = {}
        duplicate_hreflangs: list[str] = []
        for lang, href in assets.hreflang_links:
            if lang in hreflang_map:
                duplicate_hreflangs.append(lang)
            hreflang_map[lang] = href
        public_hreflang_links_checked += len(assets.hreflang_links)
        expected_hreflangs = expected_hreflang_map(path)
        missing_hreflangs = sorted(set(EXPECTED_HREFLANGS).difference(hreflang_map))
        extra_hreflangs = sorted(set(hreflang_map).difference(EXPECTED_HREFLANGS))
        if missing_hreflangs:
            issues.append(f"{path}: missing hreflang links {', '.join(missing_hreflangs)}")
        if extra_hreflangs:
            issues.append(f"{path}: unexpected hreflang links {', '.join(extra_hreflangs)}")
        if duplicate_hreflangs:
            issues.append(f"{path}: duplicate hreflang links {', '.join(sorted(set(duplicate_hreflangs)))}")
        for lang, expected_href in expected_hreflangs.items():
            actual_href = hreflang_map.get(lang)
            if actual_href and actual_href != expected_href:
                issues.append(f"{path}: hreflang {lang} should be {expected_href!r}, got {actual_href!r}")

        versioned_stylesheets = [href for href in assets.stylesheets if VERSIONED_CSS_RE.match(href)]
        versioned_interactions = [src for src in assets.scripts if VERSIONED_INTERACTIONS_RE.match(src)]
        versioned_affiliate = [src for src in assets.scripts if VERSIONED_AFFILIATE_RE.match(src)]
        versioned_quiz_data = [src for src in assets.scripts if VERSIONED_QUIZ_DATA_RE.match(src)]
        public_versioned_asset_refs_checked += (
            len(versioned_stylesheets)
            + len(versioned_interactions)
            + len(versioned_affiliate)
            + len(versioned_quiz_data)
        )
        if len(versioned_stylesheets) != 1:
            issues.append(f"{path}: expected one versioned shared CSS asset, found {versioned_stylesheets}")
        elif versioned_stylesheets[0] != CURRENT_STATIC_ASSETS["css"]:
            issues.append(
                f"{path}: expected current CSS asset {CURRENT_STATIC_ASSETS['css']}, found {versioned_stylesheets[0]}"
            )
        else:
            public_current_asset_refs_checked += 1
        if len(versioned_interactions) != 1:
            issues.append(f"{path}: expected one versioned interaction JS asset, found {versioned_interactions}")
        elif versioned_interactions[0] != CURRENT_STATIC_ASSETS["interactions"]:
            issues.append(
                f"{path}: expected current interaction asset {CURRENT_STATIC_ASSETS['interactions']}, found {versioned_interactions[0]}"
            )
        else:
            public_current_asset_refs_checked += 1
        expected_affiliate_count = 1 if path.endswith("/resources/") else 0
        if len(versioned_affiliate) != expected_affiliate_count:
            issues.append(f"{path}: expected {expected_affiliate_count} versioned affiliate JS asset(s), found {versioned_affiliate}")
        elif expected_affiliate_count and versioned_affiliate[0] != CURRENT_STATIC_ASSETS["affiliate"]:
            issues.append(
                f"{path}: expected current affiliate asset {CURRENT_STATIC_ASSETS['affiliate']}, found {versioned_affiliate[0]}"
            )
        elif expected_affiliate_count:
            public_current_asset_refs_checked += 1

        needs_quiz_data = any(marker in response.text for marker in QUIZ_DATA_REQUIRED_MARKERS)
        expected_quiz_data = [CURRENT_QUIZ_DATA_ASSETS[expected_quiz_lang(path)]] if needs_quiz_data else []
        public_quiz_data_asset_refs_checked += len(versioned_quiz_data)
        if versioned_quiz_data != expected_quiz_data:
            issues.append(f"{path}: expected quiz data assets {expected_quiz_data}, found {versioned_quiz_data}")
        elif expected_quiz_data:
            public_current_asset_refs_checked += 1

        if path.endswith("/contact/"):
            for marker in CONTACT_FUNNEL_MARKERS:
                if marker not in response.text:
                    issues.append(f"{path}: contact saved-result funnel marker missing {marker}")

        page_asset_refs.extend([*versioned_stylesheets, *versioned_interactions, *versioned_affiliate, *versioned_quiz_data])

    for source, target in REDIRECTS.items():
        cache_bust = "?cache-bust=public-deploy-smoke" if source.endswith((".webp", ".css")) else ""
        response = request_url(urljoin(base_url, source + cache_bust), follow_redirects=False)
        redirects_checked += 1
        location = response.headers.get("location", "")
        expected_location = urljoin(base_url, target)
        expected_locations = {target, expected_location}
        if cache_bust:
            expected_locations.update({target + cache_bust, expected_location + cache_bust})
        if response.status != 301:
            issues.append(f"{source}: expected 301 redirect, got {response.status}")
        if location not in expected_locations:
            issues.append(f"{source}: expected redirect to {target}, got {location!r}")

    not_found_response = request_url(urljoin(base_url, NOT_FOUND_PATH))
    not_found_checked += 1
    if not_found_response.status != 404:
        issues.append(f"{NOT_FOUND_PATH}: expected custom 404 status, got {not_found_response.status}")
    issues.extend(check_global_headers(NOT_FOUND_PATH, not_found_response))
    for snippet in NOT_FOUND_REQUIRED_TEXT:
        if snippet not in not_found_response.text:
            issues.append(f"{NOT_FOUND_PATH}: custom 404 missing required text {snippet!r}")

    for path, snippets in SUPPORT_FILES.items():
        response = request_url(urljoin(base_url, path))
        support_files_checked += 1
        issues.extend(check_text_support_file(path, response, snippets))

    sitemap_response = request_url(urljoin(base_url, "/sitemap.xml"))
    support_files_checked += 1
    sitemap_issues, sitemap_urls_checked, sitemap_alternates_total, sitemap_alternates_checked = check_sitemap(sitemap_response)
    issues.extend(sitemap_issues)
    public_sitemap_urls_checked = sitemap_urls_checked
    public_sitemap_alternates_total = sitemap_alternates_total
    public_sitemap_alternates_checked = sitemap_alternates_checked

    feed_response = request_url(urljoin(base_url, "/feed.xml"))
    support_files_checked += 1
    issues.extend(check_feed(feed_response))

    security_response = request_url(urljoin(base_url, "/security.txt"))
    well_known_security_response = request_url(urljoin(base_url, "/.well-known/security.txt"))
    if security_response.status == 200 and well_known_security_response.status == 200:
        if security_response.text != well_known_security_response.text:
            issues.append("/.well-known/security.txt: body should match /security.txt")

    for asset in unique_assets(page_asset_refs):
        response = request_url(urljoin(base_url, asset))
        immutable_assets_checked += 1
        cache_control = response.headers.get("cache-control", "")
        if response.status != 200:
            issues.append(f"{asset}: expected status 200, got {response.status}")
        if not IMMUTABLE_CACHE_RE.search(cache_control):
            issues.append(f"{asset}: expected immutable cache header, got {cache_control!r}")
        issues.extend(check_static_asset_response(asset, response))

    for image_url in unique_assets(social_image_urls):
        response = request_url(image_url)
        public_social_images_checked += 1
        if response.status != 200:
            issues.append(f"{image_url}: expected social image status 200, got {response.status}")
            continue
        image_issues, checked_immutable = check_social_image_response(image_url, response)
        issues.extend(image_issues)
        if checked_immutable:
            public_social_immutable_images_checked += 1

    print(f"public_pages_checked={pages_checked}")
    print(f"public_canonicals_checked={public_canonicals_checked}")
    print(f"public_robots_checked={public_robots_checked}")
    print(f"public_lang_checked={public_lang_checked}")
    print(f"public_hreflang_sets_checked={public_hreflang_sets_checked}")
    print(f"public_hreflang_links_checked={public_hreflang_links_checked}")
    print(f"public_social_meta_checked={public_social_meta_checked}")
    print(f"public_jsonld_blocks_checked={public_jsonld_blocks_checked}")
    print(f"public_jsonld_entities_checked={public_jsonld_entities_checked}")
    print(f"public_versioned_asset_refs_checked={public_versioned_asset_refs_checked}")
    print(f"public_current_asset_refs_checked={public_current_asset_refs_checked}")
    print(f"public_quiz_data_asset_refs_checked={public_quiz_data_asset_refs_checked}")
    print(f"public_sitemap_urls_checked={public_sitemap_urls_checked}")
    print(f"public_sitemap_alternates_total={public_sitemap_alternates_total}")
    print(f"public_sitemap_alternates_checked={public_sitemap_alternates_checked}")
    print(f"public_anchor_targets_checked={public_anchor_targets_checked}")
    print(f"public_conversion_hrefs_checked={public_conversion_hrefs_checked}")
    print(f"public_external_links_checked={public_external_links_checked}")
    print(f"public_affiliate_links_checked={public_affiliate_links_checked}")
    print(f"public_home_universe_gate_sections_checked={public_home_universe_gate_sections_checked}")
    print(f"public_home_universe_gate_cards_checked={public_home_universe_gate_cards_checked}")
    print(f"public_home_safety_sections_checked={public_home_safety_sections_checked}")
    print(f"public_home_safety_links_checked={public_home_safety_links_checked}")
    print(f"public_characters_universe_map_sections_checked={public_characters_universe_map_sections_checked}")
    print(f"public_characters_universe_map_cards_checked={public_characters_universe_map_cards_checked}")
    print(f"public_garden_map_sections_checked={public_garden_map_sections_checked}")
    print(f"public_garden_map_guardian_cards_checked={public_garden_map_guardian_cards_checked}")
    print(f"public_garden_map_guide_cards_checked={public_garden_map_guide_cards_checked}")
    print(f"public_garden_map_route_cards_checked={public_garden_map_route_cards_checked}")
    print(f"public_supply_safety_sections_checked={public_supply_safety_sections_checked}")
    print(f"public_supply_starter_cards_checked={public_supply_starter_cards_checked}")
    print(f"public_supply_wishlist_cards_checked={public_supply_wishlist_cards_checked}")
    print(f"public_social_images_checked={public_social_images_checked}")
    print(f"public_social_immutable_images_checked={public_social_immutable_images_checked}")
    print(f"public_redirects_checked={redirects_checked}")
    print(f"public_not_found_checked={not_found_checked}")
    print(f"public_support_files_checked={support_files_checked}")
    print(f"public_immutable_assets_checked={immutable_assets_checked}")
    print(f"public_deploy_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
