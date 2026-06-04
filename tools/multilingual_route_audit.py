#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_ROUTES = [
    "",
    "guides",
    "characters",
    "theory",
    "resources",
    "repair-plan",
    "keepsakes",
    "luna-yoga-music",
    "about",
    "contact",
    "privacy",
    "terms",
]


class PageShellParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.robots = ""
        self.canonical = ""
        self._in_title = False
        self._in_h1 = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._in_h1 = True
        elif tag == "meta" and data.get("name") == "robots":
            self.robots = data.get("content", "")
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_h1:
            self.h1_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join(" ".join(self.title_parts).split())

    @property
    def h1(self) -> str:
        return " ".join(" ".join(self.h1_parts).split())

    @property
    def noindex(self) -> bool:
        return "noindex" in self.robots.lower()


def load_generator_config():
    generator_path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_site_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load generator config from {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def route_path(lang_config: dict, route: str) -> Path:
    parts = [part for part in (lang_config["prefix"], route) if part]
    if not parts:
        return ROOT / "index.html"
    return ROOT.joinpath(*parts) / "index.html"


def public_path(lang_config: dict, route: str) -> str:
    parts = [part.strip("/") for part in (lang_config["prefix"], route) if part]
    return "/" + "/".join(parts) + ("/" if parts else "")


def parse_page(path: Path) -> PageShellParser:
    parser = PageShellParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser


def main() -> int:
    config = load_generator_config()
    issues: list[str] = []
    routes_checked = 0
    alias_routes_checked = 0
    expected_routes = [
        *CORE_ROUTES,
        *(f"guides/{guide['slug']}" for guide in config.GUIDES),
        *(f"characters/{slug}" for slug in config.GUARDIANS),
    ]

    for lang, lang_config in config.LANGS.items():
        for route in expected_routes:
            path = route_path(lang_config, route)
            routes_checked += 1
            if not path.exists():
                issues.append(f"{lang}:{route or '/'} missing localized route file: {path.relative_to(ROOT)}")
                continue
            page = parse_page(path)
            if page.noindex:
                issues.append(f"{lang}:{route or '/'} expected indexable route, found noindex: {path.relative_to(ROOT)}")
            if page.html_lang != lang_config["code"]:
                issues.append(
                    f"{lang}:{route or '/'} html lang should be {lang_config['code']}, got {page.html_lang!r}"
                )
            if not page.title:
                issues.append(f"{lang}:{route or '/'} missing title")
            if not page.h1:
                issues.append(f"{lang}:{route or '/'} missing h1")
            expected_canonical_suffix = public_path(lang_config, route)
            if not page.canonical.endswith(expected_canonical_suffix):
                issues.append(
                    f"{lang}:{route or '/'} canonical should end with {expected_canonical_suffix}, got {page.canonical!r}"
                )

        alias_path = route_path(lang_config, "luna")
        alias_routes_checked += 1
        if not alias_path.exists():
            issues.append(f"{lang}:luna alias missing: {alias_path.relative_to(ROOT)}")
        else:
            alias_page = parse_page(alias_path)
            if not alias_page.noindex:
                issues.append(f"{lang}:luna alias should be noindex: {alias_path.relative_to(ROOT)}")
            if alias_page.html_lang != lang_config["code"]:
                issues.append(
                    f"{lang}:luna alias html lang should be {lang_config['code']}, got {alias_page.html_lang!r}"
                )

    print(f"languages_checked={len(config.LANGS)}")
    print(f"localized_routes_checked={routes_checked}")
    print(f"luna_alias_routes_checked={alias_routes_checked}")
    print(f"multilingual_route_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
