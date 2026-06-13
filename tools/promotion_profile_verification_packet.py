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
TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
SETUP_PATH = PROMOTION_DIR / "platform-profile-setup.json"
READINESS_PATH = PROMOTION_DIR / "launch-readiness-gate.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "profile-verification-packet.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "profile-verification-packet.json"
PLATFORM_ORDER = ("youtube_shorts", "tiktok", "instagram_reels")
CONFIGURED_STATUSES = {"set", "live"}
PROFILE_SOURCES = {
    "youtube_shorts": "youtube",
    "tiktok": "tiktok",
    "instagram_reels": "instagram",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def setup_by_platform(setup: dict) -> dict[str, dict]:
    return {str(item.get("platformId", "")): item for item in setup.get("platforms", [])}


def validate_profile_url(platform: str, value: str) -> list[str]:
    issues: list[str] = []
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    expected = {
        "utm_source": PROFILE_SOURCES.get(platform, ""),
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


def evidence_requirements() -> list[str]:
    return [
        "profile link 已實際貼到平台個人頁或說明欄。",
        "從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。",
        "UTM source / medium / campaign / content 沒有被平台移除或改寫。",
        "Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。",
        "留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。",
    ]


def build_packet() -> dict:
    tracker_rows = {row["platform"]: row for row in read_csv(TRACKER_PATH)}
    setup = setup_by_platform(load_json(SETUP_PATH))
    readiness = load_json(READINESS_PATH) if READINESS_PATH.exists() else {}
    readiness_metrics = readiness.get("metrics", {}) if isinstance(readiness.get("metrics"), dict) else {}
    readiness_state = readiness.get("readiness", {}) if isinstance(readiness.get("readiness"), dict) else {}
    platforms = []
    for platform in PLATFORM_ORDER:
        tracker = tracker_rows.get(platform, {})
        setup_item = setup.get(platform, {})
        link = tracker.get("profile_link") or setup_item.get("profileLink", "")
        status = tracker.get("status", "")
        set_date = tracker.get("profile_link_set_date", "")
        configured = status in CONFIGURED_STATUSES and bool(set_date)
        url_issues = validate_profile_url(platform, link)
        platforms.append({
            "platform": platform,
            "label": tracker.get("label") or setup_item.get("label") or platform,
            "status": status,
            "configured": configured,
            "profileLink": link,
            "profileLinkSetDate": set_date,
            "profileLinkLabel": setup_item.get("profileLinkLabel", ""),
            "bio": setup_item.get("bio", ""),
            "pinnedComment": setup_item.get("pinnedComment", ""),
            "notes": tracker.get("notes", ""),
            "urlIssues": url_issues,
            "evidenceRequirements": evidence_requirements(),
            "writebackCommand": (
                f"python3 tools/promotion_profile_writeback.py update --platform {platform} "
                f"--status set --set-date {date.today().isoformat()} --proof-note \"screenshot profile-{platform}-{date.today().isoformat()}.png verified\""
            ),
            "liveCommand": (
                f"python3 tools/promotion_profile_writeback.py update --platform {platform} "
                f"--status live --set-date {date.today().isoformat()} --proof-note \"public URL profile link clicked {date.today().isoformat()}\""
            ),
            "postWritebackCheck": [
                "重新跑 promotion_launch_readiness_gate.py。",
                "確認 promotion_launch_readiness_profile_configured 變成 3。",
                "只有 promotion_launch_readiness_ready_to_publish=1 時才發布第一批。",
            ],
        })
    configured_count = sum(1 for item in platforms if item["configured"])
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "tracker": str(TRACKER_PATH.relative_to(ROOT)),
            "setup": str(SETUP_PATH.relative_to(ROOT)),
            "readiness": str(READINESS_PATH.relative_to(ROOT)),
        },
        "platformCount": len(platforms),
        "configuredCount": configured_count,
        "pendingCount": len(platforms) - configured_count,
        "readyToPublish": bool(readiness_state.get("readyToPublishPosts")),
        "readinessCounters": {
            "profileConfigured": readiness_metrics.get("profileConfigured"),
            "readyToPublish": readiness_state.get("readyToPublishPosts"),
            "blockers": readiness_metrics.get("blockers"),
        },
        "platforms": platforms,
        "policy": {
            "doNotFake": True,
            "configuredRequires": ["status set/live", "profile_link_set_date", "verified proof note", "valid UTM profile link"],
            "publishBoundary": "Do not publish first batch until all three profile links are set/live and readiness ready_to_publish is true.",
            "commercialBoundary": "Profile copy keeps the CTA on the 15-question guardian quiz and does not promote Luna, books, or paid products first.",
        },
    }


def validate_packet(packet: dict) -> list[str]:
    issues: list[str] = []
    if packet.get("platformCount") != len(PLATFORM_ORDER):
        issues.append(f"expected {len(PLATFORM_ORDER)} platforms")
    seen = set()
    for item in packet.get("platforms", []):
        platform = item.get("platform", "")
        label = platform or "<platform>"
        if platform not in PLATFORM_ORDER:
            issues.append(f"{label}: unexpected platform")
            continue
        if platform in seen:
            issues.append(f"{label}: duplicate platform")
        seen.add(platform)
        if not item.get("profileLink"):
            issues.append(f"{label}: missing profileLink")
        for issue in item.get("urlIssues", []):
            issues.append(f"{label}: {issue}")
        if not item.get("bio"):
            issues.append(f"{label}: missing bio")
        text = f"{item.get('bio', '')} {item.get('pinnedComment', '')}"
        if "完成 15 題測驗" not in text:
            issues.append(f"{label}: profile copy missing quiz CTA")
        for forbidden in ("診斷", "療效", "保證修復", "必須購買"):
            if forbidden in text:
                issues.append(f"{label}: forbidden claim {forbidden}")
        if len(item.get("evidenceRequirements", [])) < 5:
            issues.append(f"{label}: evidence requirements are incomplete")
        if "--proof-note" not in item.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command must require proof note")
        if "--status set" not in item.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command must set status")
        if not item.get("postWritebackCheck"):
            issues.append(f"{label}: missing post writeback checks")
    missing = set(PLATFORM_ORDER) - seen
    if missing:
        issues.append("missing platforms: " + ", ".join(sorted(missing)))
    counters = packet.get("readinessCounters", {})
    if not isinstance(counters, dict):
        issues.append("readinessCounters should be an object")
    if "readyToPublish" not in counters:
        issues.append("missing readyToPublish readiness counter")
    return issues


def render_markdown(packet: dict, issues: list[str]) -> str:
    lines = [
        "# LoveTypes Profile Verification Packet",
        "",
        f"- 產生日期：{packet['generatedAt']}",
        f"- platforms：{packet['platformCount']}",
        f"- configured：{packet['configuredCount']}",
        f"- pending：{packet['pendingCount']}",
        f"- ready_to_publish：{1 if packet['readyToPublish'] else 0}",
        f"- issues：{len(issues)}",
        "",
        "## Gate",
        "",
        f"- {packet['policy']['publishBoundary']}",
        f"- {packet['policy']['commercialBoundary']}",
        "- 不用本文件偽造 profile 設定、post URL 或 KPI；只在外部平台完成後回填。",
        "",
    ]
    for item in packet["platforms"]:
        lines.extend([
            f"## {item['label']}（`{item['platform']}`）",
            "",
            f"- current status：`{item['status']}`",
            f"- configured：{1 if item['configured'] else 0}",
            f"- profile link：{item['profileLink']}",
            f"- link location：{item['profileLinkLabel']}",
            "",
            "### Bio",
            "",
            "```text",
            item["bio"],
            "```",
            "",
            "### Pinned / First Comment",
            "",
            "```text",
            item["pinnedComment"],
            "```",
            "",
            "### Evidence Required",
            "",
        ])
        lines.extend(f"- {step}" for step in item["evidenceRequirements"])
        lines.extend([
            "",
            "### Writeback",
            "",
            f"- 設定完成：`{item['writebackCommand']}`",
            f"- 公開可點：`{item['liveCommand']}`",
            "",
            "### After Writeback",
            "",
        ])
        lines.extend(f"- {step}" for step in item["postWritebackCheck"])
        if item["urlIssues"]:
            lines.extend(["", "### URL Issues", ""])
            lines.extend(f"- {issue}" for issue in item["urlIssues"])
        lines.append("")
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(packet: dict, issues: list[str], output: Path, json_output: Path) -> None:
    json_output.write_text(json.dumps({**packet, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.write_text(render_markdown(packet, issues), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a current-state verification packet for LoveTypes social profile setup.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    issues = validate_packet(packet)
    if not args.check:
        write_outputs(packet, issues, Path(args.output), Path(args.json_output))
        print(f"promotion_profile_verification_packet={args.output}")
        print(f"promotion_profile_verification_packet_json={args.json_output}")
    print(f"promotion_profile_verification_platforms={packet['platformCount']}")
    print(f"promotion_profile_verification_configured={packet['configuredCount']}")
    print(f"promotion_profile_verification_pending={packet['pendingCount']}")
    print(f"promotion_profile_verification_ready_to_publish={1 if packet['readyToPublish'] else 0}")
    print(f"promotion_profile_verification_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
