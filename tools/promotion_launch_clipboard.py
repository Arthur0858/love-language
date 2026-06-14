#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import promotion_post_writeback as post_writeback


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_ACTION = PROMOTION_DIR / "profile-setup-action-sheet.json"
PUBLISH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
OPERATOR_HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
LAUNCH_DASHBOARD = PROMOTION_DIR / "launch-ops-dashboard.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "launch-clipboard.txt"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "launch-clipboard.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "launch-clipboard.json"
QUIZ_CTA_MARKERS = ("完成 15 題測驗", "Take the 15-question quiz", "15-question quiz")


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


def profile_blocks(profile: dict) -> list[dict[str, str]]:
    rows = profile.get("rows", []) if isinstance(profile.get("rows"), list) else []
    blocks: list[dict[str, str]] = []
    for row in rows:
        blocks.append({
            "kind": "profile",
            "platform": str(row.get("platform", "")),
            "label": str(row.get("label", "")),
            "status": str(row.get("action_status", "")),
            "title": f"{row.get('label', '')} profile setup",
            "copy": "\n".join([
                f"Profile link location: {row.get('profile_link_location', '')}",
                f"Profile link: {row.get('profile_link', '')}",
                "",
                "Bio:",
                str(row.get("bio", "")),
                "",
                "Pinned / first comment:",
                str(row.get("pinned_comment", "")),
            ]).strip(),
            "proof": "\n".join([
                "LoveTypes profile setup writeback",
                f"platform: {row.get('platform', '')}",
                "status: set",
                f"set_date: {date.today().isoformat()}",
                f"profile_link: {row.get('profile_link', '')}",
                "proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified",
            ]).strip(),
            "check_command": str(row.get("check_command", "")),
            "write_command": str(row.get("write_command", "")),
            "stop_condition": str(row.get("stop_condition", "")),
        })
    return blocks


def post_blocks(publish: dict) -> list[dict[str, str]]:
    rows = publish.get("rows", []) if isinstance(publish.get("rows"), list) else []
    blocks: list[dict[str, str]] = []
    placeholders = {
        "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
        "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
        "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
    }
    for row in rows:
        platform = str(row.get("platform", ""))
        blocked_by = str(row.get("blocked_by", ""))
        blocks.append({
            "kind": "post",
            "platform": platform,
            "label": platform,
            "status": str(row.get("action_status", "")),
            "title": str(row.get("title", "")),
            "copy": str(row.get("caption", "")),
            "proof": "\n".join([
                "LoveTypes platform post writeback",
                f"platform: {row.get('platform', '')}",
                f"task_id: {row.get('task_id', '')}",
                "status: published",
                f"published_date: {date.today().isoformat()}",
                f"post_url: {placeholders.get(platform, '<REAL_POST_URL>')}",
                "views: 0",
                "site_clicks: 0",
                "quiz_starts: 0",
                "quiz_completions: 0",
                f"proof_note: {post_writeback.POST_PROOF_NOTE_PLACEHOLDER}",
            ]).strip(),
            "check_command": str(row.get("check_command", "")),
            "write_command": str(row.get("write_command", "")),
            "stop_condition": str(row.get("stop_condition", "")) or (
                f"Stop while {blocked_by}; replace placeholder URL with real public post URL before writeback."
            ),
        })
    return blocks


def build_clipboard() -> dict:
    profile = load_json(PROFILE_ACTION)
    publish = load_json(PUBLISH_ACTION)
    handoff = load_json(OPERATOR_HANDOFF)
    dashboard = load_json(LAUNCH_DASHBOARD)
    blocks = profile_blocks(profile) + post_blocks(publish)
    issues = validate_blocks(blocks, profile, publish, handoff, dashboard)
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "profileActionSheet": str(PROFILE_ACTION.relative_to(ROOT)),
            "firstBatchPublishAction": str(PUBLISH_ACTION.relative_to(ROOT)),
            "operatorHandoff": str(OPERATOR_HANDOFF.relative_to(ROOT)),
            "launchOpsDashboard": str(LAUNCH_DASHBOARD.relative_to(ROOT)),
        },
        "metrics": {
            "blocks": len(blocks),
            "profileBlocks": sum(1 for block in blocks if block["kind"] == "profile"),
            "postBlocks": sum(1 for block in blocks if block["kind"] == "post"),
            "readyBlocks": sum(1 for block in blocks if str(block["status"]).startswith("ready")),
            "blockedBlocks": sum(1 for block in blocks if "blocked" in str(block["status"])),
            "dashboardBlockedAreas": metric(dashboard, "blockedAreas"),
            "handoffBlockedSteps": int(handoff.get("blockedCount", 0) or 0),
            "issues": len(issues),
        },
        "rules": [
            "Copy profile blocks first; publish blocks remain blocked until profile gate opens.",
            "Run check commands before write commands.",
            "Write commands require real external proof; placeholders must be replaced before use.",
            "Do not change the quiz CTA, add paid claims, or use guessed KPI values.",
        ],
        "blocks": blocks,
        "issues": issues,
    }


def validate_blocks(blocks: list[dict[str, str]], profile: dict, publish: dict, handoff: dict, dashboard: dict) -> list[str]:
    issues: list[str] = []
    profile_count = sum(1 for block in blocks if block["kind"] == "profile")
    post_count = sum(1 for block in blocks if block["kind"] == "post")
    expected_profile_count = len(profile.get("rows", []) if isinstance(profile.get("rows"), list) else [])
    expected_post_count = len(publish.get("rows", []) if isinstance(publish.get("rows"), list) else [])
    if profile_count != expected_profile_count:
        issues.append(f"expected {expected_profile_count} profile clipboard blocks, got {profile_count}")
    if post_count != expected_post_count:
        issues.append(f"expected {expected_post_count} post clipboard blocks, got {post_count}")
    if metric(profile, "configured") and metric(publish, "blocked") == 0 and not metric(publish, "ready"):
        issues.append("publish action metrics look inconsistent after profile configuration")
    for block in blocks:
        label = f"{block['kind']}/{block['platform']}"
        if not block.get("copy") or not block.get("proof"):
            issues.append(f"{label}: missing copy or proof block")
        if block["kind"] == "profile" and "Profile link:" not in block["copy"]:
            issues.append(f"{label}: profile copy missing Profile link")
        if block["kind"] == "profile":
            if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in block["proof"]:
                issues.append(f"{label}: profile proof should force real proof replacement")
            if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in block["write_command"]:
                issues.append(f"{label}: profile write command should force real proof replacement")
        if block["kind"] == "post" and not any(marker in block["copy"] for marker in QUIZ_CTA_MARKERS):
            issues.append(f"{label}: post copy should keep quiz CTA")
        if not block.get("check_command"):
            issues.append(f"{label}: missing check command")
        if not block.get("stop_condition"):
            issues.append(f"{label}: missing stop condition")
        if block["kind"] == "post" and "<REAL_" not in block["proof"]:
            issues.append(f"{label}: post proof should keep placeholder until real public URL exists")
        forbidden = ("診斷", "療效", "保證修復", "必須購買")
        if any(term in block["copy"] for term in forbidden):
            issues.append(f"{label}: copy contains forbidden commercial or clinical claim")
    if int(handoff.get("blockedCount", 0) or 0) < 1:
        issues.append("operator handoff should still expose blocked steps before external proof exists")
    if metric(dashboard, "blockedAreas") < 1:
        issues.append("launch dashboard should still expose blocked areas before external proof exists")
    return issues


def render_text(clipboard: dict) -> str:
    lines = [
        "LoveTypes launch clipboard",
        f"generated: {clipboard['generatedAt']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in clipboard["rules"])
    for block in clipboard["blocks"]:
        lines.extend([
            "",
            f"=== {block['kind'].upper()} / {block['label']} / {block['platform']} ===",
            f"status: {block['status']}",
            "",
            "COPY:",
            block["copy"],
            "",
            "PROOF TEMPLATE:",
            block["proof"],
            "",
            f"CHECK: {block['check_command']}",
            f"WRITE: {block['write_command']}",
            f"STOP: {block['stop_condition']}",
        ])
    if clipboard["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in clipboard["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_markdown(clipboard: dict) -> str:
    metrics = clipboard["metrics"]
    lines = [
        "# LoveTypes Launch Clipboard",
        "",
        f"- 產生日期：{clipboard['generatedAt']}",
        f"- blocks：{metrics['blocks']}",
        f"- profile blocks：{metrics['profileBlocks']}",
        f"- post blocks：{metrics['postBlocks']}",
        f"- ready / blocked blocks：{metrics['readyBlocks']} / {metrics['blockedBlocks']}",
        f"- dashboard blocked areas：{metrics['dashboardBlockedAreas']}",
        f"- handoff blocked steps：{metrics['handoffBlockedSteps']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in clipboard["rules"])
    for block in clipboard["blocks"]:
        lines.extend([
            "",
            f"## {block['kind']} · {block['label']} · `{block['platform']}`",
            "",
            f"- status：`{block['status']}`",
            "",
            "### Copy",
            "",
            "```text",
            block["copy"],
            "```",
            "",
            "### Proof Template",
            "",
            "```text",
            block["proof"],
            "```",
            "",
            f"- check：`{block['check_command']}`",
            f"- write：`{block['write_command']}`",
            f"- stop：{block['stop_condition']}",
        ])
    if clipboard["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in clipboard["issues"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a copy/paste launch clipboard for LoveTypes profile and first-batch operations.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    parser.add_argument("--md-output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    args = parser.parse_args()

    clipboard = build_clipboard()
    metrics = clipboard["metrics"]
    print(f"promotion_launch_clipboard_blocks={metrics['blocks']}")
    print(f"promotion_launch_clipboard_profile_blocks={metrics['profileBlocks']}")
    print(f"promotion_launch_clipboard_post_blocks={metrics['postBlocks']}")
    print(f"promotion_launch_clipboard_ready_blocks={metrics['readyBlocks']}")
    print(f"promotion_launch_clipboard_blocked_blocks={metrics['blockedBlocks']}")
    print(f"promotion_launch_clipboard_dashboard_blocked={metrics['dashboardBlockedAreas']}")
    print(f"promotion_launch_clipboard_issues={metrics['issues']}")
    for issue in clipboard["issues"]:
        print(issue)
    if clipboard["issues"]:
        return 1
    if not args.check:
        txt_output = Path(args.txt_output)
        md_output = Path(args.md_output)
        json_output = Path(args.json_output)
        txt_output.write_text(render_text(clipboard), encoding="utf-8")
        md_output.write_text(render_markdown(clipboard), encoding="utf-8")
        json_output.write_text(json.dumps(clipboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"promotion_launch_clipboard_txt={txt_output.relative_to(ROOT)}")
        print(f"promotion_launch_clipboard_md={md_output.relative_to(ROOT)}")
        print(f"promotion_launch_clipboard_json={json_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
