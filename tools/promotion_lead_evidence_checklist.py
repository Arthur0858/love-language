#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"
OUTPUT_MD = PROMOTION_DIR / "lead-evidence-checklist.md"
OUTPUT_JSON = PROMOTION_DIR / "lead-evidence-checklist.json"
OUTPUT_CSV = PROMOTION_DIR / "lead-evidence-checklist.csv"

REQUIRED_CHECKS = [
    {
        "check_id": "source_traceable",
        "label": "來源可追蹤",
        "evidence": "source is contact, keepsake_waitlist, resources_wishlist, luna_page, or manual_reply.",
    },
    {
        "check_id": "guardian_route_present",
        "label": "守護者與路線存在",
        "evidence": "guardian_id, guardian_name, and related_route are present.",
    },
    {
        "check_id": "intake_type_present",
        "label": "需求類型明確",
        "evidence": "intake_type maps to owned asset, Luna scene, or repair/contact request.",
    },
    {
        "check_id": "asset_preference_present",
        "label": "素材偏好明確",
        "evidence": "requested_asset describes the requested PDF, wallpaper, ritual, Luna scene, or repair prompt.",
    },
    {
        "check_id": "reply_email_available",
        "label": "可回覆信箱已取得",
        "evidence": "reply email exists in the source email or structured request, but raw email is not stored in CSV.",
    },
    {
        "check_id": "explicit_consent",
        "label": "明確同意可回覆",
        "evidence": "consent_status is explicit_reply_ok before any KPI or fulfillment writeback.",
    },
    {
        "check_id": "attribution_or_manual_rule",
        "label": "歸因規則已判定",
        "evidence": "utm_content is matched for KPI writeback, or left as manual lead only.",
    },
    {
        "check_id": "safe_scope_verified",
        "label": "安全範圍已確認",
        "evidence": "request is not emergency support, diagnosis, therapy replacement, or sensitive personal-data collection.",
    },
    {
        "check_id": "proof_note_traceable",
        "label": "證據註記可追溯",
        "evidence": "notes include a verified proof note or the operator has a traceable external proof note.",
    },
]


def today() -> str:
    return date.today().isoformat()


def read_tracker() -> tuple[list[str], list[dict[str, str]]]:
    with LEAD_TRACKER.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def row_status(lead: dict[str, str], check_id: str) -> tuple[str, str]:
    status = lead.get("status", "")
    source = lead.get("source", "")
    notes = lead.get("notes", "")
    if status == "template":
        return "pending_real_request", "模板列不可標記完成；等真實來信後逐項確認。"

    if check_id == "source_traceable":
        ok = source in {"contact", "keepsake_waitlist", "resources_wishlist", "luna_page", "manual_reply"}
        return ("complete" if ok else "missing", source or "missing source")
    if check_id == "guardian_route_present":
        ok = all(lead.get(field) for field in ("guardian_id", "guardian_name", "related_route"))
        return ("complete" if ok else "missing", "guardian_id + guardian_name + related_route")
    if check_id == "intake_type_present":
        ok = bool(lead.get("intake_type") and lead.get("kpi_writeback_field"))
        return ("complete" if ok else "missing", lead.get("intake_type") or "missing intake_type")
    if check_id == "asset_preference_present":
        ok = bool(lead.get("requested_asset"))
        return ("complete" if ok else "missing", lead.get("requested_asset") or "missing requested_asset")
    if check_id == "reply_email_available":
        ok = lead.get("email_status") in {"received", "replied", "fulfilled", "closed"}
        return ("operator_verify" if ok else "missing", "verify reply email in source; do not store raw email")
    if check_id == "explicit_consent":
        ok = lead.get("consent_status") == "explicit_reply_ok"
        return ("complete" if ok else "missing", lead.get("consent_status") or "missing consent_status")
    if check_id == "attribution_or_manual_rule":
        has_utm = bool((lead.get("utm_content") or "").strip())
        return ("complete" if has_utm else "manual_only", "matched KPI only with utm_content; otherwise qualitative lead")
    if check_id == "safe_scope_verified":
        return ("operator_verify", "confirm no crisis, diagnosis, therapy replacement, or sensitive-data request")
    if check_id == "proof_note_traceable":
        ok = "verified:" in notes
        return ("complete" if ok else "missing", notes or "missing verified proof note")
    return "missing", "unknown check"


def build_checklist(rows: list[dict[str, str]]) -> dict:
    checklist_rows = []
    for lead in rows:
        for check in REQUIRED_CHECKS:
            status, evidence_note = row_status(lead, check["check_id"])
            checklist_rows.append({
                "request_id": lead.get("request_id", ""),
                "guardian_id": lead.get("guardian_id", ""),
                "guardian_name": lead.get("guardian_name", ""),
                "intake_type": lead.get("intake_type", ""),
                "source": lead.get("source", ""),
                "lead_status": lead.get("status", ""),
                "check_id": check["check_id"],
                "check_label": check["label"],
                "required_evidence": check["evidence"],
                "operator_status": status,
                "evidence_note": evidence_note,
            })
    real_rows = [row for row in rows if row.get("status") != "template"]
    return {
        "generatedAt": today(),
        "source": str(LEAD_TRACKER.relative_to(ROOT)),
        "requiredChecks": REQUIRED_CHECKS,
        "metrics": {
            "leadRows": len(rows),
            "templateRows": len(rows) - len(real_rows),
            "realRows": len(real_rows),
            "checksPerLead": len(REQUIRED_CHECKS),
            "checklistRows": len(checklist_rows),
            "pendingTemplateRows": sum(1 for row in checklist_rows if row["operator_status"] == "pending_real_request"),
            "realCompleteRows": sum(1 for row in checklist_rows if row["operator_status"] == "complete"),
            "realManualOnlyRows": sum(1 for row in checklist_rows if row["operator_status"] == "manual_only"),
            "realOperatorVerifyRows": sum(1 for row in checklist_rows if row["operator_status"] == "operator_verify"),
            "missingRows": sum(1 for row in checklist_rows if row["operator_status"] == "missing"),
        },
        "policy": {
            "doNotFakeLeads": True,
            "doNotStoreRawEmail": True,
            "writebackRequires": [
                "traceable source",
                "guardian route",
                "intake type",
                "requested asset",
                "reply email verified outside CSV",
                "explicit_reply_ok consent",
                "attribution or manual-only decision",
                "safe non-emergency scope",
                "verified proof note",
            ],
        },
        "rows": checklist_rows,
    }


def validate(fieldnames: list[str], data: dict) -> list[str]:
    issues: list[str] = []
    required_tracker_fields = {
        "request_id",
        "source",
        "guardian_id",
        "guardian_name",
        "intake_type",
        "requested_asset",
        "related_route",
        "kpi_writeback_field",
        "email_status",
        "consent_status",
        "status",
        "notes",
    }
    missing_fields = sorted(required_tracker_fields - set(fieldnames))
    if missing_fields:
        issues.append("lead tracker missing fields: " + ", ".join(missing_fields))
    metrics = data["metrics"]
    expected_rows = metrics["leadRows"] * metrics["checksPerLead"]
    if metrics["checklistRows"] != expected_rows:
        issues.append(f"expected {expected_rows} checklist rows, got {metrics['checklistRows']}")
    if metrics["checksPerLead"] != len(REQUIRED_CHECKS):
        issues.append("required check count drifted")
    template_rows = [row for row in data["rows"] if row["lead_status"] == "template"]
    if any(row["operator_status"] != "pending_real_request" for row in template_rows):
        issues.append("template leads must stay pending_real_request")
    for row in data["rows"]:
        if not row["request_id"] or not row["check_id"] or not row["required_evidence"]:
            issues.append("checklist row missing request_id, check_id, or evidence")
    if not data["policy"].get("doNotFakeLeads"):
        issues.append("policy must prevent fake leads")
    if not data["policy"].get("doNotStoreRawEmail"):
        issues.append("policy must prevent storing raw email")
    return issues


def render_markdown(data: dict, issues: list[str]) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Lead Evidence Checklist",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- lead rows：{metrics['leadRows']}",
        f"- real rows：{metrics['realRows']}",
        f"- checklist rows：{metrics['checklistRows']}",
        f"- missing rows：{metrics['missingRows']}",
        "- 用途：真實需求寫回 KPI 或素材履約前，逐項確認來源、同意、守護者路線與安全邊界。",
        "- 隱私：不把原始 email 寫進 CSV，只保留可追蹤 request_id 與 proof note。",
        "",
        "## Required Evidence",
        "",
    ]
    for check in data["requiredChecks"]:
        lines.append(f"- `{check['check_id']}`：{check['label']}，{check['evidence']}")
    lines.extend(["", "## Operator Rule", ""])
    lines.extend([
        "- `pending_real_request`：模板列，不能當作真實需求。",
        "- `complete`：欄位證據已存在。",
        "- `operator_verify`：需在信件或外部證據中人工確認，但不可把原始 email 寫入 CSV。",
        "- `manual_only`：可以當質性線索，不可回填為 Shorts / profile 勝出依據。",
        "- `missing`：不可寫回 KPI，不可履約。",
    ])
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, issues: list[str]) -> None:
    OUTPUT_JSON.write_text(json.dumps({**data, "issues": issues}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(data, issues), encoding="utf-8")
    fieldnames = [
        "request_id",
        "guardian_id",
        "guardian_name",
        "intake_type",
        "source",
        "lead_status",
        "check_id",
        "check_label",
        "required_evidence",
        "operator_status",
        "evidence_note",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the LoveTypes real-lead evidence checklist.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    fieldnames, rows = read_tracker()
    data = build_checklist(rows)
    issues = validate(fieldnames, data)
    if not args.check:
        write_outputs(data, issues)
        print(f"promotion_lead_evidence_checklist={OUTPUT_MD}")
        print(f"promotion_lead_evidence_json={OUTPUT_JSON}")
        print(f"promotion_lead_evidence_csv={OUTPUT_CSV}")
    metrics = data["metrics"]
    print(f"promotion_lead_evidence_lead_rows={metrics['leadRows']}")
    print(f"promotion_lead_evidence_real_rows={metrics['realRows']}")
    print(f"promotion_lead_evidence_checks_per_lead={metrics['checksPerLead']}")
    print(f"promotion_lead_evidence_checklist_rows={metrics['checklistRows']}")
    print(f"promotion_lead_evidence_pending_template_rows={metrics['pendingTemplateRows']}")
    print(f"promotion_lead_evidence_missing_rows={metrics['missingRows']}")
    print(f"promotion_lead_evidence_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
