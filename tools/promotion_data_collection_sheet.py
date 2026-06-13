#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
ATTRIBUTION_PATH = PROMOTION_DIR / "attribution-reconciliation.csv"
METRIC_SOURCE_PATH = PROMOTION_DIR / "metric-source-matrix.json"
PLATFORM_PROFILE_TRACKER = PROMOTION_DIR / "platform-profile-tracker.csv"
PLATFORM_KPI_TRACKER = PROMOTION_DIR / "platform-kpi-tracker.csv"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "data-collection-sheet.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "data-collection-sheet.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "data-collection-sheet.csv"

POST_METRIC_FIELDS = [
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
PROFILE_METRIC_FIELDS = [
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
MINIMUM_DECISION_FIELDS = {"site_clicks", "quiz_starts", "quiz_completions"}
LEAD_INTENT_FIELDS = {"supply_lead_requests", "luna_pack_clicks", "contact_requests"}
CSV_FIELDS = [
    "source_type",
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "utm_content",
    "metric",
    "category",
    "collection_status",
    "source_url",
    "primary_source",
    "required_proof",
    "zero_allowed",
    "decision_gate",
    "writeback_target",
    "blocked_by",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_lookup() -> dict[str, dict]:
    matrix = load_json(METRIC_SOURCE_PATH)
    return {str(row.get("metric", "")): row for row in matrix.get("rows", [])}


def tracker_rows_by_key(path: Path, key_field: str) -> dict[str, dict[str, str]]:
    return {
        str(row.get(key_field, "")): row
        for row in read_csv(path)
        if row.get(key_field)
    }


def has_value(row: dict[str, str], metric: str) -> bool:
    return bool((row.get(metric) or "").strip())


def source_metrics(source_type: str) -> list[str]:
    if source_type == "profile":
        return PROFILE_METRIC_FIELDS
    return POST_METRIC_FIELDS


def collection_status(source: dict[str, str], tracker: dict[str, str], metric: str) -> tuple[str, str]:
    if source.get("source_type") == "profile":
        if not tracker or (tracker.get("status") or "").strip() not in {"set", "live"}:
            return "blocked_until_profile_set", "profile link is not confirmed set/live"
    else:
        if not tracker or not (tracker.get("post_url") or "").strip():
            return "blocked_until_public_post_url", "post URL is not written back"
    if has_value(tracker, metric):
        return "filled", ""
    if metric in MINIMUM_DECISION_FIELDS:
        return "ready_for_source_check", ""
    if metric in LEAD_INTENT_FIELDS:
        return "waiting_for_real_lead_or_review", ""
    return "optional_after_minimum_kpi", ""


def writeback_target(source: dict[str, str]) -> str:
    if source.get("source_type") == "profile":
        return "platform-profile-tracker.csv"
    return "platform-kpi-tracker.csv first; kpi-tracker.csv weekly rollup"


def build_sheet() -> dict:
    attribution_rows = read_csv(ATTRIBUTION_PATH)
    metrics = metric_lookup()
    profile_tracker = tracker_rows_by_key(PLATFORM_PROFILE_TRACKER, "platform")
    platform_tracker = tracker_rows_by_key(PLATFORM_KPI_TRACKER, "task_id")
    rows = []
    summary_rows = []
    for source in attribution_rows:
        source_type = source.get("source_type", "")
        metric_fields = source_metrics(source_type)
        if source_type == "profile":
            tracker = profile_tracker.get(source.get("platform", ""), {})
        else:
            tracker = platform_tracker.get(source.get("task_id", ""), {})
        source_detail_rows = []
        for metric in metric_fields:
            policy = metrics.get(metric, {})
            status, blocked_by = collection_status(source, tracker, metric)
            row = {
                "sourceType": source_type,
                "platform": source.get("platform", ""),
                "taskId": source.get("task_id", ""),
                "scriptId": source.get("script_id", ""),
                "guardianId": source.get("guardian_id", ""),
                "guardianName": source.get("guardian_name", ""),
                "utmContent": source.get("utm_content", ""),
                "trackedUrl": source.get("tracked_url", ""),
                "metric": metric,
                "category": policy.get("category", ""),
                "collectionStatus": status,
                "primarySource": policy.get("primarySource", ""),
                "requiredProof": policy.get("requiredProof", ""),
                "zeroAllowed": policy.get("zeroAllowed", ""),
                "decisionGate": (
                    "weekly_review_minimum_kpi"
                    if metric in MINIMUM_DECISION_FIELDS
                    else "lead_demand_or_offer_gate"
                    if metric in LEAD_INTENT_FIELDS
                    else "route_learning"
                ),
                "writebackTarget": writeback_target(source),
                "blockedBy": blocked_by,
                "safetyBoundary": policy.get("safetyBoundary", ""),
            }
            rows.append(row)
            source_detail_rows.append(row)
        summary_rows.append({
            "sourceType": source_type,
            "platform": source.get("platform", ""),
            "taskId": source.get("task_id", ""),
            "scriptId": source.get("script_id", ""),
            "guardianId": source.get("guardian_id", ""),
            "utmContent": source.get("utm_content", ""),
            "trackedUrl": source.get("tracked_url", ""),
            "metricRows": len(source_detail_rows),
            "blockedRows": sum(1 for row in source_detail_rows if row["collectionStatus"].startswith("blocked")),
            "minimumKpiRows": sum(1 for row in source_detail_rows if row["metric"] in MINIMUM_DECISION_FIELDS),
            "leadIntentRows": sum(1 for row in source_detail_rows if row["metric"] in LEAD_INTENT_FIELDS),
        })
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "attribution": str(ATTRIBUTION_PATH.relative_to(ROOT)),
            "metricSourceMatrix": str(METRIC_SOURCE_PATH.relative_to(ROOT)),
            "platformProfileTracker": str(PLATFORM_PROFILE_TRACKER.relative_to(ROOT)),
            "platformKpiTracker": str(PLATFORM_KPI_TRACKER.relative_to(ROOT)),
        },
        "metrics": {
            "sourceRows": len(attribution_rows),
            "collectionRows": len(rows),
            "profileCollectionRows": sum(1 for row in rows if row["sourceType"] == "profile"),
            "shortsCollectionRows": sum(1 for row in rows if row["sourceType"] == "shorts"),
            "minimumKpiRows": sum(1 for row in rows if row["metric"] in MINIMUM_DECISION_FIELDS),
            "leadIntentRows": sum(1 for row in rows if row["metric"] in LEAD_INTENT_FIELDS),
            "blockedRows": sum(1 for row in rows if row["collectionStatus"].startswith("blocked")),
            "readyRows": sum(1 for row in rows if row["collectionStatus"] == "ready_for_source_check"),
            "filledRows": sum(1 for row in rows if row["collectionStatus"] == "filled"),
        },
        "summaryRows": summary_rows,
        "rows": rows,
    }


def validate_sheet(sheet: dict) -> list[str]:
    issues: list[str] = []
    metric_names = set(metric_lookup())
    rows = sheet.get("rows", [])
    summary_rows = sheet.get("summaryRows", [])
    if sheet["metrics"]["sourceRows"] != len(summary_rows):
        issues.append("summary rows must match attribution source rows")
    expected_rows = sum(14 if row.get("sourceType") == "profile" else 18 for row in summary_rows)
    if len(rows) != expected_rows:
        issues.append(f"expected {expected_rows} collection rows, got {len(rows)}")
    if any(row.get("metric") not in metric_names for row in rows):
        issues.append("collection row references unknown metric")
    for row in rows:
        label = f"{row.get('sourceType')}/{row.get('taskId') or row.get('platform')}/{row.get('metric')}"
        if not row.get("trackedUrl", "").startswith("https://lovetypes.tw/start/"):
            issues.append(f"{label}: trackedUrl should point to /start/")
        if not row.get("requiredProof"):
            issues.append(f"{label}: missing required proof")
        if not row.get("writebackTarget"):
            issues.append(f"{label}: missing writeback target")
        if row.get("collectionStatus") not in {
            "blocked_until_profile_set",
            "blocked_until_public_post_url",
            "filled",
            "ready_for_source_check",
            "waiting_for_real_lead_or_review",
            "optional_after_minimum_kpi",
        }:
            issues.append(f"{label}: unknown collection status")
        if row.get("collectionStatus", "").startswith("blocked") and not row.get("blockedBy"):
            issues.append(f"{label}: blocked row needs blockedBy")
    if sheet["metrics"]["minimumKpiRows"] == 0:
        issues.append("minimum KPI collection rows are required")
    if sheet["metrics"]["leadIntentRows"] == 0:
        issues.append("lead intent collection rows are required")
    return issues


def render_markdown(sheet: dict, issues: list[str]) -> str:
    metrics = sheet["metrics"]
    lines = [
        "# LoveTypes Data Collection Sheet",
        "",
        f"- 產生日期：{sheet['generatedAt']}",
        f"- source rows：{metrics['sourceRows']}",
        f"- collection rows：{metrics['collectionRows']}",
        f"- profile collection rows：{metrics['profileCollectionRows']}",
        f"- Shorts collection rows：{metrics['shortsCollectionRows']}",
        f"- minimum KPI rows：{metrics['minimumKpiRows']}",
        f"- lead-intent rows：{metrics['leadIntentRows']}",
        f"- blocked rows：{metrics['blockedRows']}",
        f"- ready rows：{metrics['readyRows']}",
        f"- filled rows：{metrics['filledRows']}",
        f"- issues：{len(issues)}",
        "",
        "## Rules",
        "",
        "- Profile rows stay blocked until the profile link is confirmed set/live.",
        "- Shorts rows stay blocked until a real public post URL is written back.",
        "- Minimum KPI rows are `site_clicks`, `quiz_starts`, and `quiz_completions`.",
        "- Lead-intent rows require real user request, explicit consent, and traceable evidence.",
        "- Do not change product order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian from blank data.",
        "",
        "## Source Summary",
        "",
    ]
    for row in sheet["summaryRows"]:
        lines.append(
            f"- `{row['sourceType']}` / `{row['platform']}` / `{row['taskId'] or row['utmContent']}`: "
            f"{row['metricRows']} metrics, blocked {row['blockedRows']}, minimum {row['minimumKpiRows']}, lead-intent {row['leadIntentRows']}"
        )
    lines.extend(["", "## First 30 Collection Rows", ""])
    for row in sheet["rows"][:30]:
        lines.extend([
            f"### {row['sourceType']} · {row['platform']} · `{row['metric']}`",
            "",
            f"- task：`{row['taskId'] or row['utmContent']}`",
            f"- status：`{row['collectionStatus']}`",
            f"- gate：`{row['decisionGate']}`",
            f"- source：{row['primarySource']}",
            f"- proof：{row['requiredProof']}",
            f"- writeback：`{row['writebackTarget']}`",
            "",
        ])
    if len(sheet["rows"]) > 30:
        lines.append(f"_完整 {len(sheet['rows'])} rows 請看 CSV / JSON。_")
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "source_type": row["sourceType"],
                "platform": row["platform"],
                "task_id": row["taskId"],
                "script_id": row["scriptId"],
                "guardian_id": row["guardianId"],
                "utm_content": row["utmContent"],
                "metric": row["metric"],
                "category": row["category"],
                "collection_status": row["collectionStatus"],
                "source_url": row["trackedUrl"],
                "primary_source": row["primarySource"],
                "required_proof": row["requiredProof"],
                "zero_allowed": row["zeroAllowed"],
                "decision_gate": row["decisionGate"],
                "writeback_target": row["writebackTarget"],
                "blocked_by": row["blockedBy"],
            })


def main() -> int:
    parser = argparse.ArgumentParser(description="Build per-source KPI collection tasks from attribution rows and metric source rules.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    sheet = build_sheet()
    issues = validate_sheet(sheet)
    metrics = sheet["metrics"]
    print(f"promotion_data_collection_sources={metrics['sourceRows']}")
    print(f"promotion_data_collection_rows={metrics['collectionRows']}")
    print(f"promotion_data_collection_profile_rows={metrics['profileCollectionRows']}")
    print(f"promotion_data_collection_shorts_rows={metrics['shortsCollectionRows']}")
    print(f"promotion_data_collection_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_data_collection_lead_intent_rows={metrics['leadIntentRows']}")
    print(f"promotion_data_collection_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_data_collection_ready_rows={metrics['readyRows']}")
    print(f"promotion_data_collection_filled_rows={metrics['filledRows']}")
    print(f"promotion_data_collection_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1

    if not args.check:
        output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        output.write_text(render_markdown(sheet, issues), encoding="utf-8")
        json_output.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, sheet["rows"])
        print(f"promotion_data_collection_sheet={output.relative_to(ROOT)}")
        print(f"promotion_data_collection_sheet_json={json_output.relative_to(ROOT)}")
        print(f"promotion_data_collection_sheet_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
