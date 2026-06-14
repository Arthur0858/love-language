#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PUBLISH_KPI_HANDOFF = PROMOTION_DIR / "publish-kpi-handoff.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
WEEK_DECISION = PROMOTION_DIR / "week-decision-gate.json"
WEEKLY_EVIDENCE = PROMOTION_DIR / "weekly-decision-evidence-checklist.json"
LEAD_OPS = PROMOTION_DIR / "lead-ops-action-sheet.json"
LEAD_DEMAND = PROMOTION_DIR / "lead-demand-gate.json"
ASSET_FULFILLMENT = PROMOTION_DIR / "asset-fulfillment-gate.json"
OFFER_PLAN = PROMOTION_DIR / "offer-experiment-plan.json"
OFFER_QUEUE = PROMOTION_DIR / "offer-experiment-queue.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "weekly-lead-offer-handoff.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "weekly-lead-offer-handoff.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "weekly-lead-offer-handoff.csv"

CSV_FIELDS = [
    "step_id",
    "phase",
    "status",
    "current_value",
    "required_value",
    "owner_action",
    "evidence_required",
    "command",
    "stop_condition",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def metric(data: dict, key: str, default: int = 0) -> int:
    values = data.get("metrics", {})
    if not isinstance(values, dict):
        return default
    try:
        return int(values.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def state(data: dict, key: str) -> int:
    values = data.get("state", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def gate(data: dict, key: str) -> int:
    values = data.get("gates", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def count_ready_offers(data: dict) -> int:
    if "readyExperiments" in data:
        try:
            return int(data.get("readyExperiments") or 0)
        except (TypeError, ValueError):
            return 0
    return metric(data, "ready")


def build_rows() -> list[dict[str, object]]:
    publish_kpi = load_json(PUBLISH_KPI_HANDOFF)
    weekly = load_json(WEEKLY_REVIEW)
    week_decision = load_json(WEEK_DECISION)
    weekly_evidence = load_json(WEEKLY_EVIDENCE)
    lead_ops = load_json(LEAD_OPS)
    lead_demand = load_json(LEAD_DEMAND)
    asset_gate = load_json(ASSET_FULFILLMENT)
    offer_plan = load_json(OFFER_PLAN)
    offer_queue = load_json(OFFER_QUEUE)

    publish_ready = metric(publish_kpi, "readyForWeeklyReview")
    weekly_ready = state(weekly, "readyForWeeklyDecision")
    empty_data_off = 1 if not state(weekly, "emptyDataMode") else 0
    weekly_gate = gate(week_decision, "weeklyDecision")
    evidence_complete = metric(weekly_evidence, "completeRows")
    evidence_rows = metric(weekly_evidence, "rows", 8)
    lead_form_ready = 1 if metric(lead_ops, "readyRows") >= 1 and metric(lead_ops, "leadMagnetIssues") == 0 else 0
    real_leads = metric(lead_demand, "realLeads")
    ready_routes = metric(lead_demand, "readyRoutes")
    repeated_routes = metric(lead_demand, "repeatedDemandRoutes")
    public_free_ready = metric(asset_gate, "publicFreeReady")
    ready_demand_pairs = metric(asset_gate, "readyDemandPairs")
    ready_offer_assets = metric(asset_gate, "readyOfferAssets")
    ready_offer_plan = count_ready_offers(offer_plan)
    ready_offer_queue = metric(offer_queue, "ready")

    rows: list[dict[str, object]] = [
        {
            "step_id": "weekly_review_open",
            "phase": "weekly_review",
            "current_value": publish_ready,
            "required_value": 1,
            "owner_action": "Start lead and offer evaluation only after publish/KPI handoff opens weekly review.",
            "evidence_required": "publish-kpi-handoff readyForWeeklyReview is true.",
            "command": "python3 tools/promotion_publish_kpi_handoff.py --check",
            "stop_condition": "Do not evaluate lead or offer routes while post URLs or minimum KPI proof are incomplete.",
        },
        {
            "step_id": "weekly_decision_ready",
            "phase": "weekly_review",
            "current_value": weekly_ready + empty_data_off + weekly_gate,
            "required_value": 3,
            "owner_action": "Confirm weekly review, week decision gate, and non-empty data mode before route decisions.",
            "evidence_required": "weekly review ready=1, weeklyDecision gate=1, emptyDataMode=0.",
            "command": "python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_week_decision_gate.py --check",
            "stop_condition": "Do not pick winners or change commerce order while empty data mode is true.",
        },
        {
            "step_id": "weekly_evidence_complete",
            "phase": "weekly_review",
            "current_value": evidence_complete,
            "required_value": evidence_rows,
            "owner_action": "Complete weekly evidence checks before choosing content, asset, Luna, or affiliate direction.",
            "evidence_required": "weekly-decision-evidence-checklist completeRows equals rows.",
            "command": "python3 tools/promotion_weekly_decision_evidence_checklist.py --check",
            "stop_condition": "Stop if any weekly decision evidence row remains pending.",
        },
        {
            "step_id": "lead_capture_ready",
            "phase": "lead_collection",
            "current_value": lead_form_ready,
            "required_value": 1,
            "owner_action": "Keep Contact, keepsake, and Luna requests importable before using them as lead signals.",
            "evidence_required": "lead ops action sheet has ready capture checks and lead magnet inventory issues=0.",
            "command": "python3 tools/promotion_lead_ops_action_sheet.py --check",
            "stop_condition": "Do not collect raw sensitive content or use requests without explicit reply consent.",
        },
        {
            "step_id": "lead_demand_ready",
            "phase": "lead_collection",
            "current_value": ready_routes,
            "required_value": 1,
            "owner_action": "Advance to owned assets or Luna only after repeated same-guardian demand creates a ready route.",
            "evidence_required": "lead-demand-gate readyRoutes >= 1 with traceable evidence and explicit consent.",
            "command": "python3 tools/promotion_lead_demand_gate.py --check",
            "stop_condition": "Do not create paid or priority assets from a single request, weak signal, or no consent.",
        },
        {
            "step_id": "asset_fulfillment_ready",
            "phase": "asset_fulfillment",
            "current_value": ready_demand_pairs + ready_offer_assets,
            "required_value": 1,
            "owner_action": "Prepare only the smallest matching free asset or Luna aftercare item for proven demand.",
            "evidence_required": "asset-fulfillment-gate has at least one ready demand pair or ready offer asset.",
            "command": "python3 tools/promotion_asset_fulfillment_gate.py --check",
            "stop_condition": "Keep public free assets available, but do not build custom products before demand proof.",
        },
        {
            "step_id": "offer_experiment_ready",
            "phase": "offer_experiment",
            "current_value": min(ready_offer_plan, ready_offer_queue),
            "required_value": 1,
            "owner_action": "Only run low-risk offer experiments when both plan and queue have READY rows.",
            "evidence_required": "offer-experiment-plan and offer-experiment-queue both have at least one READY row.",
            "command": "python3 tools/promotion_offer_experiment_plan.py --check && python3 tools/promotion_offer_experiment_queue.py --check",
            "stop_condition": "Do not add paid CTA to Shorts or claim diagnosis, therapy, guarantee, or required purchase.",
        },
        {
            "step_id": "public_free_assets_remain_safe",
            "phase": "safety",
            "current_value": 1 if public_free_ready >= 5 and real_leads == 0 and repeated_routes == 0 else 0,
            "required_value": 1,
            "owner_action": "Keep five public free assets as safe lead magnets while real demand is absent.",
            "evidence_required": "asset-fulfillment-gate publicFreeReady >= 5 and lead-demand-gate has no repeated route.",
            "command": "python3 tools/promotion_asset_fulfillment_gate.py --check && python3 tools/promotion_lead_demand_gate.py --check",
            "stop_condition": "Stop if public free assets are treated as proof of product demand without tracked requests.",
        },
    ]
    for index, row in enumerate(rows):
        current = int(row["current_value"] or 0)
        required = int(row["required_value"] or 0)
        if current >= required:
            row["status"] = "complete"
        elif any(previous.get("status") != "complete" for previous in rows[:index]):
            row["status"] = "blocked_upstream"
        else:
            row["status"] = "current_blocker"
    return rows


def validate_rows(rows: list[dict[str, object]]) -> list[str]:
    issues: list[str] = []
    if len(rows) != 8:
        issues.append(f"expected 8 handoff rows, got {len(rows)}")
    statuses = {str(row.get("status", "")) for row in rows}
    if not statuses <= {"complete", "current_blocker", "blocked_upstream"}:
        issues.append("handoff rows contain invalid statuses")
    current_blockers = sum(1 for row in rows if row.get("status") == "current_blocker")
    if current_blockers != 1:
        issues.append("weekly lead offer handoff should expose exactly one current blocker")
    for row in rows:
        label = str(row.get("step_id", "<missing>"))
        if not row.get("command") or not row.get("stop_condition"):
            issues.append(f"{label}: missing command or stop condition")
        if int(row.get("required_value", 0) or 0) < 1:
            issues.append(f"{label}: required value must be positive")
    return issues


def build_handoff() -> dict:
    rows = build_rows()
    issues = validate_rows(rows)
    lead_demand = load_json(LEAD_DEMAND)
    asset_gate = load_json(ASSET_FULFILLMENT)
    offer_plan = load_json(OFFER_PLAN)
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "publishKpiHandoff": str(PUBLISH_KPI_HANDOFF.relative_to(ROOT)),
            "weeklyReviewPacket": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "weekDecisionGate": str(WEEK_DECISION.relative_to(ROOT)),
            "weeklyDecisionEvidence": str(WEEKLY_EVIDENCE.relative_to(ROOT)),
            "leadOpsActionSheet": str(LEAD_OPS.relative_to(ROOT)),
            "leadDemandGate": str(LEAD_DEMAND.relative_to(ROOT)),
            "assetFulfillmentGate": str(ASSET_FULFILLMENT.relative_to(ROOT)),
            "offerExperimentPlan": str(OFFER_PLAN.relative_to(ROOT)),
            "offerExperimentQueue": str(OFFER_QUEUE.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "completeRows": sum(1 for row in rows if row["status"] == "complete"),
            "currentBlockers": sum(1 for row in rows if row["status"] == "current_blocker"),
            "blockedUpstreamRows": sum(1 for row in rows if row["status"] == "blocked_upstream"),
            "realLeads": metric(lead_demand, "realLeads"),
            "readyLeadRoutes": metric(lead_demand, "readyRoutes"),
            "publicFreeReady": metric(asset_gate, "publicFreeReady"),
            "readyOfferExperiments": count_ready_offers(offer_plan),
            "issues": len(issues),
        },
        "policy": {
            "weeklyReviewBeforeLeadDecision": True,
            "explicitConsentBeforeLeadDemand": True,
            "repeatedDemandBeforeAssetBuild": True,
            "offerReadyBeforePaidCta": True,
            "shortsCtaRemainsQuiz": True,
        },
        "rows": rows,
        "issues": issues,
    }


def render_markdown(handoff: dict) -> str:
    metrics = handoff["metrics"]
    lines = [
        "# LoveTypes Weekly to Lead and Offer Handoff",
        "",
        f"- 產生日期：{handoff['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- complete rows：{metrics['completeRows']}",
        f"- current blockers：{metrics['currentBlockers']}",
        f"- blocked upstream rows：{metrics['blockedUpstreamRows']}",
        f"- real leads：{metrics['realLeads']}",
        f"- ready lead routes：{metrics['readyLeadRoutes']}",
        f"- public free assets ready：{metrics['publicFreeReady']}",
        f"- ready offer experiments：{metrics['readyOfferExperiments']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rule",
        "",
        "- Weekly review must open before lead, asset, Luna, affiliate, or offer decisions.",
        "- Real lead demand requires explicit consent, traceable proof, and repeated same-guardian signal.",
        "- Free public assets may stay available, but they are not proof of product demand.",
        "- Paid or priority offer experiments require READY plan and queue rows.",
        "",
        "## Handoff Steps",
        "",
    ]
    for row in handoff["rows"]:
        lines.extend([
            f"### `{row['step_id']}`",
            "",
            f"- phase：`{row['phase']}`",
            f"- status：`{row['status']}`",
            f"- value：{row['current_value']} / {row['required_value']}",
            f"- action：{row['owner_action']}",
            f"- evidence：{row['evidence_required']}",
            f"- command：`{row['command']}`",
            f"- stop：{row['stop_condition']}",
            "",
        ])
    if handoff["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in handoff["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the weekly-review to lead/offer handoff checklist for LoveTypes promotion.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    handoff = build_handoff()
    metrics = handoff["metrics"]
    print(f"promotion_weekly_lead_offer_handoff_rows={metrics['rows']}")
    print(f"promotion_weekly_lead_offer_handoff_complete={metrics['completeRows']}")
    print(f"promotion_weekly_lead_offer_handoff_current_blockers={metrics['currentBlockers']}")
    print(f"promotion_weekly_lead_offer_handoff_blocked_upstream={metrics['blockedUpstreamRows']}")
    print(f"promotion_weekly_lead_offer_handoff_real_leads={metrics['realLeads']}")
    print(f"promotion_weekly_lead_offer_handoff_ready_routes={metrics['readyLeadRoutes']}")
    print(f"promotion_weekly_lead_offer_handoff_public_free_ready={metrics['publicFreeReady']}")
    print(f"promotion_weekly_lead_offer_handoff_ready_offers={metrics['readyOfferExperiments']}")
    print(f"promotion_weekly_lead_offer_handoff_issues={metrics['issues']}")
    for issue in handoff["issues"]:
        print(issue)
    if handoff["issues"]:
        return 1
    if not args.check:
        output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        output.write_text(render_markdown(handoff), encoding="utf-8")
        json_output.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, handoff["rows"])
        print(f"promotion_weekly_lead_offer_handoff={output.relative_to(ROOT)}")
        print(f"promotion_weekly_lead_offer_handoff_json={json_output.relative_to(ROOT)}")
        print(f"promotion_weekly_lead_offer_handoff_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
