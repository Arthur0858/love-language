#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from promotion_proof_note_policy import proof_note_issue


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
PLATFORM_TRACKER_PATH = PROMOTION_DIR / "platform-kpi-tracker.csv"
SCRIPT_TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PLAYBOOK_MD = PROMOTION_DIR / "post-writeback-playbook.md"
PLAYBOOK_JSON = PROMOTION_DIR / "post-writeback-playbook.json"
PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
PUBLISH_STATUSES = ("published", "live", "posted")
STATUS_VALUES = ("planned", "scheduled", *PUBLISH_STATUSES)
PLATFORM_DOMAINS = {
    "youtube_shorts": ("youtube.com", "youtu.be"),
    "tiktok": ("tiktok.com",),
    "instagram_reels": ("instagram.com",),
}
POST_URL_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}
METRIC_FIELDS = (
    "views",
    "likes",
    "comments",
    "shares",
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


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    return int(float(text))


def validate_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def valid_post_url(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    lowered = value.strip().lower()
    placeholder_tokens = ("example.com", "placeholder", "replace-with-real", "replace_with_real")
    return not any(token in lowered for token in placeholder_tokens)


def post_url_matches_platform(platform: str, value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    host = parsed.netloc.lower().removeprefix("www.")
    return any(host == domain or host.endswith("." + domain) for domain in PLATFORM_DOMAINS.get(platform, ()))


def post_url_placeholder(platform: str) -> str:
    return POST_URL_PLACEHOLDERS.get(platform, "<REAL_POST_URL>")


def key(row: dict[str, str]) -> tuple[str, str]:
    return ((row.get("platform") or "").strip(), (row.get("task_id") or "").strip())


def validate_rows(
    queue_fields: list[str],
    queue_rows: list[dict[str, str]],
    platform_fields: list[str],
    platform_rows: list[dict[str, str]],
    script_fields: list[str],
    script_rows: list[dict[str, str]],
) -> list[str]:
    issues: list[str] = []
    required_queue = {"platform", "status", "published_date", "post_url", "task_id", "script_id", "notes"}
    required_platform = {"platform", "status", "published_date", "post_url", "task_id", "script_id", "notes", *METRIC_FIELDS}
    required_script = {"date", "platform", "post_url", "script_id", "notes", *METRIC_FIELDS}
    for label, fields, required in (
        ("posting queue", queue_fields, required_queue),
        ("platform KPI tracker", platform_fields, required_platform),
        ("script KPI tracker", script_fields, required_script),
    ):
        missing = sorted(required - set(fields))
        if missing:
            issues.append(f"{label} missing fields: {', '.join(missing)}")
    platform_lookup = {key(row): row for row in platform_rows}
    script_lookup = {row.get("script_id", ""): row for row in script_rows if row.get("script_id")}
    for row in queue_rows:
        platform, task_id = key(row)
        label = f"{platform or '<platform>'}/{task_id or '<task>'}"
        if platform not in PLATFORMS:
            issues.append(f"{label}: invalid platform")
            continue
        status = (row.get("status") or "planned").strip()
        if status not in STATUS_VALUES:
            issues.append(f"{label}: invalid status {status}")
        if status in PUBLISH_STATUSES:
            if not validate_date(row.get("published_date", "")):
                issues.append(f"{label}: published row requires published_date YYYY-MM-DD")
            if not valid_post_url(row.get("post_url", "")):
                issues.append(f"{label}: published row requires non-placeholder https post_url")
            elif not post_url_matches_platform(platform, row.get("post_url", "")):
                issues.append(f"{label}: published row post_url must match platform domain")
            if "verified:" not in (row.get("notes") or ""):
                issues.append(f"{label}: published row requires verified proof note")
            platform_row = platform_lookup.get((platform, task_id), {})
            if platform_row.get("published_date") != row.get("published_date") or platform_row.get("post_url") != row.get("post_url"):
                issues.append(f"{label}: platform KPI tracker publish fields must match posting queue")
            script_row = script_lookup.get(row.get("script_id", ""), {})
            if not all((script_row.get(field) or "").strip() for field in ("date", "platform", "post_url")):
                issues.append(f"{label}: script KPI tracker missing date/platform/post_url for published script")
        platform_row = platform_lookup.get((platform, task_id))
        if not platform_row:
            issues.append(f"{label}: missing platform KPI tracker row")
            continue
        for field in METRIC_FIELDS:
            for source_name, source_row in (("queue", row), ("platform KPI", platform_row)):
                value = (source_row.get(field) or "").strip()
                if not value:
                    continue
                try:
                    parsed = parse_int(value)
                except ValueError:
                    issues.append(f"{label}: {source_name} {field} must be numeric")
                    continue
                if parsed < 0:
                    issues.append(f"{label}: {source_name} {field} must not be negative")
    return issues


def append_note(row: dict[str, str], proof_note: str, proof_date: str) -> None:
    parts = [row.get("notes", "").strip(), f"verified:{proof_date} {proof_note}"]
    row["notes"] = " | ".join(part for part in parts if part)


def update_platform_rows(
    rows: list[dict[str, str]],
    platform: str,
    task_id: str,
    status: str,
    published_date: str,
    post_url: str,
    proof_note: str,
    metrics: dict[str, str],
) -> dict[str, str]:
    for row in rows:
        if key(row) != (platform, task_id):
            continue
        row["status"] = status
        row["published_date"] = published_date
        row["post_url"] = post_url
        for field, value in metrics.items():
            if value != "" and field in row:
                row[field] = str(parse_int(value))
        append_note(row, proof_note, published_date)
        return row
    raise SystemExit(f"row not found: {platform}/{task_id}")


def rollup_script_tracker(script_rows: list[dict[str, str]], platform_rows: list[dict[str, str]], script_id: str) -> None:
    published = [
        row for row in platform_rows
        if row.get("script_id") == script_id and row.get("status") in PUBLISH_STATUSES and row.get("post_url")
    ]
    if not published:
        return
    published.sort(key=lambda row: (row.get("published_date") or "9999-99-99", PLATFORMS.index(row["platform"]) if row.get("platform") in PLATFORMS else 99))
    first = published[0]
    for row in script_rows:
        if row.get("script_id") != script_id:
            continue
        row["date"] = first.get("published_date", "")
        row["platform"] = ",".join(sorted({item.get("platform", "") for item in published if item.get("platform")}))
        row["post_url"] = first.get("post_url", "")
        for field in METRIC_FIELDS:
            if field in row:
                total = sum(parse_int(item.get(field)) for item in published)
                row[field] = str(total) if total else row.get(field, "")
        if "verified:" not in (row.get("notes") or ""):
            append_note(row, f"script rollup from {len(published)} platform post(s)", first.get("published_date", date.today().isoformat()))
        return
    raise SystemExit(f"script not found in KPI tracker: {script_id}")


def first_batch_commands(queue_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = [
        row for row in queue_rows
        if row.get("week") == "1" and row.get("slot") == "1"
    ]
    order = {platform: index for index, platform in enumerate(PLATFORMS)}
    rows.sort(key=lambda row: order.get(row.get("platform", ""), 99))
    commands = []
    for row in rows:
        platform = row["platform"]
        task_id = row["task_id"]
        commands.append({
            "platform": platform,
            "taskId": task_id,
            "scriptId": row.get("script_id", ""),
            "title": row.get("title", ""),
            "currentStatus": row.get("status", "planned"),
            "publishCommand": (
                f"python3 tools/promotion_post_writeback.py update --platform {platform} --task-id {task_id} "
                f"--status published --published-date {date.today().isoformat()} --post-url {post_url_placeholder(platform)} "
                f"--proof-note \"public URL post checked {date.today().isoformat()}\""
            ),
        })
    return commands


def build_playbook(queue_rows: list[dict[str, str]], issues: list[str]) -> dict:
    published = sum(1 for row in queue_rows if row.get("status") in PUBLISH_STATUSES)
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "postingQueue": str(QUEUE_PATH.relative_to(ROOT)),
            "platformKpiTracker": str(PLATFORM_TRACKER_PATH.relative_to(ROOT)),
            "scriptKpiTracker": str(SCRIPT_TRACKER_PATH.relative_to(ROOT)),
        },
        "metrics": {
            "queueRows": len(queue_rows),
            "publishedRows": published,
            "issues": len(issues),
        },
        "firstBatch": first_batch_commands(queue_rows),
        "policy": {
            "doNotFake": True,
            "publishedRequires": ["published_date", "https post_url", "verified proof note"],
            "syncTargets": ["posting-queue.csv", "platform-kpi-tracker.csv", "kpi-tracker.csv", "publishing-status"],
            "minimumKpis": ["site_clicks", "quiz_starts", "quiz_completions"],
        },
        "issues": issues,
    }


def render_markdown(data: dict) -> str:
    lines = [
        "# LoveTypes Post Writeback Playbook",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- 已發布列：{data['metrics']['publishedRows']} / {data['metrics']['queueRows']}",
        f"- issues：{data['metrics']['issues']}",
        "- 原則：只有平台貼文已公開且 post URL 可驗證時，才能標記 published/live/posted。",
        "",
        "## 首批回填命令",
        "",
    ]
    for item in data["firstBatch"]:
        lines.extend([
            f"### {item['platform']} · `{item['taskId']}`",
            "",
            f"- script：`{item['scriptId']}`",
            f"- 標題：{item['title']}",
            f"- 目前狀態：`{item['currentStatus']}`",
            f"- 回填：`{item['publishCommand']}`",
            "",
        ])
    lines.extend([
        "## 平台文字匯入",
        "",
        "- 發布後可把平台、task_id、post_url、發布日期與初始 KPI 貼成一段文字，再用匯入工具檢查。",
        "- 檢查：`python3 tools/promotion_post_text_import.py check --input /path/to/post.txt`",
        "- 寫入：`python3 tools/promotion_post_text_import.py add --input /path/to/post.txt --proof-note \"public URL post checked YYYY-MM-DD\"`",
        "- 寫入時仍會同步 posting queue、platform KPI tracker、script KPI tracker 與後續摘要文件。",
        "",
        "## 安全規則",
        "",
        "- 不用本工具偽造 post URL、發布日期或 KPI。",
        "- `published/live/posted` 必須有 `--published-date`、`--post-url`、`--proof-note`。",
        "- 發布後先回填 `site_clicks`、`quiz_starts`、`quiz_completions`；沒有數據時保留空白，不做商品判斷。",
    ])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_playbook(data: dict) -> None:
    PLAYBOOK_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PLAYBOOK_MD.write_text(render_markdown(data), encoding="utf-8")


def regenerate_dependent_docs() -> None:
    commands = [
        [sys.executable, "tools/promotion_platform_kpi_tracker.py"],
        [sys.executable, "tools/promotion_sync_kpi_tracker.py"],
        [sys.executable, "tools/promotion_publishing_status.py"],
        [sys.executable, "tools/promotion_launch_readiness_gate.py"],
        [sys.executable, "tools/promotion_next_actions.py"],
        [sys.executable, "tools/promotion_weekly_summary.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely validate or write back LoveTypes platform post publication data.")
    subparsers = parser.add_subparsers(dest="command")
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--write-playbook", action="store_true")
    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--platform", choices=PLATFORMS, required=True)
    update_parser.add_argument("--task-id", required=True)
    update_parser.add_argument("--status", choices=STATUS_VALUES, required=True)
    update_parser.add_argument("--published-date", default="")
    update_parser.add_argument("--post-url", default="")
    update_parser.add_argument("--proof-note", default="")
    for field in METRIC_FIELDS:
        update_parser.add_argument(f"--{field.replace('_', '-')}", default="")

    args = parser.parse_args()
    if not args.command:
        args.command = "check"
        args.write_playbook = False

    queue_fields, queue_rows = read_csv(QUEUE_PATH)
    platform_fields, platform_rows = read_csv(PLATFORM_TRACKER_PATH)
    script_fields, script_rows = read_csv(SCRIPT_TRACKER_PATH)

    if args.command == "update":
        if args.status in PUBLISH_STATUSES:
            if not args.published_date or not validate_date(args.published_date):
                raise SystemExit("published/live/posted updates require --published-date YYYY-MM-DD")
            if not valid_post_url(args.post_url):
                raise SystemExit("published/live/posted updates require --post-url with https URL")
            if not args.proof_note.strip():
                raise SystemExit("published/live/posted updates require --proof-note with verification evidence")
            issue = proof_note_issue(args.proof_note)
            if issue:
                raise SystemExit(issue)
        metrics = {field: getattr(args, field) for field in METRIC_FIELDS}
        queue_row = update_platform_rows(queue_rows, args.platform, args.task_id, args.status, args.published_date, args.post_url, args.proof_note.strip(), metrics)
        update_platform_rows(platform_rows, args.platform, args.task_id, args.status, args.published_date, args.post_url, args.proof_note.strip(), metrics)
        rollup_script_tracker(script_rows, platform_rows, queue_row["script_id"])
        issues = validate_rows(queue_fields, queue_rows, platform_fields, platform_rows, script_fields, script_rows)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        write_csv(QUEUE_PATH, queue_fields, queue_rows)
        write_csv(PLATFORM_TRACKER_PATH, platform_fields, platform_rows)
        write_csv(SCRIPT_TRACKER_PATH, script_fields, script_rows)
        regenerate_dependent_docs()
        queue_fields, queue_rows = read_csv(QUEUE_PATH)
        platform_fields, platform_rows = read_csv(PLATFORM_TRACKER_PATH)
        script_fields, script_rows = read_csv(SCRIPT_TRACKER_PATH)

    issues = validate_rows(queue_fields, queue_rows, platform_fields, platform_rows, script_fields, script_rows)
    data = build_playbook(queue_rows, issues)
    if args.command == "update" or getattr(args, "write_playbook", False):
        write_playbook(data)
        print(f"promotion_post_writeback_playbook={PLAYBOOK_MD}")
        print(f"promotion_post_writeback_json={PLAYBOOK_JSON}")
    print(f"promotion_post_writeback_queue_rows={data['metrics']['queueRows']}")
    print(f"promotion_post_writeback_published_rows={data['metrics']['publishedRows']}")
    print(f"promotion_post_writeback_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
