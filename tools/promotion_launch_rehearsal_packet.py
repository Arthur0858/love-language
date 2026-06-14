#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
COMMAND_CENTER_PATH = PROMOTION_DIR / "launch-command-center.json"
OPERATION_PROOF_PATH = PROMOTION_DIR / "operation-proof-packet.json"
HANDOFF_PATH = PROMOTION_DIR / "operator-handoff-packet.json"
READINESS_PATH = PROMOTION_DIR / "launch-readiness-gate.json"
WEEKLY_REVIEW_PATH = PROMOTION_DIR / "weekly-review-packet.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "launch-rehearsal-packet.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "launch-rehearsal-packet.json"

STAGE_ORDER = (
    "profile_evidence",
    "profile_writeback",
    "readiness_gate",
    "publish_post",
    "minimum_kpi_backfill",
    "weekly_review",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def command_rows_by_phase(command_center: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in command_center.get("rows", []):
        grouped.setdefault(str(row.get("phase", "")), []).append(row)
    return grouped


def build_rehearsal() -> dict[str, object]:
    command_center = load_json(COMMAND_CENTER_PATH)
    operation_proof = load_json(OPERATION_PROOF_PATH)
    handoff = load_json(HANDOFF_PATH)
    readiness = load_json(READINESS_PATH)
    weekly_review = load_json(WEEKLY_REVIEW_PATH)
    readiness_metrics = readiness.get("metrics", {})
    proof_rows = operation_proof.get("proofs", [])
    profile_proofs = [row for row in proof_rows if row.get("kind") == "profile_setup"]
    post_proofs = [row for row in proof_rows if row.get("kind") == "post_publish"]
    command_by_phase = command_rows_by_phase(command_center)
    weekly_rows = weekly_review.get("rowsToUpdate", [])
    profile_configured = int(readiness_metrics.get("profileConfigured", 0) or 0)
    ready_to_publish = bool(readiness.get("readiness", {}).get("readyToPublishPosts"))
    published_rows = int(readiness_metrics.get("publishedRows", 0) or 0)
    filled_kpi_rows = int(readiness_metrics.get("filledKpiRows", 0) or 0)

    stages: list[dict[str, object]] = []
    for proof in profile_proofs:
        platform = proof.get("platform", "")
        stages.append({
            "stage": "profile_evidence",
            "status": "ready",
            "platform": platform,
            "taskId": f"profile-{platform}",
            "requiredInput": proof.get("template", ""),
            "checkCommand": proof.get("checkCommand", ""),
            "blockedBy": "",
            "successSignal": "profile proof text validates before writeback",
        })
    for proof in profile_proofs:
        platform = proof.get("platform", "")
        stages.append({
            "stage": "profile_writeback",
            "status": "ready",
            "platform": platform,
            "taskId": f"profile-{platform}",
            "writeCommand": proof.get("writeCommand", ""),
            "blockedBy": "profile_evidence" if not proof.get("template") else "",
            "successSignal": "platform profile tracker row becomes set/live with proof_note",
        })
    stages.append({
        "stage": "readiness_gate",
        "status": "ready" if profile_configured == len(profile_proofs) and ready_to_publish else "blocked_until_profiles_configured",
        "platform": "all",
        "taskId": "launch-readiness",
        "checkCommand": "python3 tools/promotion_launch_readiness_gate.py",
        "blockedBy": "" if profile_configured == len(profile_proofs) and ready_to_publish else "profile_writeback",
        "successSignal": "promotion_launch_readiness_ready_to_publish=1",
    })
    for proof in post_proofs:
        stages.append({
            "stage": "publish_post",
            "status": "ready" if ready_to_publish else "blocked_until_readiness_gate",
            "platform": proof.get("platform", ""),
            "taskId": proof.get("taskId", ""),
            "checkCommand": proof.get("checkCommand", ""),
            "writeCommand": proof.get("writeCommand", ""),
            "blockedBy": "" if ready_to_publish else "readiness_gate",
            "successSignal": "post_url and starter metrics validate before writeback",
        })
    for row in weekly_rows:
        stages.append({
            "stage": "minimum_kpi_backfill",
            "status": "ready" if row.get("postUrl") else "blocked_until_post_url",
            "platform": row.get("platform", ""),
            "taskId": row.get("taskId", ""),
            "requiredFields": row.get("minimumFields", []),
            "writebackCommand": row.get("writebackCommand", ""),
            "blockedBy": "" if row.get("postUrl") else "publish_post",
            "successSignal": "platform row has post_url, site_clicks, quiz_starts, quiz_completions",
        })
    stages.append({
        "stage": "weekly_review",
        "status": "ready" if published_rows >= len(post_proofs) and filled_kpi_rows >= len(post_proofs) else "blocked_until_minimum_kpi",
        "platform": "all",
        "taskId": "weekly-review",
        "checkCommand": "python3 tools/promotion_weekly_review_packet.py --check",
        "blockedBy": "" if weekly_review.get("state", {}).get("readyForWeeklyDecision") else "minimum_kpi_backfill",
        "successSignal": "weeklyReviewReady becomes true before offer or revenue decisions",
    })
    profile_ready_stages = sum(
        1
        for stage in stages
        if stage.get("stage") in {"profile_evidence", "profile_writeback"} and stage.get("status") == "ready"
    )
    publish_ready_stages = sum(1 for stage in stages if stage.get("stage") == "publish_post" and stage.get("status") == "ready")
    kpi_ready_stages = sum(
        1 for stage in stages if stage.get("stage") == "minimum_kpi_backfill" and stage.get("status") == "ready"
    )
    weekly_ready_stages = sum(1 for stage in stages if stage.get("stage") == "weekly_review" and stage.get("status") == "ready")

    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "launchCommandCenter": str(COMMAND_CENTER_PATH.relative_to(ROOT)),
            "operationProofPacket": str(OPERATION_PROOF_PATH.relative_to(ROOT)),
            "operatorHandoffPacket": str(HANDOFF_PATH.relative_to(ROOT)),
            "launchReadiness": str(READINESS_PATH.relative_to(ROOT)),
            "weeklyReviewPacket": str(WEEKLY_REVIEW_PATH.relative_to(ROOT)),
        },
        "state": {
            "profileConfigured": profile_configured,
            "profileProofRows": len(profile_proofs),
            "readyToPublish": ready_to_publish,
            "postProofRows": len(post_proofs),
            "publishedRows": published_rows,
            "filledKpiRows": filled_kpi_rows,
            "emptyDataMode": bool(operation_proof.get("state", {}).get("emptyDataMode")) or bool(handoff.get("state", {}).get("emptyDataMode")),
        },
        "stageOrder": list(STAGE_ORDER),
        "stageCount": len(stages),
        "readyStages": sum(1 for stage in stages if stage.get("status") == "ready"),
        "profileReadyStages": profile_ready_stages,
        "publishReadyStages": publish_ready_stages,
        "kpiReadyStages": kpi_ready_stages,
        "weeklyReadyStages": weekly_ready_stages,
        "blockedStages": sum(1 for stage in stages if str(stage.get("status", "")).startswith("blocked")),
        "commandPhaseCounts": {phase: len(rows) for phase, rows in command_by_phase.items()},
        "safety": {
            "checkBeforeWrite": True,
            "profileGateBeforePublish": True,
            "postUrlBeforeKpi": True,
            "kpiBeforeWeeklyDecision": True,
            "emptyDataPreventsOfferChanges": True,
        },
        "stages": stages,
    }


def validate_rehearsal(packet: dict[str, object]) -> list[str]:
    issues: list[str] = []
    stages = packet.get("stages", [])
    if not isinstance(stages, list):
        return ["stages should be a list"]
    state = packet.get("state", {})
    if packet.get("stageOrder") != list(STAGE_ORDER):
        issues.append("stageOrder should match launch rehearsal policy")
    if packet.get("stageCount") != len(stages):
        issues.append("stageCount should match stages length")
    ready_count = sum(1 for stage in stages if stage.get("status") == "ready")
    profile_ready_count = sum(
        1
        for stage in stages
        if stage.get("stage") in {"profile_evidence", "profile_writeback"} and stage.get("status") == "ready"
    )
    publish_ready_count = sum(1 for stage in stages if stage.get("stage") == "publish_post" and stage.get("status") == "ready")
    kpi_ready_count = sum(
        1 for stage in stages if stage.get("stage") == "minimum_kpi_backfill" and stage.get("status") == "ready"
    )
    weekly_ready_count = sum(1 for stage in stages if stage.get("stage") == "weekly_review" and stage.get("status") == "ready")
    blocked_count = sum(1 for stage in stages if str(stage.get("status", "")).startswith("blocked"))
    if packet.get("readyStages") != ready_count:
        issues.append("readyStages should match stage statuses")
    if packet.get("profileReadyStages") != profile_ready_count:
        issues.append("profileReadyStages should match profile evidence/writeback ready statuses")
    if packet.get("publishReadyStages") != publish_ready_count:
        issues.append("publishReadyStages should match publish ready statuses")
    if packet.get("kpiReadyStages") != kpi_ready_count:
        issues.append("kpiReadyStages should match minimum KPI ready statuses")
    if packet.get("weeklyReadyStages") != weekly_ready_count:
        issues.append("weeklyReadyStages should match weekly review ready statuses")
    if not state.get("readyToPublish") and publish_ready_count:
        issues.append("publishReadyStages should stay zero until readyToPublish is true")
    if packet.get("blockedStages") != blocked_count:
        issues.append("blockedStages should match stage statuses")
    profile_proofs = int(state.get("profileProofRows", 0) or 0)
    post_proofs = int(state.get("postProofRows", 0) or 0)
    if sum(1 for stage in stages if stage.get("stage") == "profile_evidence") != profile_proofs:
        issues.append("profile evidence stages should match profile proof rows")
    if sum(1 for stage in stages if stage.get("stage") == "profile_writeback") != profile_proofs:
        issues.append("profile writeback stages should match profile proof rows")
    if sum(1 for stage in stages if stage.get("stage") == "publish_post") != post_proofs:
        issues.append("publish stages should match post proof rows")
    if sum(1 for stage in stages if stage.get("stage") == "minimum_kpi_backfill") != post_proofs:
        issues.append("minimum KPI stages should match post proof rows")
    if not state.get("readyToPublish"):
        for stage in stages:
            if stage.get("stage") == "publish_post" and stage.get("status") != "blocked_until_readiness_gate":
                issues.append("publish stages should stay blocked until readiness gate passes")
    if int(state.get("publishedRows", 0) or 0) < post_proofs:
        weekly = [stage for stage in stages if stage.get("stage") == "weekly_review"]
        if not weekly or weekly[0].get("status") != "blocked_until_minimum_kpi":
            issues.append("weekly review should stay blocked until first batch and KPI rows are complete")
    safety = packet.get("safety", {})
    for key in ("checkBeforeWrite", "profileGateBeforePublish", "postUrlBeforeKpi", "kpiBeforeWeeklyDecision", "emptyDataPreventsOfferChanges"):
        if not safety.get(key):
            issues.append(f"safety.{key} should be true")
    for stage in stages:
        label = f"{stage.get('stage', '<stage>')}/{stage.get('platform', '<platform>')}/{stage.get('taskId', '')}"
        if stage.get("stage") in {"profile_evidence", "publish_post"} and " check" not in str(stage.get("checkCommand", "")):
            issues.append(f"{label}: missing check command")
        if stage.get("stage") in {"profile_writeback", "publish_post"} and "--proof-note" not in str(stage.get("writeCommand", "")):
            issues.append(f"{label}: write command should require proof note")
        if stage.get("stage") == "minimum_kpi_backfill" and "post_url" not in stage.get("requiredFields", []):
            issues.append(f"{label}: minimum KPI fields should include post_url")
        if not stage.get("successSignal"):
            issues.append(f"{label}: missing success signal")
    return issues


def render_markdown(packet: dict[str, object], issues: list[str]) -> str:
    state = packet.get("state", {})
    lines = [
        "# LoveTypes Launch Rehearsal Packet",
        "",
        f"- Generated: `{packet.get('generatedAt', '')}`",
        f"- Profile configured: `{state.get('profileConfigured', 0)}/{state.get('profileProofRows', 0)}`",
        f"- Ready to publish: `{1 if state.get('readyToPublish') else 0}`",
        f"- Profile setup ready stages: `{packet.get('profileReadyStages', 0)}`",
        f"- Publish ready stages: `{packet.get('publishReadyStages', 0)}`",
        f"- KPI ready stages: `{packet.get('kpiReadyStages', 0)}`",
        f"- Published rows: `{state.get('publishedRows', 0)}/{state.get('postProofRows', 0)}`",
        f"- Filled KPI rows: `{state.get('filledKpiRows', 0)}/{state.get('postProofRows', 0)}`",
        f"- Empty data mode: `{1 if state.get('emptyDataMode') else 0}`",
        f"- Issues: `{len(issues)}`",
        "",
        "## Stage Order",
        "",
        *[f"{index}. `{stage}`" for index, stage in enumerate(packet.get("stageOrder", []), start=1)],
        "",
        "## Rehearsal Stages",
        "",
    ]
    for stage in packet.get("stages", []):
        lines.extend([
            f"### {stage.get('stage', '')}: {stage.get('platform', '')} {stage.get('taskId', '')}".strip(),
            "",
            f"- Status: `{stage.get('status', '')}`",
            f"- Blocked by: `{stage.get('blockedBy', '')}`",
            f"- Success signal: `{stage.get('successSignal', '')}`",
        ])
        if stage.get("checkCommand"):
            lines.append(f"- Check: `{stage.get('checkCommand', '')}`")
        if stage.get("writeCommand"):
            lines.append(f"- Write: `{stage.get('writeCommand', '')}`")
        if stage.get("writebackCommand"):
            lines.append(f"- Writeback: `{stage.get('writebackCommand', '')}`")
        lines.append("")
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the LoveTypes launch rehearsal packet.")
    parser.add_argument("--check", action="store_true", help="Validate without writing output files.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    args = parser.parse_args()

    packet = build_rehearsal()
    issues = validate_rehearsal(packet)
    print(f"promotion_launch_rehearsal_stage_rows={packet.get('stageCount', 0)}")
    print(f"promotion_launch_rehearsal_ready_stages={packet.get('readyStages', 0)}")
    print(f"promotion_launch_rehearsal_profile_ready_stages={packet.get('profileReadyStages', 0)}")
    print(f"promotion_launch_rehearsal_publish_ready_stages={packet.get('publishReadyStages', 0)}")
    print(f"promotion_launch_rehearsal_kpi_ready_stages={packet.get('kpiReadyStages', 0)}")
    print(f"promotion_launch_rehearsal_weekly_ready_stages={packet.get('weeklyReadyStages', 0)}")
    print(f"promotion_launch_rehearsal_blocked_stages={packet.get('blockedStages', 0)}")
    print(f"promotion_launch_rehearsal_profile_rows={packet.get('state', {}).get('profileProofRows', 0)}")
    print(f"promotion_launch_rehearsal_post_rows={packet.get('state', {}).get('postProofRows', 0)}")
    print(f"promotion_launch_rehearsal_ready_to_publish={1 if packet.get('state', {}).get('readyToPublish') else 0}")
    print(f"promotion_launch_rehearsal_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        json_output = Path(args.json_output)
        md_output = Path(args.output)
        json_output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_output.write_text(render_markdown(packet, issues), encoding="utf-8")
        print(f"promotion_launch_rehearsal_json={json_output.relative_to(ROOT)}")
        print(f"promotion_launch_rehearsal_md={md_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
