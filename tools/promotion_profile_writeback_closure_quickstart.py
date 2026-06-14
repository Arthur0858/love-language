#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
CAPTURE = PROMOTION_DIR / "profile-proof-capture-quickstart.json"
WRITEBACK_PLAYBOOK = PROMOTION_DIR / "profile-writeback-playbook.json"
COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
PROFILE_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
LAUNCH_READINESS = PROMOTION_DIR / "launch-readiness-gate.json"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-writeback-closure-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-writeback-closure-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "profile-writeback-closure-quickstart.txt"


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def metric(payload: dict, key: str, default: int = 0) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return default
    try:
        return int(values.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def state(payload: dict, key: str) -> int:
    values = payload.get("state", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def readiness(payload: dict, key: str) -> int:
    values = payload.get("readiness", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def by_platform(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("platform", "")): row for row in rows if row.get("platform")}


def build_platforms(capture: dict, playbook: dict) -> list[dict]:
    capture_rows = by_platform(capture.get("platforms", []))
    command_rows = by_platform(playbook.get("platforms", []))
    platforms: list[dict] = []
    active_platforms = [str(row.get("platform", "")) for row in capture.get("platforms", []) if row.get("platform")]
    for platform in active_platforms:
        capture_row = capture_rows.get(platform, {})
        command_row = command_rows.get(platform, {})
        platforms.append({
            "platform": platform,
            "label": str(capture_row.get("label", command_row.get("label", platform))),
            "profileLink": str(capture_row.get("profileLink", command_row.get("profileLink", ""))),
            "proofFile": str(capture_row.get("proofFile", "")),
            "pendingEvidence": sum(1 for step in capture_row.get("evidenceSteps", []) if step.get("operatorStatus") != "done"),
            "checkCommand": str(capture_row.get("checkCommand", "")),
            "textImportWriteCommand": str(capture_row.get("writeCommand", "")),
            "setCommand": str(command_row.get("setCommand", "")),
            "liveCommand": str(command_row.get("liveCommand", "")),
            "currentStatus": str(command_row.get("currentStatus", "")),
            "stopCondition": str(capture_row.get("stopCondition", "")),
        })
    return platforms


def build_quickstart() -> dict:
    capture = read_json(CAPTURE)
    playbook = read_json(WRITEBACK_PLAYBOOK)
    completion = read_json(COMPLETION)
    handoff = read_json(PROFILE_HANDOFF)
    readiness_gate = read_json(LAUNCH_READINESS)
    master = read_json(MASTER_GATE)
    platforms = build_platforms(capture, playbook)
    data = {
        "generatedAt": today(),
        "sources": {
            "profileProofCapture": str(CAPTURE.relative_to(ROOT)),
            "profileWritebackPlaybook": str(WRITEBACK_PLAYBOOK.relative_to(ROOT)),
            "profileCompletionGate": str(COMPLETION.relative_to(ROOT)),
            "profilePublishHandoff": str(PROFILE_HANDOFF.relative_to(ROOT)),
            "launchReadinessGate": str(LAUNCH_READINESS.relative_to(ROOT)),
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
        },
        "metrics": {
            "platforms": len(platforms),
            "pendingEvidenceRows": metric(capture, "pendingEvidenceRows"),
            "captureIssues": metric(capture, "issues"),
            "configured": metric(playbook, "configured"),
            "writebackIssues": metric(playbook, "issues"),
            "completionConfigured": metric(completion, "profileConfigured"),
            "completionExpectedProfiles": metric(completion, "expectedProfiles", 3),
            "completionReady": state(completion, "readyForFirstBatchPublish"),
            "handoffReadyToPublish": metric(handoff, "readyToPublish"),
            "launchReadyToPublish": readiness(readiness_gate, "readyToPublishPosts"),
            "masterStageIndex": metric(master, "stageIndex"),
            "masterProfileConfigured": metric(master, "profileConfigured"),
            "masterFirstBatchPublished": metric(master, "firstBatchPublished"),
        },
        "rules": [
            "Do not run any add/writeback command until all six evidence checks for that platform are true.",
            "Use profile_text_import add only with a real proof note; scaffold screenshot names must be replaced by real evidence.",
            "After each writeback, run daily ops refresh before trusting downstream quickstarts.",
            "Publish can open only when profile completion, profile handoff, launch readiness, and master gate all agree.",
            "If any gate stays closed after writeback, stop and inspect that gate instead of publishing manually.",
        ],
        "closureSteps": [
            {
                "stepId": "capture_evidence",
                "status": "current" if metric(capture, "pendingEvidenceRows") else "complete",
                "command": "python3 tools/promotion_profile_proof_capture_quickstart.py --check",
                "stopCondition": "Stop if any required evidence row remains unverified for the platform you plan to write back.",
            },
            {
                "stepId": "writeback_profile_rows",
                "status": "blocked_until_evidence" if metric(capture, "pendingEvidenceRows") else "ready_after_manual_proof",
                "command": "python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-<platform>.txt --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\"",
                "stopCondition": "Stop if the proof note is generic, scaffold-only, missing, or not tied to platform/date.",
            },
            {
                "stepId": "refresh_ops_docs",
                "status": "blocked_until_writeback" if metric(playbook, "configured") < len(platforms) else "ready",
                "command": "python3 tools/promotion_daily_ops_refresh.py",
                "stopCondition": "Do not publish from stale generated packets after tracker writeback.",
            },
            {
                "stepId": "verify_profile_gates",
                "status": "blocked_until_refresh" if not state(completion, "readyForFirstBatchPublish") else "complete",
                "command": "python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_profile_publish_handoff.py --check && python3 tools/promotion_launch_readiness_gate.py --check",
                "stopCondition": "Publish only when all profile gates agree ready_to_publish is open.",
            },
            {
                "stepId": "open_first_batch_publish",
                "status": "blocked_until_profile_gate" if not readiness(readiness_gate, "readyToPublishPosts") else "ready",
                "command": "python3 tools/promotion_first_batch_publish_quickstart.py --check",
                "stopCondition": "Do not publish if any first-batch row remains blocked_until_profile_links.",
            },
        ],
        "platforms": platforms,
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    issues: list[str] = []
    metrics = data["metrics"]
    if metrics["platforms"] < 1:
        issues.append("expected at least one active platform closure row")
    if metrics["configured"] == 0 and metrics["completionReady"]:
        issues.append("profile completion cannot be ready while no profile rows are configured")
    if metrics["configured"] == 0 and metrics["launchReadyToPublish"]:
        issues.append("launch readiness cannot open publishing while no profile rows are configured")
    if metrics["masterProfileConfigured"] and metrics["masterProfileConfigured"] != metrics["completionConfigured"]:
        issues.append("master gate and profile completion configured counts should match")
    for platform in data["platforms"]:
        label = platform["platform"]
        if "/start/" not in platform["profileLink"] or "utm_campaign=first_round_quiz_completion" not in platform["profileLink"]:
            issues.append(f"{label}: profile link must use first-round /start/ campaign")
        if not platform["proofFile"].endswith(f"proof-{label}.txt"):
            issues.append(f"{label}: proof file should match platform")
        if not platform["checkCommand"] or not platform["textImportWriteCommand"]:
            issues.append(f"{label}: missing text import check/write command")
        if not platform["setCommand"] or not platform["liveCommand"]:
            issues.append(f"{label}: missing direct writeback set/live command")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in platform["setCommand"]:
            issues.append(f"{label}: direct set command must force real proof replacement")
        if "<REAL_PROFILE_CLICK_NOTE>" not in platform["liveCommand"]:
            issues.append(f"{label}: direct live command must force real click proof replacement")
        if "public URL profile link clicked 20" in platform["liveCommand"]:
            issues.append(f"{label}: direct live command must not use a scaffold click-proof phrase")
    for step in data["closureSteps"]:
        if not step.get("command") or not step.get("stopCondition"):
            issues.append(f"{step.get('stepId', '<step>')}: missing command or stop condition")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Profile Writeback Closure Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- platforms：{metrics['platforms']}",
        f"- pending evidence rows：{metrics['pendingEvidenceRows']}",
        f"- configured：{metrics['configured']} / {metrics['completionExpectedProfiles']}",
        f"- completion ready：{metrics['completionReady']}",
        f"- handoff ready to publish：{metrics['handoffReadyToPublish']}",
        f"- launch ready to publish：{metrics['launchReadyToPublish']}",
        f"- master stage index：{metrics['masterStageIndex']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Closure Steps", ""])
    for step in data["closureSteps"]:
        lines.extend([
            f"- `{step['stepId']}` / `{step['status']}`：`{step['command']}`",
            f"  Stop: {step['stopCondition']}",
        ])
    lines.extend(["", "## Platform Writeback Commands", ""])
    for platform in data["platforms"]:
        lines.extend([
            f"### {platform['label']} (`{platform['platform']}`)",
            "",
            f"- current status：`{platform['currentStatus']}`",
            f"- pending evidence：{platform['pendingEvidence']}",
            f"- profile link：{platform['profileLink']}",
            f"- proof file：`{platform['proofFile']}`",
            f"- check：`{platform['checkCommand']}`",
            f"- text import write：`{platform['textImportWriteCommand']}`",
            f"- direct set：`{platform['setCommand']}`",
            f"- direct live：`{platform['liveCommand']}`",
            f"- stop：{platform['stopCondition']}",
            "",
        ])
    if data["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes profile writeback closure quickstart",
        f"generated: {data['generatedAt']}",
        f"pending evidence rows: {metrics['pendingEvidenceRows']}",
        f"configured: {metrics['configured']} / {metrics['completionExpectedProfiles']}",
        f"launch ready to publish: {metrics['launchReadyToPublish']}",
        "",
        "Closure steps:",
    ]
    for step in data["closureSteps"]:
        lines.append(f"- {step['stepId']} / {step['status']}: {step['command']}")
    lines.extend(["", "Platforms:"])
    for platform in data["platforms"]:
        lines.extend([
            "",
            f"=== {platform['label']} / {platform['platform']} ===",
            f"pending evidence: {platform['pendingEvidence']}",
            f"check: {platform['checkCommand']}",
            f"text import write: {platform['textImportWriteCommand']}",
            f"direct set: {platform['setCommand']}",
            f"direct live: {platform['liveCommand']}",
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
    parser = argparse.ArgumentParser(description="Build a closure quickstart for LoveTypes profile writeback and gate verification.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_profile_writeback_closure_quickstart={args.output}")
        print(f"promotion_profile_writeback_closure_quickstart_json={args.json_output}")
        print(f"promotion_profile_writeback_closure_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_profile_writeback_closure_quickstart_platforms={metrics['platforms']}")
    print(f"promotion_profile_writeback_closure_quickstart_pending_evidence_rows={metrics['pendingEvidenceRows']}")
    print(f"promotion_profile_writeback_closure_quickstart_configured={metrics['configured']}")
    print(f"promotion_profile_writeback_closure_quickstart_completion_ready={metrics['completionReady']}")
    print(f"promotion_profile_writeback_closure_quickstart_handoff_ready={metrics['handoffReadyToPublish']}")
    print(f"promotion_profile_writeback_closure_quickstart_launch_ready={metrics['launchReadyToPublish']}")
    print(f"promotion_profile_writeback_closure_quickstart_master_stage_index={metrics['masterStageIndex']}")
    print(f"promotion_profile_writeback_closure_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
