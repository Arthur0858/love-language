#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from promotion_weekly_summary import is_filled, is_profile_filled


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "revenue-decision-matrix.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "revenue-decision-matrix.json"
REVENUE_FIELDS = [
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]
ROUTE_FIELDS = ["resources_clicks", "repair_plan_clicks", "luna_clicks", "keepsake_clicks"]
GUARDIAN_ORDER = ["iris", "noah", "vivian", "claire", "dora"]
FIELD_MEANINGS = {
    "free_keepsake_downloads": "角色認同與保存意願",
    "supply_lead_requests": "自有名單與補給需求",
    "luna_pack_clicks": "Luna 付費音檔意圖",
    "affiliate_book_clicks": "延伸閱讀購買意圖",
    "contact_requests": "高意圖需求或合作/修復訊號",
}


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


def load_tasks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("publishingTasks", [])
    return tasks if isinstance(tasks, list) else []


def group_tasks(tasks: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for task in tasks:
        grouped[str(task.get("guardianId", ""))].append(task)
    for guardian in grouped:
        grouped[guardian].sort(key=lambda task: (int(task.get("week", 0) or 0), int(task.get("slot", 0) or 0)))
    return grouped


def tracker_totals(rows: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    totals: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        guardian = (row.get("guardian_id") or "unknown").strip() or "unknown"
        if not is_filled(row):
            continue
        totals[guardian]["quiz_completions"] += parse_int(row.get("quiz_completions"))
        for field in ROUTE_FIELDS + REVENUE_FIELDS:
            totals[guardian][field] += parse_int(row.get(field))
    return {guardian: dict(counter) for guardian, counter in totals.items()}


def profile_tracker_totals(rows: list[dict[str, str]]) -> tuple[dict[str, int], list[dict[str, object]]]:
    totals: Counter = Counter()
    platforms: list[dict[str, object]] = []
    metric_fields = ["profile_clicks", "site_clicks", "quiz_starts", "quiz_completions", *ROUTE_FIELDS, *REVENUE_FIELDS]
    for row in rows:
        platform_metrics = {field: parse_int(row.get(field)) for field in metric_fields}
        for field, value in platform_metrics.items():
            totals[field] += value
        platforms.append({
            "platform": (row.get("platform") or "unknown").strip() or "unknown",
            "label": (row.get("label") or "").strip(),
            "profileLink": (row.get("profile_link") or "").strip(),
            "status": (row.get("status") or "").strip(),
            "metrics": platform_metrics,
        })
    return {field: int(totals[field]) for field in metric_fields}, platforms


def decision_stage(metrics: dict[str, int]) -> str:
    quiz = metrics.get("quiz_completions", 0)
    free = metrics.get("free_keepsake_downloads", 0)
    leads = metrics.get("supply_lead_requests", 0) + metrics.get("contact_requests", 0)
    paid = metrics.get("luna_pack_clicks", 0) + metrics.get("affiliate_book_clicks", 0)
    route = sum(metrics.get(field, 0) for field in ROUTE_FIELDS)
    if paid > 0:
        return "test_soft_offer"
    if leads > 0:
        return "build_owned_asset"
    if free > 0 or route > 0:
        return "deepen_identity_asset"
    if quiz >= 10:
        return "publish_guardian_variants"
    return "collect_signal"


def stage_action(stage: str, guardian: str, bridge: dict, path: dict) -> dict:
    free_id = bridge.get("primaryFreeItemId", f"free-keepsake-{guardian}")
    lead_id = bridge.get("ownedLeadItemId", f"supply-wishlist-{guardian}")
    if stage == "test_soft_offer":
        return {
            "priority": "high",
            "action": "測試柔性商品承接",
            "build": "保留測驗 CTA，把 Luna 商品包與聯盟書卷放在結果後補給路線。",
            "target": path.get("lunaScene") or path.get("supplyRoute"),
        }
    if stage == "build_owned_asset":
        return {
            "priority": "high",
            "action": "補自有名單資產",
            "build": f"優先製作或強化 {lead_id}，可選 PDF、桌布、短儀式或 Luna 下載包等待清單。",
            "target": path.get("contactRequest") or path.get("supplyRoute"),
        }
    if stage == "deepen_identity_asset":
        return {
            "priority": "medium",
            "action": "深化免費收藏物",
            "build": f"強化 {free_id} 的故事卡、練習卡或分享圖，先提高保存與分享。",
            "target": path.get("keepsake"),
        }
    if stage == "publish_guardian_variants":
        return {
            "priority": "medium",
            "action": "放大守護者內容變體",
            "build": "同守護者追加不同痛點短片，測試哪個情境帶來測驗完成。",
            "target": path.get("guardianProfile"),
        }
    return {
        "priority": "low",
        "action": "先收集訊號",
        "build": "照既有週次發布並回填，不提前改商品或付費 CTA。",
        "target": path.get("quizEntry"),
    }


def platform_stage_action(stage: str, metrics: dict[str, int]) -> dict:
    if stage == "test_soft_offer":
        return {
            "priority": "high",
            "action": "辨識平台首頁付費意圖來源",
            "build": "先看 utm_content/profile platform，再用下一支內容導向對應測驗結果後路線，不直接導購。",
            "target": "https://lovetypes.tw/start/",
        }
    if stage == "build_owned_asset":
        return {
            "priority": "high",
            "action": "補平台首頁名單承接",
            "build": "在 Bio/Profile link 後續頁強化 Contact、收藏物或等待清單承接，避免只讓流量停在測驗。",
            "target": "https://lovetypes.tw/contact/",
        }
    if stage == "deepen_identity_asset":
        return {
            "priority": "medium",
            "action": "強化首頁測驗後收藏承接",
            "build": "平台首頁已有路線或收藏興趣時，下一輪內容要提醒完成結果後領取守護者收藏物。",
            "target": "https://lovetypes.tw/keepsakes/",
        }
    if stage == "publish_guardian_variants":
        return {
            "priority": "medium",
            "action": "保留測驗 CTA，擴大平台首頁導流",
            "build": "Bio/Profile link 有測驗完成訊號，但尚未出現後段意圖；先用更多情境短片導回同一測驗入口。",
            "target": "https://lovetypes.tw/start/",
        }
    return {
        "priority": "low",
        "action": "先完成平台首頁回填",
        "build": "先設定三平台 Bio/Profile link 並回填 profile_clicks、site_clicks、quiz_starts、quiz_completions。",
        "target": "https://lovetypes.tw/start/",
    }


def guardian_name(tasks: list[dict], guardian: str) -> str:
    for task in tasks:
        if task.get("guardianName"):
            return str(task["guardianName"])
    return guardian


def build_matrix(
    fields: list[str],
    rows: list[dict[str, str]],
    tasks: list[dict],
    profile_fields: list[str] | None = None,
    profile_rows: list[dict[str, str]] | None = None,
) -> dict:
    grouped = group_tasks(tasks)
    metrics_by_guardian = tracker_totals(rows)
    missing_fields = [field for field in REVENUE_FIELDS if field not in fields]
    profile_fields = profile_fields or []
    profile_rows = profile_rows or []
    filled_profile_rows = [row for row in profile_rows if is_profile_filled(row)]
    profile_missing_fields = [field for field in REVENUE_FIELDS if profile_fields and field not in profile_fields]
    platform_metrics, platform_rows = profile_tracker_totals(filled_profile_rows)
    platform_stage = decision_stage(platform_metrics)
    guardians = []
    for guardian in GUARDIAN_ORDER:
        guardian_tasks = grouped.get(guardian, [])
        first_task = guardian_tasks[0] if guardian_tasks else {}
        bridge = first_task.get("monetizationBridge", {}) if isinstance(first_task.get("monetizationBridge"), dict) else {}
        path = first_task.get("conversionPath", {}) if isinstance(first_task.get("conversionPath"), dict) else {}
        metrics = metrics_by_guardian.get(guardian, {})
        stage = decision_stage(metrics)
        action = stage_action(stage, guardian, bridge, path)
        guardians.append({
            "guardianId": guardian,
            "guardianName": guardian_name(guardian_tasks, guardian),
            "week": first_task.get("week"),
            "taskCount": len(guardian_tasks),
            "contentAngles": sorted({str(task.get("contentAngle", "")) for task in guardian_tasks if task.get("contentAngle")}),
            "metrics": {field: int(metrics.get(field, 0)) for field in ["quiz_completions", *ROUTE_FIELDS, *REVENUE_FIELDS]},
            "stage": stage,
            "recommendedAction": action,
            "conversionPath": path,
            "monetizationBridge": {
                "primaryFreeItemId": bridge.get("primaryFreeItemId"),
                "ownedLeadItemId": bridge.get("ownedLeadItemId"),
                "lunaProductIds": bridge.get("lunaProductIds", []),
                "affiliateItemIds": bridge.get("affiliateItemIds", []),
                "successEvents": bridge.get("successEvents", []),
                "safetyNote": bridge.get("safetyNote", ""),
            },
        })
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "tracker": str(TRACKER_PATH.relative_to(ROOT)),
            "platformProfileTracker": str(PROFILE_TRACKER_PATH.relative_to(ROOT)),
            "promotionKit": str(KIT_PATH.relative_to(ROOT)),
        },
        "dataState": {
            "trackerRows": len(rows),
            "filledRows": sum(1 for row in rows if is_filled(row)),
            "profileTrackerRows": len(profile_rows),
            "profileFilledRows": len(filled_profile_rows),
            "missingRevenueFields": missing_fields,
            "profileMissingRevenueFields": profile_missing_fields,
            "emptyDataMode": not any(is_filled(row) for row in rows) and not filled_profile_rows,
        },
        "fieldMeanings": FIELD_MEANINGS,
        "decisionRules": [
            {"stage": "collect_signal", "rule": "尚無可判斷數據，照原排程發布與回填。"},
            {"stage": "publish_guardian_variants", "rule": "測驗完成累積但尚無路線/獲利意圖時，先放大同守護者內容變體。"},
            {"stage": "deepen_identity_asset", "rule": "已有收藏或路線興趣時，先強化免費收藏物與分享資產。"},
            {"stage": "build_owned_asset", "rule": "已有補給名單或 Contact 需求時，優先做自有 Email/下載資產。"},
            {"stage": "test_soft_offer", "rule": "已有 Luna 或聯盟點擊時，測試柔性商品承接，但 Shorts CTA 仍維持測驗。"},
        ],
        "platformProfileIntent": {
            "scope": "platform_profile_unassigned",
            "boundary": "此區只代表 Bio/Profile link 承接，不分配到特定守護者。",
            "trackerRows": len(profile_rows),
            "filledRows": len(filled_profile_rows),
            "metrics": platform_metrics,
            "platforms": platform_rows,
            "stage": platform_stage,
            "recommendedAction": platform_stage_action(platform_stage, platform_metrics),
        },
        "guardians": guardians,
        "safety": {
            "shortsCta": "完成 15 題測驗，找到你的情感守護者",
            "doNotClaim": ["診斷", "療效", "保證修復", "必須購買"],
            "emptyDataBoundary": "空資料時不調整商品、守護者優先序或付費 CTA。",
        },
    }


def render_markdown(matrix: dict) -> str:
    profile_intent = matrix["platformProfileIntent"]
    profile_metrics = profile_intent["metrics"]
    profile_action = profile_intent["recommendedAction"]
    lines = [
        "# LoveTypes 獲利決策矩陣",
        "",
        f"- 產生日期：{matrix['generatedAt']}",
        f"- 影片追蹤列數：{matrix['dataState']['filledRows']} / {matrix['dataState']['trackerRows']}",
        f"- 平台首頁追蹤列數：{matrix['dataState']['profileFilledRows']} / {matrix['dataState']['profileTrackerRows']}",
        f"- 空資料安全模式：{'是' if matrix['dataState']['emptyDataMode'] else '否'}",
        "",
        "## 判斷規則",
        "",
    ]
    lines.extend(f"- `{item['stage']}`: {item['rule']}" for item in matrix["decisionRules"])
    lines.extend([
        "",
        "## 平台首頁意圖",
        "",
        f"- 目前階段：`{profile_intent['stage']}`",
        f"- 建議動作：[{profile_action['priority']}] {profile_action['action']}",
        f"- 建議補強：{profile_action['build']}",
        f"- 目標入口：{profile_action['target']}",
        f"- Bio/Profile 點擊：{profile_metrics['profile_clicks']}",
        f"- 網站點擊：{profile_metrics['site_clicks']}",
        f"- 測驗開始：{profile_metrics['quiz_starts']}",
        f"- 測驗完成：{profile_metrics['quiz_completions']}",
        f"- 路線興趣：{sum(profile_metrics[field] for field in ROUTE_FIELDS)}",
        f"- 名單/Contact：{profile_metrics['supply_lead_requests'] + profile_metrics['contact_requests']}",
        f"- Luna/聯盟：{profile_metrics['luna_pack_clicks'] + profile_metrics['affiliate_book_clicks']}",
        f"- 判讀邊界：{profile_intent['boundary']}",
        "",
        "## 守護者決策",
        "",
    ])
    for item in matrix["guardians"]:
        metrics = item["metrics"]
        action = item["recommendedAction"]
        bridge = item["monetizationBridge"]
        lines.extend([
            f"### {item['guardianName']}（{item['guardianId']}）",
            "",
            f"- 週次：Week {item['week']}",
            f"- 腳本數：{item['taskCount']}",
            f"- 目前階段：`{item['stage']}`",
            f"- 建議動作：[{action['priority']}] {action['action']}",
            f"- 建議補強：{action['build']}",
            f"- 目標入口：{action['target']}",
            f"- 測驗完成：{metrics['quiz_completions']}",
            f"- 路線興趣：{sum(metrics[field] for field in ROUTE_FIELDS)}",
            f"- 免費收藏：{metrics['free_keepsake_downloads']}",
            f"- 名單/Contact：{metrics['supply_lead_requests'] + metrics['contact_requests']}",
            f"- Luna/聯盟：{metrics['luna_pack_clicks'] + metrics['affiliate_book_clicks']}",
            f"- 免費資產 ID：{bridge['primaryFreeItemId']}",
            f"- 名單資產 ID：{bridge['ownedLeadItemId']}",
            "",
        ])
    lines.extend([
        "## 安全邊界",
        "",
        f"- Shorts CTA：{matrix['safety']['shortsCta']}",
        "- 不使用診斷、療效、保證修復或必須購買的說法。",
        f"- {matrix['safety']['emptyDataBoundary']}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(matrix: dict, output: Path, json_output: Path) -> None:
    output.write_text(render_markdown(matrix), encoding="utf-8")
    json_output.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_matrix(matrix: dict) -> list[str]:
    issues: list[str] = []
    profile_intent = matrix.get("platformProfileIntent")
    if not isinstance(profile_intent, dict):
        issues.append("missing platform profile intent block")
    elif profile_intent.get("scope") != "platform_profile_unassigned":
        issues.append("platform profile intent must remain unassigned")
    if len(matrix.get("guardians", [])) != 5:
        issues.append("expected five guardian decision rows")
    stages = {item.get("stage") for item in matrix.get("guardians", [])}
    if not stages:
        issues.append("expected at least one decision stage")
    for item in matrix.get("guardians", []):
        guardian = item.get("guardianId", "<unknown>")
        if item.get("taskCount") != 3:
            issues.append(f"{guardian}: expected three campaign scripts")
        bridge = item.get("monetizationBridge", {})
        if not bridge.get("primaryFreeItemId") or not bridge.get("ownedLeadItemId"):
            issues.append(f"{guardian}: missing free or owned lead item id")
        action = item.get("recommendedAction", {})
        if not action.get("action") or not action.get("target"):
            issues.append(f"{guardian}: missing recommended action or target")
    if matrix.get("dataState", {}).get("missingRevenueFields"):
        issues.append("tracker missing revenue fields: " + ", ".join(matrix["dataState"]["missingRevenueFields"]))
    if matrix.get("dataState", {}).get("profileMissingRevenueFields"):
        issues.append("platform profile tracker missing revenue fields: " + ", ".join(matrix["dataState"]["profileMissingRevenueFields"]))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes revenue decision matrix from first-round promotion data.")
    parser.add_argument("--tracker", default=str(TRACKER_PATH))
    parser.add_argument("--profile-tracker", default=str(PROFILE_TRACKER_PATH))
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    fields, rows = read_tracker(Path(args.tracker))
    profile_fields, profile_rows = read_tracker(Path(args.profile_tracker))
    matrix = build_matrix(fields, rows, load_tasks(Path(args.kit)), profile_fields, profile_rows)
    issues = validate_matrix(matrix)
    if not args.check:
        write_outputs(matrix, Path(args.output), Path(args.json_output))
        print(f"promotion_revenue_decision_matrix={args.output}")
        print(f"promotion_revenue_decision_matrix_json={args.json_output}")
    print(f"promotion_revenue_decision_guardians={len(matrix['guardians'])}")
    print(f"promotion_revenue_decision_filled_rows={matrix['dataState']['filledRows']}")
    print(f"promotion_revenue_decision_profile_filled_rows={matrix['dataState']['profileFilledRows']}")
    print(f"promotion_revenue_decision_profile_stage={matrix['platformProfileIntent']['stage']}")
    print(f"promotion_revenue_decision_empty_data_mode={int(matrix['dataState']['emptyDataMode'])}")
    print(f"promotion_revenue_decision_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
