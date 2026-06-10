#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {"zh": "/", "en": "/en/", "ja": "/ja/", "ko": "/ko/", "es": "/es/"}
EXPECTED_SLUGS = {"iris", "noah", "vivian", "claire", "dora"}
REQUIRED_RESULT_URLS = (
    "guardianUrl",
    "guideUrl",
    "resourceUrl",
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
AFFILIATE_TOKENS = ("arthur0858", "utm_campaign=ap-202604")
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "script" and data.get("src"):
            self.scripts.append(data["src"])
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


def is_affiliate_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == AFFILIATE_HOST and all(token in value for token in AFFILIATE_TOKENS)


def is_supply_request(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme != "mailto" or parsed.path != "contact@lovetypes.tw":
        return False
    return "subject=" in parsed.query and "body=" in parsed.query


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
    if not isinstance(book_url, str) or not is_affiliate_url(book_url):
        issues.append(f"{source}: supplyBookUrl should be a tracked books.com.tw affiliate URL")
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
        if not isinstance(items, list) or len(items) != 3:
            issues.append(f"{source}: supplyProductPack should contain three product paths")
        else:
            hrefs = [item.get("href", "") for item in items if isinstance(item, dict)]
            expected_internal = ("/keepsakes/#keepsake-card-", "/luna-yoga-music/#luna-")
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
