#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
PROFILE_COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
FIRST_BATCH_COMPLETION = PROMOTION_DIR / "first-batch-completion-gate.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
LEAD_DEMAND = PROMOTION_DIR / "lead-demand-gate.json"
OFFER_PLAN = PROMOTION_DIR / "offer-experiment-plan.json"
COMMAND_CENTER = PROMOTION_DIR / "launch-command-center.json"
BLOCKER_RESOLUTION = PROMOTION_DIR / "blocker-resolution-checklist.json"
DECISION_INPUT = PROMOTION_DIR / "decision-input-matrix.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "stage-transition-matrix.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "stage-transition-matrix.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "stage-transition-matrix.csv"

TRANSITIONS = [
    {
        "fromStage": "profile_setup",
        "toStage": "first_batch_publish",
        "gateId": "profile_completion",
        "requiredMetric": "profileConfigured",
        "requiredValue": 3,
        "releaseCondition": "All three platform profile rows are set/live with profile_link_set_date and traceable proof.",
        "nextCommand": "python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_launch_readiness_gate.py --check",
        "fallbackAction": "Use profile proof import templates; do not publish first batch yet.",
    },
    {
        "fromStage": "first_batch_publish",
        "toStage": "first_batch_kpi",
        "gateId": "first_batch_publication",
        "requiredMetric": "firstBatchPublished",
        "requiredValue": 3,
        "releaseCondition": "First batch has three verified HTTPS post URLs written back.",
        "nextCommand": "python3 tools/promotion_first_batch_completion_gate.py --check",
        "fallbackAction": "Publish only after profile gate opens; reject placeholder URLs.",
    },
    {
        "fromStage": "first_batch_kpi",
        "toStage": "weekly_review",
        "gateId": "minimum_kpi",
        "requiredMetric": "firstBatchMinimumKpiRows",
        "requiredValue": 3,
        "releaseCondition": "Each first-batch post has site_clicks, quiz_starts, quiz_completions or checked-zero proof.",
        "nextCommand": "python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_week_decision_gate.py --check",
        "fallbackAction": "Keep KPI rows blank until the source was checked; 0 requires proof.",
    },
    {
        "fromStage": "weekly_review",
        "toStage": "lead_collection",
        "gateId": "weekly_review",
        "requiredMetric": "weeklyReady",
        "requiredValue": 1,
        "releaseCondition": "Weekly review is ready and empty-data mode is false before changing route or commerce emphasis.",
        "nextCommand": "python3 tools/promotion_decision_input_matrix.py --check && python3 tools/promotion_weekly_decision_evidence_checklist.py --check",
        "fallbackAction": "Keep collect_signal active; do not choose winner, paid CTA, Luna, or affiliate emphasis.",
    },
    {
        "fromStage": "lead_collection",
        "toStage": "offer_experiment",
        "gateId": "lead_demand",
        "requiredMetric": "leadReadyRoutes",
        "requiredValue": 1,
        "releaseCondition": "At least one guardian/intake route has repeated real demand, explicit consent, and traceable evidence.",
        "nextCommand": "python3 tools/promotion_lead_demand_gate.py --check && python3 tools/promotion_offer_experiment_plan.py --check",
        "fallbackAction": "Keep collecting real requests; do not build paid or priority offers from weak demand.",
    },
    {
        "fromStage": "offer_experiment",
        "toStage": "scale",
        "gateId": "offer_experiment",
        "requiredMetric": "readyOfferExperiments",
        "requiredValue": 1,
        "releaseCondition": "Offer experiment plan has at least one READY row with matching evidence and safety boundaries.",
        "nextCommand": "python3 tools/promotion_offer_experiment_queue.py --check && python3 tools/promotion_asset_fulfillment_gate.py --check",
        "fallbackAction": "Keep offer rows on HOLD; do not add paid CTA to first-touch Shorts.",
    },
]
CSV_FIELDS = [
    "from_stage",
    "to_stage",
    "gate_id",
    "status",
    "current_value",
    "required_value",
    "active_stage",
    "release_condition",
    "next_command",
    "fallback_action",
    "blocker",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def metric(data: dict, key: str, default: int = 0) -> int:
    metrics = data.get("metrics", {})
    if isinstance(metrics, dict):
        try:
            return int(metrics.get(key, default) or default)
        except (TypeError, ValueError):
            return default
    return default


def state_bool(data: dict, key: str) -> int:
    state = data.get("state", {})
    return 1 if isinstance(state, dict) and state.get(key) else 0


def current_values(master: dict, profile: dict, first_batch: dict, weekly: dict, lead: dict, offer: dict) -> dict[str, int]:
    return {
        "profileConfigured": metric(profile, "profileConfigured"),
        "firstBatchPublished": metric(first_batch, "publishedRows"),
        "firstBatchMinimumKpiRows": metric(first_batch, "minimumKpiRows"),
        "weeklyReady": state_bool(weekly, "readyForWeeklyDecision"),
        "leadReadyRoutes": metric(lead, "readyRoutes"),
        "readyOfferExperiments": int(offer.get("readyExperiments", 0) or 0),
        "commandReadyRows": metric(master, "commandReadyRows"),
    }


def blocker_for(stage: str, blockers: dict, decision_input: dict) -> str:
    rows = blockers.get("rows", []) if isinstance(blockers.get("rows"), list) else []
    if stage == "profile_setup":
        ready = [row.get("blocker_id", "") for row in rows if row.get("phase") == "profile_setup" and row.get("status") == "ready_to_act"]
        return ", ".join(ready[:3]) or "profile proof evidence is not complete"
    if stage == "first_batch_publish":
        return "first batch post URLs are not all verified"
    if stage == "first_batch_kpi":
        return "minimum KPI rows need checked source proof"
    if stage == "weekly_review":
        metrics = decision_input.get("metrics", {}) if isinstance(decision_input.get("metrics"), dict) else {}
        if metrics.get("emptyDataMode"):
            return "empty data mode is still active"
        return "weekly review gate is not ready"
    if stage == "lead_collection":
        return "no repeated consented real lead demand route"
    if stage == "offer_experiment":
        return "no READY offer experiment"
    return ""


def build_matrix() -> dict:
    master = load_json(MASTER_GATE)
    profile = load_json(PROFILE_COMPLETION)
    first_batch = load_json(FIRST_BATCH_COMPLETION)
    weekly = load_json(WEEKLY_REVIEW)
    lead = load_json(LEAD_DEMAND)
    offer = load_json(OFFER_PLAN)
    command = load_json(COMMAND_CENTER)
    blockers = load_json(BLOCKER_RESOLUTION)
    decision_input = load_json(DECISION_INPUT)

    active_stage = str(master.get("stage", ""))
    values = current_values(master, profile, first_batch, weekly, lead, offer)
    rows = []
    passed_so_far = True
    for item in TRANSITIONS:
        current_value = values.get(item["requiredMetric"], 0)
        complete = current_value >= int(item["requiredValue"])
        active = item["fromStage"] == active_stage
        if complete:
            status = "complete"
        elif active and passed_so_far:
            status = "current_blocker"
        elif passed_so_far:
            status = "next"
        else:
            status = "blocked_upstream"
        if not complete:
            passed_so_far = False
        rows.append({
            **item,
            "status": status,
            "activeStage": 1 if active else 0,
            "currentValue": current_value,
            "blocker": "" if complete else blocker_for(item["fromStage"], blockers, decision_input),
        })
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
            "profileCompletion": str(PROFILE_COMPLETION.relative_to(ROOT)),
            "firstBatchCompletion": str(FIRST_BATCH_COMPLETION.relative_to(ROOT)),
            "weeklyReview": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "leadDemand": str(LEAD_DEMAND.relative_to(ROOT)),
            "offerExperimentPlan": str(OFFER_PLAN.relative_to(ROOT)),
            "launchCommandCenter": str(COMMAND_CENTER.relative_to(ROOT)),
            "blockerResolution": str(BLOCKER_RESOLUTION.relative_to(ROOT)),
            "decisionInput": str(DECISION_INPUT.relative_to(ROOT)),
        },
        "stage": active_stage,
        "metrics": {
            "rows": len(rows),
            "completeRows": sum(1 for row in rows if row["status"] == "complete"),
            "currentBlockers": sum(1 for row in rows if row["status"] == "current_blocker"),
            "nextRows": sum(1 for row in rows if row["status"] == "next"),
            "blockedUpstreamRows": sum(1 for row in rows if row["status"] == "blocked_upstream"),
            "commandReadyRows": int(command.get("readyRows", 0) or 0),
            "commandBlockedRows": int(command.get("blockedRows", 0) or 0),
            "emptyDataMode": 1 if decision_input.get("metrics", {}).get("emptyDataMode") else 0,
        },
        "policy": {
            "oneCurrentBlocker": True,
            "noStageSkip": True,
            "profileBeforePublish": True,
            "minimumKpiBeforeWeeklyDecision": True,
            "leadEvidenceBeforeOffer": True,
        },
        "rows": rows,
    }


def validate_matrix(matrix: dict) -> list[str]:
    issues: list[str] = []
    rows = matrix.get("rows", [])
    if len(rows) != len(TRANSITIONS):
        issues.append(f"expected {len(TRANSITIONS)} transition rows, got {len(rows)}")
    current_blockers = [row for row in rows if row.get("status") == "current_blocker"]
    if len(current_blockers) != 1:
        issues.append("stage transition matrix should expose exactly one current blocker")
    if not matrix.get("policy", {}).get("noStageSkip"):
        issues.append("policy must prevent stage skips")
    for row in rows:
        label = f"{row.get('fromStage')}->{row.get('toStage')}"
        if row.get("status") not in {"complete", "current_blocker", "next", "blocked_upstream"}:
            issues.append(f"{label}: invalid status")
        if int(row.get("requiredValue", 0) or 0) < 1:
            issues.append(f"{label}: required value must be positive")
        if not row.get("releaseCondition") or not row.get("nextCommand") or not row.get("fallbackAction"):
            issues.append(f"{label}: missing release condition, command, or fallback")
        if row.get("status") in {"current_blocker", "next", "blocked_upstream"} and not row.get("blocker"):
            issues.append(f"{label}: non-complete transition needs blocker text")
    if matrix.get("stage") == "profile_setup" and rows[0].get("status") != "current_blocker":
        issues.append("profile_setup stage should put the first transition as current_blocker")
    return issues


def render_markdown(matrix: dict, issues: list[str]) -> str:
    metrics = matrix["metrics"]
    lines = [
        "# LoveTypes Stage Transition Matrix",
        "",
        f"- 產生日期：{matrix['generatedAt']}",
        f"- current stage：`{matrix['stage']}`",
        f"- rows：{metrics['rows']}",
        f"- complete rows：{metrics['completeRows']}",
        f"- current blockers：{metrics['currentBlockers']}",
        f"- blocked upstream rows：{metrics['blockedUpstreamRows']}",
        f"- command rows ready / blocked：{metrics['commandReadyRows']} / {metrics['commandBlockedRows']}",
        f"- empty data mode：{metrics['emptyDataMode']}",
        f"- issues：{len(issues)}",
        "",
        "## Policy",
        "",
        "- Do not skip stages.",
        "- Profile setup must complete before publishing.",
        "- Public post URLs and minimum KPI proof must complete before weekly decisions.",
        "- Lead evidence must be repeated, consented, and traceable before offer experiments.",
        "",
        "## Transitions",
        "",
    ]
    for row in matrix["rows"]:
        lines.extend([
            f"### `{row['fromStage']}` -> `{row['toStage']}`",
            "",
            f"- status：`{row['status']}`",
            f"- gate：`{row['gateId']}`",
            f"- value：{row['currentValue']} / {row['requiredValue']} `{row['requiredMetric']}`",
            f"- release：{row['releaseCondition']}",
            f"- next command：`{row['nextCommand']}`",
            f"- fallback：{row['fallbackAction']}",
            f"- blocker：{row['blocker'] or 'none'}",
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "from_stage": row["fromStage"],
                "to_stage": row["toStage"],
                "gate_id": row["gateId"],
                "status": row["status"],
                "current_value": row["currentValue"],
                "required_value": row["requiredValue"],
                "active_stage": row["activeStage"],
                "release_condition": row["releaseCondition"],
                "next_command": row["nextCommand"],
                "fallback_action": row["fallbackAction"],
                "blocker": row["blocker"],
            })


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the stage transition matrix for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    matrix = build_matrix()
    issues = validate_matrix(matrix)
    metrics = matrix["metrics"]
    print(f"promotion_stage_transition_rows={metrics['rows']}")
    print(f"promotion_stage_transition_complete={metrics['completeRows']}")
    print(f"promotion_stage_transition_current_blockers={metrics['currentBlockers']}")
    print(f"promotion_stage_transition_next_rows={metrics['nextRows']}")
    print(f"promotion_stage_transition_blocked_upstream={metrics['blockedUpstreamRows']}")
    print(f"promotion_stage_transition_command_ready={metrics['commandReadyRows']}")
    print(f"promotion_stage_transition_empty_data={metrics['emptyDataMode']}")
    print(f"promotion_stage_transition_issues={len(issues)}")
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
        print(f"promotion_stage_transition_matrix={output.relative_to(ROOT)}")
        print(f"promotion_stage_transition_matrix_json={json_output.relative_to(ROOT)}")
        print(f"promotion_stage_transition_matrix_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
