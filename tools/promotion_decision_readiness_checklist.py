#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
WEEK_DECISION_PATH = PROMOTION_DIR / "week-decision-gate.json"
REVENUE_MATRIX_PATH = PROMOTION_DIR / "revenue-decision-matrix.json"
WEEKLY_SUMMARY_PATH = PROMOTION_DIR / "weekly-summary.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "decision-readiness-checklist.csv"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "decision-readiness-checklist.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "decision-readiness-checklist.md"

FIELDNAMES = [
    "decision_id",
    "status",
    "required_signal",
    "current_value",
    "required_value",
    "allowed_action",
    "blocked_action",
    "evidence_source",
    "operator_status",
    "notes",
]

DECISIONS = [
    {
        "decision_id": "collect_signal",
        "gate_key": "weeklyDecision",
        "required_signal": "profile links and first-batch publication not complete",
        "required_value": "Allowed while launch is incomplete; do not make commercial decisions.",
        "allowed_action": "Set profile links, publish first batch, backfill post URL and minimum KPI.",
        "blocked_action": "Change offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian.",
    },
    {
        "decision_id": "scale_content",
        "gate_key": "scaleContent",
        "required_signal": "quiz_completions",
        "required_value": "At least the configured scale-content quiz completion threshold and acceptable completion rate.",
        "allowed_action": "Publish more variants for the strongest guardian or pain point while keeping quiz CTA.",
        "blocked_action": "Treat content interest as proof of purchase intent.",
    },
    {
        "decision_id": "deepen_identity_asset",
        "gate_key": "deepenIdentityAsset",
        "required_signal": "identityRouteInterest",
        "required_value": "Any guardian result, route, keepsake, or resource interest after weekly gate is ready.",
        "allowed_action": "Improve free keepsakes, story cards, share images, and result-route assets.",
        "blocked_action": "Move the primary CTA directly to paid products.",
    },
    {
        "decision_id": "build_owned_lead_asset",
        "gate_key": "buildOwnedLeadAsset",
        "required_signal": "leadIntent",
        "required_value": "Any supply lead, contact request, or explicit downloadable asset request.",
        "allowed_action": "Build one low-risk email/download asset for the signaled guardian or route.",
        "blocked_action": "Build a paid product before repeated lead evidence exists.",
    },
    {
        "decision_id": "test_soft_offer",
        "gate_key": "testSoftOffer",
        "required_signal": "paidRevenueIntent",
        "required_value": "Any Luna pack, affiliate book, or other revenue-route click after result-route context.",
        "allowed_action": "Test a soft result-route offer; keep Shorts and profile CTAs focused on the quiz.",
        "blocked_action": "Use direct sales language in first-touch Shorts or profile bio.",
    },
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_value(gate: dict, signal: str) -> str:
    metrics = gate.get("metrics", {})
    aliases = {
        "quiz_completions": "quizCompletions",
        "quiz_starts": "quizStarts",
        "site_clicks": "siteClicks",
    }
    if signal in metrics:
        return str(metrics.get(signal, 0))
    if signal in aliases and aliases[signal] in metrics:
        return str(metrics.get(aliases[signal], 0))
    if signal == "profile links and first-batch publication not complete":
        blockers = gate.get("blockers", [])
        return "blocked" if blockers else "ready"
    return ""


def build_rows() -> list[dict[str, str]]:
    gate = read_json(WEEK_DECISION_PATH)
    matrix = read_json(REVENUE_MATRIX_PATH)
    summary = read_json(WEEKLY_SUMMARY_PATH)
    rows: list[dict[str, str]] = []
    gates = gate.get("gates", {})
    empty_data = bool(gate.get("safety", {}).get("emptyDataFailClosed"))
    recommended = str(gate.get("recommendedFocus", ""))
    thresholds = gate.get("decisionThresholds", {})
    for item in DECISIONS:
        decision_id = item["decision_id"]
        passed = bool(gates.get(item["gate_key"], False))
        if decision_id == "collect_signal":
            status = "active" if recommended == "collect_signal" else "complete"
        else:
            status = "ready" if passed else "blocked"
        required_value = item["required_value"]
        if decision_id == "scale_content":
            required_value += f" Current threshold: {thresholds.get('scaleContentMinQuizCompletions', '')} quiz completions."
        if empty_data and decision_id != "collect_signal":
            required_value += " Empty-data mode forces this decision closed."
        rows.append({
            "decision_id": decision_id,
            "status": status,
            "required_signal": item["required_signal"],
            "current_value": metric_value(gate, item["required_signal"]),
            "required_value": required_value,
            "allowed_action": item["allowed_action"],
            "blocked_action": item["blocked_action"],
            "evidence_source": "; ".join([
                str(WEEK_DECISION_PATH.relative_to(ROOT)),
                str(REVENUE_MATRIX_PATH.relative_to(ROOT)),
                str(WEEKLY_SUMMARY_PATH.relative_to(ROOT)),
            ]),
            "operator_status": "pending" if status in {"active", "ready"} else "blocked",
            "notes": f"matrix_stage={matrix.get('profileDecision', {}).get('stage', '')}; empty_data={int(empty_data)}; summary_rows={summary.get('trackerRows', 0)}",
        })
    return rows


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    if len(rows) != len(DECISIONS):
        issues.append(f"expected {len(DECISIONS)} decision readiness rows, got {len(rows)}")
    decision_ids = {row["decision_id"] for row in rows}
    expected_ids = {item["decision_id"] for item in DECISIONS}
    if decision_ids != expected_ids:
        issues.append("decision readiness rows should cover every decision")
    active_collect = [row for row in rows if row["decision_id"] == "collect_signal" and row["status"] == "active"]
    if active_collect:
        for row in rows:
            if row["decision_id"] != "collect_signal" and row["status"] != "blocked":
                issues.append(f"{row['decision_id']}: should stay blocked while collect_signal is active")
    for row in rows:
        label = row["decision_id"]
        if not row["allowed_action"] or not row["blocked_action"]:
            issues.append(f"{label}: missing allowed or blocked action")
        if "week-decision-gate.json" not in row["evidence_source"]:
            issues.append(f"{label}: missing week decision evidence source")
        if row["decision_id"] != "collect_signal" and "Empty-data mode forces this decision closed." in row["required_value"] and row["status"] != "blocked":
            issues.append(f"{label}: empty data should block non-signal decisions")
    return issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes Decision Readiness Checklist",
        "",
        f"- Generated: `{payload['generatedAt']}`",
        f"- Decisions: `{payload['rows']}`",
        f"- Active signal rows: `{payload['activeSignalRows']}`",
        f"- Ready rows: `{payload['readyRows']}`",
        f"- Blocked rows: `{payload['blockedRows']}`",
        f"- Issues: `{len(payload['issues'])}`",
        "",
        "## Rule",
        "",
        "- Empty or minimum-only data can only support launch execution and KPI backfill.",
        "- Commercial changes require matching route, lead, Luna, affiliate, or contact signals.",
        "- Shorts and profile CTAs remain focused on the quiz until result-route evidence exists.",
        "",
    ]
    for row in payload["items"]:
        lines.extend([
            f"## `{row['decision_id']}`",
            "",
            f"- Status: `{row['status']}`",
            f"- Required signal: {row['required_signal']}",
            f"- Current value: `{row['current_value']}`",
            f"- Required value: {row['required_value']}",
            f"- Allowed: {row['allowed_action']}",
            f"- Blocked: {row['blocked_action']}",
            f"- Evidence: `{row['evidence_source']}`",
            "",
        ])
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes weekly decision readiness checklist.")
    parser.add_argument("--check", action="store_true", help="Validate current decision readiness rows without writing outputs.")
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    args = parser.parse_args()

    rows = build_rows()
    issues = validate_rows(rows)
    payload = {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "weekDecisionGate": str(WEEK_DECISION_PATH.relative_to(ROOT)),
            "revenueDecisionMatrix": str(REVENUE_MATRIX_PATH.relative_to(ROOT)),
            "weeklySummary": str(WEEKLY_SUMMARY_PATH.relative_to(ROOT)),
        },
        "rows": len(rows),
        "activeSignalRows": sum(1 for row in rows if row["status"] == "active"),
        "readyRows": sum(1 for row in rows if row["status"] == "ready"),
        "blockedRows": sum(1 for row in rows if row["status"] == "blocked"),
        "items": rows,
        "issues": issues,
    }
    print(f"promotion_decision_readiness_rows={payload['rows']}")
    print(f"promotion_decision_readiness_active_signal={payload['activeSignalRows']}")
    print(f"promotion_decision_readiness_ready={payload['readyRows']}")
    print(f"promotion_decision_readiness_blocked={payload['blockedRows']}")
    print(f"promotion_decision_readiness_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        write_csv(rows, Path(args.csv_output))
        Path(args.json_output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        Path(args.output).write_text(render_markdown(payload), encoding="utf-8")
        print(f"promotion_decision_readiness_csv={Path(args.csv_output).relative_to(ROOT)}")
        print(f"promotion_decision_readiness_json={Path(args.json_output).relative_to(ROOT)}")
        print(f"promotion_decision_readiness_md={Path(args.output).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
