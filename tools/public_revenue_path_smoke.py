#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {"zh": "/", "en": "/en/", "ja": "/ja/", "ko": "/ko/", "es": "/es/"}
EXPECTED_SLUGS = {"iris", "noah", "vivian", "claire", "dora"}
REQUIRED_RESULT_URLS = (
    "guardianUrl",
    "guideUrl",
    "resourceUrl",
    "contactUrl",
    "lunaUrl",
    "collectorHallUrl",
    "planUrl",
)
REQUIRED_RESULT_TEXT = (
    "supplyTitle",
    "supplyDesc",
    "supplyMission",
    "supplyText",
    "supplyBook",
    "planLabel",
    "collectorTitle",
)
AFFILIATE_HOST = "www.books.com.tw"
AMAZON_HOST = "www.amazon.com"
AMAZON_ASSOCIATE_TAG = "parenttechche-20"
AFFILIATE_TOKENS = ("arthur0858", "utm_campaign=ap-202604")
GUMROAD_HOST = "lunayogamusic.gumroad.com"
EXPECTED_LUNA_PRODUCTS = {
    "healing-vibes-starter",
    "sleep-deep-rest",
    "morning-awakening",
    "stress-relief-yin",
    "feminine-healing",
    "luna-flow-sessions",
}
QUIZ_SRC_RE = re.compile(r"^/quiz-data-(zh|en|ja|ko|es)-[^/]+\.js$")
ASSIGNMENT_RE = re.compile(r"window\.__LOVETYPES_QUIZ_DATA\s*=\s*(\{.*\})\s*;?\s*$", re.S)


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    text: str


class ScriptAndIdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []
        self.ids: set[str] = set()
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "script" and data.get("src"):
            self.scripts.append(data["src"])
        if tag == "a" and data.get("href"):
            self.links.append(data)
        if data.get("id"):
            self.ids.add(data["id"])


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "LoveTypes public revenue path smoke/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/javascript,*/*;q=0.8",
                },
            )
            with urlopen(request, timeout=20) as raw:
                return Response(raw.geturl(), raw.status, raw.read().decode("utf-8", errors="replace"))
        except HTTPError as error:
            return Response(error.geturl(), error.code, error.read().decode("utf-8", errors="replace"))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def parse_html(text: str) -> ScriptAndIdParser:
    parser = ScriptAndIdParser()
    parser.feed(text)
    return parser


def discover_quiz_asset(base_url: str, lang: str, path: str) -> tuple[str, list[str]]:
    issues: list[str] = []
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    if response.status != 200:
        return "", [f"{path}: expected status 200, got {response.status}"]
    parser = parse_html(response.text)
    matches = [src for src in parser.scripts if QUIZ_SRC_RE.match(src)]
    expected_prefix = f"/quiz-data-{lang}-"
    localized = [src for src in matches if src.startswith(expected_prefix)]
    if len(localized) != 1:
        issues.append(f"{path}: expected one {expected_prefix} quiz asset, got {len(localized)}")
        return "", issues
    return localized[0], issues


def load_quiz_data(base_url: str, asset_src: str) -> tuple[dict, list[str]]:
    response = request_url(urljoin(base_url + "/", asset_src.lstrip("/")))
    if response.status != 200:
        return {}, [f"{asset_src}: expected status 200, got {response.status}"]
    match = ASSIGNMENT_RE.search(response.text)
    if not match:
        return {}, [f"{asset_src}: missing window.__LOVETYPES_QUIZ_DATA assignment"]
    try:
        return json.loads(match.group(1)), []
    except json.JSONDecodeError as error:
        return {}, [f"{asset_src}: invalid quiz JSON: {error}"]


def is_internal_url(value: str) -> bool:
    parsed = urlparse(value)
    return not parsed.scheme and value.startswith("/")


def is_affiliate_url(value: str, lang: str = "zh") -> bool:
    parsed = urlparse(value)
    if lang == "zh":
        return parsed.scheme == "https" and parsed.hostname == AFFILIATE_HOST and all(token in value for token in AFFILIATE_TOKENS)
    return (
        parsed.scheme == "https"
        and parsed.hostname == AMAZON_HOST
        and parsed.path.startswith("/dp/")
        and parse_qs(parsed.query).get("tag", [""])[0] == AMAZON_ASSOCIATE_TAG
    )


def is_supply_request(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme != "mailto" or parsed.path != "contact@lovetypes.tw":
        return False
    return "subject=" in parsed.query and "body=" in parsed.query


def is_gumroad_product_link(link: dict[str, str], expected_event: str = "luna_gumroad_pack_click") -> bool:
    href = link.get("href", "")
    parsed = urlparse(href)
    product_slug = link.get("data-luna-product", "")
    if parsed.scheme != "https" or parsed.netloc != GUMROAD_HOST:
        return False
    if product_slug not in EXPECTED_LUNA_PRODUCTS:
        return False
    query = parse_qs(parsed.query)
    return (
        query.get("utm_source", [""])[0] == "lovetypes"
        and query.get("utm_medium", [""])[0] == "luna-page"
        and query.get("utm_campaign", [""])[0] == "luna_gumroad_offer"
        and query.get("utm_content", [""])[0] == product_slug
        and link.get("data-funnel-event") == expected_event
        and "sponsored" in link.get("rel", "").split()
    )


def is_gumroad_starter_href(value: str) -> bool:
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    return (
        parsed.scheme == "https"
        and parsed.netloc == GUMROAD_HOST
        and "/l/healing-vibes-starter" in parsed.path
        and query.get("utm_source", [""])[0] == "lovetypes"
        and query.get("utm_medium", [""])[0] == "luna-page"
        and query.get("utm_campaign", [""])[0] == "luna_gumroad_offer"
        and query.get("utm_content", [""])[0] == "healing-vibes-starter"
    )


def validate_target(base_url: str, source: str, value: str, cache: dict[str, tuple[int, set[str]]]) -> list[str]:
    issues: list[str] = []
    path, fragment = urldefrag(value)
    if path not in cache:
        response = request_url(urljoin(base_url + "/", path.lstrip("/")))
        parser = parse_html(response.text)
        cache[path] = (response.status, parser.ids)
    status, ids = cache[path]
    if status != 200:
        issues.append(f"{source}: {value} expected status 200, got {status}")
    if fragment and fragment not in ids:
        issues.append(f"{source}: {value} missing target id #{fragment}")
    return issues


def validate_result(base_url: str, lang: str, result_key: str, result: dict, cache: dict[str, tuple[int, set[str]]]) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "result_url_fields": 0,
        "result_text_fields": 0,
        "internal_targets": 0,
        "affiliate_links": 0,
        "starter_kits": 0,
        "supply_product_packs": 0,
    }
    source = f"{lang}:{result_key}"
    slug = result.get("slug", "")
    if slug not in EXPECTED_SLUGS:
        issues.append(f"{source}: unexpected slug {slug!r}")
    for key in REQUIRED_RESULT_TEXT:
        if not isinstance(result.get(key), str) or not result[key].strip():
            issues.append(f"{source}: missing {key}")
        else:
            stats["result_text_fields"] += 1
    for key in REQUIRED_RESULT_URLS:
        value = result.get(key, "")
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{source}: missing {key}")
            continue
        if not is_internal_url(value):
            issues.append(f"{source}: {key} should be an internal URL, got {value!r}")
            continue
        stats["result_url_fields"] += 1
        stats["internal_targets"] += 1
        issues.extend(validate_target(base_url, f"{source}:{key}", value, cache))
    book_url = result.get("supplyBookUrl", "")
    if not isinstance(book_url, str) or not is_affiliate_url(book_url, lang):
        expected = "tracked Books.com.tw affiliate URL" if lang == "zh" else f"Amazon affiliate URL with tag={AMAZON_ASSOCIATE_TAG}"
        issues.append(f"{source}: supplyBookUrl should be a {expected}")
    else:
        stats["affiliate_links"] += 1
    starter = result.get("starterKit")
    if not isinstance(starter, dict):
        issues.append(f"{source}: missing starterKit")
    else:
        missing_text = [key for key in ("title", "intro") if not isinstance(starter.get(key), str) or not starter[key].strip()]
        steps = starter.get("steps")
        if missing_text:
            issues.append(f"{source}: starterKit missing {', '.join(missing_text)}")
        if not isinstance(steps, list) or len(steps) != 4:
            issues.append(f"{source}: starterKit should contain four next-step cards")
        else:
            starter_issue_count = len(issues)
            hrefs = [step.get("href", "") for step in steps if isinstance(step, dict)]
            expected_fragments = ("/keepsakes/", "/repair-plan/", "/luna-yoga-music/", "/resources/#supply-")
            for fragment in expected_fragments:
                if not any(fragment in href for href in hrefs):
                    issues.append(f"{source}: starterKit missing route containing {fragment}")
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    issues.append(f"{source}: starterKit step {index} should be an object")
                    continue
                for key in ("title", "desc", "action", "href"):
                    if not isinstance(step.get(key), str) or not step[key].strip():
                        issues.append(f"{source}: starterKit step {index} missing {key}")
            if len(issues) == starter_issue_count and not missing_text:
                stats["starter_kits"] += 1
    pack = result.get("supplyProductPack")
    if not isinstance(pack, dict):
        issues.append(f"{source}: missing supplyProductPack")
    else:
        pack_issue_count = len(issues)
        for key in ("label", "note"):
            if not isinstance(pack.get(key), str) or not pack[key].strip():
                issues.append(f"{source}: supplyProductPack missing {key}")
        items = pack.get("items")
        if not isinstance(items, list) or len(items) != 4:
            issues.append(f"{source}: supplyProductPack should contain four product paths")
        else:
            hrefs = [item.get("href", "") for item in items if isinstance(item, dict)]
            expected_internal = ("/keepsakes/#keepsake-card-", "/luna-yoga-music/#luna-", "/contact/#luna-supply-request")
            for fragment in expected_internal:
                if not any(fragment in href for href in hrefs):
                    issues.append(f"{source}: supplyProductPack missing route containing {fragment}")
            if not any(is_supply_request(href) for href in hrefs):
                issues.append(f"{source}: supplyProductPack missing contact request mailto")
            for index, item in enumerate(items, start=1):
                if not isinstance(item, dict):
                    issues.append(f"{source}: supplyProductPack item {index} should be an object")
                    continue
                for key in ("number", "title", "desc", "href"):
                    if not isinstance(item.get(key), str) or not item[key].strip():
                        issues.append(f"{source}: supplyProductPack item {index} missing {key}")
        if len(issues) == pack_issue_count:
            stats["supply_product_packs"] += 1
    return issues, stats


def validate_luna_products(base_url: str) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "luna_pages": 0,
        "luna_product_links": 0,
        "luna_starter_links": 0,
        "luna_product_slugs": 0,
        "funnel_revenue_events": 0,
    }
    seen_product_slugs: set[str] = set()
    for lang in LANG_PATHS:
        prefix = "" if lang == "zh" else f"/{lang}"
        path = f"{prefix}/luna-yoga-music/" if prefix else "/luna-yoga-music/"
        response = request_url(urljoin(base_url + "/", path.lstrip("/")))
        if response.status != 200:
            issues.append(f"{path}: expected status 200, got {response.status}")
            continue
        stats["luna_pages"] += 1
        parser = parse_html(response.text)
        product_links = [link for link in parser.links if link.get("data-funnel-event") == "luna_gumroad_pack_click"]
        starter_links = [link for link in parser.links if link.get("data-funnel-event") == "luna_starter_pack_click"]
        if len(product_links) != len(EXPECTED_LUNA_PRODUCTS):
            issues.append(f"{path}: expected {len(EXPECTED_LUNA_PRODUCTS)} Luna product links, got {len(product_links)}")
        if len(starter_links) != 1:
            issues.append(f"{path}: expected one Luna starter link, got {len(starter_links)}")
        page_slugs = {link.get("data-luna-product", "") for link in product_links}
        missing_slugs = sorted(EXPECTED_LUNA_PRODUCTS.difference(page_slugs))
        if missing_slugs:
            issues.append(f"{path}: missing Luna product slugs {', '.join(missing_slugs)}")
        for link in product_links:
            product_slug = link.get("data-luna-product", "")
            if not is_gumroad_product_link(link):
                issues.append(f"{path}: invalid Gumroad product revenue link for {product_slug or '<missing>'}: {link.get('href', '')}")
                continue
            seen_product_slugs.add(product_slug)
            stats["luna_product_links"] += 1
        for link in starter_links:
            if link.get("data-luna-product") != "healing-vibes-starter" or not is_gumroad_product_link(
                link, "luna_starter_pack_click"
            ):
                issues.append(f"{path}: invalid Gumroad starter revenue link: {link.get('href', '')}")
                continue
            stats["luna_starter_links"] += 1
    stats["luna_product_slugs"] = len(seen_product_slugs)

    funnel_response = request_url(urljoin(base_url + "/", "funnel-events.json"))
    if funnel_response.status != 200:
        issues.append(f"/funnel-events.json: expected status 200, got {funnel_response.status}")
    else:
        try:
            funnel_data = json.loads(funnel_response.text)
        except json.JSONDecodeError as error:
            issues.append(f"/funnel-events.json: invalid JSON: {error}")
        else:
            events = {event.get("name"): event for event in funnel_data.get("events", []) if isinstance(event, dict)}
            gumroad_event = events.get("luna_gumroad_pack_click", {})
            starter_event = events.get("luna_starter_pack_click", {})
            if gumroad_event.get("role") != "revenue":
                issues.append("/funnel-events.json: luna_gumroad_pack_click should be revenue")
            elif gumroad_event.get("count") != len(EXPECTED_LUNA_PRODUCTS) * len(LANG_PATHS):
                issues.append(
                    "/funnel-events.json: luna_gumroad_pack_click count should match product links "
                    f"{len(EXPECTED_LUNA_PRODUCTS) * len(LANG_PATHS)}, got {gumroad_event.get('count')}"
                )
            else:
                stats["funnel_revenue_events"] += 1
            if starter_event.get("role") != "revenue":
                issues.append("/funnel-events.json: luna_starter_pack_click should be revenue")
            elif starter_event.get("count") != len(LANG_PATHS):
                issues.append(
                    "/funnel-events.json: luna_starter_pack_click count should match starter links "
                    f"{len(LANG_PATHS)}, got {starter_event.get('count')}"
                )
            else:
                stats["funnel_revenue_events"] += 1
    return issues, stats


def run(base_url: str) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "pages_checked": 0,
        "quiz_assets_checked": 0,
        "results_checked": 0,
        "result_url_fields_checked": 0,
        "result_text_fields_checked": 0,
        "internal_targets_checked": 0,
        "affiliate_links_checked": 0,
        "starter_kits_checked": 0,
        "supply_product_packs_checked": 0,
        "quiz_luna_starter_templates_checked": 0,
        "luna_pages_checked": 0,
        "luna_product_links_checked": 0,
        "luna_starter_links_checked": 0,
        "luna_product_slugs_checked": 0,
        "funnel_revenue_events_checked": 0,
    }
    target_cache: dict[str, tuple[int, set[str]]] = {}
    for lang, path in LANG_PATHS.items():
        stats["pages_checked"] += 1
        asset_src, asset_issues = discover_quiz_asset(base_url, lang, path)
        issues.extend(asset_issues)
        if not asset_src:
            continue
        data, data_issues = load_quiz_data(base_url, asset_src)
        issues.extend(data_issues)
        if not data:
            continue
        stats["quiz_assets_checked"] += 1
        home_response = request_url(urljoin(base_url + "/", path.lstrip("/")))
        home_text = home_response.text
        starter_markers = (
            "data-quiz-luna-starter-link",
            "quiz_luna_starter_pack_click",
            "data-home-saved-luna-starter-link",
            "home_saved_luna_starter_pack_click",
            "https://lunayogamusic.gumroad.com/l/healing-vibes-starter",
            "utm_campaign=luna_gumroad_offer",
            "utm_content=healing-vibes-starter",
        )
        missing_starter_markers = [marker for marker in starter_markers if marker not in home_text]
        if missing_starter_markers:
            issues.append(f"{path}: missing quiz Luna starter markers {', '.join(missing_starter_markers)}")
        else:
            stats["quiz_luna_starter_templates_checked"] += 1
        results = data.get("results", {})
        if set(results) != {"W", "T", "G", "S", "P"}:
            issues.append(f"{lang}: expected five result keys W/T/G/S/P, got {sorted(results)}")
        for result_key, result in sorted(results.items()):
            if not isinstance(result, dict):
                issues.append(f"{lang}:{result_key}: result should be an object")
                continue
            stats["results_checked"] += 1
            result_issues, result_stats = validate_result(base_url, lang, result_key, result, target_cache)
            issues.extend(result_issues)
            stats["result_url_fields_checked"] += result_stats["result_url_fields"]
            stats["result_text_fields_checked"] += result_stats["result_text_fields"]
            stats["internal_targets_checked"] += result_stats["internal_targets"]
            stats["affiliate_links_checked"] += result_stats["affiliate_links"]
            stats["starter_kits_checked"] += result_stats["starter_kits"]
            stats["supply_product_packs_checked"] += result_stats["supply_product_packs"]
    luna_issues, luna_stats = validate_luna_products(base_url)
    issues.extend(luna_issues)
    stats["luna_pages_checked"] += luna_stats["luna_pages"]
    stats["luna_product_links_checked"] += luna_stats["luna_product_links"]
    stats["luna_starter_links_checked"] += luna_stats["luna_starter_links"]
    stats["luna_product_slugs_checked"] += luna_stats["luna_product_slugs"]
    stats["funnel_revenue_events_checked"] += luna_stats["funnel_revenue_events"]
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check LoveTypes public revenue and supply conversion paths.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    issues, stats = run(normalize_base_url(args.base_url))
    for key, value in stats.items():
        print(f"public_revenue_path_{key}={value}")
    print(f"public_revenue_path_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
