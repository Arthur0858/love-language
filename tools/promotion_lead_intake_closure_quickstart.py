#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LEAD_INTAKE = PROMOTION_DIR / "lead-intake-playbook.json"
LEAD_WRITEBACK = PROMOTION_DIR / "lead-writeback-playbook.json"
LEAD_EVIDENCE = PROMOTION_DIR / "lead-evidence-checklist.json"
LEAD_OPS = PROMOTION_DIR / "lead-ops-action-sheet.json"
LEAD_PROOF = PROMOTION_DIR / "lead-request-proof-packet.json"
LEAD_SUMMARY = PROMOTION_DIR / "lead-tracker-summary.json"
LEAD_DEMAND = PROMOTION_DIR / "lead-demand-gate.json"
LEAD_OFFER = PROMOTION_DIR / "lead-offer-quickstart.json"
HANDOFF = PROMOTION_DIR / "weekly-lead-offer-handoff.json"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "lead-intake-closure-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "lead-intake-closure-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "lead-intake-closure-quickstart.txt"
GUARDIAN_ORDER = ("iris", "noah", "vivian", "claire", "dora")
INTAKE_TYPES = ("owned_asset_request", "luna_scene_request", "repair_or_contact_request")
REQUIRED_EVIDENCE = (
    "source_traceable",
    "guardian_route_present",
    "intake_type_present",
    "asset_preference_present",
    "reply_email_available",
    "explicit_consent",
    "attribution_or_manual_rule",
    "safe_scope_verified",
    "proof_note_traceable",
)


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def metric(payload: dict, key: str) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return 0
    try:
        return int(values.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def guardian_commands(writeback: dict) -> dict[str, dict]:
    commands = writeback.get("commands", [])
    if not isinstance(commands, list):
        return {}
    return {str(row.get("guardian", "")): row for row in commands if isinstance(row, dict)}


def tracker_templates(intake: dict) -> list[dict]:
    rows = intake.get("trackerRows", [])
    return rows if isinstance(rows, list) else []


def evidence_checks(evidence: dict) -> dict[str, list[dict]]:
    rows = evidence.get("rows", [])
    grouped: dict[str, list[dict]] = {}
    if not isinstance(rows, list):
        return grouped
    for row in rows:
        if not isinstance(row, dict):
            continue
        request_id = str(row.get("request_id", ""))
        grouped.setdefault(request_id, []).append(row)
    return grouped


def closure_steps(metrics: dict) -> list[dict[str, str]]:
    has_real_lead = metrics["realLeads"] > 0
    evidence_ready = has_real_lead and metrics["evidenceMissingRows"] == 0 and metrics["evidenceOperatorVerifyRows"] == 0
    demand_ready = metrics["readyRoutes"] > 0
    return [
        {
            "id": "capture_structured_request",
            "status": "ready_to_receive",
            "command": "python3 tools/promotion_lead_form_audit.py && python3 tools/promotion_lead_form_importability_audit.py",
            "release": "Contact / keepsake / Luna request text is structured and importable.",
            "stop": "Do not store raw email content in CSV; copy only the structured request fields and proof note.",
        },
        {
            "id": "verify_consent_and_scope",
            "status": "blocked_until_real_request" if not has_real_lead else "operator_verify",
            "command": "python3 tools/promotion_lead_evidence_checklist.py --check",
            "release": "The request has explicit_reply_ok consent, reply email verified outside CSV, and safe non-emergency scope.",
            "stop": "Do not use emergency, diagnostic, therapy-replacement, or sensitive-detail requests for marketing decisions.",
        },
        {
            "id": "writeback_real_lead",
            "status": "blocked_until_verified_request" if not has_real_lead else "ready_to_validate",
            "command": "python3 tools/promotion_lead_text_import.py add --input <REAL_STRUCTURED_REQUEST.txt> --proof-note \"email thread checked YYYY-MM-DD\"",
            "release": "A real non-template lead row exists with traceable proof and no raw email stored.",
            "stop": "Do not create fake leads, inferred consent, or placeholder request rows.",
        },
        {
            "id": "refresh_lead_demand",
            "status": "blocked_until_real_lead" if not has_real_lead else "ready_to_refresh",
            "command": "python3 tools/promotion_daily_ops_refresh.py",
            "release": "Lead summary, evidence checklist, demand gate, handoff, and offer quickstart reflect the real request.",
            "stop": "Do not make lead or offer decisions from stale generated files.",
        },
        {
            "id": "open_asset_or_offer_route",
            "status": "complete" if demand_ready else "blocked_until_repeated_demand",
            "command": "python3 tools/promotion_lead_demand_gate.py --check && python3 tools/promotion_lead_offer_quickstart.py --check",
            "release": "Same guardian / intake has repeated demand and a matching ready route.",
            "stop": "Do not build paid, Luna, or affiliate experiments from one request or empty data.",
        },
    ]


def build_quickstart() -> dict:
    intake = read_json(LEAD_INTAKE)
    writeback = read_json(LEAD_WRITEBACK)
    evidence = read_json(LEAD_EVIDENCE)
    lead_ops = read_json(LEAD_OPS)
    lead_proof = read_json(LEAD_PROOF)
    lead_summary = read_json(LEAD_SUMMARY)
    lead_demand = read_json(LEAD_DEMAND)
    lead_offer = read_json(LEAD_OFFER)
    handoff = read_json(HANDOFF)
    master = read_json(MASTER_GATE)

    templates = tracker_templates(intake)
    commands = guardian_commands(writeback)
    grouped_checks = evidence_checks(evidence)
    rows: list[dict] = []
    for guardian in GUARDIAN_ORDER:
        guardian_templates = [row for row in templates if row.get("guardian_id") == guardian]
        command = commands.get(guardian, {})
        rows.append({
            "guardianId": guardian,
            "guardianName": str(command.get("guardianName") or (guardian_templates[0].get("guardian_name") if guardian_templates else guardian)),
            "templateRows": len(guardian_templates),
            "intakeTypes": [str(row.get("intake_type", "")) for row in guardian_templates],
            "ownedAssetCommand": str(command.get("ownedAssetCommand", "")),
            "lunaCommand": str(command.get("lunaCommand", "")),
            "relatedRoutes": sorted({str(row.get("related_route", "")) for row in guardian_templates if row.get("related_route")}),
            "evidenceCheckCounts": {
                str(row.get("request_id", "")): len(grouped_checks.get(str(row.get("request_id", "")), []))
                for row in guardian_templates
            },
        })

    metrics = {
        "templateRows": metric(writeback, "templateRows"),
        "realLeads": metric(writeback, "realRows"),
        "leadEvidenceRows": metric(evidence, "checklistRows"),
        "evidencePendingTemplateRows": metric(evidence, "pendingTemplateRows"),
        "evidenceOperatorVerifyRows": metric(evidence, "realOperatorVerifyRows"),
        "evidenceMissingRows": metric(evidence, "missingRows"),
        "proofTemplates": metric(lead_proof, "rows"),
        "proofSafeRejected": metric(lead_proof, "safeRejected"),
        "leadOpsReadyRows": metric(lead_ops, "readyRows"),
        "leadOpsBlockedRows": metric(lead_ops, "blockedRows"),
        "summaryRealRows": metric(lead_summary, "realRows"),
        "summaryExplicitConsentRows": metric(lead_summary, "explicitConsentRows"),
        "readyRoutes": metric(lead_demand, "readyRoutes"),
        "repeatedRoutes": metric(lead_demand, "repeatedDemandRoutes"),
        "demandBlockers": metric(lead_demand, "blockers"),
        "handoffCurrentBlockers": metric(handoff, "currentBlockers"),
        "handoffBlockedUpstreamRows": metric(handoff, "blockedUpstreamRows"),
        "publicFreeAssets": metric(lead_offer, "publicFreeAssets"),
        "offerQueueReady": metric(lead_offer, "offerQueueReady"),
        "masterStage": str(master.get("stage", "")),
        "masterLeadReadyRoutes": metric(master, "leadReadyRoutes"),
    }
    steps = closure_steps(metrics)
    issues = validate(rows, metrics, steps)
    metrics["issues"] = len(issues)
    return {
        "generatedAt": today(),
        "sources": {
            "leadIntakePlaybook": str(LEAD_INTAKE.relative_to(ROOT)),
            "leadWritebackPlaybook": str(LEAD_WRITEBACK.relative_to(ROOT)),
            "leadEvidenceChecklist": str(LEAD_EVIDENCE.relative_to(ROOT)),
            "leadOpsActionSheet": str(LEAD_OPS.relative_to(ROOT)),
            "leadRequestProofPacket": str(LEAD_PROOF.relative_to(ROOT)),
            "leadTrackerSummary": str(LEAD_SUMMARY.relative_to(ROOT)),
            "leadDemandGate": str(LEAD_DEMAND.relative_to(ROOT)),
            "leadOfferQuickstart": str(LEAD_OFFER.relative_to(ROOT)),
            "weeklyLeadOfferHandoff": str(HANDOFF.relative_to(ROOT)),
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rules": [
            "Template rows are readiness scaffolds, not real leads.",
            "A real lead requires explicit_reply_ok consent, a traceable proof note, and safe non-emergency scope.",
            "Raw email addresses or message bodies must not be stored in tracker CSV files.",
            "Matched UTM can increment KPI; unmatched UTM remains qualitative manual lead only.",
            "Owned assets, Luna packs, or offer experiments open only after repeated same-guardian demand.",
        ],
        "steps": steps,
        "rows": rows,
        "issues": issues,
    }


def validate(rows: list[dict], metrics: dict, steps: list[dict]) -> list[str]:
    issues: list[str] = []
    if len(rows) != len(GUARDIAN_ORDER):
        issues.append(f"expected {len(GUARDIAN_ORDER)} guardian rows, got {len(rows)}")
    if metrics["templateRows"] != len(GUARDIAN_ORDER) * len(INTAKE_TYPES):
        issues.append("lead intake closure must expose 15 template rows")
    if metrics["realLeads"] != metrics["summaryRealRows"]:
        issues.append("lead writeback real rows and summary real rows disagree")
    if metrics["realLeads"] == 0 and metrics["readyRoutes"] != 0:
        issues.append("ready routes must stay zero without real leads")
    if metrics["realLeads"] == 0 and metrics["offerQueueReady"] != 0:
        issues.append("offer queue must stay closed without real leads")
    if metrics["realLeads"] == 0 and metrics["evidenceMissingRows"] != 0:
        issues.append("template-only evidence should not create missing real-lead rows")
    if metrics["proofTemplates"] != len(GUARDIAN_ORDER) * len(INTAKE_TYPES):
        issues.append("lead proof packet must expose one proof template per guardian/intake pair")
    if metrics["publicFreeAssets"] < len(GUARDIAN_ORDER):
        issues.append("five public free assets should remain available as lead magnets")
    step_ids = {step.get("id") for step in steps}
    required_steps = {
        "capture_structured_request",
        "verify_consent_and_scope",
        "writeback_real_lead",
        "refresh_lead_demand",
        "open_asset_or_offer_route",
    }
    if step_ids != required_steps:
        issues.append("lead closure steps must include capture, consent, writeback, refresh, and demand gate")
    for row in rows:
        label = row.get("guardianId", "<guardian>")
        intake_types = set(row.get("intakeTypes", []))
        if intake_types != set(INTAKE_TYPES):
            issues.append(f"{label}: expected owned asset, Luna scene, and repair/contact templates")
        if not row.get("ownedAssetCommand") or not row.get("lunaCommand"):
            issues.append(f"{label}: missing lead writeback command examples")
        for request_id, count in row.get("evidenceCheckCounts", {}).items():
            if count != len(REQUIRED_EVIDENCE):
                issues.append(f"{request_id}: expected {len(REQUIRED_EVIDENCE)} evidence checks, got {count}")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Lead Intake Closure Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- template rows：{metrics['templateRows']}",
        f"- real leads：{metrics['realLeads']}",
        f"- lead evidence rows：{metrics['leadEvidenceRows']}",
        f"- pending template evidence rows：{metrics['evidencePendingTemplateRows']}",
        f"- evidence missing rows：{metrics['evidenceMissingRows']}",
        f"- proof templates：{metrics['proofTemplates']}",
        f"- lead ops ready / blocked：{metrics['leadOpsReadyRows']} / {metrics['leadOpsBlockedRows']}",
        f"- repeated routes / ready routes：{metrics['repeatedRoutes']} / {metrics['readyRoutes']}",
        f"- public free assets：{metrics['publicFreeAssets']}",
        f"- offer queue ready：{metrics['offerQueueReady']}",
        f"- master stage：`{metrics['masterStage']}`",
        f"- master lead ready routes：{metrics['masterLeadReadyRoutes']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Closure Steps", ""])
    for step in data["steps"]:
        lines.extend([
            f"### `{step['id']}`",
            "",
            f"- status：`{step['status']}`",
            f"- command：`{step['command']}`",
            f"- release：{step['release']}",
            f"- stop：{step['stop']}",
            "",
        ])
    lines.extend(["## Guardian Intake Rows", ""])
    for row in data["rows"]:
        lines.extend([
            f"### {row['guardianName']} · `{row['guardianId']}`",
            "",
            f"- template rows：{row['templateRows']}",
            f"- intake types：`{', '.join(row['intakeTypes'])}`",
            f"- routes：{', '.join(row['relatedRoutes'])}",
            "",
            "Writeback commands after a real verified request:",
            "",
            "```text",
            row["ownedAssetCommand"],
            row["lunaCommand"],
            "```",
            "",
            "Evidence checks per template:",
            "",
        ])
        for request_id, count in row["evidenceCheckCounts"].items():
            lines.append(f"- `{request_id}`：{count} checks")
        lines.append("")
    if data["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes lead intake closure quickstart",
        f"generated: {data['generatedAt']}",
        f"template rows: {metrics['templateRows']}",
        f"real leads: {metrics['realLeads']}",
        f"ready routes: {metrics['readyRoutes']}",
        f"offer queue ready: {metrics['offerQueueReady']}",
        "",
        "Closure steps:",
    ]
    for step in data["steps"]:
        lines.extend([
            "",
            f"{step['id']}: {step['status']}",
            f"command: {step['command']}",
            f"release: {step['release']}",
            f"stop: {step['stop']}",
        ])
    for row in data["rows"]:
        lines.extend([
            "",
            f"=== {row['guardianId']} ===",
            f"template rows: {row['templateRows']}",
            f"intake types: {', '.join(row['intakeTypes'])}",
            "commands:",
            row["ownedAssetCommand"],
            row["lunaCommand"],
        ])
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the lead intake closure quickstart for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_lead_intake_closure_quickstart={args.output}")
        print(f"promotion_lead_intake_closure_quickstart_json={args.json_output}")
        print(f"promotion_lead_intake_closure_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_lead_intake_closure_quickstart_template_rows={metrics['templateRows']}")
    print(f"promotion_lead_intake_closure_quickstart_real_leads={metrics['realLeads']}")
    print(f"promotion_lead_intake_closure_quickstart_evidence_rows={metrics['leadEvidenceRows']}")
    print(f"promotion_lead_intake_closure_quickstart_evidence_missing_rows={metrics['evidenceMissingRows']}")
    print(f"promotion_lead_intake_closure_quickstart_proof_templates={metrics['proofTemplates']}")
    print(f"promotion_lead_intake_closure_quickstart_lead_ops_ready_rows={metrics['leadOpsReadyRows']}")
    print(f"promotion_lead_intake_closure_quickstart_repeated_routes={metrics['repeatedRoutes']}")
    print(f"promotion_lead_intake_closure_quickstart_ready_routes={metrics['readyRoutes']}")
    print(f"promotion_lead_intake_closure_quickstart_public_free_assets={metrics['publicFreeAssets']}")
    print(f"promotion_lead_intake_closure_quickstart_offer_queue_ready={metrics['offerQueueReady']}")
    print(f"promotion_lead_intake_closure_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
