#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
WEEK_DECISION_GATE = PROMOTION_DIR / "week-decision-gate.json"
PUBLIC_POST_URL = PROMOTION_DIR / "public-post-url-checklist.json"
ZERO_KPI = PROMOTION_DIR / "zero-kpi-evidence-checklist.json"
PROFILE_COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
FIRST_BATCH_COMPLETION = PROMOTION_DIR / "first-batch-completion-gate.json"
OUTPUT_MD = PROMOTION_DIR / "weekly-decision-evidence-checklist.md"
OUTPUT_JSON = PROMOTION_DIR / "weekly-decision-evidence-checklist.json"
OUTPUT_CSV = PROMOTION_DIR / "weekly-decision-evidence-checklist.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def status(ok: bool, pending_reason: str) -> tuple[str, str]:
    return ("complete", "證據已滿足。") if ok else ("pending", pending_reason)


def build_payload() -> dict:
    weekly = load_json(WEEKLY_REVIEW)
    decision = load_json(WEEK_DECISION_GATE)
    public_url = load_json(PUBLIC_POST_URL)
    zero_kpi = load_json(ZERO_KPI)
    profile = load_json(PROFILE_COMPLETION)
    first_batch = load_json(FIRST_BATCH_COMPLETION)

    weekly_state = weekly.get("state", {})
    decision_gates = decision.get("gates", {})
    public_metrics = public_url.get("metrics", {})
    zero_metrics = zero_kpi.get("metrics", {})
    profile_metrics = profile.get("metrics", {})
    first_batch_metrics = first_batch.get("metrics", {})

    checks = [
        {
            "check_id": "profiles_configured",
            "phase": "profile_setup",
            "expected": "All active platform profile links are set/live with traceable evidence.",
            "result": status(
                int(profile_metrics.get("configured", 0) or 0) == int(profile_metrics.get("expected", 1) or 1),
                "啟用平台 profile 尚未全部 set/live。",
            ),
        },
        {
            "check_id": "first_batch_published",
            "phase": "publish_first_batch",
            "expected": "First-batch posts are published on all active platforms.",
            "result": status(
                int(first_batch_metrics.get("publishedRows", 0) or 0) == int(first_batch_metrics.get("rowCount", first_batch_metrics.get("rows", 1)) or 1),
                "首批啟用平台尚未全部發布。",
            ),
        },
        {
            "check_id": "public_post_urls_verified",
            "phase": "publish_first_batch",
            "expected": "Every public post URL has platform domain, public view, CTA, UTM, and proof evidence checked.",
            "result": status(
                int(public_metrics.get("publishedPosts", 0) or 0) == int(public_metrics.get("posts", 1) or 1)
                and int(public_metrics.get("pendingPublishRows", 0) or 0) == 0
                and int(public_metrics.get("missingRows", 0) or 0) == 0,
                "公開貼文 URL 檢查仍有 pending 或缺證據。",
            ),
        },
        {
            "check_id": "zero_kpis_have_source",
            "phase": "kpi_backfill",
            "expected": "Zero values for site_clicks, quiz_starts, and quiz_completions have checked-source proof.",
            "result": status(
                int(zero_metrics.get("publishedPosts", 0) or 0) == int(zero_metrics.get("posts", 1) or 1)
                and int(zero_metrics.get("pendingPublishRows", 0) or 0) == 0
                and int(zero_metrics.get("needsSourceProofRows", 0) or 0) == 0
                and int(zero_metrics.get("missingRows", 0) or 0) == 0,
                "核心 KPI 仍未發布、未回填，或 0 值缺來源證據。",
            ),
        },
        {
            "check_id": "weekly_review_ready",
            "phase": "weekly_review",
            "expected": "Weekly review packet reports readyForWeeklyDecision=1.",
            "result": status(
                bool(weekly_state.get("readyForWeeklyDecision")),
                "weekly review 尚未達可決策狀態。",
            ),
        },
        {
            "check_id": "not_empty_data_mode",
            "phase": "weekly_review",
            "expected": "Empty data mode is false before commerce or prioritization decisions.",
            "result": status(
                not bool(weekly_state.get("emptyDataMode")) and not bool(decision.get("safety", {}).get("emptyDataFailClosed")),
                "目前仍是空資料安全模式。",
            ),
        },
        {
            "check_id": "decision_gate_ready",
            "phase": "weekly_decision",
            "expected": "Week decision gate allows at least weeklyDecision before changing content or commerce paths.",
            "result": status(
                bool(decision_gates.get("weeklyDecision")),
                "week decision gate 仍是 HOLD。",
            ),
        },
        {
            "check_id": "commerce_changes_still_blocked",
            "phase": "commerce_safety",
            "expected": "Paid CTA, Luna emphasis, affiliate emphasis, and offer order remain blocked until intent exists.",
            "result": status(
                not bool(decision_gates.get("testSoftOffer")) and not bool(decision_gates.get("buildOwnedLeadAsset")),
                "若商品 gate 已開，需先確認 paid/lead intent 證據。",
            ),
        },
    ]
    rows = []
    for item in checks:
        operator_status, evidence_note = item["result"]
        rows.append({
            "phase": item["phase"],
            "check_id": item["check_id"],
            "expected_value": item["expected"],
            "operator_status": operator_status,
            "evidence_note": evidence_note,
        })
    return {
        "generatedAt": today(),
        "sources": {
            "weeklyReview": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "weekDecisionGate": str(WEEK_DECISION_GATE.relative_to(ROOT)),
            "publicPostUrl": str(PUBLIC_POST_URL.relative_to(ROOT)),
            "zeroKpi": str(ZERO_KPI.relative_to(ROOT)),
            "profileCompletion": str(PROFILE_COMPLETION.relative_to(ROOT)),
            "firstBatchCompletion": str(FIRST_BATCH_COMPLETION.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "completeRows": sum(1 for row in rows if row["operator_status"] == "complete"),
            "pendingRows": sum(1 for row in rows if row["operator_status"] == "pending"),
            "weeklyReady": 1 if weekly_state.get("readyForWeeklyDecision") else 0,
            "decisionReady": 1 if decision_gates.get("weeklyDecision") else 0,
            "emptyDataMode": 1 if weekly_state.get("emptyDataMode") or decision.get("safety", {}).get("emptyDataFailClosed") else 0,
        },
        "policy": {
            "doNotUseSingleMetricForCommerce": True,
            "weeklyDecisionRequiresAllEvidence": True,
            "emptyDataFailsClosed": True,
        },
        "items": rows,
    }


def validate(payload: dict) -> list[str]:
    issues: list[str] = []
    metrics = payload["metrics"]
    if metrics["rows"] != 8:
        issues.append(f"expected 8 weekly decision evidence rows, got {metrics['rows']}")
    if metrics["completeRows"] + metrics["pendingRows"] != metrics["rows"]:
        issues.append("weekly decision evidence status counts do not add up")
    if metrics["emptyDataMode"] and metrics["decisionReady"]:
        issues.append("weekly decision cannot be ready in empty data mode")
    for row in payload["items"]:
        if not row["phase"] or not row["check_id"] or not row["expected_value"]:
            issues.append("weekly decision evidence row missing phase, check_id, or expected_value")
        if row["operator_status"] not in {"complete", "pending"}:
            issues.append(f"{row['check_id']}: invalid operator_status")
    if not payload["policy"].get("weeklyDecisionRequiresAllEvidence"):
        issues.append("policy must require all evidence for weekly decision")
    return issues


def render_markdown(payload: dict, issues: list[str]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes Weekly Decision Evidence Checklist",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- checklist rows：{metrics['rows']}",
        f"- complete rows：{metrics['completeRows']}",
        f"- pending rows：{metrics['pendingRows']}",
        f"- weekly ready：{metrics['weeklyReady']}",
        f"- decision ready：{metrics['decisionReady']}",
        f"- empty data mode：{metrics['emptyDataMode']}",
        "- 用途：週回顧前確認 profile、公開貼文、KPI、0 值來源與空資料安全邊界都已滿足。",
        "",
        "## Rule",
        "",
        "- 不能用單一指標或空資料調整商品、Luna、聯盟或守護者優先序。",
        "- 週決策必須同時具備公開 URL、KPI 來源、週摘要與 gate 通過。",
        "- 只要仍是 empty data mode，就保持收集訊號，不做商品化判斷。",
        "",
    ]
    for row in payload["items"]:
        marker = "x" if row["operator_status"] == "complete" else " "
        lines.append(f"- [{marker}] `{row['check_id']}`：{row['expected_value']}（{row['operator_status']}；{row['evidence_note']}）")
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict, issues: list[str]) -> None:
    OUTPUT_JSON.write_text(json.dumps({**payload, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload, issues), encoding="utf-8")
    fieldnames = ["phase", "check_id", "expected_value", "operator_status", "evidence_note"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(payload["items"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a weekly decision evidence checklist for LoveTypes promotion gates.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    issues = validate(payload)
    if not args.check:
        write_outputs(payload, issues)
        print(f"promotion_weekly_decision_evidence_csv={OUTPUT_CSV}")
        print(f"promotion_weekly_decision_evidence_json={OUTPUT_JSON}")
        print(f"promotion_weekly_decision_evidence_md={OUTPUT_MD}")
    metrics = payload["metrics"]
    print(f"promotion_weekly_decision_evidence_rows={metrics['rows']}")
    print(f"promotion_weekly_decision_evidence_complete={metrics['completeRows']}")
    print(f"promotion_weekly_decision_evidence_pending={metrics['pendingRows']}")
    print(f"promotion_weekly_decision_evidence_weekly_ready={metrics['weeklyReady']}")
    print(f"promotion_weekly_decision_evidence_decision_ready={metrics['decisionReady']}")
    print(f"promotion_weekly_decision_evidence_empty_data={metrics['emptyDataMode']}")
    print(f"promotion_weekly_decision_evidence_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
