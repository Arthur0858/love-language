#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
VERSIONED_ROOT_ASSET_RE = re.compile(
    r"^/(shared-[^/]+\.css|site-interactions-[^/]+\.js|deferred-external-[^/]+\.js|quiz-data-(zh|en|ja|ko|es)-[^/]+\.js)$"
)


@dataclass
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class VersionedAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stylesheets: list[str] = []
        self.scripts: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "link" and data.get("href"):
            rel = set(data.get("rel", "").lower().split())
            if "stylesheet" in rel:
                self.stylesheets.append(data["href"])
        elif tag == "script" and data.get("src"):
            self.scripts.append(data)


def load_generator_config():
    generator_path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_site_generator_public_version", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load generator config from {generator_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR_CONFIG = load_generator_config()
CURRENT_CSS_ASSET = GENERATOR_CONFIG.CSS_ASSET
CURRENT_INTERACTIONS_ASSET = GENERATOR_CONFIG.INTERACTIONS_ASSET
CURRENT_AFFILIATE_ASSET = GENERATOR_CONFIG.AFFILIATE_ASSET
CURRENT_QUIZ_DATA_ASSETS = GENERATOR_CONFIG.QUIZ_DATA_ASSETS
CURRENT_VERSIONED_ASSETS = {
    CURRENT_CSS_ASSET,
    CURRENT_INTERACTIONS_ASSET,
    CURRENT_AFFILIATE_ASSET,
    *CURRENT_QUIZ_DATA_ASSETS.values(),
}


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public versioned asset smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                headers = {key.lower(): value for key, value in raw.headers.items()}
                return Response(raw.geturl(), raw.status, headers, raw.read())
        except HTTPError as error:
            headers = {key.lower(): value for key, value in error.headers.items()}
            return Response(error.geturl(), error.code, headers, error.read())
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def sitemap_locations(base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.body)
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
    return sorted(set(locations)), issues


def public_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    return path if path.endswith("/") or "." in path.rsplit("/", 1)[-1] else f"{path}/"


def loc_to_base_url(base_url: str, loc: str) -> str:
    parsed = urlparse(loc)
    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return urljoin(base_url + "/", path.lstrip("/") + query)


def public_asset_path(raw: str, page_url: str) -> str:
    parsed = urlparse(urljoin(page_url, raw))
    return parsed.path or "/"


def locale_for_path(path: str) -> str:
    first = path.strip("/").split("/", 1)[0]
    if first in {"en", "ja", "ko", "es"}:
        return first
    return "zh"


def is_home_path(path: str) -> bool:
    stripped = path.strip("/")
    return stripped in {"", "en", "ja", "ko", "es"}


def is_resources_path(path: str) -> bool:
    parts = [part for part in path.strip("/").split("/") if part]
    if parts and parts[0] in {"en", "ja", "ko", "es"}:
        parts = parts[1:]
    return parts == ["resources"]


def check_page(url: str) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "css_refs": 0,
        "interaction_refs": 0,
        "affiliate_refs": 0,
        "quiz_data_refs": 0,
        "versioned_refs": 0,
        "stale_versioned_refs": 0,
    }
    response = request_url(url)
    path = public_path(response.url)
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats

    parser = VersionedAssetParser()
    parser.feed(response.text)
    stylesheet_paths = [public_asset_path(href, response.url) for href in parser.stylesheets]
    script_paths = [public_asset_path(script["src"], response.url) for script in parser.scripts]

    css_refs = [path for path in stylesheet_paths if path.startswith("/shared-")]
    stats["css_refs"] = len(css_refs)
    if css_refs != [CURRENT_CSS_ASSET]:
        issues.append(f"{path}: expected current CSS {CURRENT_CSS_ASSET}, found {css_refs}")

    interaction_refs = [path for path in script_paths if path.startswith("/site-interactions-")]
    stats["interaction_refs"] = len(interaction_refs)
    if interaction_refs != [CURRENT_INTERACTIONS_ASSET]:
        issues.append(f"{path}: expected current interactions {CURRENT_INTERACTIONS_ASSET}, found {interaction_refs}")

    affiliate_refs = [path for path in script_paths if path.startswith("/deferred-external-")]
    expected_affiliate_refs = [CURRENT_AFFILIATE_ASSET] if is_resources_path(path) else []
    stats["affiliate_refs"] = len(affiliate_refs)
    if affiliate_refs != expected_affiliate_refs:
        issues.append(f"{path}: expected affiliate asset {expected_affiliate_refs}, found {affiliate_refs}")

    quiz_refs = [path for path in script_paths if path.startswith("/quiz-data-")]
    current_locale_quiz_asset = CURRENT_QUIZ_DATA_ASSETS[locale_for_path(path)]
    expected_quiz_refs = [current_locale_quiz_asset] if quiz_refs or is_home_path(path) else []
    stats["quiz_data_refs"] = len(quiz_refs)
    if quiz_refs != expected_quiz_refs:
        issues.append(f"{path}: expected current locale quiz data asset {expected_quiz_refs}, found {quiz_refs}")

    versioned_refs = [
        asset_path
        for asset_path in [*stylesheet_paths, *script_paths]
        if VERSIONED_ROOT_ASSET_RE.match(asset_path)
    ]
    stats["versioned_refs"] = len(versioned_refs)
    stale_refs = sorted({asset_path for asset_path in versioned_refs if asset_path not in CURRENT_VERSIONED_ASSETS})
    stats["stale_versioned_refs"] = len(stale_refs)
    if stale_refs:
        issues.append(f"{path}: stale versioned root assets found: {stale_refs}")

    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that public pages reference the current versioned LoveTypes assets.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    locations, issues = sitemap_locations(base_url)
    totals = {
        "pages": 0,
        "css_refs": 0,
        "interaction_refs": 0,
        "affiliate_refs": 0,
        "quiz_data_refs": 0,
        "versioned_refs": 0,
        "stale_versioned_refs": 0,
    }

    for loc in locations:
        page_issues, page_stats = check_page(loc_to_base_url(base_url, loc))
        issues.extend(page_issues)
        totals["pages"] += 1
        for key, value in page_stats.items():
            totals[key] += value

    print(f"public_versioned_asset_pages_checked={totals['pages']}")
    print(f"public_versioned_asset_css_refs_checked={totals['css_refs']}")
    print(f"public_versioned_asset_interaction_refs_checked={totals['interaction_refs']}")
    print(f"public_versioned_asset_affiliate_refs_checked={totals['affiliate_refs']}")
    print(f"public_versioned_asset_quiz_data_refs_checked={totals['quiz_data_refs']}")
    print(f"public_versioned_asset_root_refs_checked={totals['versioned_refs']}")
    print(f"public_versioned_asset_stale_refs={totals['stale_versioned_refs']}")
    print(f"public_versioned_asset_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
