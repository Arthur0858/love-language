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
LEAD_PLAYBOOK = PROMOTION_DIR / "lead-intake-playbook.json"
LEAD_WRITEBACK = PROMOTION_DIR / "lead-writeback-playbook.json"
LEAD_EVIDENCE = PROMOTION_DIR / "lead-evidence-checklist.json"
LEAD_DEMAND = PROMOTION_DIR / "lead-demand-gate.json"
LEAD_MAGNET = PROMOTION_DIR / "lead-magnet-inventory.json"
FORM_AUDIT_TOOL = "tools/promotion_lead_form_audit.py"
FORM_IMPORT_TOOL = "tools/promotion_lead_form_importability_audit.py"
TEXT_IMPORT_TOOL = "tools/promotion_lead_text_import.py"
WRITEBACK_TOOL = "tools/promotion_lead_writeback.py"
OUTPUT_MD = PROMOTION_DIR / "lead-ops-action-sheet.md"
OUTPUT_JSON = PROMOTION_DIR / "lead-ops-action-sheet.json"
OUTPUT_CSV = PROMOTION_DIR / "lead-ops-action-sheet.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def real_leads(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if (row.get("status") or "").strip() != "template"]


def demand_blockers(demand: dict) -> list[str]:
    blockers = demand.get("blockers", [])
    if not isinstance(blockers, list):
        return []
    values: list[str] = []
    for blocker in blockers:
        if isinstance(blocker, dict):
            values.append(str(blocker.get("id") or blocker.get("message") or "unknown_blocker"))
        else:
            values.append(str(blocker))
    return values


def evidence_metrics(evidence: dict) -> dict[str, int]:
    metrics = evidence.get("metrics", {})
    if not isinstance(metrics, dict):
        return {}
    return {str(key): int(value or 0) for key, value in metrics.items() if str(value or "").isdigit()}


def build_rows(playbook: dict, writeback: dict, demand: dict, lead_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    real_count = len(real_leads(lead_rows))
    sources = playbook.get("sourceOptions", [])
    intake_types = playbook.get("intakeTypes", [])
    demand_metrics = demand.get("metrics", {}) if isinstance(demand.get("metrics"), dict) else {}
    blockers = demand_blockers(demand)
    rows = [
        {
            "step_id": "lead-form-health",
            "phase": "capture",
            "status": "ready_to_check",
            "owner_action": "Run lead form and importability audits before treating Contact or keepsake requests as structured leads.",
            "command": f"python3 {FORM_AUDIT_TOOL} && python3 {FORM_IMPORT_TOOL}",
            "evidence_required": "configured/rendered forms and importable sample texts must report issues=0.",
            "next_gate": "structured_request_can_be_copied",
        },
        {
            "step_id": "incoming-request-triage",
            "phase": "triage",
            "status": "waiting_for_real_email" if real_count == 0 else "active",
            "owner_action": "For each real Contact or keepsake email, copy only the LoveTypes structured request block into a temporary text file.",
            "command": f"python3 {TEXT_IMPORT_TOOL} check --input /path/to/request.txt",
            "evidence_required": "source, guardian, intake_type, reply email presence, consent and utm_content parsing all visible in check output.",
            "next_gate": "safe_to_writeback",
        },
        {
            "step_id": "lead-writeback",
            "phase": "writeback",
            "status": "blocked_until_real_request" if real_count == 0 else "ready_for_real_request",
            "owner_action": "Write back only real requests with explicit reply consent and a traceable proof note; never store raw email in the CSV.",
            "command": f"python3 {TEXT_IMPORT_TOOL} add --input /path/to/request.txt --proof-note \"email thread Gmail request checked {today()}\"",
            "evidence_required": "lead-intake-tracker.csv gains one real row, and matched utm_content increments the mapped KPI field.",
            "next_gate": "lead_evidence_checklist",
        },
        {
            "step_id": "evidence-and-demand",
            "phase": "gate",
            "status": "blocked_until_traceable_leads" if blockers else "ready",
            "owner_action": "Refresh evidence and demand gates before deciding whether to build a free asset, Luna pack, or offer experiment.",
            "command": "python3 tools/promotion_evidence_ledger.py && python3 tools/promotion_lead_evidence_checklist.py && python3 tools/promotion_lead_demand_gate.py",
            "evidence_required": "real leads have traceable evidence and explicit consent; repeated guardian demand reaches the threshold before any offer build.",
            "next_gate": "offer_or_asset_queue",
        },
    ]
    if writeback.get("commands"):
        rows.append({
            "step_id": "manual-command-fallback",
            "phase": "fallback",
            "status": "available",
            "owner_action": "If structured text parsing fails, use guardian-specific command examples from lead-writeback-playbook.md after manual validation.",
            "command": "python3 tools/promotion_lead_writeback.py add --source contact --guardian <guardian> --intake-type <type> --consent-status explicit_reply_ok --proof-note \"email thread checked YYYY-MM-DD\"",
            "evidence_required": "manual command still requires explicit consent, safe scope and proof note policy.",
            "next_gate": "lead_evidence_checklist",
        })
    rows.append({
        "step_id": "current-demand-state",
        "phase": "state",
        "status": "hold" if int(demand_metrics.get("readyRoutes", 0) or 0) == 0 else "ready_route_present",
        "owner_action": "Use the demand gate state as the only source for asset or offer priority.",
        "command": "python3 tools/promotion_lead_demand_gate.py --check",
        "evidence_required": f"real_leads={demand_metrics.get('realLeads', 0)}, ready_routes={demand_metrics.get('readyRoutes', 0)}, blockers={','.join(blockers) or 'none'}",
        "next_gate": "master_gate_lead_ready_routes",
    })
    return rows


def build_sheet() -> dict:
    lead_rows = read_csv(LEAD_TRACKER)
    playbook = load_json(LEAD_PLAYBOOK)
    writeback = load_json(LEAD_WRITEBACK)
    evidence = load_json(LEAD_EVIDENCE)
    demand = load_json(LEAD_DEMAND)
    lead_magnet = load_json(LEAD_MAGNET)
    rows = build_rows(playbook, writeback, demand, lead_rows)
    real_rows = real_leads(lead_rows)
    demand_metrics = demand.get("metrics", {}) if isinstance(demand.get("metrics"), dict) else {}
    lead_magnet_assets = lead_magnet.get("assets", []) if isinstance(lead_magnet.get("assets"), list) else []
    lead_magnet_issues = lead_magnet.get("issues", []) if isinstance(lead_magnet.get("issues"), list) else []
    metrics = {
        "rows": len(rows),
        "realLeads": len(real_rows),
        "templateRows": len(lead_rows) - len(real_rows),
        "blockedRows": sum(1 for row in rows if str(row["status"]).startswith("blocked")),
        "waitingRows": sum(1 for row in rows if str(row["status"]).startswith("waiting")),
        "readyRows": sum(1 for row in rows if "ready" in str(row["status"])),
        "readyRoutes": int(demand_metrics.get("readyRoutes", 0) or 0),
        "repeatedRoutes": int(demand_metrics.get("repeatedRoutes", 0) or 0),
        "storyAssets": len(lead_magnet_assets),
        "leadMagnetIssues": len(lead_magnet_issues),
    }
    issues: list[str] = []
    if metrics["templateRows"] < 15:
        issues.append("lead tracker should keep at least 15 guardian intake template rows")
    if metrics["storyAssets"] and metrics["storyAssets"] < 25:
        issues.append("lead magnet inventory should keep five-language guardian story assets")
    if metrics["leadMagnetIssues"] != 0:
        issues.append("lead magnet inventory has issues")
    if not playbook.get("sourceOptions"):
        issues.append("lead intake playbook source options missing")
    if not writeback.get("sources"):
        issues.append("lead writeback playbook sources missing")
    return {
        "generatedAt": today(),
        "sources": {
            "leadTracker": str(LEAD_TRACKER.relative_to(ROOT)),
            "leadIntakePlaybook": str(LEAD_PLAYBOOK.relative_to(ROOT)),
            "leadWritebackPlaybook": str(LEAD_WRITEBACK.relative_to(ROOT)),
            "leadEvidenceChecklist": str(LEAD_EVIDENCE.relative_to(ROOT)),
            "leadDemandGate": str(LEAD_DEMAND.relative_to(ROOT)),
            "leadMagnetInventory": str(LEAD_MAGNET.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Only real emails or copied structured requests may become real lead rows.",
            "Do not store raw reply email in lead-intake-tracker.csv.",
            "A zero, empty or missing KPI signal is not a commercial decision.",
            "Repeated same-guardian demand must appear before building paid or priority assets.",
            "Emergency, diagnosis, counseling replacement or sensitive personal-data requests stay outside the promotion tracker.",
        ],
        "issues": issues,
    }


def render_markdown(sheet: dict) -> str:
    metrics = sheet["metrics"]
    lines = [
        "# LoveTypes Lead Ops Action Sheet",
        "",
        f"- 產生日期：{sheet['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- real leads：{metrics['realLeads']}",
        f"- template rows：{metrics['templateRows']}",
        f"- blocked rows：{metrics['blockedRows']}",
        f"- ready rows：{metrics['readyRows']}",
        f"- ready routes：{metrics['readyRoutes']}",
        f"- issues：{len(sheet['issues'])}",
        "",
        "## Rule",
        "",
    ]
    lines.extend(f"- {rule}" for rule in sheet["rules"])
    lines.extend(["", "## Actions", ""])
    for row in sheet["rows"]:
        lines.extend([
            f"### {row['step_id']}",
            "",
            f"- phase：`{row['phase']}`",
            f"- status：`{row['status']}`",
            f"- action：{row['owner_action']}",
            f"- command：`{row['command']}`",
            f"- evidence：{row['evidence_required']}",
            f"- next gate：`{row['next_gate']}`",
            "",
        ])
    if sheet["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in sheet["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(sheet: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(sheet), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["step_id", "phase", "status", "owner_action", "command", "evidence_required", "next_gate"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sheet["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a daily action sheet for LoveTypes lead intake operations.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    sheet = build_sheet()
    metrics = sheet["metrics"]
    if not args.check:
        write_outputs(sheet)
        print(f"promotion_lead_ops_action_sheet={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_lead_ops_action_sheet_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_lead_ops_action_sheet_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_lead_ops_action_rows={metrics['rows']}")
    print(f"promotion_lead_ops_action_real_leads={metrics['realLeads']}")
    print(f"promotion_lead_ops_action_template_rows={metrics['templateRows']}")
    print(f"promotion_lead_ops_action_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_lead_ops_action_waiting_rows={metrics['waitingRows']}")
    print(f"promotion_lead_ops_action_ready_rows={metrics['readyRows']}")
    print(f"promotion_lead_ops_action_ready_routes={metrics['readyRoutes']}")
    print(f"promotion_lead_ops_action_repeated_routes={metrics['repeatedRoutes']}")
    print(f"promotion_lead_ops_action_story_assets={metrics['storyAssets']}")
    print(f"promotion_lead_ops_action_issues={len(sheet['issues'])}")
    for issue in sheet["issues"]:
        print(issue)
    return 1 if sheet["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
