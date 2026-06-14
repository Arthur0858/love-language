#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import promotion_post_writeback as post_writeback


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LAUNCH_READINESS = PROMOTION_DIR / "launch-readiness-gate.json"
COMMAND_CENTER = PROMOTION_DIR / "launch-command-center.json"
PROFILE_COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
BLOCKER_CHECKLIST = PROMOTION_DIR / "blocker-resolution-checklist.json"
KPI_HEALTH = PROMOTION_DIR / "kpi-attribution-health-report.json"
OUTPUT_MD = PROMOTION_DIR / "launch-blocker-digest.md"
OUTPUT_JSON = PROMOTION_DIR / "launch-blocker-digest.json"


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def as_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def current_stage(launch: dict, weekly: dict) -> str:
    readiness = launch.get("readiness", {}) if isinstance(launch.get("readiness"), dict) else {}
    weekly_state = weekly.get("state", {}) if isinstance(weekly.get("state"), dict) else {}
    metrics = launch.get("metrics", {}) if isinstance(launch.get("metrics"), dict) else {}
    if as_int(metrics.get("profileConfigured")) < as_int(metrics.get("profileRows")):
        return "profile_setup"
    if as_int(metrics.get("publishedRows")) < as_int(metrics.get("firstBatchRows")):
        return "first_batch_publish"
    if as_int(metrics.get("filledKpiRows")) < as_int(metrics.get("firstBatchRows")):
        return "kpi_backfill"
    if not weekly_state.get("readyForWeeklyDecision"):
        return "weekly_evidence"
    if readiness.get("readyForKpiDecision"):
        return "weekly_decision"
    return "launch_monitoring"


def next_action_for(stage: str) -> dict[str, str]:
    actions = {
        "profile_setup": {
            "action": "Set the three external platform profile links, capture real proof, then import profile proof text.",
            "command": "python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-<platform>.txt --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\"",
            "release": "promotion_launch_readiness_profile_configured=3 and ready_to_publish=1",
        },
        "first_batch_publish": {
            "action": "Publish the first three platform posts and write back real public post URLs.",
            "command": f"python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-<platform>-<task>.txt --proof-note \"{post_writeback.POST_PROOF_NOTE_PLACEHOLDER}\"",
            "release": "first-batch post_url values exist for YouTube Shorts, TikTok, and Instagram Reels",
        },
        "kpi_backfill": {
            "action": "Backfill source-checked site_clicks, quiz_starts, and quiz_completions for the first batch.",
            "command": "python3 tools/promotion_post_text_import.py add --input <post-proof.txt> --proof-note \"public URL and KPI source checked YYYY-MM-DD\"",
            "release": "filled KPI rows cover the first batch or source-checked zeros are recorded",
        },
        "weekly_evidence": {
            "action": "Refresh weekly evidence and keep revenue decisions closed until the review packet is ready.",
            "command": "python3 tools/promotion_weekly_summary.py && python3 tools/promotion_week_decision_gate.py && python3 tools/promotion_weekly_review_packet.py",
            "release": "weekly review ready=1 and empty_data_mode=0",
        },
        "weekly_decision": {
            "action": "Run the weekly review and decide whether to keep, adjust, or test one soft offer.",
            "command": "python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_decision_readiness_checklist.py --check",
            "release": "decision evidence is complete and commerce changes remain safety-checked",
        },
        "launch_monitoring": {
            "action": "Continue weekly monitoring without changing offer order unless evidence supports it.",
            "command": "python3 tools/promotion_daily_ops_refresh.py && python3 tools/site_health_summary.py --skip-public",
            "release": "weekly summary remains current and issues stay at 0",
        },
    }
    return actions.get(stage, actions["launch_monitoring"])


def build_digest() -> dict:
    launch = read_json(LAUNCH_READINESS)
    command = read_json(COMMAND_CENTER)
    profile = read_json(PROFILE_COMPLETION)
    weekly = read_json(WEEKLY_REVIEW)
    checklist = read_json(BLOCKER_CHECKLIST)
    kpi = read_json(KPI_HEALTH)

    launch_metrics = launch.get("metrics", {}) if isinstance(launch.get("metrics"), dict) else {}
    readiness = launch.get("readiness", {}) if isinstance(launch.get("readiness"), dict) else {}
    command_counts = command.get("phaseCounts", {}) if isinstance(command.get("phaseCounts"), dict) else {}
    weekly_state = weekly.get("state", {}) if isinstance(weekly.get("state"), dict) else {}
    checklist_metrics = checklist.get("metrics", {}) if isinstance(checklist.get("metrics"), dict) else {}
    kpi_writeback = kpi.get("writebackMetrics", {}) if isinstance(kpi.get("writebackMetrics"), dict) else {}
    kpi_attr = kpi.get("attributionMetrics", {}) if isinstance(kpi.get("attributionMetrics"), dict) else {}

    stage = current_stage(launch, weekly)
    next_action = next_action_for(stage)
    blockers = launch.get("blockers", []) if isinstance(launch.get("blockers"), list) else []
    first_blocker = blockers[0] if blockers else {}
    profile_blockers = profile.get("blockers", []) if isinstance(profile.get("blockers"), list) else []

    metrics = {
        "profileConfigured": as_int(launch_metrics.get("profileConfigured")),
        "profileRows": as_int(launch_metrics.get("profileRows")),
        "publishedRows": as_int(launch_metrics.get("publishedRows")),
        "firstBatchRows": as_int(launch_metrics.get("firstBatchRows")),
        "filledKpiRows": as_int(launch_metrics.get("filledKpiRows")),
        "blockers": as_int(launch_metrics.get("blockers")),
        "checklistActiveBlockers": as_int(checklist_metrics.get("activeBlockers")),
        "checklistReadyNow": as_int(checklist_metrics.get("readyNow")),
        "commandReady": as_int(command.get("readyRows")),
        "commandPrepared": as_int(command.get("preparedRows")),
        "commandBlocked": as_int(command.get("blockedRows")),
        "profileCompletionBlockers": len(profile_blockers),
        "weeklyReady": int(bool(weekly_state.get("readyForWeeklyDecision"))),
        "emptyDataMode": int(bool(readiness.get("emptyDataMode") or weekly_state.get("emptyDataMode"))),
        "kpiPostingRows": as_int(kpi_writeback.get("postingRows")),
        "kpiPlatformRows": as_int(kpi_writeback.get("platformRows")),
        "kpiScriptRows": as_int(kpi_writeback.get("scriptRows")),
        "attributionRows": as_int(kpi_attr.get("rows")),
    }

    issues: list[str] = []
    if metrics["profileRows"] != 3 or metrics["firstBatchRows"] != 3:
        issues.append("launch digest expects exactly three profile rows and three first-batch rows")
    if metrics["blockers"] != len(blockers):
        issues.append("launch readiness blocker count does not match blocker rows")
    if metrics["checklistActiveBlockers"] < metrics["blockers"]:
        issues.append("blocker checklist should not have fewer active blockers than launch readiness")
    if metrics["emptyDataMode"] == 0 and metrics["filledKpiRows"] == 0:
        issues.append("empty data mode should stay on until KPI evidence exists")
    if stage == "profile_setup" and metrics["checklistReadyNow"] < 3:
        issues.append("profile setup stage should expose three ready-now profile actions")
    if kpi.get("issues"):
        issues.append("KPI attribution health report has issues")
    if launch.get("issues"):
        issues.append("launch readiness gate has structural issues")
    if weekly.get("issues"):
        issues.append("weekly review packet has issues")

    return {
        "generatedAt": today(),
        "sources": {
            "launchReadiness": str(LAUNCH_READINESS.relative_to(ROOT)),
            "commandCenter": str(COMMAND_CENTER.relative_to(ROOT)),
            "profileCompletion": str(PROFILE_COMPLETION.relative_to(ROOT)),
            "weeklyReview": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "blockerChecklist": str(BLOCKER_CHECKLIST.relative_to(ROOT)),
            "kpiHealth": str(KPI_HEALTH.relative_to(ROOT)),
        },
        "stage": stage,
        "firstBlocker": {
            "id": str(first_blocker.get("id", "")),
            "phase": str(first_blocker.get("phase", "")),
            "severity": str(first_blocker.get("severity", "")),
            "message": str(first_blocker.get("message", "")),
        },
        "nextAction": next_action,
        "allowedNow": [
            "Set or verify external platform profile links.",
            "Capture real proof notes and import only source-checked profile proof.",
            "Refresh daily ops packets after any writeback.",
        ] if stage == "profile_setup" else [
            next_action["action"],
            "Refresh daily ops packets after any writeback.",
        ],
        "doNotDo": [
            "Do not publish first-batch posts before all profile rows are set/live.",
            "Do not mark posts published without real public post URLs.",
            "Do not fill KPI values from guesses or placeholders.",
            "Do not change Luna, affiliate, paid offer, or guardian winner decisions while empty_data_mode=1.",
        ],
        "metrics": metrics,
        "commandPhaseCounts": command_counts,
        "issues": issues,
    }


def render_markdown(digest: dict) -> str:
    metrics = digest["metrics"]
    blocker = digest["firstBlocker"]
    lines = [
        "# LoveTypes Launch Blocker Digest",
        "",
        f"- 產生日期：{digest['generatedAt']}",
        f"- current stage：`{digest['stage']}`",
        f"- first blocker：`{blocker['id'] or 'none'}`",
        f"- profile configured：{metrics['profileConfigured']} / {metrics['profileRows']}",
        f"- first batch published：{metrics['publishedRows']} / {metrics['firstBatchRows']}",
        f"- filled KPI rows：{metrics['filledKpiRows']}",
        f"- active blockers：{metrics['checklistActiveBlockers']}",
        f"- ready now：{metrics['checklistReadyNow']}",
        f"- empty data mode：{metrics['emptyDataMode']}",
        f"- issues：{len(digest['issues'])}",
        "",
        "## Next Action",
        "",
        f"- action：{digest['nextAction']['action']}",
        f"- command：`{digest['nextAction']['command']}`",
        f"- release：{digest['nextAction']['release']}",
        "",
        "## First Blocker",
        "",
        f"- phase：`{blocker['phase']}`",
        f"- severity：`{blocker['severity']}`",
        f"- message：{blocker['message'] or 'None.'}",
        "",
        "## Allowed Now",
        "",
    ]
    lines.extend(f"- {item}" for item in digest["allowedNow"])
    lines.extend(["", "## Do Not Do", ""])
    lines.extend(f"- {item}" for item in digest["doNotDo"])
    lines.extend([
        "",
        "## Evidence Snapshot",
        "",
        f"- command ready / prepared / blocked：{metrics['commandReady']} / {metrics['commandPrepared']} / {metrics['commandBlocked']}",
        f"- profile completion blockers：{metrics['profileCompletionBlockers']}",
        f"- weekly ready：{metrics['weeklyReady']}",
        f"- KPI posting / platform / script rows：{metrics['kpiPostingRows']} / {metrics['kpiPlatformRows']} / {metrics['kpiScriptRows']}",
        f"- attribution rows：{metrics['attributionRows']}",
        "",
    ])
    if digest["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in digest["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(digest: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(digest), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(digest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a concise current-stage blocker digest for LoveTypes launch operations.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    args = parser.parse_args()
    digest = build_digest()
    if not args.check:
        write_outputs(digest)
        print(f"promotion_launch_blocker_digest={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_launch_blocker_digest_json={OUTPUT_JSON.relative_to(ROOT)}")
    metrics = digest["metrics"]
    print(f"promotion_launch_blocker_digest_stage={digest['stage']}")
    print(f"promotion_launch_blocker_digest_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_launch_blocker_digest_first_batch_published={metrics['publishedRows']}")
    print(f"promotion_launch_blocker_digest_filled_kpi_rows={metrics['filledKpiRows']}")
    print(f"promotion_launch_blocker_digest_active_blockers={metrics['checklistActiveBlockers']}")
    print(f"promotion_launch_blocker_digest_ready_now={metrics['checklistReadyNow']}")
    print(f"promotion_launch_blocker_digest_empty_data_mode={metrics['emptyDataMode']}")
    print(f"promotion_launch_blocker_digest_issues={len(digest['issues'])}")
    for issue in digest["issues"]:
        print(issue)
    return 1 if digest["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
