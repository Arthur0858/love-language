#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
TRACKER_PATH = PROMOTION_DIR / "platform-kpi-tracker.csv"
TRACKER_JSON_PATH = PROMOTION_DIR / "platform-kpi-tracker.json"
PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
METRIC_FIELDS = [
    "views",
    "likes",
    "comments",
    "shares",
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]
FIELDNAMES = [
    "week",
    "slot",
    "platform",
    "status",
    "scheduled_date",
    "scheduled_time",
    "timezone",
    "published_date",
    "post_url",
    "task_id",
    "script_id",
    "guardian_id",
    "guardian_name",
    "content_angle",
    "title",
    "utm_content",
    "tracked_url",
    *METRIC_FIELDS,
    "notes",
]
PRESERVE_FIELDS = {"published_date", "post_url", *METRIC_FIELDS, "notes"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def existing_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {
        ((row.get("platform") or "").strip(), (row.get("task_id") or "").strip()): row
        for row in rows
        if row.get("platform") and row.get("task_id")
    }


def tracker_row(queue_row: dict[str, str], existing: dict[str, str] | None = None) -> dict[str, str]:
    existing = existing or {}
    row = {field: "" for field in FIELDNAMES}
    for field in (
        "week",
        "slot",
        "platform",
        "status",
        "scheduled_date",
        "scheduled_time",
        "timezone",
        "published_date",
        "post_url",
        "task_id",
        "script_id",
        "guardian_id",
        "guardian_name",
        "content_angle",
        "title",
        "utm_content",
        "tracked_url",
        "notes",
    ):
        row[field] = queue_row.get(field, "")
    for field in PRESERVE_FIELDS:
        if existing.get(field):
            row[field] = existing[field]
    return row


def build_rows(queue_rows: list[dict[str, str]], existing_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    existing = existing_lookup(existing_rows)
    rows = []
    for queue_row in queue_rows:
        key = ((queue_row.get("platform") or "").strip(), (queue_row.get("task_id") or "").strip())
        rows.append(tracker_row(queue_row, existing.get(key)))
    return rows


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    if len(rows) != 45:
        issues.append(f"expected 45 platform KPI rows, got {len(rows)}")
    seen: set[tuple[str, str]] = set()
    platform_counts = {platform: 0 for platform in PLATFORMS}
    for row in rows:
        platform = (row.get("platform") or "").strip()
        task_id = (row.get("task_id") or "").strip()
        key = (platform, task_id)
        label = f"{platform or '<missing-platform>'}/{task_id or '<missing-task>'}"
        if key in seen:
            issues.append(f"duplicate platform KPI row {label}")
        seen.add(key)
        if platform not in PLATFORMS:
            issues.append(f"{label}: invalid platform")
        else:
            platform_counts[platform] += 1
        for field in ("week", "slot", "status", "scheduled_date", "scheduled_time", "timezone", "task_id", "script_id", "guardian_id", "title", "utm_content", "tracked_url"):
            if not row.get(field):
                issues.append(f"{label}: missing {field}")
        if row.get("tracked_url") and f"utm_content={row.get('utm_content')}" not in row["tracked_url"]:
            issues.append(f"{label}: tracked_url should contain matching utm_content")
        if row.get("status") in {"published", "live", "posted"}:
            for field in ("published_date", "post_url"):
                if not row.get(field):
                    issues.append(f"{label}: published row missing {field}")
    for platform, count in platform_counts.items():
        if count != 15:
            issues.append(f"{platform} should have 15 platform KPI rows, got {count}")
    return issues


def write_outputs(rows: list[dict[str, str]], csv_path: Path, json_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "rowCount": len(rows),
        "platforms": list(PLATFORMS),
        "metricFields": METRIC_FIELDS,
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync LoveTypes platform-level KPI tracker from posting queue.")
    parser.add_argument("--queue", default=str(QUEUE_PATH))
    parser.add_argument("--output", default=str(TRACKER_PATH))
    parser.add_argument("--json-output", default=str(TRACKER_JSON_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows = build_rows(read_csv(Path(args.queue)), read_csv(Path(args.output)))
    issues = validate_rows(rows)
    if not args.check:
        if issues:
            for issue in issues:
                print(issue)
            return 1
        write_outputs(rows, Path(args.output), Path(args.json_output))
        print(f"promotion_platform_kpi_tracker={args.output}")
        print(f"promotion_platform_kpi_tracker_json={args.json_output}")
    filled_metric_rows = sum(1 for row in rows if any(parse_int(row.get(field)) > 0 for field in METRIC_FIELDS))
    published_rows = sum(1 for row in rows if row.get("status") in {"published", "live", "posted"})
    print(f"promotion_platform_kpi_tracker_rows={len(rows)}")
    print(f"promotion_platform_kpi_tracker_platforms={len(PLATFORMS)}")
    print(f"promotion_platform_kpi_tracker_metric_fields={len(METRIC_FIELDS)}")
    print(f"promotion_platform_kpi_tracker_published_rows={published_rows}")
    print(f"promotion_platform_kpi_tracker_filled_metric_rows={filled_metric_rows}")
    print(f"promotion_platform_kpi_tracker_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
