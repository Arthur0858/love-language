#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import promotion_profile_writeback as writeback


TODAY = date.today().isoformat()
SAMPLE_TEXT = f"""LoveTypes profile setup writeback
platform: youtube_shorts
status: set
set_date: {TODAY}
profile_link: https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio
proof_note: screenshot profile-youtube_shorts-{TODAY}.png verified
"""

PLATFORM_ALIASES = {
    "youtube": "youtube_shorts",
    "youtube shorts": "youtube_shorts",
    "youtube_shorts": "youtube_shorts",
    "shorts": "youtube_shorts",
    "tiktok": "tiktok",
    "tik tok": "tiktok",
    "instagram": "instagram_reels",
    "instagram reels": "instagram_reels",
    "instagram_reels": "instagram_reels",
    "reels": "instagram_reels",
}
KEY_ALIASES = {
    "platform": "platform",
    "平台": "platform",
    "status": "status",
    "狀態": "status",
    "set date": "set_date",
    "set_date": "set_date",
    "date": "set_date",
    "設定日期": "set_date",
    "profile link": "profile_link",
    "profile_link": "profile_link",
    "link": "profile_link",
    "個人頁連結": "profile_link",
    "proof": "proof_note",
    "proof note": "proof_note",
    "proof_note": "proof_note",
    "驗證": "proof_note",
}
for metric in writeback.METRIC_FIELDS:
    KEY_ALIASES[metric] = metric
    KEY_ALIASES[metric.replace("_", " ")] = metric


SCAFFOLD_PROOF_RE = re.compile(r"^screenshot\s+profile-(youtube_shorts|tiktok|instagram_reels)-20\d{2}-\d{2}-\d{2}\.png\s+verified$", re.IGNORECASE)


def normalize_key(value: str) -> str:
    return " ".join(value.strip().lower().replace("：", ":").replace("-", "_").split())


def split_line(line: str) -> tuple[str, str] | None:
    normalized = line.replace("：", ":", 1)
    if ":" not in normalized:
        return None
    key, value = normalized.split(":", 1)
    return key.strip(), value.strip()


def resolve_platform(value: str) -> str:
    normalized = " ".join(value.strip().lower().replace("-", " ").replace("_", " ").split())
    return PLATFORM_ALIASES.get(value.strip().lower()) or PLATFORM_ALIASES.get(normalized) or value.strip()


def parse_text(text: str) -> tuple[dict[str, str], list[str]]:
    data: dict[str, str] = {}
    issues: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        split = split_line(line)
        if not split:
            continue
        key, value = split
        canonical = KEY_ALIASES.get(normalize_key(key))
        if canonical:
            data[canonical] = value

    if data.get("platform"):
        data["platform"] = resolve_platform(data["platform"])
    data.setdefault("status", "set")

    for field in ("platform", "status", "set_date", "profile_link"):
        if not data.get(field):
            issues.append(f"missing {field}")
    platform = data.get("platform", "")
    if platform not in writeback.PLATFORMS:
        issues.append(f"invalid platform {platform!r}")
    if data.get("status") not in writeback.STATUS_VALUES:
        issues.append(f"invalid status {data.get('status')!r}")
    if data.get("status") in writeback.CONFIGURED_STATUSES:
        if not writeback.validate_date(data.get("set_date", "")):
            issues.append("set/live status requires set_date YYYY-MM-DD")
        if platform in writeback.PLATFORMS and not writeback.is_start_campaign_url(platform, data.get("profile_link", "")):
            issues.append("profile_link must be the platform-specific /start/ campaign URL")
    for field in writeback.METRIC_FIELDS:
        value = (data.get(field) or "").strip()
        if not value:
            continue
        try:
            parsed = writeback.parse_int(value)
        except ValueError:
            issues.append(f"{field} must be numeric")
            continue
        if parsed < 0:
            issues.append(f"{field} must not be negative")
    return data, issues


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def scaffold_proof_issue(proof: str) -> str:
    if SCAFFOLD_PROOF_RE.match(" ".join((proof or "").strip().split())):
        return (
            "profile proof_note still looks like the scaffold screenshot filename; "
            "replace it with real evidence such as an actual screenshot filename, "
            "public profile URL click note, screen recording filename, or platform URL"
        )
    return ""


def add_profile(data: dict[str, str], proof_note: str) -> None:
    fieldnames, rows = writeback.read_rows(writeback.TRACKER_PATH)
    proof = proof_note or data.get("proof_note", "")
    if data["status"] in writeback.CONFIGURED_STATUSES and not proof.strip():
        raise SystemExit("set/live import requires --proof-note or proof_note in input")
    issue = scaffold_proof_issue(proof)
    if issue:
        raise SystemExit(issue)
    metrics = {field: data.get(field, "") for field in writeback.METRIC_FIELDS}
    writeback.update_row(rows, data["platform"], data["status"], data["set_date"], proof.strip(), metrics)
    issues = writeback.validate_tracker(fieldnames, rows)
    if issues:
        raise SystemExit("\n".join(issues))
    writeback.write_rows(writeback.TRACKER_PATH, fieldnames, rows)
    writeback.regenerate_dependent_docs()
    _, refreshed = writeback.read_rows(writeback.TRACKER_PATH)
    writeback.write_playbook(writeback.playbook(fieldnames, refreshed, []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse copied profile setup proof text into safe LoveTypes profile writeback fields.")
    subparsers = parser.add_subparsers(dest="command")
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--input", default="", help="Optional text file to validate instead of the built-in sample.")
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--input", required=True, help="Text file path, or - for stdin.")
    add_parser.add_argument("--proof-note", default="", help="Short verification note if the text does not contain proof_note.")
    args = parser.parse_args()
    command = args.command or "check"
    text = read_input(args.input) if getattr(args, "input", "") else SAMPLE_TEXT
    data, issues = parse_text(text)
    print(f"promotion_profile_text_import_fields_parsed={len(data)}")
    print(f"promotion_profile_text_import_platform={data.get('platform', '')}")
    print(f"promotion_profile_text_import_status={data.get('status', '')}")
    print(f"promotion_profile_text_import_has_profile_link={1 if data.get('profile_link') else 0}")
    print(f"promotion_profile_text_import_metric_fields_present={sum(1 for field in writeback.METRIC_FIELDS if data.get(field))}")
    if command == "add" and not issues:
        add_profile(data, args.proof_note)
        print("promotion_profile_text_import_writeback=1")
    print(f"promotion_profile_text_import_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
