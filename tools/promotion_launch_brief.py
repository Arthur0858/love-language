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
DEFAULT_INDEX_PATH = PROMOTION_DIR / "platform-launch-brief-index.md"
DEFAULT_INDEX_JSON_PATH = PROMOTION_DIR / "platform-launch-brief-index.json"
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


def available_weeks(rows: list[dict[str, str]]) -> list[int]:
    return sorted({
        int(row.get("week", "0") or 0)
        for row in rows
        if row.get("week") and int(row.get("week", "0") or 0) > 0
    })


def week_output_paths(week: int) -> tuple[Path, Path]:
    return (
        PROMOTION_DIR / f"week-{week}-platform-launch-brief.md",
        PROMOTION_DIR / f"week-{week}-platform-launch-brief.json",
    )


def render_index(reports: list[dict]) -> str:
    total_rows = sum(int(report["rowCount"]) for report in reports)
    total_scripts = sum(int(report["scriptCount"]) for report in reports)
    issue_count = sum(len(report["issues"]) for report in reports)
    lines = [
        "# LoveTypes 第一輪平台發布簡報索引",
        "",
        f"- 產生日期：{date.today().isoformat()}",
        f"- 週次：{len(reports)}",
        f"- 平台任務：{total_rows}",
        f"- 腳本數：{total_scripts}",
        f"- 問題數：{issue_count}",
        "",
        "## 週次",
        "",
    ]
    for report in reports:
        week = report["week"]
        guardian_text = ", ".join(f"{key}: {value}" for key, value in report["guardianDistribution"].items())
        lines.extend([
            f"### Week {week}",
            "",
            f"- 簡報：`week-{week}-platform-launch-brief.md`",
            f"- 平台任務：{report['rowCount']}",
            f"- 腳本數：{report['scriptCount']}",
            f"- 守護者分布：{guardian_text}",
            f"- 問題數：{len(report['issues'])}",
            "",
        ])
    lines.extend([
        "## 使用規則",
        "",
        "- 每週只看該週的 `week-N-platform-launch-brief.md` 發布，不需要從 45 筆佇列人工篩選。",
        "- 發布後先更新 `posting-queue.csv`，再更新 `kpi-tracker.csv`。",
        "- 判斷放大或商品承接前，先跑 `python3 tools/promotion_publishing_status.py`。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_index(reports: list[dict], output_path: Path, json_path: Path) -> None:
    output_path.write_text(render_index(reports), encoding="utf-8")
    payload = {
        "generatedAt": date.today().isoformat(),
        "weekCount": len(reports),
        "rowCount": sum(int(report["rowCount"]) for report in reports),
        "scriptCount": sum(int(report["scriptCount"]) for report in reports),
        "issueCount": sum(len(report["issues"]) for report in reports),
        "reports": [
            {
                "week": report["week"],
                "rowCount": report["rowCount"],
                "scriptCount": report["scriptCount"],
                "platformCount": report["platformCount"],
                "guardianDistribution": report["guardianDistribution"],
                "issues": report["issues"],
            }
            for report in reports
        ],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the next LoveTypes platform launch brief from posting queue rows.")
    parser.add_argument("--queue", default=str(QUEUE_PATH))
    parser.add_argument("--week", type=int, default=None, help="Promotion week to render. Defaults to first planned week.")
    parser.add_argument("--all", action="store_true", help="Render launch briefs for every week in the posting queue.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--index-output", default=str(DEFAULT_INDEX_PATH))
    parser.add_argument("--index-json-output", default=str(DEFAULT_INDEX_JSON_PATH))
    parser.add_argument("--check", action="store_true", help="Validate without writing launch brief files.")
    args = parser.parse_args()

    rows = read_queue(Path(args.queue))
    weeks = available_weeks(rows) if args.all else [selected_week(rows, args.week)]
    reports = [build_report(rows, week) for week in weeks]
    report = reports[0]
    if not args.check:
        if args.all:
            for item in reports:
                output_path, json_path = week_output_paths(int(item["week"]))
                write_outputs(item, output_path, json_path)
            write_index(reports, Path(args.index_output), Path(args.index_json_output))
            print(f"promotion_launch_brief_index={args.index_output}")
            print(f"promotion_launch_brief_index_json={args.index_json_output}")
        else:
            write_outputs(report, Path(args.output), Path(args.json_output))
            print(f"promotion_launch_brief={args.output}")
            print(f"promotion_launch_brief_json={args.json_output}")
    all_issues = [issue for item in reports for issue in item["issues"]]
    all_warnings = [warning for item in reports for warning in item["warnings"]]
    print(f"promotion_launch_brief_weeks={len(reports)}")
    print(f"promotion_launch_brief_week={report['week']}")
    print(f"promotion_launch_brief_rows={sum(int(item['rowCount']) for item in reports)}")
    print(f"promotion_launch_brief_scripts={sum(int(item['scriptCount']) for item in reports)}")
    print(f"promotion_launch_brief_platforms={max((int(item['platformCount']) for item in reports), default=0)}")
    print(f"promotion_launch_brief_warnings={len(all_warnings)}")
    print(f"promotion_launch_brief_issues={len(all_issues)}")
    for issue in all_issues:
        print(issue)
    return 1 if all_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
