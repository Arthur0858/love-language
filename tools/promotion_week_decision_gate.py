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
MATRIX_PATH = PROMOTION_DIR / "revenue-decision-matrix.json"
NEXT_ACTIONS_PATH = PROMOTION_DIR / "next-actions.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "week-decision-gate.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "week-decision-gate.json"
QUIZ_START_RATE_MIN = 0.3
QUIZ_COMPLETION_RATE_MIN = 0.4
SCALE_CONTENT_MIN_QUIZ_COMPLETIONS_FALLBACK = 10


def matrix_decision_thresholds(matrix: dict) -> dict:
    thresholds = matrix.get("decisionThresholds", {})
    return thresholds if isinstance(thresholds, dict) else {}


def decision_thresholds(matrix: dict) -> dict[str, float | int]:
    matrix_thresholds = matrix_decision_thresholds(matrix)
    return {
        "quizStartRateMin": QUIZ_START_RATE_MIN,
        "quizCompletionRateMin": QUIZ_COMPLETION_RATE_MIN,
        "scaleContentMinQuizCompletions": int(
            matrix_thresholds.get(
                "publishGuardianVariantsMinQuizCompletions",
                SCALE_CONTENT_MIN_QUIZ_COMPLETIONS_FALLBACK,
            )
            or SCALE_CONTENT_MIN_QUIZ_COMPLETIONS_FALLBACK
        ),
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


def status_label(value: bool) -> str:
    return "PASS" if value else "HOLD"


def build_gate(status: dict, summary: dict, matrix: dict, next_actions: dict) -> dict:
    totals = summary.get("totals", {})
    derived = summary.get("derived", {})
    computed = summary.get("computedTotals", {})
    leaders = summary.get("leaders", {})
    data_state = matrix.get("dataState", {})
    ready_for_weekly = bool(status.get("readyForWeeklyDecision"))
    empty_data = bool(summary.get("safety", {}).get("emptyDataMode")) or bool(data_state.get("emptyDataMode"))
    quiz_completions = int(totals.get("quiz_completions", 0) or 0)
    quiz_starts = int(totals.get("quiz_starts", 0) or 0)
    site_clicks = int(totals.get("site_clicks", 0) or 0)
    identity_interest = int(computed.get("identityInterest", 0) or 0)
    route_interest = int(computed.get("routeInterest", 0) or 0)
    identity_route_interest = int(computed.get("identityRouteInterest", identity_interest + route_interest) or 0)
    paid_intent = int(computed.get("paidRevenueIntent", 0) or 0)
    lead_intent = int(computed.get("leadIntent", 0) or 0)
    completion_rate = derived.get("quizCompletionRate")
    start_rate = derived.get("quizStartRate")
    thresholds = decision_thresholds(matrix)
    scale_content_min_quiz = int(thresholds["scaleContentMinQuizCompletions"])
    positive_signal_total = site_clicks + quiz_starts + quiz_completions + identity_route_interest + lead_intent + paid_intent
    blockers: list[str] = []
    if not ready_for_weekly:
        blockers.append("尚未達週決策門檻：發布狀態或 KPI 回填不足。")
    if empty_data:
        blockers.append("目前仍是空資料模式，不能放大守護者、商品或付費 CTA。")
    if ready_for_weekly and not empty_data and positive_signal_total == 0:
        blockers.append("已回填 KPI，但目前所有關鍵訊號皆為 0；維持 collect_signal，不調整商品、守護者優先序或內容放大。")
    if site_clicks > 0 and start_rate is not None and start_rate < QUIZ_START_RATE_MIN:
        blockers.append(f"網站點擊進來但測驗開始率低於 {QUIZ_START_RATE_MIN:.0%}，先修 /start/ 首屏與 CTA。")
    if quiz_starts > 0 and completion_rate is not None and completion_rate < QUIZ_COMPLETION_RATE_MIN:
        blockers.append(f"測驗開始後完成率低於 {QUIZ_COMPLETION_RATE_MIN:.0%}，先修手機題目節奏與結果揭示。")

    can_scale_content = (
        ready_for_weekly
        and not empty_data
        and quiz_completions >= scale_content_min_quiz
        and not any("測驗開始後完成率" in item for item in blockers)
    )
    can_build_owned = ready_for_weekly and not empty_data and lead_intent > 0
    can_test_soft_offer = ready_for_weekly and not empty_data and paid_intent > 0
    can_deepen_identity = ready_for_weekly and not empty_data and identity_route_interest > 0

    recommended_focus = "collect_signal"
    if can_test_soft_offer:
        recommended_focus = "test_soft_offer"
    elif can_build_owned:
        recommended_focus = "build_owned_asset"
    elif can_deepen_identity:
        recommended_focus = "deepen_identity_asset"
    elif can_scale_content:
        recommended_focus = "scale_content"

    next_steps: list[str] = []
    if recommended_focus == "test_soft_offer":
        next_steps.append("只在結果後路線測試 Luna starter 或聯盟書卷，不把 Shorts CTA 改成購買。")
    elif recommended_focus == "build_owned_asset":
        next_steps.append("優先補對應守護者的 Email/下載資產，收集最低限度需求脈絡。")
    elif recommended_focus == "deepen_identity_asset":
        next_steps.append("強化免費收藏物、故事卡或分享圖，先提高保存與回訪。")
    elif recommended_focus == "scale_content":
        guardian = leaders.get("quizGuardian") or {}
        name = guardian.get("id") or "最佳守護者"
        next_steps.append(f"放大 {name} 的不同痛點變體，仍維持測驗 CTA。")
    else:
        next_steps.extend(action.get("summary", "") for action in next_actions.get("actions", []) if action.get("summary"))

    if not next_steps:
        next_steps.append("先補發布與 KPI 回填，再重新產生週決策 gate。")

    gates = {
        "weeklyDecision": ready_for_weekly and not empty_data and not blockers,
        "scaleContent": can_scale_content,
        "deepenIdentityAsset": can_deepen_identity,
        "buildOwnedLeadAsset": can_build_owned,
        "testSoftOffer": can_test_soft_offer,
    }
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "publishingStatus": str(STATUS_PATH.relative_to(ROOT)),
            "weeklySummary": str(SUMMARY_PATH.relative_to(ROOT)),
            "revenueDecisionMatrix": str(MATRIX_PATH.relative_to(ROOT)),
            "nextActions": str(NEXT_ACTIONS_PATH.relative_to(ROOT)),
        },
        "metrics": {
            "siteClicks": site_clicks,
            "quizStarts": quiz_starts,
            "quizCompletions": quiz_completions,
            "quizStartRate": start_rate,
            "quizCompletionRate": completion_rate,
            "identityInterest": identity_interest,
            "routeInterest": route_interest,
            "identityRouteInterest": identity_route_interest,
            "leadIntent": lead_intent,
            "paidRevenueIntent": paid_intent,
            "positiveSignalTotal": positive_signal_total,
        },
        "decisionThresholds": thresholds,
        "leaders": leaders,
        "gates": gates,
        "recommendedFocus": recommended_focus,
        "blockers": blockers,
        "nextSteps": next_steps,
        "safety": {
            "shortsCtaMustRemainQuiz": True,
            "doNotUse": ["診斷", "療效", "保證修復", "必須購買"],
            "emptyDataFailClosed": empty_data,
            "noPositiveSignalFailClosed": ready_for_weekly and not empty_data and positive_signal_total == 0,
            "offerTestsOnlyAfterResultRoute": True,
        },
    }


def render_markdown(gate: dict) -> str:
    metrics = gate["metrics"]
    lines = [
        "# LoveTypes 週決策 Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- 建議焦點：`{gate['recommendedFocus']}`",
        f"- 週決策：{status_label(gate['gates']['weeklyDecision'])}",
        f"- 內容放大：{status_label(gate['gates']['scaleContent'])}",
        f"- 免費收藏深化：{status_label(gate['gates']['deepenIdentityAsset'])}",
        f"- 自有名單資產：{status_label(gate['gates']['buildOwnedLeadAsset'])}",
        f"- Luna/聯盟柔性測試：{status_label(gate['gates']['testSoftOffer'])}",
        "",
        "## 核心數據",
        "",
        f"- 網站點擊：{metrics['siteClicks']}",
        f"- 測驗開始：{metrics['quizStarts']}（start rate: {pct(metrics['quizStartRate'])}）",
        f"- 測驗完成：{metrics['quizCompletions']}（completion rate: {pct(metrics['quizCompletionRate'])}）",
        f"- 守護者認同：{metrics['identityInterest']}",
        f"- 路線興趣：{metrics['routeInterest']}",
        f"- 認同 + 路線興趣：{metrics['identityRouteInterest']}",
        f"- 名單/需求意圖：{metrics['leadIntent']}",
        f"- Luna/聯盟付費意圖：{metrics['paidRevenueIntent']}",
        f"- 正向訊號總和：{metrics['positiveSignalTotal']}",
        "",
        "## 阻擋條件",
        "",
    ]
    if gate["blockers"]:
        lines.extend(f"- {item}" for item in gate["blockers"])
    else:
        lines.append("- 無")
    lines.extend(["", "## 下一步", ""])
    lines.extend(f"- {item}" for item in gate["nextSteps"])
    lines.extend([
        "",
        "## 安全邊界",
        "",
        "- Shorts CTA 維持測驗，不直接導購。",
        "- 商品或聯盟只放在結果後路線，不在空資料時放大。",
        "- 不使用診斷、療效、保證修復或必須購買說法。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def validate_gate(gate: dict) -> list[str]:
    issues: list[str] = []
    gates = gate.get("gates", {})
    if not isinstance(gates, dict) or set(gates) != {"weeklyDecision", "scaleContent", "deepenIdentityAsset", "buildOwnedLeadAsset", "testSoftOffer"}:
        issues.append("gate payload should include all decision gates")
    if gate.get("safety", {}).get("emptyDataFailClosed") and any(gates.values()):
        issues.append("empty data mode must fail closed for every decision gate")
    if gate.get("safety", {}).get("noPositiveSignalFailClosed") and any(gates.values()):
        issues.append("no-positive-signal mode must fail closed for every decision gate")
    if gate.get("gates", {}).get("testSoftOffer") and gate.get("metrics", {}).get("paidRevenueIntent", 0) <= 0:
        issues.append("soft offer gate cannot pass without paid revenue intent")
    if gate.get("gates", {}).get("deepenIdentityAsset") and gate.get("metrics", {}).get("identityRouteInterest", 0) <= 0:
        issues.append("identity asset gate cannot pass without identity or route interest")
    if int(gate.get("decisionThresholds", {}).get("scaleContentMinQuizCompletions", 0) or 0) < 1:
        issues.append("scale content gate missing quiz completion threshold")
    if not gate.get("nextSteps"):
        issues.append("gate should include at least one next step")
    if gate.get("recommendedFocus") not in {"collect_signal", "scale_content", "deepen_identity_asset", "build_owned_asset", "test_soft_offer"}:
        issues.append("unexpected recommended focus")
    return issues


def write_outputs(gate: dict, output: Path, json_output: Path) -> None:
    output.write_text(render_markdown(gate), encoding="utf-8")
    json_output.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes weekly go/no-go decision gate for promotion monetization.")
    parser.add_argument("--status", default=str(STATUS_PATH))
    parser.add_argument("--summary", default=str(SUMMARY_PATH))
    parser.add_argument("--matrix", default=str(MATRIX_PATH))
    parser.add_argument("--next-actions", default=str(NEXT_ACTIONS_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    gate = build_gate(
        load_json(Path(args.status)),
        load_json(Path(args.summary)),
        load_json(Path(args.matrix)),
        load_json(Path(args.next_actions)),
    )
    issues = validate_gate(gate)
    if not args.check:
        write_outputs(gate, Path(args.output), Path(args.json_output))
        print(f"promotion_week_decision_gate={args.output}")
        print(f"promotion_week_decision_gate_json={args.json_output}")
    print(f"promotion_week_decision_gate_weekly={int(gate['gates']['weeklyDecision'])}")
    print(f"promotion_week_decision_gate_scale={int(gate['gates']['scaleContent'])}")
    print(f"promotion_week_decision_gate_owned={int(gate['gates']['buildOwnedLeadAsset'])}")
    print(f"promotion_week_decision_gate_offer={int(gate['gates']['testSoftOffer'])}")
    print(f"promotion_week_decision_gate_positive_signal_total={gate['metrics']['positiveSignalTotal']}")
    print(f"promotion_week_decision_gate_no_positive_signal={int(gate['safety']['noPositiveSignalFailClosed'])}")
    print(f"promotion_week_decision_gate_blockers={len(gate['blockers'])}")
    print(f"promotion_week_decision_gate_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
