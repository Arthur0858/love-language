#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
DEFAULT_WEEK = 1
DEFAULT_WEEKS = [1, 2, 3, 4, 5]
HASHTAGS = ["#五種愛之語測驗", "#情感守護者", "#心語庭園", "#錯頻修復", "#LoveTypes"]
KPI_FIELDS = [
    "week",
    "slot",
    "task_id",
    "date",
    "platform",
    "post_url",
    "script_id",
    "guardian_id",
    "guardian_name",
    "content_angle",
    "utm_content",
    "tracked_url",
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
    "notes",
]


def load_tasks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("publishingTasks", [])
    return tasks if isinstance(tasks, list) else []


def select_week_tasks(tasks: list[dict], week: int) -> list[dict]:
    selected = [task for task in tasks if int(task.get("week", 0) or 0) == week]
    return sorted(selected, key=lambda task: int(task.get("slot", 0) or 0))


def caption_for(task: dict) -> str:
    lines = [
        str(task.get("hook", "")).strip(),
        "",
        f"完成 15 題測驗，找到你的情感守護者：{task.get('trackedUrl', '')}",
        "",
        str(task.get("commentCta", "")).strip(),
        " ".join(HASHTAGS),
    ]
    return "\n".join(line for line in lines if line or line == "")


def kpi_row_template(task: dict) -> dict[str, str]:
    row = {field: "" for field in KPI_FIELDS}
    row["week"] = str(task.get("week", ""))
    row["slot"] = str(task.get("slot", ""))
    row["task_id"] = str(task.get("taskId", ""))
    row["script_id"] = str(task.get("scriptId", ""))
    row["guardian_id"] = str(task.get("guardianId", ""))
    row["guardian_name"] = str(task.get("guardianName", ""))
    row["content_angle"] = str(task.get("contentAngle", ""))
    row["utm_content"] = str(task.get("utmContent", ""))
    row["tracked_url"] = str(task.get("trackedUrl", ""))
    row["notes"] = str(task.get("notes", ""))
    return row


def task_payload(task: dict) -> dict:
    bridge = task.get("monetizationBridge", {})
    return {
        "taskId": task.get("taskId"),
        "week": task.get("week"),
        "slot": task.get("slot"),
        "status": task.get("status"),
        "guardianId": task.get("guardianId"),
        "guardianName": task.get("guardianName"),
        "scriptId": task.get("scriptId"),
        "contentAngle": task.get("contentAngle"),
        "title": task.get("title"),
        "hook": task.get("hook"),
        "caption": caption_for(task),
        "trackedUrl": task.get("trackedUrl"),
        "utmContent": task.get("utmContent"),
        "subtitleLines": task.get("subtitleLines", []),
        "visualSuggestions": task.get("visualSuggestions", []),
        "commentCta": task.get("commentCta"),
        "conversionPath": task.get("conversionPath", {}),
        "monetizationBridge": {
            "primaryFreeItemId": bridge.get("primaryFreeItemId"),
            "ownedLeadItemId": bridge.get("ownedLeadItemId"),
            "playbookSequence": bridge.get("playbookSequence", []),
            "recommendedFirstAction": bridge.get("recommendedFirstAction", ""),
            "safetyNote": bridge.get("safetyNote", ""),
        },
        "kpiRowTemplate": kpi_row_template(task),
    }


def build_pack(tasks: list[dict], week: int) -> dict:
    selected = select_week_tasks(tasks, week)
    return {
        "generatedAt": date.today().isoformat(),
        "campaign": "first_round_quiz_completion",
        "week": week,
        "taskCount": len(selected),
        "primaryCta": "完成 15 題測驗，找到你的情感守護者",
        "publishingRules": [
            "每支 Shorts 只放一個主 CTA：完成 15 題測驗。",
            "說明欄使用 trackedUrl；若平台不允許長連結，至少保留 https://lovetypes.tw/start/。",
            "不把守護者結果描述成診斷、療效、保證修復或購買要求。",
            "發布後回填 kpi-tracker.csv，先看 quiz_completions，再看獲利意圖欄位。",
        ],
        "tasks": [task_payload(task) for task in selected],
    }


def build_markdown(pack: dict) -> str:
    lines = [
        f"# LoveTypes 第一輪 Week {pack['week']} 發布包",
        "",
        f"- 產生日期：{pack['generatedAt']}",
        f"- 任務數：{pack['taskCount']}",
        f"- 主 CTA：{pack['primaryCta']}",
        "",
        "## 發布規則",
        "",
    ]
    lines.extend(f"- {rule}" for rule in pack["publishingRules"])
    for task in pack["tasks"]:
        bridge = task["monetizationBridge"]
        paths = task["conversionPath"]
        lines.extend([
            "",
            f"## {task['slot']}. {task['title']}",
            "",
            f"- 任務：{task['taskId']}",
            f"- 守護者：{task['guardianName']}（{task['guardianId']}）",
            f"- 內容角度：{task['contentAngle']}",
            f"- 追蹤連結：{task['trackedUrl']}",
            f"- UTM content：{task['utmContent']}",
            "",
            "### 說明欄文案",
            "",
            "```text",
            task["caption"],
            "```",
            "",
            "### 字幕節奏",
            "",
        ])
        lines.extend(f"{index}. {line}" for index, line in enumerate(task["subtitleLines"], start=1))
        lines.extend([
            "",
            "### 視覺提示",
            "",
        ])
        lines.extend(f"- {item}" for item in task["visualSuggestions"])
        lines.extend([
            "",
            "### 結果後承接",
            "",
            f"- 守護者頁：{paths.get('guardianProfile', '')}",
            f"- 補給路線：{paths.get('supplyRoute', '')}",
            f"- 修復計畫：{paths.get('repairPlan', '')}",
            f"- Luna：{paths.get('lunaScene', '')}",
            f"- 收藏物：{paths.get('keepsake', '')}",
            f"- Contact：{paths.get('contactRequest', '')}",
            f"- 免費資產：{bridge.get('primaryFreeItemId', '')}",
            f"- 名單承接：{bridge.get('ownedLeadItemId', '')}",
            f"- 安全提醒：{bridge.get('safetyNote', '')}",
            "",
            "### KPI 回填起點",
            "",
            f"- `script_id`: `{task['scriptId']}`",
            f"- `guardian_id`: `{task['guardianId']}`",
            "- 發布後至少回填：`post_url`、`site_clicks`、`quiz_starts`、`quiz_completions`",
            "- 有結果後互動時回填：`free_keepsake_downloads`、`supply_lead_requests`、`luna_pack_clicks`、`affiliate_book_clicks`、`contact_requests`",
        ])
    return "\n".join(lines).rstrip() + "\n"


def build_index(packs: list[dict]) -> dict:
    return {
        "generatedAt": date.today().isoformat(),
        "campaign": "first_round_quiz_completion",
        "weekCount": len(packs),
        "taskCount": sum(pack["taskCount"] for pack in packs),
        "weeks": [
            {
                "week": pack["week"],
                "taskCount": pack["taskCount"],
                "markdown": f"week-{pack['week']}-publish-pack.md",
                "json": f"week-{pack['week']}-publish-pack.json",
                "guardians": [task.get("guardianId") for task in pack["tasks"]],
                "taskIds": [task.get("taskId") for task in pack["tasks"]],
            }
            for pack in packs
        ],
    }


def build_index_markdown(index: dict) -> str:
    lines = [
        "# LoveTypes 第一輪發布包索引",
        "",
        f"- 產生日期：{index['generatedAt']}",
        f"- 週數：{index['weekCount']}",
        f"- 任務數：{index['taskCount']}",
        "",
        "## Weeks",
        "",
    ]
    for week in index["weeks"]:
        lines.extend([
            f"### Week {week['week']}",
            "",
            f"- 任務數：{week['taskCount']}",
            f"- Markdown：`{week['markdown']}`",
            f"- JSON：`{week['json']}`",
            f"- 守護者：{', '.join(week['guardians'])}",
            f"- 任務：{', '.join(week['taskIds'])}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def validate_pack(pack: dict, week: int, expected_task_count: int) -> list[str]:
    issues = []
    if pack["taskCount"] != expected_task_count:
        issues.append(f"expected {expected_task_count} tasks for week {week}, got {pack['taskCount']}")
    for task in pack["tasks"]:
        if not task.get("trackedUrl") or "utm_content=" not in task["trackedUrl"]:
            issues.append(f"{task.get('taskId')}: missing trackedUrl UTM content")
        if not task.get("caption") or task.get("trackedUrl") not in task.get("caption", ""):
            issues.append(f"{task.get('taskId')}: caption should include trackedUrl")
        bridge = task.get("monetizationBridge", {})
        if not bridge.get("primaryFreeItemId") or not bridge.get("ownedLeadItemId"):
            issues.append(f"{task.get('taskId')}: missing monetization bridge items")
        if not task.get("kpiRowTemplate", {}).get("script_id"):
            issues.append(f"{task.get('taskId')}: missing KPI row template")
    markdown = build_markdown(pack)
    if not markdown.startswith(f"# LoveTypes 第一輪 Week {week} 發布包"):
        issues.append("markdown pack missing title")
    return issues


def write_pack(pack: dict, output: Path, json_output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_markdown(pack), encoding="utf-8")
    json_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a LoveTypes weekly Shorts publishing pack.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--week", type=int, default=DEFAULT_WEEK)
    parser.add_argument("--all", action="store_true", help="Generate or validate all first-round weekly packs.")
    parser.add_argument("--output", default="")
    parser.add_argument("--json-output", default="")
    parser.add_argument("--check", action="store_true", help="Validate the selected week pack without writing files.")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    tasks = load_tasks(Path(args.kit))
    weeks = DEFAULT_WEEKS if args.all else [args.week]
    packs = [build_pack(tasks, week) for week in weeks]
    pack = packs[0]
    markdown = build_markdown(pack)
    if args.check:
        issues = []
        for candidate in packs:
            expected_task_count = len(select_week_tasks(tasks, int(candidate["week"])))
            issues.extend(validate_pack(candidate, int(candidate["week"]), expected_task_count))
        print(f"promotion_publish_pack_week={'all' if args.all else args.week}")
        print(f"promotion_publish_pack_weeks={len(packs)}")
        print(f"promotion_publish_pack_tasks={sum(candidate['taskCount'] for candidate in packs)}")
        print(f"promotion_publish_pack_issues={len(issues)}")
        for issue in issues:
            print(issue)
        return 1 if issues else 0
    elif args.stdout:
        if args.all:
            print(build_index_markdown(build_index(packs)), end="")
            return 0
        print(markdown, end="")
    else:
        if args.all:
            for candidate in packs:
                output = PROMOTION_DIR / f"week-{candidate['week']}-publish-pack.md"
                json_output = PROMOTION_DIR / f"week-{candidate['week']}-publish-pack.json"
                write_pack(candidate, output, json_output)
            index = build_index(packs)
            index_output = PROMOTION_DIR / "publish-pack-index.md"
            index_json_output = PROMOTION_DIR / "publish-pack-index.json"
            index_output.write_text(build_index_markdown(index), encoding="utf-8")
            index_json_output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"promotion_publish_pack_index={index_output}")
            print(f"promotion_publish_pack_index_json={index_json_output}")
            print(f"promotion_publish_pack_weeks={len(packs)}")
            print(f"promotion_publish_pack_tasks={index['taskCount']}")
        else:
            output = Path(args.output) if args.output else PROMOTION_DIR / f"week-{args.week}-publish-pack.md"
            json_output = Path(args.json_output) if args.json_output else PROMOTION_DIR / f"week-{args.week}-publish-pack.json"
            write_pack(pack, output, json_output)
            print(f"promotion_publish_pack={output}")
            print(f"promotion_publish_pack_json={json_output}")
            print(f"promotion_publish_pack_tasks={pack['taskCount']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
