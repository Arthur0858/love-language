#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LAUNCH_READINESS = PROMOTION_DIR / "launch-readiness-gate.json"
PROFILE_COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
FIRST_BATCH_COMPLETION = PROMOTION_DIR / "first-batch-completion-gate.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
LEAD_DEMAND = PROMOTION_DIR / "lead-demand-gate.json"
OFFER_PLAN = PROMOTION_DIR / "offer-experiment-plan.json"
COMMAND_CENTER = PROMOTION_DIR / "launch-command-center.json"
NEXT_ACTIONS = PROMOTION_DIR / "next-actions.json"
MD_OUTPUT = PROMOTION_DIR / "master-gate.md"
JSON_OUTPUT = PROMOTION_DIR / "master-gate.json"


STAGES = (
    "profile_setup",
    "first_batch_publish",
    "first_batch_kpi",
    "weekly_review",
    "lead_collection",
    "offer_experiment",
    "scale",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def metric(data: dict, key: str, default: int = 0) -> int:
    metrics = data.get("metrics", {})
    if not isinstance(metrics, dict):
        return default
    try:
        return int(metrics.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def state_bool(data: dict, key: str) -> bool:
    state = data.get("state", {})
    return bool(state.get(key)) if isinstance(state, dict) else False


def first_blocker_ids(data: dict) -> list[str]:
    blockers = data.get("blockers", [])
    if not isinstance(blockers, list):
        return []
    ids = []
    for blocker in blockers:
        if isinstance(blocker, dict):
            ids.append(str(blocker.get("id", "")))
        else:
            ids.append(str(blocker))
    return [item for item in ids if item]


def determine_stage(profile: dict, first_batch: dict, weekly: dict, lead: dict, offer: dict) -> tuple[str, str]:
    if not state_bool(profile, "readyForFirstBatchPublish"):
        return "profile_setup", "Finish three platform profile links, then run profile writeback and refresh ops docs."
    if not state_bool(first_batch, "firstBatchPublished"):
        return "first_batch_publish", "Publish the first-batch Shorts on three platforms and write back real post URLs."
    if not state_bool(first_batch, "minimumKpiComplete"):
        return "first_batch_kpi", "Fill or verified-zero site_clicks, quiz_starts, and quiz_completions for each first-batch post."
    if not weekly.get("state", {}).get("readyForWeeklyDecision"):
        return "weekly_review", "Refresh weekly summary and week decision gates before any offer decision."
    if metric(lead, "readyRoutes") == 0:
        return "lead_collection", "Keep collecting real requests; do not build paid or priority offers from weak demand."
    if int(offer.get("readyExperiments", 0) or 0) == 0:
        return "offer_experiment", "Wait for offer experiment plan to open a READY row before production."
    return "scale", "Run the ready offer experiment with safety QA and KPI writeback."


def build_gate() -> dict:
    launch = load_json(LAUNCH_READINESS)
    profile = load_json(PROFILE_COMPLETION)
    first_batch = load_json(FIRST_BATCH_COMPLETION)
    weekly = load_json(WEEKLY_REVIEW)
    lead = load_json(LEAD_DEMAND)
    offer = load_json(OFFER_PLAN)
    command = load_json(COMMAND_CENTER)
    next_actions = load_json(NEXT_ACTIONS)

    stage, next_action = determine_stage(profile, first_batch, weekly, lead, offer)
    stage_index = STAGES.index(stage)
    gate_states = [
        {
            "id": "launch_readiness",
            "status": "open" if launch.get("readiness", {}).get("readyToStartSetup") else "blocked",
            "blockers": first_blocker_ids(launch),
        },
        {
            "id": "profile_completion",
            "status": "open" if state_bool(profile, "readyForFirstBatchPublish") else "blocked",
            "blockers": first_blocker_ids(profile),
        },
        {
            "id": "first_batch_completion",
            "status": "open" if state_bool(first_batch, "readyForWeeklyReview") else "blocked",
            "blockers": first_blocker_ids(first_batch),
        },
        {
            "id": "weekly_review",
            "status": "open" if weekly.get("state", {}).get("readyForWeeklyDecision") else "blocked",
            "blockers": list(weekly.get("holdReasons", [])) if isinstance(weekly.get("holdReasons"), list) else [],
        },
        {
            "id": "lead_demand",
            "status": "open" if metric(lead, "readyRoutes") > 0 else "blocked",
            "blockers": first_blocker_ids(lead),
        },
        {
            "id": "offer_experiment",
            "status": "open" if int(offer.get("readyExperiments", 0) or 0) > 0 else "blocked",
            "blockers": [str(item) for item in offer.get("blockers", [])] if isinstance(offer.get("blockers"), list) else [],
        },
    ]
    blocked_decisions = [
        "change_offer_order",
        "pick_winning_guardian",
        "increase_paid_cta",
        "prioritize_luna_or_affiliate",
        "build_paid_product_from_empty_data",
    ]
    if stage_index < STAGES.index("weekly_review"):
        blocked_decisions.extend(["weekly_decision", "offer_experiment", "scale_content"])
    if stage_index < STAGES.index("lead_collection"):
        blocked_decisions.extend(["build_owned_asset_from_lead", "luna_pack_production"])

    issues: list[str] = []
    if stage not in STAGES:
        issues.append(f"unknown stage: {stage}")
    if stage == "profile_setup" and state_bool(profile, "readyForFirstBatchPublish"):
        issues.append("profile_setup stage cannot be active when profile completion is ready")
    if stage != "profile_setup" and not state_bool(profile, "readyForFirstBatchPublish"):
        issues.append("cannot leave profile_setup before profile completion gate opens")
    if stage_index >= STAGES.index("weekly_review") and not state_bool(first_batch, "readyForWeeklyReview"):
        issues.append("weekly or later stage requires first batch completion")
    if stage_index >= STAGES.index("offer_experiment") and metric(lead, "readyRoutes") == 0:
        issues.append("offer stage requires at least one ready lead demand route")
    if command.get("readyRows") is not None and int(command.get("readyRows", 0) or 0) < 1:
        issues.append("command center should expose at least one ready operational row")
    if next_actions.get("dataState", {}).get("emptyDataMode") and stage_index >= STAGES.index("offer_experiment"):
        issues.append("empty data mode cannot enter offer experiment stage")

    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "launchReadiness": str(LAUNCH_READINESS.relative_to(ROOT)),
            "profileCompletion": str(PROFILE_COMPLETION.relative_to(ROOT)),
            "firstBatchCompletion": str(FIRST_BATCH_COMPLETION.relative_to(ROOT)),
            "weeklyReview": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "leadDemand": str(LEAD_DEMAND.relative_to(ROOT)),
            "offerExperimentPlan": str(OFFER_PLAN.relative_to(ROOT)),
            "commandCenter": str(COMMAND_CENTER.relative_to(ROOT)),
            "nextActions": str(NEXT_ACTIONS.relative_to(ROOT)),
        },
        "stage": stage,
        "stageIndex": stage_index,
        "stageOrder": list(STAGES),
        "nextAction": next_action,
        "metrics": {
            "profileConfigured": metric(profile, "profileConfigured"),
            "expectedProfiles": metric(profile, "expectedProfiles"),
            "firstBatchPublished": metric(first_batch, "publishedRows"),
            "firstBatchMinimumKpiRows": metric(first_batch, "minimumKpiRows"),
            "leadReadyRoutes": metric(lead, "readyRoutes"),
            "readyOfferExperiments": int(offer.get("readyExperiments", 0) or 0),
            "commandReadyRows": int(command.get("readyRows", 0) or 0),
            "commandBlockedRows": int(command.get("blockedRows", 0) or 0),
            "issues": len(issues),
        },
        "gateStates": gate_states,
        "allowedNow": [
            "set_platform_profile_links",
            "verify_profile_utm",
            "writeback_profile_proof",
        ] if stage == "profile_setup" else [stage],
        "blockedDecisions": sorted(set(blocked_decisions)),
        "safety": {
            "emptyDataMode": bool(next_actions.get("dataState", {}).get("emptyDataMode")),
            "keepShortsCtaQuiz": True,
            "doNotClaim": ["診斷", "療效", "保證修復", "必須購買"],
        },
        "issues": issues,
    }


def render_markdown(gate: dict) -> str:
    metrics = gate["metrics"]
    lines = [
        "# LoveTypes Promotion Master Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- current stage：`{gate['stage']}` ({gate['stageIndex']} / {len(gate['stageOrder']) - 1})",
        f"- next action：{gate['nextAction']}",
        f"- profile configured：{metrics['profileConfigured']} / {metrics['expectedProfiles']}",
        f"- first batch published：{metrics['firstBatchPublished']} / 3",
        f"- minimum KPI rows：{metrics['firstBatchMinimumKpiRows']} / 3",
        f"- lead ready routes：{metrics['leadReadyRoutes']}",
        f"- ready offer experiments：{metrics['readyOfferExperiments']}",
        f"- command rows ready / blocked：{metrics['commandReadyRows']} / {metrics['commandBlockedRows']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Gate States",
        "",
    ]
    for item in gate["gateStates"]:
        lines.append(f"- `{item['id']}`：{item['status']}（blockers: {len(item['blockers'])}）")
    lines.extend([
        "",
        "## Allowed Now",
        "",
    ])
    lines.extend(f"- `{item}`" for item in gate["allowedNow"])
    lines.extend(["", "## Blocked Decisions", ""])
    lines.extend(f"- `{item}`" for item in gate["blockedDecisions"])
    lines.extend([
        "",
        "## Safety",
        "",
        f"- emptyDataMode：`{int(gate['safety']['emptyDataMode'])}`",
        "- Shorts / profile CTA stays on the 15-question guardian quiz.",
        "- Do not claim diagnosis, therapeutic outcome, guaranteed repair, or required purchase.",
    ])
    if gate["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in gate["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(gate: dict) -> None:
    JSON_OUTPUT.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(render_markdown(gate), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the master stage gate for LoveTypes first-round promotion operations.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    args = parser.parse_args()

    gate = build_gate()
    if not args.check:
        write_outputs(gate)
        print(f"promotion_master_gate={MD_OUTPUT}")
        print(f"promotion_master_gate_json={JSON_OUTPUT}")
    metrics = gate["metrics"]
    print(f"promotion_master_stage={gate['stage']}")
    print(f"promotion_master_stage_index={gate['stageIndex']}")
    print(f"promotion_master_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_master_first_batch_published={metrics['firstBatchPublished']}")
    print(f"promotion_master_minimum_kpi_rows={metrics['firstBatchMinimumKpiRows']}")
    print(f"promotion_master_lead_ready_routes={metrics['leadReadyRoutes']}")
    print(f"promotion_master_ready_offer_experiments={metrics['readyOfferExperiments']}")
    print(f"promotion_master_command_ready_rows={metrics['commandReadyRows']}")
    print(f"promotion_master_blocked_decisions={len(gate['blockedDecisions'])}")
    print(f"promotion_master_issues={metrics['issues']}")
    for issue in gate["issues"]:
        print(issue)
    return 1 if metrics["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
