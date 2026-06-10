#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {
    "zh": "/repair-plan/",
    "en": "/en/repair-plan/",
    "ja": "/ja/repair-plan/",
    "ko": "/ko/repair-plan/",
    "es": "/es/repair-plan/",
}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
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


class RepairPlanParser(HTMLParser):
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


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public repair plan smoke/1.0"})
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


def find_by_id(root: Element, element_id: str) -> Element | None:
    return next((element for element in walk(root) if element.attrs.get("id") == element_id), None)


def find_all(root: Element, *, tag: str | None = None, class_name: str | None = None, attr: str | None = None) -> list[Element]:
    items = walk(root)
    if tag:
        items = [item for item in items if item.tag == tag]
    if class_name:
        items = [item for item in items if has_class(item, class_name)]
    if attr:
        items = [item for item in items if attr in item.attrs]
    return items


def localized_path(lang: str, route: str = "") -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    route = route.strip("/")
    if not route:
        return f"{prefix}/" if prefix else "/"
    return f"{prefix}/{route}/" if prefix else f"/{route}/"


def is_affiliate_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == BOOKS_HOST and all(token in value for token in AFFILIATE_TOKENS)


def validate_page(base_url: str, lang: str, path: str) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "pages": 0,
        "day_cards": 0,
        "worksheet_fields": 0,
        "worksheet_actions": 0,
        "asset_sections": 0,
        "asset_cards": 0,
        "asset_links": 0,
        "guardian_cards": 0,
        "guardian_supply_links": 0,
        "guardian_character_links": 0,
        "guardian_luna_links": 0,
        "guardian_affiliate_links": 0,
        "resume_templates": 0,
        "safety_sections": 0,
    }
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["pages"] = 1
    parser = RepairPlanParser()
    parser.feed(response.text)
    root = parser.root

    if "data-repair-saved" not in response.text or "data-fill-repair" not in response.text:
        issues.append(f"{path}: missing saved result repair resume template")
    else:
        stats["resume_templates"] += 1

    asset_section = find_by_id(root, "repair-card-pack")
    if asset_section is None:
        issues.append(f"{path}: missing repair card pack asset section")
    else:
        stats["asset_sections"] += 1
        if not has_class(asset_section, "repair-asset-section"):
            issues.append(f"{path}: #repair-card-pack should be repair-asset-section")
        asset_cards = [card for card in descendants(asset_section, "article") if has_class(card, "repair-asset-card")]
        stats["asset_cards"] += len(asset_cards)
        if len(asset_cards) != 3:
            issues.append(f"{path}: expected three repair asset cards, got {len(asset_cards)}")
        asset_hrefs = [link.attrs.get("href", "") for link in descendants(asset_section, "a")]
        expected_asset_links = {
            localized_path(lang, "keepsakes"),
            "#repair-worksheet",
            localized_path(lang, "contact").rstrip("/") + "#luna-supply-request",
        }
        for expected in expected_asset_links:
            if expected in asset_hrefs:
                stats["asset_links"] += 1
            else:
                issues.append(f"{path}: repair asset pack missing link {expected}")
        hero_hrefs = [link.attrs.get("href", "") for link in descendants(root, "a")]
        if "#repair-card-pack" not in hero_hrefs:
            issues.append(f"{path}: missing hero link to repair card pack")

    day_section = next((item for item in walk(root) if has_class(item, "repair-plan-section")), None)
    if day_section is None:
        issues.append(f"{path}: missing repair plan day route section")
    else:
        day_cards = descendants(day_section, "article")
        stats["day_cards"] += len(day_cards)
        if len(day_cards) != 7:
            issues.append(f"{path}: expected seven day cards, got {len(day_cards)}")

    worksheet = next((item for item in walk(root) if item.attrs.get("data-repair-worksheet") == ""), None)
    if worksheet is None:
        issues.append(f"{path}: missing repair worksheet form")
    else:
        fields = [field for field in descendants(worksheet, "textarea") if "data-field" in field.attrs]
        stats["worksheet_fields"] += len(fields)
        if len(fields) != 4:
            issues.append(f"{path}: expected four worksheet textarea fields, got {len(fields)}")
        field_indexes = {field.attrs.get("data-field") for field in fields}
        if field_indexes != {"0", "1", "2", "3"}:
            issues.append(f"{path}: worksheet fields should be indexed 0-3, got {sorted(field_indexes)}")
    for marker in ("data-copy-worksheet-summary", "data-clear-worksheet"):
        if marker not in response.text:
            issues.append(f"{path}: missing worksheet action {marker}")
        else:
            stats["worksheet_actions"] += 1
    if "onclick=\"window.print()\"" not in response.text:
        issues.append(f"{path}: missing print/save button")
    else:
        stats["worksheet_actions"] += 1
    if "data-worksheet-status" not in response.text or 'aria-live="polite"' not in response.text:
        issues.append(f"{path}: worksheet status should be an aria-live polite region")
    else:
        stats["worksheet_actions"] += 1

    if "affiliate-disclosure" not in response.text:
        issues.append(f"{path}: missing affiliate disclosure")
    if "not_now" in response.text:
        issues.append(f"{path}: unexpected untranslated not_now token")
    if "supply" not in response.text or "LoveTypes" not in response.text:
        issues.append(f"{path}: repair plan page body looks incomplete")
    trust_section = next((item for item in walk(root) if has_class(item, "intro-grid")), None)
    if trust_section is None:
        issues.append(f"{path}: missing boundary and no-buy safety section")
    else:
        stats["safety_sections"] += 1

    for slug in GUARDIAN_SLUGS:
        card = find_by_id(root, f"plan-{slug}")
        if card is None:
            issues.append(f"{path}: missing #plan-{slug} guardian repair card")
            continue
        if not has_class(card, "repair-guardian-card"):
            issues.append(f"{path}: #plan-{slug} should be repair-guardian-card")
        stats["guardian_cards"] += 1
        hrefs = [link.attrs.get("href", "") for link in descendants(card, "a")]
        supply = localized_path(lang, "resources") + f"#supply-{slug}"
        character = localized_path(lang, f"characters/{slug}")
        luna = localized_path(lang, "luna-yoga-music") + f"#luna-{slug}"
        if supply in hrefs:
            stats["guardian_supply_links"] += 1
        else:
            issues.append(f"{path}: {slug} repair card missing supply link")
        if character in hrefs:
            stats["guardian_character_links"] += 1
        else:
            issues.append(f"{path}: {slug} repair card missing character link")
        if luna in hrefs:
            stats["guardian_luna_links"] += 1
        else:
            issues.append(f"{path}: {slug} repair card missing Luna link")
        affiliates = [link for link in descendants(card, "a") if is_affiliate_url(link.attrs.get("href", ""))]
        if len(affiliates) != 1:
            issues.append(f"{path}: {slug} repair card should include one tracked affiliate book link, got {len(affiliates)}")
        else:
            stats["guardian_affiliate_links"] += 1
            rel_tokens = set(affiliates[0].attrs.get("rel", "").split())
            if not {"noopener", "noreferrer", "sponsored"}.issubset(rel_tokens):
                issues.append(f"{path}: {slug} affiliate link missing safe sponsored rel")

    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes repair plan worksheet and guardian repair routes.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    issues: list[str] = []
    totals = {
        "pages": 0,
        "day_cards": 0,
        "worksheet_fields": 0,
        "worksheet_actions": 0,
        "asset_sections": 0,
        "asset_cards": 0,
        "asset_links": 0,
        "guardian_cards": 0,
        "guardian_supply_links": 0,
        "guardian_character_links": 0,
        "guardian_luna_links": 0,
        "guardian_affiliate_links": 0,
        "resume_templates": 0,
        "safety_sections": 0,
    }
    for lang, path in LANG_PATHS.items():
        page_issues, stats = validate_page(base_url, lang, path)
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"public_repair_plan_pages_checked={totals['pages']}")
    print(f"public_repair_plan_day_cards_checked={totals['day_cards']}")
    print(f"public_repair_plan_worksheet_fields_checked={totals['worksheet_fields']}")
    print(f"public_repair_plan_worksheet_actions_checked={totals['worksheet_actions']}")
    print(f"public_repair_plan_asset_sections_checked={totals['asset_sections']}")
    print(f"public_repair_plan_asset_cards_checked={totals['asset_cards']}")
    print(f"public_repair_plan_asset_links_checked={totals['asset_links']}")
    print(f"public_repair_plan_guardian_cards_checked={totals['guardian_cards']}")
    print(f"public_repair_plan_guardian_supply_links_checked={totals['guardian_supply_links']}")
    print(f"public_repair_plan_guardian_character_links_checked={totals['guardian_character_links']}")
    print(f"public_repair_plan_guardian_luna_links_checked={totals['guardian_luna_links']}")
    print(f"public_repair_plan_guardian_affiliate_links_checked={totals['guardian_affiliate_links']}")
    print(f"public_repair_plan_resume_templates_checked={totals['resume_templates']}")
    print(f"public_repair_plan_safety_sections_checked={totals['safety_sections']}")
    print(f"public_repair_plan_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
