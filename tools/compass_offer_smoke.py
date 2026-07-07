#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {
    "zh": "/compass/",
    "en": "/en/compass/",
    "ja": "/ja/compass/",
    "ko": "/ko/compass/",
    "es": "/es/compass/",
}
SCRIPT_PATHS = ("/compass-tool-20260707.js",)
EXPECTED_TITLES = {
    "Your Emotional Love Pattern",
    "LoveTypes Compatibility Report",
    "BaZi Love Compatibility Report",
    "2026 Love Timing Report",
    "7-Day Relationship Repair Plan",
}
EXPECTED_PRICES = {"US$4.99", "US$9.99"}
HARD_VERDICT_PHRASES = (
    "一定會分手",
    "不能結婚",
    "命中注定不適合",
    "will definitely break up",
    "should not marry",
    "destined to fail",
)


class CompassParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hero_sections = 0
        self.hero_badges = 0
        self.hero_events = 0
        self.visual_layers = 0
        self.visual_events = 0
        self.guardian_strips = 0
        self.guardian_tiles = 0
        self.audience_panels = 0
        self.audience_cards = 0
        self.result_preview_sections = 0
        self.result_preview_cards = 0
        self.result_preview_events = 0
        self.in_offer_section = False
        self.offer_depth = 0
        self.offer_cards = 0
        self.offer_events = 0
        self.offer_hrefs: list[str] = []
        self.offer_text: list[str] = []
        self.faq_sections = 0
        self.faq_details = 0
        self.in_faq_section = False
        self.faq_depth = 0
        self.jsonld_blocks = 0
        self.in_jsonld = False
        self._jsonld_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        if "data-compass-landing-hero" in attr:
            self.hero_sections += 1
        if "data-compass-hero-badges" in attr:
            self.hero_badges += 1
        if "data-compass-visual-layer" in attr:
            self.visual_layers += 1
        if "data-compass-guardian-strip" in attr:
            self.guardian_strips += 1
        if "data-compass-guardian-tile" in attr:
            self.guardian_tiles += 1
        if "data-compass-audience-panel" in attr:
            self.audience_panels += 1
        if "data-compass-audience-card" in attr:
            self.audience_cards += 1
        if "data-compass-result-preview" in attr:
            self.result_preview_sections += 1
        if "data-compass-result-preview-card" in attr:
            self.result_preview_cards += 1
        if "data-compass-faq" in attr:
            self.faq_sections += 1
            self.in_faq_section = True
            self.faq_depth = 1
        elif self.in_faq_section:
            self.faq_depth += 1
        if self.in_faq_section and tag.lower() == "details":
            self.faq_details += 1
        if tag.lower() == "script" and attr.get("type") == "application/ld+json":
            self.in_jsonld = True
            self._jsonld_buf = []
        event = attr.get("data-funnel-event", "")
        if event.startswith("compass_hero_"):
            self.hero_events += 1
        if event in {"compass_visual_start", "compass_guardian_tile"}:
            self.visual_events += 1
        if event == "compass_result_preview_start":
            self.result_preview_events += 1
        if "data-compass-report-offers" in attr:
            self.in_offer_section = True
            self.offer_depth = 1
        elif self.in_offer_section:
            self.offer_depth += 1

        if not self.in_offer_section:
            return
        if "data-compass-report-offer" in attr:
            self.offer_cards += 1
        if tag.lower() == "a":
            if attr.get("data-funnel-event") == "compass_report_request":
                self.offer_events += 1
            self.offer_hrefs.append(attr.get("href", ""))

    def handle_endtag(self, tag: str) -> None:
        if self.in_jsonld and tag.lower() == "script":
            self.in_jsonld = False
            self.jsonld_blocks += 1
            self._jsonld_buf = []
        if self.in_faq_section:
            self.faq_depth -= 1
            if self.faq_depth <= 0:
                self.in_faq_section = False
                self.faq_depth = 0
        if not self.in_offer_section:
            return
        self.offer_depth -= 1
        if self.offer_depth <= 0:
            self.in_offer_section = False
            self.offer_depth = 0

    def handle_data(self, data: str) -> None:
        if self.in_jsonld:
            self._jsonld_buf.append(data)
        if self.in_offer_section and data.strip():
            self.offer_text.append(data.strip())


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_text(url: str, attempts: int = 3) -> tuple[int, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes compass offer smoke/1.0"})
            with urlopen(request, timeout=20) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8", errors="replace")
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def validate_page(base_url: str, path: str) -> tuple[list[str], dict[str, int]]:
    status, text = request_text(urljoin(base_url + "/", path.lstrip("/")))
    stats = {
        "pages": 0,
        "hero_sections": 0,
        "hero_badges": 0,
        "hero_events": 0,
        "visual_layers": 0,
        "visual_events": 0,
        "guardian_strips": 0,
        "guardian_tiles": 0,
        "audience_panels": 0,
        "audience_cards": 0,
        "result_preview_sections": 0,
        "result_preview_cards": 0,
        "result_preview_events": 0,
        "offer_sections": 0,
        "offer_cards": 0,
        "offer_events": 0,
        "mailto_links": 0,
        "prices": 0,
        "titles": 0,
        "boundary_phrases": 0,
        "faq_sections": 0,
        "faq_details": 0,
        "jsonld_blocks": 0,
    }
    issues: list[str] = []
    if status != 200:
        return [f"{path}: expected status 200, got {status}"], stats
    stats["pages"] = 1

    parser = CompassParser()
    parser.feed(text)
    stats["hero_sections"] = parser.hero_sections
    stats["hero_badges"] = parser.hero_badges
    stats["hero_events"] = parser.hero_events
    stats["visual_layers"] = parser.visual_layers
    stats["visual_events"] = parser.visual_events
    stats["guardian_strips"] = parser.guardian_strips
    stats["guardian_tiles"] = parser.guardian_tiles
    stats["audience_panels"] = parser.audience_panels
    stats["audience_cards"] = parser.audience_cards
    stats["result_preview_sections"] = parser.result_preview_sections
    stats["result_preview_cards"] = parser.result_preview_cards
    stats["result_preview_events"] = parser.result_preview_events
    stats["faq_sections"] = parser.faq_sections
    stats["faq_details"] = parser.faq_details
    stats["jsonld_blocks"] = parser.jsonld_blocks
    if parser.hero_sections != 1:
        issues.append(f"{path}: expected one compass landing hero, got {parser.hero_sections}")
    if parser.hero_badges != 1:
        issues.append(f"{path}: expected one compass hero badge group, got {parser.hero_badges}")
    if parser.hero_events != 3:
        issues.append(f"{path}: expected 3 compass hero CTA events, got {parser.hero_events}")
    if parser.visual_layers != 1:
        issues.append(f"{path}: expected one compass visual traffic layer, got {parser.visual_layers}")
    if parser.visual_events != 6:
        issues.append(f"{path}: expected 6 compass visual CTA events, got {parser.visual_events}")
    if parser.guardian_strips != 1:
        issues.append(f"{path}: expected one guardian visual strip, got {parser.guardian_strips}")
    if parser.guardian_tiles != 5:
        issues.append(f"{path}: expected 5 guardian visual tiles, got {parser.guardian_tiles}")
    if parser.audience_panels != 1:
        issues.append(f"{path}: expected one audience panel, got {parser.audience_panels}")
    if parser.audience_cards != 3:
        issues.append(f"{path}: expected 3 audience cards, got {parser.audience_cards}")
    if parser.result_preview_sections != 1:
        issues.append(f"{path}: expected one compass result preview section, got {parser.result_preview_sections}")
    if parser.result_preview_cards != 3:
        issues.append(f"{path}: expected 3 compass result preview cards, got {parser.result_preview_cards}")
    if parser.result_preview_events != 1:
        issues.append(f"{path}: expected one compass result preview CTA event, got {parser.result_preview_events}")
    if parser.faq_sections != 1:
        issues.append(f"{path}: expected one compass FAQ section, got {parser.faq_sections}")
    if parser.faq_details != 3:
        issues.append(f"{path}: expected 3 compass FAQ details, got {parser.faq_details}")
    if parser.jsonld_blocks < 2:
        issues.append(f"{path}: expected WebApplication and FAQ JSON-LD blocks, got {parser.jsonld_blocks}")

    offer_text = "\n".join(parser.offer_text)
    if not offer_text:
        issues.append(f"{path}: missing compass report offer section")
    else:
        stats["offer_sections"] = 1
    stats["offer_cards"] = parser.offer_cards
    stats["offer_events"] = parser.offer_events
    if parser.offer_cards != 5:
        issues.append(f"{path}: expected 5 compass report offer cards, got {parser.offer_cards}")
    if parser.offer_events != 5:
        issues.append(f"{path}: expected 5 compass report request events, got {parser.offer_events}")

    mailtos = [href for href in parser.offer_hrefs if href.startswith("mailto:contact@lovetypes.tw?")]
    stats["mailto_links"] = len(mailtos)
    if len(mailtos) != 5:
        issues.append(f"{path}: expected 5 report mailto links, got {len(mailtos)}")
    for href in mailtos:
        if "subject=" not in href or "body=" not in href:
            issues.append(f"{path}: report mailto missing subject/body: {href}")

    for title in EXPECTED_TITLES:
        if title in offer_text:
            stats["titles"] += 1
        else:
            issues.append(f"{path}: missing report title {title}")
    for price in EXPECTED_PRICES:
        if price in offer_text:
            stats["prices"] += 1
        else:
            issues.append(f"{path}: missing price {price}")
    boundary_hits = sum(
        1
        for phrase in ("不取代", "replace counseling", "代替しません", "대신하지 않습니다", "ni reemplaza")
        if phrase in offer_text
    )
    stats["boundary_phrases"] = boundary_hits
    if boundary_hits < 1:
        issues.append(f"{path}: report offer missing safety boundary wording")
    for phrase in HARD_VERDICT_PHRASES:
        if re.search(re.escape(phrase), offer_text, re.I):
            issues.append(f"{path}: report offer includes hard verdict phrase {phrase!r}")
    return issues, stats


def validate_result_template(base_url: str, path: str) -> tuple[list[str], dict[str, int]]:
    status, text = request_text(urljoin(base_url + "/", path.lstrip("/")))
    stats = {
        "scripts": 0,
        "result_offer_templates": 0,
        "result_offer_events": 0,
        "result_offer_mailtos": 0,
        "result_offer_subjects": 0,
        "result_offer_locales": 0,
    }
    issues: list[str] = []
    if status != 200:
        return [f"{path}: expected status 200, got {status}"], stats
    stats["scripts"] = 1

    required_markers = {
        "data-compass-result-offer": "result offer template",
        "data-compass-result-report-request": "result report request link",
        'data-funnel-event="compass_result_report_request"': "result report funnel event",
        "mailto:contact@lovetypes.tw?subject=": "result report mailto",
        "resultOfferSubject": "result offer subject label",
        "Free compass result:": "result report free summary",
        "Main cross-signal:": "result report cross-signal field",
        "24-hour action:": "result report action field",
        "Status: ": "result report status field",
        "Issue: ": "result report issue field",
    }
    for marker, label in required_markers.items():
        if marker not in text:
            issues.append(f"{path}: missing {label}")

    stats["result_offer_templates"] = text.count("data-compass-result-offer")
    stats["result_offer_events"] = text.count("compass_result_report_request")
    stats["result_offer_mailtos"] = text.count("mailto:contact@lovetypes.tw?subject=")
    stats["result_offer_subjects"] = text.count("resultOfferSubject")
    stats["result_offer_locales"] = text.count("resultOfferTitle")
    if stats["result_offer_templates"] < 1:
        issues.append(f"{path}: expected at least one result offer template")
    if stats["result_offer_events"] < 2:
        issues.append(f"{path}: expected markup and click tracking for compass_result_report_request")
    if stats["result_offer_mailtos"] < 1:
        issues.append(f"{path}: expected result report mailto template")
    if stats["result_offer_subjects"] < 5 or stats["result_offer_locales"] < 5:
        issues.append(f"{path}: expected localized result offer labels for five languages")
    for phrase in HARD_VERDICT_PHRASES:
        if re.search(re.escape(phrase), text, re.I):
            issues.append(f"{path}: result template includes hard verdict phrase {phrase!r}")
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check LoveTypes Relationship Compass report offer ladder.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    totals = {
        "pages": 0,
        "hero_sections": 0,
        "hero_badges": 0,
        "hero_events": 0,
        "visual_layers": 0,
        "visual_events": 0,
        "guardian_strips": 0,
        "guardian_tiles": 0,
        "audience_panels": 0,
        "audience_cards": 0,
        "result_preview_sections": 0,
        "result_preview_cards": 0,
        "result_preview_events": 0,
        "offer_sections": 0,
        "offer_cards": 0,
        "offer_events": 0,
        "mailto_links": 0,
        "prices": 0,
        "titles": 0,
        "boundary_phrases": 0,
        "faq_sections": 0,
        "faq_details": 0,
        "jsonld_blocks": 0,
        "scripts": 0,
        "result_offer_templates": 0,
        "result_offer_events": 0,
        "result_offer_mailtos": 0,
        "result_offer_subjects": 0,
        "result_offer_locales": 0,
    }
    issues: list[str] = []
    for path in LANG_PATHS.values():
        page_issues, stats = validate_page(base_url, path)
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value
    for path in SCRIPT_PATHS:
        script_issues, stats = validate_result_template(base_url, path)
        issues.extend(script_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"compass_offer_pages_checked={totals['pages']}")
    print(f"compass_offer_hero_sections_checked={totals['hero_sections']}")
    print(f"compass_offer_hero_badges_checked={totals['hero_badges']}")
    print(f"compass_offer_hero_events_checked={totals['hero_events']}")
    print(f"compass_offer_visual_layers_checked={totals['visual_layers']}")
    print(f"compass_offer_visual_events_checked={totals['visual_events']}")
    print(f"compass_offer_guardian_strips_checked={totals['guardian_strips']}")
    print(f"compass_offer_guardian_tiles_checked={totals['guardian_tiles']}")
    print(f"compass_offer_audience_panels_checked={totals['audience_panels']}")
    print(f"compass_offer_audience_cards_checked={totals['audience_cards']}")
    print(f"compass_offer_result_preview_sections_checked={totals['result_preview_sections']}")
    print(f"compass_offer_result_preview_cards_checked={totals['result_preview_cards']}")
    print(f"compass_offer_result_preview_events_checked={totals['result_preview_events']}")
    print(f"compass_offer_sections_checked={totals['offer_sections']}")
    print(f"compass_offer_cards_checked={totals['offer_cards']}")
    print(f"compass_offer_events_checked={totals['offer_events']}")
    print(f"compass_offer_mailto_links_checked={totals['mailto_links']}")
    print(f"compass_offer_prices_checked={totals['prices']}")
    print(f"compass_offer_titles_checked={totals['titles']}")
    print(f"compass_offer_boundary_phrases_checked={totals['boundary_phrases']}")
    print(f"compass_offer_faq_sections_checked={totals['faq_sections']}")
    print(f"compass_offer_faq_details_checked={totals['faq_details']}")
    print(f"compass_offer_jsonld_blocks_checked={totals['jsonld_blocks']}")
    print(f"compass_offer_result_scripts_checked={totals['scripts']}")
    print(f"compass_offer_result_templates_checked={totals['result_offer_templates']}")
    print(f"compass_offer_result_events_checked={totals['result_offer_events']}")
    print(f"compass_offer_result_mailtos_checked={totals['result_offer_mailtos']}")
    print(f"compass_offer_result_subjects_checked={totals['result_offer_subjects']}")
    print(f"compass_offer_result_locales_checked={totals['result_offer_locales']}")
    print(f"compass_offer_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
