#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import promotion_post_writeback as post_writeback


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
POSTING_QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
READINESS_PATH = PROMOTION_DIR / "launch-readiness-gate.json"
DEFAULT_WEEK = 1
PLATFORM_ORDER = ("youtube_shorts",)
QUIZ_CTA_MARKERS = ("完成 15 題測驗", "Take the 15-question quiz", "15-question quiz")
POST_URL_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}
MINIMUM_KPI_FIELDS = ("post_url", "site_clicks", "quiz_starts", "quiz_completions")
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
FORBIDDEN_COPY = ("診斷", "療效", "保證修復", "必須購買")
FORBIDDEN_PLACEHOLDER_SNIPPETS = (
    "replace-with-real",
    "example.com",
    "lovetypes-proof-url-123",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def output_paths(week: int) -> tuple[Path, Path]:
    return (
        PROMOTION_DIR / f"week-{week}-publication-runbook.md",
        PROMOTION_DIR / f"week-{week}-publication-runbook.json",
    )


def platform_sort(row: dict[str, str]) -> tuple[int, int]:
    platform = row.get("platform", "")
    return (
        int(row.get("slot", "0") or 0),
        PLATFORM_ORDER.index(platform) if platform in PLATFORM_ORDER else 99,
    )


def post_url_placeholder(platform: str) -> str:
    return POST_URL_PLACEHOLDERS.get(platform, "<REAL_POST_URL>")


def valid_tracked_url(value: str, utm_content: str) -> bool:
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "lovetypes.tw"
        and parsed.path == "/start/"
        and query.get("utm_source") == ["shorts"]
        and query.get("utm_medium") == ["social"]
        and query.get("utm_campaign") == ["first_round_quiz_completion"]
        and query.get("utm_content") == [utm_content]
    )


def build_publish_command(row: dict[str, str], placeholder: str) -> str:
    return (
        f"python3 tools/promotion_post_writeback.py update --platform {row.get('platform', '')} "
        f"--task-id {row.get('task_id', '')} --status published "
        f"--published-date {date.today().isoformat()} --post-url {placeholder} "
        f"--proof-note \"{post_writeback.POST_PROOF_NOTE_PLACEHOLDER}\""
    )


def build_kpi_command(row: dict[str, str], placeholder: str) -> str:
    return (
        f"python3 tools/promotion_post_writeback.py update --platform {row.get('platform', '')} "
        f"--task-id {row.get('task_id', '')} --status published "
        f"--published-date {date.today().isoformat()} --post-url {placeholder} "
        "--site-clicks 0 --quiz-starts 0 --quiz-completions 0 "
        f"--proof-note \"{post_writeback.ANALYTICS_PROOF_NOTE_PLACEHOLDER}\""
    )


def build_import_template(row: dict[str, str], placeholder: str) -> str:
    return "\n".join([
        "LoveTypes platform post writeback",
        f"platform: {row.get('platform', '')}",
        f"task_id: {row.get('task_id', '')}",
        "status: published",
        f"published_date: {date.today().isoformat()}",
        f"post_url: {placeholder}",
        "views: 0",
        "site_clicks: 0",
        "quiz_starts: 0",
        "quiz_completions: 0",
        f"proof_note: {post_writeback.POST_PROOF_NOTE_PLACEHOLDER}",
    ])


def build_runbook(week: int) -> dict:
    queue_rows = [
        row for row in read_csv(POSTING_QUEUE_PATH)
        if int(row.get("week", 0) or 0) == week
    ]
    readiness = load_json(READINESS_PATH)
    readiness_state = readiness.get("readiness", {}) if isinstance(readiness.get("readiness"), dict) else {}
    tasks = []
    for row in sorted(queue_rows, key=platform_sort):
        platform = row.get("platform", "")
        placeholder = post_url_placeholder(platform)
        blocked_by = "" if readiness_state.get("readyToPublishPosts") else "profile links are not all set/live"
        tasks.append({
            "week": int(row.get("week", 0) or 0),
            "slot": int(row.get("slot", 0) or 0),
            "platform": platform,
            "status": row.get("status", ""),
            "blockedBy": blocked_by,
            "scheduled": f"{row.get('scheduled_date', '')} {row.get('scheduled_time', '')} {row.get('timezone', '')}".strip(),
            "taskId": row.get("task_id", ""),
            "scriptId": row.get("script_id", ""),
            "guardianId": row.get("guardian_id", ""),
            "guardianName": row.get("guardian_name", ""),
            "contentAngle": row.get("content_angle", ""),
            "title": row.get("title", ""),
            "caption": row.get("caption", ""),
            "trackedUrl": row.get("tracked_url", ""),
            "utmContent": row.get("utm_content", ""),
            "postUrlPlaceholder": placeholder,
            "publishCommand": build_publish_command(row, placeholder),
            "kpiCommand": build_kpi_command(row, placeholder),
            "importTemplate": build_import_template(row, placeholder),
            "prePublishChecks": [
                "launch readiness ready_to_publish=1。",
                "profile link 已完成 set/live，且平台個人頁只導向測驗。",
                "影片素材已完成 9:16、字幕、封面或首幀 QA。",
                "Caption 保留單一 CTA：take the 15-question quiz。",
                "Tracked URL 指向 /start/ 且 UTM content 與任務一致。",
                "不加入 Luna、聯盟書卷或付費商品作為第一 CTA。",
            ],
            "postPublishChecks": [
                "公開 post URL 是真實 https URL，不是 <REAL_...>、example.com 或文字型假網址。",
                "用 post text import check 先驗證，再 add 寫入。",
                "有平台或網站來源檢查後，才回填 site_clicks、quiz_starts、quiz_completions；0 必須是確認後的 0。",
                "週回顧前重新跑 publishing status、weekly summary、week decision gate。",
            ],
        })
    active_platforms = tuple(platform for platform in PLATFORM_ORDER if any(task["platform"] == platform for task in tasks))
    active_platforms = active_platforms + tuple(
        sorted({str(task["platform"]) for task in tasks if task["platform"] not in active_platforms})
    )
    platform_distribution = {platform: 0 for platform in active_platforms}
    for task in tasks:
        if task["platform"] in platform_distribution:
            platform_distribution[task["platform"]] += 1
    return {
        "generatedAt": date.today().isoformat(),
        "week": week,
        "source": {
            "postingQueue": str(POSTING_QUEUE_PATH.relative_to(ROOT)),
            "launchReadiness": str(READINESS_PATH.relative_to(ROOT)),
        },
        "readyToPublish": bool(readiness_state.get("readyToPublishPosts")),
        "taskCount": len(tasks),
        "scriptCount": len({task["scriptId"] for task in tasks}),
        "platformCount": len({task["platform"] for task in tasks}),
        "platformDistribution": platform_distribution,
        "minimumKpiFields": list(MINIMUM_KPI_FIELDS),
        "followupKpiFields": list(FOLLOWUP_KPI_FIELDS),
        "tasks": tasks,
        "policy": {
            "noFakePostUrl": True,
            "checkBeforeWrite": True,
            "profileGateBeforePublish": True,
            "emptyDataBoundary": "沒有 post URL 與最小 KPI 前，不調整商品、Luna、聯盟或付費 CTA。",
        },
    }


def validate_runbook(runbook: dict) -> list[str]:
    issues: list[str] = []
    tasks = runbook.get("tasks", [])
    active_platforms = tuple(runbook.get("platformDistribution", {}).keys())
    expected_task_count = runbook.get("scriptCount", 0) * len(active_platforms)
    if runbook.get("taskCount") != expected_task_count:
        issues.append(f"expected {expected_task_count} platform tasks")
    if runbook.get("platformDistribution") != {platform: runbook.get("scriptCount", 0) for platform in active_platforms}:
        issues.append("platform distribution should be balanced across the week")
    if set(runbook.get("minimumKpiFields", [])) != set(MINIMUM_KPI_FIELDS):
        issues.append("minimum KPI fields do not match policy")
    for task in tasks:
        label = f"{task.get('platform', '<platform>')}/{task.get('taskId', '<task>')}"
        platform = str(task.get("platform", ""))
        placeholder = str(task.get("postUrlPlaceholder", ""))
        if platform not in active_platforms:
            issues.append(f"{label}: unexpected platform")
            continue
        if placeholder != post_url_placeholder(platform):
            issues.append(f"{label}: wrong platform-specific post URL placeholder")
        command_text = " ".join([
            str(task.get("publishCommand", "")),
            str(task.get("kpiCommand", "")),
            str(task.get("importTemplate", "")),
        ])
        for forbidden in FORBIDDEN_PLACEHOLDER_SNIPPETS:
            if forbidden in command_text:
                issues.append(f"{label}: contains URL-like placeholder {forbidden}")
        if "--proof-note" not in str(task.get("publishCommand", "")):
            issues.append(f"{label}: publish command should require proof note")
        if "--site-clicks 0 --quiz-starts 0 --quiz-completions 0" not in str(task.get("kpiCommand", "")):
            issues.append(f"{label}: KPI command should include minimum KPI fields")
        if not valid_tracked_url(str(task.get("trackedUrl", "")), str(task.get("utmContent", ""))):
            issues.append(f"{label}: tracked URL should point to /start/ with matching first-round UTM")
        if not any(marker in str(task.get("caption", "")) for marker in QUIZ_CTA_MARKERS):
            issues.append(f"{label}: caption missing quiz CTA")
        for forbidden in FORBIDDEN_COPY:
            if forbidden in str(task.get("caption", "")):
                issues.append(f"{label}: caption contains forbidden claim {forbidden}")
        if len(task.get("prePublishChecks", [])) < 6:
            issues.append(f"{label}: pre-publish checklist is incomplete")
        if len(task.get("postPublishChecks", [])) < 4:
            issues.append(f"{label}: post-publish checklist is incomplete")
        if not task.get("blockedBy") and not runbook.get("readyToPublish"):
            issues.append(f"{label}: should stay blocked while readiness is false")
    policy = runbook.get("policy", {})
    for key in ("noFakePostUrl", "checkBeforeWrite", "profileGateBeforePublish"):
        if not policy.get(key):
            issues.append(f"policy.{key} should be true")
    return issues


def render_markdown(runbook: dict, issues: list[str]) -> str:
    lines = [
        f"# LoveTypes Week {runbook['week']} Publication Runbook",
        "",
        f"- 產生日期：{runbook['generatedAt']}",
        f"- tasks：{runbook['taskCount']}",
        f"- scripts：{runbook['scriptCount']}",
        f"- platforms：{runbook['platformCount']}",
        f"- ready_to_publish：{1 if runbook['readyToPublish'] else 0}",
        f"- issues：{len(issues)}",
        "",
        "## Rules",
        "",
        "- 先完成 YouTube profile gate，再發布 Week 任務。",
        "- 每則貼文只導向 15 題測驗，不把 caption 變成導購。",
        "- `<REAL_...>` 必須替換成公開平台上的真實 https post URL；沒有真實 URL 時，匯入檢查應拒絕。",
        "- 0 KPI 只能在平台或網站來源檢查後回填，不用空資料做商品判斷。",
        "",
        "## KPI Fields",
        "",
        "Minimum:",
    ]
    lines.extend(f"- `{field}`" for field in runbook["minimumKpiFields"])
    lines.extend(["", "Follow-up:"])
    lines.extend(f"- `{field}`" for field in runbook["followupKpiFields"])
    lines.append("")
    for task in runbook["tasks"]:
        lines.extend([
            f"## Slot {task['slot']} · {task['platform']} · `{task['taskId']}`",
            "",
            f"- status：`{task['status']}`",
            f"- blocked by：`{task['blockedBy'] or 'none'}`",
            f"- scheduled：{task['scheduled']}",
            f"- script：`{task['scriptId']}`",
            f"- guardian：{task['guardianName']}（`{task['guardianId']}`）",
            f"- title：{task['title']}",
            f"- tracked URL：{task['trackedUrl']}",
            f"- post URL placeholder：`{task['postUrlPlaceholder']}`",
            "",
            "### Caption",
            "",
            "```text",
            task["caption"],
            "```",
            "",
            "### Pre-publish Checks",
            "",
        ])
        lines.extend(f"- {item}" for item in task["prePublishChecks"])
        lines.extend([
            "",
            "### Post-publish Checks",
            "",
        ])
        lines.extend(f"- {item}" for item in task["postPublishChecks"])
        lines.extend([
            "",
            "### Writeback",
            "",
            "Published URL:",
            "",
            "```bash",
            task["publishCommand"],
            "```",
            "",
            "Minimum KPI after source check:",
            "",
            "```bash",
            task["kpiCommand"],
            "```",
            "",
            "Structured import template:",
            "",
            "```text",
            task["importTemplate"],
            "```",
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(runbook: dict, issues: list[str], md_output: Path, json_output: Path) -> None:
    md_output.write_text(render_markdown(runbook, issues), encoding="utf-8")
    json_output.write_text(json.dumps({**runbook, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a proof-gated publication runbook for a LoveTypes promotion week.")
    parser.add_argument("--week", type=int, default=DEFAULT_WEEK)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    runbook = build_runbook(args.week)
    issues = validate_runbook(runbook)
    md_output, json_output = output_paths(args.week)
    if not args.check:
        write_outputs(runbook, issues, md_output, json_output)
        print(f"promotion_week_publication_runbook={md_output}")
        print(f"promotion_week_publication_runbook_json={json_output}")
    print(f"promotion_week_publication_runbook_week={runbook['week']}")
    print(f"promotion_week_publication_runbook_tasks={runbook['taskCount']}")
    print(f"promotion_week_publication_runbook_scripts={runbook['scriptCount']}")
    print(f"promotion_week_publication_runbook_platforms={runbook['platformCount']}")
    print(f"promotion_week_publication_runbook_ready_to_publish={1 if runbook['readyToPublish'] else 0}")
    print(f"promotion_week_publication_runbook_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
