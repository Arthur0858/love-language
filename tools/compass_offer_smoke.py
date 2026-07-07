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
        self.intent_fast_track_sections = 0
        self.intent_fast_track_cards = 0
        self.result_preview_sections = 0
        self.result_preview_cards = 0
        self.result_preview_events = 0
        self.popular_pairing_sections = 0
        self.popular_pairing_cards = 0
        self.popular_pairing_events = 0
        self.situation_route_sections = 0
        self.situation_route_cards = 0
        self.situation_route_events = 0
        self.pair_matrix_sections = 0
        self.pair_matrix_cards = 0
        self.pair_matrix_events = 0
        self.use_flow_sections = 0
        self.use_flow_steps = 0
        self.use_flow_events = 0
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
        if "data-compass-intent-fast-track" in attr:
            self.intent_fast_track_sections += 1
        if "data-compass-intent-card" in attr:
            self.intent_fast_track_cards += 1
        if "data-compass-result-preview" in attr:
            self.result_preview_sections += 1
        if "data-compass-result-preview-card" in attr:
            self.result_preview_cards += 1
        if "data-compass-popular-pairings" in attr:
            self.popular_pairing_sections += 1
        if "data-compass-popular-pair" in attr:
            self.popular_pairing_cards += 1
        if "data-compass-situation-routes" in attr:
            self.situation_route_sections += 1
        if "data-compass-situation-route" in attr:
            self.situation_route_cards += 1
        if "data-compass-pair-matrix" in attr:
            if tag.lower() == "section":
                self.pair_matrix_sections += 1
            else:
                self.pair_matrix_cards += 1
        if "data-compass-use-flow" in attr:
            self.use_flow_sections += 1
        if "data-compass-use-flow-step" in attr:
            self.use_flow_steps += 1
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
        if event in {"compass_popular_pair", "compass_popular_pair_tool"}:
            self.popular_pairing_events += 1
        if event in {"compass_situation_route", "compass_situation_tool"}:
            self.situation_route_events += 1
        if event in {"compass_pair_matrix", "compass_pair_matrix_tool"}:
            self.pair_matrix_events += 1
        if event == "compass_use_flow_start":
            self.use_flow_events += 1
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
        "intent_fast_track_sections": 0,
        "intent_fast_track_cards": 0,
        "result_preview_sections": 0,
        "result_preview_cards": 0,
        "result_preview_events": 0,
        "popular_pairing_sections": 0,
        "popular_pairing_cards": 0,
        "popular_pairing_events": 0,
        "situation_route_sections": 0,
        "situation_route_cards": 0,
        "situation_route_events": 0,
        "pair_matrix_sections": 0,
        "pair_matrix_cards": 0,
        "pair_matrix_events": 0,
        "use_flow_sections": 0,
        "use_flow_steps": 0,
        "use_flow_events": 0,
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
    stats["intent_fast_track_sections"] = parser.intent_fast_track_sections
    stats["intent_fast_track_cards"] = parser.intent_fast_track_cards
    stats["result_preview_sections"] = parser.result_preview_sections
    stats["result_preview_cards"] = parser.result_preview_cards
    stats["result_preview_events"] = parser.result_preview_events
    if parser.intent_fast_track_sections != 1:
        issues.append(f"{path}: expected 1 intent fast-track section, got {parser.intent_fast_track_sections}")
    if parser.intent_fast_track_cards != 6:
        issues.append(f"{path}: expected 6 intent fast-track cards, got {parser.intent_fast_track_cards}")
    stats["popular_pairing_sections"] = parser.popular_pairing_sections
    stats["popular_pairing_cards"] = parser.popular_pairing_cards
    stats["popular_pairing_events"] = parser.popular_pairing_events
    stats["situation_route_sections"] = parser.situation_route_sections
    stats["situation_route_cards"] = parser.situation_route_cards
    stats["situation_route_events"] = parser.situation_route_events
    stats["pair_matrix_sections"] = parser.pair_matrix_sections
    stats["pair_matrix_cards"] = parser.pair_matrix_cards
    stats["pair_matrix_events"] = parser.pair_matrix_events
    stats["use_flow_sections"] = parser.use_flow_sections
    stats["use_flow_steps"] = parser.use_flow_steps
    stats["use_flow_events"] = parser.use_flow_events
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
    if parser.popular_pairing_sections != 1:
        issues.append(f"{path}: expected one popular pairing section, got {parser.popular_pairing_sections}")
    if parser.popular_pairing_cards != 5:
        issues.append(f"{path}: expected 5 popular pairing cards, got {parser.popular_pairing_cards}")
    if parser.popular_pairing_events != 6:
        issues.append(f"{path}: expected 6 popular pairing events, got {parser.popular_pairing_events}")
    if parser.situation_route_sections != 1:
        issues.append(f"{path}: expected one situation route section, got {parser.situation_route_sections}")
    if parser.situation_route_cards != 4:
        issues.append(f"{path}: expected 4 situation route cards, got {parser.situation_route_cards}")
    if parser.situation_route_events != 5:
        issues.append(f"{path}: expected 5 situation route events, got {parser.situation_route_events}")
    if parser.pair_matrix_sections != 1:
        issues.append(f"{path}: expected one pair matrix section, got {parser.pair_matrix_sections}")
    if parser.pair_matrix_cards != 25:
        issues.append(f"{path}: expected 25 pair matrix cards, got {parser.pair_matrix_cards}")
    if parser.pair_matrix_events != 26:
        issues.append(f"{path}: expected 26 pair matrix events, got {parser.pair_matrix_events}")
    if parser.use_flow_sections != 1:
        issues.append(f"{path}: expected one compass use flow section, got {parser.use_flow_sections}")
    if parser.use_flow_steps != 3:
        issues.append(f"{path}: expected 3 compass use flow steps, got {parser.use_flow_steps}")
    if parser.use_flow_events != 1:
        issues.append(f"{path}: expected one compass use flow CTA event, got {parser.use_flow_events}")
    if parser.faq_sections != 1:
        issues.append(f"{path}: expected one compass FAQ section, got {parser.faq_sections}")
    if parser.faq_details != 5:
        issues.append(f"{path}: expected 5 compass FAQ details, got {parser.faq_details}")
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
        "result_copy_templates": 0,
        "result_copy_events": 0,
        "result_copy_payloads": 0,
        "result_copy_labels": 0,
        "result_share_link_templates": 0,
        "result_share_link_events": 0,
        "result_share_link_labels": 0,
        "result_next_step_templates": 0,
        "result_next_step_events": 0,
        "result_next_step_labels": 0,
        "result_query_prefill_helpers": 0,
        "result_prefill_notice_templates": 0,
        "result_prefill_events": 0,
        "result_prefill_labels": 0,
        "result_prefill_copy_templates": 0,
        "result_prefill_copy_events": 0,
    }
    issues: list[str] = []
    if status != 200:
        return [f"{path}: expected status 200, got {status}"], stats
    stats["scripts"] = 1

    required_markers = {
        "data-compass-result-offer": "result offer template",
        "data-compass-result-report-request": "result report request link",
        'data-funnel-event="compass_result_report_request"': "result report funnel event",
        "data-compass-result-share": "result share template",
        "data-compass-result-copy": "result copy button",
        'data-funnel-event="compass_result_copy"': "result copy funnel event",
        'data-copy-text=""': "result copy payload placeholder",
        "data-compass-result-share-link": "result share link button",
        'data-funnel-event="compass_result_share_link"': "result share link funnel event",
        "function compassPrefillUrl": "result prefill URL builder",
        "function resultShareText": "result share text builder",
        "function copyText": "result copy helper",
        "copyResultIntro": "result copy intro label",
        "copyResultLink": "result share link localized label",
        "copiedResultLink": "result share link copied localized label",
        "data-compass-result-next-steps": "result next-step template",
        "data-compass-result-next-link": "result next-step links",
        'data-funnel-event="compass_result_guardian"': "result guardian next-step funnel event",
        'data-funnel-event="compass_result_repair"': "result repair next-step funnel event",
        'data-funnel-event="compass_result_supply"': "result supply next-step funnel event",
        "function localizedPath": "localized next-step path helper",
        "function guardianSlug": "guardian slug helper",
        "nextStepsTitle": "result next-step localized labels",
        "function applyQueryPrefill": "query prefill helper",
        "function recordFunnelEventWhenReady": "query prefill funnel retry helper",
        "new URLSearchParams": "query string parser",
        "applyQueryPrefill();": "query prefill initializer",
        "data-compass-prefill-notice": "query prefill notice",
        "data-compass-prefill-copy-link": "query prefill copy link",
        "compass_prefill_pair": "query prefill funnel event",
        "compass_prefill_copy_link": "query prefill copy link funnel event",
        "prefillTitle": "query prefill localized title",
        "prefillIntro": "query prefill localized intro",
        "prefillCopyLink": "query prefill copy localized label",
        "prefillCopiedLink": "query prefill copied localized label",
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
    stats["result_copy_templates"] = text.count("data-compass-result-share")
    stats["result_copy_events"] = text.count("compass_result_copy")
    stats["result_copy_payloads"] = text.count("data-copy-text")
    result_copy_label_keys = ("copyResult:", "copyResultIntro:", "copiedResult:", "copyUnavailable:")
    stats["result_copy_labels"] = sum(text.count(key) for key in result_copy_label_keys)
    stats["result_share_link_templates"] = text.count("data-compass-result-share-link")
    stats["result_share_link_events"] = text.count("compass_result_share_link")
    result_share_link_label_keys = ("copyResultLink:", "copiedResultLink:")
    stats["result_share_link_labels"] = sum(text.count(key) for key in result_share_link_label_keys)
    stats["result_next_step_templates"] = text.count("data-compass-result-next-steps")
    stats["result_next_step_events"] = sum(
        text.count(name)
        for name in (
            "compass_result_guardian",
            "compass_result_repair",
            "compass_result_supply",
        )
    )
    result_next_step_label_keys = (
        "nextStepsTitle:",
        "nextStepsIntro:",
        "nextStepsGuardian:",
        "nextStepsRepair:",
        "nextStepsSupply:",
    )
    stats["result_next_step_labels"] = sum(text.count(key) for key in result_next_step_label_keys)
    stats["result_query_prefill_helpers"] = sum(
        text.count(marker)
        for marker in (
            "function applyQueryPrefill",
            "function recordFunnelEventWhenReady",
            "new URLSearchParams",
            "applyQueryPrefill();",
        )
    )
    stats["result_prefill_notice_templates"] = text.count("data-compass-prefill-notice")
    stats["result_prefill_events"] = text.count("compass_prefill_pair")
    result_prefill_label_keys = ("prefillTitle:", "prefillIntro:", "prefillCopyLink:", "prefillCopiedLink:")
    stats["result_prefill_labels"] = sum(text.count(key) for key in result_prefill_label_keys)
    stats["result_prefill_copy_templates"] = text.count("data-compass-prefill-copy-link")
    stats["result_prefill_copy_events"] = text.count("compass_prefill_copy_link")
    if stats["result_offer_templates"] < 1:
        issues.append(f"{path}: expected at least one result offer template")
    if stats["result_offer_events"] < 2:
        issues.append(f"{path}: expected markup and click tracking for compass_result_report_request")
    if stats["result_offer_mailtos"] < 1:
        issues.append(f"{path}: expected result report mailto template")
    if stats["result_offer_subjects"] < 5 or stats["result_offer_locales"] < 5:
        issues.append(f"{path}: expected localized result offer labels for five languages")
    if stats["result_copy_templates"] < 1:
        issues.append(f"{path}: expected result copy template")
    if stats["result_copy_events"] < 1:
        issues.append(f"{path}: expected markup event for compass_result_copy")
    if stats["result_copy_payloads"] < 1:
        issues.append(f"{path}: expected result copy data-copy-text payload")
    if stats["result_copy_labels"] < 20:
        issues.append(f"{path}: expected localized copy labels for five languages")
    if stats["result_share_link_templates"] < 1:
        issues.append(f"{path}: expected result share link button")
    if stats["result_share_link_events"] < 1:
        issues.append(f"{path}: expected compass_result_share_link event")
    if stats["result_share_link_labels"] < 10:
        issues.append(f"{path}: expected localized result share link labels for five languages")
    if stats["result_next_step_templates"] < 1:
        issues.append(f"{path}: expected result next-step template")
    if stats["result_next_step_events"] < 3:
        issues.append(f"{path}: expected guardian, repair, and supply next-step events")
    if stats["result_next_step_labels"] < 25:
        issues.append(f"{path}: expected localized next-step labels for five languages")
    if stats["result_query_prefill_helpers"] < 4:
        issues.append(f"{path}: expected query prefill helper, retry helper, parser, and initializer")
    if stats["result_prefill_notice_templates"] < 1:
        issues.append(f"{path}: expected query prefill notice template")
    if stats["result_prefill_events"] < 1:
        issues.append(f"{path}: expected compass_prefill_pair event")
    if stats["result_prefill_labels"] < 20:
        issues.append(f"{path}: expected localized prefill labels for five languages")
    if stats["result_prefill_copy_templates"] < 1:
        issues.append(f"{path}: expected prefill copy link button")
    if stats["result_prefill_copy_events"] < 1:
        issues.append(f"{path}: expected compass_prefill_copy_link event")
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
        "intent_fast_track_sections": 0,
        "intent_fast_track_cards": 0,
        "result_preview_sections": 0,
        "result_preview_cards": 0,
        "result_preview_events": 0,
        "popular_pairing_sections": 0,
        "popular_pairing_cards": 0,
        "popular_pairing_events": 0,
        "situation_route_sections": 0,
        "situation_route_cards": 0,
        "situation_route_events": 0,
        "pair_matrix_sections": 0,
        "pair_matrix_cards": 0,
        "pair_matrix_events": 0,
        "use_flow_sections": 0,
        "use_flow_steps": 0,
        "use_flow_events": 0,
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
        "result_copy_templates": 0,
        "result_copy_events": 0,
        "result_copy_payloads": 0,
        "result_copy_labels": 0,
        "result_share_link_templates": 0,
        "result_share_link_events": 0,
        "result_share_link_labels": 0,
        "result_next_step_templates": 0,
        "result_next_step_events": 0,
        "result_next_step_labels": 0,
        "result_query_prefill_helpers": 0,
        "result_prefill_notice_templates": 0,
        "result_prefill_events": 0,
        "result_prefill_labels": 0,
        "result_prefill_copy_templates": 0,
        "result_prefill_copy_events": 0,
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
    print(f"compass_offer_intent_fast_track_sections_checked={totals['intent_fast_track_sections']}")
    print(f"compass_offer_intent_fast_track_cards_checked={totals['intent_fast_track_cards']}")
    print(f"compass_offer_result_preview_sections_checked={totals['result_preview_sections']}")
    print(f"compass_offer_result_preview_cards_checked={totals['result_preview_cards']}")
    print(f"compass_offer_result_preview_events_checked={totals['result_preview_events']}")
    print(f"compass_offer_popular_pairing_sections_checked={totals['popular_pairing_sections']}")
    print(f"compass_offer_popular_pairing_cards_checked={totals['popular_pairing_cards']}")
    print(f"compass_offer_popular_pairing_events_checked={totals['popular_pairing_events']}")
    print(f"compass_offer_situation_route_sections_checked={totals['situation_route_sections']}")
    print(f"compass_offer_situation_route_cards_checked={totals['situation_route_cards']}")
    print(f"compass_offer_situation_route_events_checked={totals['situation_route_events']}")
    print(f"compass_offer_pair_matrix_sections_checked={totals['pair_matrix_sections']}")
    print(f"compass_offer_pair_matrix_cards_checked={totals['pair_matrix_cards']}")
    print(f"compass_offer_pair_matrix_events_checked={totals['pair_matrix_events']}")
    print(f"compass_offer_use_flow_sections_checked={totals['use_flow_sections']}")
    print(f"compass_offer_use_flow_steps_checked={totals['use_flow_steps']}")
    print(f"compass_offer_use_flow_events_checked={totals['use_flow_events']}")
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
    print(f"compass_offer_result_copy_templates_checked={totals['result_copy_templates']}")
    print(f"compass_offer_result_copy_events_checked={totals['result_copy_events']}")
    print(f"compass_offer_result_copy_payloads_checked={totals['result_copy_payloads']}")
    print(f"compass_offer_result_copy_labels_checked={totals['result_copy_labels']}")
    print(f"compass_offer_result_share_link_templates_checked={totals['result_share_link_templates']}")
    print(f"compass_offer_result_share_link_events_checked={totals['result_share_link_events']}")
    print(f"compass_offer_result_share_link_labels_checked={totals['result_share_link_labels']}")
    print(f"compass_offer_result_next_step_templates_checked={totals['result_next_step_templates']}")
    print(f"compass_offer_result_next_step_events_checked={totals['result_next_step_events']}")
    print(f"compass_offer_result_next_step_labels_checked={totals['result_next_step_labels']}")
    print(f"compass_offer_result_query_prefill_helpers_checked={totals['result_query_prefill_helpers']}")
    print(f"compass_offer_result_prefill_notice_templates_checked={totals['result_prefill_notice_templates']}")
    print(f"compass_offer_result_prefill_events_checked={totals['result_prefill_events']}")
    print(f"compass_offer_result_prefill_labels_checked={totals['result_prefill_labels']}")
    print(f"compass_offer_result_prefill_copy_templates_checked={totals['result_prefill_copy_templates']}")
    print(f"compass_offer_result_prefill_copy_events_checked={totals['result_prefill_copy_events']}")
    print(f"compass_offer_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
