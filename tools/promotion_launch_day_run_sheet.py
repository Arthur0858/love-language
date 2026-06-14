#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LAUNCH_DASHBOARD = PROMOTION_DIR / "launch-ops-dashboard.json"
REHEARSAL = PROMOTION_DIR / "launch-rehearsal-packet.json"
HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
PROFILE_PROOF = PROMOTION_DIR / "profile-proof-readiness-pack.json"
PUBLISH_READINESS = PROMOTION_DIR / "first-batch-publish-readiness-pack.json"
POST_OPS = PROMOTION_DIR / "post-ops-readiness-pack.json"
MASTER = PROMOTION_DIR / "master-gate.json"
OUTPUT_MD = PROMOTION_DIR / "launch-day-run-sheet.md"
OUTPUT_JSON = PROMOTION_DIR / "launch-day-run-sheet.json"
OUTPUT_CSV = PROMOTION_DIR / "launch-day-run-sheet.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def stage_rows(rehearsal: dict, stage_name: str) -> list[dict]:
    return [row for row in rehearsal.get("stages", []) if row.get("stage") == stage_name]


def proof_rows(pack: dict) -> list[dict]:
    return [row for row in pack.get("rows", []) if isinstance(row, dict)]


def build_run_sheet() -> dict:
    dashboard = load_json(LAUNCH_DASHBOARD)
    rehearsal = load_json(REHEARSAL)
    handoff = load_json(HANDOFF)
    profile = load_json(PROFILE_PROOF)
    publish = load_json(PUBLISH_READINESS)
    post_ops = load_json(POST_OPS)
    master = load_json(MASTER)

    profile_rows = proof_rows(profile)
    publish_rows = proof_rows(publish)
    post_rows = proof_rows(post_ops)
    rows: list[dict[str, str]] = []

    for item in profile_rows:
        rows.append({
            "order": str(len(rows) + 1),
            "phase": "profile_setup",
            "platform": str(item.get("platform", "")),
            "task": f"profile-{item.get('platform', '')}",
            "status": str(item.get("operator_status", "")),
            "action": "Set the platform profile link, then verify the structured proof text before writeback.",
            "check_command": str(item.get("check_command", "")),
            "write_command": str(item.get("write_command", "")),
            "success_signal": "profile proof import validates and platform tracker row can be set/live with real proof.",
            "stop_condition": str(item.get("evidence_required", "")),
        })

    rows.append({
        "order": str(len(rows) + 1),
        "phase": "readiness_gate",
        "platform": "all",
        "task": "launch-readiness",
        "status": "blocked" if master.get("stage") == "profile_setup" else "ready",
        "action": "Refresh profile completion, launch readiness and dashboard before publishing.",
        "check_command": "python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_launch_readiness_gate.py --check && python3 tools/promotion_launch_ops_dashboard.py --check",
        "write_command": "",
        "success_signal": "promotion_launch_readiness_ready_to_publish=1 and profile_configured=3.",
        "stop_condition": "Stop before publishing while profile_configured is less than 3.",
    })

    for item in publish_rows:
        rows.append({
            "order": str(len(rows) + 1),
            "phase": "publish_first_batch",
            "platform": str(item.get("platform", "")),
            "task": str(item.get("task_id", "")),
            "status": str(item.get("operator_status", "")),
            "action": "Publish the first Iris post only after profile gate is ready; keep quiz CTA unchanged.",
            "check_command": "python3 tools/promotion_first_batch_publish_readiness_pack.py --check",
            "write_command": "",
            "success_signal": "A real public post URL exists and replaces the placeholder in the post proof file.",
            "stop_condition": str(item.get("stop_condition", "")),
        })

    for item in post_rows:
        platform = str(item.get("platform", ""))
        task_id = str(item.get("task_id", ""))
        rows.append({
            "order": str(len(rows) + 1),
            "phase": "post_url_and_kpi",
            "platform": platform,
            "task": task_id,
            "status": str(item.get("status", "")),
            "action": str(item.get("next_action", "")),
            "check_command": f"python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-{platform}-{task_id}.txt",
            "write_command": str(item.get("kpi_command", "")),
            "success_signal": "post URL, site_clicks, quiz_starts and quiz_completions are backed by checked evidence.",
            "stop_condition": "Do not run writeback with placeholder URLs or guessed KPI values.",
        })

    rows.append({
        "order": str(len(rows) + 1),
        "phase": "weekly_review",
        "platform": "all",
        "task": "weekly-review",
        "status": "blocked_until_minimum_kpi",
        "action": "Run weekly review only after all first-batch post URL and KPI evidence passes.",
        "check_command": "python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_weekly_decision_evidence_checklist.py --check",
        "write_command": "",
        "success_signal": "weekly_review_ready=1 and empty_data=0 before changing content or commerce paths.",
        "stop_condition": "Stop all offer/Luna/affiliate prioritization while empty_data=1.",
    })

    metrics = {
        "rows": len(rows),
        "profileRows": sum(1 for row in rows if row["phase"] == "profile_setup"),
        "publishRows": sum(1 for row in rows if row["phase"] == "publish_first_batch"),
        "postOpsRows": sum(1 for row in rows if row["phase"] == "post_url_and_kpi"),
        "operatorActionRows": sum(1 for row in rows if row["status"] == "ready_to_configure"),
        "safeWritebackRows": sum(1 for row in rows if row["status"] in {"ready", "ready_to_writeback", "ready_to_publish"}),
        "readyRows": sum(1 for row in rows if row["status"] in {"ready", "ready_to_writeback", "ready_to_publish"}),
        "blockedRows": sum(1 for row in rows if row["status"].startswith("blocked")),
        "profileProofRows": int(profile.get("metrics", {}).get("rows", 0) or 0),
        "profileProofRealReadyRows": int(profile.get("metrics", {}).get("realProofReadyRows", 0) or 0),
        "profileProofPlaceholderRows": int(profile.get("metrics", {}).get("placeholderProofRows", 0) or 0),
        "externalProfileProofBlockers": max(
            0,
            int(profile.get("metrics", {}).get("rows", 0) or 0)
            - int(profile.get("metrics", {}).get("realProofReadyRows", 0) or 0),
        ),
        "masterStageIndex": int(master.get("stageIndex", 0) or 0),
        "dashboardBlockedAreas": int(dashboard.get("metrics", {}).get("blockedAreas", 0) or 0),
        "rehearsalReadyStages": int(rehearsal.get("readyStages", 0) or 0),
        "rehearsalProfileReadyStages": int(rehearsal.get("profileReadyStages", 0) or 0),
        "rehearsalPublishReadyStages": int(rehearsal.get("publishReadyStages", 0) or 0),
        "rehearsalKpiReadyStages": int(rehearsal.get("kpiReadyStages", 0) or 0),
        "rehearsalWeeklyReadyStages": int(rehearsal.get("weeklyReadyStages", 0) or 0),
        "handoffReadySteps": int(handoff.get("readyCount", 0) or 0),
        "profileConfigured": int(master.get("metrics", {}).get("profileConfigured", 0) or 0) if isinstance(master.get("metrics"), dict) else 0,
        "expectedProfiles": max(1, int(master.get("metrics", {}).get("expectedProfiles", 1) or 1)) if isinstance(master.get("metrics"), dict) else 1,
    }
    issues: list[str] = []
    if metrics["profileRows"] < 1:
        issues.append("expected at least 1 profile setup row")
    if metrics["publishRows"] < 1:
        issues.append("expected at least 1 publish row")
    if metrics["postOpsRows"] < 1:
        issues.append("expected at least 1 post ops row")
    expected_rows = metrics["profileRows"] + metrics["publishRows"] + metrics["postOpsRows"] + 2
    if metrics["rows"] != expected_rows:
        issues.append(f"expected {expected_rows} launch day rows, got {metrics['rows']}")
    if master.get("stage") == "profile_setup" and not any(row["phase"] == "readiness_gate" and row["status"] == "blocked" for row in rows):
        issues.append("readiness gate should stay blocked while master stage is profile_setup")
    if metrics["profileConfigured"] < metrics["expectedProfiles"] and metrics["externalProfileProofBlockers"] and metrics["readyRows"]:
        issues.append("safe ready rows should stay zero while external profile proof blockers exist")
    for row in rows:
        if not row["action"] or not row["success_signal"] or not row["stop_condition"]:
            issues.append(f"{row['phase']}/{row['platform']}/{row['task']}: missing action, success signal, or stop condition")
    return {
        "generatedAt": today(),
        "sources": {
            "launchOpsDashboard": str(LAUNCH_DASHBOARD.relative_to(ROOT)),
            "launchRehearsalPacket": str(REHEARSAL.relative_to(ROOT)),
            "operatorHandoffPacket": str(HANDOFF.relative_to(ROOT)),
            "profileProofReadinessPack": str(PROFILE_PROOF.relative_to(ROOT)),
            "firstBatchPublishReadinessPack": str(PUBLISH_READINESS.relative_to(ROOT)),
            "postOpsReadinessPack": str(POST_OPS.relative_to(ROOT)),
            "masterGate": str(MASTER.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Execute rows in order; later rows do not override earlier blocked gates.",
            "Check commands are safe to run; write commands require real external proof.",
            "Profile setup must complete for all active platforms before first-batch publishing.",
            "Post URL and KPI evidence must complete before weekly review or commerce decisions.",
        ],
        "issues": issues,
    }


def render_markdown(sheet: dict) -> str:
    metrics = sheet["metrics"]
    lines = [
        "# LoveTypes Launch Day Run Sheet",
        "",
        f"- 產生日期：{sheet['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- profile rows：{metrics['profileRows']}",
        f"- publish rows：{metrics['publishRows']}",
        f"- post ops rows：{metrics['postOpsRows']}",
        f"- operator action rows：{metrics['operatorActionRows']}",
        f"- safe writeback rows：{metrics['safeWritebackRows']}",
        f"- ready rows：{metrics['readyRows']}",
        f"- blocked rows：{metrics['blockedRows']}",
        f"- real profile proof ready：{metrics['profileProofRealReadyRows']} / {metrics['profileProofRows']}",
        f"- placeholder proof rows：{metrics['profileProofPlaceholderRows']}",
        f"- external profile proof blockers：{metrics['externalProfileProofBlockers']}",
        f"- issues：{len(sheet['issues'])}",
        "",
        "## Rule",
        "",
    ]
    lines.extend(f"- {rule}" for rule in sheet["rules"])
    lines.extend(["", "## Run Order", ""])
    for row in sheet["rows"]:
        lines.extend([
            f"### {row['order']}. {row['phase']} · {row['platform']} · `{row['task']}`",
            "",
            f"- status：`{row['status']}`",
            f"- action：{row['action']}",
            f"- check：`{row['check_command']}`" if row["check_command"] else "- check：",
            f"- write：`{row['write_command']}`" if row["write_command"] else "- write：",
            f"- success：{row['success_signal']}",
            f"- stop：{row['stop_condition']}",
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
    fieldnames = ["order", "phase", "platform", "task", "status", "action", "check_command", "write_command", "success_signal", "stop_condition"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in sheet["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a launch-day run sheet for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    sheet = build_run_sheet()
    metrics = sheet["metrics"]
    if not args.check:
        write_outputs(sheet)
        print(f"promotion_launch_day_run_sheet={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_launch_day_run_sheet_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_launch_day_run_sheet_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_launch_day_run_rows={metrics['rows']}")
    print(f"promotion_launch_day_run_profile_rows={metrics['profileRows']}")
    print(f"promotion_launch_day_run_publish_rows={metrics['publishRows']}")
    print(f"promotion_launch_day_run_post_ops_rows={metrics['postOpsRows']}")
    print(f"promotion_launch_day_run_operator_action_rows={metrics['operatorActionRows']}")
    print(f"promotion_launch_day_run_safe_writeback_rows={metrics['safeWritebackRows']}")
    print(f"promotion_launch_day_run_ready_rows={metrics['readyRows']}")
    print(f"promotion_launch_day_run_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_launch_day_run_profile_proof_real_ready={metrics['profileProofRealReadyRows']}")
    print(f"promotion_launch_day_run_profile_proof_placeholder_rows={metrics['profileProofPlaceholderRows']}")
    print(f"promotion_launch_day_run_external_profile_proof_blockers={metrics['externalProfileProofBlockers']}")
    print(f"promotion_launch_day_run_dashboard_blocked_areas={metrics['dashboardBlockedAreas']}")
    print(f"promotion_launch_day_run_rehearsal_profile_ready_stages={metrics['rehearsalProfileReadyStages']}")
    print(f"promotion_launch_day_run_rehearsal_publish_ready_stages={metrics['rehearsalPublishReadyStages']}")
    print(f"promotion_launch_day_run_rehearsal_kpi_ready_stages={metrics['rehearsalKpiReadyStages']}")
    print(f"promotion_launch_day_run_rehearsal_weekly_ready_stages={metrics['rehearsalWeeklyReadyStages']}")
    print(f"promotion_launch_day_run_issues={len(sheet['issues'])}")
    for issue in sheet["issues"]:
        print(issue)
    return 1 if sheet["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
