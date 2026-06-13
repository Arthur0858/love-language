#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import promotion_post_writeback as writeback


SAMPLE_TEXT = """LoveTypes platform post writeback
platform: youtube_shorts
task_id: publish-lt-s01-iris-silence
status: published
published_date: 2026-06-15
post_url: https://www.youtube.com/shorts/lovetypes-proof-url-123
views: 0
site_clicks: 0
quiz_starts: 0
quiz_completions: 0
proof_note: public URL and analytics source checked 2026-06-15
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
    "task": "task_id",
    "task id": "task_id",
    "task_id": "task_id",
    "任務": "task_id",
    "status": "status",
    "狀態": "status",
    "published date": "published_date",
    "published_date": "published_date",
    "date": "published_date",
    "發布日期": "published_date",
    "post url": "post_url",
    "post_url": "post_url",
    "url": "post_url",
    "貼文網址": "post_url",
    "proof": "proof_note",
    "proof note": "proof_note",
    "proof_note": "proof_note",
    "驗證": "proof_note",
}
for metric in writeback.METRIC_FIELDS:
    KEY_ALIASES[metric] = metric
    KEY_ALIASES[metric.replace("_", " ")] = metric


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
    data.setdefault("status", "published")

    for field in ("platform", "task_id", "status", "published_date", "post_url"):
        if not data.get(field):
            issues.append(f"missing {field}")
    if data.get("platform") not in writeback.PLATFORMS:
        issues.append(f"invalid platform {data.get('platform')!r}")
    if data.get("status") not in writeback.STATUS_VALUES:
        issues.append(f"invalid status {data.get('status')!r}")
    if data.get("status") in writeback.PUBLISH_STATUSES:
        if not writeback.validate_date(data.get("published_date", "")):
            issues.append("published status requires published_date YYYY-MM-DD")
        if not writeback.valid_post_url(data.get("post_url", "")):
            issues.append("published status requires non-placeholder https post_url")
        elif not writeback.post_url_matches_platform(data.get("platform", ""), data.get("post_url", "")):
            issues.append("published status requires post_url to match platform domain")
        proof = data.get("proof_note", "")
        zero_issue = writeback.zero_metric_source_issue(proof, data)
        if zero_issue:
            issues.append(zero_issue)
    if data.get("task_id") and not task_exists(data.get("platform", ""), data["task_id"]):
        issues.append(f"unknown platform/task_id {data.get('platform')}/{data.get('task_id')}")
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


def task_exists(platform: str, task_id: str) -> bool:
    _, queue_rows = writeback.read_csv(writeback.QUEUE_PATH)
    return any(row.get("platform") == platform and row.get("task_id") == task_id for row in queue_rows)


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def add_post(data: dict[str, str], proof_note: str) -> None:
    queue_fields, queue_rows = writeback.read_csv(writeback.QUEUE_PATH)
    platform_fields, platform_rows = writeback.read_csv(writeback.PLATFORM_TRACKER_PATH)
    script_fields, script_rows = writeback.read_csv(writeback.SCRIPT_TRACKER_PATH)
    proof = proof_note or data.get("proof_note", "")
    if data["status"] in writeback.PUBLISH_STATUSES and not proof.strip():
        raise SystemExit("published/live/posted import requires --proof-note or proof_note in input")
    metrics = {field: data.get(field, "") for field in writeback.METRIC_FIELDS}
    queue_row = writeback.update_platform_rows(
        queue_rows,
        data["platform"],
        data["task_id"],
        data["status"],
        data["published_date"],
        data["post_url"],
        proof.strip(),
        metrics,
    )
    writeback.update_platform_rows(
        platform_rows,
        data["platform"],
        data["task_id"],
        data["status"],
        data["published_date"],
        data["post_url"],
        proof.strip(),
        metrics,
    )
    writeback.rollup_script_tracker(script_rows, platform_rows, queue_row["script_id"])
    issues = writeback.validate_rows(queue_fields, queue_rows, platform_fields, platform_rows, script_fields, script_rows)
    if issues:
        raise SystemExit("\n".join(issues))
    writeback.write_csv(writeback.QUEUE_PATH, queue_fields, queue_rows)
    writeback.write_csv(writeback.PLATFORM_TRACKER_PATH, platform_fields, platform_rows)
    writeback.write_csv(writeback.SCRIPT_TRACKER_PATH, script_fields, script_rows)
    writeback.regenerate_dependent_docs()
    _, refreshed = writeback.read_csv(writeback.QUEUE_PATH)
    data_for_playbook = writeback.build_playbook(refreshed, [])
    writeback.write_playbook(data_for_playbook)


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse copied platform post/KPI text into safe LoveTypes post writeback fields.")
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
    print(f"promotion_post_text_import_fields_parsed={len(data)}")
    print(f"promotion_post_text_import_platform={data.get('platform', '')}")
    print(f"promotion_post_text_import_task_id={data.get('task_id', '')}")
    print(f"promotion_post_text_import_status={data.get('status', '')}")
    print(f"promotion_post_text_import_has_post_url={1 if data.get('post_url') else 0}")
    print(f"promotion_post_text_import_metric_fields_present={sum(1 for field in writeback.METRIC_FIELDS if data.get(field))}")
    if command == "add" and not issues:
        add_post(data, args.proof_note)
        print("promotion_post_text_import_writeback=1")
    print(f"promotion_post_text_import_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
