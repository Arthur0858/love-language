#!/usr/bin/env python3
"""Verify the production editorial trust surface used for AdSense review."""

from __future__ import annotations

import html
import json
import re
import sys
from urllib.parse import urlparse

from editorial_guides import GUIDE_EDITORIAL_CONTENT, GUIDE_UPDATED_BY_SLUG
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
        if len(urls) < 2:
            issues.append(f"{route}: expected at least two visible external sources")
        for url in urls:
            host = urlparse(html.unescape(url)).hostname or ""
            source_urls.add(html.unescape(url))
            source_hosts.add(host)
            if host not in ALLOWED_SOURCE_HOSTS:
                issues.append(f"{route}: unexpected source host {host}")
        if source_raw.count("<p>") < len(urls) + 1:
            issues.append(f"{route}: each source needs a visible explanation plus the authorship note")
        validate_article_schema(route, raw, updated, issues)

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
