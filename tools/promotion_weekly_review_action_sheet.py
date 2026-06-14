#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
WEEKLY_DECISION_EVIDENCE = PROMOTION_DIR / "weekly-decision-evidence-checklist.json"
WEEK_DECISION_GATE = PROMOTION_DIR / "week-decision-gate.json"
FIRST_BATCH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
KPI_ACTION = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
LEAD_OPS_ACTION = PROMOTION_DIR / "lead-ops-action-sheet.json"
OUTPUT_MD = PROMOTION_DIR / "weekly-review-action-sheet.md"
OUTPUT_JSON = PROMOTION_DIR / "weekly-review-action-sheet.json"
OUTPUT_CSV = PROMOTION_DIR / "weekly-review-action-sheet.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_rows(
    weekly: dict,
    evidence: dict,
    gate: dict,
    first_batch: dict,
    kpi_action: dict,
    lead_ops: dict,
) -> list[dict[str, str]]:
    weekly_state = weekly.get("state", {}) if isinstance(weekly.get("state"), dict) else {}
    evidence_metrics = evidence.get("metrics", {}) if isinstance(evidence.get("metrics"), dict) else {}
    gate_gates = gate.get("gates", {}) if isinstance(gate.get("gates"), dict) else {}
    first_metrics = first_batch.get("metrics", {}) if isinstance(first_batch.get("metrics"), dict) else {}
    kpi_metrics = kpi_action.get("metrics", {}) if isinstance(kpi_action.get("metrics"), dict) else {}
    lead_metrics = lead_ops.get("metrics", {}) if isinstance(lead_ops.get("metrics"), dict) else {}
    ready_weekly = bool(weekly_state.get("readyForWeeklyDecision"))
    empty_data = bool(weekly_state.get("emptyDataMode")) or bool(gate.get("safety", {}).get("emptyDataFailClosed"))
    return [
        {
            "step_id": "profile-before-review",
            "phase": "precondition",
            "status": "blocked" if int(first_metrics.get("profileGateReady", 0) or 0) == 0 else "ready",
            "operator_action": "Confirm all platform profile links are set/live before using first-batch posts for weekly review.",
            "command": "python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_link_readiness_packet.py --check",
            "evidence_required": "profile_configured=3 and profile gate ready before publish/review.",
            "decision_boundary": "Without profile links, do not treat missing clicks as content failure.",
        },
        {
            "step_id": "first-batch-public-url",
            "phase": "publish",
            "status": "blocked" if int(first_metrics.get("ready", 0) or 0) == 0 else "ready_to_publish",
            "operator_action": "Publish or verify the first YouTube Shorts post and record the real public post URL.",
            "command": "python3 tools/promotion_first_batch_publish_action_sheet.py --check",
            "evidence_required": "Three real platform post_url values, not placeholders.",
            "decision_boundary": "No public URL means no weekly decision.",
        },
        {
            "step_id": "minimum-kpi-backfill",
            "phase": "kpi",
            "status": "blocked" if int(kpi_metrics.get("published", 0) or 0) == 0 else "ready_to_backfill",
            "operator_action": "Backfill site_clicks, quiz_starts and quiz_completions for each published first-batch post.",
            "command": "python3 tools/promotion_first_batch_kpi_action_sheet.py --check",
            "evidence_required": "Each 0 value has a checked platform or site source, not an assumption.",
            "decision_boundary": "Zero without source is still unknown.",
        },
        {
            "step_id": "weekly-evidence-check",
            "phase": "review",
            "status": "blocked" if int(evidence_metrics.get("pendingRows", 0) or 0) else "ready",
            "operator_action": "Run the weekly decision evidence checklist and require all evidence rows to complete before ranking content.",
            "command": "python3 tools/promotion_weekly_decision_evidence_checklist.py --check",
            "evidence_required": f"complete={evidence_metrics.get('completeRows', 0)}, pending={evidence_metrics.get('pendingRows', 0)}.",
            "decision_boundary": "Pending evidence keeps all commerce and winner decisions on HOLD.",
        },
        {
            "step_id": "weekly-review-packet",
            "phase": "review",
            "status": "ready" if ready_weekly and not empty_data else "hold",
            "operator_action": "Regenerate weekly summary, decision gate and review packet before changing the next content batch.",
            "command": "python3 tools/promotion_weekly_summary.py && python3 tools/promotion_week_decision_gate.py && python3 tools/promotion_weekly_review_packet.py",
            "evidence_required": f"weekly_ready={1 if ready_weekly else 0}, empty_data={1 if empty_data else 0}.",
            "decision_boundary": "Empty data mode allows only setup, publish, and KPI backfill actions.",
        },
        {
            "step_id": "lead-and-offer-safety",
            "phase": "commerce",
            "status": "blocked" if int(lead_metrics.get("readyRoutes", 0) or 0) == 0 else "ready_route_present",
            "operator_action": "Check lead demand before building owned assets, Luna packs or paid offer experiments.",
            "command": "python3 tools/promotion_lead_ops_action_sheet.py --check && python3 tools/promotion_lead_demand_gate.py --check",
            "evidence_required": f"lead_ready_routes={lead_metrics.get('readyRoutes', 0)}, repeated_routes={lead_metrics.get('repeatedRoutes', 0)}.",
            "decision_boundary": "No repeated lead demand means no paid or priority offer build.",
        },
        {
            "step_id": "allowed-decision-scope",
            "phase": "decision",
            "status": "hold" if not bool(gate_gates.get("weeklyDecision")) else "ready",
            "operator_action": "Use week-decision-gate as the only source of truth for allowed next decisions.",
            "command": "python3 tools/promotion_week_decision_gate.py --check",
            "evidence_required": f"weeklyDecision={1 if gate_gates.get('weeklyDecision') else 0}, testSoftOffer={1 if gate_gates.get('testSoftOffer') else 0}.",
            "decision_boundary": "Do not alter offer order, guardian priority, Luna emphasis, or affiliate weighting unless gate allows it.",
        },
    ]


def build_sheet() -> dict:
    weekly = load_json(WEEKLY_REVIEW)
    evidence = load_json(WEEKLY_DECISION_EVIDENCE)
    gate = load_json(WEEK_DECISION_GATE)
    first_batch = load_json(FIRST_BATCH_ACTION)
    kpi_action = load_json(KPI_ACTION)
    lead_ops = load_json(LEAD_OPS_ACTION)
    rows = build_rows(weekly, evidence, gate, first_batch, kpi_action, lead_ops)
    weekly_state = weekly.get("state", {}) if isinstance(weekly.get("state"), dict) else {}
    evidence_metrics = evidence.get("metrics", {}) if isinstance(evidence.get("metrics"), dict) else {}
    metrics = {
        "rows": len(rows),
        "readyRows": sum(1 for row in rows if str(row["status"]).startswith("ready")),
        "blockedRows": sum(1 for row in rows if str(row["status"]).startswith("blocked")),
        "holdRows": sum(1 for row in rows if str(row["status"]) == "hold"),
        "weeklyReady": 1 if weekly_state.get("readyForWeeklyDecision") else 0,
        "emptyData": 1 if weekly_state.get("emptyDataMode") else 0,
        "evidencePending": int(evidence_metrics.get("pendingRows", 0) or 0),
        "evidenceComplete": int(evidence_metrics.get("completeRows", 0) or 0),
    }
    issues: list[str] = []
    if metrics["rows"] != 7:
        issues.append(f"expected 7 weekly review action rows, got {metrics['rows']}")
    if metrics["emptyData"] and any(row["status"] == "ready" and row["phase"] in {"commerce", "decision"} for row in rows):
        issues.append("empty data mode cannot mark commerce or decision rows ready")
    if metrics["weeklyReady"] and metrics["evidencePending"]:
        issues.append("weekly review cannot be ready while evidence remains pending")
    if not weekly or not evidence or not gate:
        issues.append("weekly review action sheet missing source packet")
    return {
        "generatedAt": today(),
        "sources": {
            "weeklyReview": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "weeklyDecisionEvidence": str(WEEKLY_DECISION_EVIDENCE.relative_to(ROOT)),
            "weekDecisionGate": str(WEEK_DECISION_GATE.relative_to(ROOT)),
            "firstBatchAction": str(FIRST_BATCH_ACTION.relative_to(ROOT)),
            "kpiAction": str(KPI_ACTION.relative_to(ROOT)),
            "leadOpsAction": str(LEAD_OPS_ACTION.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Weekly review is not a commerce decision until public URLs, minimum KPIs and evidence rows are complete.",
            "Empty data mode fails closed: keep setup, publishing and KPI backfill only.",
            "Do not pick a winning guardian, change offer order or increase paid CTA from zero or missing data.",
            "Lead and offer experiments require repeated guardian demand, not a single click or template row.",
        ],
        "issues": issues,
    }


def render_markdown(sheet: dict) -> str:
    metrics = sheet["metrics"]
    lines = [
        "# LoveTypes Weekly Review Action Sheet",
        "",
        f"- 產生日期：{sheet['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready rows：{metrics['readyRows']}",
        f"- blocked rows：{metrics['blockedRows']}",
        f"- hold rows：{metrics['holdRows']}",
        f"- weekly ready：{metrics['weeklyReady']}",
        f"- empty data：{metrics['emptyData']}",
        f"- evidence pending：{metrics['evidencePending']}",
        f"- issues：{len(sheet['issues'])}",
        "",
        "## Rule",
        "",
    ]
    lines.extend(f"- {rule}" for rule in sheet["rules"])
    lines.extend(["", "## Actions", ""])
    for row in sheet["rows"]:
        lines.extend([
            f"### {row['step_id']}",
            "",
            f"- phase：`{row['phase']}`",
            f"- status：`{row['status']}`",
            f"- action：{row['operator_action']}",
            f"- command：`{row['command']}`",
            f"- evidence：{row['evidence_required']}",
            f"- boundary：{row['decision_boundary']}",
            "",
        ])
    if sheet["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in sheet["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(sheet: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(sheet), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["step_id", "phase", "status", "operator_action", "command", "evidence_required", "decision_boundary"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sheet["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an action sheet for weekly LoveTypes promotion review decisions.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    sheet = build_sheet()
    metrics = sheet["metrics"]
    if not args.check:
        write_outputs(sheet)
        print(f"promotion_weekly_review_action_sheet={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_weekly_review_action_sheet_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_weekly_review_action_sheet_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_weekly_review_action_rows={metrics['rows']}")
    print(f"promotion_weekly_review_action_ready_rows={metrics['readyRows']}")
    print(f"promotion_weekly_review_action_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_weekly_review_action_hold_rows={metrics['holdRows']}")
    print(f"promotion_weekly_review_action_weekly_ready={metrics['weeklyReady']}")
    print(f"promotion_weekly_review_action_empty_data={metrics['emptyData']}")
    print(f"promotion_weekly_review_action_evidence_pending={metrics['evidencePending']}")
    print(f"promotion_weekly_review_action_evidence_complete={metrics['evidenceComplete']}")
    print(f"promotion_weekly_review_action_issues={len(sheet['issues'])}")
    for issue in sheet["issues"]:
        print(issue)
    return 1 if sheet["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
