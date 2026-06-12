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
HASHTAGS = ["#五種愛之語測驗", "#情感守護者", "#心語庭園", "#錯頻修復", "#LoveTypes"]
KPI_FIELDS = [
    "date",
    "platform",
    "post_url",
    "script_id",
    "guardian_id",
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
    row["script_id"] = str(task.get("scriptId", ""))
    row["guardian_id"] = str(task.get("guardianId", ""))
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a LoveTypes weekly Shorts publishing pack.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--week", type=int, default=DEFAULT_WEEK)
    parser.add_argument("--output", default="")
    parser.add_argument("--json-output", default="")
    parser.add_argument("--check", action="store_true", help="Validate the selected week pack without writing files.")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    pack = build_pack(load_tasks(Path(args.kit)), args.week)
    markdown = build_markdown(pack)
    if args.check:
        issues = []
        if pack["taskCount"] != 3:
            issues.append(f"expected 3 tasks for week {args.week}, got {pack['taskCount']}")
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
        if not markdown.startswith(f"# LoveTypes 第一輪 Week {args.week} 發布包"):
            issues.append("markdown pack missing title")
        print(f"promotion_publish_pack_week={args.week}")
        print(f"promotion_publish_pack_tasks={pack['taskCount']}")
        print(f"promotion_publish_pack_issues={len(issues)}")
        for issue in issues:
            print(issue)
        return 1 if issues else 0
    elif args.stdout:
        print(markdown, end="")
    else:
        output = Path(args.output) if args.output else PROMOTION_DIR / f"week-{args.week}-publish-pack.md"
        json_output = Path(args.json_output) if args.json_output else PROMOTION_DIR / f"week-{args.week}-publish-pack.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        json_output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        json_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"promotion_publish_pack={output}")
        print(f"promotion_publish_pack_json={json_output}")
        print(f"promotion_publish_pack_tasks={pack['taskCount']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
