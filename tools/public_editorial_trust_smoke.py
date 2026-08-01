#!/usr/bin/env python3
"""Verify the production editorial trust surface used for AdSense review."""

from __future__ import annotations

import html
import json
import re
import sys
from urllib.parse import urlparse

from editorial_guides import GUIDE_EDITORIAL_CONTENT, GUIDE_TRUST_SECTION_TITLES, GUIDE_UPDATED_BY_SLUG
from generate_multilingual_site import ZH_GUARDIAN_SECTION_TITLES
from lab_reports import LAB_REPORTS
from public_adsense_review_smoke import request, visible_text


GUIDE_MARKERS = (
    "data-guide-editorial-byline",
    "data-guide-example",
    "data-guide-workbook",
    "data-guide-applicability",
    "data-guide-revision",
    "data-guide-sources",
)
LAB_MARKERS = (
    "data-lab-editorial-byline",
    "data-lab-environment",
    "data-lab-fixture",
    "data-lab-steps",
    "data-lab-results",
    "data-lab-raw-results",
    "data-lab-failure",
    "data-lab-fix",
    "data-lab-limitations",
    "data-lab-method",
)
AUTHOR = "LoveTypes 內容編輯團隊"
GUARDIAN_UPDATED = "2026-08-01"
START_UPDATED = "2026-08-01"
REPAIR_PLAN_UPDATED = "2026-08-01"
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
METHOD_LINK = 'href="/about/#editorial-method"'
CORRECTION_LINK = 'href="/contact/#site-repair-report"'
ALLOWED_SOURCE_HOSTS = {
    "doi.org",
    "rainn.org",
    "www.cdc.gov",
    "www.cnvc.org",
    "www.who.int",
}


def main_html(raw: str) -> str:
    match = re.search(r"<main\b[^>]*>(.*?)</main>", raw, re.I | re.S)
    return match.group(1) if match else ""


def section(raw: str, marker: str) -> str:
    match = re.search(
        rf"<section\b[^>]*\b{re.escape(marker)}\b[^>]*>(.*?)</section>",
        raw,
        re.I | re.S,
    )
    return match.group(1) if match else ""


def schemas(raw: str) -> list[dict]:
    found: list[dict] = []
    for body in re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', raw, re.I | re.S):
        try:
            value = json.loads(html.unescape(body))
        except json.JSONDecodeError:
            continue
        values = value if isinstance(value, list) else [value]
        found.extend(item for item in values if isinstance(item, dict))
    return found


def article_schema(raw: str) -> dict | None:
    return next((item for item in schemas(raw) if item.get("@type") == "Article"), None)


def cjk_count(raw: str) -> int:
    return len(re.findall(r"[\u3400-\u9fff]", visible_text(main_html(raw))))


def cjk_shingles(raw: str, size: int = 6) -> frozenset[str]:
    characters = "".join(re.findall(r"[\u3400-\u9fff]", visible_text(main_html(raw))))
    return frozenset(characters[index : index + size] for index in range(max(0, len(characters) - size + 1)))


def validate_article_schema(route: str, raw: str, expected_modified: str, issues: list[str]) -> None:
    item = article_schema(raw)
    if item is None:
        issues.append(f"{route}: missing Article schema")
        return
    for field in ("author", "publisher"):
        value = item.get(field)
        if not isinstance(value, dict) or value.get("@type") != "Organization":
            issues.append(f"{route}: {field} must be an Organization")
    if item.get("dateModified") != expected_modified:
        issues.append(f"{route}: dateModified must be {expected_modified}")
    if item.get("mainEntityOfPage", {}).get("@id") != f"https://lovetypes.tw{route}":
        issues.append(f"{route}: mainEntityOfPage mismatch")


def main() -> int:
    issues: list[str] = []
    source_urls: set[str] = set()
    source_hosts: set[str] = set()
    revision_texts: set[str] = set()
    evidence_images: set[str] = set()
    guardian_shingle_sets: dict[str, frozenset[str]] = {}
    guide_h2_triplets: dict[tuple[str, str, str], str] = {}
    guardian_h2_owners: dict[str, str] = {}

    for slug in GUIDE_EDITORIAL_CONTENT:
        route = f"/guides/{slug}/"
        response = request(route)
        raw = response.text
        if response.status != 200:
            issues.append(f"{route}: expected 200, got {response.status}")
            continue
        count = cjk_count(raw)
        if not 2000 <= count <= 2800:
            issues.append(f"{route}: visible main CJK count outside 2000-2800: {count}")
        for marker in GUIDE_MARKERS:
            minimum = 2 if marker == "data-guide-example" else 1
            if raw.count(marker) < minimum:
                issues.append(f"{route}: expected at least {minimum} {marker} marker(s)")
        updated = GUIDE_UPDATED_BY_SLUG[slug]
        byline = re.search(r"<p\b[^>]*data-guide-editorial-byline[^>]*>(.*?)</p>", raw, re.I | re.S)
        byline_raw = byline.group(1) if byline else ""
        if AUTHOR not in visible_text(byline_raw):
            issues.append(f"{route}: missing real team byline")
        if f'<time datetime="{updated}">' not in byline_raw:
            issues.append(f"{route}: byline date must be {updated}")
        if METHOD_LINK not in byline_raw or CORRECTION_LINK not in byline_raw:
            issues.append(f"{route}: byline must link to method and correction routes")

        revision = visible_text(section(raw, "data-guide-revision"))
        if not revision or updated not in revision:
            issues.append(f"{route}: revision note must include the real update date")
        elif revision in revision_texts:
            issues.append(f"{route}: revision note duplicates another guide")
        revision_texts.add(revision)

        source_raw = section(raw, "data-guide-sources")
        urls = re.findall(r'<a\b[^>]*href="(https?://[^"]+)"[^>]*>', source_raw, re.I)
        if not 2 <= len(urls) <= 4:
            issues.append(f"{route}: expected two to four visible external sources")
        if len(set(urls)) != len(urls):
            issues.append(f"{route}: source URLs must be unique within the guide")
        source_items = re.findall(r"<li\b[^>]*>(.*?)</li>", source_raw, re.I | re.S)
        source_paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", source_raw, re.I | re.S)
        for url in urls:
            host = urlparse(html.unescape(url)).hostname or ""
            source_urls.add(html.unescape(url))
            source_hosts.add(host)
            if host not in ALLOWED_SOURCE_HOSTS:
                issues.append(f"{route}: unexpected source host {host}")
            item = next((value for value in source_items if f'href="{url}"' in value), "")
            explanation = re.search(r"<p\b[^>]*>(.*?)</p>", item, re.I | re.S)
            explanation_cjk = len(
                re.findall(r"[\u3400-\u9fff]", visible_text(explanation.group(1) if explanation else ""))
            )
            if explanation_cjk < 18:
                issues.append(f"{route}: source needs a specific visible explanation: {url}")
        source_anchors = re.findall(r"<a\b([^>]*)>", source_raw, re.I | re.S)
        if any('target="_blank"' not in attrs or 'rel="noopener noreferrer"' not in attrs for attrs in source_anchors):
            issues.append(f"{route}: external source links need safe new-tab attributes")
        if len(source_items) != len(urls) or len(source_paragraphs) < len(urls) + 1:
            issues.append(f"{route}: each source needs a visible explanation plus the authorship note")
        article_match = re.search(
            r'<article\b[^>]*class="[^"]*\barticle-body\b[^"]*"[^>]*>(.*?)</article>',
            raw,
            re.I | re.S,
        )
        article = article_match.group(1) if article_match and "data-guide-editorial-byline" in article_match.group(1) else ""
        if not article:
            issues.append(f"{route}: guide article body missing")
        headings = [visible_text(value) for value in re.findall(r"<h2\b[^>]*>(.*?)</h2>", article, re.I | re.S)]
        expected_trust_titles = set(GUIDE_TRUST_SECTION_TITLES[slug].values())
        missing_trust_titles = expected_trust_titles.difference(headings)
        if missing_trust_titles:
            issues.append(f"{route}: missing guide trust headings {sorted(missing_trust_titles)}")
        for position in range(max(0, len(headings) - 2)):
            triplet = tuple(headings[position : position + 3])
            previous = guide_h2_triplets.get(triplet)
            if previous:
                issues.append(f"{route}: repeats an H2 triplet from {previous}: {triplet}")
            guide_h2_triplets[triplet] = route
        validate_article_schema(route, raw, updated, issues)

    for slug in GUARDIAN_SLUGS:
        route = f"/characters/{slug}/"
        response = request(route)
        raw = response.text
        if response.status != 200:
            issues.append(f"{route}: expected 200, got {response.status}")
            continue
        count = cjk_count(raw)
        if not 2000 <= count <= 2600:
            issues.append(f"{route}: visible main CJK count outside 2000-2600: {count}")
        if raw.count("data-guardian-example") != 2:
            issues.append(f"{route}: expected exactly two labeled examples")
        for marker in (
            "data-guardian-editorial",
            "data-guardian-editorial-byline",
            "data-guardian-workbook",
            "適合使用",
            "不適用與限制",
            METHOD_LINK,
            CORRECTION_LINK,
        ):
            if marker not in raw:
                issues.append(f"{route}: missing guardian editorial marker {marker!r}")
        guardian_main = re.sub(
            r"<(script|style|template)\b[^>]*>.*?</\1>",
            " ",
            main_html(raw),
            flags=re.I | re.S,
        )
        headings = [visible_text(value) for value in re.findall(r"<h2\b[^>]*>(.*?)</h2>", guardian_main, re.I | re.S)]
        missing_titles = set(ZH_GUARDIAN_SECTION_TITLES[slug].values()).difference(headings)
        if missing_titles:
            issues.append(f"{route}: missing guardian topic headings {sorted(missing_titles)}")
        for heading in headings:
            previous = guardian_h2_owners.get(heading)
            if previous:
                issues.append(f"{route}: repeats visible guardian H2 from {previous}: {heading}")
            guardian_h2_owners[heading] = route
        web_page = next((item for item in schemas(raw) if item.get("@type") == "WebPage"), None)
        if web_page is None:
            issues.append(f"{route}: missing WebPage schema")
        else:
            if web_page.get("dateModified") != GUARDIAN_UPDATED:
                issues.append(f"{route}: dateModified must be {GUARDIAN_UPDATED}")
            for field in ("author", "publisher"):
                if web_page.get(field, {}).get("@type") != "Organization":
                    issues.append(f"{route}: {field} must be an Organization")
        guardian_shingle_sets[slug] = cjk_shingles(raw)

    max_guardian_jaccard = 0.0
    max_guardian_containment = 0.0
    guardian_items = list(guardian_shingle_sets.items())
    for index, (left_slug, left) in enumerate(guardian_items):
        for right_slug, right in guardian_items[index + 1 :]:
            overlap = len(left & right)
            union = len(left | right)
            smaller = min(len(left), len(right))
            jaccard = overlap / union if union else 0.0
            containment = overlap / smaller if smaller else 0.0
            max_guardian_jaccard = max(max_guardian_jaccard, jaccard)
            max_guardian_containment = max(max_guardian_containment, containment)
            if jaccard >= 0.30 or containment >= 0.45:
                issues.append(
                    f"guardian pages too similar: {left_slug}/{right_slug} "
                    f"jaccard={jaccard:.3f} containment={containment:.3f}"
                )

    start_response = request("/start/")
    start_raw = start_response.text
    if start_response.status != 200:
        issues.append(f"/start/: expected 200, got {start_response.status}")
    else:
        start_count = cjk_count(start_raw)
        if not 900 <= start_count <= 1300:
            issues.append(f"/start/: visible main CJK count outside 900-1300: {start_count}")
        for marker in ("data-start-method", "data-start-editorial-byline", METHOD_LINK, CORRECTION_LINK):
            if marker not in start_raw:
                issues.append(f"/start/: missing start trust marker {marker!r}")
        start_page = next((item for item in schemas(start_raw) if item.get("@type") == "WebPage"), None)
        if start_page is None or start_page.get("dateModified") != START_UPDATED:
            issues.append("/start/: missing WebPage schema or real update date")
        elif any(start_page.get(field, {}).get("@type") != "Organization" for field in ("author", "publisher")):
            issues.append("/start/: author and publisher must be Organization")

    repair_response = request("/repair-plan/")
    repair_raw = repair_response.text
    if repair_response.status != 200:
        issues.append(f"/repair-plan/: expected 200, got {repair_response.status}")
    else:
        repair_count = cjk_count(repair_raw)
        if not 2000 <= repair_count <= 2800:
            issues.append(f"/repair-plan/: visible main CJK count outside 2000-2800: {repair_count}")
        if repair_raw.count("data-repair-example") != 2:
            issues.append("/repair-plan/: expected exactly two labeled examples")
        for marker in (
            "data-repair-method",
            "data-repair-editorial-byline",
            "data-repair-decision",
            "data-repair-sources",
            METHOD_LINK,
            CORRECTION_LINK,
        ):
            if marker not in repair_raw:
                issues.append(f"/repair-plan/: missing repair trust marker {marker!r}")
        for url in (
            "https://www.cnvc.org/images/pdf/certification/EN-Certification%20Preparation%20Packet.pdf",
            "https://www.who.int/publications/i/item/WHO-RHR-14.26",
        ):
            if f'href="{url}"' not in repair_raw:
                issues.append(f"/repair-plan/: missing authoritative source {url}")
        howto = next((item for item in schemas(repair_raw) if item.get("@type") == "HowTo"), None)
        if howto is None or howto.get("dateModified") != REPAIR_PLAN_UPDATED:
            issues.append("/repair-plan/: missing HowTo schema or real update date")
        elif any(howto.get(field, {}).get("@type") != "Organization" for field in ("author", "publisher")):
            issues.append("/repair-plan/: author and publisher must be Organization")

    lab_heading_owner: dict[str, str] = {}
    lab_headings_checked = 0
    for report in LAB_REPORTS:
        slug = report["slug"]
        route = f"/lab/{slug}/"
        response = request(route)
        raw = response.text
        if response.status != 200:
            issues.append(f"{route}: expected 200, got {response.status}")
            continue
        count = cjk_count(raw)
        if not 1200 <= count <= 1800:
            issues.append(f"{route}: visible main CJK count outside 1200-1800: {count}")
        for marker in LAB_MARKERS:
            if marker not in raw:
                issues.append(f"{route}: missing {marker}")
        if report["test_id"] not in raw:
            issues.append(f"{route}: missing stable test ID")
        environment_count = len(re.findall(r"<li\b", section(raw, "data-lab-environment"), re.I))
        step_count = len(re.findall(r"<li\b", section(raw, "data-lab-steps"), re.I))
        result_body = re.search(r"<tbody\b[^>]*>(.*?)</tbody>", section(raw, "data-lab-results"), re.I | re.S)
        result_count = len(re.findall(r"<tr\b", result_body.group(1) if result_body else "", re.I))
        if environment_count != len(report["environment"]) or environment_count < 7:
            issues.append(f"{route}: environment details must include date, platform, browser and build")
        if step_count != len(report["steps"]) or step_count < 4:
            issues.append(f"{route}: reproducible steps are incomplete")
        if result_count != len(report["results"]) or result_count < 4:
            issues.append(f"{route}: raw result table is incomplete")
        for marker, minimum_cjk in (
            ("data-lab-fixture", 30),
            ("data-lab-raw-results", 150),
            ("data-lab-failure", 30),
            ("data-lab-fix", 35),
            ("data-lab-limitations", 40),
        ):
            marker_count = len(re.findall(r"[\u3400-\u9fff]", visible_text(section(raw, marker))))
            if marker_count < minimum_cjk:
                issues.append(f"{route}: {marker} evidence is too brief: {marker_count} CJK")
        report_article = re.search(r'<article\b[^>]*data-lab-report[^>]*>(.*?)</article>', raw, re.I | re.S)
        lab_headings = [
            visible_text(value)
            for value in re.findall(r"<h2\b[^>]*>(.*?)</h2>", report_article.group(1) if report_article else "", re.I | re.S)
        ]
        expected_headings = {
            title for key, title in report["section_titles"].items() if key != "next"
        }
        if len(lab_headings) != 12 or set(lab_headings) != expected_headings:
            issues.append(f"{route}: headings do not match the test-specific structure")
        if report["section_titles"]["next"] not in raw:
            issues.append(f"{route}: missing test-specific next-step heading")
        for heading in lab_headings:
            previous = lab_heading_owner.get(heading)
            if previous:
                issues.append(f"{route}: H2 {heading!r} is reused by {previous}")
            lab_heading_owner[heading] = route
            lab_headings_checked += 1
        updated = report["updated"]
        byline = re.search(r"<p\b[^>]*data-lab-editorial-byline[^>]*>(.*?)</p>", raw, re.I | re.S)
        byline_raw = byline.group(1) if byline else ""
        if AUTHOR not in visible_text(byline_raw) or f'<time datetime="{updated}">' not in byline_raw:
            issues.append(f"{route}: missing team byline or real test date")
        if METHOD_LINK not in byline_raw or CORRECTION_LINK not in byline_raw:
            issues.append(f"{route}: byline must link to method and correction routes")
        if "不是受試者研究、臨床驗證或關係成效證明" not in visible_text(main_html(raw)):
            issues.append(f"{route}: engineering evidence boundary is missing")
        images = re.findall(r'<img\b[^>]*src="(/assets/lovetypes/lab/[^"]+)"', main_html(raw), re.I)
        if len(set(images)) < 2:
            issues.append(f"{route}: expected two distinct evidence screenshots")
        for image in images:
            if image in evidence_images:
                issues.append(f"{route}: evidence screenshot reused by another report: {image}")
            evidence_images.add(image)
        validate_article_schema(route, raw, updated, issues)

    trust_expectations = {
        "/about/": (
            'id="editorial-method"',
            "團隊不具醫療、心理治療或法律專業資格",
            "問題定義、公開資料查核、工具實測、人工編輯、安全檢查與版本修訂",
            CORRECTION_LINK,
        ),
        "/theory/": (
            "不是人格診斷",
            "沒有單一「正確配對」",
            "https://doi.org/10.1177/09637214231217663",
            "https://rainn.org/articles/what-is-consent",
        ),
        "/privacy/": ("更新日期 2026-08-01", CORRECTION_LINK),
        "/contact/": ('id="site-repair-report"', "不要寄送測驗答案", "危急、暴力、跟蹤、強迫或自傷風險"),
    }
    for route, markers in trust_expectations.items():
        response = request(route)
        if response.status != 200:
            issues.append(f"{route}: expected 200, got {response.status}")
            continue
        for marker in markers:
            if marker not in response.text:
                issues.append(f"{route}: missing trust marker {marker!r}")

    print(f"public_editorial_trust_guides_checked={len(GUIDE_EDITORIAL_CONTENT)}")
    print(f"public_editorial_trust_labs_checked={len(LAB_REPORTS)}")
    print(f"public_editorial_trust_guardians_checked={len(guardian_shingle_sets)}")
    print(f"public_editorial_trust_guardian_max_jaccard={max_guardian_jaccard:.3f}")
    print(f"public_editorial_trust_guardian_max_containment={max_guardian_containment:.3f}")
    print("public_editorial_trust_start_pages_checked=1")
    print("public_editorial_trust_repair_plans_checked=1")
    print(f"public_editorial_trust_core_pages_checked={len(trust_expectations)}")
    print(f"public_editorial_trust_unique_sources={len(source_urls)}")
    print(f"public_editorial_trust_source_hosts={len(source_hosts)}")
    print(f"public_editorial_trust_evidence_images={len(evidence_images)}")
    print(f"public_editorial_trust_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
