#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PREFIXES = {"zh": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
TYPE_GUIDE_ROUTES = {
    "iris": "guides/words-of-affirmation-scripts",
    "noah": "guides/quality-time-long-distance",
    "vivian": "guides/gifts-are-not-materialism",
    "claire": "guides/acts-of-service-boundaries",
    "dora": "guides/physical-touch-consent-safety",
}
BOOKS_HOST = "www.books.com.tw"
AFFILIATE_TOKENS = ("arthur0858", "utm_campaign=ap-202604")


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    text: str


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    text: str = ""
    children: list["Element"] = field(default_factory=list)


class GuardianParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root = Element("root", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        element = Element(tag, {key.lower(): value or "" for key, value in attrs})
        self.stack[-1].children.append(element)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(element)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.stack[-1].text += data


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def localized_path(lang: str, route: str = "") -> str:
    prefix = LANG_PREFIXES[lang]
    route = route.strip("/")
    parts = [part for part in (prefix, route) if part]
    return "/" + "/".join(parts) + ("/" if parts else "")


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public guardian smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                return Response(raw.geturl(), raw.status, raw.read().decode("utf-8", errors="replace"))
        except HTTPError as error:
            return Response(error.geturl(), error.code, error.read().decode("utf-8", errors="replace"))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def walk(element: Element) -> list[Element]:
    elements = [element]
    for child in element.children:
        elements.extend(walk(child))
    return elements


def descendants(element: Element, tag: str | None = None) -> list[Element]:
    items = walk(element)[1:]
    return [item for item in items if tag is None or item.tag == tag]


def has_class(element: Element, class_name: str) -> bool:
    return class_name in element.attrs.get("class", "").split()


def find_all(root: Element, *, tag: str | None = None, class_name: str | None = None, attr: str | None = None) -> list[Element]:
    items = walk(root)
    if tag:
        items = [item for item in items if item.tag == tag]
    if class_name:
        items = [item for item in items if has_class(item, class_name)]
    if attr:
        items = [item for item in items if attr in item.attrs]
    return items


def find_by_class(root: Element, class_name: str) -> Element | None:
    return next((element for element in walk(root) if has_class(element, class_name)), None)


def is_affiliate_url(value: str) -> bool:
    return value.startswith(f"https://{BOOKS_HOST}/") and all(token in value for token in AFFILIATE_TOKENS)


def hrefs_under(element: Element) -> list[str]:
    return [link.attrs.get("href", "") for link in descendants(element, "a")]


def validate_overview(base_url: str, lang: str) -> tuple[list[str], dict[str, int]]:
    path = localized_path(lang, "characters")
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    stats = {"overview_pages": 0, "overview_map_cards": 0, "overview_need_cards": 0, "overview_entry_actions": 0}
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["overview_pages"] = 1
    parser = GuardianParser()
    parser.feed(response.text)
    root = parser.root

    map_section = find_by_class(root, "universe-map-section")
    if map_section is None or "data-universe-map" not in response.text:
        issues.append(f"{path}: missing five-domain universe map")
    else:
        cards = [card for card in descendants(map_section, "a") if has_class(card, "guardian-card")]
        stats["overview_map_cards"] += len(cards)
        if len(cards) != len(GUARDIAN_SLUGS):
            issues.append(f"{path}: expected five universe guardian cards, got {len(cards)}")
        for slug in GUARDIAN_SLUGS:
            expected = localized_path(lang, f"characters/{slug}")
            if expected not in [card.attrs.get("href", "") for card in cards]:
                issues.append(f"{path}: universe map missing {slug} link")

    need_cards = find_all(root, tag="article", class_name="guardian-need-card")
    stats["overview_need_cards"] += len(need_cards)
    if len(need_cards) != len(GUARDIAN_SLUGS):
        issues.append(f"{path}: expected five need-router cards, got {len(need_cards)}")
    for slug in GUARDIAN_SLUGS:
        card = next((item for item in need_cards if item.attrs.get("data-guardian-domain") == slug), None)
        if card is None:
            issues.append(f"{path}: need router missing {slug}")
            continue
        hrefs = hrefs_under(card)
        if localized_path(lang, f"characters/{slug}") not in hrefs:
            issues.append(f"{path}: {slug} need router missing character link")
        if localized_path(lang, "resources") + f"#supply-{slug}" not in hrefs:
            issues.append(f"{path}: {slug} need router missing supply link")

    entry = find_by_class(root, "guardian-entry-section")
    if entry is None:
        issues.append(f"{path}: missing guardian entry section")
    else:
        action_hrefs = hrefs_under(entry)
        for expected in (localized_path(lang) + "#quiz-section", "#guardian-map", localized_path(lang, "resources")):
            if expected not in action_hrefs:
                issues.append(f"{path}: guardian entry missing action {expected}")
            else:
                stats["overview_entry_actions"] += 1
    return issues, stats


def validate_guardian_page(base_url: str, lang: str, slug: str) -> tuple[list[str], dict[str, int]]:
    path = localized_path(lang, f"characters/{slug}")
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    stats = {
        "guardian_pages": 0,
        "domain_markers": 0,
        "hero_supply_links": 0,
        "route_snapshots": 0,
        "guide_links": 0,
        "repair_links": 0,
        "supply_links": 0,
        "luna_links": 0,
        "affiliate_links": 0,
        "nav_cards": 0,
        "resume_templates": 0,
    }
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["guardian_pages"] = 1
    parser = GuardianParser()
    parser.feed(response.text)
    root = parser.root

    hero = find_by_class(root, "guardian-domain-hero")
    if hero is None or hero.attrs.get("data-guardian-domain") != slug:
        issues.append(f"{path}: missing guardian domain hero for {slug}")
    else:
        hrefs = hrefs_under(hero)
        if localized_path(lang, "resources") + f"#supply-{slug}" in hrefs:
            stats["hero_supply_links"] += 1
        else:
            issues.append(f"{path}: hero missing primary supply route")
        if localized_path(lang) + "#quiz-section" not in hrefs:
            issues.append(f"{path}: hero missing quiz action")
        if localized_path(lang, "characters") not in hrefs:
            issues.append(f"{path}: hero missing guardians overview action")

    if "data-domain-marker" not in response.text:
        issues.append(f"{path}: missing guardian domain marker")
    else:
        stats["domain_markers"] += 1
    if "data-guardian-saved" not in response.text or "guardian-resume-card" not in response.text:
        issues.append(f"{path}: missing saved guardian resume template")
    else:
        stats["resume_templates"] += 1

    snapshot = find_by_class(root, "guardian-route-snapshot")
    if snapshot is None:
        issues.append(f"{path}: missing guardian route snapshot")
    else:
        stats["route_snapshots"] += 1
        hrefs = hrefs_under(snapshot)
        expected_guide = localized_path(lang, TYPE_GUIDE_ROUTES[slug])
        expected_repair = localized_path(lang, "repair-plan") + f"#plan-{slug}"
        expected_supply = localized_path(lang, "resources") + f"#supply-{slug}"
        if expected_guide in hrefs:
            stats["guide_links"] += 1
        else:
            issues.append(f"{path}: route snapshot missing guide link")
        if expected_repair in hrefs:
            stats["repair_links"] += 1
        else:
            issues.append(f"{path}: route snapshot missing repair link")
        if expected_supply in hrefs:
            stats["supply_links"] += 1
        else:
            issues.append(f"{path}: route snapshot missing supply link")

    supply_panel = find_by_class(root, "supply-panel-section")
    if supply_panel is None:
        issues.append(f"{path}: missing guardian supply panel")
    else:
        hrefs = hrefs_under(supply_panel)
        expected_guide = localized_path(lang, TYPE_GUIDE_ROUTES[slug])
        expected_luna = localized_path(lang, "luna-yoga-music") + f"#luna-{slug}"
        expected_supply = localized_path(lang, "resources") + f"#supply-{slug}"
        if expected_guide not in hrefs:
            issues.append(f"{path}: supply panel missing guide link")
        if expected_luna in hrefs:
            stats["luna_links"] += 1
        else:
            issues.append(f"{path}: supply panel missing Luna link")
        if expected_supply in hrefs:
            stats["supply_links"] += 1
        else:
            issues.append(f"{path}: supply panel missing supply link")
        affiliate_links = [href for href in hrefs if is_affiliate_url(href)]
        if len(affiliate_links) != 1:
            issues.append(f"{path}: supply panel should include one tracked affiliate book link, got {len(affiliate_links)}")
        else:
            stats["affiliate_links"] += 1
        if "affiliate-disclosure" not in response.text:
            issues.append(f"{path}: missing affiliate disclosure")

    nav_section = find_by_class(root, "guardian-nav-section")
    if nav_section is None:
        issues.append(f"{path}: missing guardian interlink section")
    else:
        nav_cards = [card for card in descendants(nav_section, "a") if has_class(card, "guardian-card")]
        stats["nav_cards"] += len(nav_cards)
        if len(nav_cards) != len(GUARDIAN_SLUGS):
            issues.append(f"{path}: expected five guardian nav cards, got {len(nav_cards)}")
        nav_hrefs = [card.attrs.get("href", "") for card in nav_cards]
        for target_slug in GUARDIAN_SLUGS:
            if localized_path(lang, f"characters/{target_slug}") not in nav_hrefs:
                issues.append(f"{path}: guardian nav missing {target_slug}")
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes guardian overview and character universe routes.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    totals = {
        "overview_pages": 0,
        "overview_map_cards": 0,
        "overview_need_cards": 0,
        "overview_entry_actions": 0,
        "guardian_pages": 0,
        "domain_markers": 0,
        "hero_supply_links": 0,
        "route_snapshots": 0,
        "guide_links": 0,
        "repair_links": 0,
        "supply_links": 0,
        "luna_links": 0,
        "affiliate_links": 0,
        "nav_cards": 0,
        "resume_templates": 0,
    }
    for lang in LANG_PREFIXES:
        overview_issues, overview_stats = validate_overview(base_url, lang)
        issues.extend(overview_issues)
        for key, value in overview_stats.items():
            totals[key] += value
        for slug in GUARDIAN_SLUGS:
            page_issues, page_stats = validate_guardian_page(base_url, lang, slug)
            issues.extend(page_issues)
            for key, value in page_stats.items():
                totals[key] += value

    print(f"public_guardian_overview_pages_checked={totals['overview_pages']}")
    print(f"public_guardian_overview_map_cards_checked={totals['overview_map_cards']}")
    print(f"public_guardian_overview_need_cards_checked={totals['overview_need_cards']}")
    print(f"public_guardian_overview_entry_actions_checked={totals['overview_entry_actions']}")
    print(f"public_guardian_pages_checked={totals['guardian_pages']}")
    print(f"public_guardian_domain_markers_checked={totals['domain_markers']}")
    print(f"public_guardian_hero_supply_links_checked={totals['hero_supply_links']}")
    print(f"public_guardian_route_snapshots_checked={totals['route_snapshots']}")
    print(f"public_guardian_guide_links_checked={totals['guide_links']}")
    print(f"public_guardian_repair_links_checked={totals['repair_links']}")
    print(f"public_guardian_supply_links_checked={totals['supply_links']}")
    print(f"public_guardian_luna_links_checked={totals['luna_links']}")
    print(f"public_guardian_affiliate_links_checked={totals['affiliate_links']}")
    print(f"public_guardian_nav_cards_checked={totals['nav_cards']}")
    print(f"public_guardian_resume_templates_checked={totals['resume_templates']}")
    print(f"public_guardian_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
