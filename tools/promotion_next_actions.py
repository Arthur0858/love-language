#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

from promotion_weekly_summary import build_report, is_filled, is_profile_filled, load_tasks, read_tracker


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
PROFILE_SETUP_PATH = PROMOTION_DIR / "platform-profile-setup.json"
PROOF_CONTROL_PATH = PROMOTION_DIR / "launch-proof-control-sheet.json"
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
ROUTE_FIELDS = [
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
]
IDENTITY_FIELDS = ["guardian_result_clicks"]
EMPTY_DATA_ACTION_IDS = (
    "set_platform_profile_links",
    "fill_platform_profile_kpis",
    "publish_first_batch",
    "fill_required_kpis",
    "hold_offer_changes",
)
PROFILE_FIRST_KPIS = (
    "status",
    "profile_link_set_date",
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
)
QUIZ_START_RATE_MIN = 0.3
QUIZ_COMPLETION_RATE_MIN = 0.4


def decision_thresholds() -> dict[str, float]:
    return {
        "quizStartRateMin": QUIZ_START_RATE_MIN,
        "quizCompletionRateMin": QUIZ_COMPLETION_RATE_MIN,
    }


def action_policy() -> dict[str, object]:
    return {
        "emptyDataActionOrder": list(EMPTY_DATA_ACTION_IDS),
        "emptyDataSelectedTaskRule": "When profile links are pending, finish platform profile setup first; then select the first three planned tasks by week and slot and keep Shorts CTA focused on the 15-question quiz.",
        "profileSetupBeforePublish": True,
        "profileFirstKpis": list(PROFILE_FIRST_KPIS),
        "shortsKpiMinimumFields": ["post_url", "site_clicks", "quiz_starts", "quiz_completions"],
        "shortsKpiDownstreamFields": [*IDENTITY_FIELDS, *ROUTE_FIELDS, *REVENUE_FIELDS],
        "offerChangeGate": "Do not change products, guardian priority, paid CTA, Luna emphasis, or affiliate emphasis until filled KPI rows create quiz, route, lead, Luna, or affiliate intent.",
        "leaderSelectionRule": "When KPI rows are filled, score guardian and content-angle leaders by quiz_completions * 3 + identity_clicks + route_clicks + revenue_intent * 2.",
        "proofControlFirst": "Use launch-proof-control-sheet as the operator source of truth before manual CSV or tracker edits.",
    }


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def filled_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if is_filled(row)]


def tasks_by_script(tasks: list[dict]) -> dict[str, dict]:
    return {str(task.get("scriptId", "")): task for task in tasks}


def planned_tasks(tasks: list[dict]) -> list[dict]:
    return sorted(
        [task for task in tasks if task.get("status") == "planned"],
        key=lambda task: (int(task.get("week", 0) or 0), int(task.get("slot", 0) or 0)),
    )


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def platform_setup_lookup(data: dict) -> dict[str, dict]:
    return {str(item.get("platformId", "")): item for item in data.get("platforms", []) if item.get("platformId")}


def platform_setup_expectations(data: dict) -> dict[str, int]:
    return {
        "expectedVerificationSteps": int(data.get("expectedVerificationSteps", 0) or 0),
        "expectedDoNotPublishGates": int(data.get("expectedDoNotPublishGates", 0) or 0),
    }


def profile_rows_to_actions(rows: list[dict[str, str]], setup: dict[str, dict], expectations: dict[str, int]) -> list[dict]:
    actions = []
    for row in rows:
        if is_profile_filled(row):
            continue
        platform = (row.get("platform") or "").strip()
        item = setup.get(platform, {})
        actions.append({
            "platform": platform,
            "label": row.get("label") or item.get("label") or platform,
            "status": row.get("status") or "planned",
            "profileLink": row.get("profile_link") or item.get("profileLink"),
            "profileLinkLabel": item.get("profileLinkLabel", "Profile link"),
            "bio": item.get("bio", ""),
            "pinnedComment": item.get("pinnedComment", ""),
            "writebackValues": item.get("writebackValues", {}),
            "verificationSteps": item.get("verificationSteps", []),
            "doNotPublishUntil": item.get("doNotPublishUntil", []),
            "expectedVerificationSteps": expectations.get("expectedVerificationSteps", 0),
            "expectedDoNotPublishGates": expectations.get("expectedDoNotPublishGates", 0),
            "firstKpis": list(PROFILE_FIRST_KPIS),
        })
    return actions


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
        identity = sum(parse_int(row.get(field)) for field in IDENTITY_FIELDS)
        revenue = sum(parse_int(row.get(field)) for field in REVENUE_FIELDS)
        score = quiz * 3 + identity + route + revenue * 2
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


def build_actions(
    fields: list[str],
    rows: list[dict[str, str]],
    tasks: list[dict],
    profile_fields: list[str] | None = None,
    profile_rows: list[dict[str, str]] | None = None,
    profile_setup: dict[str, dict] | None = None,
    profile_setup_expectations: dict[str, int] | None = None,
    proof_control: dict | None = None,
) -> dict:
    profile_fields = profile_fields or []
    profile_rows = profile_rows or []
    profile_setup = profile_setup or {}
    profile_setup_expectations = profile_setup_expectations or {}
    proof_control = proof_control or {}
    report = build_report(fields, rows, tasks, profile_fields, profile_rows)
    active_rows = filled_rows(rows)
    active_profile_rows = [row for row in profile_rows if is_profile_filled(row)]
    pending_profile_actions = profile_rows_to_actions(profile_rows, profile_setup, profile_setup_expectations)
    guardian_scores, angle_scores, revenue_scores = score_rows(active_rows, tasks)
    top_guardian = top_key(guardian_scores)
    top_angle = top_key(angle_scores)
    top_revenue_guardian = top_key(revenue_scores)
    selected = select_followup_tasks(tasks, top_guardian, top_angle)
    actions = []
    if not active_rows:
        selected = planned_tasks(tasks)[:3]
        publish_priority = "blocked" if pending_profile_actions else "high"
        kpi_priority = "blocked" if pending_profile_actions else "high"
        publish_summary = (
            "Profile link 完成並回填後，才發布 Week 1 前 3 支 Shorts，先取得測驗完成樣本。"
            if pending_profile_actions
            else "發布 Week 1 前 3 支 Shorts，先取得測驗完成樣本。"
        )
        kpi_summary = (
            "發布被 profile setup gate 鎖住；發布後才回填 post_url、site_clicks、quiz_starts、quiz_completions。"
            if pending_profile_actions
            else "發布後先回填 post_url、site_clicks、quiz_starts、quiz_completions；有結果後互動時補齊 guardian_result_clicks、resources_clicks、repair_plan_clicks、luna_clicks、keepsake_clicks、free_keepsake_downloads、supply_lead_requests、luna_pack_clicks、affiliate_book_clicks、contact_requests。"
        )
        actions.extend([
            {
                "id": "set_platform_profile_links",
                "priority": "high",
                "type": "distribution",
                "summary": "先依 launch-proof-control-sheet 完成 YouTube、TikTok、Instagram 的 Profile proof；三筆 ready 後才執行 profile batch add。",
            },
            {
                "id": "fill_platform_profile_kpis",
                "priority": "high",
                "type": "measurement",
                "summary": "平台首頁設定後先更新三個 proof-*.txt，再跑 profile batch check/add；不要直接手改 tracker。",
            },
            {
                "id": "publish_first_batch",
                "priority": publish_priority,
                "type": "execution",
                "summary": publish_summary,
            },
            {
                "id": "fill_required_kpis",
                "priority": kpi_priority,
                "type": "measurement",
                "summary": kpi_summary,
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
        if derived["quizStartRate"] is not None and derived["quizStartRate"] < QUIZ_START_RATE_MIN:
            actions.append({
                "id": "repair_start_landing",
                "priority": "high",
                "type": "site",
                "summary": "網站點擊有進來但測驗開始率低，優先檢查 /start/ 首屏與 CTA。",
            })
        if derived["quizCompletionRate"] is not None and derived["quizCompletionRate"] < QUIZ_COMPLETION_RATE_MIN:
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
            "platformProfileTracker": str(PROFILE_TRACKER_PATH.relative_to(ROOT)),
            "platformProfileSetup": str(PROFILE_SETUP_PATH.relative_to(ROOT)),
            "proofControl": str(PROOF_CONTROL_PATH.relative_to(ROOT)),
            "promotionKit": str(KIT_PATH.relative_to(ROOT)),
        },
        "dataState": {
            "trackerRows": report["trackerRows"],
            "profileTrackerRows": report["profileTrackerTotalRows"],
            "profileFilledRows": report["profileTrackerRows"],
            "profilePendingRows": len(pending_profile_actions),
            "emptyDataMode": report["safety"]["emptyDataMode"],
            "fieldComplete": report["fieldStatus"]["complete"],
            "proofControlRows": int((proof_control.get("metrics") or {}).get("rows", 0) or 0),
            "profileProofReady": int((proof_control.get("metrics") or {}).get("profileReady", 0) or 0),
            "profileProofBlocked": int((proof_control.get("metrics") or {}).get("profileBlocked", 0) or 0),
            "postProofReady": int((proof_control.get("metrics") or {}).get("postReady", 0) or 0),
            "postProofBlocked": int((proof_control.get("metrics") or {}).get("postBlocked", 0) or 0),
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
        "decisionThresholds": decision_thresholds(),
        "actionPolicy": action_policy(),
        "proofControl": {
            "steps": proof_control.get("steps", []),
            "rows": proof_control.get("rows", []),
            "issues": proof_control.get("issues", []),
        },
        "actions": actions,
        "platformProfileActions": pending_profile_actions,
        "selectedTasks": [task_summary(task) for task in selected],
        "safety": {
            "doNotChangeOffersFromEmptyData": not active_rows and not active_profile_rows,
            "doNotUseDiagnosisClaims": True,
            "keepShortsCtaQuizOnly": True,
            "profileLinksQuizOnly": True,
        },
    }


def build_markdown(plan: dict) -> str:
    lines = [
        "# LoveTypes 下一批推廣動作建議",
        "",
        f"- 產生日期：{plan['generatedAt']}",
        f"- 影片追蹤列數：{plan['dataState']['trackerRows']}",
        f"- 平台首頁待設定列數：{plan['dataState']['profilePendingRows']} / {plan['dataState']['profileTrackerRows']}",
        f"- Profile proof ready / blocked：{plan['dataState']['profileProofReady']} / {plan['dataState']['profileProofBlocked']}",
        f"- Post proof ready / blocked：{plan['dataState']['postProofReady']} / {plan['dataState']['postProofBlocked']}",
        f"- 空資料安全模式：{'是' if plan['dataState']['emptyDataMode'] else '否'}",
        f"- 行動選擇規則：{plan['actionPolicy']['emptyDataSelectedTaskRule']}",
        f"- 商品調整 gate：{plan['actionPolicy']['offerChangeGate']}",
        "",
        "## 優先動作",
        "",
    ]
    for action in plan["actions"]:
        lines.append(f"- [{action['priority']}] {action['summary']}")
    lines.extend(["", "## Proof Control", ""])
    proof_control = plan.get("proofControl", {})
    steps = proof_control.get("steps", [])
    if steps:
        for step in steps:
            lines.extend([
                f"### `{step.get('id', '')}`",
                "",
                f"- status：`{step.get('status', '')}`",
                f"- command：`{step.get('command', '')}`",
                f"- release：{step.get('release', '')}",
                "",
            ])
    else:
        lines.append("- 尚未產生 launch-proof-control-sheet，先跑 `python3 tools/promotion_launch_proof_control_sheet.py`。")
        lines.append("")
    proof_rows = proof_control.get("rows", [])
    if proof_rows:
        lines.extend(["Proof rows:", ""])
        for row in proof_rows:
            lines.append(
                f"- `{row.get('proofType', '')}` / `{row.get('platform', '')}`：`{row.get('status', '')}` ready={row.get('ready', '')} file=`{row.get('proofFile', '')}`"
            )
        lines.append("")
    lines.extend(["", "## 平台首頁設定", ""])
    for item in plan["platformProfileActions"]:
        lines.extend([
            f"### {item['label']}（`{item['platform']}`）",
            "",
            f"- 連結位置：{item['profileLinkLabel']}",
            f"- Profile link：{item['profileLink']}",
            f"- 狀態：`{item['status']}`",
            "- Bio：",
            "",
            "```text",
            item["bio"],
            "```",
            "",
            "- 置頂留言 / 首則留言：",
            "",
            "```text",
            item["pinnedComment"],
            "```",
            "",
            "- 設定後回填值：",
            "",
        ])
        writeback_values = item.get("writebackValues", {})
        if writeback_values:
            lines.extend(f"  - `{field}`：{value}" for field, value in writeback_values.items())
        else:
            lines.append("  - `status`：set")
        lines.extend([
            "",
            "- 設定後驗證：",
            "",
        ])
        verification_steps = item.get("verificationSteps", [])
        if verification_steps:
            lines.extend(f"  - {step}" for step in verification_steps)
        else:
            lines.append("  - 開啟 profile link，確認會到 /start/ 並保留 UTM。")
        lines.extend([
            "",
            "- 未完成前不要發布：",
            "",
        ])
        do_not_publish = item.get("doNotPublishUntil", [])
        if do_not_publish:
            lines.extend(f"  - {step}" for step in do_not_publish)
        else:
            lines.append("  - status 尚未標記 set/live。")
        lines.extend([
            "",
            f"- 優先回填欄位：{', '.join(f'`{field}`' for field in item['firstKpis'])}",
            "",
        ])
    if not plan["platformProfileActions"]:
        lines.extend(["- 平台首頁追蹤列已設定，下一步看 profile_clicks、site_clicks、quiz_starts、quiz_completions。", ""])
    lines.extend(["## 建議發布任務", ""])
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
        "- 平台首頁 Bio/Profile link 也維持測驗，不直接導購。",
        "- 不把守護者結果描述成診斷、療效或保證修復。",
        "- 空資料時不調整商品、守護者優先序或付費 CTA。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate LoveTypes next promotion actions from KPI tracker data.")
    parser.add_argument("--tracker", default=str(TRACKER_PATH))
    parser.add_argument("--profile-tracker", default=str(PROFILE_TRACKER_PATH))
    parser.add_argument("--profile-setup", default=str(PROFILE_SETUP_PATH))
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--output", default=str(PROMOTION_DIR / "next-actions.md"))
    parser.add_argument("--json-output", default=str(PROMOTION_DIR / "next-actions.json"))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    fields, rows = read_tracker(Path(args.tracker))
    profile_fields, profile_rows = read_tracker(Path(args.profile_tracker))
    profile_setup_data = read_json(Path(args.profile_setup))
    profile_setup = platform_setup_lookup(profile_setup_data)
    profile_expectations = platform_setup_expectations(profile_setup_data)
    proof_control = read_json(PROOF_CONTROL_PATH)
    tasks = load_tasks(Path(args.kit))
    plan = build_actions(fields, rows, tasks, profile_fields, profile_rows, profile_setup, profile_expectations, proof_control)
    markdown = build_markdown(plan)
    if args.check:
        issues = []
        policy = plan.get("actionPolicy", {})
        if policy.get("emptyDataActionOrder") != list(EMPTY_DATA_ACTION_IDS):
            issues.append("actionPolicy.emptyDataActionOrder does not match generator policy")
        if policy.get("profileSetupBeforePublish") is not True:
            issues.append("actionPolicy should require profile setup before publish")
        if policy.get("profileFirstKpis") != list(PROFILE_FIRST_KPIS):
            issues.append("actionPolicy.profileFirstKpis does not match generator policy")
        if len(plan["actions"]) < 1:
            issues.append("expected at least one action")
        if len(plan["selectedTasks"]) < 1:
            issues.append("expected at least one selected task")
        if plan["dataState"]["proofControlRows"] != 6:
            issues.append("proof control should expose six profile/post proof rows")
        if plan["dataState"]["emptyDataMode"] and plan["dataState"]["profileProofBlocked"] < 1:
            issues.append("empty data mode should expose blocked profile proof rows")
        proof_steps = [step.get("id") for step in plan.get("proofControl", {}).get("steps", [])]
        if proof_steps[:2] != ["prepare_profile_proofs", "write_profile_batch"]:
            issues.append("proof control should start with profile proof preparation and profile batch write")
        if plan["dataState"]["emptyDataMode"] and not plan["safety"]["doNotChangeOffersFromEmptyData"]:
            issues.append("empty data mode should block offer changes")
        if plan["dataState"]["profileTrackerRows"] and not plan["platformProfileActions"] and plan["dataState"]["profilePendingRows"]:
            issues.append("expected platform profile actions for pending rows")
        if plan["dataState"]["emptyDataMode"] and plan["dataState"]["profilePendingRows"] < 1:
            issues.append("empty data mode should surface platform profile setup actions")
        if plan["dataState"]["emptyDataMode"]:
            action_ids = [action.get("id") for action in plan["actions"]]
            if action_ids != list(EMPTY_DATA_ACTION_IDS):
                issues.append("empty data mode action order should match policy")
            slots = [int(task.get("slot", 0) or 0) for task in plan["selectedTasks"]]
            if slots != [1, 2, 3]:
                issues.append("empty data mode should select first three planned slots")
        for item in plan["platformProfileActions"]:
            if not item.get("writebackValues"):
                issues.append(f"{item.get('platform')}: missing writebackValues")
            if item.get("firstKpis") != list(PROFILE_FIRST_KPIS):
                issues.append(f"{item.get('platform')}: firstKpis does not match policy")
            expected_verification_steps = int(item.get("expectedVerificationSteps", 0) or 0)
            if len(item.get("verificationSteps", [])) < expected_verification_steps:
                issues.append(f"{item.get('platform')}: missing verificationSteps")
            expected_do_not_publish = int(item.get("expectedDoNotPublishGates", 0) or 0)
            if len(item.get("doNotPublishUntil", [])) < expected_do_not_publish:
                issues.append(f"{item.get('platform')}: missing doNotPublishUntil")
        if not markdown.startswith("# LoveTypes 下一批推廣動作建議"):
            issues.append("markdown missing title")
        print(f"promotion_next_actions_selected_tasks={len(plan['selectedTasks'])}")
        print(f"promotion_next_actions_actions={len(plan['actions'])}")
        print(f"promotion_next_actions_profile_actions={len(plan['platformProfileActions'])}")
        print(f"promotion_next_actions_profile_pending_rows={plan['dataState']['profilePendingRows']}")
        print(f"promotion_next_actions_profile_proof_blocked={plan['dataState']['profileProofBlocked']}")
        print(f"promotion_next_actions_post_proof_blocked={plan['dataState']['postProofBlocked']}")
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
