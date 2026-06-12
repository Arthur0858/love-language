#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
EXPECTED_GUARDIANS = {"iris", "noah", "vivian", "claire", "dora"}
EXPECTED_CAMPAIGN = "first_round_quiz_completion"
EXPECTED_KPI_FIELDS = {
    "views",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "luna_clicks",
    "notes",
}


def request_json(base_url: str) -> tuple[dict, str]:
    url = urljoin(base_url.rstrip("/") + "/", "promotion-kit.json")
    request = Request(url, headers={"User-Agent": "LoveTypes promotion kit smoke/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=20) as response:
        text = response.read().decode("utf-8")
        return json.loads(text), response.headers.get("content-type", "")


def local_calendar_rows() -> list[dict[str, str]]:
    path = ROOT / "docs" / "promotion" / "first-round" / "publishing-calendar.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_tracked_url(source: str, value: str) -> list[str]:
    issues: list[str] = []
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
        issues.append(f"{source}: trackedUrl should point to https://lovetypes.tw/start/")
    expected = {
        "utm_source": "shorts",
        "utm_medium": "social",
        "utm_campaign": EXPECTED_CAMPAIGN,
    }
    for key, expected_value in expected.items():
        if query.get(key, [""])[0] != expected_value:
            issues.append(f"{source}: trackedUrl missing {key}={expected_value}")
    if not query.get("utm_content", [""])[0]:
        issues.append(f"{source}: trackedUrl missing utm_content")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes promotion kit metadata.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/") or DEFAULT_BASE_URL
    issues: list[str] = []
    kit, content_type = request_json(base_url)
    if "json" not in content_type:
        issues.append(f"/promotion-kit.json: expected JSON content type, got {content_type!r}")

    local_rows = local_calendar_rows()
    calendar = kit.get("publishingCalendar")
    if not isinstance(calendar, list) or len(calendar) != 15:
        issues.append(f"/promotion-kit.json: expected 15 publishingCalendar rows, got {len(calendar) if isinstance(calendar, list) else 'invalid'}")
        calendar = []
    if len(local_rows) != len(calendar):
        issues.append(f"/promotion-kit.json: local calendar has {len(local_rows)} rows, public kit has {len(calendar)}")

    if kit.get("campaignId") != "lovetypes-first-round-quiz-completion":
        issues.append("/promotion-kit.json: campaignId should match the scripts library campaign id")
    if kit.get("utmCampaign") != EXPECTED_CAMPAIGN:
        issues.append(f"/promotion-kit.json: utmCampaign should be {EXPECTED_CAMPAIGN}")
    if kit.get("primaryUrl") != "https://lovetypes.tw/start/":
        issues.append("/promotion-kit.json: primaryUrl should be the dedicated quiz start URL")
    if kit.get("scriptCount") != 15 or kit.get("campaignCount") != 15:
        issues.append("/promotion-kit.json: scriptCount and campaignCount should both be 15")
    if kit.get("guardianCount") != 5:
        issues.append("/promotion-kit.json: guardianCount should be 5")
    kpi_fields = kit.get("kpiFields")
    if not isinstance(kpi_fields, list) or not EXPECTED_KPI_FIELDS.issubset(kpi_fields):
        issues.append("/promotion-kit.json: missing expected KPI fields")

    seen_scripts: set[str] = set()
    seen_guardians: set[str] = set()
    seen_contents: set[str] = set()
    for index, row in enumerate(calendar, start=1):
        source = f"/promotion-kit.json:publishingCalendar[{index}]"
        guardian = row.get("guardianId")
        script_id = row.get("scriptId")
        utm_content = row.get("utmContent")
        if guardian not in EXPECTED_GUARDIANS:
            issues.append(f"{source}: unexpected guardianId {guardian!r}")
        else:
            seen_guardians.add(guardian)
        if not isinstance(script_id, str) or not script_id.startswith("lt-s"):
            issues.append(f"{source}: invalid scriptId {script_id!r}")
        elif script_id in seen_scripts:
            issues.append(f"{source}: duplicate scriptId {script_id}")
        else:
            seen_scripts.add(script_id)
        if not utm_content:
            issues.append(f"{source}: missing utmContent")
        elif utm_content in seen_contents:
            issues.append(f"{source}: duplicate utmContent {utm_content}")
        else:
            seen_contents.add(utm_content)
        if row.get("utmCampaign") != EXPECTED_CAMPAIGN:
            issues.append(f"{source}: unexpected utmCampaign {row.get('utmCampaign')!r}")
        tracked = row.get("trackedUrl", "")
        issues.extend(validate_tracked_url(source, tracked))
        if utm_content and parse_qs(urlparse(tracked).query).get("utm_content", [""])[0] != utm_content:
            issues.append(f"{source}: trackedUrl utm_content should match utmContent")

    if seen_guardians != EXPECTED_GUARDIANS:
        issues.append(f"/promotion-kit.json: missing guardians {sorted(EXPECTED_GUARDIANS - seen_guardians)}")

    print(f"public_promotion_kit_campaigns_checked={len(calendar)}")
    print(f"public_promotion_kit_guardians_checked={len(seen_guardians)}")
    print(f"public_promotion_kit_scripts_checked={len(seen_scripts)}")
    print(f"public_promotion_kit_utm_contents_checked={len(seen_contents)}")
    print(f"public_promotion_kit_kpi_fields_checked={len(kpi_fields) if isinstance(kpi_fields, list) else 0}")
    print(f"public_promotion_kit_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
