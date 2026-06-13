#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
from pathlib import Path

import promotion_lead_writeback as lead_writeback
import promotion_post_text_import as post_text_import
import promotion_post_writeback as post_writeback
import promotion_profile_text_import as profile_text_import
import promotion_profile_writeback as profile_writeback


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_TRACKER = PROMOTION_DIR / "platform-profile-tracker.csv"
POSTING_QUEUE = PROMOTION_DIR / "posting-queue.csv"
PLATFORM_KPI_TRACKER = PROMOTION_DIR / "platform-kpi-tracker.csv"
SCRIPT_KPI_TRACKER = PROMOTION_DIR / "kpi-tracker.csv"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def parsed_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def future_profile_text(future: str) -> str:
    text = profile_text_import.SAMPLE_TEXT
    text = text.replace(profile_text_import.TODAY, future)
    return text


def future_post_text(future: str) -> str:
    text = post_text_import.SAMPLE_TEXT
    text = text.replace(post_text_import.TODAY, future)
    return text


def lead_future_rejected(future: str) -> bool:
    _, rows = read_csv(LEAD_TRACKER)
    args = argparse.Namespace(
        request_date=future,
        request_id="",
        guardian="iris",
        intake_type="owned_asset_request",
        proof_note="email thread Gmail request checked " + date.today().isoformat(),
        source="contact",
        consent_status="explicit_reply_ok",
        utm_content="iris_silence",
        requested_asset="PDF practice card",
    )
    try:
        lead_writeback.build_row(args, rows)
    except SystemExit:
        return True
    return False


def count_future_profile_rows(today: date) -> int:
    _, rows = read_csv(PROFILE_TRACKER)
    count = 0
    for row in rows:
        if row.get("status") not in profile_writeback.CONFIGURED_STATUSES:
            continue
        profile_date = parsed_date(row.get("profile_link_set_date", ""))
        if profile_date is None or profile_date > today:
            count += 1
    return count


def count_future_published_rows(today: date) -> int:
    count = 0
    for path in (POSTING_QUEUE, PLATFORM_KPI_TRACKER):
        _, rows = read_csv(path)
        for row in rows:
            if row.get("status") not in post_writeback.PUBLISH_STATUSES:
                continue
            published_date = parsed_date(row.get("published_date", ""))
            if published_date is None or published_date > today:
                count += 1
    _, rows = read_csv(SCRIPT_KPI_TRACKER)
    for row in rows:
        if not row.get("post_url"):
            continue
        script_date = parsed_date(row.get("date", ""))
        if script_date is None or script_date > today:
            count += 1
    return count


def count_future_real_leads(today: date) -> int:
    _, rows = read_csv(LEAD_TRACKER)
    count = 0
    for row in rows:
        if row.get("status") == "template":
            continue
        lead_date = parsed_date(row.get("date", ""))
        if lead_date is None or lead_date > today:
            count += 1
    return count


def main() -> int:
    today_value = date.today()
    future = (today_value + timedelta(days=1)).isoformat()
    profile_data, profile_issues = profile_text_import.parse_text(future_profile_text(future))
    post_data, post_issues = post_text_import.parse_text(future_post_text(future))
    metrics = {
        "promotion_temporal_future_profile_rejected": int(bool(profile_issues)),
        "promotion_temporal_future_post_rejected": int(bool(post_issues)),
        "promotion_temporal_future_lead_rejected": int(lead_future_rejected(future)),
        "promotion_temporal_profile_future_rows": count_future_profile_rows(today_value),
        "promotion_temporal_post_future_rows": count_future_published_rows(today_value),
        "promotion_temporal_lead_future_rows": count_future_real_leads(today_value),
        "promotion_temporal_profile_fields_parsed": len(profile_data),
        "promotion_temporal_post_fields_parsed": len(post_data),
    }
    issues: list[str] = []
    if metrics["promotion_temporal_future_profile_rejected"] != 1:
        issues.append("future profile set/live date should be rejected")
    if metrics["promotion_temporal_future_post_rejected"] != 1:
        issues.append("future published/posted/live date should be rejected")
    if metrics["promotion_temporal_future_lead_rejected"] != 1:
        issues.append("future real lead request date should be rejected")
    if metrics["promotion_temporal_profile_future_rows"] != 0:
        issues.append("current configured profile rows contain future/invalid dates")
    if metrics["promotion_temporal_post_future_rows"] != 0:
        issues.append("current published post rows contain future/invalid dates")
    if metrics["promotion_temporal_lead_future_rows"] != 0:
        issues.append("current real lead rows contain future/invalid dates")

    for key, value in metrics.items():
        print(f"{key}={value}")
    print(f"promotion_temporal_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
