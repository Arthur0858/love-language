#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "week-1-platform-launch-brief.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "week-1-platform-launch-brief.json"
PLATFORM_LABELS = {
    "youtube_shorts": "YouTube Shorts",
    "tiktok": "TikTok",
    "instagram_reels": "Instagram Reels",
}
REQUIRED_FIELDS = [
    "week",
    "slot",
    "platform",
    "status",
    "scheduled_date",
    "scheduled_time",
    "timezone",
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
]


def read_queue(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def selected_week(rows: list[dict[str, str]], requested_week: int | None) -> int:
    if requested_week is not None:
        return requested_week
    planned_weeks = sorted({
        int(row.get("week", "0") or 0)
        for row in rows
        if (row.get("status") or "planned").strip().lower() in {"planned", "scheduled"}
    })
    if planned_weeks:
        return planned_weeks[0]
    all_weeks = sorted({int(row.get("week", "0") or 0) for row in rows if row.get("week")})
    return all_weeks[0] if all_weeks else 1


def tracked_url_ok(row: dict[str, str]) -> bool:
    parsed = urlparse(row.get("tracked_url", ""))
    query = parse_qs(parsed.query)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "lovetypes.tw"
        and parsed.path == "/start/"
        and query.get("utm_source", [""])[0] == "shorts"
        and query.get("utm_medium", [""])[0] == "social"
        and query.get("utm_campaign", [""])[0] == "first_round_quiz_completion"
        and query.get("utm_content", [""])[0] == row.get("utm_content")
    )


def build_report(rows: list[dict[str, str]], week: int) -> dict:
    launch_rows = [
        row
        for row in rows
        if int(row.get("week", "0") or 0) == week
        and (row.get("status") or "planned").strip().lower() in {"planned", "scheduled"}
    ]
    launch_rows.sort(key=lambda row: (int(row.get("slot", "0") or 0), row.get("scheduled_time", ""), row.get("platform", "")))
    issues: list[str] = []
    warnings: list[str] = []
    by_platform = Counter(row.get("platform", "") for row in launch_rows)
    by_task = Counter(row.get("task_id", "") for row in launch_rows)
    by_guardian = Counter(row.get("guardian_id", "") for row in launch_rows)

    if len(launch_rows) != 9:
        issues.append(f"week {week} launch brief should include 9 platform rows, got {len(launch_rows)}")
    if len(by_task) != 3:
        issues.append(f"week {week} launch brief should include 3 scripts, got {len(by_task)}")
    for platform in PLATFORM_LABELS:
        if by_platform[platform] != 3:
            issues.append(f"week {week} should include 3 {platform} rows, got {by_platform[platform]}")
    for row in launch_rows:
        label = f"{row.get('platform', '<platform>')}/{row.get('task_id', '<task>')}"
        for field in REQUIRED_FIELDS:
            if not (row.get(field) or "").strip():
                issues.append(f"{label}: missing {field}")
        if not tracked_url_ok(row):
            issues.append(f"{label}: tracked_url should be the first-round /start/ UTM link")
        if "診斷" in row.get("caption", "") or "保證修復" in row.get("caption", ""):
            issues.append(f"{label}: caption should not imply diagnosis or guaranteed repair")
        if (row.get("post_url") or "").strip():
            warnings.append(f"{label}: already has post_url; verify whether this should still be in launch brief")

    next_actions = [
        "發布後先在 posting-queue.csv 回填 status、published_date、post_url。",
        "同一天或隔天回填 kpi-tracker.csv 的 platform、post_url、site_clicks、quiz_starts、quiz_completions。",
        "只有在 publishing-status.md 顯示可做週決策後，才放大守護者或商品承接方向。",
    ]
    return {
        "generatedAt": date.today().isoformat(),
        "week": week,
        "rowCount": len(launch_rows),
        "scriptCount": len(by_task),
        "platformCount": len(by_platform),
        "guardianDistribution": dict(sorted(by_guardian.items())),
        "platformDistribution": dict(sorted(by_platform.items())),
        "tasks": launch_rows,
        "nextActions": next_actions,
        "safety": {
            "primaryCta": "完成 15 題測驗，找到你的情感守護者",
            "doNotClaim": ["診斷", "療效", "保證修復", "必須購買"],
            "measurementFirst": True,
        },
        "warnings": warnings,
        "issues": issues,
    }


def render_task(row: dict[str, str]) -> list[str]:
    platform = row["platform"]
    label = PLATFORM_LABELS.get(platform, platform)
    return [
        f"### {row['scheduled_date']} {row['scheduled_time']} {row['timezone']} · {label}",
        "",
        f"- 任務：`{row['task_id']}`",
        f"- 腳本：`{row['script_id']}`",
        f"- 守護者：{row['guardian_name']}（`{row['guardian_id']}`）",
        f"- 內容角度：{row['content_angle']}",
        f"- 標題：{row['title']}",
        f"- 追蹤連結：{row['tracked_url']}",
        f"- UTM content：`{row['utm_content']}`",
        "",
        "```text",
        row["caption"].strip(),
        "```",
        "",
        "回填欄位：`status`、`published_date`、`post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`。",
        "",
    ]


def render_markdown(report: dict) -> str:
    lines = [
        f"# LoveTypes Week {report['week']} 平台發布簡報",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- 平台任務：{report['rowCount']}",
        f"- 腳本數：{report['scriptCount']}",
        "- 主 CTA：完成 15 題測驗，找到你的情感守護者",
        "",
        "## 發布前規則",
        "",
        "- 每支內容只放一個主 CTA，不在影片或說明欄直接導購。",
        "- 優先使用追蹤連結；若平台限制連結，至少保留 `https://lovetypes.tw/start/`。",
        "- 不使用診斷、療效、保證修復或必須購買的說法。",
        "",
        "## 平台任務",
        "",
    ]
    for row in report["tasks"]:
        lines.extend(render_task(row))
    lines.extend(["## 發布後回填", ""])
    lines.extend(f"- {item}" for item in report["nextActions"])
    if report["warnings"]:
        lines.extend(["", "## 注意事項", ""])
        lines.extend(f"- {item}" for item in report["warnings"])
    if report["issues"]:
        lines.extend(["", "## 問題", ""])
        lines.extend(f"- {item}" for item in report["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict, output_path: Path, json_path: Path) -> None:
    output_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the next LoveTypes platform launch brief from posting queue rows.")
    parser.add_argument("--queue", default=str(QUEUE_PATH))
    parser.add_argument("--week", type=int, default=None, help="Promotion week to render. Defaults to first planned week.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true", help="Validate without writing launch brief files.")
    args = parser.parse_args()

    rows = read_queue(Path(args.queue))
    week = selected_week(rows, args.week)
    report = build_report(rows, week)
    if not args.check:
        write_outputs(report, Path(args.output), Path(args.json_output))
        print(f"promotion_launch_brief={args.output}")
        print(f"promotion_launch_brief_json={args.json_output}")
    print(f"promotion_launch_brief_week={report['week']}")
    print(f"promotion_launch_brief_rows={report['rowCount']}")
    print(f"promotion_launch_brief_scripts={report['scriptCount']}")
    print(f"promotion_launch_brief_platforms={report['platformCount']}")
    print(f"promotion_launch_brief_warnings={len(report['warnings'])}")
    print(f"promotion_launch_brief_issues={len(report['issues'])}")
    for issue in report["issues"]:
        print(issue)
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
