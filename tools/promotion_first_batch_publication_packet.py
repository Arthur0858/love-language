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
QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
PLATFORM_TRACKER_PATH = PROMOTION_DIR / "platform-kpi-tracker.csv"
PUBLISHING_STATUS_PATH = PROMOTION_DIR / "publishing-status.json"
READINESS_PATH = PROMOTION_DIR / "launch-readiness-gate.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "first-batch-publication-packet.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
PLATFORM_ORDER = ("youtube_shorts", "tiktok", "instagram_reels")
PUBLISHED_STATUSES = {"published", "live", "posted"}
POST_URL_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}
MINIMUM_KPI_FIELDS = ("site_clicks", "quiz_starts", "quiz_completions")
FOLLOWUP_KPI_FIELDS = (
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    return int(float(text))


def valid_tracked_url(value: str, expected_utm_content: str) -> list[str]:
    issues: list[str] = []
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    expected = {
        "utm_source": "shorts",
        "utm_medium": "social",
        "utm_campaign": "first_round_quiz_completion",
        "utm_content": expected_utm_content,
    }
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
        issues.append("tracked URL must point to https://lovetypes.tw/start/")
    for key, expected_value in expected.items():
        if query.get(key, [""])[0] != expected_value:
            issues.append(f"tracked URL missing {key}={expected_value}")
    return issues


def queue_key(row: dict[str, str]) -> tuple[str, str]:
    return ((row.get("platform") or "").strip(), (row.get("task_id") or "").strip())


def first_batch_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    batch = [row for row in rows if row.get("week") == "1" and row.get("slot") == "1"]
    order = {platform: index for index, platform in enumerate(PLATFORM_ORDER)}
    return sorted(batch, key=lambda row: order.get(row.get("platform", ""), 99))


def platform_tracker_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {queue_key(row): row for row in rows}


def post_url_placeholder(platform: str) -> str:
    return POST_URL_PLACEHOLDERS.get(platform, "<REAL_POST_URL>")


def build_packet() -> dict:
    queue_rows = read_csv(QUEUE_PATH)
    platform_rows = read_csv(PLATFORM_TRACKER_PATH)
    platform_lookup = platform_tracker_lookup(platform_rows)
    publishing_status = load_json(PUBLISHING_STATUS_PATH)
    readiness = load_json(READINESS_PATH)
    readiness_state = readiness.get("readiness", {}) if isinstance(readiness.get("readiness"), dict) else {}
    rows = []
    for row in first_batch_rows(queue_rows):
        platform = row.get("platform", "")
        task_id = row.get("task_id", "")
        tracker = platform_lookup.get((platform, task_id), {})
        status = row.get("status", "planned")
        published = status in PUBLISHED_STATUSES
        minimum_kpis = {field: parse_int(tracker.get(field) or row.get(field)) for field in MINIMUM_KPI_FIELDS}
        placeholder = post_url_placeholder(platform)
        rows.append({
            "platform": platform,
            "taskId": task_id,
            "scriptId": row.get("script_id", ""),
            "guardianId": row.get("guardian_id", ""),
            "guardianName": row.get("guardian_name", ""),
            "title": row.get("title", ""),
            "status": status,
            "scheduledDate": row.get("scheduled_date", ""),
            "scheduledTime": row.get("scheduled_time", ""),
            "published": published,
            "publishedDate": row.get("published_date", ""),
            "postUrl": row.get("post_url", ""),
            "trackedUrl": row.get("tracked_url", ""),
            "utmContent": row.get("utm_content", ""),
            "caption": row.get("caption", ""),
            "primaryCta": row.get("primary_cta", ""),
            "minimumKpis": minimum_kpis,
            "minimumKpiFilled": any(value > 0 for value in minimum_kpis.values()),
            "writebackCommand": (
                f"python3 tools/promotion_post_writeback.py update --platform {platform} --task-id {task_id} "
                f"--status published --published-date {date.today().isoformat()} --post-url {placeholder} "
                f"--proof-note \"public URL post checked {date.today().isoformat()}\""
            ),
            "kpiExampleCommand": (
                f"python3 tools/promotion_post_writeback.py update --platform {platform} --task-id {task_id} "
                f"--status published --published-date {date.today().isoformat()} --post-url {placeholder} "
                "--site-clicks 0 --quiz-starts 0 --quiz-completions 0 "
                f"--proof-note \"platform analytics checked {date.today().isoformat()}\""
            ),
            "postUrlPlaceholder": placeholder,
            "prePublishChecks": [
                "Profile link 已完成 set/live，且 launch readiness ready_to_publish=1。",
                "影片、字幕、首幀或封面使用正確守護者宇宙，不交換角色設定。",
                "Caption 保留單一 CTA：完成 15 題測驗，找到你的情感守護者。",
                "Tracked URL 指向 /start/ 且保留 utm_content。",
                "不加入 Luna、聯盟書卷或付費商品作為第一 CTA。",
            ],
            "postPublishChecks": [
                "貼文公開 URL 是 https URL，且可以在無登入狀態開啟或至少可從平台公開頁驗證。",
                "回填 published_date、post_url、proof_note。",
                "有平台數據後才回填 site_clicks、quiz_starts、quiz_completions。",
                "週回顧前確認 platform-kpi-tracker 與 kpi-tracker 已同步。",
            ],
        })
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "postingQueue": str(QUEUE_PATH.relative_to(ROOT)),
            "platformKpiTracker": str(PLATFORM_TRACKER_PATH.relative_to(ROOT)),
            "publishingStatus": str(PUBLISHING_STATUS_PATH.relative_to(ROOT)),
            "readiness": str(READINESS_PATH.relative_to(ROOT)),
        },
        "week": 1,
        "slot": 1,
        "rowCount": len(rows),
        "publishedRows": sum(1 for row in rows if row["published"]),
        "pendingRows": sum(1 for row in rows if not row["published"]),
        "minimumKpiRows": sum(1 for row in rows if row["minimumKpiFilled"]),
        "readyToPublish": bool(readiness_state.get("readyToPublishPosts")),
        "publishingReadyForWeeklyDecision": bool(publishing_status.get("readyForWeeklyDecision")),
        "minimumKpiFields": list(MINIMUM_KPI_FIELDS),
        "followupKpiFields": list(FOLLOWUP_KPI_FIELDS),
        "rows": rows,
        "policy": {
            "doNotFake": True,
            "publishedRequires": ["published_date", "https post_url", "verified proof note"],
            "emptyDataBoundary": "If first batch has no post URLs or KPI rows, keep offer order, paid CTA, Luna emphasis, and affiliate emphasis unchanged.",
            "firstBatchGoal": "Publish the first Iris script across three platforms, then measure quiz starts and quiz completions before revenue decisions.",
        },
    }


def validate_packet(packet: dict) -> list[str]:
    issues: list[str] = []
    rows = packet.get("rows", [])
    if packet.get("rowCount") != 3:
        issues.append(f"expected 3 first batch rows, got {packet.get('rowCount')}")
    platforms = [row.get("platform", "") for row in rows]
    if platforms != list(PLATFORM_ORDER):
        issues.append("first batch rows should be ordered youtube_shorts, tiktok, instagram_reels")
    for row in rows:
        label = f"{row.get('platform', '<platform>')}/{row.get('taskId', '<task>')}"
        if row.get("guardianId") != "iris":
            issues.append(f"{label}: first batch should be Iris")
        if row.get("scriptId") != "lt-s01-iris-silence":
            issues.append(f"{label}: first batch should use lt-s01-iris-silence")
        if row.get("primaryCta") and "完成 15 題測驗" not in row.get("primaryCta", ""):
            issues.append(f"{label}: primary CTA should stay on quiz completion")
        if "完成 15 題測驗" not in row.get("caption", ""):
            issues.append(f"{label}: caption missing quiz CTA")
        for issue in valid_tracked_url(row.get("trackedUrl", ""), row.get("utmContent", "")):
            issues.append(f"{label}: {issue}")
        if len(row.get("prePublishChecks", [])) < 5:
            issues.append(f"{label}: missing pre-publish checks")
        if len(row.get("postPublishChecks", [])) < 4:
            issues.append(f"{label}: missing post-publish checks")
        if "--proof-note" not in row.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command must require proof note")
        placeholder = row.get("postUrlPlaceholder", "")
        if row.get("platform") in POST_URL_PLACEHOLDERS and placeholder != POST_URL_PLACEHOLDERS[row.get("platform", "")]:
            issues.append(f"{label}: post URL placeholder should be platform-specific")
        if "replace-with-real" in row.get("writebackCommand", "") or "example.com" in row.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command should not contain URL-like placeholders")
        if row.get("published"):
            if not row.get("publishedDate"):
                issues.append(f"{label}: published row missing publishedDate")
            parsed = urlparse(row.get("postUrl", ""))
            if parsed.scheme != "https" or not parsed.netloc:
                issues.append(f"{label}: published row missing https postUrl")
    if packet.get("publishedRows", 0) == 0 and packet.get("publishingReadyForWeeklyDecision"):
        issues.append("weekly decision should not be ready without published first-batch rows")
    if set(packet.get("minimumKpiFields", [])) != set(MINIMUM_KPI_FIELDS):
        issues.append("minimum KPI fields do not match policy")
    return issues


def render_markdown(packet: dict, issues: list[str]) -> str:
    lines = [
        "# LoveTypes First Batch Publication Packet",
        "",
        f"- 產生日期：{packet['generatedAt']}",
        f"- week / slot：{packet['week']} / {packet['slot']}",
        f"- rows：{packet['rowCount']}",
        f"- published：{packet['publishedRows']}",
        f"- pending：{packet['pendingRows']}",
        f"- rows with minimum KPI：{packet['minimumKpiRows']}",
        f"- ready_to_publish：{1 if packet['readyToPublish'] else 0}",
        f"- weekly_decision_ready：{1 if packet['publishingReadyForWeeklyDecision'] else 0}",
        f"- issues：{len(issues)}",
        "",
        "## Gate",
        "",
        f"- {packet['policy']['firstBatchGoal']}",
        f"- {packet['policy']['emptyDataBoundary']}",
        "- 不用本文件偽造 post URL、發布日期或 KPI；只有貼文公開後才回填。",
        "",
        "## Minimum KPI",
        "",
    ]
    lines.extend(f"- `{field}`" for field in packet["minimumKpiFields"])
    lines.extend(["", "## Follow-up KPI", ""])
    lines.extend(f"- `{field}`" for field in packet["followupKpiFields"])
    lines.append("")
    for row in packet["rows"]:
        lines.extend([
            f"## {row['platform']} · `{row['taskId']}`",
            "",
            f"- script：`{row['scriptId']}`",
            f"- guardian：{row['guardianName']}（`{row['guardianId']}`）",
            f"- title：{row['title']}",
            f"- status：`{row['status']}`",
            f"- schedule：{row['scheduledDate']} {row['scheduledTime']} Asia/Taipei",
            f"- tracked URL：{row['trackedUrl']}",
            f"- post URL：{row['postUrl'] or '(pending)'}",
            f"- post URL placeholder：`{row['postUrlPlaceholder']}`",
            "",
            "### Caption",
            "",
            "```text",
            row["caption"],
            "```",
            "",
            "### Pre-publish Checks",
            "",
        ])
        lines.extend(f"- {check}" for check in row["prePublishChecks"])
        lines.extend(["", "### Post-publish Checks", ""])
        lines.extend(f"- {check}" for check in row["postPublishChecks"])
        lines.extend([
            "",
            "### Writeback",
            "",
            f"- 發布 URL 回填：`{row['writebackCommand']}`",
            f"- 初始 KPI 回填：`{row['kpiExampleCommand']}`",
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(packet: dict, issues: list[str], output: Path, json_output: Path) -> None:
    json_output.write_text(json.dumps({**packet, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.write_text(render_markdown(packet, issues), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a first-batch publication and KPI writeback packet for LoveTypes promotion.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    issues = validate_packet(packet)
    if not args.check:
        write_outputs(packet, issues, Path(args.output), Path(args.json_output))
        print(f"promotion_first_batch_publication_packet={args.output}")
        print(f"promotion_first_batch_publication_packet_json={args.json_output}")
    print(f"promotion_first_batch_rows={packet['rowCount']}")
    print(f"promotion_first_batch_published={packet['publishedRows']}")
    print(f"promotion_first_batch_pending={packet['pendingRows']}")
    print(f"promotion_first_batch_minimum_kpi_rows={packet['minimumKpiRows']}")
    print(f"promotion_first_batch_ready_to_publish={1 if packet['readyToPublish'] else 0}")
    print(f"promotion_first_batch_weekly_decision_ready={1 if packet['publishingReadyForWeeklyDecision'] else 0}")
    print(f"promotion_first_batch_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
