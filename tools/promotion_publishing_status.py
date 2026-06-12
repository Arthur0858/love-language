#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "publishing-status.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "publishing-status.json"
PLATFORMS = {"youtube_shorts", "tiktok", "instagram_reels"}
PUBLISHED_STATUSES = {"published", "live", "posted"}
ACTIVE_STATUSES = {"planned", "scheduled", *PUBLISHED_STATUSES}
REVENUE_FIELDS = [
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def normal_status(value: str | None) -> str:
    return (value or "planned").strip().lower() or "planned"


def tracked_url_platform(value: str) -> str:
    query = parse_qs(urlparse(value).query)
    return query.get("utm_source", [""])[0]


def tracker_by_script(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("script_id", ""): row for row in rows if row.get("script_id")}


def build_report(
    queue_fields: list[str],
    queue_rows: list[dict[str, str]],
    tracker_fields: list[str],
    tracker_rows: list[dict[str, str]],
) -> dict:
    issues: list[str] = []
    warnings: list[str] = []
    queue_by_platform = Counter()
    queue_by_status = Counter()
    queue_by_guardian = Counter()
    published_by_platform = Counter()
    missing_post_url: list[str] = []
    missing_published_date: list[str] = []
    invalid_statuses: list[str] = []
    invalid_platforms: list[str] = []
    invalid_tracking_sources: list[str] = []
    duplicate_keys: list[str] = []
    seen_keys: set[tuple[str, str]] = set()

    expected_queue_fields = {
        "platform",
        "status",
        "published_date",
        "post_url",
        "task_id",
        "script_id",
        "guardian_id",
        "tracked_url",
        "utm_content",
    }
    missing_queue_fields = sorted(expected_queue_fields - set(queue_fields))
    if missing_queue_fields:
        issues.append("posting queue missing fields: " + ", ".join(missing_queue_fields))

    expected_tracker_fields = {"script_id", "platform", "post_url", "date", *REVENUE_FIELDS}
    missing_tracker_fields = sorted(expected_tracker_fields - set(tracker_fields))
    if missing_tracker_fields:
        issues.append("KPI tracker missing fields: " + ", ".join(missing_tracker_fields))

    tracker_lookup = tracker_by_script(tracker_rows)
    published_scripts: set[str] = set()
    published_queue_rows: list[dict[str, str]] = []

    for row in queue_rows:
        platform = (row.get("platform") or "").strip()
        task_id = (row.get("task_id") or "").strip()
        script_id = (row.get("script_id") or "").strip()
        status = normal_status(row.get("status"))
        guardian = (row.get("guardian_id") or "unknown").strip() or "unknown"
        key = (platform, task_id)
        key_label = f"{platform or '<missing-platform>'}/{task_id or '<missing-task>'}"

        if key in seen_keys:
            duplicate_keys.append(key_label)
        seen_keys.add(key)
        queue_by_platform[platform] += 1
        queue_by_status[status] += 1
        queue_by_guardian[guardian] += 1

        if platform not in PLATFORMS:
            invalid_platforms.append(key_label)
        if status not in ACTIVE_STATUSES:
            invalid_statuses.append(f"{key_label}={status}")
        source = tracked_url_platform(row.get("tracked_url", ""))
        if source and source != "shorts":
            invalid_tracking_sources.append(f"{key_label}: utm_source={source}")

        if status in PUBLISHED_STATUSES:
            published_by_platform[platform] += 1
            published_scripts.add(script_id)
            published_queue_rows.append(row)
            if not (row.get("post_url") or "").strip():
                missing_post_url.append(key_label)
            if not (row.get("published_date") or "").strip():
                missing_published_date.append(key_label)

    if len(queue_rows) != 45:
        issues.append(f"posting queue should have 45 rows, got {len(queue_rows)}")
    if set(queue_by_platform) != PLATFORMS:
        issues.append("posting queue platforms should be exactly " + ", ".join(sorted(PLATFORMS)))
    for platform in sorted(PLATFORMS):
        if queue_by_platform[platform] != 15:
            issues.append(f"{platform} should have 15 queue rows, got {queue_by_platform[platform]}")
    if len(tracker_rows) != 15:
        issues.append(f"KPI tracker should have 15 rows, got {len(tracker_rows)}")
    for label, values in (
        ("duplicate posting queue rows", duplicate_keys),
        ("invalid posting queue platforms", invalid_platforms),
        ("invalid posting queue statuses", invalid_statuses),
        ("invalid tracking sources", invalid_tracking_sources),
        ("published queue rows missing post_url", missing_post_url),
        ("published queue rows missing published_date", missing_published_date),
    ):
        if values:
            issues.append(label + ": " + "; ".join(values[:10]))

    tracker_ready_scripts: list[str] = []
    tracker_missing_scripts: list[str] = []
    tracker_partial_scripts: list[str] = []
    revenue_intent = Counter()
    for script_id in sorted(published_scripts):
        tracker = tracker_lookup.get(script_id, {})
        filled = [field for field in ("date", "platform", "post_url") if (tracker.get(field) or "").strip()]
        if len(filled) == 3:
            tracker_ready_scripts.append(script_id)
        elif filled:
            tracker_partial_scripts.append(script_id)
        else:
            tracker_missing_scripts.append(script_id)
    for row in tracker_rows:
        for field in REVENUE_FIELDS:
            revenue_intent[field] += parse_int(row.get(field))

    if published_queue_rows and tracker_missing_scripts:
        warnings.append(
            "published posts exist but KPI tracker has no matching date/platform/post_url for: "
            + ", ".join(tracker_missing_scripts[:10])
        )
    if tracker_partial_scripts:
        warnings.append("KPI tracker has partial publish metadata for: " + ", ".join(tracker_partial_scripts[:10]))
    if not published_queue_rows:
        warnings.append("empty publish mode: no queue rows are marked published/live/posted yet")

    platform_status = defaultdict(Counter)
    guardian_status = defaultdict(Counter)
    for row in queue_rows:
        status = normal_status(row.get("status"))
        platform_status[row.get("platform", "")][status] += 1
        guardian_status[row.get("guardian_id", "unknown")][status] += 1

    return {
        "generatedAt": date.today().isoformat(),
        "queueRows": len(queue_rows),
        "trackerRows": len(tracker_rows),
        "platforms": sorted(queue_by_platform),
        "queueByPlatform": dict(sorted(queue_by_platform.items())),
        "queueByStatus": dict(sorted(queue_by_status.items())),
        "queueByGuardian": dict(sorted(queue_by_guardian.items())),
        "publishedByPlatform": dict(sorted(published_by_platform.items())),
        "platformStatus": {key: dict(sorted(value.items())) for key, value in sorted(platform_status.items())},
        "guardianStatus": {key: dict(sorted(value.items())) for key, value in sorted(guardian_status.items())},
        "publishedScripts": sorted(published_scripts),
        "trackerReadyPublishedScripts": tracker_ready_scripts,
        "trackerMissingPublishedScripts": tracker_missing_scripts,
        "trackerPartialPublishedScripts": tracker_partial_scripts,
        "revenueIntentTotals": {field: int(revenue_intent[field]) for field in REVENUE_FIELDS},
        "warnings": warnings,
        "issues": issues,
        "readyForWeeklyDecision": bool(published_queue_rows) and not tracker_missing_scripts and not tracker_partial_scripts,
        "safety": {
            "emptyPublishMode": not published_queue_rows,
            "note": "Do not pick winning guardians or monetization routes before published posts and KPI rows are backfilled."
            if not published_queue_rows
            else "",
        },
    }


def render_summary(report: dict) -> str:
    lines = [
        "# LoveTypes 第一輪發布狀態對帳",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- 發文佇列列數：{report['queueRows']}",
        f"- KPI 追蹤列數：{report['trackerRows']}",
        f"- 是否可做週決策：{'可以' if report['readyForWeeklyDecision'] else '尚不可'}",
        "",
        "## 平台進度",
        "",
    ]
    for platform, statuses in report["platformStatus"].items():
        status_text = ", ".join(f"{status}: {count}" for status, count in statuses.items())
        lines.append(f"- {platform}: {status_text}")
    lines.extend(["", "## 守護者進度", ""])
    for guardian, statuses in report["guardianStatus"].items():
        status_text = ", ".join(f"{status}: {count}" for status, count in statuses.items())
        lines.append(f"- {guardian}: {status_text}")
    lines.extend(["", "## KPI 對帳", ""])
    lines.append(f"- 已發布腳本：{len(report['publishedScripts'])}")
    lines.append(f"- KPI 已完整回填的已發布腳本：{len(report['trackerReadyPublishedScripts'])}")
    lines.append(f"- KPI 缺回填的已發布腳本：{len(report['trackerMissingPublishedScripts'])}")
    lines.append(f"- KPI 部分回填的已發布腳本：{len(report['trackerPartialPublishedScripts'])}")
    lines.extend(["", "## 獲利意圖欄位總計", ""])
    for field, value in report["revenueIntentTotals"].items():
        lines.append(f"- {field}: {value}")
    if report["warnings"]:
        lines.extend(["", "## 注意事項", ""])
        lines.extend(f"- {item}" for item in report["warnings"])
    if report["issues"]:
        lines.extend(["", "## 問題", ""])
        lines.extend(f"- {item}" for item in report["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict, output_path: Path, json_path: Path) -> None:
    output_path.write_text(render_summary(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile LoveTypes posting queue and KPI tracker publish status.")
    parser.add_argument("--queue", default=str(QUEUE_PATH))
    parser.add_argument("--tracker", default=str(TRACKER_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true", help="Validate without writing status files.")
    args = parser.parse_args()

    queue_fields, queue_rows = read_csv(Path(args.queue))
    tracker_fields, tracker_rows = read_csv(Path(args.tracker))
    report = build_report(queue_fields, queue_rows, tracker_fields, tracker_rows)
    if not args.check:
        write_outputs(report, Path(args.output), Path(args.json_output))
        print(f"promotion_publishing_status={args.output}")
        print(f"promotion_publishing_status_json={args.json_output}")
    print(f"promotion_publishing_status_queue_rows={report['queueRows']}")
    print(f"promotion_publishing_status_tracker_rows={report['trackerRows']}")
    print(f"promotion_publishing_status_platforms={len(report['platforms'])}")
    print(f"promotion_publishing_status_published_scripts={len(report['publishedScripts'])}")
    print(f"promotion_publishing_status_ready={1 if report['readyForWeeklyDecision'] else 0}")
    print(f"promotion_publishing_status_warnings={len(report['warnings'])}")
    print(f"promotion_publishing_status_issues={len(report['issues'])}")
    for issue in report["issues"]:
        print(issue)
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
