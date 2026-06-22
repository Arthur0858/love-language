#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
NEXT_ACTIONS = PROMOTION_DIR / "next-actions.json"
BLOCKERS = PROMOTION_DIR / "blocker-resolution-checklist.json"
LAUNCH_CLIPBOARD = PROMOTION_DIR / "launch-clipboard.json"
LAUNCH_DAY = PROMOTION_DIR / "launch-day-run-sheet.json"
OPERATOR_HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
PROOF_IMPORT = PROMOTION_DIR / "proof-import-closure-quickstart.json"
LAUNCH_EXECUTION = PROMOTION_DIR / "launch-execution-closure-quickstart.json"
PROFILE_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
PUBLISH_KPI = PROMOTION_DIR / "publish-kpi-handoff.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "operator-next-action-closure-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "operator-next-action-closure-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "operator-next-action-closure-quickstart.txt"


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


def blocks(payload: dict) -> list[dict]:
    value = payload.get("blocks", [])
    return value if isinstance(value, list) else []


def profile_clipboard_by_platform(payload: dict) -> dict[str, dict]:
    return {
        str(row.get("platform", "")): row
        for row in blocks(payload)
        if row.get("kind") == "profile"
    }


def launch_day_by_platform(payload: dict) -> dict[str, dict]:
    return {
        str(row.get("platform", "")): row
        for row in rows(payload)
        if row.get("phase") == "profile_setup"
    }


def handoff_by_platform(payload: dict) -> dict[str, dict]:
    return {
        str(row.get("platform", "")): row
        for row in rows(payload, "steps")
        if row.get("phase") == "profile_setup"
    }


def blocker_by_scope(payload: dict) -> dict[str, dict]:
    return {
        str(row.get("scope", "")): row
        for row in rows(payload)
        if row.get("phase") == "profile_setup"
    }


def active_platforms(*sources: dict[str, dict]) -> tuple[str, ...]:
    platforms: set[str] = set()
    for source in sources:
        platforms.update(platform for platform in source if platform)
    return tuple(sorted(platforms)) or ("youtube_shorts",)


def build_quickstart() -> dict:
    master = read_json(MASTER_GATE)
    next_actions = read_json(NEXT_ACTIONS)
    blockers = read_json(BLOCKERS)
    clipboard = read_json(LAUNCH_CLIPBOARD)
    launch_day = read_json(LAUNCH_DAY)
    handoff = read_json(OPERATOR_HANDOFF)
    proof_import = read_json(PROOF_IMPORT)
    launch_execution = read_json(LAUNCH_EXECUTION)
    profile_handoff = read_json(PROFILE_HANDOFF)
    publish_kpi = read_json(PUBLISH_KPI)
    clip_by_platform = profile_clipboard_by_platform(clipboard)
    day_by_platform = launch_day_by_platform(launch_day)
    handoff_platform = handoff_by_platform(handoff)
    blocker_scope = blocker_by_scope(blockers)
    platforms = active_platforms(clip_by_platform, day_by_platform, handoff_platform, blocker_scope)
    actions: list[dict] = []
    for platform in platforms:
        clip = clip_by_platform.get(platform, {})
        day = day_by_platform.get(platform, {})
        handoff_row = handoff_platform.get(platform, {})
        blocker = blocker_scope.get(platform, {})
        actions.append({
            "platform": platform,
            "status": str(day.get("status") or clip.get("status") or blocker.get("status") or ""),
            "title": str(handoff_row.get("title") or clip.get("label") or platform),
            "profileUrl": str(clip.get("copy", "")).split("Profile link: ", 1)[-1].split("\n", 1)[0] if "Profile link: " in str(clip.get("copy", "")) else str(handoff_row.get("url", "")),
            "copyBlock": str(clip.get("copy", "")),
            "proofTemplate": str(clip.get("proof", "")),
            "checkCommand": str(day.get("check_command") or clip.get("check_command") or ""),
            "writeCommand": str(day.get("write_command") or clip.get("write_command") or blocker.get("writeback_command") or ""),
            "stopCondition": str(day.get("stop_condition") or clip.get("stop_condition") or ""),
            "releaseCondition": str(blocker.get("release_condition") or "profile tracker row is set/live with proof note"),
            "evidenceRequired": handoff_row.get("evidenceRequired", []) if isinstance(handoff_row.get("evidenceRequired"), list) else [],
        })

    metrics = {
        "stage": str(master.get("stage", "")),
        "profileConfigured": metric(master, "profileConfigured"),
        "firstBatchPublished": metric(master, "firstBatchPublished"),
        "minimumKpiRows": metric(master, "firstBatchMinimumKpiRows"),
        "readyActions": sum(1 for item in actions if item["status"] in {"ready_to_configure", "ready_to_act", "ready"}),
        "profileActions": len(actions),
        "activePlatforms": len(platforms),
        "proofProfileValid": metric(proof_import, "profileValid"),
        "proofProfileTemplateValid": metric(proof_import, "profileTemplateValid") or metric(proof_import, "profileValid"),
        "proofProfilePlaceholderRows": metric(proof_import, "profilePlaceholderProofRows"),
        "proofProfileRealReadyRows": metric(proof_import, "profileRealProofReadyRows"),
        "proofPostRejected": metric(proof_import, "postSafelyRejected"),
        "launchProfileClipboardReady": metric(launch_execution, "profileClipboardReady"),
        "launchPostClipboardBlocked": metric(launch_execution, "postClipboardBlocked"),
        "profilePublishReady": metric(profile_handoff, "readyToPublish"),
        "publishKpiWeeklyReady": metric(publish_kpi, "readyForWeeklyReview"),
        "nextActionRows": len(rows(next_actions)),
        "activeBlockers": metric(blockers, "activeBlockers"),
        "readyNowBlockers": metric(blockers, "readyNow"),
    }
    data = {
        "generatedAt": today(),
        "sources": {
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
            "nextActions": str(NEXT_ACTIONS.relative_to(ROOT)),
            "blockerResolutionChecklist": str(BLOCKERS.relative_to(ROOT)),
            "launchClipboard": str(LAUNCH_CLIPBOARD.relative_to(ROOT)),
            "launchDayRunSheet": str(LAUNCH_DAY.relative_to(ROOT)),
            "operatorHandoffPacket": str(OPERATOR_HANDOFF.relative_to(ROOT)),
            "proofImportClosure": str(PROOF_IMPORT.relative_to(ROOT)),
            "launchExecutionClosure": str(LAUNCH_EXECUTION.relative_to(ROOT)),
            "profilePublishHandoff": str(PROFILE_HANDOFF.relative_to(ROOT)),
            "publishKpiHandoff": str(PUBLISH_KPI.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rules": [
            "Active platforms only are considered for first-round promotion operations.",
            "Run the check command before any writeback command.",
            "If profile setup is complete and first batch is published, the next external action is KPI source-proof collection.",
            "Do not write KPI, weekly review, lead route, Luna, affiliate, or offer decisions without source-checked evidence.",
            "Stop immediately if account identity, permission, URL preservation, or safety copy is uncertain.",
        ],
        "actions": actions,
        "afterActions": [
            {
                "id": "refresh_after_profile_writeback",
                "command": "python3 tools/promotion_daily_ops_refresh.py",
                "expected": "profileConfigured reflects active platform proof writeback.",
            },
            {
                "id": "check_profile_to_publish_gate",
                "command": "python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_publish_handoff.py --check",
                "expected": "readyToPublish opens only after active profile setup is complete.",
            },
            {
                "id": "keep_publish_locked_until_gate",
                "command": "python3 tools/promotion_first_batch_publish_closure_quickstart.py --check",
                "expected": "first-batch publishing stays proof-gated until a real public post URL exists.",
            },
        ],
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    metrics = data["metrics"]
    expected = metrics["activePlatforms"]
    issues: list[str] = []
    if metrics["stage"] not in {"profile_setup", "first_batch_publish", "first_batch_kpi", "kpi_backfill", "weekly_evidence"}:
        issues.append("operator next action closure expects profile_setup, first_batch_publish, first_batch_kpi, kpi_backfill, or weekly_evidence stage")
    if len(data["actions"]) != expected:
        issues.append(f"expected {expected} active profile setup actions")
    if metrics["profileConfigured"] < expected and metrics["readyActions"] != expected:
        issues.append("all active profile setup actions should be ready to act before profile configuration")
    if metrics["profileConfigured"] == 0 and metrics["profilePublishReady"] != 0:
        issues.append("profile publish handoff cannot be ready before profile writeback")
    if metrics["firstBatchPublished"] == 0 and metrics["publishKpiWeeklyReady"] != 0:
        issues.append("publish/KPI handoff cannot open weekly review before posts are published")
    if metrics["profileConfigured"] < expected and metrics["proofProfileTemplateValid"] != expected:
        issues.append("proof import closure should validate active profile proof templates before profile configuration")
    if metrics["firstBatchPublished"] < expected and metrics["proofPostRejected"] != expected:
        issues.append("proof import closure should reject active post placeholder templates")
    for action in data["actions"]:
        label = action.get("platform", "<platform>")
        if metrics["profileConfigured"] >= expected:
            continue
        if not action.get("copyBlock") or not action.get("proofTemplate"):
            issues.append(f"{label}: missing copy block or proof template")
        if "promotion_profile_text_import.py check" not in action.get("checkCommand", ""):
            issues.append(f"{label}: missing profile check command")
        if "promotion_profile_text_import.py add" not in action.get("writeCommand", "") or "--proof-note" not in action.get("writeCommand", ""):
            issues.append(f"{label}: missing proof-gated write command")
        if not str(action.get("profileUrl", "")).startswith("https://lovetypes.tw/start/?"):
            issues.append(f"{label}: profile URL should be tracked /start/ URL")
        if len(action.get("evidenceRequired", [])) < 5:
            issues.append(f"{label}: expected at least five evidence requirements")
        if not action.get("stopCondition"):
            issues.append(f"{label}: missing stop condition")
    for item in data["afterActions"]:
        if not item.get("command") or not item.get("expected"):
            issues.append(f"{item.get('id', '<after>')}: missing command or expected result")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Operator Next Action Closure Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- stage：`{metrics['stage']}`",
        f"- active platforms：{metrics['activePlatforms']}",
        f"- profile configured：{metrics['profileConfigured']} / {metrics['activePlatforms']}",
        f"- ready actions：{metrics['readyActions']} / {metrics['profileActions']}",
        f"- first batch published：{metrics['firstBatchPublished']} / {metrics['activePlatforms']}",
        f"- minimum KPI rows：{metrics['minimumKpiRows']} / {metrics['activePlatforms']}",
        f"- proof profile template valid：{metrics['proofProfileTemplateValid']}",
        f"- proof profile placeholder rows：{metrics['proofProfilePlaceholderRows']}",
        f"- proof profile real ready rows：{metrics['proofProfileRealReadyRows']}",
        f"- proof post rejected：{metrics['proofPostRejected']}",
        f"- profile publish ready：{metrics['profilePublishReady']}",
        f"- publish KPI weekly ready：{metrics['publishKpiWeeklyReady']}",
        f"- active blockers：{metrics['activeBlockers']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Allowed Actions Now", ""])
    for action in data["actions"]:
        lines.extend([
            f"### {action['title']} · `{action['platform']}`",
            "",
            f"- status：`{action['status']}`",
            f"- profile URL：{action['profileUrl']}",
            f"- release：{action['releaseCondition']}",
            f"- stop：{action['stopCondition']}",
            "",
            "Copy block:",
            "",
            "```text",
            action["copyBlock"],
            "```",
            "",
            "Proof template:",
            "",
            "```text",
            action["proofTemplate"],
            "```",
            "",
            f"- check：`{action['checkCommand']}`",
            f"- write：`{action['writeCommand']}`",
            "",
        ])
    lines.extend(["## After External Proof", ""])
    for item in data["afterActions"]:
        lines.append(f"- `{item['id']}`：`{item['command']}`；expected：{item['expected']}")
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes operator next action closure quickstart",
        f"generated: {data['generatedAt']}",
        f"stage: {metrics['stage']}",
        f"ready actions: {metrics['readyActions']} / {metrics['profileActions']}",
        f"profile configured: {metrics['profileConfigured']}",
        f"proof profile template valid: {metrics['proofProfileTemplateValid']}",
        f"proof profile placeholder rows: {metrics['proofProfilePlaceholderRows']}",
        f"proof profile real ready rows: {metrics['proofProfileRealReadyRows']}",
        "",
        "Allowed actions:",
    ]
    for action in data["actions"]:
        lines.extend([
            "",
            f"{action['platform']}: {action['status']}",
            f"profile URL: {action['profileUrl']}",
            f"check: {action['checkCommand']}",
            f"write: {action['writeCommand']}",
            f"stop: {action['stopCondition']}",
        ])
    lines.extend(["", "After external proof:"])
    for item in data["afterActions"]:
        lines.append(f"- {item['id']}: {item['command']} | {item['expected']}")
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the operator next action closure quickstart for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_operator_next_action_closure_quickstart={args.output}")
        print(f"promotion_operator_next_action_closure_quickstart_json={args.json_output}")
        print(f"promotion_operator_next_action_closure_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_operator_next_action_closure_quickstart_stage={metrics['stage']}")
    print(f"promotion_operator_next_action_closure_quickstart_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_operator_next_action_closure_quickstart_ready_actions={metrics['readyActions']}")
    print(f"promotion_operator_next_action_closure_quickstart_profile_actions={metrics['profileActions']}")
    print(f"promotion_operator_next_action_closure_quickstart_first_batch_published={metrics['firstBatchPublished']}")
    print(f"promotion_operator_next_action_closure_quickstart_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_operator_next_action_closure_quickstart_proof_profile_valid={metrics['proofProfileValid']}")
    print(f"promotion_operator_next_action_closure_quickstart_proof_profile_template_valid={metrics['proofProfileTemplateValid']}")
    print(f"promotion_operator_next_action_closure_quickstart_proof_profile_placeholder_rows={metrics['proofProfilePlaceholderRows']}")
    print(f"promotion_operator_next_action_closure_quickstart_proof_profile_real_ready={metrics['proofProfileRealReadyRows']}")
    print(f"promotion_operator_next_action_closure_quickstart_proof_post_rejected={metrics['proofPostRejected']}")
    print(f"promotion_operator_next_action_closure_quickstart_profile_publish_ready={metrics['profilePublishReady']}")
    print(f"promotion_operator_next_action_closure_quickstart_publish_kpi_weekly_ready={metrics['publishKpiWeeklyReady']}")
    print(f"promotion_operator_next_action_closure_quickstart_active_blockers={metrics['activeBlockers']}")
    print(f"promotion_operator_next_action_closure_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
