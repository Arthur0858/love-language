#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
STATUS_PATH = PROMOTION_DIR / "publishing-status.json"
SUMMARY_PATH = PROMOTION_DIR / "weekly-summary.json"
GATE_PATH = PROMOTION_DIR / "week-decision-gate.json"
MATRIX_PATH = PROMOTION_DIR / "revenue-decision-matrix.json"
FIRST_BATCH_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "weekly-review-packet.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "weekly-review-packet.json"
MINIMUM_REVIEW_FIELDS = [
    "post_url",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
]
ROUTE_REVIEW_FIELDS = [
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
]
REVENUE_REVIEW_FIELDS = [
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_packet() -> dict:
    status = load_json(STATUS_PATH)
    summary = load_json(SUMMARY_PATH)
    gate = load_json(GATE_PATH)
    matrix = load_json(MATRIX_PATH)
    first_batch = load_json(FIRST_BATCH_PATH)
    empty_data = bool(summary.get("safety", {}).get("emptyDataMode")) or bool(matrix.get("dataState", {}).get("emptyDataMode"))
    ready_for_weekly = bool(status.get("readyForWeeklyDecision")) and bool(gate.get("gates", {}).get("weeklyDecision"))
    first_batch_rows = first_batch.get("rows", [])
    rows_to_update = []
    for row in first_batch_rows:
        rows_to_update.append({
            "platform": row.get("platform", ""),
            "taskId": row.get("taskId", ""),
            "scriptId": row.get("scriptId", ""),
            "status": row.get("status", ""),
            "postUrl": row.get("postUrl", ""),
            "minimumFields": MINIMUM_REVIEW_FIELDS,
            "routeFields": ROUTE_REVIEW_FIELDS,
            "revenueFields": REVENUE_REVIEW_FIELDS,
            "writebackCommand": row.get("kpiExampleCommand") or row.get("writebackCommand", ""),
        })
    hold_reasons: list[str] = []
    if not first_batch.get("publishedRows"):
        hold_reasons.append("首批 YouTube Shorts 尚無公開 post URL。")
    if not first_batch.get("minimumKpiRows"):
        hold_reasons.append("首批尚無 site_clicks / quiz_starts / quiz_completions 回填列。")
    if not status.get("readyForWeeklyDecision"):
        hold_reasons.append("publishing-status 尚未達週決策條件。")
    if empty_data:
        hold_reasons.append("目前仍是空資料模式，不能調整商品、付費 CTA、Luna 或聯盟優先序。")
    allowed_decisions = []
    blocked_decisions = [
        "change_offer_order",
        "pick_winning_guardian",
        "increase_paid_cta",
        "prioritize_luna_or_affiliate",
        "build_paid_product_from_empty_data",
    ]
    if ready_for_weekly and not empty_data:
        allowed_decisions.extend([
            "review_quiz_completion_path",
            "rank_guardian_content_variants",
            "decide_next_content_angle",
        ])
        if gate.get("gates", {}).get("deepenIdentityAsset"):
            allowed_decisions.append("deepen_free_keepsake_asset")
        if gate.get("gates", {}).get("buildOwnedLeadAsset"):
            allowed_decisions.append("build_owned_lead_asset")
        if gate.get("gates", {}).get("testSoftOffer"):
            allowed_decisions.append("test_soft_offer_after_result_route")
    else:
        allowed_decisions.extend([
            "publish_or_verify_first_batch",
            "set_profile_links",
            "backfill_minimum_kpis",
        ])
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "publishingStatus": str(STATUS_PATH.relative_to(ROOT)),
            "weeklySummary": str(SUMMARY_PATH.relative_to(ROOT)),
            "weekDecisionGate": str(GATE_PATH.relative_to(ROOT)),
            "revenueDecisionMatrix": str(MATRIX_PATH.relative_to(ROOT)),
            "firstBatchPublicationPacket": str(FIRST_BATCH_PATH.relative_to(ROOT)),
        },
        "state": {
            "readyForWeeklyDecision": ready_for_weekly,
            "publishingStatusReady": bool(status.get("readyForWeeklyDecision")),
            "weekDecisionGateReady": bool(gate.get("gates", {}).get("weeklyDecision")),
            "emptyDataMode": empty_data,
            "firstBatchRows": int(first_batch.get("rowCount", 0) or 0),
            "firstBatchPublishedRows": int(first_batch.get("publishedRows", 0) or 0),
            "firstBatchMinimumKpiRows": int(first_batch.get("minimumKpiRows", 0) or 0),
            "trackerRows": int(summary.get("trackerRows", 0) or 0),
            "profileTrackerRows": int(summary.get("profileTrackerRows", 0) or 0),
        },
        "reviewFields": {
            "minimum": MINIMUM_REVIEW_FIELDS,
            "route": ROUTE_REVIEW_FIELDS,
            "revenue": REVENUE_REVIEW_FIELDS,
        },
        "rowsToUpdate": rows_to_update,
        "holdReasons": hold_reasons,
        "allowedDecisions": allowed_decisions,
        "blockedDecisions": blocked_decisions,
        "decisionOutputs": {
            "recommendedFocus": gate.get("recommendedFocus", "collect_signal"),
            "matrixEmptyDataMode": bool(matrix.get("dataState", {}).get("emptyDataMode")),
            "weeklyRecommendations": summary.get("recommendations", []),
        },
        "policy": {
            "doNotUseEmptyDataForCommerce": True,
            "minimumEvidenceForWeeklyDecision": [
                "至少一個已發布 post_url",
                "對應平台列已回填 published_date 與 proof note",
                "至少填入 site_clicks、quiz_starts、quiz_completions 或確認為 0",
                "weekly summary 與 week decision gate 重新產生",
            ],
            "safety": "週回顧只判斷內容與漏斗，不把測驗寫成診斷，不承諾修復結果。",
        },
    }


def validate_packet(packet: dict) -> list[str]:
    issues: list[str] = []
    state = packet.get("state", {})
    if int(state.get("firstBatchRows", 0) or 0) < 1:
        issues.append("expected at least 1 first batch row")
    if len(packet.get("rowsToUpdate", [])) != state.get("firstBatchRows"):
        issues.append("rowsToUpdate should match first batch rows")
    if set(packet.get("reviewFields", {}).get("minimum", [])) != set(MINIMUM_REVIEW_FIELDS):
        issues.append("minimum review fields do not match policy")
    if set(packet.get("reviewFields", {}).get("revenue", [])) != set(REVENUE_REVIEW_FIELDS):
        issues.append("revenue review fields do not match policy")
    if state.get("emptyDataMode") and any(item in packet.get("allowedDecisions", []) for item in ("build_owned_lead_asset", "test_soft_offer_after_result_route")):
        issues.append("empty data mode cannot allow owned lead or soft offer decisions")
    if state.get("emptyDataMode") and "change_offer_order" not in packet.get("blockedDecisions", []):
        issues.append("empty data mode should explicitly block offer order changes")
    if not packet.get("holdReasons") and not state.get("readyForWeeklyDecision"):
        issues.append("not-ready review should include hold reasons")
    for row in packet.get("rowsToUpdate", []):
        label = f"{row.get('platform', '<platform>')}/{row.get('taskId', '<task>')}"
        if "--proof-note" not in row.get("writebackCommand", ""):
            issues.append(f"{label}: writeback command should include proof note")
        if row.get("scriptId") != "lt-s01-iris-silence":
            issues.append(f"{label}: first batch review should target lt-s01-iris-silence")
    if len(packet.get("policy", {}).get("minimumEvidenceForWeeklyDecision", [])) < 4:
        issues.append("minimum evidence policy is incomplete")
    return issues


def render_markdown(packet: dict, issues: list[str]) -> str:
    state = packet["state"]
    lines = [
        "# LoveTypes Weekly Review Packet",
        "",
        f"- 產生日期：{packet['generatedAt']}",
        f"- weekly decision ready：{1 if state['readyForWeeklyDecision'] else 0}",
        f"- empty data mode：{1 if state['emptyDataMode'] else 0}",
        f"- first batch published：{state['firstBatchPublishedRows']} / {state['firstBatchRows']}",
        f"- first batch minimum KPI rows：{state['firstBatchMinimumKpiRows']}",
        f"- tracker rows：{state['trackerRows']}",
        f"- profile tracker rows：{state['profileTrackerRows']}",
        f"- issues：{len(issues)}",
        "",
        "## Hold Reasons",
        "",
    ]
    if packet["holdReasons"]:
        lines.extend(f"- {item}" for item in packet["holdReasons"])
    else:
        lines.append("- 無")
    lines.extend(["", "## Required Review Fields", ""])
    lines.append("### Minimum")
    lines.extend(f"- `{field}`" for field in packet["reviewFields"]["minimum"])
    lines.append("")
    lines.append("### Route")
    lines.extend(f"- `{field}`" for field in packet["reviewFields"]["route"])
    lines.append("")
    lines.append("### Revenue")
    lines.extend(f"- `{field}`" for field in packet["reviewFields"]["revenue"])
    lines.extend(["", "## Rows To Update", ""])
    for row in packet["rowsToUpdate"]:
        lines.extend([
            f"### {row['platform']} · `{row['taskId']}`",
            "",
            f"- script：`{row['scriptId']}`",
            f"- status：`{row['status']}`",
            f"- post URL：{row['postUrl'] or '(pending)'}",
            f"- writeback：`{row['writebackCommand']}`",
            "",
        ])
    lines.extend(["## Allowed Decisions Now", ""])
    lines.extend(f"- `{item}`" for item in packet["allowedDecisions"])
    lines.extend(["", "## Blocked Decisions", ""])
    lines.extend(f"- `{item}`" for item in packet["blockedDecisions"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in packet["policy"]["minimumEvidenceForWeeklyDecision"])
    lines.append(f"- {packet['policy']['safety']}")
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(packet: dict, issues: list[str], output: Path, json_output: Path) -> None:
    json_output.write_text(json.dumps({**packet, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.write_text(render_markdown(packet, issues), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a LoveTypes weekly review packet before promotion decisions.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    issues = validate_packet(packet)
    if not args.check:
        write_outputs(packet, issues, Path(args.output), Path(args.json_output))
        print(f"promotion_weekly_review_packet={args.output}")
        print(f"promotion_weekly_review_packet_json={args.json_output}")
    state = packet["state"]
    print(f"promotion_weekly_review_ready={1 if state['readyForWeeklyDecision'] else 0}")
    print(f"promotion_weekly_review_empty_data={1 if state['emptyDataMode'] else 0}")
    print(f"promotion_weekly_review_first_batch_rows={state['firstBatchRows']}")
    print(f"promotion_weekly_review_first_batch_published={state['firstBatchPublishedRows']}")
    print(f"promotion_weekly_review_minimum_kpi_rows={state['firstBatchMinimumKpiRows']}")
    print(f"promotion_weekly_review_hold_reasons={len(packet['holdReasons'])}")
    print(f"promotion_weekly_review_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
