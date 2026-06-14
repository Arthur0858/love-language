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
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"
MD_OUTPUT = PROMOTION_DIR / "lead-tracker-summary.md"
JSON_OUTPUT = PROMOTION_DIR / "lead-tracker-summary.json"
GUARDIANS = ("iris", "noah", "vivian", "claire", "dora")
INTAKE_TYPES = ("owned_asset_request", "luna_scene_request", "repair_or_contact_request")
TEMPLATE_STATUS = "template"
REAL_CONSENT = "explicit_reply_ok"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def is_real(row: dict[str, str]) -> bool:
    return (row.get("status") or "").strip() != TEMPLATE_STATUS


def is_traceable(row: dict[str, str]) -> bool:
    notes = row.get("notes") or ""
    return "verified:" in notes or "checked" in notes or "message id" in notes.lower()


def build_summary(rows: list[dict[str, str]]) -> dict:
    real_rows = [row for row in rows if is_real(row)]
    by_guardian = Counter(row.get("guardian_id", "") for row in real_rows)
    by_intake = Counter(row.get("intake_type", "") for row in real_rows)
    by_source = Counter(row.get("source", "") for row in real_rows)
    by_status = Counter(row.get("status", "") for row in rows)
    by_pair = Counter((row.get("guardian_id", ""), row.get("intake_type", "")) for row in real_rows)
    pair_rows = [
        {
            "guardianId": guardian,
            "intakeType": intake,
            "realLeads": by_pair[(guardian, intake)],
        }
        for guardian in GUARDIANS
        for intake in INTAKE_TYPES
    ]
    explicit_consent = sum(1 for row in real_rows if row.get("consent_status") == REAL_CONSENT)
    matched_utm = sum(1 for row in real_rows if (row.get("utm_content") or "").strip())
    traceable = sum(1 for row in real_rows if is_traceable(row))
    return {
        "generatedAt": date.today().isoformat(),
        "source": str(LEAD_TRACKER.relative_to(ROOT)),
        "policy": {
            "summaryOnly": True,
            "doesNotIncludeRequestRows": True,
            "doesNotStoreRawEmail": True,
            "realConsentRequired": REAL_CONSENT,
            "repeatDemandThreshold": 2,
        },
        "metrics": {
            "totalRows": len(rows),
            "templateRows": len(rows) - len(real_rows),
            "realRows": len(real_rows),
            "explicitConsentRows": explicit_consent,
            "matchedUtmRows": matched_utm,
            "traceableRows": traceable,
            "guardianCount": len(GUARDIANS),
            "intakeTypeCount": len(INTAKE_TYPES),
        },
        "counts": {
            "byGuardian": {guardian: by_guardian[guardian] for guardian in GUARDIANS},
            "byIntakeType": {intake: by_intake[intake] for intake in INTAKE_TYPES},
            "bySource": dict(sorted((key, value) for key, value in by_source.items() if key)),
            "byStatus": dict(sorted((key, value) for key, value in by_status.items() if key)),
            "byGuardianIntake": pair_rows,
        },
    }


def validate(summary: dict) -> list[str]:
    issues: list[str] = []
    policy = summary.get("policy", {})
    metrics = summary.get("metrics", {})
    counts = summary.get("counts", {})
    if policy.get("summaryOnly") is not True or policy.get("doesNotIncludeRequestRows") is not True:
        issues.append("lead summary must stay aggregate-only")
    if policy.get("doesNotStoreRawEmail") is not True:
        issues.append("lead summary policy must prohibit raw email storage")
    if metrics.get("realRows", 0) < metrics.get("explicitConsentRows", 0):
        issues.append("explicit consent rows cannot exceed real rows")
    if metrics.get("realRows", 0) < metrics.get("matchedUtmRows", 0):
        issues.append("matched UTM rows cannot exceed real rows")
    if metrics.get("realRows", 0) < metrics.get("traceableRows", 0):
        issues.append("traceable rows cannot exceed real rows")
    by_pair = counts.get("byGuardianIntake", [])
    if not isinstance(by_pair, list) or len(by_pair) != len(GUARDIANS) * len(INTAKE_TYPES):
        issues.append("lead summary must include every guardian/intake pair")
    if "rows" in summary:
        issues.append("lead summary must not include raw row payloads")
    return issues


def render_markdown(summary: dict, issues: list[str]) -> str:
    metrics = summary["metrics"]
    counts = summary["counts"]
    lines = [
        "# LoveTypes Lead Tracker Summary",
        "",
        f"- 產生日期：{summary['generatedAt']}",
        f"- source：`{summary['source']}`",
        f"- total rows：{metrics['totalRows']}",
        f"- template rows：{metrics['templateRows']}",
        f"- real rows：{metrics['realRows']}",
        f"- explicit consent rows：{metrics['explicitConsentRows']}",
        f"- matched UTM rows：{metrics['matchedUtmRows']}",
        f"- traceable rows：{metrics['traceableRows']}",
        f"- issues：{len(issues)}",
        "",
        "## Policy",
        "",
        "- This file is aggregate-only and does not duplicate request rows.",
        "- Raw reply emails are not stored here or in lead-intake-tracker.csv.",
        "- Use repeated same-guardian demand only after explicit consent and traceable proof.",
        "",
        "## Guardian / Intake Counts",
        "",
    ]
    for row in counts["byGuardianIntake"]:
        lines.append(f"- `{row['guardianId']}` / `{row['intakeType']}`：{row['realLeads']}")
    lines.extend(["", "## Status Counts", ""])
    for status, value in counts["byStatus"].items():
        lines.append(f"- `{status}`：{value}")
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(summary: dict, issues: list[str]) -> None:
    JSON_OUTPUT.write_text(json.dumps({**summary, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(render_markdown(summary, issues), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an aggregate-only summary of LoveTypes lead intake tracker state.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    args = parser.parse_args()

    summary = build_summary(read_rows(LEAD_TRACKER))
    issues = validate(summary)
    if not args.check:
        write_outputs(summary, issues)
        print(f"promotion_lead_tracker_summary={MD_OUTPUT}")
        print(f"promotion_lead_tracker_summary_json={JSON_OUTPUT}")
    metrics = summary["metrics"]
    print(f"promotion_lead_tracker_summary_rows={metrics['totalRows']}")
    print(f"promotion_lead_tracker_summary_template_rows={metrics['templateRows']}")
    print(f"promotion_lead_tracker_summary_real_rows={metrics['realRows']}")
    print(f"promotion_lead_tracker_summary_explicit_consent_rows={metrics['explicitConsentRows']}")
    print(f"promotion_lead_tracker_summary_matched_utm_rows={metrics['matchedUtmRows']}")
    print(f"promotion_lead_tracker_summary_traceable_rows={metrics['traceableRows']}")
    print(f"promotion_lead_tracker_summary_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
