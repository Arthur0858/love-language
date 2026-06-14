#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
LAUNCH_QUICKSTART = PROMOTION_DIR / "launch-quickstart.json"
LAUNCH_CLIPBOARD = PROMOTION_DIR / "launch-clipboard.json"
LAUNCH_DAY = PROMOTION_DIR / "launch-day-run-sheet.json"
EXCEPTION_RUNBOOK = PROMOTION_DIR / "launch-exception-runbook.json"
PROOF_TEMPLATES = PROMOTION_DIR / "operation-proof-templates.json"
PROOF_REHEARSAL = PROMOTION_DIR / "proof-rehearsal.json"
HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
BLOCKERS = PROMOTION_DIR / "blocker-resolution-checklist.json"
PROFILE_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
PUBLISH_KPI_HANDOFF = PROMOTION_DIR / "publish-kpi-handoff.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "launch-execution-closure-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "launch-execution-closure-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "launch-execution-closure-quickstart.txt"
EXPECTED_PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def metric(payload: dict, key: str) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return 0
    try:
        return int(values.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def rows(payload: dict, key: str = "rows") -> list[dict]:
    value = payload.get(key, [])
    return value if isinstance(value, list) else []


def ready_profile_blocks(clipboard: dict) -> list[dict]:
    return [
        row for row in rows(clipboard, "blocks")
        if row.get("kind") == "profile" and row.get("status") == "ready_to_configure"
    ]


def blocked_post_blocks(clipboard: dict) -> list[dict]:
    return [
        row for row in rows(clipboard, "blocks")
        if row.get("kind") == "post" and str(row.get("status", "")).startswith("blocked")
    ]


def launch_day_profile_rows(launch_day: dict) -> list[dict]:
    return [
        row for row in rows(launch_day)
        if row.get("phase") == "profile_setup"
    ]


def exception_stop_rows(runbook: dict) -> list[dict]:
    return [
        row for row in rows(runbook)
        if row.get("severity") == "stop"
    ]


def closure_steps(metrics: dict) -> list[dict[str, str]]:
    profile_ready = metrics["profileConfigured"] == len(EXPECTED_PLATFORMS)
    ready_to_publish = metrics["profilePublishReady"] == 1
    first_batch_done = metrics["firstBatchPublished"] == len(EXPECTED_PLATFORMS)
    kpi_done = metrics["minimumKpiRows"] == len(EXPECTED_PLATFORMS)
    return [
        {
            "id": "prepare_profile_clipboard",
            "status": "ready_to_act" if metrics["profileClipboardReady"] == len(EXPECTED_PLATFORMS) else "blocked",
            "command": "python3 tools/promotion_launch_clipboard.py --check && python3 tools/promotion_operation_proof_templates.py --check",
            "release": "Three profile setup copy blocks and profile proof templates are ready.",
            "stop": "Stop if the visible platform account is not LoveTypes or the profile copy adds paid, diagnosis, therapy, or guarantee claims.",
        },
        {
            "id": "capture_profile_proof",
            "status": "current_blocker" if not profile_ready else "complete",
            "command": "python3 tools/promotion_proof_rehearsal.py --check && python3 tools/promotion_profile_writeback.py check",
            "release": "All profile links are set/live with traceable proof notes.",
            "stop": "Do not write back profile status from memory, draft screens, private previews, or missing screenshots.",
        },
        {
            "id": "open_first_batch_publish",
            "status": "blocked_until_profile_writeback" if not ready_to_publish else "ready_to_publish",
            "command": "python3 tools/promotion_profile_publish_handoff.py --check && python3 tools/promotion_first_batch_publish_closure_quickstart.py --check",
            "release": "Profile handoff opens first-batch publishing.",
            "stop": "Do not publish first-batch posts while profile setup remains incomplete.",
        },
        {
            "id": "close_first_batch_and_kpi",
            "status": "blocked_until_public_posts" if not first_batch_done else "blocked_until_kpi" if not kpi_done else "complete",
            "command": "python3 tools/promotion_publish_kpi_handoff.py --check && python3 tools/promotion_first_batch_kpi_closure_quickstart.py --check",
            "release": "First batch posts have public URLs and checked minimum KPI rows.",
            "stop": "Do not open weekly review from placeholder URLs, private posts, or unchecked zero KPI values.",
        },
        {
            "id": "keep_exception_runbook_armed",
            "status": "armed",
            "command": "python3 tools/promotion_launch_exception_runbook.py --check",
            "release": "Stop/hold/escalate conditions are visible before every external platform action.",
            "stop": "Stop immediately on wrong account, missing permission, URL rewrite, unsafe copy, or emergency/support request.",
        },
    ]


def build_quickstart() -> dict:
    master = read_json(MASTER_GATE)
    launch = read_json(LAUNCH_QUICKSTART)
    clipboard = read_json(LAUNCH_CLIPBOARD)
    launch_day = read_json(LAUNCH_DAY)
    exception = read_json(EXCEPTION_RUNBOOK)
    proof_templates = read_json(PROOF_TEMPLATES)
    rehearsal = read_json(PROOF_REHEARSAL)
    handoff = read_json(HANDOFF)
    blockers = read_json(BLOCKERS)
    profile_handoff = read_json(PROFILE_HANDOFF)
    publish_kpi = read_json(PUBLISH_KPI_HANDOFF)

    profile_blocks = ready_profile_blocks(clipboard)
    post_blocks = blocked_post_blocks(clipboard)
    profile_rows = launch_day_profile_rows(launch_day)
    stop_rows = exception_stop_rows(exception)
    metrics = {
        "masterStage": str(master.get("stage", "")),
        "masterStageIndex": int(master.get("stageIndex", 0) or 0),
        "profileConfigured": metric(master, "profileConfigured"),
        "firstBatchPublished": metric(master, "firstBatchPublished"),
        "minimumKpiRows": metric(master, "firstBatchMinimumKpiRows"),
        "commandReadyRows": metric(master, "commandReadyRows"),
        "blockedDecisions": metric(master, "commandBlockedRows"),
        "launchCurrentBlockers": metric(launch, "stageCurrentBlockers"),
        "profileActions": metric(launch, "profileActions"),
        "profileClipboardReady": len(profile_blocks),
        "postClipboardBlocked": len(post_blocks),
        "launchDayReadyRows": metric(launch_day, "readyRows"),
        "launchDayBlockedRows": metric(launch_day, "blockedRows"),
        "exceptionStopRows": metric(exception, "stopRows"),
        "exceptionHoldRows": metric(exception, "holdRows"),
        "proofRows": metric(proof_templates, "proofRows"),
        "profileProofValid": metric(proof_templates, "profileValid"),
        "postProofSafelyRejected": metric(proof_templates, "postSafelyRejected"),
        "rehearsalProfilePass": metric(rehearsal, "profilePass"),
        "rehearsalPostPlaceholderRejected": metric(rehearsal, "postPlaceholderRejected"),
        "handoffReadyCount": int(handoff.get("readyCount", 0) or 0),
        "handoffBlockedCount": int(handoff.get("blockedCount", 0) or 0),
        "activeBlockers": metric(blockers, "activeBlockers"),
        "readyNowBlockers": metric(blockers, "readyNow"),
        "profilePublishReady": metric(profile_handoff, "readyToPublish"),
        "publishKpiReadyForWeekly": metric(publish_kpi, "readyForWeeklyReview"),
    }
    data = {
        "generatedAt": today(),
        "sources": {
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
            "launchQuickstart": str(LAUNCH_QUICKSTART.relative_to(ROOT)),
            "launchClipboard": str(LAUNCH_CLIPBOARD.relative_to(ROOT)),
            "launchDayRunSheet": str(LAUNCH_DAY.relative_to(ROOT)),
            "launchExceptionRunbook": str(EXCEPTION_RUNBOOK.relative_to(ROOT)),
            "operationProofTemplates": str(PROOF_TEMPLATES.relative_to(ROOT)),
            "proofRehearsal": str(PROOF_REHEARSAL.relative_to(ROOT)),
            "operatorHandoffPacket": str(HANDOFF.relative_to(ROOT)),
            "blockerResolutionChecklist": str(BLOCKERS.relative_to(ROOT)),
            "profilePublishHandoff": str(PROFILE_HANDOFF.relative_to(ROOT)),
            "publishKpiHandoff": str(PUBLISH_KPI_HANDOFF.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rules": [
            "Use master-gate stage as the source of truth; do not skip profile_setup.",
            "Profile setup may proceed now, but publish, KPI, weekly review, lead, and offer decisions remain blocked.",
            "Every external action needs visible account identity, safe copy, public URL verification, and proof note.",
            "Placeholder post URLs must be rejected until real public post URLs exist.",
            "Exception runbook stop conditions override all quickstarts.",
        ],
        "steps": closure_steps(metrics),
        "profileRows": profile_rows,
        "profileClipboardBlocks": profile_blocks,
        "blockedPostBlocks": post_blocks,
        "stopRows": stop_rows,
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    metrics = data["metrics"]
    issues: list[str] = []
    if metrics["masterStage"] != "profile_setup" and metrics["profileConfigured"] < len(EXPECTED_PLATFORMS):
        issues.append("stage must remain profile_setup until all profile links are configured")
    if metrics["profileActions"] != len(EXPECTED_PLATFORMS):
        issues.append("launch quickstart should expose three profile actions")
    if metrics["profileClipboardReady"] != len(EXPECTED_PLATFORMS):
        issues.append("launch clipboard should expose three ready profile blocks")
    if metrics["postClipboardBlocked"] != len(EXPECTED_PLATFORMS):
        issues.append("launch clipboard should keep three post blocks blocked before profile completion")
    if metrics["profileProofValid"] != len(EXPECTED_PLATFORMS):
        issues.append("operation proof templates should validate three profile proof files")
    if metrics["postProofSafelyRejected"] != len(EXPECTED_PLATFORMS):
        issues.append("operation proof templates should safely reject three placeholder post proof files")
    if metrics["rehearsalProfilePass"] != len(EXPECTED_PLATFORMS):
        issues.append("proof rehearsal should pass three profile scenarios")
    if metrics["rehearsalPostPlaceholderRejected"] != len(EXPECTED_PLATFORMS):
        issues.append("proof rehearsal should reject three placeholder post scenarios")
    if metrics["profileConfigured"] == 0 and metrics["profilePublishReady"] != 0:
        issues.append("profile publish handoff cannot open before profile links are configured")
    if metrics["firstBatchPublished"] == 0 and metrics["publishKpiReadyForWeekly"] != 0:
        issues.append("publish KPI handoff cannot open weekly review before first-batch posts are published")
    if not data["stopRows"]:
        issues.append("launch execution closure needs armed stop rows")
    for row in data["profileRows"]:
        label = f"{row.get('phase', '<phase>')}/{row.get('platform', '<platform>')}"
        if not row.get("check_command") or not row.get("write_command") or not row.get("stop_condition"):
            issues.append(f"{label}: profile launch row missing check/write/stop command")
    for step in data["steps"]:
        if not step.get("command") or not step.get("stop"):
            issues.append(f"{step.get('id', '<step>')}: missing command or stop condition")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Launch Execution Closure Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- master stage：`{metrics['masterStage']}`",
        f"- profile configured：{metrics['profileConfigured']} / {len(EXPECTED_PLATFORMS)}",
        f"- first batch published：{metrics['firstBatchPublished']} / {len(EXPECTED_PLATFORMS)}",
        f"- minimum KPI rows：{metrics['minimumKpiRows']} / {len(EXPECTED_PLATFORMS)}",
        f"- profile clipboard ready：{metrics['profileClipboardReady']}",
        f"- post clipboard blocked：{metrics['postClipboardBlocked']}",
        f"- launch day ready / blocked：{metrics['launchDayReadyRows']} / {metrics['launchDayBlockedRows']}",
        f"- exception stop / hold：{metrics['exceptionStopRows']} / {metrics['exceptionHoldRows']}",
        f"- proof profile pass / post rejected：{metrics['rehearsalProfilePass']} / {metrics['rehearsalPostPlaceholderRejected']}",
        f"- profile publish ready：{metrics['profilePublishReady']}",
        f"- publish KPI weekly ready：{metrics['publishKpiReadyForWeekly']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Closure Steps", ""])
    for step in data["steps"]:
        lines.extend([
            f"### `{step['id']}`",
            "",
            f"- status：`{step['status']}`",
            f"- command：`{step['command']}`",
            f"- release：{step['release']}",
            f"- stop：{step['stop']}",
            "",
        ])
    lines.extend(["## Profile Actions", ""])
    for row in data["profileRows"]:
        lines.extend([
            f"### {row.get('platform', '')}",
            "",
            f"- status：`{row.get('status', '')}`",
            f"- action：{row.get('action', '')}",
            f"- check：`{row.get('check_command', '')}`",
            f"- write：`{row.get('write_command', '')}`",
            f"- stop：{row.get('stop_condition', '')}",
            "",
        ])
    lines.extend(["## Armed Stop Conditions", ""])
    for row in data["stopRows"]:
        lines.append(f"- `{row.get('id', '')}`：{row.get('trigger', '')} Stop：{row.get('stop', '')}")
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes launch execution closure quickstart",
        f"generated: {data['generatedAt']}",
        f"master stage: {metrics['masterStage']}",
        f"profile configured: {metrics['profileConfigured']} / {len(EXPECTED_PLATFORMS)}",
        f"first batch published: {metrics['firstBatchPublished']} / {len(EXPECTED_PLATFORMS)}",
        f"minimum KPI rows: {metrics['minimumKpiRows']} / {len(EXPECTED_PLATFORMS)}",
        "",
        "Closure steps:",
    ]
    for step in data["steps"]:
        lines.extend([
            "",
            f"{step['id']}: {step['status']}",
            f"command: {step['command']}",
            f"release: {step['release']}",
            f"stop: {step['stop']}",
        ])
    lines.extend(["", "Profile actions:"])
    for row in data["profileRows"]:
        lines.extend([
            "",
            f"{row.get('platform', '')}: {row.get('status', '')}",
            f"check: {row.get('check_command', '')}",
            f"write: {row.get('write_command', '')}",
            f"stop: {row.get('stop_condition', '')}",
        ])
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the launch execution closure quickstart for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_launch_execution_closure_quickstart={args.output}")
        print(f"promotion_launch_execution_closure_quickstart_json={args.json_output}")
        print(f"promotion_launch_execution_closure_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_launch_execution_closure_quickstart_stage={metrics['masterStage']}")
    print(f"promotion_launch_execution_closure_quickstart_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_launch_execution_closure_quickstart_first_batch_published={metrics['firstBatchPublished']}")
    print(f"promotion_launch_execution_closure_quickstart_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_launch_execution_closure_quickstart_profile_clipboard_ready={metrics['profileClipboardReady']}")
    print(f"promotion_launch_execution_closure_quickstart_post_clipboard_blocked={metrics['postClipboardBlocked']}")
    print(f"promotion_launch_execution_closure_quickstart_launch_ready_rows={metrics['launchDayReadyRows']}")
    print(f"promotion_launch_execution_closure_quickstart_launch_blocked_rows={metrics['launchDayBlockedRows']}")
    print(f"promotion_launch_execution_closure_quickstart_exception_stop_rows={metrics['exceptionStopRows']}")
    print(f"promotion_launch_execution_closure_quickstart_profile_proof_valid={metrics['profileProofValid']}")
    print(f"promotion_launch_execution_closure_quickstart_post_proof_rejected={metrics['postProofSafelyRejected']}")
    print(f"promotion_launch_execution_closure_quickstart_profile_publish_ready={metrics['profilePublishReady']}")
    print(f"promotion_launch_execution_closure_quickstart_publish_kpi_weekly_ready={metrics['publishKpiReadyForWeekly']}")
    print(f"promotion_launch_execution_closure_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
