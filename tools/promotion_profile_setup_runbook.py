#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
SETUP_PATH = PROMOTION_DIR / "platform-profile-setup.json"
TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
COMPLETION_GATE_PATH = PROMOTION_DIR / "profile-completion-gate.json"
MASTER_GATE_PATH = PROMOTION_DIR / "master-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-setup-runbook.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-setup-runbook.json"
DEFAULT_CLIPBOARD_OUTPUT = PROMOTION_DIR / "profile-setup-clipboard.txt"
DEFAULT_PLATFORM_ORDER = ("youtube_shorts",)
CONFIGURED_STATUSES = {"set", "live"}
FORBIDDEN_CLAIMS = ("診斷", "療效", "保證修復", "必須購買")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def by_id(items: list[dict], key: str) -> dict[str, dict]:
    return {str(item.get(key, "")): item for item in items}


def platform_order(setup_items: dict[str, dict]) -> tuple[str, ...]:
    ordered = tuple(platform for platform in DEFAULT_PLATFORM_ORDER if platform in setup_items)
    return ordered + tuple(platform for platform in setup_items if platform not in ordered)


def expected_source(platform: str, setup_item: dict) -> str:
    query = parse_qs(urlparse(str(setup_item.get("profileLink", ""))).query)
    return query.get("utm_source", [""])[0]


def validate_profile_url(platform: str, value: str, setup_item: dict) -> list[str]:
    issues: list[str] = []
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    expected = {
        "utm_source": expected_source(platform, setup_item),
        "utm_medium": "social_profile",
        "utm_campaign": "first_round_quiz_completion",
        "utm_content": f"{platform}_bio",
    }
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
        issues.append("profile link must point to https://lovetypes.tw/start/")
    for key, expected_value in expected.items():
        if query.get(key, [""])[0] != expected_value:
            issues.append(f"profile link missing {key}={expected_value}")
    return issues


def proof_examples(platform: str, today_value: str) -> list[str]:
    return [
        "<REAL_SCREENSHOT_FILENAME> verified",
        "<REAL_PUBLIC_PROFILE_CLICK_URL_OR_TIMESTAMP> verified",
        "<REAL_SCREEN_RECORDING_FILENAME> verified",
    ]


def build_runbook() -> dict:
    today_value = date.today().isoformat()
    setup = load_json(SETUP_PATH)
    setup_items = by_id(setup.get("platforms", []), "platformId")
    tracker_items = {row["platform"]: row for row in read_csv(TRACKER_PATH)}
    completion_gate = load_json(COMPLETION_GATE_PATH)
    master_gate = load_json(MASTER_GATE_PATH)

    platforms: list[dict] = []
    for platform in platform_order(setup_items):
        setup_item = setup_items.get(platform, {})
        tracker_item = tracker_items.get(platform, {})
        profile_link = tracker_item.get("profile_link") or setup_item.get("profileLink", "")
        status = tracker_item.get("status", "")
        set_date = tracker_item.get("profile_link_set_date", "")
        configured = status in CONFIGURED_STATUSES and bool(set_date)
        writeback_set = (
            f"python3 tools/promotion_profile_writeback.py update --platform {platform} "
            f"--status set --set-date {today_value} "
            "--proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\""
        )
        writeback_live = (
            f"python3 tools/promotion_profile_writeback.py update --platform {platform} "
            f"--status live --set-date {today_value} "
            "--proof-note \"<REAL_PROFILE_CLICK_NOTE> verified\""
        )
        import_template = "\n".join([
            "LoveTypes profile setup writeback",
            f"platform: {platform}",
            "status: set",
            f"set_date: {today_value}",
            f"profile_link: {profile_link}",
            "proof_note: <REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified",
        ])
        platforms.append({
            "platform": platform,
            "label": tracker_item.get("label") or setup_item.get("label") or platform,
            "status": status,
            "configured": configured,
            "profileLink": profile_link,
            "profileLinkLabel": setup_item.get("profileLinkLabel", ""),
            "bio": setup_item.get("bio", ""),
            "pinnedComment": setup_item.get("pinnedComment", ""),
            "linkLimitNote": setup_item.get("linkLimitNote") or tracker_item.get("notes", ""),
            "verificationSteps": [
                "貼上 profile link 後，從平台畫面點擊或複製連結。",
                "確認瀏覽器抵達 https://lovetypes.tw/start/，且沒有 404。",
                f"確認 UTM 保留 utm_source={expected_source(platform, setup_item)}、utm_medium=social_profile、utm_campaign=first_round_quiz_completion、utm_content={platform}_bio。",
                "確認 Bio / 置頂留言只有測驗 CTA，沒有 Luna、聯盟書卷、診斷或療效承諾。",
                "保存截圖或公開點擊紀錄，proof note 必須含 screenshot / public URL / clicked / verified 等可追溯詞。",
            ],
            "writebackCommand": writeback_set,
            "liveCommand": writeback_live,
            "proofExamples": proof_examples(platform, today_value),
            "importTemplate": import_template,
            "postWritebackCommands": [
                "python3 tools/promotion_daily_ops_refresh.py",
                "python3 tools/promotion_profile_completion_gate.py --check",
                "python3 tools/promotion_master_gate.py --check",
            ],
            "urlIssues": validate_profile_url(platform, profile_link, setup_item),
        })

    configured_count = sum(1 for item in platforms if item["configured"])
    return {
        "generatedAt": today_value,
        "sourceFiles": {
            "setup": str(SETUP_PATH.relative_to(ROOT)),
            "tracker": str(TRACKER_PATH.relative_to(ROOT)),
            "profileCompletionGate": str(COMPLETION_GATE_PATH.relative_to(ROOT)),
            "masterGate": str(MASTER_GATE_PATH.relative_to(ROOT)),
        },
        "platformCount": len(platforms),
        "configuredCount": configured_count,
        "pendingCount": len(platforms) - configured_count,
        "clipboardBlocks": len(platforms),
        "currentStage": str(master_gate.get("stage", "")),
        "readyToPublish": bool(completion_gate.get("readyToPublish")),
        "platforms": platforms,
        "rules": {
            "publishGate": "目前活動平台的 profile link 都完成 set/live 並通過 gate 後，才發布第一批 Shorts。",
            "singleCta": "平台個人頁先只承接 15 題測驗，不直接導購。",
            "noFakeProof": "沒有外部平台截圖、公開點擊或可追溯紀錄時，不回填 set/live。",
            "forbiddenClaims": list(FORBIDDEN_CLAIMS),
        },
    }


def validate_runbook(runbook: dict) -> list[str]:
    issues: list[str] = []
    active_platforms = tuple(item.get("platform", "") for item in runbook.get("platforms", []))
    if runbook.get("platformCount") != len(active_platforms):
        issues.append(f"expected {len(active_platforms)} platforms")
    if runbook.get("clipboardBlocks") != len(active_platforms):
        issues.append(f"expected {len(active_platforms)} clipboard blocks")
    seen: set[str] = set()
    for item in runbook.get("platforms", []):
        platform = item.get("platform", "")
        label = platform or "<platform>"
        if platform not in active_platforms:
            issues.append(f"{label}: unexpected platform")
            continue
        if platform in seen:
            issues.append(f"{label}: duplicate platform")
        seen.add(platform)
        for issue in item.get("urlIssues", []):
            issues.append(f"{label}: {issue}")
        if not item.get("profileLinkLabel"):
            issues.append(f"{label}: missing profile link location")
        text = f"{item.get('bio', '')} {item.get('pinnedComment', '')}"
        if "完成 15 題測驗" not in text and "15-question quiz" not in text:
            issues.append(f"{label}: missing quiz CTA")
        for forbidden in FORBIDDEN_CLAIMS:
            if forbidden in text:
                issues.append(f"{label}: forbidden claim {forbidden}")
        if "--proof-note" not in item.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command missing --proof-note")
        if "--set-date" not in item.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command missing --set-date")
        if "--status set" not in item.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command must set status")
        if "LoveTypes profile setup writeback" not in item.get("importTemplate", ""):
            issues.append(f"{label}: missing structured import template")
        examples = " ".join(item.get("proofExamples", []))
        if "<REAL_" not in examples:
            issues.append(f"{label}: proof examples must force real proof replacement")
        if f"screenshot profile-{platform}-" in examples:
            issues.append(f"{label}: proof examples must not look like completed scaffold proof")
        commands = item.get("postWritebackCommands", [])
        for expected in (
            "python3 tools/promotion_daily_ops_refresh.py",
            "python3 tools/promotion_profile_completion_gate.py --check",
            "python3 tools/promotion_master_gate.py --check",
        ):
            if expected not in commands:
                issues.append(f"{label}: missing post-writeback command {expected}")
    missing = set(active_platforms) - seen
    if missing:
        issues.append("missing platforms: " + ", ".join(sorted(missing)))
    return issues


def render_markdown(runbook: dict, issues: list[str]) -> str:
    lines = [
        "# LoveTypes Profile Setup Runbook",
        "",
        f"- 產生日期：{runbook['generatedAt']}",
        f"- platforms：{runbook['platformCount']}",
        f"- configured：{runbook['configuredCount']}",
        f"- pending：{runbook['pendingCount']}",
        f"- clipboard blocks：{runbook['clipboardBlocks']}",
        f"- current stage：`{runbook['currentStage']}`",
        f"- ready_to_publish：{1 if runbook['readyToPublish'] else 0}",
        f"- issues：{len(issues)}",
        "",
        "## Operating Rules",
        "",
        f"- {runbook['rules']['publishGate']}",
        f"- {runbook['rules']['singleCta']}",
        f"- {runbook['rules']['noFakeProof']}",
        "- 禁用詞：" + "、".join(runbook["rules"]["forbiddenClaims"]),
        "",
        "## After Every Profile Update",
        "",
        "```bash",
        "python3 tools/promotion_daily_ops_refresh.py",
        "python3 tools/promotion_profile_completion_gate.py --check",
        "python3 tools/promotion_master_gate.py --check",
        "```",
        "",
    ]
    for item in runbook["platforms"]:
        lines.extend([
            f"## {item['label']}（`{item['platform']}`）",
            "",
            f"- current status：`{item['status']}`",
            f"- configured：{1 if item['configured'] else 0}",
            f"- link location：{item['profileLinkLabel']}",
            f"- profile link：{item['profileLink']}",
            f"- platform note：{item['linkLimitNote']}",
            "",
            "### Copy Into Profile",
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
            "### Verification",
            "",
        ])
        lines.extend(f"- {step}" for step in item["verificationSteps"])
        lines.extend([
            "",
            "### Writeback",
            "",
            "設定完成後：",
            "",
            "```bash",
            item["writebackCommand"],
            "```",
            "",
            "公開可點後：",
            "",
            "```bash",
            item["liveCommand"],
            "```",
            "",
            "Structured import template:",
            "",
            "```text",
            item["importTemplate"],
            "```",
            "",
            "Traceable proof note examples:",
            "",
        ])
        lines.extend(f"- `{example}`" for example in item["proofExamples"])
        if item["urlIssues"]:
            lines.extend(["", "### URL Issues", ""])
            lines.extend(f"- {issue}" for issue in item["urlIssues"])
        lines.append("")
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_clipboard(runbook: dict) -> str:
    lines = [
        "LoveTypes profile setup clipboard",
        f"generated: {runbook['generatedAt']}",
        "",
    ]
    for item in runbook["platforms"]:
        lines.extend([
            f"=== {item['label']} / {item['platform']} ===",
            f"Profile link location: {item['profileLinkLabel']}",
            f"Profile link: {item['profileLink']}",
            "",
            "Bio:",
            item["bio"],
            "",
            "Pinned / first comment:",
            item["pinnedComment"],
            "",
            "Writeback after setup:",
            item["writebackCommand"],
            "",
            "Structured import:",
            item["importTemplate"],
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(runbook: dict, issues: list[str], md_output: Path, json_output: Path, clipboard_output: Path) -> None:
    md_output.write_text(render_markdown(runbook, issues), encoding="utf-8")
    json_output.write_text(json.dumps({**runbook, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    clipboard_output.write_text(render_clipboard(runbook), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a copy/paste runbook for LoveTypes platform profile setup.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--clipboard-output", default=str(DEFAULT_CLIPBOARD_OUTPUT))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    runbook = build_runbook()
    issues = validate_runbook(runbook)
    if not args.check:
        write_outputs(runbook, issues, Path(args.output), Path(args.json_output), Path(args.clipboard_output))
        print(f"promotion_profile_setup_runbook={args.output}")
        print(f"promotion_profile_setup_runbook_json={args.json_output}")
        print(f"promotion_profile_setup_clipboard={args.clipboard_output}")
    print(f"promotion_profile_setup_runbook_platforms={runbook['platformCount']}")
    print(f"promotion_profile_setup_runbook_configured={runbook['configuredCount']}")
    print(f"promotion_profile_setup_runbook_pending={runbook['pendingCount']}")
    print(f"promotion_profile_setup_runbook_clipboard_blocks={runbook['clipboardBlocks']}")
    print(f"promotion_profile_setup_runbook_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
