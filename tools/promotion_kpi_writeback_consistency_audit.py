#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
POSTING_QUEUE = PROMOTION_DIR / "posting-queue.csv"
PLATFORM_KPI = PROMOTION_DIR / "platform-kpi-tracker.csv"
SCRIPT_KPI = PROMOTION_DIR / "kpi-tracker.csv"
WEEKLY_SUMMARY = PROMOTION_DIR / "weekly-summary.json"
ATTRIBUTION = PROMOTION_DIR / "attribution-reconciliation.json"
LAUNCH_READINESS = PROMOTION_DIR / "launch-readiness-gate.json"
PUBLISHING_STATUS = PROMOTION_DIR / "publishing-status.json"

PUBLISH_STATUSES = {"published", "live", "posted"}
METRIC_FIELDS = (
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
)
ATTRIBUTION_REQUIRED_FIELDS = (
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
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def row_key(row: dict[str, str]) -> tuple[str, str]:
    return ((row.get("platform") or "").strip(), (row.get("task_id") or "").strip())


def is_published(row: dict[str, str]) -> bool:
    return (row.get("status") or "").strip() in PUBLISH_STATUSES


def is_script_filled(row: dict[str, str]) -> bool:
    if any((row.get(field) or "").strip() for field in ("date", "platform", "post_url")):
        return True
    return any(parse_int(row.get(field)) > 0 for field in METRIC_FIELDS)


def is_attribution_filled(row: dict[str, str]) -> bool:
    return bool((row.get("post_url") or "").strip()) and any(parse_int(row.get(field)) for field in ATTRIBUTION_REQUIRED_FIELDS)


def sum_metrics(rows: list[dict[str, str]]) -> Counter:
    totals: Counter = Counter()
    for row in rows:
        for field in METRIC_FIELDS:
            totals[field] += parse_int(row.get(field))
    return totals


def published_script_rollups(platform_rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in platform_rows:
        if not is_published(row) or not (row.get("post_url") or "").strip():
            continue
        script_id = (row.get("script_id") or "").strip()
        if script_id:
            grouped.setdefault(script_id, []).append(row)
    rollups: dict[str, dict[str, object]] = {}
    for script_id, rows in grouped.items():
        rows.sort(key=lambda row: ((row.get("published_date") or "9999-99-99"), row.get("platform") or ""))
        rollups[script_id] = {
            "date": rows[0].get("published_date", ""),
            "platforms": sorted({row.get("platform", "") for row in rows if row.get("platform")}),
            "postUrl": rows[0].get("post_url", ""),
            "metrics": sum_metrics(rows),
        }
    return rollups


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    queue_fields, queue_rows = read_csv(POSTING_QUEUE)
    platform_fields, platform_rows = read_csv(PLATFORM_KPI)
    script_fields, script_rows = read_csv(SCRIPT_KPI)
    weekly_summary = read_json(WEEKLY_SUMMARY)
    attribution = read_json(ATTRIBUTION)
    launch_readiness = read_json(LAUNCH_READINESS)
    publishing_status = read_json(PUBLISHING_STATUS)

    for label, fields, required in (
        ("posting queue", queue_fields, {"platform", "task_id", "script_id", "status", "published_date", "post_url"}),
        ("platform KPI tracker", platform_fields, {"platform", "task_id", "script_id", "status", "published_date", "post_url", *METRIC_FIELDS}),
        ("script KPI tracker", script_fields, {"script_id", "date", "platform", "post_url", *METRIC_FIELDS}),
    ):
        missing = sorted(required - set(fields))
        if missing:
            issues.append(f"{label} missing fields: {', '.join(missing)}")

    platform_by_key = {row_key(row): row for row in platform_rows}
    queue_published = [row for row in queue_rows if is_published(row)]
    platform_published = [row for row in platform_rows if is_published(row)]
    script_filled = [row for row in script_rows if is_script_filled(row)]
    attribution_filled = [row for row in script_rows if is_attribution_filled(row)]

    for queue_row in queue_rows:
        key = row_key(queue_row)
        label = "/".join(key)
        platform_row = platform_by_key.get(key)
        if not platform_row:
            issues.append(f"{label}: missing platform KPI tracker row")
            continue
        for field in ("status", "published_date", "post_url"):
            if (platform_row.get(field) or "") != (queue_row.get(field) or ""):
                issues.append(f"{label}: platform KPI {field} should match posting queue")
        for field in METRIC_FIELDS:
            queue_value = (queue_row.get(field) or "").strip()
            platform_value = (platform_row.get(field) or "").strip()
            if queue_value and queue_value != platform_value:
                issues.append(f"{label}: platform KPI {field} should match posting queue when queue metric is present")

    rollups = published_script_rollups(platform_rows)
    script_by_id = {row.get("script_id", ""): row for row in script_rows if row.get("script_id")}
    for script_id, rollup in rollups.items():
        script_row = script_by_id.get(script_id)
        if not script_row:
            issues.append(f"{script_id}: missing script KPI row")
            continue
        if (script_row.get("date") or "") != rollup["date"]:
            issues.append(f"{script_id}: script KPI date should match earliest published platform date")
        if (script_row.get("post_url") or "") != rollup["postUrl"]:
            issues.append(f"{script_id}: script KPI post_url should match earliest published platform post_url")
        platforms = sorted(item for item in (script_row.get("platform") or "").split(",") if item)
        if platforms != rollup["platforms"]:
            issues.append(f"{script_id}: script KPI platform list should match published platform rollup")
        metrics: Counter = rollup["metrics"]  # type: ignore[assignment]
        for field in METRIC_FIELDS:
            expected = int(metrics[field])
            actual = parse_int(script_row.get(field))
            if expected != actual:
                issues.append(f"{script_id}: script KPI {field} should be {expected}, got {actual}")

    weekly_source = weekly_summary.get("sourceBreakdown", {}).get("videoTracker", {})
    if weekly_source.get("rows") != len(script_filled):
        issues.append("weekly summary videoTracker.rows should match filled script KPI rows")
    if weekly_summary.get("trackerRows") != len(script_filled):
        issues.append("weekly summary trackerRows should match filled script KPI rows")
    if attribution.get("filledKpiRows") != len(attribution_filled):
        issues.append("attribution filledKpiRows should match filled script KPI rows")
    readiness_metrics = launch_readiness.get("metrics", {})
    if readiness_metrics.get("publishedRows") != len(queue_published):
        issues.append("launch readiness publishedRows should match published posting queue rows")
    if readiness_metrics.get("filledKpiRows") != len(attribution_filled):
        issues.append("launch readiness filledKpiRows should match filled script KPI rows")
    if publishing_status.get("publishedScripts") != sorted(rollups):
        issues.append("publishing status publishedScripts should match published platform rollups")
    if publishing_status.get("platformTrackerMetricRows") != sum(1 for row in platform_rows if any(parse_int(row.get(field)) > 0 for field in METRIC_FIELDS)):
        issues.append("publishing status platformTrackerMetricRows should match platform KPI metric rows")

    return {
        "postingRows": len(queue_rows),
        "platformRows": len(platform_rows),
        "scriptRows": len(script_rows),
        "publishedRows": len(queue_published),
        "filledScriptRows": len(script_filled),
        "attributionFilledRows": len(attribution_filled),
        "rollupScripts": len(rollups),
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_kpi_writeback_posting_rows={metrics['postingRows']}")
    print(f"promotion_kpi_writeback_platform_rows={metrics['platformRows']}")
    print(f"promotion_kpi_writeback_script_rows={metrics['scriptRows']}")
    print(f"promotion_kpi_writeback_published_rows={metrics['publishedRows']}")
    print(f"promotion_kpi_writeback_filled_script_rows={metrics['filledScriptRows']}")
    print(f"promotion_kpi_writeback_attribution_filled_rows={metrics['attributionFilledRows']}")
    print(f"promotion_kpi_writeback_rollup_scripts={metrics['rollupScripts']}")
    print(f"promotion_kpi_writeback_consistency_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
