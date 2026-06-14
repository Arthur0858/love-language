#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
ACTION_PATH = PROMOTION_DIR / "profile-setup-action-sheet.json"
TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.json"
EVIDENCE_PATH = PROMOTION_DIR / "profile-evidence-checklist.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "profile-quickstart.txt"
REQUIRED_PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
FORBIDDEN_TERMS = ("診斷", "療效", "保證修復", "必須購買")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def by_platform(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("platform", "")): row for row in rows if row.get("platform")}


def evidence_counts(evidence: dict) -> dict[str, dict[str, int]]:
    counts = {platform: {"total": 0, "pending": 0, "done": 0} for platform in REQUIRED_PLATFORMS}
    for item in evidence.get("items", []):
        platform = str(item.get("platform", ""))
        status = str(item.get("operator_status", "pending"))
        if platform not in counts:
            continue
        counts[platform]["total"] += 1
        if status == "done":
            counts[platform]["done"] += 1
        else:
            counts[platform]["pending"] += 1
    return counts


def proof_template(row: dict) -> str:
    platform = str(row.get("platform", ""))
    return "\n".join([
        "LoveTypes profile setup writeback",
        f"platform: {platform}",
        "status: set",
        f"set_date: {today()}",
        f"profile_link: {row.get('profile_link', '')}",
        "proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified",
    ])


def write_command(row: dict) -> str:
    platform = str(row.get("platform", ""))
    proof_file = f"docs/promotion/first-round/proof-{platform}.txt"
    return (
        "python3 tools/promotion_profile_text_import.py add "
        f"--input {proof_file} "
        "--proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\""
    )


def build_quickstart() -> dict:
    action = read_json(ACTION_PATH)
    tracker = read_json(TRACKER_PATH)
    evidence = read_json(EVIDENCE_PATH)
    action_rows = by_platform(action.get("rows", []))
    tracker_rows = by_platform(tracker.get("rows", []))
    evidence_by_platform = evidence_counts(evidence)
    platforms: list[dict] = []

    for platform in REQUIRED_PLATFORMS:
        row = action_rows.get(platform, {})
        tracker_row = tracker_rows.get(platform, {})
        proof_file = str(row.get("proof_file") or f"docs/promotion/first-round/proof-{platform}.txt")
        platforms.append({
            "platform": platform,
            "label": str(row.get("label", platform)),
            "currentStatus": str(tracker_row.get("status", row.get("status", ""))),
            "actionStatus": str(row.get("action_status", "")),
            "profileLinkLocation": str(row.get("profile_link_location", "")),
            "profileLink": str(row.get("profile_link", "")),
            "bio": str(row.get("bio", "")),
            "pinnedComment": str(row.get("pinned_comment", "")),
            "identityChecks": int(row.get("identity_checks", 0) or 0),
            "evidenceChecks": int(row.get("evidence_checks", 0) or 0),
            "pendingEvidenceChecks": evidence_by_platform.get(platform, {}).get("pending", 0),
            "proofFile": proof_file,
            "proofTemplate": proof_template(row),
            "checkCommand": str(row.get("check_command", "")),
            "writeCommand": write_command(row),
            "stopCondition": str(row.get("stop_condition", "")),
        })

    issues = validate(platforms)
    return {
        "generatedAt": today(),
        "sources": {
            "profileActionSheet": str(ACTION_PATH.relative_to(ROOT)),
            "profileTracker": str(TRACKER_PATH.relative_to(ROOT)),
            "profileEvidenceChecklist": str(EVIDENCE_PATH.relative_to(ROOT)),
        },
        "metrics": {
            "platforms": len(platforms),
            "readyToConfigure": sum(1 for item in platforms if item["actionStatus"] == "ready_to_configure"),
            "readyToWriteback": sum(1 for item in platforms if item["actionStatus"] == "ready_to_writeback"),
            "configured": sum(1 for item in platforms if item["currentStatus"] in {"set", "live"}),
            "pendingEvidenceChecks": sum(int(item["pendingEvidenceChecks"]) for item in platforms),
            "issues": len(issues),
        },
        "rules": [
            "Only complete profile setup when the external platform profile visibly contains the tracked /start/ link.",
            "Use the profile proof text after replacing the proof placeholder with real evidence.",
            "Run the check command before the write command.",
            "Do not publish first-batch posts until all three profile links are set or live.",
            "Keep profile copy focused on the 15-question quiz; do not add paid, affiliate, diagnosis, or treatment claims.",
        ],
        "platforms": platforms,
        "issues": issues,
    }


def validate(platforms: list[dict]) -> list[str]:
    issues: list[str] = []
    seen = {item.get("platform") for item in platforms}
    if seen != set(REQUIRED_PLATFORMS):
        issues.append("profile quickstart must include YouTube Shorts, TikTok, and Instagram Reels")
    for item in platforms:
        label = str(item.get("platform", "<platform>"))
        link = str(item.get("profileLink", ""))
        combined_copy = "\n".join([
            str(item.get("bio", "")),
            str(item.get("pinnedComment", "")),
        ])
        if "/start/" not in link or "utm_campaign=first_round_quiz_completion" not in link:
            issues.append(f"{label}: profile link must use the first-round /start/ campaign URL")
        if "完成 15 題測驗" not in combined_copy and "15 題" not in combined_copy:
            issues.append(f"{label}: profile copy should keep the 15-question quiz CTA")
        if any(term in combined_copy for term in FORBIDDEN_TERMS):
            issues.append(f"{label}: profile copy contains forbidden claim language")
        if int(item.get("identityChecks", 0) or 0) != 7:
            issues.append(f"{label}: expected 7 identity checks")
        if int(item.get("evidenceChecks", 0) or 0) != 6:
            issues.append(f"{label}: expected 6 evidence checks")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in str(item.get("proofTemplate", "")):
            issues.append(f"{label}: proof template must force real external evidence replacement")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in str(item.get("writeCommand", "")):
            issues.append(f"{label}: write command must keep real evidence placeholder")
        if not item.get("checkCommand"):
            issues.append(f"{label}: missing check command")
        if not item.get("stopCondition"):
            issues.append(f"{label}: missing stop condition")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Profile Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- platforms：{metrics['platforms']}",
        f"- ready to configure：{metrics['readyToConfigure']}",
        f"- ready to writeback：{metrics['readyToWriteback']}",
        f"- configured：{metrics['configured']}",
        f"- pending evidence checks：{metrics['pendingEvidenceChecks']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    for item in data["platforms"]:
        lines.extend([
            "",
            f"## {item['label']}（`{item['platform']}`）",
            "",
            f"- current status：`{item['currentStatus']}`",
            f"- action status：`{item['actionStatus']}`",
            f"- link location：{item['profileLinkLocation']}",
            f"- profile link：{item['profileLink']}",
            f"- identity / evidence checks：{item['identityChecks']} / {item['evidenceChecks']}",
            f"- pending evidence checks：{item['pendingEvidenceChecks']}",
            f"- proof file：`{item['proofFile']}`",
            "",
            "Bio:",
            "",
            "```text",
            item["bio"],
            "```",
            "",
            "Pinned / first comment:",
            "",
            "```text",
            item["pinnedComment"],
            "```",
            "",
            "Proof text to save after real platform verification:",
            "",
            "```text",
            item["proofTemplate"],
            "```",
            "",
            f"- check：`{item['checkCommand']}`",
            f"- write：`{item['writeCommand']}`",
            f"- stop：{item['stopCondition']}",
        ])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    lines = [
        "LoveTypes profile quickstart",
        f"generated: {data['generatedAt']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    for item in data["platforms"]:
        lines.extend([
            "",
            f"=== {item['label']} / {item['platform']} ===",
            f"status: {item['currentStatus']} / {item['actionStatus']}",
            f"location: {item['profileLinkLocation']}",
            f"profile link: {item['profileLink']}",
            "",
            "BIO:",
            item["bio"],
            "",
            "PINNED / FIRST COMMENT:",
            item["pinnedComment"],
            "",
            f"Save this proof text to {item['proofFile']} after replacing the proof placeholder:",
            item["proofTemplate"],
            "",
            f"CHECK: {item['checkCommand']}",
            f"WRITE: {item['writeCommand']}",
            f"STOP: {item['stopCondition']}",
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
    parser = argparse.ArgumentParser(description="Build a profile-only quickstart packet for LoveTypes promotion launch.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_profile_quickstart={args.output}")
        print(f"promotion_profile_quickstart_json={args.json_output}")
        print(f"promotion_profile_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_profile_quickstart_platforms={metrics['platforms']}")
    print(f"promotion_profile_quickstart_ready_configure={metrics['readyToConfigure']}")
    print(f"promotion_profile_quickstart_ready_writeback={metrics['readyToWriteback']}")
    print(f"promotion_profile_quickstart_configured={metrics['configured']}")
    print(f"promotion_profile_quickstart_pending_evidence={metrics['pendingEvidenceChecks']}")
    print(f"promotion_profile_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
