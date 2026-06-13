#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
FUNNEL_EVENTS_PATH = ROOT / "funnel-events.json"
KPI_TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PLATFORM_KPI_TRACKER_PATH = PROMOTION_DIR / "platform-kpi-tracker.csv"
PLATFORM_PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
LEAD_TRACKER_PATH = PROMOTION_DIR / "lead-intake-tracker.csv"
ATTRIBUTION_PATH = PROMOTION_DIR / "attribution-reconciliation.csv"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "metric-source-matrix.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "metric-source-matrix.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "metric-source-matrix.csv"

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
MANUAL_LEAD_FIELDS = {"supply_lead_requests", "luna_pack_clicks", "contact_requests"}
MINIMUM_DECISION_FIELDS = {"site_clicks", "quiz_starts", "quiz_completions"}
ROUTE_FIELDS = {
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
    "free_keepsake_downloads",
    "affiliate_book_clicks",
}
PLATFORM_FIELDS = {"views", "likes", "comments", "shares", "profile_clicks"}
CSV_FIELDS = [
    "metric",
    "category",
    "primary_source",
    "tracker_files",
    "required_proof",
    "zero_allowed",
    "zero_rule",
    "decision_use",
    "manual_writeback",
    "safety_boundary",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def csv_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


def event_map() -> dict[str, list[str]]:
    kit = load_json(KIT_PATH)
    measurement = kit.get("measurementPlan") if isinstance(kit.get("measurementPlan"), dict) else {}
    rows = measurement.get("eventKpiMap") if isinstance(measurement.get("eventKpiMap"), list) else []
    return {
        str(row.get("kpi", "")): [str(event) for event in row.get("events", [])]
        for row in rows
        if isinstance(row, dict) and row.get("kpi")
    }


def source_policy(metric: str, events: list[str]) -> dict[str, str]:
    if metric in PLATFORM_FIELDS:
        return {
            "category": "platform_engagement",
            "primary_source": "Platform analytics screen for the published post or profile link.",
            "required_proof": "public post/profile URL plus analytics screenshot or checked proof note.",
            "zero_allowed": "yes_after_public_source_check",
            "zero_rule": "0 is valid only after the public URL exists and the platform analytics screen has been checked for the same date window.",
            "decision_use": "Useful for creative learning, but cannot choose a winning guardian or product path without site and quiz data.",
            "manual_writeback": "promotion_post_writeback.py or promotion_profile_writeback.py",
        }
    if metric in MINIMUM_DECISION_FIELDS:
        return {
            "category": "site_conversion",
            "primary_source": "Website analytics or event log filtered by tracked_url / utm_content.",
            "required_proof": "post/profile URL, tracked UTM, analytics date window, and proof note.",
            "zero_allowed": "yes_after_site_source_check",
            "zero_rule": "0 is valid only after the site analytics source was checked; blank is not the same as 0.",
            "decision_use": "Minimum required for weekly review; quiz_completions is the main first-round success signal.",
            "manual_writeback": "promotion_post_writeback.py or promotion_profile_writeback.py",
        }
    if metric in ROUTE_FIELDS:
        return {
            "category": "route_interest",
            "primary_source": "Website event catalog: " + (", ".join(events) if events else "mapped route events"),
            "required_proof": "site event count or checked-zero proof note tied to the same UTM row.",
            "zero_allowed": "yes_after_site_source_check",
            "zero_rule": "0 can inform route ordering only after minimum decision fields are also checked.",
            "decision_use": "Supports route sequencing after quiz completion exists; does not justify paid-product production by itself.",
            "manual_writeback": "promotion_post_writeback.py, promotion_profile_writeback.py, or weekly review rollup",
        }
    if metric in MANUAL_LEAD_FIELDS:
        return {
            "category": "lead_or_revenue_intent",
            "primary_source": "lead-intake-tracker.csv plus traceable consent/evidence; optional matching UTM attribution.",
            "required_proof": "real user request, explicit_reply_ok consent, traceable email/thread/proof note, and safe notes without raw sensitive content.",
            "zero_allowed": "no_without_review",
            "zero_rule": "Do not write fake 0 demand from silence; keep blank until the lead window is reviewed, then document checked-zero separately.",
            "decision_use": "Can open owned asset or Luna experiments only after repeated same-guardian demand and matching gates.",
            "manual_writeback": "promotion_lead_writeback.py",
        }
    return {
        "category": "unclassified",
        "primary_source": "",
        "required_proof": "",
        "zero_allowed": "no",
        "zero_rule": "",
        "decision_use": "",
        "manual_writeback": "",
    }


def build_matrix() -> dict:
    event_lookup = event_map()
    rows = []
    for metric in POST_METRIC_FIELDS:
        policy = source_policy(metric, event_lookup.get(metric, []))
        tracker_files = ["kpi-tracker.csv", "platform-kpi-tracker.csv"]
        if metric in PROFILE_METRIC_FIELDS:
            tracker_files.append("platform-profile-tracker.csv")
        if metric in MANUAL_LEAD_FIELDS:
            tracker_files.append("lead-intake-tracker.csv")
        rows.append({
            "metric": metric,
            "category": policy["category"],
            "primarySource": policy["primary_source"],
            "trackerFiles": tracker_files,
            "requiredProof": policy["required_proof"],
            "zeroAllowed": policy["zero_allowed"],
            "zeroRule": policy["zero_rule"],
            "decisionUse": policy["decision_use"],
            "manualWriteback": policy["manual_writeback"],
            "safetyBoundary": (
                "Do not use this metric to claim diagnosis, therapeutic outcome, guaranteed repair, or required purchase."
            ),
            "eventNames": event_lookup.get(metric, []),
        })
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "promotionKit": str(KIT_PATH.relative_to(ROOT)),
            "funnelEvents": str(FUNNEL_EVENTS_PATH.relative_to(ROOT)),
            "kpiTracker": str(KPI_TRACKER_PATH.relative_to(ROOT)),
            "platformKpiTracker": str(PLATFORM_KPI_TRACKER_PATH.relative_to(ROOT)),
            "platformProfileTracker": str(PLATFORM_PROFILE_TRACKER_PATH.relative_to(ROOT)),
            "leadTracker": str(LEAD_TRACKER_PATH.relative_to(ROOT)),
            "attribution": str(ATTRIBUTION_PATH.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "platformFields": sum(1 for row in rows if row["category"] == "platform_engagement"),
            "siteConversionFields": sum(1 for row in rows if row["category"] == "site_conversion"),
            "routeInterestFields": sum(1 for row in rows if row["category"] == "route_interest"),
            "leadIntentFields": sum(1 for row in rows if row["category"] == "lead_or_revenue_intent"),
        },
        "rows": rows,
    }


def validate_matrix(matrix: dict) -> list[str]:
    issues: list[str] = []
    kpi_header = csv_header(KPI_TRACKER_PATH)
    platform_header = csv_header(PLATFORM_KPI_TRACKER_PATH)
    profile_header = csv_header(PLATFORM_PROFILE_TRACKER_PATH)
    lead_header = csv_header(LEAD_TRACKER_PATH)
    metrics = [row.get("metric", "") for row in matrix.get("rows", [])]
    if metrics != POST_METRIC_FIELDS:
        issues.append("metric source matrix rows must match post metric field order")
    for metric in POST_METRIC_FIELDS:
        if metric not in kpi_header:
            issues.append(f"kpi-tracker.csv missing {metric}")
        if metric not in platform_header:
            issues.append(f"platform-kpi-tracker.csv missing {metric}")
    for metric in PROFILE_METRIC_FIELDS:
        if metric not in profile_header:
            issues.append(f"platform-profile-tracker.csv missing {metric}")
    for metric in MANUAL_LEAD_FIELDS:
        if "kpi_writeback_field" not in lead_header:
            issues.append("lead-intake-tracker.csv missing kpi_writeback_field")
        if not any(row.get("metric") == metric and "lead-intake-tracker.csv" in row.get("trackerFiles", []) for row in matrix["rows"]):
            issues.append(f"{metric}: lead-intake tracker is not listed")
    for row in matrix["rows"]:
        label = row.get("metric", "<unknown>")
        if row.get("category") == "unclassified":
            issues.append(f"{label}: unclassified metric")
        for field in ("primarySource", "requiredProof", "zeroRule", "decisionUse", "manualWriteback", "safetyBoundary"):
            if not row.get(field):
                issues.append(f"{label}: missing {field}")
        if row.get("zeroAllowed") not in {"yes_after_public_source_check", "yes_after_site_source_check", "no_without_review"}:
            issues.append(f"{label}: unsupported zeroAllowed policy")
        if label in MINIMUM_DECISION_FIELDS and row.get("category") != "site_conversion":
            issues.append(f"{label}: minimum decision field must be site_conversion")
        if label in MANUAL_LEAD_FIELDS and row.get("category") != "lead_or_revenue_intent":
            issues.append(f"{label}: manual lead field must be lead_or_revenue_intent")
    return issues


def render_markdown(matrix: dict, issues: list[str]) -> str:
    metrics = matrix["metrics"]
    lines = [
        "# LoveTypes Metric Source Matrix",
        "",
        f"- 產生日期：{matrix['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- platform fields：{metrics['platformFields']}",
        f"- site conversion fields：{metrics['siteConversionFields']}",
        f"- route interest fields：{metrics['routeInterestFields']}",
        f"- lead / revenue-intent fields：{metrics['leadIntentFields']}",
        f"- issues：{len(issues)}",
        "",
        "## Operating Rules",
        "",
        "- Blank is unknown; 0 is valid only after the matching source window is checked.",
        "- Weekly and product decisions require site / quiz data, not platform engagement alone.",
        "- Lead-intent fields require explicit consent and traceable evidence before they influence product work.",
        "- Do not store raw sensitive email content in trackers.",
        "",
        "## Metrics",
        "",
    ]
    for row in matrix["rows"]:
        lines.extend([
            f"### `{row['metric']}`",
            "",
            f"- category：`{row['category']}`",
            f"- primary source：{row['primarySource']}",
            f"- trackers：{', '.join(row['trackerFiles'])}",
            f"- required proof：{row['requiredProof']}",
            f"- zero policy：`{row['zeroAllowed']}`；{row['zeroRule']}",
            f"- decision use：{row['decisionUse']}",
            f"- writeback：`{row['manualWriteback']}`",
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "metric": row["metric"],
                "category": row["category"],
                "primary_source": row["primarySource"],
                "tracker_files": "|".join(row["trackerFiles"]),
                "required_proof": row["requiredProof"],
                "zero_allowed": row["zeroAllowed"],
                "zero_rule": row["zeroRule"],
                "decision_use": row["decisionUse"],
                "manual_writeback": row["manualWriteback"],
                "safety_boundary": row["safetyBoundary"],
            })


def main() -> int:
    parser = argparse.ArgumentParser(description="Build KPI source-of-truth rules for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    matrix = build_matrix()
    issues = validate_matrix(matrix)
    metrics = matrix["metrics"]
    print(f"promotion_metric_source_rows={metrics['rows']}")
    print(f"promotion_metric_source_platform_fields={metrics['platformFields']}")
    print(f"promotion_metric_source_site_conversion_fields={metrics['siteConversionFields']}")
    print(f"promotion_metric_source_route_interest_fields={metrics['routeInterestFields']}")
    print(f"promotion_metric_source_lead_intent_fields={metrics['leadIntentFields']}")
    print(f"promotion_metric_source_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1

    if not args.check:
        output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        output.write_text(render_markdown(matrix, issues), encoding="utf-8")
        json_output.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, matrix["rows"])
        print(f"promotion_metric_source_matrix={output.relative_to(ROOT)}")
        print(f"promotion_metric_source_matrix_json={json_output.relative_to(ROOT)}")
        print(f"promotion_metric_source_matrix_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
