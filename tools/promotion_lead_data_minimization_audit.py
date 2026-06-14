#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "lead-data-minimization-audit.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "lead-data-minimization-audit.md"

EXPECTED_FIELDS = [
    "request_id",
    "date",
    "source",
    "utm_content",
    "contact_campaign_content",
    "guardian_id",
    "guardian_name",
    "intake_type",
    "requested_asset",
    "related_route",
    "kpi_writeback_field",
    "kpi_writeback_rule",
    "email_status",
    "consent_status",
    "priority",
    "status",
    "first_response",
    "next_action",
    "follow_up_deadline",
    "fulfillment_asset",
    "notes",
]
GUARDIANS = {"iris", "noah", "vivian", "claire", "dora"}
INTAKE_TYPES = {
    "owned_asset_request": "supply_lead_requests",
    "luna_scene_request": "luna_pack_clicks",
    "repair_or_contact_request": "contact_requests",
}
TEMPLATE_CONSENT = "not_applicable_until_user_contacts"
REAL_CONSENT = {"explicit_reply_ok"}
REAL_STATUSES = {"new", "triaged", "queued", "fulfilled", "closed"}
REAL_SOURCES = {"contact", "keepsake_waitlist", "resources_wishlist", "luna_page", "manual_reply"}
RAW_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
SENSITIVE_TOKENS = (
    "phone",
    "tel",
    "address",
    "birthday",
    "birthdate",
    "diagnosis",
    "medical",
    "therapy notes",
    "身分證",
    "電話",
    "地址",
    "生日",
    "病歷",
    "診斷",
)


def read_tracker() -> tuple[list[str], list[dict[str, str]]]:
    with LEAD_TRACKER.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def has_raw_email(row: dict[str, str]) -> bool:
    return any(RAW_EMAIL_RE.search(value or "") for value in row.values())


def has_sensitive_token(row: dict[str, str]) -> bool:
    user_supplied_fields = (
        "requested_asset",
        "first_response",
        "next_action",
        "fulfillment_asset",
        "notes",
    )
    haystack = " ".join(row.get(field, "") or "" for field in user_supplied_fields).lower()
    return any(token.lower() in haystack for token in SENSITIVE_TOKENS)


def row_is_template(row: dict[str, str]) -> bool:
    return row.get("status") == "template"


def validate(fieldnames: list[str], rows: list[dict[str, str]]) -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    if fieldnames != EXPECTED_FIELDS:
        missing = [field for field in EXPECTED_FIELDS if field not in fieldnames]
        extra = [field for field in fieldnames if field not in EXPECTED_FIELDS]
        if missing:
            issues.append("lead tracker missing fields: " + ", ".join(missing))
        if extra:
            issues.append("lead tracker has non-minimized extra fields: " + ", ".join(extra))
        if not missing and not extra:
            issues.append("lead tracker fields changed order; keep the reviewed schema stable")

    seen_request_ids: set[str] = set()
    template_rows = 0
    real_rows = 0
    template_minimized = 0
    explicit_consent_rows = 0
    raw_email_rows = 0
    sensitive_rows = 0
    route_rows = 0

    for index, row in enumerate(rows, start=2):
        request_id = (row.get("request_id") or "").strip()
        if not request_id:
            issues.append(f"row {index}: missing request_id")
        elif request_id in seen_request_ids:
            issues.append(f"{request_id}: duplicate request_id")
        seen_request_ids.add(request_id)

        guardian = row.get("guardian_id", "")
        intake = row.get("intake_type", "")
        expected_kpi = INTAKE_TYPES.get(intake)
        if guardian not in GUARDIANS:
            issues.append(f"{request_id or 'row ' + str(index)}: invalid guardian_id {guardian!r}")
        if expected_kpi is None:
            issues.append(f"{request_id or 'row ' + str(index)}: invalid intake_type {intake!r}")
        elif row.get("kpi_writeback_field") != expected_kpi:
            issues.append(f"{request_id}: kpi_writeback_field should be {expected_kpi}")
        if row.get("related_route", "").startswith("https://lovetypes.tw/"):
            route_rows += 1
        else:
            issues.append(f"{request_id}: related_route must stay on lovetypes.tw")

        if has_raw_email(row):
            raw_email_rows += 1
            issues.append(f"{request_id}: raw email address must not be stored in lead tracker")
        if row_is_template(row):
            template_rows += 1
            required_empty = ("date", "utm_content", "follow_up_deadline", "fulfillment_asset")
            if row.get("source") != "template":
                issues.append(f"{request_id}: template source must be template")
            if row.get("email_status") != "not_received":
                issues.append(f"{request_id}: template email_status must be not_received")
            if row.get("consent_status") != TEMPLATE_CONSENT:
                issues.append(f"{request_id}: template consent_status must be {TEMPLATE_CONSENT}")
            if row.get("notes") == "No user data. Replace this template row only after a real request arrives.":
                template_minimized += 1
            else:
                issues.append(f"{request_id}: template notes must state no user data")
            for field in required_empty:
                if row.get(field):
                    issues.append(f"{request_id}: template field {field} must remain empty")
        else:
            real_rows += 1
            if has_sensitive_token(row):
                sensitive_rows += 1
                issues.append(f"{request_id}: potential sensitive personal data field/token found")
            if row.get("source") not in REAL_SOURCES:
                issues.append(f"{request_id}: invalid real source {row.get('source')!r}")
            if row.get("status") not in REAL_STATUSES:
                issues.append(f"{request_id}: invalid real status {row.get('status')!r}")
            if row.get("consent_status") in REAL_CONSENT:
                explicit_consent_rows += 1
            else:
                issues.append(f"{request_id}: real lead requires explicit_reply_ok consent")
            if not row.get("date"):
                issues.append(f"{request_id}: real lead requires date")
            if "verified:" not in row.get("notes", ""):
                issues.append(f"{request_id}: real lead requires traceable verified note")
            if row.get("email_status") not in {"received", "replied", "fulfilled", "closed"}:
                issues.append(f"{request_id}: real lead must have received/replied/fulfilled/closed email_status")

    metrics = {
        "fields": len(fieldnames),
        "expectedFields": len(EXPECTED_FIELDS),
        "rows": len(rows),
        "templateRows": template_rows,
        "templateMinimizedRows": template_minimized,
        "realRows": real_rows,
        "explicitConsentRows": explicit_consent_rows,
        "rawEmailRows": raw_email_rows,
        "sensitiveRows": sensitive_rows,
        "routeRows": route_rows,
    }
    return metrics, issues


def build_report() -> dict:
    fieldnames, rows = read_tracker()
    metrics, issues = validate(fieldnames, rows)
    return {
        "generatedAt": date.today().isoformat(),
        "source": {"leadIntakeTracker": str(LEAD_TRACKER.relative_to(ROOT))},
        "metrics": {**metrics, "issues": len(issues)},
        "expectedFields": EXPECTED_FIELDS,
        "allowed": {
            "guardians": sorted(GUARDIANS),
            "intakeTypes": INTAKE_TYPES,
            "templateConsent": TEMPLATE_CONSENT,
            "realConsent": sorted(REAL_CONSENT),
            "realStatuses": sorted(REAL_STATUSES),
            "realSources": sorted(REAL_SOURCES),
        },
        "safety": {
            "rawEmailStored": metrics["rawEmailRows"] > 0,
            "sensitiveTokensDetected": metrics["sensitiveRows"] > 0,
            "templateRowsContainNoUserData": metrics["templateRows"] == metrics["templateMinimizedRows"],
            "realRowsRequireExplicitConsent": True,
            "relatedRoutesStayOnLoveTypes": metrics["routeRows"] == metrics["rows"],
        },
        "issues": issues,
    }


def render_markdown(report: dict) -> str:
    metrics = report["metrics"]
    lines = [
        "# LoveTypes Lead Data Minimization Audit",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- tracker rows：{metrics['rows']}",
        f"- template rows：{metrics['templateRows']}",
        f"- real rows：{metrics['realRows']}",
        f"- raw email rows：{metrics['rawEmailRows']}",
        f"- sensitive rows：{metrics['sensitiveRows']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Safety",
        "",
    ]
    for key, value in report["safety"].items():
        lines.append(f"- {key}: `{int(bool(value))}`")
    lines.extend(["", "## Allowed Fields", ""])
    lines.extend(f"- `{field}`" for field in report["expectedFields"])
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in report["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict, json_output: Path, md_output: Path) -> None:
    json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_output.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit LoveTypes lead tracker data minimization rules.")
    parser.add_argument("--check", action="store_true", help="Validate without writing generated outputs.")
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    args = parser.parse_args()

    report = build_report()
    metrics = report["metrics"]
    issues = report["issues"]
    if not args.check:
        write_outputs(report, Path(args.json_output), Path(args.output))
        print(f"promotion_lead_data_minimization_audit={args.output}")
        print(f"promotion_lead_data_minimization_audit_json={args.json_output}")
    print(f"promotion_lead_data_min_fields={metrics['fields']}")
    print(f"promotion_lead_data_min_expected_fields={metrics['expectedFields']}")
    print(f"promotion_lead_data_min_rows={metrics['rows']}")
    print(f"promotion_lead_data_min_template_rows={metrics['templateRows']}")
    print(f"promotion_lead_data_min_template_minimized_rows={metrics['templateMinimizedRows']}")
    print(f"promotion_lead_data_min_real_rows={metrics['realRows']}")
    print(f"promotion_lead_data_min_explicit_consent_rows={metrics['explicitConsentRows']}")
    print(f"promotion_lead_data_min_raw_email_rows={metrics['rawEmailRows']}")
    print(f"promotion_lead_data_min_sensitive_rows={metrics['sensitiveRows']}")
    print(f"promotion_lead_data_min_route_rows={metrics['routeRows']}")
    print(f"promotion_lead_data_min_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
