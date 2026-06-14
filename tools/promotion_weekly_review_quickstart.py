#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
WEEKLY_ACTION = PROMOTION_DIR / "weekly-review-action-sheet.json"
WEEKLY_EVIDENCE = PROMOTION_DIR / "weekly-decision-evidence-checklist.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
WEEK_DECISION = PROMOTION_DIR / "week-decision-gate.json"
DECISION_READINESS = PROMOTION_DIR / "decision-readiness-checklist.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "weekly-review-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "weekly-review-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "weekly-review-quickstart.txt"
BLOCKED_DECISIONS = (
    "change_offer_order",
    "pick_winning_guardian",
    "increase_paid_cta",
    "prioritize_luna_or_affiliate",
    "build_paid_product_from_empty_data",
)


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def metric(payload: dict, key: str) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return 0
    try:
        return int(values.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def build_quickstart() -> dict:
    action = read_json(WEEKLY_ACTION)
    evidence = read_json(WEEKLY_EVIDENCE)
    weekly = read_json(WEEKLY_REVIEW)
    decision = read_json(WEEK_DECISION)
    readiness = read_json(DECISION_READINESS)
    weekly_state = weekly.get("state", {}) if isinstance(weekly.get("state"), dict) else {}
    decision_gates = decision.get("gates", {}) if isinstance(decision.get("gates"), dict) else {}
    rows = action.get("rows", []) if isinstance(action.get("rows"), list) else []
    evidence_rows = evidence.get("items", []) if isinstance(evidence.get("items"), list) else []
    readiness_rows = readiness.get("items", []) if isinstance(readiness.get("items"), list) else []
    ready_for_weekly = bool(weekly_state.get("readyForWeeklyDecision"))
    empty_data = bool(weekly_state.get("emptyDataMode")) or bool(decision.get("safety", {}).get("emptyDataFailClosed"))
    quickstart = {
        "generatedAt": today(),
        "sources": {
            "weeklyAction": str(WEEKLY_ACTION.relative_to(ROOT)),
            "weeklyEvidence": str(WEEKLY_EVIDENCE.relative_to(ROOT)),
            "weeklyReview": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "weekDecision": str(WEEK_DECISION.relative_to(ROOT)),
            "decisionReadiness": str(DECISION_READINESS.relative_to(ROOT)),
        },
        "metrics": {
            "actionRows": len(rows),
            "readyRows": sum(1 for row in rows if str(row.get("status", "")).startswith("ready")),
            "blockedRows": sum(1 for row in rows if str(row.get("status", "")).startswith("blocked")),
            "holdRows": sum(1 for row in rows if str(row.get("status", "")) == "hold"),
            "evidenceRows": len(evidence_rows),
            "evidenceComplete": sum(1 for row in evidence_rows if row.get("operator_status") == "complete"),
            "evidencePending": sum(1 for row in evidence_rows if row.get("operator_status") == "pending"),
            "weeklyReady": 1 if ready_for_weekly else 0,
            "decisionReady": 1 if decision_gates.get("weeklyDecision") else 0,
            "emptyDataMode": 1 if empty_data else 0,
            "blockedDecisionRows": sum(1 for row in readiness_rows if str(row.get("status", "")) == "blocked"),
        },
        "rules": [
            "Weekly review starts only after profile links, public post URLs, and minimum KPI source checks are complete.",
            "If empty data mode is active, keep all commerce and prioritization decisions on HOLD.",
            "Do not rank guardians, change offer order, increase paid CTA, or prioritize Luna/affiliate from zero or missing data.",
            "Use weekly summary, week decision gate, and decision readiness checklist as the decision source of truth.",
            "Lead and offer work requires repeated route or lead demand, not template rows or one-off clicks.",
        ],
        "actions": rows,
        "evidence": evidence_rows,
        "blockedDecisions": [decision_id for decision_id in BLOCKED_DECISIONS if decision_id in weekly.get("blockedDecisions", [])],
        "issues": [],
    }
    quickstart["issues"] = validate(quickstart)
    quickstart["metrics"]["issues"] = len(quickstart["issues"])
    return quickstart


def validate(data: dict) -> list[str]:
    issues: list[str] = []
    metrics = data["metrics"]
    if metrics["actionRows"] != 7:
        issues.append(f"expected 7 weekly action rows, got {metrics['actionRows']}")
    if metrics["evidenceRows"] != 8:
        issues.append(f"expected 8 weekly evidence rows, got {metrics['evidenceRows']}")
    if metrics["evidenceComplete"] + metrics["evidencePending"] != metrics["evidenceRows"]:
        issues.append("weekly evidence status counts do not add up")
    if metrics["emptyDataMode"] and metrics["decisionReady"]:
        issues.append("weekly decision cannot be ready in empty data mode")
    if metrics["emptyDataMode"] and len(data["blockedDecisions"]) < 5:
        issues.append("empty data mode must keep core commerce decisions blocked")
    for row in data["actions"]:
        label = row.get("step_id", "<action>")
        if not row.get("command") or not row.get("decision_boundary"):
            issues.append(f"{label}: missing command or decision boundary")
        if row.get("phase") in {"commerce", "decision"} and metrics["emptyDataMode"] and str(row.get("status", "")).startswith("ready"):
            issues.append(f"{label}: commerce or decision row cannot be ready in empty data mode")
    for row in data["evidence"]:
        label = row.get("check_id", "<evidence>")
        if not row.get("expected_value") or not row.get("evidence_note"):
            issues.append(f"{label}: missing expected value or evidence note")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Weekly Review Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- action rows：{metrics['actionRows']}",
        f"- ready / blocked / hold rows：{metrics['readyRows']} / {metrics['blockedRows']} / {metrics['holdRows']}",
        f"- evidence complete / pending：{metrics['evidenceComplete']} / {metrics['evidencePending']}",
        f"- weekly ready：{metrics['weeklyReady']}",
        f"- decision ready：{metrics['decisionReady']}",
        f"- empty data mode：{metrics['emptyDataMode']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Actions", ""])
    for row in data["actions"]:
        lines.extend([
            f"### `{row.get('step_id', '')}`",
            "",
            f"- phase：`{row.get('phase', '')}`",
            f"- status：`{row.get('status', '')}`",
            f"- action：{row.get('operator_action', '')}",
            f"- command：`{row.get('command', '')}`",
            f"- evidence：{row.get('evidence_required', '')}",
            f"- boundary：{row.get('decision_boundary', '')}",
            "",
        ])
    lines.extend(["## Evidence Checklist", ""])
    for row in data["evidence"]:
        marker = "x" if row.get("operator_status") == "complete" else " "
        lines.append(
            f"- [{marker}] `{row.get('check_id', '')}`：{row.get('expected_value', '')}"
            f"（{row.get('operator_status', '')}；{row.get('evidence_note', '')}）"
        )
    lines.extend(["", "## Blocked Decisions", ""])
    lines.extend(f"- `{item}`" for item in data["blockedDecisions"])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes weekly review quickstart",
        f"generated: {data['generatedAt']}",
        f"weekly ready: {metrics['weeklyReady']}",
        f"decision ready: {metrics['decisionReady']}",
        f"empty data mode: {metrics['emptyDataMode']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "Actions:"])
    for row in data["actions"]:
        lines.extend([
            "",
            f"=== {row.get('step_id', '')} ===",
            f"status: {row.get('status', '')}",
            f"action: {row.get('operator_action', '')}",
            f"command: {row.get('command', '')}",
            f"evidence: {row.get('evidence_required', '')}",
            f"boundary: {row.get('decision_boundary', '')}",
        ])
    lines.extend(["", "Evidence checklist:"])
    for row in data["evidence"]:
        lines.append(f"- {row.get('check_id', '')}: {row.get('operator_status', '')} | {row.get('evidence_note', '')}")
    lines.extend(["", "Blocked decisions:"])
    lines.extend(f"- {item}" for item in data["blockedDecisions"])
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a weekly review quickstart packet for LoveTypes promotion decisions.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_weekly_review_quickstart={args.output}")
        print(f"promotion_weekly_review_quickstart_json={args.json_output}")
        print(f"promotion_weekly_review_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_weekly_review_quickstart_action_rows={metrics['actionRows']}")
    print(f"promotion_weekly_review_quickstart_ready_rows={metrics['readyRows']}")
    print(f"promotion_weekly_review_quickstart_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_weekly_review_quickstart_hold_rows={metrics['holdRows']}")
    print(f"promotion_weekly_review_quickstart_evidence_complete={metrics['evidenceComplete']}")
    print(f"promotion_weekly_review_quickstart_evidence_pending={metrics['evidencePending']}")
    print(f"promotion_weekly_review_quickstart_weekly_ready={metrics['weeklyReady']}")
    print(f"promotion_weekly_review_quickstart_decision_ready={metrics['decisionReady']}")
    print(f"promotion_weekly_review_quickstart_empty_data={metrics['emptyDataMode']}")
    print(f"promotion_weekly_review_quickstart_blocked_decision_rows={metrics['blockedDecisionRows']}")
    print(f"promotion_weekly_review_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
