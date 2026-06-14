#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROOF_PACKET = PROMOTION_DIR / "operation-proof-packet.json"
PROOF_TEMPLATES = PROMOTION_DIR / "operation-proof-templates.json"
PROOF_REHEARSAL = PROMOTION_DIR / "proof-rehearsal.json"
PROFILE_EVIDENCE = PROMOTION_DIR / "profile-evidence-checklist.json"
LAUNCH_REHEARSAL = PROMOTION_DIR / "launch-rehearsal-packet.json"
OPERATOR_HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "proof-import-closure-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "proof-import-closure-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "import-proof-closure-quickstart.txt"
EXPECTED_PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
PROFILE_EVIDENCE_CHECKS = 6
PROOF_IMPORTS = ("profile_setup_import", "post_publish_import", "lead_request_import")


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


def state_int(payload: dict, key: str) -> int:
    state = payload.get("state", {})
    if not isinstance(state, dict):
        return 0
    try:
        return int(state.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def rows(payload: dict, key: str = "rows") -> list[dict]:
    value = payload.get(key, [])
    return value if isinstance(value, list) else []


def structured_imports(payload: dict) -> list[dict]:
    value = payload.get("structuredImports", [])
    return value if isinstance(value, list) else []


def profile_template_rows(templates: dict) -> list[dict]:
    return [row for row in rows(templates) if row.get("kind") == "profile_setup"]


def post_template_rows(templates: dict) -> list[dict]:
    return [row for row in rows(templates) if row.get("kind") == "post_publish"]


def closure_steps(metrics: dict) -> list[dict[str, str]]:
    profile_ready = metrics["profileValid"] == len(EXPECTED_PLATFORMS)
    post_guard_ready = metrics["postSafelyRejected"] == len(EXPECTED_PLATFORMS)
    rehearsal_ready = (
        metrics["rehearsalProfilePass"] == len(EXPECTED_PLATFORMS)
        and metrics["rehearsalPostPlaceholderRejected"] == len(EXPECTED_PLATFORMS)
        and metrics["rehearsalPostRealUrlPass"] == len(EXPECTED_PLATFORMS)
    )
    return [
        {
            "id": "validate_profile_proof_templates",
            "status": "ready_to_use" if profile_ready else "blocked",
            "command": "python3 tools/promotion_operation_proof_templates.py --check && python3 tools/promotion_profile_evidence_checklist.py --check",
            "release": "Three profile proof templates validate and each platform has six evidence checks.",
            "stop": "Do not write profile status unless all six evidence checks are backed by real platform proof.",
        },
        {
            "id": "reject_post_placeholders",
            "status": "guard_active" if post_guard_ready else "blocked",
            "command": "python3 tools/promotion_operation_proof_templates.py --check",
            "release": "Three post proof templates are safely rejected while their post URLs are placeholders.",
            "stop": "Do not weaken this guard; placeholder post URLs must never write to trackers.",
        },
        {
            "id": "rehearse_import_paths",
            "status": "complete" if rehearsal_ready else "blocked",
            "command": "python3 tools/promotion_proof_rehearsal.py --check && python3 tools/promotion_operator_import_template_audit.py",
            "release": "Profile import passes, placeholder post import fails, sample real post URLs pass, and operator import templates enforce safe rejection.",
            "stop": "Do not run add/writeback commands until the check path behaves as expected.",
        },
        {
            "id": "writeback_after_external_proof",
            "status": "blocked_until_external_proof",
            "command": "python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-<platform>.txt --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\"",
            "release": "A real platform screenshot/click proof exists and the profile proof text passed check.",
            "stop": "Do not write back from rehearsal data, templates, private previews, or memory.",
        },
        {
            "id": "open_publish_only_after_profile_gate",
            "status": "blocked_until_profile_writeback",
            "command": "python3 tools/promotion_launch_rehearsal_packet.py --check && python3 tools/promotion_profile_publish_handoff.py --check",
            "release": "Profile writeback is complete and first-batch publishing is explicitly open.",
            "stop": "Do not publish or backfill KPI while launch rehearsal says publish is blocked.",
        },
    ]


def build_quickstart() -> dict:
    proof_packet = read_json(PROOF_PACKET)
    templates = read_json(PROOF_TEMPLATES)
    rehearsal = read_json(PROOF_REHEARSAL)
    evidence = read_json(PROFILE_EVIDENCE)
    launch_rehearsal = read_json(LAUNCH_REHEARSAL)
    handoff = read_json(OPERATOR_HANDOFF)
    profile_rows = profile_template_rows(templates)
    post_rows = post_template_rows(templates)
    imports = structured_imports(handoff)
    import_ids = sorted(str(item.get("id", "")) for item in imports if item.get("id"))
    metrics = {
        "proofPacketProfilePending": state_int(proof_packet, "profilePending"),
        "proofPacketPostPending": state_int(proof_packet, "firstBatchPending"),
        "profileTemplates": len(profile_rows),
        "postTemplates": len(post_rows),
        "proofFiles": metric(templates, "files"),
        "profileValid": metric(templates, "profileValid"),
        "postSafelyRejected": metric(templates, "postSafelyRejected"),
        "rehearsalRows": metric(rehearsal, "rows"),
        "rehearsalProfilePass": metric(rehearsal, "profilePass"),
        "rehearsalPostPlaceholderRejected": metric(rehearsal, "postPlaceholderRejected"),
        "rehearsalPostRealUrlPass": metric(rehearsal, "postRehearsalPass"),
        "profileEvidencePlatforms": int(evidence.get("platforms", 0) or 0),
        "profileEvidenceRows": int(evidence.get("rows", 0) or 0),
        "profileEvidencePendingRows": int(evidence.get("pendingRows", 0) or 0),
        "structuredImports": len(imports),
        "expectedStructuredImports": len(PROOF_IMPORTS),
        "launchRehearsalReadyStages": int(launch_rehearsal.get("readyStages", 0) or 0),
        "launchRehearsalProfileReadyStages": int(launch_rehearsal.get("profileReadyStages", 0) or 0),
        "launchRehearsalPublishReadyStages": int(launch_rehearsal.get("publishReadyStages", 0) or 0),
        "launchRehearsalKpiReadyStages": int(launch_rehearsal.get("kpiReadyStages", 0) or 0),
        "launchRehearsalWeeklyReadyStages": int(launch_rehearsal.get("weeklyReadyStages", 0) or 0),
        "launchRehearsalBlockedStages": int(launch_rehearsal.get("blockedStages", 0) or 0),
        "launchReadyToPublish": 1 if launch_rehearsal.get("state", {}).get("readyToPublish") else 0,
        "launchEmptyDataMode": 1 if launch_rehearsal.get("state", {}).get("emptyDataMode") else 0,
    }
    proof_rows = []
    for row in [*profile_rows, *post_rows]:
        proof_rows.append({
            "kind": str(row.get("kind", "")),
            "platform": str(row.get("platform", "")),
            "taskId": str(row.get("taskId", "")),
            "path": str(row.get("path", "")),
            "status": str(row.get("status", "")),
            "checkCommand": str(row.get("checkCommand", "")),
            "writeCommand": str(row.get("writeCommand", "")),
            "requiredEvidenceCount": len(row.get("requiredEvidence", [])) if isinstance(row.get("requiredEvidence"), list) else 0,
        })
    data = {
        "generatedAt": today(),
        "sources": {
            "operationProofPacket": str(PROOF_PACKET.relative_to(ROOT)),
            "operationProofTemplates": str(PROOF_TEMPLATES.relative_to(ROOT)),
            "proofRehearsal": str(PROOF_REHEARSAL.relative_to(ROOT)),
            "profileEvidenceChecklist": str(PROFILE_EVIDENCE.relative_to(ROOT)),
            "launchRehearsalPacket": str(LAUNCH_REHEARSAL.relative_to(ROOT)),
            "operatorHandoffPacket": str(OPERATOR_HANDOFF.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rules": [
            "Check commands must pass before any add/writeback command is allowed.",
            "Profile proof templates may pass structurally, but still require real external evidence before writeback.",
            "Post proof templates must fail while placeholder URLs remain in place.",
            "A zero KPI is valid only after a real analytics source check.",
            "Rehearsal data, sample URLs, and templates are never production evidence.",
        ],
        "steps": closure_steps(metrics),
        "proofRows": proof_rows,
        "structuredImportIds": import_ids,
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    metrics = data["metrics"]
    issues: list[str] = []
    if metrics["profileTemplates"] != len(EXPECTED_PLATFORMS):
        issues.append("expected three profile proof templates")
    if metrics["postTemplates"] != len(EXPECTED_PLATFORMS):
        issues.append("expected three post proof templates")
    if metrics["profileValid"] != len(EXPECTED_PLATFORMS):
        issues.append("profile proof templates should all validate")
    if metrics["postSafelyRejected"] != len(EXPECTED_PLATFORMS):
        issues.append("post proof templates should all be safely rejected while placeholder URLs remain")
    if metrics["rehearsalProfilePass"] != len(EXPECTED_PLATFORMS):
        issues.append("proof rehearsal should pass all profile imports")
    if metrics["rehearsalPostPlaceholderRejected"] != len(EXPECTED_PLATFORMS):
        issues.append("proof rehearsal should reject all placeholder post imports")
    if metrics["rehearsalPostRealUrlPass"] != len(EXPECTED_PLATFORMS):
        issues.append("proof rehearsal should pass sample real post URL imports")
    if metrics["profileEvidencePlatforms"] != len(EXPECTED_PLATFORMS):
        issues.append("profile evidence checklist should cover three platforms")
    expected_evidence_rows = len(EXPECTED_PLATFORMS) * PROFILE_EVIDENCE_CHECKS
    if metrics["profileEvidenceRows"] != expected_evidence_rows:
        issues.append(f"profile evidence checklist should expose {expected_evidence_rows} rows")
    if set(data["structuredImportIds"]) != set(PROOF_IMPORTS):
        issues.append("operator handoff should expose profile, post, and lead structured import templates")
    if metrics["launchReadyToPublish"] and metrics["proofPacketProfilePending"]:
        issues.append("launch rehearsal cannot be ready to publish while profile proof rows are pending")
    if not metrics["launchReadyToPublish"] and metrics["launchRehearsalPublishReadyStages"]:
        issues.append("publish rehearsal stages should stay at zero until launch is ready to publish")
    for row in data["proofRows"]:
        label = f"{row.get('kind', '<kind>')}/{row.get('platform', '<platform>')}/{row.get('taskId', '')}"
        if not row.get("path") or not row.get("checkCommand"):
            issues.append(f"{label}: missing proof path or check command")
        if "--proof-note" not in str(row.get("writeCommand", "")):
            issues.append(f"{label}: write command must require proof note")
        if row.get("kind") == "profile_setup" and row.get("requiredEvidenceCount") != PROFILE_EVIDENCE_CHECKS:
            issues.append(f"{label}: profile proof row should require six evidence checks")
        if row.get("kind") == "post_publish" and int(row.get("requiredEvidenceCount", 0) or 0) < 7:
            issues.append(f"{label}: post proof row should require public URL, CTA, UTM, and safety evidence")
    for step in data["steps"]:
        if not step.get("command") or not step.get("stop"):
            issues.append(f"{step.get('id', '<step>')}: missing command or stop condition")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Proof Import Closure Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- profile templates：{metrics['profileTemplates']}",
        f"- post templates：{metrics['postTemplates']}",
        f"- profile valid：{metrics['profileValid']}",
        f"- post safely rejected：{metrics['postSafelyRejected']}",
        f"- rehearsal rows：{metrics['rehearsalRows']}",
        f"- rehearsal profile pass：{metrics['rehearsalProfilePass']}",
        f"- rehearsal post placeholder rejected：{metrics['rehearsalPostPlaceholderRejected']}",
        f"- rehearsal post real URL pass：{metrics['rehearsalPostRealUrlPass']}",
        f"- profile evidence rows：{metrics['profileEvidenceRows']}",
        f"- profile evidence pending：{metrics['profileEvidencePendingRows']}",
        f"- structured imports：{metrics['structuredImports']} / {metrics['expectedStructuredImports']}",
        f"- launch ready to publish：{metrics['launchReadyToPublish']}",
        f"- empty data mode：{metrics['launchEmptyDataMode']}",
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
    lines.extend(["## Proof Rows", ""])
    for row in data["proofRows"]:
        lines.extend([
            f"### {row['kind']} · {row['platform']} {row['taskId']}".rstrip(),
            "",
            f"- file：`{row['path']}`",
            f"- status：`{row['status']}`",
            f"- evidence count：{row['requiredEvidenceCount']}",
            f"- check：`{row['checkCommand']}`",
            f"- write：`{row['writeCommand']}`",
            "",
        ])
    lines.extend(["## Structured Imports", ""])
    lines.extend(f"- `{item}`" for item in data["structuredImportIds"])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes proof import closure quickstart",
        f"generated: {data['generatedAt']}",
        f"profile valid: {metrics['profileValid']}",
        f"post safely rejected: {metrics['postSafelyRejected']}",
        f"rehearsal rows: {metrics['rehearsalRows']}",
        f"profile evidence rows: {metrics['profileEvidenceRows']}",
        f"launch ready to publish: {metrics['launchReadyToPublish']}",
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
    for row in data["proofRows"]:
        lines.extend([
            "",
            f"{row['kind']} / {row['platform']} / {row['taskId']}",
            f"file: {row['path']}",
            f"check: {row['checkCommand']}",
            f"write: {row['writeCommand']}",
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
    parser = argparse.ArgumentParser(description="Build the proof import closure quickstart for LoveTypes promotion operations.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_proof_import_closure_quickstart={args.output}")
        print(f"promotion_proof_import_closure_quickstart_json={args.json_output}")
        print(f"promotion_proof_import_closure_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_proof_import_closure_quickstart_profile_templates={metrics['profileTemplates']}")
    print(f"promotion_proof_import_closure_quickstart_post_templates={metrics['postTemplates']}")
    print(f"promotion_proof_import_closure_quickstart_profile_valid={metrics['profileValid']}")
    print(f"promotion_proof_import_closure_quickstart_post_rejected={metrics['postSafelyRejected']}")
    print(f"promotion_proof_import_closure_quickstart_rehearsal_rows={metrics['rehearsalRows']}")
    print(f"promotion_proof_import_closure_quickstart_profile_rehearsal_pass={metrics['rehearsalProfilePass']}")
    print(f"promotion_proof_import_closure_quickstart_post_placeholder_rejected={metrics['rehearsalPostPlaceholderRejected']}")
    print(f"promotion_proof_import_closure_quickstart_post_real_url_pass={metrics['rehearsalPostRealUrlPass']}")
    print(f"promotion_proof_import_closure_quickstart_profile_evidence_rows={metrics['profileEvidenceRows']}")
    print(f"promotion_proof_import_closure_quickstart_profile_evidence_pending={metrics['profileEvidencePendingRows']}")
    print(f"promotion_proof_import_closure_quickstart_structured_imports={metrics['structuredImports']}")
    print(f"promotion_proof_import_closure_quickstart_launch_ready_to_publish={metrics['launchReadyToPublish']}")
    print(f"promotion_proof_import_closure_quickstart_empty_data={metrics['launchEmptyDataMode']}")
    print(f"promotion_proof_import_closure_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
