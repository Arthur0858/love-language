#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
DATA_COLLECTION_PATH = PROMOTION_DIR / "data-collection-sheet.json"
WEEK_DECISION_PATH = PROMOTION_DIR / "week-decision-gate.json"
DECISION_READINESS_PATH = PROMOTION_DIR / "decision-readiness-checklist.json"
WEEKLY_REVIEW_PATH = PROMOTION_DIR / "weekly-review-packet.json"
LEAD_DEMAND_PATH = PROMOTION_DIR / "lead-demand-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "decision-input-matrix.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "decision-input-matrix.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "decision-input-matrix.csv"

DECISION_INPUTS = [
    {
        "decisionId": "collect_signal",
        "gateKey": "weeklyDecision",
        "requiredMetrics": ["profile_clicks", "site_clicks", "quiz_starts", "quiz_completions"],
        "requiredCollectionStatuses": {"blocked_until_profile_set", "blocked_until_public_post_url", "ready_for_source_check", "filled"},
        "minimumFilled": 0,
        "allowedAction": "Set profiles, publish first batch, and backfill public URLs plus minimum KPI evidence.",
        "blockedAction": "Change offer order, pick a winning guardian, or increase paid CTA.",
    },
    {
        "decisionId": "scale_content",
        "gateKey": "scaleContent",
        "requiredMetrics": ["site_clicks", "quiz_starts", "quiz_completions"],
        "requiredCollectionStatuses": {"filled"},
        "minimumFilled": 3,
        "allowedAction": "Publish more variants for the strongest guardian or pain point while keeping quiz CTA.",
        "blockedAction": "Treat views, likes, or comments as proof of purchase intent.",
    },
    {
        "decisionId": "deepen_identity_asset",
        "gateKey": "deepenIdentityAsset",
        "requiredMetrics": [
            "guardian_result_clicks",
            "resources_clicks",
            "repair_plan_clicks",
            "luna_clicks",
            "keepsake_clicks",
            "free_keepsake_downloads",
        ],
        "requiredCollectionStatuses": {"filled"},
        "minimumFilled": 1,
        "allowedAction": "Improve free keepsakes, story cards, share images, and result-route assets.",
        "blockedAction": "Move the primary CTA directly to paid products.",
    },
    {
        "decisionId": "build_owned_lead_asset",
        "gateKey": "buildOwnedLeadAsset",
        "requiredMetrics": ["supply_lead_requests", "contact_requests"],
        "requiredCollectionStatuses": {"filled"},
        "minimumFilled": 1,
        "allowedAction": "Build one low-risk email/download asset for the signaled guardian or route.",
        "blockedAction": "Build a paid product before repeated lead evidence and explicit consent exist.",
    },
    {
        "decisionId": "test_soft_offer",
        "gateKey": "testSoftOffer",
        "requiredMetrics": ["luna_pack_clicks", "affiliate_book_clicks", "quiz_completions"],
        "requiredCollectionStatuses": {"filled"},
        "minimumFilled": 2,
        "allowedAction": "Test a soft result-route Luna or affiliate offer after the quiz/result context.",
        "blockedAction": "Use direct sales language in first-touch Shorts or profile bio.",
    },
]
CSV_FIELDS = [
    "decision_id",
    "gate_key",
    "gate_open",
    "decision_status",
    "required_metrics",
    "input_rows",
    "filled_rows",
    "ready_rows",
    "blocked_rows",
    "minimum_filled",
    "primary_blocker",
    "allowed_action",
    "blocked_action",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def collection_rows_by_metric(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("metric", "")), []).append(row)
    return grouped


def readiness_lookup(readiness: dict) -> dict[str, dict]:
    items = readiness.get("items", [])
    if not isinstance(items, list):
        return {}
    return {str(row.get("decision_id", "")): row for row in items}


def metric_rows(grouped: dict[str, list[dict]], metrics: list[str]) -> list[dict]:
    rows: list[dict] = []
    for metric in metrics:
        rows.extend(grouped.get(metric, []))
    return rows


def count_status(rows: list[dict], statuses: set[str]) -> int:
    return sum(1 for row in rows if str(row.get("collectionStatus", "")) in statuses)


def build_matrix() -> dict:
    data_collection = load_json(DATA_COLLECTION_PATH)
    week_decision = load_json(WEEK_DECISION_PATH)
    readiness = load_json(DECISION_READINESS_PATH)
    weekly_review = load_json(WEEKLY_REVIEW_PATH)
    lead_demand = load_json(LEAD_DEMAND_PATH)
    grouped = collection_rows_by_metric(data_collection.get("rows", []))
    gates = week_decision.get("gates", {}) if isinstance(week_decision.get("gates"), dict) else {}
    readiness_rows = readiness_lookup(readiness)
    rows = []
    for spec in DECISION_INPUTS:
        inputs = metric_rows(grouped, spec["requiredMetrics"])
        filled_rows = count_status(inputs, {"filled"})
        ready_rows = count_status(inputs, {"ready_for_source_check", "optional_after_minimum_kpi", "waiting_for_real_lead_or_review"})
        blocked_rows = sum(1 for row in inputs if str(row.get("collectionStatus", "")).startswith("blocked"))
        gate_open = bool(gates.get(spec["gateKey"]))
        readiness_status = str(readiness_rows.get(spec["decisionId"], {}).get("status", "unknown"))
        enough_inputs = filled_rows >= int(spec["minimumFilled"])
        if gate_open and enough_inputs:
            decision_status = "ready"
            primary_blocker = ""
        elif spec["decisionId"] == "collect_signal":
            decision_status = "active"
            primary_blocker = ""
        elif blocked_rows:
            decision_status = "blocked_waiting_for_source"
            primary_blocker = "required source rows are still blocked by profile/post/KPI setup"
        elif not enough_inputs:
            decision_status = "blocked_insufficient_signal"
            primary_blocker = "required filled KPI rows have not reached the minimum signal"
        else:
            decision_status = "blocked_by_gate"
            primary_blocker = "week decision gate is not open"
        rows.append({
            "decisionId": spec["decisionId"],
            "gateKey": spec["gateKey"],
            "gateOpen": gate_open,
            "readinessStatus": readiness_status,
            "decisionStatus": decision_status,
            "requiredMetrics": list(spec["requiredMetrics"]),
            "inputRows": len(inputs),
            "filledRows": filled_rows,
            "readyRows": ready_rows,
            "blockedRows": blocked_rows,
            "minimumFilled": int(spec["minimumFilled"]),
            "primaryBlocker": primary_blocker,
            "allowedAction": spec["allowedAction"],
            "blockedAction": spec["blockedAction"],
        })
    empty_data_mode = bool(weekly_review.get("state", {}).get("emptyDataMode")) or bool(week_decision.get("safety", {}).get("emptyDataFailClosed"))
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "dataCollection": str(DATA_COLLECTION_PATH.relative_to(ROOT)),
            "weekDecision": str(WEEK_DECISION_PATH.relative_to(ROOT)),
            "decisionReadiness": str(DECISION_READINESS_PATH.relative_to(ROOT)),
            "weeklyReview": str(WEEKLY_REVIEW_PATH.relative_to(ROOT)),
            "leadDemand": str(LEAD_DEMAND_PATH.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "readyRows": sum(1 for row in rows if row["decisionStatus"] == "ready"),
            "activeRows": sum(1 for row in rows if row["decisionStatus"] == "active"),
            "blockedRows": sum(1 for row in rows if row["decisionStatus"].startswith("blocked")),
            "inputRows": sum(int(row["inputRows"]) for row in rows),
            "filledInputRows": sum(int(row["filledRows"]) for row in rows),
            "blockedInputRows": sum(int(row["blockedRows"]) for row in rows),
            "leadReadyRoutes": int(lead_demand.get("metrics", {}).get("readyRoutes", 0) or 0),
            "emptyDataMode": 1 if empty_data_mode else 0,
        },
        "policy": {
            "decisionRequiresGateAndInputs": True,
            "emptyDataBlocksCommerce": True,
            "platformEngagementCannotOpenCommerce": True,
            "leadDecisionsRequireExplicitConsent": True,
        },
        "rows": rows,
    }


def validate_matrix(matrix: dict) -> list[str]:
    issues: list[str] = []
    rows = matrix.get("rows", [])
    expected = {item["decisionId"] for item in DECISION_INPUTS}
    actual = {row.get("decisionId") for row in rows}
    if actual != expected:
        issues.append("decision input matrix must cover every decision")
    if matrix.get("metrics", {}).get("rows") != len(DECISION_INPUTS):
        issues.append(f"expected {len(DECISION_INPUTS)} decision input rows")
    if matrix.get("metrics", {}).get("emptyDataMode") and matrix.get("metrics", {}).get("readyRows"):
        issues.append("empty data mode cannot have ready decision rows")
    if not matrix.get("policy", {}).get("decisionRequiresGateAndInputs"):
        issues.append("policy must require both gate and inputs")
    for row in rows:
        label = str(row.get("decisionId", "<unknown>"))
        if not row.get("requiredMetrics"):
            issues.append(f"{label}: missing required metrics")
        if int(row.get("inputRows", 0) or 0) == 0:
            issues.append(f"{label}: required metrics did not match data collection rows")
        if row.get("decisionStatus") == "ready" and (not row.get("gateOpen") or int(row.get("filledRows", 0) or 0) < int(row.get("minimumFilled", 0) or 0)):
            issues.append(f"{label}: ready decision must have open gate and enough filled inputs")
        if row.get("decisionStatus", "").startswith("blocked") and not row.get("primaryBlocker"):
            issues.append(f"{label}: blocked decision must include primary blocker")
        if row.get("decisionId") != "collect_signal" and row.get("decisionStatus") == "active":
            issues.append(f"{label}: only collect_signal can be active")
    return issues


def render_markdown(matrix: dict, issues: list[str]) -> str:
    metrics = matrix["metrics"]
    lines = [
        "# LoveTypes Decision Input Matrix",
        "",
        f"- 產生日期：{matrix['generatedAt']}",
        f"- decisions：{metrics['rows']}",
        f"- ready decisions：{metrics['readyRows']}",
        f"- active decisions：{metrics['activeRows']}",
        f"- blocked decisions：{metrics['blockedRows']}",
        f"- input rows：{metrics['inputRows']}",
        f"- filled input rows：{metrics['filledInputRows']}",
        f"- blocked input rows：{metrics['blockedInputRows']}",
        f"- lead ready routes：{metrics['leadReadyRoutes']}",
        f"- empty data mode：{metrics['emptyDataMode']}",
        f"- issues：{len(issues)}",
        "",
        "## Rules",
        "",
        "- A decision needs both an open week gate and enough filled input rows.",
        "- Empty-data mode blocks commerce, offer order changes, Luna emphasis, affiliate emphasis, and winning-guardian decisions.",
        "- Platform engagement alone cannot open commerce decisions.",
        "- Lead decisions require explicit consent and traceable evidence.",
        "",
        "## Decisions",
        "",
    ]
    for row in matrix["rows"]:
        lines.extend([
            f"### `{row['decisionId']}`",
            "",
            f"- status：`{row['decisionStatus']}`",
            f"- gate：`{row['gateKey']}` open={int(row['gateOpen'])}",
            f"- readiness checklist：`{row['readinessStatus']}`",
            f"- required metrics：`{', '.join(row['requiredMetrics'])}`",
            f"- inputs：{row['inputRows']} rows; filled {row['filledRows']}; ready {row['readyRows']}; blocked {row['blockedRows']}",
            f"- minimum filled：{row['minimumFilled']}",
            f"- blocker：{row['primaryBlocker'] or 'none'}",
            f"- allowed：{row['allowedAction']}",
            f"- blocked：{row['blockedAction']}",
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
                "decision_id": row["decisionId"],
                "gate_key": row["gateKey"],
                "gate_open": int(row["gateOpen"]),
                "decision_status": row["decisionStatus"],
                "required_metrics": "|".join(row["requiredMetrics"]),
                "input_rows": row["inputRows"],
                "filled_rows": row["filledRows"],
                "ready_rows": row["readyRows"],
                "blocked_rows": row["blockedRows"],
                "minimum_filled": row["minimumFilled"],
                "primary_blocker": row["primaryBlocker"],
                "allowed_action": row["allowedAction"],
                "blocked_action": row["blockedAction"],
            })


def main() -> int:
    parser = argparse.ArgumentParser(description="Build decision-to-input evidence matrix for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    matrix = build_matrix()
    issues = validate_matrix(matrix)
    metrics = matrix["metrics"]
    print(f"promotion_decision_input_rows={metrics['rows']}")
    print(f"promotion_decision_input_ready={metrics['readyRows']}")
    print(f"promotion_decision_input_active={metrics['activeRows']}")
    print(f"promotion_decision_input_blocked={metrics['blockedRows']}")
    print(f"promotion_decision_input_input_rows={metrics['inputRows']}")
    print(f"promotion_decision_input_filled_rows={metrics['filledInputRows']}")
    print(f"promotion_decision_input_blocked_input_rows={metrics['blockedInputRows']}")
    print(f"promotion_decision_input_lead_ready_routes={metrics['leadReadyRoutes']}")
    print(f"promotion_decision_input_empty_data={metrics['emptyDataMode']}")
    print(f"promotion_decision_input_issues={len(issues)}")
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
        print(f"promotion_decision_input_matrix={output.relative_to(ROOT)}")
        print(f"promotion_decision_input_matrix_json={json_output.relative_to(ROOT)}")
        print(f"promotion_decision_input_matrix_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
