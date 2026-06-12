#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

from promotion_weekly_summary import build_report, load_tasks, read_tracker


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
KIT_PATH = ROOT / "promotion-kit.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "next-actions.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "next-actions.json"
REVENUE_FIELDS = [
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def filled_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if any((value or "").strip() for value in row.values())]


def tasks_by_script(tasks: list[dict]) -> dict[str, dict]:
    return {str(task.get("scriptId", "")): task for task in tasks}


def planned_tasks(tasks: list[dict]) -> list[dict]:
    return sorted(
        [task for task in tasks if task.get("status") == "planned"],
        key=lambda task: (int(task.get("week", 0) or 0), int(task.get("slot", 0) or 0)),
    )


def score_rows(rows: list[dict[str, str]], tasks: list[dict]) -> tuple[Counter, Counter, Counter]:
    script_lookup = tasks_by_script(tasks)
    guardian_scores = Counter()
    angle_scores = Counter()
    revenue_scores = Counter()
    for row in rows:
        guardian = (row.get("guardian_id") or "unknown").strip() or "unknown"
        task = script_lookup.get((row.get("script_id") or "").strip(), {})
        angle = task.get("contentAngle") or "unknown"
        quiz = parse_int(row.get("quiz_completions"))
        route = (
            parse_int(row.get("resources_clicks"))
            + parse_int(row.get("repair_plan_clicks"))
            + parse_int(row.get("luna_clicks"))
            + parse_int(row.get("keepsake_clicks"))
        )
        revenue = sum(parse_int(row.get(field)) for field in REVENUE_FIELDS)
        score = quiz * 3 + route + revenue * 2
        guardian_scores[guardian] += score
        angle_scores[angle] += score
        revenue_scores[guardian] += revenue
    return guardian_scores, angle_scores, revenue_scores


def top_key(counter: Counter) -> str | None:
    if not counter:
        return None
    key, value = counter.most_common(1)[0]
    return key if value > 0 else None


def select_followup_tasks(tasks: list[dict], guardian: str | None, angle: str | None) -> list[dict]:
    pool = planned_tasks(tasks)
    if guardian:
        matching_guardian = [task for task in pool if task.get("guardianId") == guardian]
        if matching_guardian:
            pool = matching_guardian
    if angle:
        matching_angle = [task for task in pool if task.get("contentAngle") == angle]
        if matching_angle:
            return matching_angle[:3]
    return pool[:3]


def task_summary(task: dict) -> dict:
    bridge = task.get("monetizationBridge", {})
    path = task.get("conversionPath", {})
    return {
        "taskId": task.get("taskId"),
        "week": task.get("week"),
        "slot": task.get("slot"),
        "guardianId": task.get("guardianId"),
        "guardianName": task.get("guardianName"),
        "contentAngle": task.get("contentAngle"),
        "title": task.get("title"),
        "trackedUrl": task.get("trackedUrl"),
        "primaryFreeItemId": bridge.get("primaryFreeItemId"),
        "ownedLeadItemId": bridge.get("ownedLeadItemId"),
        "supplyRoute": path.get("supplyRoute"),
        "lunaScene": path.get("lunaScene"),
        "keepsake": path.get("keepsake"),
    }


def build_actions(fields: list[str], rows: list[dict[str, str]], tasks: list[dict]) -> dict:
    report = build_report(fields, rows, tasks)
    active_rows = filled_rows(rows)
    guardian_scores, angle_scores, revenue_scores = score_rows(active_rows, tasks)
    top_guardian = top_key(guardian_scores)
    top_angle = top_key(angle_scores)
    top_revenue_guardian = top_key(revenue_scores)
    selected = select_followup_tasks(tasks, top_guardian, top_angle)
    actions = []
    if not active_rows:
        selected = planned_tasks(tasks)[:3]
        actions.extend([
            {
                "id": "publish_first_batch",
                "priority": "high",
                "type": "execution",
                "summary": "發布 Week 1 前 3 支 Shorts，先取得測驗完成樣本。",
            },
            {
                "id": "fill_required_kpis",
                "priority": "high",
                "type": "measurement",
                "summary": "發布後至少回填 post_url、site_clicks、quiz_starts、quiz_completions。",
            },
            {
                "id": "hold_offer_changes",
                "priority": "medium",
                "type": "safety",
                "summary": "目前沒有回填數據，不調整商品、守護者優先序或付費 CTA。",
            },
        ])
    else:
        derived = report["derived"]
        if derived["quizStartRate"] is not None and derived["quizStartRate"] < 0.3:
            actions.append({
                "id": "repair_start_landing",
                "priority": "high",
                "type": "site",
                "summary": "網站點擊有進來但測驗開始率低，優先檢查 /start/ 首屏與 CTA。",
            })
        if derived["quizCompletionRate"] is not None and derived["quizCompletionRate"] < 0.4:
            actions.append({
                "id": "repair_quiz_completion",
                "priority": "high",
                "type": "site",
                "summary": "測驗完成率偏低，優先檢查手機版題目節奏與結果揭示。",
            })
        if top_revenue_guardian:
            actions.append({
                "id": "build_guardian_asset",
                "priority": "high",
                "type": "offer",
                "summary": f"{top_revenue_guardian} 已有獲利意圖，優先補免費 PDF、桌布、短儀式或 Luna 承接。",
            })
        if top_guardian:
            actions.append({
                "id": "scale_best_guardian",
                "priority": "medium",
                "type": "content",
                "summary": f"放大 {top_guardian}，下一批發布同守護者不同痛點變體。",
            })
        if not actions:
            actions.append({
                "id": "collect_more_data",
                "priority": "medium",
                "type": "measurement",
                "summary": "目前數據不足以調整策略，先補足回填並維持原排程。",
            })
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "tracker": str(TRACKER_PATH.relative_to(ROOT)),
            "promotionKit": str(KIT_PATH.relative_to(ROOT)),
        },
        "dataState": {
            "trackerRows": report["trackerRows"],
            "emptyDataMode": report["safety"]["emptyDataMode"],
            "fieldComplete": report["fieldStatus"]["complete"],
        },
        "leaders": {
            "guardian": top_guardian,
            "contentAngle": top_angle,
            "revenueGuardian": top_revenue_guardian,
        },
        "scores": {
            "guardians": dict(sorted(guardian_scores.items())),
            "contentAngles": dict(sorted(angle_scores.items())),
            "revenueGuardians": dict(sorted(revenue_scores.items())),
        },
        "actions": actions,
        "selectedTasks": [task_summary(task) for task in selected],
        "safety": {
            "doNotChangeOffersFromEmptyData": not active_rows,
            "doNotUseDiagnosisClaims": True,
            "keepShortsCtaQuizOnly": True,
        },
    }


def build_markdown(plan: dict) -> str:
    lines = [
        "# LoveTypes 下一批推廣動作建議",
        "",
        f"- 產生日期：{plan['generatedAt']}",
        f"- 追蹤列數：{plan['dataState']['trackerRows']}",
        f"- 空資料安全模式：{'是' if plan['dataState']['emptyDataMode'] else '否'}",
        "",
        "## 優先動作",
        "",
    ]
    for action in plan["actions"]:
        lines.append(f"- [{action['priority']}] {action['summary']}")
    lines.extend(["", "## 建議發布任務", ""])
    for task in plan["selectedTasks"]:
        lines.extend([
            f"### {task['taskId']}",
            "",
            f"- Week/Slot：{task['week']} / {task['slot']}",
            f"- 守護者：{task['guardianName']}（{task['guardianId']}）",
            f"- 內容角度：{task['contentAngle']}",
            f"- 標題：{task['title']}",
            f"- 追蹤連結：{task['trackedUrl']}",
            f"- 免費資產：{task['primaryFreeItemId']}",
            f"- 名單承接：{task['ownedLeadItemId']}",
            f"- 補給路線：{task['supplyRoute']}",
            f"- Luna：{task['lunaScene']}",
            f"- 收藏物：{task['keepsake']}",
            "",
        ])
    lines.extend([
        "## 安全邊界",
        "",
        "- Shorts CTA 維持測驗，不直接導購。",
        "- 不把守護者結果描述成診斷、療效或保證修復。",
        "- 空資料時不調整商品、守護者優先序或付費 CTA。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate LoveTypes next promotion actions from KPI tracker data.")
    parser.add_argument("--tracker", default=str(TRACKER_PATH))
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--output", default=str(PROMOTION_DIR / "next-actions.md"))
    parser.add_argument("--json-output", default=str(PROMOTION_DIR / "next-actions.json"))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    fields, rows = read_tracker(Path(args.tracker))
    tasks = load_tasks(Path(args.kit))
    plan = build_actions(fields, rows, tasks)
    markdown = build_markdown(plan)
    if args.check:
        issues = []
        if len(plan["actions"]) < 1:
            issues.append("expected at least one action")
        if len(plan["selectedTasks"]) < 1:
            issues.append("expected at least one selected task")
        if plan["dataState"]["emptyDataMode"] and not plan["safety"]["doNotChangeOffersFromEmptyData"]:
            issues.append("empty data mode should block offer changes")
        if not markdown.startswith("# LoveTypes 下一批推廣動作建議"):
            issues.append("markdown missing title")
        print(f"promotion_next_actions_selected_tasks={len(plan['selectedTasks'])}")
        print(f"promotion_next_actions_actions={len(plan['actions'])}")
        print(f"promotion_next_actions_empty_data_mode={int(plan['dataState']['emptyDataMode'])}")
        print(f"promotion_next_actions_issues={len(issues)}")
        for issue in issues:
            print(issue)
        return 1 if issues else 0
    if args.stdout:
        print(markdown, end="")
        return 0
    output = Path(args.output)
    json_output = Path(args.json_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    json_output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"promotion_next_actions={output}")
    print(f"promotion_next_actions_json={json_output}")
    print(f"promotion_next_actions_selected_tasks={len(plan['selectedTasks'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
