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
    "zh": "/tools/love-compatibility/",
    "en": "/en/tools/love-compatibility/",
    "ja": "/ja/tools/love-compatibility/",
    "ko": "/ko/tools/love-compatibility/",
    "es": "/es/tools/love-compatibility/",
}
LONG_TAIL_PATHS = {
    "zh": ("/tools/bazi-love-compatibility/", "/tools/2026-love-timing/", "/tools/long-distance-fight-repair/", "/tools/love-language-compatibility/", "/tools/relationship-compatibility-test/", "/tools/couples-communication-quiz/", "/tools/relationship-repair-after-fight/", "/tools/emotional-distance-relationship/", "/tools/trust-issues-relationship/", "/tools/insecure-in-relationship/", "/tools/silent-treatment-relationship/", "/tools/breakup-signs-relationship/", "/tools/feeling-misunderstood-relationship/", "/tools/partner-wont-communicate/", "/tools/one-sided-relationship/"),
    "en": ("/en/tools/bazi-love-compatibility/", "/en/tools/2026-love-timing/", "/en/tools/long-distance-fight-repair/", "/en/tools/love-language-compatibility/", "/en/tools/relationship-compatibility-test/", "/en/tools/couples-communication-quiz/", "/en/tools/relationship-repair-after-fight/", "/en/tools/emotional-distance-relationship/", "/en/tools/trust-issues-relationship/", "/en/tools/insecure-in-relationship/", "/en/tools/silent-treatment-relationship/", "/en/tools/breakup-signs-relationship/", "/en/tools/feeling-misunderstood-relationship/", "/en/tools/partner-wont-communicate/", "/en/tools/one-sided-relationship/"),
    "ja": ("/ja/tools/bazi-love-compatibility/", "/ja/tools/2026-love-timing/", "/ja/tools/long-distance-fight-repair/", "/ja/tools/love-language-compatibility/", "/ja/tools/relationship-compatibility-test/", "/ja/tools/couples-communication-quiz/", "/ja/tools/relationship-repair-after-fight/", "/ja/tools/emotional-distance-relationship/", "/ja/tools/trust-issues-relationship/", "/ja/tools/insecure-in-relationship/", "/ja/tools/silent-treatment-relationship/", "/ja/tools/breakup-signs-relationship/", "/ja/tools/feeling-misunderstood-relationship/", "/ja/tools/partner-wont-communicate/", "/ja/tools/one-sided-relationship/"),
    "ko": ("/ko/tools/bazi-love-compatibility/", "/ko/tools/2026-love-timing/", "/ko/tools/long-distance-fight-repair/", "/ko/tools/love-language-compatibility/", "/ko/tools/relationship-compatibility-test/", "/ko/tools/couples-communication-quiz/", "/ko/tools/relationship-repair-after-fight/", "/ko/tools/emotional-distance-relationship/", "/ko/tools/trust-issues-relationship/", "/ko/tools/insecure-in-relationship/", "/ko/tools/silent-treatment-relationship/", "/ko/tools/breakup-signs-relationship/", "/ko/tools/feeling-misunderstood-relationship/", "/ko/tools/partner-wont-communicate/", "/ko/tools/one-sided-relationship/"),
    "es": ("/es/tools/bazi-love-compatibility/", "/es/tools/2026-love-timing/", "/es/tools/long-distance-fight-repair/", "/es/tools/love-language-compatibility/", "/es/tools/relationship-compatibility-test/", "/es/tools/couples-communication-quiz/", "/es/tools/relationship-repair-after-fight/", "/es/tools/emotional-distance-relationship/", "/es/tools/trust-issues-relationship/", "/es/tools/insecure-in-relationship/", "/es/tools/silent-treatment-relationship/", "/es/tools/breakup-signs-relationship/", "/es/tools/feeling-misunderstood-relationship/", "/es/tools/partner-wont-communicate/", "/es/tools/one-sided-relationship/"),
}
INBOUND_PATHS = {
    "zh": ("/", "/compass/", "/garden-map/", "/resources/"),
    "en": ("/en/", "/en/compass/", "/en/garden-map/", "/en/resources/"),
    "ja": ("/ja/", "/ja/compass/", "/ja/garden-map/", "/ja/resources/"),
    "ko": ("/ko/", "/ko/compass/", "/ko/garden-map/", "/ko/resources/"),
    "es": ("/es/", "/es/compass/", "/es/garden-map/", "/es/resources/"),
}
REQUIRED_EVENTS = {
    "love_compatibility_compass_start",
    "love_compatibility_quiz",
    "love_compatibility_repair",
    "love_compatibility_section_compass",
    "love_compatibility_report_ladder",
    "love_compatibility_report_request",
    "love_compatibility_offer_compass",
    "love_compatibility_long_tail_entry",
}
LONG_TAIL_REQUIRED_EVENTS = {
    "love_compatibility_compass_start",
    "love_compatibility_hub",
    "love_compatibility_section_compass",
    "love_compatibility_report_ladder",
    "love_compatibility_report_request",
    "love_compatibility_repair",
}
HARD_VERDICT_PHRASES = (
    "一定會分手",
    "不能結婚",
    "命中注定不適合",
    "will definitely break up",
    "should not marry",
    "destined to fail",
)


class LoveCompatibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.events: set[str] = set()
        self.hrefs: set[str] = set()
        self.mailtos: list[str] = []
        self.faq_details = 0
        self.jsonld_blocks = 0
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "h1":
            self.h1 += 1
        event = attr.get("data-funnel-event", "")
        if event:
            self.events.add(event)
        href = attr.get("href", "")
        if href:
            self.hrefs.add(href)
        if href.startswith("mailto:"):
            self.mailtos.append(href)
        if tag.lower() == "details":
            self.faq_details += 1
        if tag.lower() == "script" and attr.get("type") == "application/ld+json":
            self.jsonld_blocks += 1

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text_parts.append(data.strip())


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_text(url: str, attempts: int = 3) -> tuple[int, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes love compatibility smoke/1.0"})
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
        "h1": 0,
        "events": 0,
        "mailto_links": 0,
        "faq_details": 0,
        "jsonld_blocks": 0,
        "boundary_phrases": 0,
    }
    issues: list[str] = []
    if status != 200:
        return [f"{path}: expected status 200, got {status}"], stats
    stats["pages"] = 1

    parser = LoveCompatibilityParser()
    parser.feed(text)
    full_text = "\n".join(parser.text_parts)
    stats["h1"] = parser.h1
    stats["events"] = len(parser.events)
    stats["mailto_links"] = len(parser.mailtos)
    stats["faq_details"] = parser.faq_details
    stats["jsonld_blocks"] = parser.jsonld_blocks
    stats["boundary_phrases"] = sum(
        1
        for phrase in ("不取代", "replace", "代替", "대신", "reemplaza")
        if phrase in full_text
    )
    if parser.h1 != 1:
        issues.append(f"{path}: expected one h1, got {parser.h1}")
    missing_events = sorted(REQUIRED_EVENTS.difference(parser.events))
    if missing_events:
        issues.append(f"{path}: missing funnel events {', '.join(missing_events)}")
    report_mailtos = [href for href in parser.mailtos if href.startswith("mailto:contact@lovetypes.tw?")]
    if len(report_mailtos) != 1:
        issues.append(f"{path}: expected one report mailto to contact@lovetypes.tw, got {len(report_mailtos)}")
    for href in report_mailtos:
        if "subject=" not in href or "body=" not in href:
            issues.append(f"{path}: report mailto missing subject/body")
    if parser.faq_details < 3:
        issues.append(f"{path}: expected at least 3 FAQ details, got {parser.faq_details}")
    if parser.jsonld_blocks < 4:
        issues.append(f"{path}: expected organization, breadcrumb, webpage, and FAQ JSON-LD")
    if stats["boundary_phrases"] < 1:
        issues.append(f"{path}: missing safety boundary wording")
    for phrase in HARD_VERDICT_PHRASES:
        if re.search(re.escape(phrase), full_text, re.I):
            issues.append(f"{path}: includes hard verdict phrase {phrase!r}")
    return issues, stats


def validate_long_tail_page(base_url: str, path: str) -> tuple[list[str], dict[str, int]]:
    issues, stats = validate_page(base_url, path)
    if issues and any("missing funnel events" in issue for issue in issues):
        issues = [issue for issue in issues if "missing funnel events" not in issue]
    status, text = request_text(urljoin(base_url + "/", path.lstrip("/")))
    if status != 200:
        return issues, stats
    parser = LoveCompatibilityParser()
    parser.feed(text)
    missing_events = sorted(LONG_TAIL_REQUIRED_EVENTS.difference(parser.events))
    if missing_events:
        issues.append(f"{path}: missing long-tail funnel events {', '.join(missing_events)}")
    if parser.jsonld_blocks < 4:
        issues.append(f"{path}: expected organization, breadcrumb, webpage, and FAQ JSON-LD")
    if parser.faq_details < 3:
        issues.append(f"{path}: expected at least 3 FAQ details, got {parser.faq_details}")
    return issues, stats


def validate_inbound_links(base_url: str) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "inbound_pages": 0,
        "inbound_links": 0,
        "inbound_events": 0,
        "compass_long_tail_links": 0,
        "home_long_tail_links": 0,
    }
    for lang, paths in INBOUND_PATHS.items():
        expected_href = LANG_PATHS[lang]
        for path in paths:
            status, text = request_text(urljoin(base_url + "/", path.lstrip("/")))
            if status != 200:
                issues.append(f"{path}: expected status 200, got {status}")
                continue
            stats["inbound_pages"] += 1
            parser = LoveCompatibilityParser()
            parser.feed(text)
            if expected_href not in parser.hrefs:
                issues.append(f"{path}: missing link to {expected_href}")
            else:
                stats["inbound_links"] += 1
            if path.endswith("/compass/"):
                if "compass_compatibility_entry" not in parser.events:
                    issues.append(f"{path}: missing compass_compatibility_entry event")
                else:
                    stats["inbound_events"] += 1
                if "compass_long_tail_entry" not in parser.events:
                    issues.append(f"{path}: missing compass_long_tail_entry event")
                else:
                    stats["inbound_events"] += 1
                for long_tail_path in LONG_TAIL_PATHS[lang]:
                    if long_tail_path not in parser.hrefs:
                        issues.append(f"{path}: missing compass long-tail link to {long_tail_path}")
                    else:
                        stats["compass_long_tail_links"] += 1
            if path in {"/", "/en/", "/ja/", "/ko/", "/es/"}:
                if "home_compass_bridge_entry" not in parser.events:
                    issues.append(f"{path}: missing home_compass_bridge_entry event")
                else:
                    stats["inbound_events"] += 1
                if "home_compass_bridge_long_tail" not in parser.events:
                    issues.append(f"{path}: missing home_compass_bridge_long_tail event")
                else:
                    stats["inbound_events"] += 1
                for long_tail_path in LONG_TAIL_PATHS[lang]:
                    if long_tail_path not in parser.hrefs:
                        issues.append(f"{path}: missing home long-tail link to {long_tail_path}")
                    else:
                        stats["home_long_tail_links"] += 1
    return issues, stats


def validate_hub_long_tail_links(base_url: str) -> tuple[list[str], int]:
    issues: list[str] = []
    links_checked = 0
    for lang, hub_path in LANG_PATHS.items():
        status, text = request_text(urljoin(base_url + "/", hub_path.lstrip("/")))
        if status != 200:
            issues.append(f"{hub_path}: expected status 200, got {status}")
            continue
        parser = LoveCompatibilityParser()
        parser.feed(text)
        for long_tail_path in LONG_TAIL_PATHS[lang]:
            if long_tail_path not in parser.hrefs:
                issues.append(f"{hub_path}: missing long-tail link to {long_tail_path}")
            else:
                links_checked += 1
    return issues, links_checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Check LoveTypes love compatibility SEO landing pages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    totals = {
        "pages": 0,
        "h1": 0,
        "events": 0,
        "mailto_links": 0,
        "faq_details": 0,
        "jsonld_blocks": 0,
        "boundary_phrases": 0,
        "inbound_pages": 0,
        "inbound_links": 0,
        "inbound_events": 0,
        "compass_long_tail_links": 0,
        "home_long_tail_links": 0,
        "hub_long_tail_links": 0,
    }
    issues: list[str] = []
    for path in LANG_PATHS.values():
        page_issues, stats = validate_page(base_url, path)
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value
    for paths in LONG_TAIL_PATHS.values():
        for path in paths:
            page_issues, stats = validate_long_tail_page(base_url, path)
            issues.extend(page_issues)
            for key, value in stats.items():
                totals[key] += value
    inbound_issues, inbound_stats = validate_inbound_links(base_url)
    issues.extend(inbound_issues)
    for key, value in inbound_stats.items():
        totals[key] += value
    hub_long_tail_issues, hub_long_tail_links = validate_hub_long_tail_links(base_url)
    issues.extend(hub_long_tail_issues)
    totals["hub_long_tail_links"] += hub_long_tail_links

    print(f"love_compatibility_pages_checked={totals['pages']}")
    print(f"love_compatibility_h1_checked={totals['h1']}")
    print(f"love_compatibility_events_checked={totals['events']}")
    print(f"love_compatibility_mailto_links_checked={totals['mailto_links']}")
    print(f"love_compatibility_faq_details_checked={totals['faq_details']}")
    print(f"love_compatibility_jsonld_blocks_checked={totals['jsonld_blocks']}")
    print(f"love_compatibility_boundary_phrases_checked={totals['boundary_phrases']}")
    print(f"love_compatibility_inbound_pages_checked={totals['inbound_pages']}")
    print(f"love_compatibility_inbound_links_checked={totals['inbound_links']}")
    print(f"love_compatibility_inbound_events_checked={totals['inbound_events']}")
    print(f"love_compatibility_compass_long_tail_links_checked={totals['compass_long_tail_links']}")
    print(f"love_compatibility_home_long_tail_links_checked={totals['home_long_tail_links']}")
    print(f"love_compatibility_hub_long_tail_links_checked={totals['hub_long_tail_links']}")
    print(f"love_compatibility_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
