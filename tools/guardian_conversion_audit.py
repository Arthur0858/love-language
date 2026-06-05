#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DYNAMIC_RESUME_MARKERS = {
    "guide": 'id="guide-${result.slug}"',
    "keepsake": 'id="keepsake-${result.slug}"',
    "luna": "#luna-${slug}",
}


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.sponsored_hrefs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if "id" in data:
            self.ids.add(data["id"])
        if tag == "a" and data.get("href"):
            href = data["href"]
            self.hrefs.append(href)
            if "sponsored" in data.get("rel", "").split():
                self.sponsored_hrefs.add(href)


def load_generator_config():
    generator_path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_site_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load generator config from {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def page_path(config, lang: str, route: str = "") -> Path:
    prefix = config.LANGS[lang]["prefix"]
    parts = []
    if prefix:
        parts.append(prefix)
    clean = route.strip("/")
    if clean:
        parts.extend(clean.split("/"))
    return ROOT.joinpath(*parts, "index.html") if parts else ROOT / "index.html"


def asset_path(src: str) -> Path:
    return ROOT / src.lstrip("/")


def parse_page(path: Path) -> tuple[AnchorParser, str]:
    source = path.read_text(encoding="utf-8", errors="ignore")
    parser = AnchorParser()
    parser.feed(source)
    return parser, source


def require_text(value: object, label: str, issues: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        issues.append(f"{label} is empty")


def require_page(path: Path, label: str, issues: list[str]) -> tuple[AnchorParser | None, str]:
    if not path.exists():
        issues.append(f"{label} missing page: {path.relative_to(ROOT)}")
        return None, ""
    return parse_page(path)


def require_static_id(parser: AnchorParser | None, expected_id: str, label: str, issues: list[str]) -> None:
    if parser is None:
        return
    if expected_id not in parser.ids:
        issues.append(f"{label} missing #{expected_id}")


def require_dynamic_marker(source: str, marker_key: str, label: str, issues: list[str]) -> None:
    marker = DYNAMIC_RESUME_MARKERS[marker_key]
    if marker not in source:
        issues.append(f"{label} missing dynamic resume marker {marker!r}")


def require_local_target(config, lang: str, href: str, label: str, issues: list[str]) -> None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        issues.append(f"{label} should be a local URL, got {href!r}")
        return
    path = parsed.path.strip("/")
    prefix = config.LANGS[lang]["prefix"].strip("/")
    if prefix and path.startswith(prefix + "/"):
        path = path[len(prefix) + 1 :]
    elif prefix and path == prefix:
        path = ""
    target = page_path(config, lang, path)
    if not target.exists():
        issues.append(f"{label} target missing: {href}")


def audit_guardian(config, lang: str, result_key: str, meta: dict, issues: list[str]) -> int:
    checks = 0
    slug = meta["slug"]
    guide_slug = meta["guide"]
    label = f"{lang}:{slug}"
    guardian = config.GUARDIANS.get(slug)
    if guardian is None:
        issues.append(f"{label} missing guardian config")
        return checks
    if lang not in guardian:
        issues.append(f"{label} missing localized guardian copy")
        return checks

    guardian_name, guardian_type, guardian_desc = guardian[lang]
    for field_label, value in (
        ("guardian name", guardian_name),
        ("guardian type", guardian_type),
        ("guardian desc", guardian_desc),
    ):
        checks += 1
        require_text(value, f"{label} {field_label}", issues)

    for asset_label, src in (("guardian image", guardian.get("asset", "")), ("guardian prop", guardian.get("prop", ""))):
        checks += 1
        if not src or not asset_path(src).exists():
            issues.append(f"{label} missing {asset_label}: {src}")

    story_image = config.guardian_story_image(lang, slug)
    checks += 1
    if not asset_path(story_image).exists():
        issues.append(f"{label} missing story image: {story_image}")

    guide = next((guide for guide in config.GUIDES if guide["slug"] == guide_slug), None)
    checks += 1
    if guide is None:
        issues.append(f"{label} missing guide config: {guide_slug}")
    elif lang not in guide or not guide[lang][0].strip():
        issues.append(f"{label} missing localized guide title: {guide_slug}")

    route = config.supply_route(lang, slug)
    for field_name in ("title", "desc", "wound", "mission", "supply"):
        checks += 1
        require_text(route.get(field_name), f"{label} supply route {field_name}", issues)

    book = route.get("book", {})
    book_url = book.get("url", "")
    checks += 1
    if not isinstance(book_url, str) or not book_url.startswith("https://"):
        issues.append(f"{label} affiliate book url should be https: {book_url!r}")
    checks += 1
    if lang not in book.get("title", {}) or not book["title"][lang].strip():
        issues.append(f"{label} missing localized affiliate book title")

    tips = config.QUIZ_TIPS.get(lang, {}).get(result_key, [])
    checks += 1
    if len([tip for tip in tips if isinstance(tip, str) and tip.strip()]) < 2:
        issues.append(f"{label} should have at least 2 quiz tips")

    resource_parser, resource_source = require_page(page_path(config, lang, "resources"), f"{label} resources", issues)
    plan_parser, _plan_source = require_page(page_path(config, lang, "repair-plan"), f"{label} repair plan", issues)
    guide_parser, guide_source = require_page(page_path(config, lang, f"guides/{guide_slug}"), f"{label} guide", issues)
    keepsake_parser, keepsake_source = require_page(page_path(config, lang, "keepsakes"), f"{label} keepsakes", issues)
    luna_parser, luna_source = require_page(page_path(config, lang, "luna-yoga-music"), f"{label} luna", issues)
    character_parser, _character_source = require_page(page_path(config, lang, f"characters/{slug}"), f"{label} character", issues)

    checks += 6
    require_static_id(resource_parser, f"supply-{slug}", f"{label} resources", issues)
    require_static_id(plan_parser, f"plan-{slug}", f"{label} repair plan", issues)
    require_dynamic_marker(guide_source, "guide", f"{label} guide", issues)
    require_dynamic_marker(keepsake_source, "keepsake", f"{label} keepsakes", issues)
    require_dynamic_marker(luna_source, "luna", f"{label} luna", issues)
    if character_parser is None:
        issues.append(f"{label} character page is unavailable")

    checks += 1
    if resource_parser is not None and book_url not in resource_parser.sponsored_hrefs:
        issues.append(f"{label} resources page missing sponsored affiliate link: {book_url}")

    result_urls = {
        "guardianUrl": config.lang_url(lang, "characters/" + slug),
        "guideUrl": config.lang_url(lang, "guides/" + guide_slug) + f"#guide-{slug}",
        "resourceUrl": config.lang_url(lang, "resources") + f"#supply-{slug}",
        "lunaUrl": config.lang_url(lang, "luna-yoga-music") + f"#luna-{slug}",
        "collectorHallUrl": config.lang_url(lang, "keepsakes") + f"#keepsake-{slug}",
        "planUrl": config.lang_url(lang, "repair-plan") + f"#plan-{slug}",
    }
    for url_label, href in result_urls.items():
        checks += 1
        require_local_target(config, lang, href, f"{label} {url_label}", issues)

    checks += 1
    if plan_parser is not None and result_urls["lunaUrl"] not in plan_parser.hrefs:
        issues.append(f"{label} repair plan missing guardian Luna route: {result_urls['lunaUrl']}")

    starter_kit = config.starter_kit_payload(lang, result_urls["resourceUrl"])
    steps = starter_kit.get("steps", [])
    checks += 1
    if len(steps) != 4:
        issues.append(f"{label} starter kit should have 4 steps, got {len(steps)}")
    for idx, step in enumerate(steps, start=1):
        href = step.get("href", "")
        checks += 1
        if not href:
            issues.append(f"{label} starter kit step {idx} missing href")
        elif href.startswith("/"):
            require_local_target(config, lang, href, f"{label} starter kit step {idx}", issues)

    if resource_source and f'href="{book_url}"' not in resource_source:
        checks += 1
        issues.append(f"{label} resources source does not contain affiliate book URL")

    return checks


def main() -> int:
    config = load_generator_config()
    issues: list[str] = []
    routes_checked = 0
    target_checks = 0

    for lang in config.LANGS:
        for result_key, meta in config.QUIZ_TYPES.items():
            routes_checked += 1
            target_checks += audit_guardian(config, lang, result_key, meta, issues)

    print(f"conversion_languages_checked={len(config.LANGS)}")
    print(f"guardian_conversion_routes_checked={routes_checked}")
    print(f"guardian_conversion_target_checks={target_checks}")
    print(f"guardian_conversion_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
