#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
WEEKLY_SUMMARY = PROMOTION_DIR / "weekly-summary.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
WEEK_DECISION = PROMOTION_DIR / "week-decision-gate.json"
REVENUE_MATRIX = PROMOTION_DIR / "revenue-decision-matrix.json"
OFFER_BOARD = PROMOTION_DIR / "offer-hypothesis-board.json"
OFFER_PLAN = PROMOTION_DIR / "offer-experiment-plan.json"
OFFER_QUEUE = PROMOTION_DIR / "offer-experiment-queue.json"
NEXT_ACTIONS = PROMOTION_DIR / "next-actions.json"
LAUNCH_READINESS = PROMOTION_DIR / "launch-readiness-gate.json"
FIRST_BATCH = PROMOTION_DIR / "first-batch-publication-packet.json"
REQUIRED_FILES = [
    WEEKLY_SUMMARY,
    WEEKLY_REVIEW,
    WEEK_DECISION,
    REVENUE_MATRIX,
    OFFER_BOARD,
    OFFER_PLAN,
    OFFER_QUEUE,
    NEXT_ACTIONS,
    LAUNCH_READINESS,
    FIRST_BATCH,
]
BLOCKED_DECISIONS = {
    "change_offer_order",
    "pick_winning_guardian",
    "increase_paid_cta",
    "prioritize_luna_or_affiliate",
    "build_paid_product_from_empty_data",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def all_rows_status(data: dict, key: str, allowed: set[str]) -> bool:
    rows = data.get(key, [])
    return isinstance(rows, list) and all(str(row.get("status", "")) in allowed for row in rows if isinstance(row, dict))


def validate() -> tuple[dict[str, int], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not path.exists()]
    weekly_summary = load_json(WEEKLY_SUMMARY)
    weekly_review = load_json(WEEKLY_REVIEW)
    week_decision = load_json(WEEK_DECISION)
    revenue_matrix = load_json(REVENUE_MATRIX)
    offer_board = load_json(OFFER_BOARD)
    offer_plan = load_json(OFFER_PLAN)
    offer_queue = load_json(OFFER_QUEUE)
    next_actions = load_json(NEXT_ACTIONS)
    launch_readiness = load_json(LAUNCH_READINESS)
    first_batch = load_json(FIRST_BATCH)
    issues: list[str] = []
    for path in missing_files:
        issues.append(f"required promotion decision file is missing: {path.relative_to(ROOT)}")

    empty_data_mode = bool(weekly_summary.get("safety", {}).get("emptyDataMode"))
    if not empty_data_mode:
        return {
            "emptyDataMode": 0,
            "failClosedChecks": 0,
            "blockedOfferRows": 0,
            "blockedExperimentRows": 0,
        }, issues

    checks = 0
    if not revenue_matrix.get("dataState", {}).get("emptyDataMode"):
        issues.append("revenue decision matrix should be in empty data mode")
    checks += 1
    if weekly_review.get("state", {}).get("readyForWeeklyDecision"):
        issues.append("weekly review should not be ready in empty data mode")
    checks += 1
    if not BLOCKED_DECISIONS.issubset(set(weekly_review.get("blockedDecisions", []))):
        issues.append("weekly review should block commerce and winner decisions")
    checks += 1
    gates = week_decision.get("gates", {})
    if any(gates.get(key) for key in ("weeklyDecision", "scaleContent", "deepenIdentityAsset", "buildOwnedLeadAsset", "testSoftOffer")):
        issues.append("week decision gates should all hold in empty data mode")
    checks += 1
    if week_decision.get("recommendedFocus") != "collect_signal":
        issues.append("week decision focus should remain collect_signal")
    checks += 1
    if any(row.get("readiness") != "HOLD" for row in offer_board.get("rows", [])):
        issues.append("offer hypothesis rows should all be HOLD")
    checks += 1
    if any(row.get("status") != "HOLD" for row in offer_plan.get("experiments", [])):
        issues.append("offer experiments should all be HOLD")
    checks += 1
    if not all_rows_status(offer_queue, "rows", {"blocked"}):
        issues.append("offer experiment queue rows should all be blocked")
    checks += 1
    if not next_actions.get("dataState", {}).get("emptyDataMode"):
        issues.append("next actions should preserve empty data mode")
    checks += 1
    if launch_readiness.get("readyToPublish"):
        issues.append("launch readiness should not be ready to publish before profile setup")
    checks += 1
    if int(first_batch.get("publishedRows", 0) or 0) != 0 or int(first_batch.get("minimumKpiRows", 0) or 0) != 0:
        issues.append("first batch should have no published or minimum KPI rows in empty data mode")
    checks += 1
    if int(revenue_matrix.get("filledRows", 0) or 0) != 0 or int(revenue_matrix.get("filledProfileRows", 0) or 0) != 0:
        issues.append("revenue matrix should have zero filled video/profile rows")
    checks += 1

    return {
        "emptyDataMode": 1,
        "failClosedChecks": checks,
        "blockedOfferRows": sum(1 for row in offer_board.get("rows", []) if row.get("readiness") == "HOLD"),
        "blockedExperimentRows": sum(1 for row in offer_plan.get("experiments", []) if row.get("status") == "HOLD"),
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_empty_data_safety_empty_mode={metrics['emptyDataMode']}")
    print(f"promotion_empty_data_safety_fail_closed_checks={metrics['failClosedChecks']}")
    print(f"promotion_empty_data_safety_blocked_offer_rows={metrics['blockedOfferRows']}")
    print(f"promotion_empty_data_safety_blocked_experiment_rows={metrics['blockedExperimentRows']}")
    print(f"promotion_empty_data_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
