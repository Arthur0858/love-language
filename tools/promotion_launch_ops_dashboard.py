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
COMMAND_CENTER = PROMOTION_DIR / "launch-command-center.json"
NEXT_ACTIONS = PROMOTION_DIR / "next-actions.json"
OPERATOR_HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
PROFILE_READINESS = PROMOTION_DIR / "profile-link-readiness-packet.json"
PROFILE_PROOF_READINESS = PROMOTION_DIR / "profile-proof-readiness-pack.json"
PUBLISH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
KPI_ACTION = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
LEAD_OPS = PROMOTION_DIR / "lead-ops-action-sheet.json"
WEEKLY_ACTION = PROMOTION_DIR / "weekly-review-action-sheet.json"
PROFILE_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
PUBLISH_KPI_HANDOFF = PROMOTION_DIR / "publish-kpi-handoff.json"
WEEKLY_LEAD_OFFER_HANDOFF = PROMOTION_DIR / "weekly-lead-offer-handoff.json"
OUTPUT_MD = PROMOTION_DIR / "launch-ops-dashboard.md"
OUTPUT_JSON = PROMOTION_DIR / "launch-ops-dashboard.json"
OUTPUT_CSV = PROMOTION_DIR / "launch-ops-dashboard.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def metric(data: dict, key: str, default: int = 0) -> int:
    metrics = data.get("metrics", {})
    if isinstance(metrics, dict):
        try:
            return int(metrics.get(key, default) or 0)
        except (TypeError, ValueError):
            return default
    try:
        return int(data.get(key, default) or 0)
    except (TypeError, ValueError):
        return default


def status_from_counts(ready: int, blocked: int, hold: int = 0) -> str:
    if blocked:
        return "blocked"
    if hold:
        return "hold"
    if ready:
        return "ready"
    return "waiting"


def next_actions_status(master: dict, next_actions: dict) -> str:
    if not next_actions.get("actions"):
        return "waiting"
    master_metrics = master.get("metrics", {}) if isinstance(master.get("metrics"), dict) else {}
    profile_configured = int(master_metrics.get("profileConfigured", 0) or 0)
    expected_profiles = max(1, int(master_metrics.get("expectedProfiles", 1) or 1))
    if str(master.get("stage", "")) == "profile_setup" and profile_configured < expected_profiles:
        return "actionable_profile_setup"
    if any(str(action.get("priority", "")) == "blocked" for action in next_actions.get("actions", [])):
        return "blocked"
    return "ready"


def build_rows(bundle: dict[str, dict]) -> list[dict[str, str]]:
    master = bundle["master"]
    command = bundle["command"]
    next_actions = bundle["next"]
    handoff = bundle["handoff"]
    profile = bundle["profile"]
    profile_proof = bundle["profile_proof"]
    publish = bundle["publish"]
    kpi = bundle["kpi"]
    lead = bundle["lead"]
    weekly = bundle["weekly"]
    profile_handoff = bundle["profile_handoff"]
    publish_kpi_handoff = bundle["publish_kpi_handoff"]
    weekly_lead_offer_handoff = bundle["weekly_lead_offer_handoff"]
    master_metrics = master.get("metrics", {}) if isinstance(master.get("metrics"), dict) else {}
    handoff_state = handoff.get("state", {}) if isinstance(handoff.get("state"), dict) else {}
    profile_ready_to_configure = metric(profile, "readyToConfigure")
    profile_configured = metric(profile, "configured")
    profile_public_ready = metric(profile, "publicReady")
    profile_proof_rows = metric(profile_proof, "rows")
    profile_proof_real_ready = metric(profile_proof, "realProofReadyRows")
    profile_proof_blockers = max(0, profile_proof_rows - profile_proof_real_ready)
    profile_status = (
        "ready"
        if metric(profile, "profileGateReady") > 0
        else "actionable"
        if profile_ready_to_configure > profile_configured and profile_public_ready >= profile_ready_to_configure
        else "blocked"
    )
    rows = [
        {
            "area": "master_gate",
            "status": str(master.get("stage", "unknown")),
            "ready": str(master_metrics.get("commandReadyRows", 0)),
            "blocked": str(master_metrics.get("commandBlockedRows", 0)),
            "next_action": str(master.get("nextAction", "Follow current stage gate.")),
            "evidence": f"profile={master_metrics.get('profileConfigured', 0)}/{master_metrics.get('expectedProfiles', 1)}, first_batch={master_metrics.get('firstBatchPublished', 0)}, kpi_rows={master_metrics.get('firstBatchMinimumKpiRows', 0)}",
            "safety": "Use master gate as final stage source; do not skip profile_setup.",
        },
        {
            "area": "profile_setup",
            "status": profile_status,
            "ready": str(profile_ready_to_configure),
            "blocked": str(max(0, int(master_metrics.get("expectedProfiles", 1) or 1) - profile_configured)),
            "next_action": "Set active platform profile links and write back proof.",
            "evidence": f"public_ready={profile_public_ready}, configured={profile_configured}, real_proof={profile_proof_real_ready}/{profile_proof_rows}, ready_to_writeback={metric(profile, 'readyToWriteback')}",
            "safety": "Do not mark set/live without real screenshot or click proof from the platform.",
        },
        {
            "area": "first_batch_publish",
            "status": status_from_counts(metric(publish, "ready"), metric(publish, "blocked")),
            "ready": str(metric(publish, "ready")),
            "blocked": str(metric(publish, "blocked")),
            "next_action": "Publish first-batch posts only after profile gate is ready.",
            "evidence": f"complete={metric(publish, 'complete')}, profile_gate={metric(publish, 'profileGateReady')}",
            "safety": "No placeholder post URLs; keep CTA focused on quiz.",
        },
        {
            "area": "minimum_kpi",
            "status": status_from_counts(metric(kpi, "ready"), metric(kpi, "blocked")),
            "ready": str(metric(kpi, "ready")),
            "blocked": str(metric(kpi, "blocked")),
            "next_action": "Backfill post_url, site_clicks, quiz_starts and quiz_completions after publish.",
            "evidence": f"published={metric(kpi, 'published')}, zero_source_rows={metric(kpi, 'zeroSourceRows')}",
            "safety": "A zero needs a checked source; unknown is not zero.",
        },
        {
            "area": "lead_ops",
            "status": status_from_counts(metric(lead, "readyRows"), metric(lead, "blockedRows"), metric(lead, "waitingRows")),
            "ready": str(metric(lead, "readyRows")),
            "blocked": str(metric(lead, "blockedRows") + metric(lead, "waitingRows")),
            "next_action": "Use structured request import when real Contact or keepsake emails arrive.",
            "evidence": f"real_leads={metric(lead, 'realLeads')}, ready_routes={metric(lead, 'readyRoutes')}, story_assets={metric(lead, 'storyAssets')}",
            "safety": "No raw email in CSV; no offer build without repeated demand.",
        },
        {
            "area": "weekly_review",
            "status": status_from_counts(metric(weekly, "readyRows"), metric(weekly, "blockedRows"), metric(weekly, "holdRows")),
            "ready": str(metric(weekly, "readyRows")),
            "blocked": str(metric(weekly, "blockedRows") + metric(weekly, "holdRows")),
            "next_action": "Keep weekly review on hold until public URLs, KPIs and evidence rows are complete.",
            "evidence": f"weekly_ready={metric(weekly, 'weeklyReady')}, empty_data={metric(weekly, 'emptyData')}, evidence_pending={metric(weekly, 'evidencePending')}",
            "safety": "No winning guardian, offer order change, Luna emphasis or affiliate weighting in empty data mode.",
        },
        {
            "area": "operator_handoff",
            "status": "blocked" if int(handoff.get("blockedCount", 0) or 0) else "ready",
            "ready": str(handoff.get("readyCount", 0)),
            "blocked": str(handoff.get("blockedCount", 0)),
            "next_action": "Follow the handoff packet for structured proof imports and do-not-do rules.",
            "evidence": f"profile_pending={handoff_state.get('profilePending', 0)}, first_batch_pending={handoff_state.get('firstBatchPending', 0)}, weekly_ready={1 if handoff_state.get('weeklyReviewReady') else 0}",
            "safety": "Keep external operations evidence-backed.",
        },
        {
            "area": "profile_publish_handoff",
            "status": "blocked" if metric(profile_handoff, "readyToPublish") == 0 else "ready",
            "ready": str(metric(profile_handoff, "completeRows")),
            "blocked": str(metric(profile_handoff, "currentBlockers") + metric(profile_handoff, "blockedUpstreamRows")),
            "next_action": "Use this gate to hand off completed profile proof into first-batch publishing.",
            "evidence": f"ready_to_publish={metric(profile_handoff, 'readyToPublish')}, current_blockers={metric(profile_handoff, 'currentBlockers')}, blocked_upstream={metric(profile_handoff, 'blockedUpstreamRows')}",
            "safety": "No first-batch publishing until profile proof and refreshed packets are complete.",
        },
        {
            "area": "publish_kpi_handoff",
            "status": "blocked" if metric(publish_kpi_handoff, "readyForWeeklyReview") == 0 else "ready",
            "ready": str(metric(publish_kpi_handoff, "completeRows")),
            "blocked": str(metric(publish_kpi_handoff, "currentBlockers") + metric(publish_kpi_handoff, "blockedUpstreamRows")),
            "next_action": "Use this gate to hand off public post URLs and minimum KPI into weekly review.",
            "evidence": f"published={metric(publish_kpi_handoff, 'publishedRows')}, minimum_kpi={metric(publish_kpi_handoff, 'minimumKpiRows')}, weekly={metric(publish_kpi_handoff, 'readyForWeeklyReview')}",
            "safety": "No weekly review or commerce decision until post URL, proof, and KPI checks are complete.",
        },
        {
            "area": "weekly_lead_offer_handoff",
            "status": "blocked" if metric(weekly_lead_offer_handoff, "readyLeadRoutes") == 0 and metric(weekly_lead_offer_handoff, "readyOfferExperiments") == 0 else "ready",
            "ready": str(metric(weekly_lead_offer_handoff, "completeRows")),
            "blocked": str(metric(weekly_lead_offer_handoff, "currentBlockers") + metric(weekly_lead_offer_handoff, "blockedUpstreamRows")),
            "next_action": "Use this gate to move weekly signals into lead, asset, Luna, or offer work only when evidence exists.",
            "evidence": f"real_leads={metric(weekly_lead_offer_handoff, 'realLeads')}, ready_routes={metric(weekly_lead_offer_handoff, 'readyLeadRoutes')}, ready_offers={metric(weekly_lead_offer_handoff, 'readyOfferExperiments')}",
            "safety": "Public free assets are safe lead magnets, not proof of product demand.",
        },
        {
            "area": "next_actions",
            "status": next_actions_status(master, next_actions),
            "ready": str(command.get("readyRows", 0)),
            "blocked": str(command.get("blockedRows", 0)),
            "next_action": "Only profile setup is currently actionable; publishing remains blocked until profile proof is written back.",
            "evidence": f"selected_tasks={len(next_actions.get('selectedTasks', []))}, command_rows={command.get('rowCount', 0)}",
            "safety": "A next-actions packet can include blocked downstream work; follow status and master gate before acting.",
        },
    ]
    return rows


def build_dashboard() -> dict:
    bundle = {
        "master": load_json(MASTER_GATE),
        "command": load_json(COMMAND_CENTER),
        "next": load_json(NEXT_ACTIONS),
        "handoff": load_json(OPERATOR_HANDOFF),
        "profile": load_json(PROFILE_READINESS),
        "profile_proof": load_json(PROFILE_PROOF_READINESS),
        "publish": load_json(PUBLISH_ACTION),
        "kpi": load_json(KPI_ACTION),
        "lead": load_json(LEAD_OPS),
        "weekly": load_json(WEEKLY_ACTION),
        "profile_handoff": load_json(PROFILE_HANDOFF),
        "publish_kpi_handoff": load_json(PUBLISH_KPI_HANDOFF),
        "weekly_lead_offer_handoff": load_json(WEEKLY_LEAD_OFFER_HANDOFF),
    }
    rows = build_rows(bundle)
    blocked = sum(1 for row in rows if row["status"] == "blocked")
    hold = sum(1 for row in rows if row["status"] == "hold")
    actionable = sum(1 for row in rows if str(row["status"]).startswith("actionable"))
    ready = sum(1 for row in rows if row["status"] == "ready")
    master_metrics = bundle["master"].get("metrics", {}) if isinstance(bundle["master"].get("metrics"), dict) else {}
    profile_proof_metrics = bundle["profile_proof"].get("metrics", {}) if isinstance(bundle["profile_proof"].get("metrics"), dict) else {}
    profile_proof_rows = int(profile_proof_metrics.get("rows", 0) or 0)
    profile_proof_real_ready = int(profile_proof_metrics.get("realProofReadyRows", 0) or 0)
    external_profile_proof_blockers = max(0, profile_proof_rows - profile_proof_real_ready)
    metrics = {
        "rows": len(rows),
        "readyAreas": ready,
        "actionableAreas": actionable,
        "blockedAreas": blocked,
        "holdAreas": hold,
        "masterStageIndex": int(bundle["master"].get("stageIndex", 0) or 0),
        "profileConfigured": int(master_metrics.get("profileConfigured", 0) or 0),
        "expectedProfiles": max(1, int(master_metrics.get("expectedProfiles", 1) or 1)),
        "profileProofRows": profile_proof_rows,
        "profileProofRealReadyRows": profile_proof_real_ready,
        "externalProfileProofBlockers": external_profile_proof_blockers,
        "currentTrueBlockers": 1 if str(bundle["master"].get("stage", "")) == "profile_setup" and external_profile_proof_blockers else 0,
        "firstBatchPublished": int(master_metrics.get("firstBatchPublished", 0) or 0),
        "minimumKpiRows": int(master_metrics.get("firstBatchMinimumKpiRows", 0) or 0),
        "leadReadyRoutes": int(master_metrics.get("leadReadyRoutes", 0) or 0),
    }
    issues: list[str] = []
    if metrics["rows"] != 11:
        issues.append(f"expected 11 launch ops dashboard rows, got {metrics['rows']}")
    if not bundle["master"] or not bundle["command"] or not bundle["handoff"]:
        issues.append("launch ops dashboard missing core source packet")
    if metrics["profileConfigured"] == 0 and rows[0]["status"] != "profile_setup":
        issues.append("dashboard should show master stage profile_setup while no profiles are configured")
    profile_row = next((row for row in rows if row["area"] == "profile_setup"), {})
    if metrics["profileConfigured"] < metrics["expectedProfiles"] and profile_row.get("status") != "actionable":
        issues.append("profile setup should be actionable while public profile links are ready but not configured")
    if metrics["profileConfigured"] < metrics["expectedProfiles"] and metrics["actionableAreas"] < 2:
        issues.append("dashboard should expose actionable profile setup and next actions before external profile proof")
    if metrics["profileConfigured"] < metrics["expectedProfiles"] and metrics["externalProfileProofBlockers"] == 0:
        issues.append("dashboard should show external profile proof blockers before profile setup completes")
    if metrics["minimumKpiRows"] == 0 and any(row["area"] == "weekly_review" and row["status"] == "ready" for row in rows):
        issues.append("weekly review cannot be ready without minimum KPI rows")
    if metrics["profileConfigured"] < metrics["expectedProfiles"] and any(row["area"] == "next_actions" and row["status"] == "ready" for row in rows):
        issues.append("next actions cannot be fully ready before profile setup completes")
    return {
        "generatedAt": today(),
        "sources": {
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
            "launchCommandCenter": str(COMMAND_CENTER.relative_to(ROOT)),
            "nextActions": str(NEXT_ACTIONS.relative_to(ROOT)),
            "operatorHandoff": str(OPERATOR_HANDOFF.relative_to(ROOT)),
            "profileReadiness": str(PROFILE_READINESS.relative_to(ROOT)),
            "profileProofReadiness": str(PROFILE_PROOF_READINESS.relative_to(ROOT)),
            "publishAction": str(PUBLISH_ACTION.relative_to(ROOT)),
            "kpiAction": str(KPI_ACTION.relative_to(ROOT)),
            "leadOps": str(LEAD_OPS.relative_to(ROOT)),
            "weeklyAction": str(WEEKLY_ACTION.relative_to(ROOT)),
            "profilePublishHandoff": str(PROFILE_HANDOFF.relative_to(ROOT)),
            "publishKpiHandoff": str(PUBLISH_KPI_HANDOFF.relative_to(ROOT)),
            "weeklyLeadOfferHandoff": str(WEEKLY_LEAD_OFFER_HANDOFF.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Use this dashboard for orientation only; individual gates remain authoritative.",
            "Do not skip profile setup, public post URL verification, or KPI proof notes.",
            "Empty data mode keeps commerce and winning-content decisions closed.",
            "Only externally verified platform/profile/post/lead evidence can move a blocked area forward.",
        ],
        "issues": issues,
    }


def render_markdown(dashboard: dict) -> str:
    metrics = dashboard["metrics"]
    lines = [
        "# LoveTypes Launch Ops Dashboard",
        "",
        f"- 產生日期：{dashboard['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready areas：{metrics['readyAreas']}",
        f"- actionable areas：{metrics['actionableAreas']}",
        f"- blocked areas：{metrics['blockedAreas']}",
        f"- hold areas：{metrics['holdAreas']}",
        f"- profile configured：{metrics['profileConfigured']} / 3",
        f"- real profile proof ready：{metrics['profileProofRealReadyRows']} / {metrics['profileProofRows']}",
        f"- external profile proof blockers：{metrics['externalProfileProofBlockers']}",
        f"- current true blockers：{metrics['currentTrueBlockers']}",
        f"- first batch published：{metrics['firstBatchPublished']} / 3",
        f"- minimum KPI rows：{metrics['minimumKpiRows']}",
        f"- lead ready routes：{metrics['leadReadyRoutes']}",
        f"- issues：{len(dashboard['issues'])}",
        "",
        "## Rule",
        "",
    ]
    lines.extend(f"- {rule}" for rule in dashboard["rules"])
    lines.extend(["", "## Areas", ""])
    for row in dashboard["rows"]:
        lines.extend([
            f"### {row['area']}",
            "",
            f"- status：`{row['status']}`",
            f"- ready / blocked：{row['ready']} / {row['blocked']}",
            f"- next：{row['next_action']}",
            f"- evidence：{row['evidence']}",
            f"- safety：{row['safety']}",
            "",
        ])
    if dashboard["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in dashboard["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(dashboard: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(dashboard), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["area", "status", "ready", "blocked", "next_action", "evidence", "safety"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(dashboard["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a single-page LoveTypes launch operations dashboard.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    dashboard = build_dashboard()
    metrics = dashboard["metrics"]
    if not args.check:
        write_outputs(dashboard)
        print(f"promotion_launch_ops_dashboard={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_launch_ops_dashboard_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_launch_ops_dashboard_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_launch_ops_dashboard_rows={metrics['rows']}")
    print(f"promotion_launch_ops_dashboard_ready_areas={metrics['readyAreas']}")
    print(f"promotion_launch_ops_dashboard_actionable_areas={metrics['actionableAreas']}")
    print(f"promotion_launch_ops_dashboard_blocked_areas={metrics['blockedAreas']}")
    print(f"promotion_launch_ops_dashboard_hold_areas={metrics['holdAreas']}")
    print(f"promotion_launch_ops_dashboard_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_launch_ops_dashboard_profile_proof_real_ready={metrics['profileProofRealReadyRows']}")
    print(f"promotion_launch_ops_dashboard_external_profile_proof_blockers={metrics['externalProfileProofBlockers']}")
    print(f"promotion_launch_ops_dashboard_current_true_blockers={metrics['currentTrueBlockers']}")
    print(f"promotion_launch_ops_dashboard_first_batch_published={metrics['firstBatchPublished']}")
    print(f"promotion_launch_ops_dashboard_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_launch_ops_dashboard_lead_ready_routes={metrics['leadReadyRoutes']}")
    print(f"promotion_launch_ops_dashboard_issues={len(dashboard['issues'])}")
    for issue in dashboard["issues"]:
        print(issue)
    return 1 if dashboard["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
