#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_QUICKSTART = PROMOTION_DIR / "profile-quickstart.json"
PROOF_READINESS = PROMOTION_DIR / "profile-proof-readiness-pack.json"
EVIDENCE_CHECKLIST = PROMOTION_DIR / "profile-evidence-checklist.json"
PROFILE_COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-proof-capture-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-proof-capture-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "profile-proof-capture-quickstart.txt"
REQUIRED_EVIDENCE = (
    "platform_account_visible",
    "profile_link_visible_or_clickable",
    "start_url_resolves",
    "utm_parameters_preserved",
    "quiz_only_copy",
    "proof_note_present",
)


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def metric(payload: dict, key: str, default: int = 0) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return default
    try:
        return int(values.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def grouped_items(checklist: dict) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in checklist.get("items", []) if isinstance(checklist.get("items"), list) else []:
        groups[str(item.get("platform", ""))].append(item)
    for platform in groups:
        groups[platform].sort(key=lambda item: str(item.get("check_id", "")))
    return groups


def by_platform(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("platform", "")): row for row in rows if row.get("platform")}


def build_quickstart() -> dict:
    profile = read_json(PROFILE_QUICKSTART)
    readiness = read_json(PROOF_READINESS)
    checklist = read_json(EVIDENCE_CHECKLIST)
    completion = read_json(PROFILE_COMPLETION)
    profile_by_platform = by_platform(profile.get("platforms", []))
    proof_by_platform = by_platform(readiness.get("rows", []))
    evidence_by_platform = grouped_items(checklist)
    platforms: list[dict] = []

    active_platforms = [str(item.get("platform", "")) for item in profile.get("platforms", []) if item.get("platform")]
    for platform in active_platforms:
        profile_row = profile_by_platform.get(platform, {})
        proof_row = proof_by_platform.get(platform, {})
        items = evidence_by_platform.get(platform, [])
        evidence_steps = [
            {
                "checkId": str(item.get("check_id", "")),
                "requiredEvidence": str(item.get("required_evidence", "")),
                "expectedValue": str(item.get("expected_value", "")),
                "notes": str(item.get("notes", "")),
                "operatorStatus": str(item.get("operator_status", "")),
            }
            for item in items
        ]
        platforms.append({
            "platform": platform,
            "label": str(profile_row.get("label", proof_row.get("label", platform))),
            "currentStatus": str(profile_row.get("currentStatus", "")),
            "actionStatus": str(profile_row.get("actionStatus", "")),
            "profileLinkLocation": str(profile_row.get("profileLinkLocation", "")),
            "profileLink": str(profile_row.get("profileLink", "")),
            "proofFile": str(profile_row.get("proofFile") or proof_row.get("proof_file", "")),
            "proofTemplateImportable": int(str(proof_row.get("proof_template_importable", "0")) == "1"),
            "publicProfileLinkReady": int(str(proof_row.get("public_profile_link_ready", "0")) == "1"),
            "profileConfigured": int(str(proof_row.get("profile_configured", "0")) == "1"),
            "checkCommand": str(profile_row.get("checkCommand") or proof_row.get("check_command", "")),
            "writeCommand": str(profile_row.get("writeCommand") or proof_row.get("write_command", "")),
            "proofBundleCheckCommand": "python3 tools/promotion_profile_batch_import.py --check",
            "postWritebackCheckCommand": "python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_profile_completion_gate.py --check && python3 tools/promotion_master_gate.py --check",
            "stopCondition": str(profile_row.get("stopCondition", "")),
            "captureFileName": f"profile-{platform}-{today()}.png",
            "captureArtifactRequired": 1,
            "safeWritebackReady": int(str(proof_row.get("operator_status", "")) == "ready_to_writeback"),
            "proofNote": "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified",
            "proofNoteRequiredTokens": ["screenshot", "public URL", "clicked", "screen recording", "verified"],
            "evidenceSteps": evidence_steps,
        })

    data = {
        "generatedAt": today(),
        "sources": {
            "profileQuickstart": str(PROFILE_QUICKSTART.relative_to(ROOT)),
            "profileProofReadiness": str(PROOF_READINESS.relative_to(ROOT)),
            "profileEvidenceChecklist": str(EVIDENCE_CHECKLIST.relative_to(ROOT)),
            "profileCompletionGate": str(PROFILE_COMPLETION.relative_to(ROOT)),
        },
        "metrics": {
            "platforms": len(platforms),
            "captureRows": sum(len(platform["evidenceSteps"]) for platform in platforms),
            "pendingEvidenceRows": int(checklist.get("pendingRows", 0) or 0),
            "proofFiles": metric(readiness, "proofFiles"),
            "importableTemplates": metric(readiness, "importableTemplates"),
            "publicReady": metric(readiness, "publicReady"),
            "configured": metric(readiness, "configured"),
            "artifactRequiredRows": len(platforms),
            "safeWritebackRows": sum(int(platform["safeWritebackReady"]) for platform in platforms),
            "writebackBlockedRows": sum(1 for platform in platforms if not int(platform["safeWritebackReady"])),
            "profileGateReady": metric(readiness, "profileGateReady"),
            "completionReadyForFirstBatch": 1 if completion.get("state", {}).get("readyForFirstBatchPublish") else 0,
        },
        "rules": [
            "Capture proof before writeback; importable text is only a format check.",
            "Each active platform keeps six optional evidence checks for operator review.",
            "Use screenshot, clicked public link, screen recording, or platform timestamp as proof.",
            "Keep the proof note tied to platform and date; do not use generic notes like done or checked.",
            "After all active profile writebacks, rerun daily ops refresh, profile completion gate, and launch quickstart.",
        ],
        "platforms": platforms,
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    issues: list[str] = []
    metrics = data["metrics"]
    if metrics["platforms"] < 1:
        issues.append("expected at least one active profile platform")
    if metrics["captureRows"] != metrics["platforms"] * len(REQUIRED_EVIDENCE):
        issues.append(f"expected {metrics['platforms'] * len(REQUIRED_EVIDENCE)} capture evidence rows, got {metrics['captureRows']}")
    if metrics["proofFiles"] != metrics["platforms"] or metrics["importableTemplates"] != metrics["platforms"]:
        issues.append("all active profile proof files must exist and be importable")
    if metrics["profileGateReady"] and metrics["configured"] != metrics["platforms"]:
        issues.append("profile gate cannot be ready before all active profile rows are configured")
    seen = {platform["platform"] for platform in data["platforms"]}
    for platform in data["platforms"]:
        label = platform["platform"]
        link = platform["profileLink"]
        if "/start/" not in link or "utm_campaign=first_round_quiz_completion" not in link:
            issues.append(f"{label}: profile link must use first-round /start/ campaign")
        if not platform["proofFile"].endswith(f"proof-{label}.txt"):
            issues.append(f"{label}: proof file should match platform")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in platform["writeCommand"]:
            issues.append(f"{label}: write command must require real proof replacement")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in platform["proofNote"]:
            issues.append(f"{label}: proof note must be a real evidence placeholder")
        if "screenshot profile-" in platform["proofNote"]:
            issues.append(f"{label}: proof note must not use scaffold screenshot filenames")
        if not platform.get("captureArtifactRequired"):
            issues.append(f"{label}: capture artifact must be required before writeback")
        if "promotion_profile_batch_import.py --check" not in platform.get("proofBundleCheckCommand", ""):
            issues.append(f"{label}: missing profile batch proof check command")
        if platform.get("safeWritebackReady") and "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" in platform["proofNote"]:
            issues.append(f"{label}: safe writeback cannot rely on placeholder proof note")
        if not platform["checkCommand"] or not platform["stopCondition"]:
            issues.append(f"{label}: missing check command or stop condition")
        evidence = {step["requiredEvidence"] for step in platform["evidenceSteps"]}
        missing = set(REQUIRED_EVIDENCE) - evidence
        if missing:
            issues.append(f"{label}: missing evidence steps {sorted(missing)}")
        if len(platform["evidenceSteps"]) != 6:
            issues.append(f"{label}: expected six evidence steps")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Profile Proof Capture Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- platforms：{metrics['platforms']}",
        f"- capture rows：{metrics['captureRows']}",
        f"- pending evidence rows：{metrics['pendingEvidenceRows']}",
        f"- proof files / importable templates：{metrics['proofFiles']} / {metrics['importableTemplates']}",
        f"- public ready / configured：{metrics['publicReady']} / {metrics['configured']}",
        f"- artifact required rows：{metrics['artifactRequiredRows']}",
        f"- safe writeback rows：{metrics['safeWritebackRows']}",
        f"- writeback blocked rows：{metrics['writebackBlockedRows']}",
        f"- profile gate ready：{metrics['profileGateReady']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Capture Steps", ""])
    for platform in data["platforms"]:
        lines.extend([
            f"### {platform['label']} (`{platform['platform']}`)",
            "",
            f"- status：`{platform['actionStatus']}`",
            f"- profile link location：{platform['profileLinkLocation']}",
            f"- profile link：{platform['profileLink']}",
            f"- proof file：`{platform['proofFile']}`",
            f"- suggested capture：`{platform['captureFileName']}`",
            f"- capture artifact required：{platform['captureArtifactRequired']}",
            f"- safe writeback ready：{platform['safeWritebackReady']}",
            f"- proof note：`{platform['proofNote']}`",
            f"- required proof-note tokens：{', '.join(platform['proofNoteRequiredTokens'])}",
            f"- check：`{platform['checkCommand']}`",
            f"- proof bundle check：`{platform['proofBundleCheckCommand']}`",
            f"- write after proof：`{platform['writeCommand']}`",
            f"- post-writeback check：`{platform['postWritebackCheckCommand']}`",
            f"- stop：{platform['stopCondition']}",
            "",
            "Evidence checklist:",
            "",
        ])
        for step in platform["evidenceSteps"]:
            lines.append(f"- [ ] `{step['requiredEvidence']}`：{step['expectedValue']} Notes: {step['notes']}")
        lines.append("")
    if data["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    lines = [
        "LoveTypes profile proof capture quickstart",
        f"generated: {data['generatedAt']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    for platform in data["platforms"]:
        lines.extend([
            "",
            f"=== {platform['label']} / {platform['platform']} ===",
            f"status: {platform['actionStatus']}",
            f"profile link: {platform['profileLink']}",
            f"proof file: {platform['proofFile']}",
            f"suggested capture: {platform['captureFileName']}",
            f"capture artifact required: {platform['captureArtifactRequired']}",
            f"safe writeback ready: {platform['safeWritebackReady']}",
            f"proof note: {platform['proofNote']}",
            f"required proof-note tokens: {', '.join(platform['proofNoteRequiredTokens'])}",
            f"check: {platform['checkCommand']}",
            f"proof bundle check: {platform['proofBundleCheckCommand']}",
            f"write after proof: {platform['writeCommand']}",
            f"post-writeback check: {platform['postWritebackCheckCommand']}",
            f"stop: {platform['stopCondition']}",
            "Evidence:",
        ])
        for step in platform["evidenceSteps"]:
            lines.append(f"- {step['requiredEvidence']}: {step['expectedValue']}")
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a profile proof capture quickstart for LoveTypes launch setup.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_profile_proof_capture_quickstart={args.output}")
        print(f"promotion_profile_proof_capture_quickstart_json={args.json_output}")
        print(f"promotion_profile_proof_capture_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_profile_proof_capture_quickstart_platforms={metrics['platforms']}")
    print(f"promotion_profile_proof_capture_quickstart_capture_rows={metrics['captureRows']}")
    print(f"promotion_profile_proof_capture_quickstart_pending_evidence_rows={metrics['pendingEvidenceRows']}")
    print(f"promotion_profile_proof_capture_quickstart_proof_files={metrics['proofFiles']}")
    print(f"promotion_profile_proof_capture_quickstart_importable_templates={metrics['importableTemplates']}")
    print(f"promotion_profile_proof_capture_quickstart_public_ready={metrics['publicReady']}")
    print(f"promotion_profile_proof_capture_quickstart_configured={metrics['configured']}")
    print(f"promotion_profile_proof_capture_quickstart_artifact_required_rows={metrics['artifactRequiredRows']}")
    print(f"promotion_profile_proof_capture_quickstart_safe_writeback_rows={metrics['safeWritebackRows']}")
    print(f"promotion_profile_proof_capture_quickstart_writeback_blocked_rows={metrics['writebackBlockedRows']}")
    print(f"promotion_profile_proof_capture_quickstart_gate_ready={metrics['profileGateReady']}")
    print(f"promotion_profile_proof_capture_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
