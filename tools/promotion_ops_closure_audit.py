#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
COMMAND_CENTER = PROMOTION_DIR / "launch-command-center.json"
OPERATOR_HANDOFF = PROMOTION_DIR / "operator-handoff-packet.json"
PROFILE_PUBLISH_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
NEXT_ACTIONS = PROMOTION_DIR / "next-actions.json"
PROFILE_PACKET = PROMOTION_DIR / "profile-verification-packet.json"
FIRST_BATCH = PROMOTION_DIR / "first-batch-publication-packet.json"
READINESS = PROMOTION_DIR / "launch-readiness-gate.json"
EXPECTED_EMPTY_ACTIONS = {
    "publish_first_batch",
    "fill_required_kpis",
    "set_platform_profile_links",
    "fill_platform_profile_kpis",
    "hold_offer_changes",
}
EXPECTED_HANDOFF_IMPORTS = {
    "profile_setup_import",
    "post_publish_import",
    "lead_request_import",
}
EXPECTED_PROFILE_PUBLISH_STEPS = {
    "profile_action_sheet_ready",
    "profile_setup_handoff_ready",
    "profile_writeback_complete",
    "profile_evidence_complete",
    "ops_refresh_after_profile",
    "launch_readiness_open",
    "first_batch_action_sheet_ready",
    "publish_readiness_guarded",
    "post_proof_handoff_guarded",
    "single_current_blocker_visible",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rows_by_phase(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("phase", "")), []).append(row)
    return grouped


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    command = load_json(COMMAND_CENTER)
    handoff = load_json(OPERATOR_HANDOFF)
    profile_publish = load_json(PROFILE_PUBLISH_HANDOFF)
    next_actions = load_json(NEXT_ACTIONS)
    profile = load_json(PROFILE_PACKET)
    first_batch = load_json(FIRST_BATCH)
    readiness = load_json(READINESS)

    command_rows = command.get("rows", [])
    handoff_steps = handoff.get("steps", [])
    profile_publish_rows = profile_publish.get("rows", [])
    next_action_rows = next_actions.get("actions", [])
    profile_platforms = profile.get("platforms", [])
    first_batch_rows = first_batch.get("rows", [])
    readiness_metrics = readiness.get("metrics", {})
    command_by_phase = rows_by_phase(command_rows if isinstance(command_rows, list) else [])
    handoff_by_phase = rows_by_phase(handoff_steps if isinstance(handoff_steps, list) else [])

    if not isinstance(command_rows, list):
        issues.append("launch-command-center rows should be a list")
        command_rows = []
    if not isinstance(handoff_steps, list):
        issues.append("operator handoff steps should be a list")
        handoff_steps = []
    if not isinstance(profile_publish_rows, list):
        issues.append("profile publish handoff rows should be a list")
        profile_publish_rows = []
    if command.get("rowCount") != len(command_rows):
        issues.append("command center rowCount should match rows length")
    if handoff.get("stepCount") != len(handoff_steps):
        issues.append("operator handoff stepCount should match steps length")
    profile_publish_metrics = profile_publish.get("metrics", {})
    if not isinstance(profile_publish_metrics, dict):
        profile_publish_metrics = {}
    if int(profile_publish_metrics.get("rows", 0) or 0) != len(profile_publish_rows):
        issues.append("profile publish handoff metrics.rows should match rows length")
    if len(profile_publish_rows) != len(EXPECTED_PROFILE_PUBLISH_STEPS):
        issues.append(f"profile publish handoff should have {len(EXPECTED_PROFILE_PUBLISH_STEPS)} rows")

    expected_phase_counts = command.get("expectedPhaseCounts", {})
    for phase, expected in expected_phase_counts.items():
        if len(command_by_phase.get(phase, [])) != expected:
            issues.append(f"command center phase {phase} should have {expected} rows")

    profile_pending = int(profile.get("pendingCount", 0) or 0)
    first_batch_pending = int(first_batch.get("pendingRows", 0) or 0)
    if len(command_by_phase.get("profile_setup", [])) != int(profile.get("platformCount", 0) or 0):
        issues.append("command center profile_setup rows should match profile packet platformCount")
    if len(handoff_by_phase.get("profile_setup", [])) != profile_pending:
        issues.append("operator handoff profile_setup steps should match profile pendingCount")
    if len(command_by_phase.get("publish_post", [])) != first_batch_pending * int(profile.get("platformCount", 0) or 0):
        issues.append("command center publish_post rows should cover pending first-batch scripts on each platform")
    if len(handoff_by_phase.get("publish_first_batch", [])) != first_batch_pending:
        issues.append("operator handoff publish_first_batch steps should match first batch pendingRows")

    if bool(command.get("dataState", {}).get("emptyDataMode")) != bool(next_actions.get("dataState", {}).get("emptyDataMode")):
        issues.append("command center and next actions should agree on emptyDataMode")
    if bool(handoff.get("state", {}).get("emptyDataMode")) != bool(next_actions.get("dataState", {}).get("emptyDataMode")):
        issues.append("operator handoff and next actions should agree on emptyDataMode")
    if bool(handoff.get("state", {}).get("readyToPublish")) != bool(readiness.get("readiness", {}).get("readyToPublishPosts")):
        issues.append("operator handoff readyToPublish should match readiness readyToPublishPosts")
    if int(handoff.get("state", {}).get("profilePending", 0) or 0) != profile_pending:
        issues.append("operator handoff profilePending should match profile packet")
    if int(handoff.get("state", {}).get("firstBatchPending", 0) or 0) != first_batch_pending:
        issues.append("operator handoff firstBatchPending should match first batch packet")
    if int(readiness_metrics.get("profileConfigured", 0) or 0) != int(profile.get("configuredCount", 0) or 0):
        issues.append("readiness profileConfigured should match profile packet")
    if int(readiness_metrics.get("publishedRows", 0) or 0) != int(first_batch.get("publishedRows", 0) or 0):
        issues.append("readiness publishedRows should match first batch packet")

    action_ids = {str(action.get("id", "")) for action in next_action_rows if isinstance(action, dict)}
    if not EXPECTED_EMPTY_ACTIONS.issubset(action_ids):
        issues.append("next actions missing empty-data launch actions")
    import_ids = {
        str(item.get("id", ""))
        for item in handoff.get("structuredImports", [])
        if isinstance(item, dict)
    }
    if import_ids != EXPECTED_HANDOFF_IMPORTS:
        issues.append("operator handoff structured imports should cover profile, post, and lead imports")
    profile_publish_step_ids = {
        str(row.get("step_id", ""))
        for row in profile_publish_rows
        if isinstance(row, dict)
    }
    if profile_publish_step_ids != EXPECTED_PROFILE_PUBLISH_STEPS:
        missing = sorted(EXPECTED_PROFILE_PUBLISH_STEPS - profile_publish_step_ids)
        extra = sorted(profile_publish_step_ids - EXPECTED_PROFILE_PUBLISH_STEPS)
        issues.append(f"profile publish handoff step mismatch; missing={missing}, extra={extra}")

    command_ready = sum(1 for row in command_rows if row.get("status") == "ready")
    command_blocked = sum(1 for row in command_rows if str(row.get("status", "")).startswith("blocked"))
    if command.get("readyRows") != command_ready:
        issues.append("command center readyRows should match row statuses")
    if command.get("blockedRows") != command_blocked:
        issues.append("command center blockedRows should match row statuses")
    handoff_ready = sum(1 for step in handoff_steps if step.get("status") == "ready")
    handoff_blocked = sum(1 for step in handoff_steps if str(step.get("status", "")).startswith("blocked"))
    if handoff.get("readyCount") != handoff_ready:
        issues.append("operator handoff readyCount should match step statuses")
    if handoff.get("blockedCount") != handoff_blocked:
        issues.append("operator handoff blockedCount should match step statuses")
    profile_publish_complete = sum(1 for row in profile_publish_rows if row.get("status") == "complete")
    profile_publish_current = sum(1 for row in profile_publish_rows if row.get("status") == "current_blocker")
    profile_publish_blocked = sum(1 for row in profile_publish_rows if row.get("status") == "blocked_upstream")
    if int(profile_publish_metrics.get("completeRows", 0) or 0) != profile_publish_complete:
        issues.append("profile publish handoff completeRows should match row statuses")
    if int(profile_publish_metrics.get("currentBlockers", 0) or 0) != profile_publish_current:
        issues.append("profile publish handoff currentBlockers should match row statuses")
    if int(profile_publish_metrics.get("blockedUpstreamRows", 0) or 0) != profile_publish_blocked:
        issues.append("profile publish handoff blockedUpstreamRows should match row statuses")
    if profile_publish_current != 1:
        issues.append("profile publish handoff should expose exactly one current blocker")
    if bool(profile_publish_metrics.get("readyToPublish")) != bool(readiness.get("readiness", {}).get("readyToPublishPosts")):
        issues.append("profile publish handoff readyToPublish should match launch readiness readyToPublishPosts")
    guarded_steps = {"profile_setup_handoff_ready", "publish_readiness_guarded", "post_proof_handoff_guarded"}
    incomplete_guarded = [
        str(row.get("step_id", ""))
        for row in profile_publish_rows
        if row.get("step_id") in guarded_steps and row.get("status") != "complete"
    ]
    if incomplete_guarded:
        issues.append("profile publish guarded handoff steps should be complete before profile writeback: " + ", ".join(incomplete_guarded))

    for row in command_rows:
        phase = row.get("phase", "")
        title = row.get("title", "<row>")
        if phase in {"publish_post", "kpi_backfill"} and not row.get("blocked_by"):
            issues.append(f"{title}: publish/kpi command rows should declare blocked_by")
        safety = str(row.get("safety_note", ""))
        if "測驗" not in safety and "不" not in safety:
            issues.append(f"{title}: command safety note should preserve quiz-only/no-commerce boundary")

    return {
        "commandRows": len(command_rows),
        "handoffSteps": len(handoff_steps),
        "profilePublishRows": len(profile_publish_rows),
        "profilePublishComplete": profile_publish_complete,
        "profilePublishCurrentBlockers": profile_publish_current,
        "profilePublishBlockedUpstream": profile_publish_blocked,
        "nextActions": len(next_action_rows) if isinstance(next_action_rows, list) else 0,
        "profilePlatforms": len(profile_platforms) if isinstance(profile_platforms, list) else 0,
        "firstBatchRows": len(first_batch_rows) if isinstance(first_batch_rows, list) else 0,
        "readyRows": command_ready,
        "blockedRows": command_blocked,
        "structuredImports": len(import_ids),
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_ops_closure_command_rows={metrics['commandRows']}")
    print(f"promotion_ops_closure_handoff_steps={metrics['handoffSteps']}")
    print(f"promotion_ops_closure_profile_publish_rows={metrics['profilePublishRows']}")
    print(f"promotion_ops_closure_profile_publish_complete={metrics['profilePublishComplete']}")
    print(f"promotion_ops_closure_profile_publish_current_blockers={metrics['profilePublishCurrentBlockers']}")
    print(f"promotion_ops_closure_profile_publish_blocked_upstream={metrics['profilePublishBlockedUpstream']}")
    print(f"promotion_ops_closure_next_actions={metrics['nextActions']}")
    print(f"promotion_ops_closure_profile_platforms={metrics['profilePlatforms']}")
    print(f"promotion_ops_closure_first_batch_rows={metrics['firstBatchRows']}")
    print(f"promotion_ops_closure_ready_rows={metrics['readyRows']}")
    print(f"promotion_ops_closure_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_ops_closure_structured_imports={metrics['structuredImports']}")
    print(f"promotion_ops_closure_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
