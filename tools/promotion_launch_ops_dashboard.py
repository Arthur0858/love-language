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
PUBLISH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
KPI_ACTION = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
LEAD_OPS = PROMOTION_DIR / "lead-ops-action-sheet.json"
WEEKLY_ACTION = PROMOTION_DIR / "weekly-review-action-sheet.json"
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


def build_rows(bundle: dict[str, dict]) -> list[dict[str, str]]:
    master = bundle["master"]
    command = bundle["command"]
    next_actions = bundle["next"]
    handoff = bundle["handoff"]
    profile = bundle["profile"]
    publish = bundle["publish"]
    kpi = bundle["kpi"]
    lead = bundle["lead"]
    weekly = bundle["weekly"]
    master_metrics = master.get("metrics", {}) if isinstance(master.get("metrics"), dict) else {}
    handoff_state = handoff.get("state", {}) if isinstance(handoff.get("state"), dict) else {}
    rows = [
        {
            "area": "master_gate",
            "status": str(master.get("stage", "unknown")),
            "ready": str(master_metrics.get("commandReadyRows", 0)),
            "blocked": str(master_metrics.get("commandBlockedRows", 0)),
            "next_action": str(master.get("nextAction", "Follow current stage gate.")),
            "evidence": f"profile={master_metrics.get('profileConfigured', 0)}/3, first_batch={master_metrics.get('firstBatchPublished', 0)}/3, kpi_rows={master_metrics.get('firstBatchMinimumKpiRows', 0)}",
            "safety": "Use master gate as final stage source; do not skip profile_setup.",
        },
        {
            "area": "profile_setup",
            "status": "blocked" if metric(profile, "profileGateReady") == 0 else "ready",
            "ready": str(metric(profile, "readyToConfigure")),
            "blocked": str(3 - metric(profile, "configured")),
            "next_action": "Set three platform profile links and write back proof.",
            "evidence": f"public_ready={metric(profile, 'publicReady')}, configured={metric(profile, 'configured')}, ready_to_writeback={metric(profile, 'readyToWriteback')}",
            "safety": "Do not mark set/live without platform evidence.",
        },
        {
            "area": "first_batch_publish",
            "status": status_from_counts(metric(publish, "ready"), metric(publish, "blocked")),
            "ready": str(metric(publish, "ready")),
            "blocked": str(metric(publish, "blocked")),
            "next_action": "Publish first three posts only after profile gate is ready.",
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
            "area": "next_actions",
            "status": "ready" if int(next_actions.get("actions", [{}]) and len(next_actions.get("actions", [])) or 0) else "waiting",
            "ready": str(command.get("readyRows", 0)),
            "blocked": str(command.get("blockedRows", 0)),
            "next_action": "Do the current ready actions in order: profile setup, asset readiness, then publish.",
            "evidence": f"selected_tasks={len(next_actions.get('selectedTasks', []))}, command_rows={command.get('rowCount', 0)}",
            "safety": "Ready actions do not authorize downstream commerce decisions.",
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
        "publish": load_json(PUBLISH_ACTION),
        "kpi": load_json(KPI_ACTION),
        "lead": load_json(LEAD_OPS),
        "weekly": load_json(WEEKLY_ACTION),
    }
    rows = build_rows(bundle)
    blocked = sum(1 for row in rows if row["status"] == "blocked")
    hold = sum(1 for row in rows if row["status"] == "hold")
    ready = sum(1 for row in rows if row["status"] == "ready")
    master_metrics = bundle["master"].get("metrics", {}) if isinstance(bundle["master"].get("metrics"), dict) else {}
    metrics = {
        "rows": len(rows),
        "readyAreas": ready,
        "blockedAreas": blocked,
        "holdAreas": hold,
        "masterStageIndex": int(bundle["master"].get("stageIndex", 0) or 0),
        "profileConfigured": int(master_metrics.get("profileConfigured", 0) or 0),
        "firstBatchPublished": int(master_metrics.get("firstBatchPublished", 0) or 0),
        "minimumKpiRows": int(master_metrics.get("firstBatchMinimumKpiRows", 0) or 0),
        "leadReadyRoutes": int(master_metrics.get("leadReadyRoutes", 0) or 0),
    }
    issues: list[str] = []
    if metrics["rows"] != 8:
        issues.append(f"expected 8 launch ops dashboard rows, got {metrics['rows']}")
    if not bundle["master"] or not bundle["command"] or not bundle["handoff"]:
        issues.append("launch ops dashboard missing core source packet")
    if metrics["profileConfigured"] == 0 and rows[0]["status"] != "profile_setup":
        issues.append("dashboard should show master stage profile_setup while no profiles are configured")
    if metrics["minimumKpiRows"] == 0 and any(row["area"] == "weekly_review" and row["status"] == "ready" for row in rows):
        issues.append("weekly review cannot be ready without minimum KPI rows")
    return {
        "generatedAt": today(),
        "sources": {
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
            "launchCommandCenter": str(COMMAND_CENTER.relative_to(ROOT)),
            "nextActions": str(NEXT_ACTIONS.relative_to(ROOT)),
            "operatorHandoff": str(OPERATOR_HANDOFF.relative_to(ROOT)),
            "profileReadiness": str(PROFILE_READINESS.relative_to(ROOT)),
            "publishAction": str(PUBLISH_ACTION.relative_to(ROOT)),
            "kpiAction": str(KPI_ACTION.relative_to(ROOT)),
            "leadOps": str(LEAD_OPS.relative_to(ROOT)),
            "weeklyAction": str(WEEKLY_ACTION.relative_to(ROOT)),
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
        f"- blocked areas：{metrics['blockedAreas']}",
        f"- hold areas：{metrics['holdAreas']}",
        f"- profile configured：{metrics['profileConfigured']} / 3",
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
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
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
    print(f"promotion_launch_ops_dashboard_blocked_areas={metrics['blockedAreas']}")
    print(f"promotion_launch_ops_dashboard_hold_areas={metrics['holdAreas']}")
    print(f"promotion_launch_ops_dashboard_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_launch_ops_dashboard_first_batch_published={metrics['firstBatchPublished']}")
    print(f"promotion_launch_ops_dashboard_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_launch_ops_dashboard_lead_ready_routes={metrics['leadReadyRoutes']}")
    print(f"promotion_launch_ops_dashboard_issues={len(dashboard['issues'])}")
    for issue in dashboard["issues"]:
        print(issue)
    return 1 if dashboard["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
