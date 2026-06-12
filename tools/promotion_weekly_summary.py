#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
KIT_PATH = ROOT / "promotion-kit.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "weekly-summary.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "weekly-summary.json"

NUMERIC_FIELDS = [
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
]
ACTIVITY_FIELDS = ["date", "platform", "post_url"]
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


def read_tracker(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def is_filled(row: dict[str, str]) -> bool:
    if any((row.get(field) or "").strip() for field in ACTIVITY_FIELDS):
        return True
    return any(parse_int(row.get(field)) > 0 for field in NUMERIC_FIELDS)


def is_profile_filled(row: dict[str, str]) -> bool:
    status = (row.get("status") or "").strip().lower()
    if status in {"set", "live"}:
        return True
    if (row.get("profile_link_set_date") or "").strip():
        return True
    return any(parse_int(row.get(field)) > 0 for field in NUMERIC_FIELDS)


def load_tasks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("publishingTasks", [])
    return tasks if isinstance(tasks, list) else []


def sum_fields(rows: list[dict[str, str]]) -> Counter:
    totals: Counter = Counter()
    for row in rows:
        for field in NUMERIC_FIELDS:
            totals[field] += parse_int(row.get(field))
    return totals


def rate(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "n/a"
    return f"{numerator / denominator:.1%}"


def rate_value(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def format_rate_value(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


def top_counter(counter: Counter) -> tuple[str, int] | None:
    if not counter:
        return None
    key, value = counter.most_common(1)[0]
    if value <= 0:
        return None
    return key, value


def planned_task_summary(tasks: list[dict]) -> tuple[int, Counter, list[str]]:
    planned = [task for task in tasks if task.get("status") == "planned"]
    by_guardian = Counter(task.get("guardianId", "unknown") for task in planned)
    next_tasks = [
        f"{task.get('taskId')} ({task.get('guardianName')} / {task.get('contentAngle')})"
        for task in planned[:3]
    ]
    return len(planned), by_guardian, next_tasks


def add_counters(left: Counter, right: Counter) -> Counter:
    total = Counter(left)
    total.update(right)
    return total


def build_report(
    fields: list[str],
    rows: list[dict[str, str]],
    tasks: list[dict],
    profile_fields: list[str] | None = None,
    profile_rows: list[dict[str, str]] | None = None,
) -> dict:
    filled_rows = [row for row in rows if is_filled(row)]
    profile_fields = profile_fields or []
    profile_rows = profile_rows or []
    filled_profile_rows = [row for row in profile_rows if is_profile_filled(row)]
    video_totals = sum_fields(filled_rows)
    profile_totals = sum_fields(filled_profile_rows)
    totals = add_counters(video_totals, profile_totals)
    planned_count, planned_by_guardian, next_tasks = planned_task_summary(tasks)
    guardian_quiz = Counter()
    guardian_revenue = Counter()
    angle_quiz = Counter()
    missing_fields = [field for field in REVENUE_FIELDS if field not in fields]
    profile_missing_fields = [field for field in REVENUE_FIELDS if profile_fields and field not in profile_fields]

    for row in filled_rows:
        guardian = (row.get("guardian_id") or "unknown").strip() or "unknown"
        script_id = (row.get("script_id") or "").strip()
        task = next((item for item in tasks if item.get("scriptId") == script_id), {})
        angle = (task.get("contentAngle") or "unknown").strip()
        quiz_completions = parse_int(row.get("quiz_completions"))
        revenue_intent = sum(parse_int(row.get(field)) for field in REVENUE_FIELDS)
        guardian_quiz[guardian] += quiz_completions
        guardian_revenue[guardian] += revenue_intent
        angle_quiz[angle] += quiz_completions

    top_guardian = top_counter(guardian_quiz)
    top_revenue_guardian = top_counter(guardian_revenue)
    top_angle = top_counter(angle_quiz)
    route_interest = totals["resources_clicks"] + totals["repair_plan_clicks"] + totals["luna_clicks"] + totals["keepsake_clicks"]
    revenue_total = sum(totals[field] for field in REVENUE_FIELDS)
    lead_total = totals["supply_lead_requests"] + totals["contact_requests"]
    paid_revenue_intent = totals["luna_pack_clicks"] + totals["affiliate_book_clicks"]
    recommendations: list[str] = []
    if not filled_rows and not filled_profile_rows:
        recommendations.extend([
            "先發布前 3 個 planned 任務，保持單一 CTA：完成 15 題測驗，找到你的情感守護者。",
            "發布後至少回填 post_url、site_clicks、quiz_starts、quiz_completions。",
            "完成平台首頁設定後，同步回填 platform-profile-tracker.csv，分開判讀 Bio/Profile link 成效。",
            "若有使用者點擊結果後路線，務必回填收藏物、補給名單、Luna、聯盟書卷與 Contact 欄位。",
        ])
        if next_tasks:
            recommendations.append("下一批建議任務：" + "；".join(next_tasks))
    else:
        if totals["site_clicks"] > 0 and totals["quiz_starts"] * 10 < totals["site_clicks"] * 3:
            recommendations.append("修首頁或 /start/ 首屏：網站點擊有進來，但測驗開始率低於 30%。")
        if totals["quiz_starts"] > 0 and totals["quiz_completions"] * 10 < totals["quiz_starts"] * 4:
            recommendations.append("修測驗流程：測驗完成率低於 40%，優先檢查手機版題目節奏與結果揭示。")
        if lead_total > 0:
            recommendations.append("補自有資產：已有補給或 Contact 需求，優先做對應守護者的 PDF、桌布或短儀式。")
        if paid_revenue_intent > 0:
            recommendations.append("測試柔性商品承接：已有 Luna 或聯盟意圖，下支內容仍以測驗為 CTA，商品只放在結果後路線。")
        if top_guardian:
            recommendations.append(f"放大 {top_guardian[0]}：下一週多做一支同守護者、不同痛點的變體。")
        if not recommendations:
            recommendations.append("數據不足以調整策略，先補足本週回填。")

    return {
        "generatedAt": date.today().isoformat(),
        "trackerTotalRows": len(rows),
        "trackerRows": len(filled_rows),
        "profileTrackerTotalRows": len(profile_rows),
        "profileTrackerRows": len(filled_profile_rows),
        "plannedTasks": planned_count,
        "fieldStatus": {
            "complete": not missing_fields and not profile_missing_fields,
            "missingFields": missing_fields,
            "profileMissingFields": profile_missing_fields,
        },
        "totals": {field: int(totals[field]) for field in NUMERIC_FIELDS},
        "sourceBreakdown": {
            "videoTracker": {
                "rows": len(filled_rows),
                "totalRows": len(rows),
                "totals": {field: int(video_totals[field]) for field in NUMERIC_FIELDS},
            },
            "platformProfileTracker": {
                "rows": len(filled_profile_rows),
                "totalRows": len(profile_rows),
                "totals": {field: int(profile_totals[field]) for field in NUMERIC_FIELDS},
            },
        },
        "derived": {
            "siteClickRate": rate_value(totals["site_clicks"], totals["profile_clicks"]),
            "quizStartRate": rate_value(totals["quiz_starts"], totals["site_clicks"]),
            "quizCompletionRate": rate_value(totals["quiz_completions"], totals["quiz_starts"]),
            "routeInterestRate": rate_value(route_interest, totals["quiz_completions"]),
            "revenueIntentRate": rate_value(paid_revenue_intent, totals["quiz_completions"]),
            "leadCaptureRate": rate_value(lead_total, totals["quiz_completions"]),
        },
        "computedTotals": {
            "routeInterest": int(route_interest),
            "revenueIntent": int(revenue_total),
            "paidRevenueIntent": int(paid_revenue_intent),
            "leadIntent": int(lead_total),
        },
        "leaders": {
            "quizGuardian": {"id": top_guardian[0], "value": top_guardian[1]} if top_guardian else None,
            "revenueGuardian": {"id": top_revenue_guardian[0], "value": top_revenue_guardian[1]} if top_revenue_guardian else None,
            "contentAngle": {"id": top_angle[0], "value": top_angle[1]} if top_angle else None,
        },
        "recommendations": recommendations,
        "plannedTaskDistribution": dict(sorted(planned_by_guardian.items())),
        "nextPlannedTasks": next_tasks,
        "safety": {
            "emptyDataMode": not filled_rows and not filled_profile_rows,
            "emptyDataNote": "Do not change product, offer, or guardian priorities from empty tracker data." if not filled_rows and not filled_profile_rows else "",
        },
    }


def build_summary(report: dict) -> str:
    totals = report["totals"]
    derived = report["derived"]
    computed = report["computedTotals"]
    leaders = report["leaders"]
    field_status = report["fieldStatus"]
    missing_fields = field_status["missingFields"]
    profile_missing_fields = field_status.get("profileMissingFields", [])
    source_breakdown = report["sourceBreakdown"]
    lines = [
        "# LoveTypes 第一輪推廣週摘要",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- 影片追蹤列數：{report['trackerRows']} / {report.get('trackerTotalRows', report['trackerRows'])}",
        f"- 平台首頁追蹤列數：{report['profileTrackerRows']} / {report.get('profileTrackerTotalRows', report['profileTrackerRows'])}",
        f"- 已規劃待發布任務：{report['plannedTasks']}",
        f"- 追蹤欄位狀態：{'完整' if field_status['complete'] else '缺少 ' + ', '.join([*missing_fields, *profile_missing_fields])}",
        "",
        "## 漏斗總覽",
        "",
        f"- 觀看：{totals['views']}",
        f"- 個人檔案點擊：{totals['profile_clicks']}",
        f"- 網站點擊：{totals['site_clicks']}（site click rate: {rate(totals['site_clicks'], totals['profile_clicks'])}）",
        f"- 測驗開始：{totals['quiz_starts']}（quiz start rate: {rate(totals['quiz_starts'], totals['site_clicks'])}）",
        f"- 測驗完成：{totals['quiz_completions']}（completion rate: {rate(totals['quiz_completions'], totals['quiz_starts'])}）",
        f"- 路線興趣：{computed['routeInterest']}（route interest rate: {format_rate_value(derived['routeInterestRate'])}）",
        f"- 獲利意圖：{computed['revenueIntent']}（revenue intent rate: {format_rate_value(derived['revenueIntentRate'])}）",
        f"- 名單/需求意圖：{computed['leadIntent']}（lead capture rate: {format_rate_value(derived['leadCaptureRate'])}）",
        "",
        "## 來源拆分",
        "",
        f"- 單支影片網站點擊：{source_breakdown['videoTracker']['totals']['site_clicks']}；測驗完成：{source_breakdown['videoTracker']['totals']['quiz_completions']}",
        f"- Bio/Profile 網站點擊：{source_breakdown['platformProfileTracker']['totals']['site_clicks']}；測驗完成：{source_breakdown['platformProfileTracker']['totals']['quiz_completions']}",
        "",
        "## 守護者與內容角度",
        "",
    ]
    if report["trackerRows"]:
        lines.extend([
            f"- 測驗完成最高守護者：{leaders['quizGuardian']['id']}（{leaders['quizGuardian']['value']}）" if leaders["quizGuardian"] else "- 測驗完成最高守護者：尚無",
            f"- 獲利意圖最高守護者：{leaders['revenueGuardian']['id']}（{leaders['revenueGuardian']['value']}）" if leaders["revenueGuardian"] else "- 獲利意圖最高守護者：尚無",
            f"- 測驗完成最高內容角度：{leaders['contentAngle']['id']}（{leaders['contentAngle']['value']}）" if leaders["contentAngle"] else "- 測驗完成最高內容角度：尚無",
        ])
    else:
        lines.extend([
            "- 尚未有已發布且已回填的追蹤列，不能判斷優勝守護者或內容角度。",
            "- 目前應先完成發布與回填，不應根據空資料調整商品或文案。",
        ])

    lines.extend(["", "## 下一週建議", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])

    lines.extend(["", "## Planned 任務分布", ""])
    for guardian, count in report["plannedTaskDistribution"].items():
        lines.append(f"- {guardian}: {count}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a LoveTypes first-round promotion weekly summary.")
    parser.add_argument("--tracker", default=str(TRACKER_PATH))
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--profile-tracker", default=str(PROFILE_TRACKER_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true", help="Validate the summary inputs and report shape without writing files.")
    parser.add_argument("--stdout", action="store_true", help="Print the summary instead of writing a file.")
    args = parser.parse_args()

    fields, rows = read_tracker(Path(args.tracker))
    profile_fields, profile_rows = read_tracker(Path(args.profile_tracker))
    tasks = load_tasks(Path(args.kit))
    report = build_report(fields, rows, tasks, profile_fields, profile_rows)
    summary = build_summary(report)
    if args.check:
        required_report_keys = {
            "generatedAt",
            "trackerRows",
            "trackerTotalRows",
            "profileTrackerRows",
            "profileTrackerTotalRows",
            "plannedTasks",
            "fieldStatus",
            "totals",
            "sourceBreakdown",
            "derived",
            "computedTotals",
            "leaders",
            "recommendations",
            "plannedTaskDistribution",
            "nextPlannedTasks",
            "safety",
        }
        issues = []
        if not required_report_keys.issubset(report):
            issues.append("report missing required keys")
        if report["fieldStatus"]["missingFields"]:
            issues.append("tracker missing revenue fields")
        if report["fieldStatus"].get("profileMissingFields"):
            issues.append("profile tracker missing revenue fields")
        if len(report["recommendations"]) < 1:
            issues.append("report should include at least one recommendation")
        if not summary.startswith("# LoveTypes 第一輪推廣週摘要"):
            issues.append("markdown summary missing title")
        print(f"promotion_weekly_summary_tracker_rows={report['trackerRows']}")
        print(f"promotion_weekly_summary_profile_tracker_rows={report['profileTrackerRows']}")
        print(f"promotion_weekly_summary_recommendations={len(report['recommendations'])}")
        print(f"promotion_weekly_summary_empty_data_mode={int(report['safety']['emptyDataMode'])}")
        print(f"promotion_weekly_summary_issues={len(issues)}")
        for issue in issues:
            print(issue)
        return 1 if issues else 0
    elif args.stdout:
        print(summary, end="")
    else:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary, encoding="utf-8")
        json_output_path = Path(args.json_output)
        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        json_output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"promotion_weekly_summary={output_path}")
        print(f"promotion_weekly_summary_json={json_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
