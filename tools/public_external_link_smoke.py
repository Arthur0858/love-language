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
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
ACCEPTED_STATUSES = set(range(200, 400)) | {403, 405, 429}
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}


@dataclass(frozen=True)
class ExternalLink:
    url: str
    source_paths: tuple[str, ...]


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


def collect_external_links(base_url: str) -> list[ExternalLink]:
    smoke = load_public_deploy_smoke()
    sources_by_url: dict[str, set[str]] = {}
    for path in smoke.PUBLIC_PATHS:
        response = smoke.request_url(urljoin(base_url + "/", path.lstrip("/")))
        assets = smoke.extract_head_assets(response.text)
        for anchor in assets.anchors:
            href = anchor.get("href", "")
            parsed = urlparse(href)
            if parsed.scheme not in {"http", "https"} or parsed.hostname in LOCAL_HOSTS:
                continue
            sources_by_url.setdefault(href, set()).add(path)
    return [
        ExternalLink(url=url, source_paths=tuple(sorted(source_paths)))
        for url, source_paths in sorted(sources_by_url.items())
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that public external LoveTypes links are reachable.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    links = collect_external_links(base_url)
    hosts: set[str] = set()
    affiliate_links_checked = 0

    for link in links:
        host = urlparse(link.url).hostname or ""
        hosts.add(host)
        if host == "www.books.com.tw":
            affiliate_links_checked += 1
        try:
            status, final_url = resilient_status(link.url)
        except RuntimeError as error:
            issues.append(f"{link.url}: request failed from {', '.join(link.source_paths)}: {error}")
            continue
        if status not in ACCEPTED_STATUSES:
            issues.append(f"{link.url}: expected reachable status, got {status} final={final_url}")

    print(f"public_external_unique_links_checked={len(links)}")
    print(f"public_external_hosts_checked={len(hosts)}")
    print(f"public_external_affiliate_links_checked={affiliate_links_checked}")
    print(f"public_external_link_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
