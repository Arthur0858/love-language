#!/usr/bin/env python3
"""Audit whether every indexable page is discoverable through editorial links."""

from __future__ import annotations

import json
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PAGE_COUNT = 30
MAX_HOME_DEPTH = 3
HUB_PREFIXES = {
    "/guides/": "/guides/",
    "/characters/": "/characters/",
    "/lab/": "/lab/",
}
LOCAL_HOSTS = {None, "lovetypes.tw", "www.lovetypes.tw"}


class MainLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.main_depth = 0
        self.skip_depth = 0
        self.main_count = 0
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "main":
            self.main_depth += 1
            self.main_count += 1
        elif self.main_depth and tag in {"script", "style", "nav", "header", "footer", "svg"}:
            self.skip_depth += 1
        if self.main_depth and not self.skip_depth and tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])

    def handle_endtag(self, tag: str) -> None:
        if self.main_depth and tag in {"script", "style", "nav", "header", "footer", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        elif tag == "main" and self.main_depth:
            self.main_depth -= 1


def normalize_route(value: str) -> str:
    path = urlparse(urldefrag(value)[0]).path or "/"
    if path.endswith("/") or "." in path.rsplit("/", 1)[-1]:
        return path
    return f"{path}/"


def page_file(route: str, root: Path = ROOT) -> Path:
    return root / (route.strip("/") or ".") / "index.html"


def parse_main_links(raw: str, routes: set[str]) -> tuple[set[str], int]:
    parser = MainLinkParser()
    parser.feed(raw)
    targets = {
        target
        for href in parser.hrefs
        if urlparse(urldefrag(href)[0]).hostname in LOCAL_HOSTS
        and (target := normalize_route(href)) in routes
    }
    return targets, parser.main_count


def shortest_depths(graph: dict[str, set[str]], start: str = "/") -> dict[str, int]:
    if start not in graph:
        return {}
    depths = {start: 0}
    queue = deque([start])
    while queue:
        route = queue.popleft()
        for target in graph.get(route, set()):
            if target not in depths:
                depths[target] = depths[route] + 1
                queue.append(target)
    return depths


def analyze_graph(
    graph: dict[str, set[str]],
    *,
    expected_routes: set[str],
    expected_page_count: int = EXPECTED_PAGE_COUNT,
    max_home_depth: int = MAX_HOME_DEPTH,
) -> dict[str, object]:
    issues: list[str] = []
    routes = set(graph)
    if routes != expected_routes:
        issues.append(
            "editorial graph routes differ: "
            f"missing={sorted(expected_routes-routes)} extra={sorted(routes-expected_routes)}"
        )
    if len(routes) != expected_page_count:
        issues.append(f"editorial graph must contain {expected_page_count} pages, found {len(routes)}")

    inbound: dict[str, set[str]] = {route: set() for route in routes}
    edge_count = 0
    for source, targets in graph.items():
        for target in targets:
            if target in routes and target != source:
                inbound[target].add(source)
                edge_count += 1

    orphaned = sorted(route for route in routes - {"/"} if not inbound[route])
    if orphaned:
        issues.append(f"indexable pages lack main-content inbound links: {orphaned}")

    depths = shortest_depths(graph)
    unreachable = sorted(routes - set(depths))
    if unreachable:
        issues.append(f"indexable pages are unreachable from home main content: {unreachable}")
    too_deep = sorted((route, depth) for route, depth in depths.items() if depth > max_home_depth)
    if too_deep:
        issues.append(f"indexable pages exceed home depth {max_home_depth}: {too_deep}")

    for hub, prefix in HUB_PREFIXES.items():
        children = {route for route in routes if route.startswith(prefix) and route != hub}
        missing = sorted(children - graph.get(hub, set()))
        if missing:
            issues.append(f"{hub} does not directly link every child page: {missing}")

    return {
        "pages": len(routes),
        "edges": edge_count,
        "orphaned": len(orphaned),
        "unreachable": len(unreachable),
        "maxDepth": max(depths.values(), default=-1),
        "issues": issues,
    }


def local_graph(root: Path = ROOT) -> tuple[dict[str, set[str]], set[str], list[str]]:
    index = json.loads((root / "site-index.json").read_text(encoding="utf-8"))
    routes = {page["path"] for page in index.get("pages", [])}
    graph: dict[str, set[str]] = {}
    issues: list[str] = []
    for route in sorted(routes):
        path = page_file(route, root)
        if not path.exists():
            issues.append(f"missing indexable page file: {path.relative_to(root)}")
            continue
        targets, main_count = parse_main_links(path.read_text(encoding="utf-8"), routes)
        if main_count != 1:
            issues.append(f"{route}: expected exactly one main element, found {main_count}")
        graph[route] = targets
    return graph, routes, issues


def print_result(result: dict[str, object]) -> None:
    print(f"editorial_link_graph_pages={result['pages']}")
    print(f"editorial_link_graph_edges={result['edges']}")
    print(f"editorial_link_graph_orphaned={result['orphaned']}")
    print(f"editorial_link_graph_unreachable={result['unreachable']}")
    print(f"editorial_link_graph_max_home_depth={result['maxDepth']}")
    print(f"editorial_link_graph_issues={len(result['issues'])}")
    for issue in result["issues"]:
        print(issue)


def main() -> int:
    graph, routes, parse_issues = local_graph()
    result = analyze_graph(graph, expected_routes=routes)
    result["issues"] = [*parse_issues, *result["issues"]]
    print_result(result)
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
