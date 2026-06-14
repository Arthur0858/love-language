#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date, timedelta
from pathlib import Path

from promotion_publish_pack import HASHTAGS, caption_for, load_tasks


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
QUEUE_JSON_PATH = PROMOTION_DIR / "posting-queue.json"
PLATFORMS = ["youtube_shorts"]
PLATFORM_TIMES = {
    "youtube_shorts": "20:30",
    "tiktok": "21:00",
    "instagram_reels": "21:30",
}
SLOT_DAY_OFFSETS = {1: 0, 2: 2, 3: 4}
TIMEZONE = "Asia/Taipei"
FIELDNAMES = [
    "week",
    "slot",
    "platform",
    "status",
    "scheduled_date",
    "scheduled_time",
    "timezone",
    "published_date",
    "post_url",
    "task_id",
    "script_id",
    "guardian_id",
    "guardian_name",
    "content_angle",
    "title",
    "caption",
    "tracked_url",
    "utm_content",
    "primary_cta",
    "hashtags",
    "notes",
]
PRESERVE_FIELDS = {"status", "scheduled_date", "scheduled_time", "timezone", "published_date", "post_url", "notes"}


def next_monday(today: date | None = None) -> date:
    today = today or date.today()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    return today + timedelta(days=days_until_monday)


def scheduled_date_for(task: dict, campaign_start: date) -> str:
    week = int(task.get("week", 1) or 1)
    slot = int(task.get("slot", 1) or 1)
    scheduled = campaign_start + timedelta(days=(week - 1) * 7 + SLOT_DAY_OFFSETS.get(slot, 0))
    return scheduled.isoformat()


def read_existing(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {
        (row.get("platform", ""), row.get("task_id", "")): row
        for row in rows
        if row.get("platform") and row.get("task_id")
    }


def platform_caption(task: dict, platform: str) -> str:
    caption = caption_for(task)
    if platform == "youtube_shorts":
        return caption
    return caption


def build_row(task: dict, platform: str, campaign_start: date, existing: dict[str, str] | None = None) -> dict[str, str]:
    existing = existing or {}
    row = {field: "" for field in FIELDNAMES}
    row.update({
        "week": str(task.get("week", "")),
        "slot": str(task.get("slot", "")),
        "platform": platform,
        "status": "planned",
        "scheduled_date": scheduled_date_for(task, campaign_start),
        "scheduled_time": PLATFORM_TIMES[platform],
        "timezone": TIMEZONE,
        "task_id": str(task.get("taskId", "")),
        "script_id": str(task.get("scriptId", "")),
        "guardian_id": str(task.get("guardianId", "")),
        "guardian_name": str(task.get("guardianName", "")),
        "content_angle": str(task.get("contentAngle", "")),
        "title": str(task.get("title", "")),
        "caption": platform_caption(task, platform),
        "tracked_url": str(task.get("trackedUrl", "")),
        "utm_content": str(task.get("utmContent", "")),
        "primary_cta": str(task.get("primaryCta", "完成 15 題測驗，找到你的情感守護者")),
        "hashtags": " ".join(HASHTAGS),
        "notes": str(task.get("notes", "")),
    })
    for field in PRESERVE_FIELDS:
        if existing.get(field):
            row[field] = existing[field]
    return row


def build_rows(tasks: list[dict], existing: dict[tuple[str, str], dict[str, str]], campaign_start: date) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    sorted_tasks = sorted(tasks, key=lambda task: (int(task.get("week", 0) or 0), int(task.get("slot", 0) or 0)))
    for task in sorted_tasks:
        for platform in PLATFORMS:
            rows.append(build_row(task, platform, campaign_start, existing.get((platform, str(task.get("taskId", ""))))))
    return rows


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    expected_rows = 15 * len(PLATFORMS)
    if len(rows) != expected_rows:
        issues.append(f"expected {expected_rows} posting rows, got {len(rows)}")
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row.get("platform", ""), row.get("task_id", ""))
        if key in seen:
            issues.append(f"duplicate posting queue row {key[0]} {key[1]}")
        seen.add(key)
        for field in ("week", "slot", "platform", "status", "scheduled_date", "scheduled_time", "timezone", "task_id", "script_id", "guardian_id", "title", "caption", "tracked_url", "utm_content"):
            if not row.get(field):
                issues.append(f"{key[0]} {key[1]}: missing {field}")
        if row.get("tracked_url") and f"utm_content={row.get('utm_content')}" not in row["tracked_url"]:
            issues.append(f"{key[0]} {key[1]}: tracked_url should contain matching utm_content")
        if "診斷" in row.get("caption", "") or "保證修復" in row.get("caption", ""):
            issues.append(f"{key[0]} {key[1]}: caption should not imply diagnosis or guaranteed repair")
    return issues


def write_outputs(rows: list[dict[str, str]], csv_path: Path, json_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "generatedAt": date.today().isoformat(),
        "platforms": PLATFORMS,
        "timezone": TIMEZONE,
        "rowCount": len(rows),
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync LoveTypes cross-platform posting queue from promotion tasks.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--output", default=str(QUEUE_PATH))
    parser.add_argument("--json-output", default=str(QUEUE_JSON_PATH))
    parser.add_argument("--start-date", default="", help="Campaign week-1 Monday in YYYY-MM-DD. Defaults to next Monday.")
    parser.add_argument("--check", action="store_true", help="Validate the posting queue shape without writing files.")
    args = parser.parse_args()

    campaign_start = date.fromisoformat(args.start_date) if args.start_date else next_monday()
    rows = build_rows(load_tasks(Path(args.kit)), read_existing(Path(args.output)), campaign_start)
    issues = validate_rows(rows)
    if args.check:
        print(f"promotion_posting_queue_platforms={len(PLATFORMS)}")
        print(f"promotion_posting_queue_rows={len(rows)}")
        print(f"promotion_posting_queue_start_date={campaign_start.isoformat()}")
        print(f"promotion_posting_queue_issues={len(issues)}")
        for issue in issues:
            print(issue)
        return 1 if issues else 0
    if issues:
        for issue in issues:
            print(issue)
        return 1
    write_outputs(rows, Path(args.output), Path(args.json_output))
    print(f"promotion_posting_queue={args.output}")
    print(f"promotion_posting_queue_json={args.json_output}")
    print(f"promotion_posting_queue_rows={len(rows)}")
    print(f"promotion_posting_queue_start_date={campaign_start.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
