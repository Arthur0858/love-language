#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import promotion_refresh
from promotion_proof_note_policy import proof_note_issue


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
PLAYBOOK_MD = PROMOTION_DIR / "profile-writeback-playbook.md"
PLAYBOOK_JSON = PROMOTION_DIR / "profile-writeback-playbook.json"
PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
STATUS_VALUES = ("planned", "set", "live", "paused", "blocked")
CONFIGURED_STATUSES = ("set", "live")
PROFILE_SOURCES = {
    "youtube_shorts": "youtube",
    "tiktok": "tiktok",
    "instagram_reels": "instagram",
}
METRIC_FIELDS = (
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    return int(float(text))


def is_start_campaign_url(platform: str, value: str) -> bool:
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


def validate_date(value: str) -> bool:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return False
    return parsed <= date.today()


def validate_tracker(fieldnames: list[str], rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    missing_fields = {"platform", "status", "profile_link", "profile_link_set_date", "notes", *METRIC_FIELDS} - set(fieldnames)
    if missing_fields:
        issues.append(f"missing tracker fields: {', '.join(sorted(missing_fields))}")
    seen = set()
    for row in rows:
        platform = (row.get("platform") or "").strip()
        label = platform or "<platform>"
        if platform not in PLATFORMS:
            issues.append(f"{label}: unexpected platform")
            continue
        if platform in seen:
            issues.append(f"{label}: duplicate platform")
        seen.add(platform)
        status = (row.get("status") or "").strip()
        if status not in STATUS_VALUES:
            issues.append(f"{label}: invalid status {status}")
        if not is_start_campaign_url(platform, row.get("profile_link", "")):
            issues.append(f"{label}: profile_link must be the platform-specific /start/ campaign URL")
        set_date = (row.get("profile_link_set_date") or "").strip()
        if status in CONFIGURED_STATUSES:
            if not set_date:
                issues.append(f"{label}: {status} requires profile_link_set_date")
            elif not validate_date(set_date):
                issues.append(f"{label}: profile_link_set_date must be YYYY-MM-DD and not in the future")
            if "verified:" not in (row.get("notes") or ""):
                issues.append(f"{label}: {status} requires verified proof note")
            issue = proof_note_issue(row.get("notes") or "", f"{label} notes")
            if issue:
                issues.append(issue)
        for field in METRIC_FIELDS:
            value = (row.get(field) or "").strip()
            if not value:
                continue
            try:
                parsed = parse_int(value)
            except ValueError:
                issues.append(f"{label}: {field} must be numeric")
                continue
            if parsed < 0:
                issues.append(f"{label}: {field} must not be negative")
    missing_platforms = set(PLATFORMS) - seen
    if missing_platforms:
        issues.append(f"missing platforms: {', '.join(sorted(missing_platforms))}")
    return issues


def update_row(
    rows: list[dict[str, str]],
    platform: str,
    status: str,
    set_date: str,
    proof_note: str,
    metrics: dict[str, str],
) -> None:
    if platform not in PLATFORMS:
        raise SystemExit(f"unknown platform: {platform}")
    if status not in STATUS_VALUES:
        raise SystemExit(f"invalid status: {status}")
    if status in CONFIGURED_STATUSES:
        if not set_date or not validate_date(set_date):
            raise SystemExit("set/live updates require --set-date YYYY-MM-DD and not in the future")
        if not proof_note:
            raise SystemExit("set/live updates require --proof-note with real verification evidence")
        issue = proof_note_issue(proof_note)
        if issue:
            raise SystemExit(issue)
    for row in rows:
        if row.get("platform") != platform:
            continue
        row["status"] = status
        if set_date:
            row["profile_link_set_date"] = set_date
        for field, value in metrics.items():
            if value != "":
                row[field] = str(parse_int(value))
        note_parts = [row.get("notes", "").strip()]
        if proof_note:
            note_parts.append(f"verified:{set_date or date.today().isoformat()} {proof_note}")
        row["notes"] = " | ".join(part for part in note_parts if part)
        return
    raise SystemExit(f"platform not found in tracker: {platform}")


def playbook(fieldnames: list[str], rows: list[dict[str, str]], issues: list[str]) -> dict:
    commands = []
    for row in rows:
        platform = row["platform"]
        commands.append({
            "platform": platform,
            "label": row.get("label", platform),
            "profileLink": row.get("profile_link", ""),
            "currentStatus": row.get("status", "planned"),
            "setCommand": (
                f"python3 tools/promotion_profile_writeback.py update --platform {platform} "
                f"--status set --set-date {date.today().isoformat()} --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\""
            ),
            "liveCommand": (
                f"python3 tools/promotion_profile_writeback.py update --platform {platform} "
                f"--status live --set-date {date.today().isoformat()} --proof-note \"<REAL_PROFILE_CLICK_NOTE> verified\""
            ),
        })
    configured = sum(1 for row in rows if row.get("status") in CONFIGURED_STATUSES)
    return {
        "generatedAt": date.today().isoformat(),
        "source": str(TRACKER_PATH.relative_to(ROOT)),
        "platforms": commands,
        "metrics": {
            "rows": len(rows),
            "configured": configured,
            "issues": len(issues),
        },
        "policy": {
            "doNotFake": True,
            "configuredStatuses": list(CONFIGURED_STATUSES),
            "setLiveRequires": ["profile_link_set_date", "verified proof note", "platform-specific /start/ URL"],
            "afterWriteback": [
                "Run promotion_platform_profile_tracker.py",
                "Run promotion_launch_readiness_gate.py",
                "Only publish first batch when readiness ready_to_publish=1",
            ],
        },
        "issues": issues,
    }


def render_markdown(data: dict) -> str:
    lines = [
        "# LoveTypes Profile Writeback Playbook",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- configured：{data['metrics']['configured']} / {data['metrics']['rows']}",
        f"- issues：{data['metrics']['issues']}",
        "- 原則：只有實際設定並確認平台 profile link 後，才能用 `set` 或 `live`。",
        "",
        "## 回填命令",
        "",
    ]
    for item in data["platforms"]:
        lines.extend([
            f"### {item['label']}（`{item['platform']}`）",
            "",
            f"- 目前狀態：`{item['currentStatus']}`",
            f"- Profile link：{item['profileLink']}",
            "- 設定完成後：",
            f"  - `{item['setCommand']}`",
            "- 已確認公開可點後：",
            f"  - `{item['liveCommand']}`",
            "",
        ])
    lines.extend([
        "## Profile 設定文字匯入",
        "",
        "- 設定平台 profile link 後，可把平台、狀態、日期、profile link 與 proof note 貼成一段文字，再用匯入工具檢查。",
        "- 檢查：`python3 tools/promotion_profile_text_import.py check --input /path/to/profile.txt`",
        "- 寫入：`python3 tools/promotion_profile_text_import.py add --input /path/to/profile.txt --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\"`",
        "- 寫入時仍會驗證平台專屬 `/start/` UTM、同步 readiness 與 next actions。",
        "",
        "## 安全規則",
        "",
        "- 不用本工具偽造 profile link 設定、post URL 或 KPI。",
        "- `set/live` 必須有 `--set-date` 與 `--proof-note`。",
        "- 更新後要重新跑 launch readiness；只有 `ready_to_publish=1` 才發布首批。",
    ])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_playbook(data: dict) -> None:
    PLAYBOOK_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PLAYBOOK_MD.write_text(render_markdown(data), encoding="utf-8")


def regenerate_dependent_docs() -> None:
    promotion_refresh.run_daily_ops_refresh()


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely validate or write back LoveTypes platform profile setup status.")
    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--write-playbook", action="store_true")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--platform", choices=PLATFORMS, required=True)
    update_parser.add_argument("--status", choices=STATUS_VALUES, required=True)
    update_parser.add_argument("--set-date", default="")
    update_parser.add_argument("--proof-note", default="")
    for field in METRIC_FIELDS:
        update_parser.add_argument(f"--{field.replace('_', '-')}", default="")

    args = parser.parse_args()
    if not args.command:
        args.command = "check"
        args.write_playbook = False

    fieldnames, rows = read_rows(TRACKER_PATH)
    if args.command == "update":
        metrics = {field: getattr(args, field) for field in METRIC_FIELDS}
        update_row(rows, args.platform, args.status, args.set_date, args.proof_note.strip(), metrics)
        issues = validate_tracker(fieldnames, rows)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        write_rows(TRACKER_PATH, fieldnames, rows)
        regenerate_dependent_docs()
        fieldnames, rows = read_rows(TRACKER_PATH)

    issues = validate_tracker(fieldnames, rows)
    data = playbook(fieldnames, rows, issues)
    if args.command == "update" or getattr(args, "write_playbook", False):
        write_playbook(data)
        print(f"promotion_profile_writeback_playbook={PLAYBOOK_MD}")
        print(f"promotion_profile_writeback_json={PLAYBOOK_JSON}")
    print(f"promotion_profile_writeback_rows={data['metrics']['rows']}")
    print(f"promotion_profile_writeback_configured={data['metrics']['configured']}")
    print(f"promotion_profile_writeback_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
