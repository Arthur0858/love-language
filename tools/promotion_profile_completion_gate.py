#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
READINESS_PATH = PROMOTION_DIR / "launch-readiness-gate.json"
EVIDENCE_PATH = PROMOTION_DIR / "evidence-ledger.json"
PROFILE_PACKET_PATH = PROMOTION_DIR / "profile-verification-packet.json"
FIRST_BATCH_PACKET_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
MD_OUTPUT = PROMOTION_DIR / "profile-completion-gate.md"
JSON_OUTPUT = PROMOTION_DIR / "profile-completion-gate.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_gate() -> dict:
    readiness = load_json(READINESS_PATH)
    evidence = load_json(EVIDENCE_PATH)
    profile_packet = load_json(PROFILE_PACKET_PATH)
    first_batch = load_json(FIRST_BATCH_PACKET_PATH)

    readiness_metrics = readiness.get("metrics", {}) if isinstance(readiness.get("metrics"), dict) else {}
    readiness_state = readiness.get("readiness", {}) if isinstance(readiness.get("readiness"), dict) else {}
    evidence_metrics = evidence.get("metrics", {}) if isinstance(evidence.get("metrics"), dict) else {}

    profile_configured = int(readiness_metrics.get("profileConfigured") or 0)
    expected_profiles = int(readiness_metrics.get("profileRows") or 0)
    ready_to_publish = bool(readiness_state.get("readyToPublishPosts"))
    evidence_required = int(evidence_metrics.get("required") or 0)
    evidence_traceable = int(evidence_metrics.get("traceable") or 0)
    evidence_pending = int(evidence_metrics.get("pending") or 0)
    evidence_issues = int(evidence_metrics.get("issues") or 0)
    evidence_not_required_yet = sum(
        1
        for row in evidence.get("rows", [])
        if isinstance(row, dict) and row.get("evidence_status") == "not_required_yet"
    )
    profile_packet_ready = bool(profile_packet.get("readyToPublish"))
    first_batch_ready = bool(first_batch.get("readyToPublish"))

    all_profiles_configured = expected_profiles > 0 and profile_configured == expected_profiles
    evidence_structurally_clean = evidence_issues == 0
    evidence_required_now = evidence_required > 0
    evidence_complete = (
        all_profiles_configured
        and evidence_structurally_clean
        and evidence_required_now
        and evidence_required == evidence_traceable
    )
    packets_in_sync = profile_packet_ready == ready_to_publish and first_batch_ready == ready_to_publish
    ready_for_first_batch_publish = all_profiles_configured and ready_to_publish and evidence_complete and packets_in_sync

    blockers: list[dict[str, str]] = []
    if not all_profiles_configured:
        blockers.append({
            "id": "profile_links_not_configured",
            "message": f"profile configured {profile_configured}/{expected_profiles}; finish platform profile setup before publishing.",
            "release": "All profile rows are set/live in platform-profile-tracker.csv.",
        })
    if evidence_required_now and not evidence_complete:
        blockers.append({
            "id": "profile_evidence_incomplete",
            "message": (
                f"traceable evidence {evidence_traceable}/{evidence_required}, "
                f"pending rows {evidence_pending}, evidence issues {evidence_issues}."
            ),
            "release": "Every completed profile/post/lead row has a traceable proof note.",
        })
    if not packets_in_sync:
        blockers.append({
            "id": "profile_publish_packets_out_of_sync",
            "message": "profile verification packet or first-batch publication packet does not match launch readiness.",
            "release": "Run promotion_daily_ops_refresh.py after profile writeback.",
        })
    if all_profiles_configured and not ready_to_publish:
        blockers.append({
            "id": "readiness_not_open",
            "message": "profiles are configured but launch readiness has not opened first-batch publishing.",
            "release": "Run launch readiness and resolve any remaining structural blocker.",
        })

    issues: list[str] = []
    if expected_profiles != 3:
        issues.append(f"expected 3 profile rows, got {expected_profiles}")
    if evidence_required and evidence_traceable > evidence_required:
        issues.append("traceable evidence count cannot exceed required evidence count")
    if first_batch.get("rowCount") != 3:
        issues.append(f"expected first batch rowCount 3, got {first_batch.get('rowCount')}")
    if profile_packet.get("platformCount") != 3:
        issues.append(f"expected profile packet platformCount 3, got {profile_packet.get('platformCount')}")
    if packets_in_sync is False and ready_to_publish:
        issues.append("publish packets must be refreshed when readiness opens")

    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "readiness": str(READINESS_PATH.relative_to(ROOT)),
            "evidence": str(EVIDENCE_PATH.relative_to(ROOT)),
            "profilePacket": str(PROFILE_PACKET_PATH.relative_to(ROOT)),
            "firstBatchPacket": str(FIRST_BATCH_PACKET_PATH.relative_to(ROOT)),
        },
        "metrics": {
            "profileConfigured": profile_configured,
            "expectedProfiles": expected_profiles,
            "evidenceRequired": evidence_required,
            "evidenceTraceable": evidence_traceable,
            "evidencePending": evidence_pending,
            "evidenceNotRequiredYet": evidence_not_required_yet,
            "evidenceIssues": evidence_issues,
            "blockers": len(blockers),
            "issues": len(issues),
        },
        "state": {
            "allProfilesConfigured": all_profiles_configured,
            "readinessReadyToPublish": ready_to_publish,
            "profilePacketReadyToPublish": profile_packet_ready,
            "firstBatchPacketReadyToPublish": first_batch_ready,
            "evidenceStructurallyClean": evidence_structurally_clean,
            "evidenceRequiredNow": evidence_required_now,
            "evidenceComplete": evidence_complete,
            "packetsInSync": packets_in_sync,
            "readyForFirstBatchPublish": ready_for_first_batch_publish,
        },
        "nextAction": (
            "Publish first-batch Shorts and write back post URLs."
            if ready_for_first_batch_publish
            else "Finish three platform profile links, refresh ops docs, then re-run this gate."
        ),
        "blockers": blockers,
        "issues": issues,
    }


def render_markdown(gate: dict) -> str:
    metrics = gate["metrics"]
    state = gate["state"]
    lines = [
        "# LoveTypes Profile Completion Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- profile configured：{metrics['profileConfigured']} / {metrics['expectedProfiles']}",
        f"- evidence traceable：{metrics['evidenceTraceable']} / {metrics['evidenceRequired']}",
        f"- evidence pending：{metrics['evidencePending']}",
        f"- evidence not required yet：{metrics['evidenceNotRequiredYet']}",
        f"- evidence issues：{metrics['evidenceIssues']}",
        f"- packets in sync：{int(state['packetsInSync'])}",
        f"- ready for first batch publish：{int(state['readyForFirstBatchPublish'])}",
        f"- blockers：{metrics['blockers']}",
        f"- issues：{metrics['issues']}",
        "",
        "## State",
        "",
        f"- allProfilesConfigured：`{int(state['allProfilesConfigured'])}`",
        f"- readinessReadyToPublish：`{int(state['readinessReadyToPublish'])}`",
        f"- profilePacketReadyToPublish：`{int(state['profilePacketReadyToPublish'])}`",
        f"- firstBatchPacketReadyToPublish：`{int(state['firstBatchPacketReadyToPublish'])}`",
        f"- evidenceStructurallyClean：`{int(state['evidenceStructurallyClean'])}`",
        f"- evidenceRequiredNow：`{int(state['evidenceRequiredNow'])}`",
        f"- evidenceComplete：`{int(state['evidenceComplete'])}`",
        "",
        "## Next Action",
        "",
        f"- {gate['nextAction']}",
        "",
        "## Blockers",
        "",
    ]
    if gate["blockers"]:
        for blocker in gate["blockers"]:
            lines.append(f"- `{blocker['id']}`：{blocker['message']} 解除條件：{blocker['release']}")
    else:
        lines.append("- 無。")
    if gate["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in gate["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(gate: dict) -> None:
    JSON_OUTPUT.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(render_markdown(gate), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether completed profile setup can hand off to first-batch publishing.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    args = parser.parse_args()

    gate = build_gate()
    if not args.check:
        write_outputs(gate)
        print(f"promotion_profile_completion_gate={MD_OUTPUT}")
        print(f"promotion_profile_completion_gate_json={JSON_OUTPUT}")
    metrics = gate["metrics"]
    state = gate["state"]
    print(f"promotion_profile_completion_configured={metrics['profileConfigured']}")
    print(f"promotion_profile_completion_expected={metrics['expectedProfiles']}")
    print(f"promotion_profile_completion_evidence_required={metrics['evidenceRequired']}")
    print(f"promotion_profile_completion_evidence_traceable={metrics['evidenceTraceable']}")
    print(f"promotion_profile_completion_evidence_pending={metrics['evidencePending']}")
    print(f"promotion_profile_completion_evidence_not_required_yet={metrics['evidenceNotRequiredYet']}")
    print(f"promotion_profile_completion_evidence_issues={metrics['evidenceIssues']}")
    print(f"promotion_profile_completion_evidence_structurally_clean={int(state['evidenceStructurallyClean'])}")
    print(f"promotion_profile_completion_evidence_required_now={int(state['evidenceRequiredNow'])}")
    print(f"promotion_profile_completion_evidence_complete={int(state['evidenceComplete'])}")
    print(f"promotion_profile_completion_packets_in_sync={int(state['packetsInSync'])}")
    print(f"promotion_profile_completion_ready_to_publish={int(state['readyForFirstBatchPublish'])}")
    print(f"promotion_profile_completion_blockers={metrics['blockers']}")
    print(f"promotion_profile_completion_issues={metrics['issues']}")
    for issue in gate["issues"]:
        print(issue)
    return 1 if gate["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
