#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {"zh": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
GUIDES = (
    ("share-your-result", "iris"),
    ("repair-after-conflict", "noah"),
    ("words-of-affirmation-scripts", "iris"),
    ("acts-of-service-boundaries", "claire"),
    ("gifts-are-not-materialism", "vivian"),
    ("quality-time-long-distance", "noah"),
    ("physical-touch-consent-safety", "dora"),
    ("weekly-relationship-review", "claire"),
    ("emotional-needs-checklist", "vivian"),
    ("misfrequency-examples", "iris"),
    ("relationship-stages", "noah"),
    ("healthy-boundaries", "dora"),
)
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
QUIZ_SRC_RE = re.compile(r"^/quiz-data-(zh|en|ja|ko|es)-[^/]+\.js$")


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


class GuideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root = Element("root", {})
        self.stack = [self.root]
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        element = Element(tag, {key.lower(): value or "" for key, value in attrs})
        self.stack[-1].children.append(element)
        if tag == "script" and element.attrs.get("src"):
            self.scripts.append(element.attrs["src"])
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
    prefix = LANG_PATHS[lang]
    route = route.strip("/")
    parts = [part for part in (prefix, route) if part]
    return "/" + "/".join(parts) + ("/" if parts else "")


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public guide smoke/1.0"})
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


def find_all(root: Element, *, tag: str | None = None, class_name: str | None = None, attr: str | None = None, element_id: str | None = None) -> list[Element]:
    items = walk(root)
    if tag:
        items = [item for item in items if item.tag == tag]
    if class_name:
        items = [item for item in items if has_class(item, class_name)]
    if attr:
        items = [item for item in items if attr in item.attrs]
    if element_id:
        items = [item for item in items if item.attrs.get("id") == element_id]
    return items


def find_by_class(root: Element, class_name: str) -> Element | None:
    return next((element for element in walk(root) if has_class(element, class_name)), None)


def hrefs_under(element: Element) -> list[str]:
    return [link.attrs.get("href", "") for link in descendants(element, "a")]


def parse(text: str) -> GuideParser:
    parser = GuideParser()
    parser.feed(text)
    return parser


def validate_quiz_script(path: str, lang: str, parser: GuideParser) -> tuple[list[str], int]:
    scripts = [src for src in parser.scripts if QUIZ_SRC_RE.match(src)]
    if len(scripts) != 1:
        return [f"{path}: expected one localized quiz-data script, found {scripts}"], 0
    match = QUIZ_SRC_RE.match(scripts[0])
    if match and match.group(1) != lang:
        return [f"{path}: expected {lang} quiz-data script, got {scripts[0]}"], 0
    return [], 1


def validate_index(base_url: str, lang: str) -> tuple[list[str], dict[str, int]]:
    path = localized_path(lang, "guides")
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    stats = {
        "index_pages": 0,
        "index_actions": 0,
        "index_action_events": 0,
        "index_compass_cards": 0,
        "index_compass_events": 0,
        "index_domain_cards": 0,
        "index_domain_actions": 0,
        "index_domain_events": 0,
        "index_guide_cards": 0,
        "index_boundary_sections": 0,
    }
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["index_pages"] = 1
    parser = parse(response.text)
    root = parser.root

    actions = find_all(root, attr="data-guide-index-actions")
    if len(actions) != 1:
        issues.append(f"{path}: expected one guide index action group, got {len(actions)}")
    else:
        hrefs = hrefs_under(actions[0])
        for expected in (localized_path(lang) + "#quiz-section", localized_path(lang, "characters"), localized_path(lang, "resources")):
            if expected not in hrefs:
                issues.append(f"{path}: guide index actions missing {expected}")
            else:
                stats["index_actions"] += 1
        hero_events = {link.attrs.get("data-funnel-event", "") for link in descendants(actions[0], "a")}
        expected_hero_events = {"guide_index_hero_quiz", "guide_index_hero_guardians", "guide_index_hero_resources"}
        missing_hero_events = expected_hero_events.difference(hero_events)
        if missing_hero_events:
            issues.append(f"{path}: guide index hero missing events {', '.join(sorted(missing_hero_events))}")
        else:
            stats["index_action_events"] += len(expected_hero_events)

    compass = find_by_class(root, "guide-index-compass")
    if compass is None:
        issues.append(f"{path}: missing guide index compass")
    else:
        cards = descendants(compass, "article")
        stats["index_compass_cards"] += len(cards)
        if len(cards) != 3:
            issues.append(f"{path}: expected three guide compass cards, got {len(cards)}")
        compass_events = {link.attrs.get("data-funnel-event", "") for link in descendants(compass, "a")}
        expected_compass_events = {"guide_index_compass_1", "guide_index_compass_2", "guide_index_compass_3"}
        missing_compass_events = expected_compass_events.difference(compass_events)
        if missing_compass_events:
            issues.append(f"{path}: guide compass missing events {', '.join(sorted(missing_compass_events))}")
        else:
            stats["index_compass_events"] += len(expected_compass_events)

    domain = find_all(root, attr="data-guide-domain-routes")
    if len(domain) != 1:
        issues.append(f"{path}: expected one guide domain route section, got {len(domain)}")
    else:
        cards = [card for card in descendants(domain[0], "article") if has_class(card, "guide-domain-card")]
        stats["index_domain_cards"] += len(cards)
        if len(cards) != len(GUARDIAN_SLUGS):
            issues.append(f"{path}: expected five guide domain cards, got {len(cards)}")
        for slug in GUARDIAN_SLUGS:
            card = next((item for item in cards if item.attrs.get("data-guardian-domain") == slug), None)
            if card is None:
                issues.append(f"{path}: domain routes missing {slug}")
                continue
            hrefs = hrefs_under(card)
            expected_links = (localized_path(lang, "characters/" + slug), localized_path(lang, "resources") + f"#supply-{slug}")
            for expected in expected_links:
                if expected not in hrefs:
                    issues.append(f"{path}: {slug} domain card missing {expected}")
                else:
                    stats["index_domain_actions"] += 1
            guide_links = [href for href in hrefs if href.startswith(localized_path(lang, "guides/"))]
            if not guide_links:
                issues.append(f"{path}: {slug} domain card missing guide link")
            else:
                stats["index_domain_actions"] += 1
            domain_events = {link.attrs.get("data-funnel-event", "") for link in descendants(card, "a")}
            expected_domain_events = {"guide_domain_read", "guide_domain_guardian", "guide_domain_supply"}
            missing_domain_events = expected_domain_events.difference(domain_events)
            if missing_domain_events:
                issues.append(f"{path}: {slug} domain card missing events {', '.join(sorted(missing_domain_events))}")
            else:
                stats["index_domain_events"] += len(expected_domain_events)

    cards = [card for card in find_all(root, tag="a", class_name="content-card") if card.attrs.get("href", "").startswith(localized_path(lang, "guides/"))]
    stats["index_guide_cards"] += len(cards)
    if len(cards) != len(GUIDES):
        issues.append(f"{path}: expected {len(GUIDES)} guide cards, got {len(cards)}")
    expected_hrefs = {localized_path(lang, f"guides/{slug}") for slug, _guardian in GUIDES}
    actual_hrefs = {card.attrs.get("href", "") for card in cards}
    missing = sorted(expected_hrefs.difference(actual_hrefs))
    if missing:
        issues.append(f"{path}: guide index missing cards {', '.join(missing)}")
    if find_by_class(root, "note-section") is None:
        issues.append(f"{path}: missing boundary note section")
    else:
        stats["index_boundary_sections"] += 1
    return issues, stats


def validate_guide(base_url: str, lang: str, guide_slug: str, guardian_slug: str) -> tuple[list[str], dict[str, int]]:
    path = localized_path(lang, f"guides/{guide_slug}")
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    stats = {
        "guide_pages": 0,
        "guide_quiz_scripts": 0,
        "guide_resume_templates": 0,
        "guide_resume_events": 0,
        "guide_article_sections": 0,
        "guide_safety_callouts": 0,
        "guide_related_cards": 0,
        "guide_action_bridges": 0,
        "guide_action_cards": 0,
        "guide_action_events": 0,
        "guide_guardian_links": 0,
        "guide_supply_links": 0,
        "guide_repair_links": 0,
        "guide_luna_links": 0,
        "guide_anchor_targets": 0,
    }
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["guide_pages"] = 1
    parser = parse(response.text)
    root = parser.root
    script_issues, scripts_checked = validate_quiz_script(path, lang, parser)
    issues.extend(script_issues)
    stats["guide_quiz_scripts"] += scripts_checked

    if "data-guide-saved" not in response.text or "data-clear-guide-result" not in response.text:
        issues.append(f"{path}: missing guide saved-result resume template")
    else:
        stats["guide_resume_templates"] += 1
        expected_resume_events = {
            "guide_resume_plan",
            "guide_resume_route",
            "guide_resume_luna",
            "guide_resume_keepsake",
            "guide_resume_contact",
            "guide_resume_guardian",
            "guide_resume_clear",
        }
        missing_resume_events = [
            event for event in sorted(expected_resume_events)
            if f'data-funnel-event="{event}"' not in response.text
        ]
        if missing_resume_events:
            issues.append(f"{path}: guide resume template missing events {', '.join(missing_resume_events)}")
        else:
            stats["guide_resume_events"] += len(expected_resume_events)

    article = find_by_class(root, "article-body")
    if article is None:
        issues.append(f"{path}: missing article body")
    else:
        headings = descendants(article, "h2")
        stats["guide_article_sections"] += len(headings)
        if len(headings) < 6:
            issues.append(f"{path}: expected at least six article sections, got {len(headings)}")
        if find_by_class(article, "safety") is None:
            issues.append(f"{path}: missing safety boundary callout")
        else:
            stats["guide_safety_callouts"] += 1

    aside = find_by_class(root, "article-side")
    if aside is None:
        issues.append(f"{path}: missing related guide sidebar")
    else:
        related = [card for card in descendants(aside, "a") if has_class(card, "content-card")]
        stats["guide_related_cards"] += len(related)
        if len(related) != 2:
            issues.append(f"{path}: expected two related guide cards, got {len(related)}")

    if find_all(root, element_id=f"guide-{guardian_slug}"):
        stats["guide_anchor_targets"] += 1
    else:
        issues.append(f"{path}: missing guide guardian anchor #guide-{guardian_slug}")

    bridges = find_all(root, attr="data-guide-action-bridge")
    if len(bridges) != 1:
        issues.append(f"{path}: expected one guide action bridge, got {len(bridges)}")
    else:
        stats["guide_action_bridges"] += 1
        cards = [card for card in descendants(bridges[0], "article") if has_class(card, "guide-action-card")]
        stats["guide_action_cards"] += len(cards)
        if len(cards) != 4:
            issues.append(f"{path}: expected four guide action cards, got {len(cards)}")
        hrefs = hrefs_under(bridges[0])
        action_events = {link.attrs.get("data-funnel-event", "") for link in descendants(bridges[0], "a")}
        expected_action_events = {"guide_action_01", "guide_action_02", "guide_action_03", "guide_action_04"}
        missing_action_events = expected_action_events.difference(action_events)
        if missing_action_events:
            issues.append(f"{path}: action bridge missing events {', '.join(sorted(missing_action_events))}")
        else:
            stats["guide_action_events"] += len(expected_action_events)
        expected = {
            "guardian": localized_path(lang, f"characters/{guardian_slug}"),
            "supply": localized_path(lang, "resources") + f"#supply-{guardian_slug}",
            "repair": localized_path(lang, "repair-plan") + f"#plan-{guardian_slug}",
            "luna": localized_path(lang, "luna-yoga-music") + f"#luna-{guardian_slug}",
        }
        if expected["guardian"] in hrefs:
            stats["guide_guardian_links"] += 1
        else:
            issues.append(f"{path}: action bridge missing guardian link")
        if expected["supply"] in hrefs:
            stats["guide_supply_links"] += 1
        else:
            issues.append(f"{path}: action bridge missing supply link")
        if expected["repair"] in hrefs:
            stats["guide_repair_links"] += 1
        else:
            issues.append(f"{path}: action bridge missing repair plan link")
        if expected["luna"] in hrefs:
            stats["guide_luna_links"] += 1
        else:
            issues.append(f"{path}: action bridge missing Luna link")
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes guide index and guide detail routes.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    totals = {
        "index_pages": 0,
        "index_actions": 0,
        "index_action_events": 0,
        "index_compass_cards": 0,
        "index_compass_events": 0,
        "index_domain_cards": 0,
        "index_domain_actions": 0,
        "index_domain_events": 0,
        "index_guide_cards": 0,
        "index_boundary_sections": 0,
        "guide_pages": 0,
        "guide_quiz_scripts": 0,
        "guide_resume_templates": 0,
        "guide_resume_events": 0,
        "guide_article_sections": 0,
        "guide_safety_callouts": 0,
        "guide_related_cards": 0,
        "guide_action_bridges": 0,
        "guide_action_cards": 0,
        "guide_action_events": 0,
        "guide_guardian_links": 0,
        "guide_supply_links": 0,
        "guide_repair_links": 0,
        "guide_luna_links": 0,
        "guide_anchor_targets": 0,
    }
    issues: list[str] = []
    for lang in LANG_PATHS:
        index_issues, index_stats = validate_index(base_url, lang)
        issues.extend(index_issues)
        for key, value in index_stats.items():
            totals[key] += value
        for guide_slug, guardian_slug in GUIDES:
            guide_issues, guide_stats = validate_guide(base_url, lang, guide_slug, guardian_slug)
            issues.extend(guide_issues)
            for key, value in guide_stats.items():
                totals[key] += value

    print(f"public_guide_index_pages_checked={totals['index_pages']}")
    print(f"public_guide_index_actions_checked={totals['index_actions']}")
    print(f"public_guide_index_action_events_checked={totals['index_action_events']}")
    print(f"public_guide_index_compass_cards_checked={totals['index_compass_cards']}")
    print(f"public_guide_index_compass_events_checked={totals['index_compass_events']}")
    print(f"public_guide_index_domain_cards_checked={totals['index_domain_cards']}")
    print(f"public_guide_index_domain_actions_checked={totals['index_domain_actions']}")
    print(f"public_guide_index_domain_events_checked={totals['index_domain_events']}")
    print(f"public_guide_index_cards_checked={totals['index_guide_cards']}")
    print(f"public_guide_index_boundary_sections_checked={totals['index_boundary_sections']}")
    print(f"public_guide_pages_checked={totals['guide_pages']}")
    print(f"public_guide_quiz_scripts_checked={totals['guide_quiz_scripts']}")
    print(f"public_guide_resume_templates_checked={totals['guide_resume_templates']}")
    print(f"public_guide_resume_events_checked={totals['guide_resume_events']}")
    print(f"public_guide_article_sections_checked={totals['guide_article_sections']}")
    print(f"public_guide_safety_callouts_checked={totals['guide_safety_callouts']}")
    print(f"public_guide_related_cards_checked={totals['guide_related_cards']}")
    print(f"public_guide_action_bridges_checked={totals['guide_action_bridges']}")
    print(f"public_guide_action_cards_checked={totals['guide_action_cards']}")
    print(f"public_guide_action_events_checked={totals['guide_action_events']}")
    print(f"public_guide_guardian_links_checked={totals['guide_guardian_links']}")
    print(f"public_guide_supply_links_checked={totals['guide_supply_links']}")
    print(f"public_guide_repair_links_checked={totals['guide_repair_links']}")
    print(f"public_guide_luna_links_checked={totals['guide_luna_links']}")
    print(f"public_guide_anchor_targets_checked={totals['guide_anchor_targets']}")
    print(f"public_guide_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
