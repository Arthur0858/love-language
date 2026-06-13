#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import ssl
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
ACCEPTED_STATUSES = set(range(200, 400)) | {403, 405, 429}
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
AFFILIATE_HOSTS = {"www.books.com.tw", "www.amazon.com"}
AMAZON_ASSOCIATE_TAG = "parenttechche-20"
BOOKS_AFFILIATE_TOKENS = ("arthur0858", "utm_campaign=ap-202604")


@dataclass(frozen=True)
class ExternalLink:
    url: str
    source_paths: tuple[str, ...]


@dataclass
class ExternalLinkStats:
    anchors_checked: int = 0
    blank_target_rel_checked: int = 0
    affiliate_anchors_checked: int = 0
    affiliate_zh_books_links_checked: int = 0
    affiliate_non_zh_amazon_links_checked: int = 0
    affiliate_disclosure_pages_checked: int = 0


def load_public_deploy_smoke():
    module_path = ROOT / "tools" / "public_deploy_smoke.py"
    spec = importlib.util.spec_from_file_location("public_deploy_smoke_import", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_status(url: str, method: str = "HEAD") -> tuple[int, str]:
    context = ssl.create_default_context()
    request = Request(
        url,
        method=method,
        headers={
            "User-Agent": "LoveTypes external link smoke/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=20, context=context) as response:
            return response.status, response.geturl()
    except HTTPError as error:
        return error.code, error.geturl()
    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError(str(error)) from error


def resilient_status(url: str, attempts: int = 2) -> tuple[int, str]:
    last_error: RuntimeError | None = None
    for attempt in range(1, attempts + 1):
        for method in ("HEAD", "GET"):
            try:
                status, final_url = request_status(url, method=method)
                if status == 405 and method == "HEAD":
                    continue
                return status, final_url
            except RuntimeError as error:
                last_error = error
        if attempt < attempts:
            time.sleep(0.75 * attempt)
    assert last_error is not None
    raise last_error


def resource_lang(path: str) -> str:
    if path.startswith("/en/"):
        return "en"
    if path.startswith("/ja/"):
        return "ja"
    if path.startswith("/ko/"):
        return "ko"
    if path.startswith("/es/"):
        return "es"
    return "zh"


def rel_tokens(anchor: dict[str, str]) -> set[str]:
    return {token.strip().lower() for token in anchor.get("rel", "").split() if token.strip()}


def is_expected_affiliate_url(path: str, href: str) -> bool:
    parsed = urlparse(href)
    if resource_lang(path) == "zh":
        return parsed.hostname == "www.books.com.tw" and all(token in href for token in BOOKS_AFFILIATE_TOKENS)
    return (
        parsed.hostname == "www.amazon.com"
        and parsed.path.startswith("/dp/")
        and parse_qs(parsed.query).get("tag", [""])[0] == AMAZON_ASSOCIATE_TAG
    )


def collect_external_links(base_url: str) -> tuple[list[ExternalLink], ExternalLinkStats, list[str]]:
    smoke = load_public_deploy_smoke()
    generator = smoke.GENERATOR_CONFIG
    issues: list[str] = []
    stats = ExternalLinkStats()
    sources_by_url: dict[str, set[str]] = {}
    for path in smoke.PUBLIC_PATHS:
        response = smoke.request_url(urljoin(base_url + "/", path.lstrip("/")))
        assets = smoke.extract_head_assets(response.text)
        if path.endswith("/resources/"):
            expected_disclosure = generator.AFFILIATE_DISCLOSURE[resource_lang(path)]
            if expected_disclosure not in response.text:
                issues.append(f"{path}: missing localized affiliate disclosure")
            elif "affiliate-disclosure" not in response.text:
                issues.append(f"{path}: affiliate disclosure should use affiliate-disclosure class")
            else:
                stats.affiliate_disclosure_pages_checked += 1
            if "affiliate-link-note" not in response.text:
                issues.append(f"{path}: missing external bookstore fallback note")
        for anchor in assets.anchors:
            href = anchor.get("href", "")
            parsed = urlparse(href)
            if parsed.scheme not in {"http", "https"} or parsed.hostname in LOCAL_HOSTS:
                continue
            stats.anchors_checked += 1
            rel = rel_tokens(anchor)
            if anchor.get("target") != "_blank":
                issues.append(f"{path}: external link should open in a new tab: {href}")
            elif {"noopener", "noreferrer"}.issubset(rel):
                stats.blank_target_rel_checked += 1
            else:
                issues.append(f"{path}: external new-tab link should include noopener noreferrer: {href}")
            if parsed.hostname in AFFILIATE_HOSTS:
                if "sponsored" not in rel:
                    issues.append(f"{path}: affiliate link should include sponsored rel: {href}")
                else:
                    stats.affiliate_anchors_checked += 1
                if not is_expected_affiliate_url(path, href):
                    expected = "Books.com.tw tracking" if resource_lang(path) == "zh" else f"Amazon tag={AMAZON_ASSOCIATE_TAG}"
                    issues.append(f"{path}: affiliate link should use {expected}: {href}")
                elif resource_lang(path) == "zh":
                    stats.affiliate_zh_books_links_checked += 1
                else:
                    stats.affiliate_non_zh_amazon_links_checked += 1
            sources_by_url.setdefault(href, set()).add(path)
    return [
        ExternalLink(url=url, source_paths=tuple(sorted(source_paths)))
        for url, source_paths in sorted(sources_by_url.items())
    ], stats, issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that public external LoveTypes links are reachable.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    links, stats, safety_issues = collect_external_links(base_url)
    issues.extend(safety_issues)
    hosts: set[str] = set()
    affiliate_links_checked = 0

    for link in links:
        host = urlparse(link.url).hostname or ""
        hosts.add(host)
        if host in AFFILIATE_HOSTS:
            affiliate_links_checked += 1
        try:
            status, final_url = resilient_status(link.url)
        except RuntimeError as error:
            issues.append(f"{link.url}: request failed from {', '.join(link.source_paths)}: {error}")
            continue
        if status not in ACCEPTED_STATUSES:
            issues.append(f"{link.url}: expected reachable status, got {status} final={final_url}")

    print(f"public_external_anchors_checked={stats.anchors_checked}")
    print(f"public_external_blank_target_rel_checked={stats.blank_target_rel_checked}")
    print(f"public_external_unique_links_checked={len(links)}")
    print(f"public_external_hosts_checked={len(hosts)}")
    print(f"public_external_affiliate_links_checked={affiliate_links_checked}")
    print(f"public_external_affiliate_anchors_checked={stats.affiliate_anchors_checked}")
    print(f"public_external_affiliate_zh_books_links_checked={stats.affiliate_zh_books_links_checked}")
    print(f"public_external_affiliate_non_zh_amazon_links_checked={stats.affiliate_non_zh_amazon_links_checked}")
    print(f"public_external_affiliate_disclosure_pages_checked={stats.affiliate_disclosure_pages_checked}")
    print(f"public_external_link_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
