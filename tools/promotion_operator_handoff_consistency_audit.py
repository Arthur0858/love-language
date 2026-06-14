#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import promotion_post_text_import as post_import
import promotion_profile_text_import as profile_import


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
CLIPBOARD = PROMOTION_DIR / "launch-clipboard.json"
RUNBOOK = PROMOTION_DIR / "profile-setup-runbook.json"
LINK_READY = PROMOTION_DIR / "profile-link-readiness-packet.json"
PROOF_TEMPLATES = PROMOTION_DIR / "operation-proof-templates.json"
PROFILE_ACTION = PROMOTION_DIR / "profile-setup-action-sheet.json"
PUBLISH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"

PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
PROFILE_SOURCES = {
    "youtube_shorts": "youtube",
    "tiktok": "tiktok",
    "instagram_reels": "instagram",
}
POST_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def proof_path_for(platform: str, kind: str = "profile") -> str:
    if kind == "profile":
        return f"docs/promotion/first-round/proof-{platform}.txt"
    return f"docs/promotion/first-round/proof-{platform}-publish-lt-s01-iris-silence.txt"


def expected_profile_url(platform: str) -> str:
    source = PROFILE_SOURCES[platform]
    return (
        "https://lovetypes.tw/start/"
        f"?utm_source={source}"
        "&utm_medium=social_profile"
        "&utm_campaign=first_round_quiz_completion"
        f"&utm_content={platform}_bio"
    )


def valid_profile_url(platform: str, value: str) -> bool:
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "lovetypes.tw"
        and parsed.path == "/start/"
        and query.get("utm_source") == [PROFILE_SOURCES[platform]]
        and query.get("utm_medium") == ["social_profile"]
        and query.get("utm_campaign") == ["first_round_quiz_completion"]
        and query.get("utm_content") == [f"{platform}_bio"]
    )


def by_platform(rows: list[dict], platform_key: str = "platform") -> dict[str, dict]:
    return {str(row.get(platform_key, "")): row for row in rows if isinstance(row, dict)}


def command_mentions(command: str, expected: str) -> bool:
    return expected in command


def validate_profile_sources(metrics: dict[str, int], issues: list[str]) -> None:
    runbook = load_json(RUNBOOK)
    link_ready = load_json(LINK_READY)
    profile_action = load_json(PROFILE_ACTION)
    handoff = load_json(HANDOFF)
    clipboard = load_json(CLIPBOARD)
    proof_templates = load_json(PROOF_TEMPLATES)

    runbook_rows = by_platform(runbook.get("platforms", []))
    link_rows = by_platform(link_ready.get("rows", []))
    action_rows = by_platform(profile_action.get("rows", []))
    handoff_rows = by_platform([row for row in handoff.get("steps", []) if row.get("phase") == "profile_setup"])
    clipboard_rows = by_platform([row for row in clipboard.get("blocks", []) if row.get("kind") == "profile"])
    template_rows = by_platform([row for row in proof_templates.get("rows", []) if row.get("kind") == "profile_setup"])

    for platform in PLATFORMS:
        expected_url = expected_profile_url(platform)
        expected_path = proof_path_for(platform)
        rows = {
            "runbook": runbook_rows.get(platform, {}),
            "link_ready": link_rows.get(platform, {}),
            "profile_action": action_rows.get(platform, {}),
            "handoff": handoff_rows.get(platform, {}),
            "clipboard": clipboard_rows.get(platform, {}),
            "proof_template": template_rows.get(platform, {}),
        }
        metrics["promotion_operator_handoff_profile_sources_checked"] += len(rows)
        clipboard_copy = str(rows["clipboard"].get("copy", ""))
        url_values = [
            ("runbook", rows["runbook"].get("profileLink", "")),
            ("link_ready", rows["link_ready"].get("profile_link", "")),
            ("profile_action", rows["profile_action"].get("profile_link", "")),
            ("handoff", rows["handoff"].get("url", "")),
            ("clipboard", expected_url if expected_url in clipboard_copy else clipboard_copy),
        ]
        for source_name, value in url_values:
            if value != expected_url or not valid_profile_url(platform, str(value)):
                issues.append(f"{platform}: {source_name} profile URL is not the expected /start/ UTM URL")
        proof_path = ROOT / expected_path
        if not proof_path.exists():
            issues.append(f"{platform}: missing profile proof file {expected_path}")
            continue
        data, parse_issues = profile_import.parse_text(proof_path.read_text(encoding="utf-8"))
        metrics["promotion_operator_handoff_profile_proofs_checked"] += 1
        if parse_issues:
            issues.append(f"{platform}: profile proof template should parse cleanly: {'; '.join(parse_issues)}")
        elif data.get("profile_link") != expected_url:
            issues.append(f"{platform}: profile proof file profile_link does not match expected URL")
        runbook_command = str(rows["runbook"].get("writebackCommand", ""))
        if f"--platform {platform}" not in runbook_command or "--status set" not in runbook_command:
            issues.append(f"{platform}: runbook direct writeback command should reference platform and set status")
        commands = [
            rows["link_ready"].get("write_command", ""),
            rows["profile_action"].get("write_command", ""),
            rows["clipboard"].get("check_command", ""),
            rows["clipboard"].get("write_command", ""),
            rows["proof_template"].get("checkCommand", ""),
            rows["proof_template"].get("writeCommand", ""),
        ]
        for command in commands:
            if command and not command_mentions(str(command), expected_path):
                issues.append(f"{platform}: command does not reference expected profile proof path {expected_path}")
        if rows["handoff"].get("status") != "ready":
            issues.append(f"{platform}: handoff profile step should be ready before profile setup")
        if not str(rows["clipboard"].get("status", "")).startswith("ready"):
            issues.append(f"{platform}: clipboard profile block should be ready before profile setup")


def validate_post_sources(metrics: dict[str, int], issues: list[str]) -> None:
    publish_action = load_json(PUBLISH_ACTION)
    handoff = load_json(HANDOFF)
    clipboard = load_json(CLIPBOARD)
    proof_templates = load_json(PROOF_TEMPLATES)

    action_rows = by_platform(publish_action.get("rows", []))
    handoff_rows = by_platform([row for row in handoff.get("steps", []) if row.get("phase") == "publish_first_batch"])
    clipboard_rows = by_platform([row for row in clipboard.get("blocks", []) if row.get("kind") == "post"])
    template_rows = by_platform([row for row in proof_templates.get("rows", []) if row.get("kind") == "post_publish"])
    for platform in PLATFORMS:
        expected_path = proof_path_for(platform, "post")
        placeholder = POST_PLACEHOLDERS[platform]
        rows = {
            "publish_action": action_rows.get(platform, {}),
            "handoff": handoff_rows.get(platform, {}),
            "clipboard": clipboard_rows.get(platform, {}),
            "proof_template": template_rows.get(platform, {}),
        }
        metrics["promotion_operator_handoff_post_sources_checked"] += len(rows)
        proof_path = ROOT / expected_path
        if not proof_path.exists():
            issues.append(f"{platform}: missing post proof file {expected_path}")
            continue
        data, parse_issues = post_import.parse_text(proof_path.read_text(encoding="utf-8"))
        metrics["promotion_operator_handoff_post_proofs_checked"] += 1
        if not parse_issues:
            issues.append(f"{platform}: scaffold post proof should not pass until real post URL replaces placeholder")
        elif not any("non-placeholder https post_url" in issue for issue in parse_issues):
            issues.append(f"{platform}: post proof rejected for unexpected reason: {'; '.join(parse_issues)}")
        if data.get("post_url") != placeholder:
            issues.append(f"{platform}: post proof file should keep platform placeholder URL before publishing")
        commands = [
            rows["publish_action"].get("check_command", ""),
            rows["publish_action"].get("write_command", ""),
            rows["clipboard"].get("check_command", ""),
            rows["clipboard"].get("write_command", ""),
            rows["proof_template"].get("checkCommand", ""),
            rows["proof_template"].get("writeCommand", ""),
        ]
        for command in commands:
            if command and not command_mentions(str(command), expected_path):
                issues.append(f"{platform}: command does not reference expected post proof path {expected_path}")
        for source_name, row in rows.items():
            status = str(row.get("action_status") or row.get("status") or "")
            if source_name in {"publish_action", "clipboard"} and "blocked" not in status:
                issues.append(f"{platform}: {source_name} post should remain blocked before profile gate")
        if rows["handoff"].get("status") != "blocked_until_profile_links":
            issues.append(f"{platform}: handoff post step should remain blocked_until_profile_links")
        proof_text = str(rows["clipboard"].get("proof", ""))
        if placeholder not in proof_text:
            issues.append(f"{platform}: clipboard post proof should show the platform placeholder URL")


def main() -> int:
    metrics = {
        "promotion_operator_handoff_platforms": len(PLATFORMS),
        "promotion_operator_handoff_profile_sources_checked": 0,
        "promotion_operator_handoff_profile_proofs_checked": 0,
        "promotion_operator_handoff_post_sources_checked": 0,
        "promotion_operator_handoff_post_proofs_checked": 0,
    }
    issues: list[str] = []
    validate_profile_sources(metrics, issues)
    validate_post_sources(metrics, issues)
    print(f"promotion_operator_handoff_platforms={metrics['promotion_operator_handoff_platforms']}")
    print(f"promotion_operator_handoff_profile_sources_checked={metrics['promotion_operator_handoff_profile_sources_checked']}")
    print(f"promotion_operator_handoff_profile_proofs_checked={metrics['promotion_operator_handoff_profile_proofs_checked']}")
    print(f"promotion_operator_handoff_post_sources_checked={metrics['promotion_operator_handoff_post_sources_checked']}")
    print(f"promotion_operator_handoff_post_proofs_checked={metrics['promotion_operator_handoff_post_proofs_checked']}")
    print(f"promotion_operator_handoff_consistency_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
