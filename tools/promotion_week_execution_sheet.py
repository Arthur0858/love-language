#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from promotion_weekly_summary import is_profile_filled


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
POSTING_QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
PROFILE_SETUP_PATH = PROMOTION_DIR / "platform-profile-setup.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "week-1-execution-sheet.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "week-1-execution-sheet.json"
DEFAULT_INDEX_PATH = PROMOTION_DIR / "execution-sheet-index.md"
DEFAULT_INDEX_JSON_PATH = PROMOTION_DIR / "execution-sheet-index.json"
PLATFORM_ORDER = ["youtube_shorts"]
PLATFORM_LABELS = {
    "youtube_shorts": "YouTube Shorts",
    "tiktok": "TikTok",
    "instagram_reels": "Instagram Reels",
}
POST_STATUS_READY = {"planned", "scheduled"}
MINIMUM_POST_KPI_WRITEBACK = (
    "platform-kpi-tracker.csv: post_url",
    "platform-kpi-tracker.csv: site_clicks",
    "platform-kpi-tracker.csv: quiz_starts",
    "platform-kpi-tracker.csv: quiz_completions",
)
DOWNSTREAM_POST_KPI_WRITEBACK = (
    "platform-kpi-tracker.csv: guardian_result_clicks",
    "platform-kpi-tracker.csv: resources_clicks",
    "platform-kpi-tracker.csv: repair_plan_clicks",
    "platform-kpi-tracker.csv: luna_clicks",
    "platform-kpi-tracker.csv: keepsake_clicks",
    "platform-kpi-tracker.csv: free_keepsake_downloads",
    "platform-kpi-tracker.csv: supply_lead_requests",
    "platform-kpi-tracker.csv: luna_pack_clicks",
    "platform-kpi-tracker.csv: affiliate_book_clicks",
    "platform-kpi-tracker.csv: contact_requests",
)


def inline_code_list(items: tuple[str, ...]) -> str:
    return "、".join(f"`{item}`" for item in items)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def available_weeks(rows: list[dict[str, str]]) -> list[int]:
    weeks = {
        int(row.get("week", "0") or 0)
        for row in rows
        if row.get("week") and int(row.get("week", "0") or 0) > 0
    }
    return sorted(weeks)


def selected_week(rows: list[dict[str, str]], requested_week: int | None) -> int:
    if requested_week is not None:
        return requested_week
    planned = sorted({
        int(row.get("week", "0") or 0)
        for row in rows
        if (row.get("status") or "planned").strip().lower() in POST_STATUS_READY
    })
    return planned[0] if planned else (available_weeks(rows)[0] if available_weeks(rows) else 1)


def setup_by_platform(setup: dict) -> dict[str, dict]:
    return {str(item.get("platformId", "")): item for item in setup.get("platforms", []) if item.get("platformId")}


def profile_gates(profile_rows: list[dict[str, str]], setup: dict[str, dict]) -> list[dict]:
    gates = []
    for row in sorted(profile_rows, key=lambda item: PLATFORM_ORDER.index(item["platform"]) if item.get("platform") in PLATFORM_ORDER else 99):
        platform = row.get("platform", "")
        item = setup.get(platform, {})
        status = row.get("status", "planned") or "planned"
        gates.append({
            "platform": platform,
            "label": row.get("label") or item.get("label") or platform,
            "ready": is_profile_filled(row),
            "status": status,
            "profileLink": row.get("profile_link") or item.get("profileLink", ""),
            "profileLinkLabel": item.get("profileLinkLabel", "Profile link"),
            "bio": item.get("bio", ""),
            "pinnedComment": item.get("pinnedComment", ""),
            "writeback": ["status=set/live", "profile_link_set_date", "profile_clicks", "site_clicks", "quiz_starts", "quiz_completions"],
        })
    return gates


def week_rows(rows: list[dict[str, str]], week: int) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if int(row.get("week", "0") or 0) == week
        and (row.get("status") or "planned").strip().lower() in POST_STATUS_READY
    ]
    selected.sort(key=lambda row: (
        int(row.get("slot", "0") or 0),
        PLATFORM_ORDER.index(row["platform"]) if row.get("platform") in PLATFORM_ORDER else 99,
    ))
    return selected


def scripts_from_rows(rows: list[dict[str, str]]) -> list[dict]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("task_id", "")].append(row)
    scripts = []
    for task_id, items in grouped.items():
        first = items[0]
        platforms = []
        for row in sorted(items, key=lambda item: PLATFORM_ORDER.index(item["platform"]) if item.get("platform") in PLATFORM_ORDER else 99):
            platforms.append({
                "platform": row.get("platform", ""),
                "label": PLATFORM_LABELS.get(row.get("platform", ""), row.get("platform", "")),
                "scheduledDate": row.get("scheduled_date", ""),
                "scheduledTime": row.get("scheduled_time", ""),
                "timezone": row.get("timezone", ""),
                "trackedUrl": row.get("tracked_url", ""),
                "caption": row.get("caption", ""),
                "writeback": [
                    "posting-queue.csv: status=published",
                    "posting-queue.csv: published_date",
                    "posting-queue.csv: post_url",
                    *MINIMUM_POST_KPI_WRITEBACK,
                    *DOWNSTREAM_POST_KPI_WRITEBACK,
                ],
            })
        scripts.append({
            "taskId": task_id,
            "scriptId": first.get("script_id", ""),
            "guardianId": first.get("guardian_id", ""),
            "guardianName": first.get("guardian_name", ""),
            "contentAngle": first.get("content_angle", ""),
            "title": first.get("title", ""),
            "utmContent": first.get("utm_content", ""),
            "primaryCta": first.get("primary_cta", ""),
            "platforms": platforms,
        })
    scripts.sort(key=lambda item: int(next(row.get("slot", "0") for row in rows if row.get("task_id") == item["taskId"]) or 0))
    return scripts


def build_sheet(queue_rows: list[dict[str, str]], profile_rows: list[dict[str, str]], setup: dict, week: int) -> dict:
    rows = week_rows(queue_rows, week)
    gates = profile_gates(profile_rows, setup_by_platform(setup))
    scripts = scripts_from_rows(rows)
    platform_counts = Counter(row.get("platform", "") for row in rows)
    expected_profile_gates = len(profile_rows)
    expected_scripts = len({
        (row.get("task_id") or "").strip()
        for row in rows
        if (row.get("task_id") or "").strip()
    })
    expected_platforms = {
        (row.get("platform") or "").strip()
        for row in profile_rows
        if (row.get("platform") or "").strip()
    }
    expected_platform_posts = expected_scripts * len(expected_platforms)
    issues: list[str] = []
    if len(gates) != expected_profile_gates:
        issues.append(f"expected {expected_profile_gates} platform profile gates, got {len(gates)}")
    if len(rows) != expected_platform_posts:
        issues.append(f"week {week} should include {expected_platform_posts} platform posts, got {len(rows)}")
    if len(scripts) != expected_scripts:
        issues.append(f"week {week} should include {expected_scripts} scripts, got {len(scripts)}")
    for platform in PLATFORM_ORDER:
        expected_platform_count = expected_scripts if platform in expected_platforms else 0
        if platform_counts[platform] != expected_platform_count:
            issues.append(f"week {week} should include {expected_platform_count} {platform} posts, got {platform_counts[platform]}")
    for gate in gates:
        if not gate["profileLink"] or "utm_source=" not in gate["profileLink"]:
            issues.append(f"{gate['platform']}: missing tracked profile link")
        if not gate["bio"]:
            issues.append(f"{gate['platform']}: missing profile bio")
    for script in scripts:
        expected_script_platforms = len({
            (row.get("platform") or "").strip()
            for row in rows
            if row.get("task_id") == script["taskId"] and (row.get("platform") or "").strip()
        })
        if len(script["platforms"]) != expected_script_platforms:
            issues.append(f"{script['taskId']}: expected {expected_script_platforms} platform rows")
        for item in script["platforms"]:
            if not item["trackedUrl"] or "utm_content=" not in item["trackedUrl"]:
                issues.append(f"{script['taskId']}/{item['platform']}: missing tracked URL")
    return {
        "generatedAt": date.today().isoformat(),
        "week": week,
        "profileGateCount": len(gates),
        "profilePendingCount": sum(1 for gate in gates if not gate["ready"]),
        "platformPostCount": len(rows),
        "scriptCount": len(scripts),
        "platformDistribution": dict(sorted(platform_counts.items())),
        "profileGates": gates,
        "scripts": scripts,
        "runOrder": [
            "完成 YouTube channel profile link 設定。",
            "依本週三支腳本完成影片輸出或剪輯手卡交付。",
            "依任務時間發布到 YouTube Shorts。",
            "先回填 posting-queue.csv，再回填 platform-kpi-tracker.csv 的最小 KPI；有結果後互動時補齊守護者、補給、Luna、收藏、名單與聯盟欄位。",
            "週回顧時才彙總 kpi-tracker.csv，平台首頁成效另回填 platform-profile-tracker.csv。",
            "跑 promotion_publishing_status.py；未達週決策門檻前不調整商品或付費 CTA。",
        ],
        "safety": {
            "shortsCta": "完成 15 題測驗，找到你的情感守護者",
            "profileLinksQuizOnly": True,
            "doNotUse": ["診斷", "療效", "保證修復", "必須購買"],
            "doNotChangeOffersBeforeData": True,
        },
        "issues": issues,
    }


def render_markdown(sheet: dict) -> str:
    lines = [
        f"# LoveTypes Week {sheet['week']} 推廣執行單",
        "",
        f"- 產生日期：{sheet['generatedAt']}",
        f"- 平台首頁 gate：{sheet['profilePendingCount']} 待設定 / {sheet['profileGateCount']}",
        f"- 平台發布任務：{sheet['platformPostCount']}",
        f"- 腳本數：{sheet['scriptCount']}",
        "- 主 CTA：完成 15 題測驗，找到你的情感守護者",
        "",
        "## 執行順序",
        "",
    ]
    lines.extend(f"{index}. {item}" for index, item in enumerate(sheet["runOrder"], start=1))
    lines.extend(["", "## 發布前平台首頁 Gate", ""])
    for gate in sheet["profileGates"]:
        state = "已設定" if gate["ready"] else "待設定"
        lines.extend([
            f"### {gate['label']}（`{gate['platform']}`）",
            "",
            f"- 狀態：{state} / `{gate['status']}`",
            f"- 連結位置：{gate['profileLinkLabel']}",
            f"- Profile link：{gate['profileLink']}",
            "- Bio：",
            "",
            "```text",
            gate["bio"],
            "```",
            "",
            "- 置頂留言 / 首則留言：",
            "",
            "```text",
            gate["pinnedComment"],
            "```",
            "",
            f"- 回填：{', '.join(f'`{item}`' for item in gate['writeback'])}",
            "",
        ])
    lines.extend(["## 本週三支腳本與平台發布", ""])
    for script in sheet["scripts"]:
        lines.extend([
            f"### {script['title']}",
            "",
            f"- 任務：`{script['taskId']}`",
            f"- 腳本：`{script['scriptId']}`",
            f"- 守護者：{script['guardianName']}（`{script['guardianId']}`）",
            f"- 內容角度：{script['contentAngle']}",
            f"- UTM content：`{script['utmContent']}`",
            "",
        ])
        for item in script["platforms"]:
            lines.extend([
                f"#### {item['label']} · {item['scheduledDate']} {item['scheduledTime']} {item['timezone']}",
                "",
                f"- 追蹤連結：{item['trackedUrl']}",
                "- Caption：",
                "",
                "```text",
                item["caption"].strip(),
                "```",
                "",
                f"- 回填：{', '.join(f'`{field}`' for field in item['writeback'])}",
                f"- 最小 KPI：{inline_code_list(MINIMUM_POST_KPI_WRITEBACK)}",
                f"- 結果後互動：{inline_code_list(DOWNSTREAM_POST_KPI_WRITEBACK)}",
                "",
            ])
    lines.extend([
        "## 安全邊界",
        "",
        "- Shorts 與平台首頁都只導向測驗，不直接導購。",
        "- 不使用診斷、療效、保證修復或必須購買說法。",
        "- 沒有足夠回填前，不調整守護者優先序、商品承接或付費 CTA。",
    ])
    if sheet["issues"]:
        lines.extend(["", "## 問題", ""])
        lines.extend(f"- {issue}" for issue in sheet["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_sheet(sheet: dict, output: Path, json_output: Path) -> None:
    output.write_text(render_markdown(sheet), encoding="utf-8")
    json_output.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def week_output_paths(week: int) -> tuple[Path, Path]:
    return (
        PROMOTION_DIR / f"week-{week}-execution-sheet.md",
        PROMOTION_DIR / f"week-{week}-execution-sheet.json",
    )


def render_index(sheets: list[dict]) -> str:
    lines = [
        "# LoveTypes 第一輪推廣執行單索引",
        "",
        f"- 產生日期：{date.today().isoformat()}",
        f"- 週次：{len(sheets)}",
        f"- 平台發布任務：{sum(sheet['platformPostCount'] for sheet in sheets)}",
        f"- 問題數：{sum(len(sheet['issues']) for sheet in sheets)}",
        "",
        "## 週次",
        "",
    ]
    for sheet in sheets:
        lines.extend([
            f"### Week {sheet['week']}",
            "",
            f"- 執行單：`week-{sheet['week']}-execution-sheet.md`",
            f"- 平台首頁待設定：{sheet['profilePendingCount']} / {sheet['profileGateCount']}",
            f"- 平台發布任務：{sheet['platformPostCount']}",
            f"- 腳本數：{sheet['scriptCount']}",
            f"- 問題數：{len(sheet['issues'])}",
            "",
        ])
    lines.extend([
        "## 使用規則",
        "",
        "- 每週照該週執行單發布，不從多份文件人工拼接。",
        "- 發布前先完成平台首頁 gate；發布後先回填 queue，再回填 platform-kpi-tracker.csv 的最小 KPI 與結果後互動欄位。",
        f"- 結果後互動欄位：{inline_code_list(DOWNSTREAM_POST_KPI_WRITEBACK)}。",
        "- 若執行單有問題數，先修資料再發布。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_index(sheets: list[dict], output: Path, json_output: Path) -> None:
    output.write_text(render_index(sheets), encoding="utf-8")
    payload = {
        "generatedAt": date.today().isoformat(),
        "weekCount": len(sheets),
        "platformPostCount": sum(sheet["platformPostCount"] for sheet in sheets),
        "issueCount": sum(len(sheet["issues"]) for sheet in sheets),
        "sheets": [
            {
                "week": sheet["week"],
                "profilePendingCount": sheet["profilePendingCount"],
                "profileGateCount": sheet["profileGateCount"],
                "platformPostCount": sheet["platformPostCount"],
                "scriptCount": sheet["scriptCount"],
                "issues": sheet["issues"],
            }
            for sheet in sheets
        ],
    }
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a week-level LoveTypes promotion execution sheet.")
    parser.add_argument("--queue", default=str(POSTING_QUEUE_PATH))
    parser.add_argument("--profile-tracker", default=str(PROFILE_TRACKER_PATH))
    parser.add_argument("--profile-setup", default=str(PROFILE_SETUP_PATH))
    parser.add_argument("--week", type=int, default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--index-output", default=str(DEFAULT_INDEX_PATH))
    parser.add_argument("--index-json-output", default=str(DEFAULT_INDEX_JSON_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    queue_rows = read_csv(Path(args.queue))
    profile_rows = read_csv(Path(args.profile_tracker))
    setup = read_json(Path(args.profile_setup))
    weeks = available_weeks(queue_rows) if args.all else [selected_week(queue_rows, args.week)]
    sheets = [build_sheet(queue_rows, profile_rows, setup, week) for week in weeks]
    if not args.check:
        if args.all:
            for sheet in sheets:
                output, json_output = week_output_paths(int(sheet["week"]))
                write_sheet(sheet, output, json_output)
            write_index(sheets, Path(args.index_output), Path(args.index_json_output))
            print(f"promotion_execution_sheet_index={args.index_output}")
            print(f"promotion_execution_sheet_index_json={args.index_json_output}")
        else:
            write_sheet(sheets[0], Path(args.output), Path(args.json_output))
            print(f"promotion_execution_sheet={args.output}")
            print(f"promotion_execution_sheet_json={args.json_output}")
    issue_count = sum(len(sheet["issues"]) for sheet in sheets)
    print(f"promotion_execution_sheet_weeks={len(sheets)}")
    print(f"promotion_execution_sheet_profile_gates={sum(sheet['profileGateCount'] for sheet in sheets)}")
    print(f"promotion_execution_sheet_profile_pending={sum(sheet['profilePendingCount'] for sheet in sheets)}")
    print(f"promotion_execution_sheet_platform_posts={sum(sheet['platformPostCount'] for sheet in sheets)}")
    print(f"promotion_execution_sheet_scripts={sum(sheet['scriptCount'] for sheet in sheets)}")
    print(f"promotion_execution_sheet_issues={issue_count}")
    for sheet in sheets:
        for issue in sheet["issues"]:
            print(f"week {sheet['week']}: {issue}")
    return 1 if issue_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
