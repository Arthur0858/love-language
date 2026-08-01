#!/usr/bin/env python3
"""Verify the production editorial link graph, not only link reachability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from editorial_link_graph_audit import ROOT, analyze_graph, normalize_route, parse_main_links
from public_internal_link_smoke import fetch_many, is_html, normalize_base_url, sitemap_urls


DEFAULT_BASE_URL = "https://lovetypes.tw"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--site-index", type=Path, default=ROOT / "site-index.json")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    page_urls, issues = sitemap_urls(base_url)
    routes = {normalize_route(urlparse(url).path) for url in page_urls}
    local_index = json.loads(args.site_index.read_text(encoding="utf-8"))
    expected_routes = {page["path"] for page in local_index.get("pages", [])}
    responses, request_errors = fetch_many(page_urls)
    graph: dict[str, set[str]] = {}

    for url in page_urls:
        route = normalize_route(urlparse(url).path)
        if url in request_errors:
            issues.append(f"{route}: request failed: {request_errors[url]}")
            continue
        response = responses.get(url)
        if response is None:
            issues.append(f"{route}: missing fetched response")
            continue
        if response.status != 200:
            issues.append(f"{route}: expected status 200, got {response.status}")
            continue
        if not is_html(response):
            issues.append(f"{route}: expected HTML, got {response.headers.get('content-type', '')!r}")
            continue
        targets, main_count = parse_main_links(response.text, routes)
        if main_count != 1:
            issues.append(f"{route}: expected exactly one main element, found {main_count}")
        graph[route] = targets

    result = analyze_graph(graph, expected_routes=expected_routes)
    result["issues"] = [*issues, *result["issues"]]
    print(f"public_editorial_link_graph_pages={result['pages']}")
    print(f"public_editorial_link_graph_edges={result['edges']}")
    print(f"public_editorial_link_graph_orphaned={result['orphaned']}")
    print(f"public_editorial_link_graph_unreachable={result['unreachable']}")
    print(f"public_editorial_link_graph_max_home_depth={result['maxDepth']}")
    print(f"public_editorial_link_graph_issues={len(result['issues'])}")
    for issue in result["issues"]:
        print(issue)
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
