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
LANG_PREFIXES = {"zh": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
GUIDE_SLUGS = (
    "share-your-result",
    "repair-after-conflict",
    "words-of-affirmation-scripts",
    "acts-of-service-boundaries",
    "gifts-are-not-materialism",
    "quality-time-long-distance",
    "physical-touch-consent-safety",
    "weekly-relationship-review",
    "emotional-needs-checklist",
    "misfrequency-examples",
    "relationship-stages",
    "healthy-boundaries",
)
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


class GardenMapParser(HTMLParser):
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
    prefix = LANG_PREFIXES[lang]
    route = route.strip("/")
    parts = [part for part in (prefix, route) if part]
    return "/" + "/".join(parts) + ("/" if parts else "")


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public garden map smoke/1.0"})
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


def hrefs_under(element: Element) -> list[str]:
    return [link.attrs.get("href", "") for link in descendants(element, "a")]


def count_cards(section: Element, class_name: str) -> int:
    return len([item for item in descendants(section, "a") if has_class(item, class_name)])


def validate_garden_map(base_url: str, lang: str) -> tuple[list[str], dict[str, int]]:
    path = localized_path(lang, "garden-map")
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    stats = {
        "pages": 0,
        "quiz_scripts": 0,
        "hero_actions": 0,
        "saved_templates": 0,
        "saved_actions": 0,
        "handoff_cards": 0,
        "route_cards": 0,
        "tool_cards": 0,
        "guardian_cards": 0,
        "guide_cards": 0,
        "trust_cards": 0,
        "boundary_sections": 0,
    }
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["pages"] = 1
    parser = GardenMapParser()
    parser.feed(response.text)
    root = parser.root

    scripts = [src for src in parser.scripts if QUIZ_SRC_RE.match(src)]
    if len(scripts) != 1:
        issues.append(f"{path}: expected one localized quiz data script, found {scripts}")
    else:
        match = QUIZ_SRC_RE.match(scripts[0])
        if match and match.group(1) != lang:
            issues.append(f"{path}: expected {lang} quiz data, got {scripts[0]}")
        else:
            stats["quiz_scripts"] += 1

    hero = find_by_class(root, "garden-map-hero")
    if hero is None:
        issues.append(f"{path}: missing garden map hero")
    else:
        hrefs = hrefs_under(hero)
        for expected in (localized_path(lang) + "#quiz-section", localized_path(lang, "characters")):
            if expected not in hrefs:
                issues.append(f"{path}: hero missing action {expected}")
            else:
                stats["hero_actions"] += 1

    if "data-garden-map-saved" not in response.text or "garden-map-resume-card" not in response.text:
        issues.append(f"{path}: missing garden map resume template")
    else:
        stats["saved_templates"] += 1
    for snippet in (
        "result.resourceUrl",
        "result.planUrl",
        "result.collectorHallUrl",
        "result.lunaUrl",
        "result.contactUrl",
        "result.guardianUrl",
        "data-garden-map-contact",
        "data-clear-garden-map-result",
    ):
        if snippet not in response.text:
            issues.append(f"{path}: resume template missing {snippet}")
        else:
            stats["saved_actions"] += 1

    expected_sections = {
        "data-garden-map-handoff": ("garden-map-handoff-card", 4, "handoff_cards"),
        "data-garden-map-routes": ("garden-map-route-card", 4, "route_cards"),
        "data-garden-map-tools": ("garden-map-tool-card", 3, "tool_cards"),
        "data-garden-map-guardians": ("guardian-card", 5, "guardian_cards"),
        "data-garden-map-guides": ("content-card", len(GUIDE_SLUGS), "guide_cards"),
        "data-garden-map-trust": ("garden-map-trust-card", 4, "trust_cards"),
    }
    for attr, (class_name, expected_count, stat_key) in expected_sections.items():
        sections = find_all(root, attr=attr)
        if len(sections) != 1:
            issues.append(f"{path}: expected one section {attr}, got {len(sections)}")
            continue
        count = count_cards(sections[0], class_name)
        stats[stat_key] += count
        if count != expected_count:
            issues.append(f"{path}: expected {expected_count} {class_name}, got {count}")

    route_hrefs = hrefs_under(find_all(root, attr="data-garden-map-routes")[0]) if find_all(root, attr="data-garden-map-routes") else []
    for expected in (localized_path(lang) + "#quiz-section", localized_path(lang, "characters"), localized_path(lang, "resources"), localized_path(lang, "repair-plan")):
        if expected not in route_hrefs:
            issues.append(f"{path}: main routes missing {expected}")

    handoff_hrefs = hrefs_under(find_all(root, attr="data-garden-map-handoff")[0]) if find_all(root, attr="data-garden-map-handoff") else []
    for expected in (localized_path(lang, "resources"), localized_path(lang, "repair-plan"), localized_path(lang, "keepsakes"), localized_path(lang, "luna-yoga-music")):
        if expected not in handoff_hrefs:
            issues.append(f"{path}: handoff missing {expected}")

    tool_hrefs = hrefs_under(find_all(root, attr="data-garden-map-tools")[0]) if find_all(root, attr="data-garden-map-tools") else []
    for expected in (localized_path(lang, "repair-plan"), localized_path(lang, "keepsakes"), localized_path(lang, "luna-yoga-music")):
        if expected not in tool_hrefs:
            issues.append(f"{path}: function rooms missing {expected}")

    guardian_hrefs = hrefs_under(find_all(root, attr="data-garden-map-guardians")[0]) if find_all(root, attr="data-garden-map-guardians") else []
    for slug in GUARDIAN_SLUGS:
        expected = localized_path(lang, f"characters/{slug}")
        if expected not in guardian_hrefs:
            issues.append(f"{path}: guardian map missing {expected}")

    guide_hrefs = hrefs_under(find_all(root, attr="data-garden-map-guides")[0]) if find_all(root, attr="data-garden-map-guides") else []
    for slug in GUIDE_SLUGS:
        expected = localized_path(lang, f"guides/{slug}")
        if expected not in guide_hrefs:
            issues.append(f"{path}: guide lamps missing {expected}")

    trust_hrefs = hrefs_under(find_all(root, attr="data-garden-map-trust")[0]) if find_all(root, attr="data-garden-map-trust") else []
    for expected in (localized_path(lang, "about"), localized_path(lang, "theory"), localized_path(lang, "contact"), localized_path(lang, "privacy")):
        if expected not in trust_hrefs:
            issues.append(f"{path}: trust routes missing {expected}")

    if find_by_class(root, "note-section") is None:
        issues.append(f"{path}: missing boundary note section")
    else:
        stats["boundary_sections"] += 1
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes Heart Garden map routes.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    totals = {
        "pages": 0,
        "quiz_scripts": 0,
        "hero_actions": 0,
        "saved_templates": 0,
        "saved_actions": 0,
        "handoff_cards": 0,
        "route_cards": 0,
        "tool_cards": 0,
        "guardian_cards": 0,
        "guide_cards": 0,
        "trust_cards": 0,
        "boundary_sections": 0,
    }
    issues: list[str] = []
    for lang in LANG_PREFIXES:
        page_issues, stats = validate_garden_map(base_url, lang)
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"public_garden_map_pages_checked={totals['pages']}")
    print(f"public_garden_map_quiz_scripts_checked={totals['quiz_scripts']}")
    print(f"public_garden_map_hero_actions_checked={totals['hero_actions']}")
    print(f"public_garden_map_saved_templates_checked={totals['saved_templates']}")
    print(f"public_garden_map_saved_actions_checked={totals['saved_actions']}")
    print(f"public_garden_map_handoff_cards_checked={totals['handoff_cards']}")
    print(f"public_garden_map_route_cards_checked={totals['route_cards']}")
    print(f"public_garden_map_tool_cards_checked={totals['tool_cards']}")
    print(f"public_garden_map_guardian_cards_checked={totals['guardian_cards']}")
    print(f"public_garden_map_guide_cards_checked={totals['guide_cards']}")
    print(f"public_garden_map_trust_cards_checked={totals['trust_cards']}")
    print(f"public_garden_map_boundary_sections_checked={totals['boundary_sections']}")
    print(f"public_garden_map_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
