#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {
    "zh": "/",
    "en": "/en/",
    "ja": "/ja/",
    "ko": "/ko/",
    "es": "/es/",
}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
QUIZ_SRC_RE = re.compile(r"^/quiz-data-(zh|en|ja|ko|es)-[^/]+\.js$")
ASSIGNMENT_RE = re.compile(r"window\.__LOVETYPES_QUIZ_DATA\s*=\s*(\{.*\})\s*;?\s*$", re.S)
EXPECTED_TYPES = {"W", "T", "G", "S", "P"}
EXPECTED_RESULT_SLUGS = {"iris", "noah", "vivian", "claire", "dora"}


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


class HomeParser(HTMLParser):
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


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public home smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                return Response(raw.geturl(), raw.status, raw.read().decode("utf-8", errors="replace"))
        except HTTPError as error:
            return Response(error.geturl(), error.code, error.read().decode("utf-8", errors="replace"))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def localized_path(lang: str, route: str = "") -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    route = route.strip("/")
    if not route:
        return f"{prefix}/" if prefix else "/"
    return f"{prefix}/{route}/" if prefix else f"/{route}/"


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


def find_by_class(root: Element, class_name: str) -> Element | None:
    return next((element for element in walk(root) if has_class(element, class_name)), None)


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


def hrefs_under(element: Element) -> list[str]:
    return [link.attrs.get("href", "") for link in descendants(element, "a")]


def parse_quiz_data(path: str, text: str) -> tuple[dict, list[str]]:
    match = ASSIGNMENT_RE.match(text.strip())
    if not match:
        return {}, [f"{path}: missing window.__LOVETYPES_QUIZ_DATA assignment"]
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        return {}, [f"{path}: quiz data JSON is invalid: {error}"]
    if not isinstance(data, dict):
        return {}, [f"{path}: quiz data should be an object"]
    return data, []


def validate_quiz_asset(base_url: str, lang: str, script: str) -> tuple[list[str], dict[str, int]]:
    stats = {"quiz_scripts": 0, "quiz_questions": 0, "quiz_results": 0, "quiz_labels": 0}
    issues: list[str] = []
    response = request_url(urljoin(base_url + "/", script.lstrip("/")))
    if response.status != 200:
        return [f"{script}: expected status 200, got {response.status}"], stats
    data, parse_issues = parse_quiz_data(script, response.text)
    issues.extend(parse_issues)
    if parse_issues:
        return issues, stats
    stats["quiz_scripts"] = 1

    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != 15:
        issues.append(f"{script}: expected 15 questions, got {len(questions) if isinstance(questions, list) else 'invalid'}")
    else:
        for index, question in enumerate(questions, start=1):
            options = question.get("options") if isinstance(question, dict) else None
            option_types = [option.get("type") for option in options if isinstance(option, dict)] if isinstance(options, list) else []
            if len(option_types) != 5 or set(option_types) != EXPECTED_TYPES:
                issues.append(f"{script}: question {index} should contain W/T/G/S/P options once")
            else:
                stats["quiz_questions"] += 1

    results = data.get("results")
    if not isinstance(results, dict) or set(results) != EXPECTED_TYPES:
        issues.append(f"{script}: results should contain W/T/G/S/P")
    else:
        slugs = {result.get("slug") for result in results.values() if isinstance(result, dict)}
        if slugs != EXPECTED_RESULT_SLUGS:
            issues.append(f"{script}: result slugs should be {sorted(EXPECTED_RESULT_SLUGS)}, got {sorted(slugs)}")
        for result_type, result in results.items():
            if not isinstance(result, dict):
                issues.append(f"{script}: result {result_type} should be an object")
                continue
            required = ("guardianUrl", "resourceUrl", "planUrl", "lunaUrl", "collectorHallUrl", "supplyBookUrl")
            missing = [key for key in required if not isinstance(result.get(key), str) or not result.get(key, "").strip()]
            if missing:
                issues.append(f"{script}: result {result_type} missing {', '.join(missing)}")
                continue
            if not result["guardianUrl"].startswith(localized_path(lang, "characters")):
                issues.append(f"{script}: result {result_type} guardianUrl is not localized")
            if not result["resourceUrl"].startswith(localized_path(lang, "resources")):
                issues.append(f"{script}: result {result_type} resourceUrl is not localized")
            if not result["planUrl"].startswith(localized_path(lang, "repair-plan")):
                issues.append(f"{script}: result {result_type} planUrl is not localized")
            if not result["lunaUrl"].startswith(localized_path(lang, "luna-yoga-music")):
                issues.append(f"{script}: result {result_type} lunaUrl is not localized")
            stats["quiz_results"] += 1

    labels = data.get("labels")
    required_labels = ("primary_route", "secondary_plan", "next_pack_title", "saved_route", "saved_plan", "saved_luna", "saved_card")
    if not isinstance(labels, dict):
        issues.append(f"{script}: labels should be an object")
    else:
        for key in required_labels:
            if not isinstance(labels.get(key), str) or not labels.get(key, "").strip():
                issues.append(f"{script}: missing label {key}")
            else:
                stats["quiz_labels"] += 1
    return issues, stats


def validate_home(base_url: str, lang: str, path: str) -> tuple[list[str], dict[str, int]]:
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    stats = {
        "pages": 0,
        "quiz_roots": 0,
        "quiz_start_buttons": 0,
        "saved_templates": 0,
        "saved_actions": 0,
        "universe_gate_sections": 0,
        "universe_gate_cards": 0,
        "journey_sections": 0,
        "journey_cards": 0,
        "safety_sections": 0,
        "safety_links": 0,
        "hero_ctas": 0,
        "quiz_scripts": 0,
        "quiz_questions": 0,
        "quiz_results": 0,
        "quiz_labels": 0,
    }
    issues: list[str] = []
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["pages"] = 1

    parser = HomeParser()
    parser.feed(response.text)
    root = parser.root

    scripts = [src for src in parser.scripts if QUIZ_SRC_RE.match(src)]
    if len(scripts) != 1:
        issues.append(f"{path}: expected one quiz-data script, found {scripts}")
    else:
        match = QUIZ_SRC_RE.match(scripts[0])
        if match and match.group(1) != lang:
            issues.append(f"{path}: expected {lang} quiz data, got {scripts[0]}")
        script_issues, script_stats = validate_quiz_asset(base_url, lang, scripts[0])
        issues.extend(script_issues)
        for key, value in script_stats.items():
            stats[key] += value

    if not find_all(root, element_id="quiz-section"):
        issues.append(f"{path}: missing #quiz-section anchor")
    if not find_all(root, attr="data-quiz-root"):
        issues.append(f"{path}: missing data-quiz-root")
    else:
        stats["quiz_roots"] = 1
    if not find_all(root, attr="data-quiz-start"):
        issues.append(f"{path}: missing data-quiz-start")
    else:
        stats["quiz_start_buttons"] = 1

    if "data-home-saved" not in response.text or "data-resume-pass-stamp" not in response.text:
        issues.append(f"{path}: missing home saved-result template")
    else:
        stats["saved_templates"] = 1
    for attr in ("data-home-resume-route", "data-home-resume-plan", "data-home-resume-luna", "data-home-resume-contact", "data-home-resume-guardian", "data-home-saved-keepsake", "data-clear-home-result"):
        if attr not in response.text:
            issues.append(f"{path}: missing saved-result action {attr}")
        else:
            stats["saved_actions"] += 1

    hero = find_by_class(root, "hero")
    if hero is None:
        issues.append(f"{path}: missing home hero")
    else:
        hero_hrefs = hrefs_under(hero)
        for expected in ("#quiz-section", localized_path(lang, "garden-map")):
            if expected not in hero_hrefs:
                issues.append(f"{path}: hero missing CTA {expected}")
            else:
                stats["hero_ctas"] += 1

    gates = find_all(root, attr="data-universe-gates")
    if len(gates) != 1:
        issues.append(f"{path}: expected one universe gate section, got {len(gates)}")
    else:
        stats["universe_gate_sections"] = 1
        cards = [card for card in descendants(gates[0], "a") if has_class(card, "universe-gate-card")]
        stats["universe_gate_cards"] = len(cards)
        if len(cards) != len(GUARDIAN_SLUGS):
            issues.append(f"{path}: expected five universe gate cards, got {len(cards)}")
        for slug in GUARDIAN_SLUGS:
            expected_href = localized_path(lang, f"characters/{slug}")
            card = next((item for item in cards if item.attrs.get("data-guardian-domain") == slug), None)
            if card is None:
                issues.append(f"{path}: universe gate missing {slug}")
            elif card.attrs.get("href") != expected_href:
                issues.append(f"{path}: {slug} universe gate href should be {expected_href}, got {card.attrs.get('href')}")

    journeys = find_all(root, attr="data-home-journey")
    if len(journeys) != 1:
        issues.append(f"{path}: expected one home journey section, got {len(journeys)}")
    else:
        stats["journey_sections"] = 1
        cards = [card for card in descendants(journeys[0], "article") if has_class(card, "home-journey-card")]
        stats["journey_cards"] = len(cards)
        if len(cards) != 4:
            issues.append(f"{path}: expected four journey cards, got {len(cards)}")

    safety = find_all(root, attr="data-home-safety-compass")
    if len(safety) != 1:
        issues.append(f"{path}: expected one home safety compass, got {len(safety)}")
    else:
        stats["safety_sections"] = 1
        hrefs = set(hrefs_under(safety[0]))
        expected_hrefs = {
            localized_path(lang, "privacy"),
            localized_path(lang, "terms"),
            localized_path(lang, "contact") + "#site-repair-report",
        }
        for expected in expected_hrefs:
            if expected not in hrefs:
                issues.append(f"{path}: home safety compass missing {expected}")
            else:
                stats["safety_links"] += 1
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes home universe and quiz entry routes.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    totals = {
        "pages": 0,
        "quiz_scripts": 0,
        "quiz_questions": 0,
        "quiz_results": 0,
        "quiz_labels": 0,
        "quiz_roots": 0,
        "quiz_start_buttons": 0,
        "saved_templates": 0,
        "saved_actions": 0,
        "universe_gate_sections": 0,
        "universe_gate_cards": 0,
        "journey_sections": 0,
        "journey_cards": 0,
        "safety_sections": 0,
        "safety_links": 0,
        "hero_ctas": 0,
    }
    issues: list[str] = []
    for lang, path in LANG_PATHS.items():
        page_issues, stats = validate_home(base_url, lang, path)
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"public_home_pages_checked={totals['pages']}")
    print(f"public_home_quiz_scripts_checked={totals['quiz_scripts']}")
    print(f"public_home_quiz_questions_checked={totals['quiz_questions']}")
    print(f"public_home_quiz_results_checked={totals['quiz_results']}")
    print(f"public_home_quiz_labels_checked={totals['quiz_labels']}")
    print(f"public_home_quiz_roots_checked={totals['quiz_roots']}")
    print(f"public_home_quiz_start_buttons_checked={totals['quiz_start_buttons']}")
    print(f"public_home_saved_templates_checked={totals['saved_templates']}")
    print(f"public_home_saved_actions_checked={totals['saved_actions']}")
    print(f"public_home_universe_gate_sections_checked={totals['universe_gate_sections']}")
    print(f"public_home_universe_gate_cards_checked={totals['universe_gate_cards']}")
    print(f"public_home_journey_sections_checked={totals['journey_sections']}")
    print(f"public_home_journey_cards_checked={totals['journey_cards']}")
    print(f"public_home_safety_sections_checked={totals['safety_sections']}")
    print(f"public_home_safety_links_checked={totals['safety_links']}")
    print(f"public_home_hero_ctas_checked={totals['hero_ctas']}")
    print(f"public_home_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
