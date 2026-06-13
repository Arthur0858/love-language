#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_ACTION = PROMOTION_DIR / "profile-setup-action-sheet.json"
PROFILE_COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
LAUNCH_READINESS = PROMOTION_DIR / "launch-readiness-gate.json"
FIRST_BATCH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
STAGE_MATRIX = PROMOTION_DIR / "stage-transition-matrix.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-publish-handoff.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-publish-handoff.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "profile-publish-handoff.csv"

CSV_FIELDS = [
    "step_id",
    "phase",
    "status",
    "current_value",
    "required_value",
    "owner_action",
    "evidence_required",
    "command",
    "stop_condition",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def metric(data: dict, key: str, default: int = 0) -> int:
    metrics = data.get("metrics", {})
    if not isinstance(metrics, dict):
        return default
    try:
        return int(metrics.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def state(data: dict, key: str) -> int:
    values = data.get("state", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def readiness_flag(data: dict, key: str) -> int:
    values = data.get("readiness", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def build_rows() -> list[dict[str, object]]:
    profile_action = load_json(PROFILE_ACTION)
    completion = load_json(PROFILE_COMPLETION)
    readiness = load_json(LAUNCH_READINESS)
    first_batch = load_json(FIRST_BATCH_ACTION)
    stage = load_json(STAGE_MATRIX)

    profile_rows = metric(profile_action, "rows")
    profile_action_issues = len(profile_action.get("issues", []) or [])
    profile_configured = metric(completion, "profileConfigured")
    expected_profiles = metric(completion, "expectedProfiles", 3)
    evidence_traceable = metric(completion, "evidenceTraceable")
    evidence_required = max(metric(completion, "evidenceRequired"), expected_profiles)
    packets_in_sync = state(completion, "packetsInSync")
    ready_to_publish = readiness_flag(readiness, "readyToPublishPosts")
    first_batch_ready = metric(first_batch, "ready")
    first_batch_rows = metric(first_batch, "rows", 3)
    current_blockers = metric(stage, "currentBlockers")

    rows: list[dict[str, object]] = [
        {
            "step_id": "profile_action_sheet_ready",
            "phase": "profile_setup",
            "current_value": profile_rows if profile_action_issues == 0 else 0,
            "required_value": 3,
            "owner_action": "Use the platform-specific Bio/Profile link copy from the action sheet.",
            "evidence_required": "Action sheet has three platforms, valid /start/ UTM links, and no issues.",
            "command": "python3 tools/promotion_profile_setup_action_sheet.py --check",
            "stop_condition": "Stop if any Bio adds paid, diagnosis, therapy, or guarantee claims.",
        },
        {
            "step_id": "profile_writeback_complete",
            "phase": "profile_writeback",
            "current_value": profile_configured,
            "required_value": expected_profiles,
            "owner_action": "After setting each public profile link, write back status set/live with a proof note.",
            "evidence_required": "platform-profile-tracker.csv has status set/live, set date, and traceable proof for all platforms.",
            "command": "python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts.txt",
            "stop_condition": "Do not write set/live without screenshot, clicked public link, or platform timestamp evidence.",
        },
        {
            "step_id": "profile_evidence_complete",
            "phase": "profile_writeback",
            "current_value": evidence_traceable,
            "required_value": evidence_required,
            "owner_action": "Confirm every completed profile row has proof in the evidence ledger.",
            "evidence_required": "Evidence ledger traceable count equals required count and evidence issues are zero.",
            "command": "python3 tools/promotion_evidence_ledger.py --check",
            "stop_condition": "Stop if proof note is vague, missing, or not tied to a platform/date.",
        },
        {
            "step_id": "ops_refresh_after_profile",
            "phase": "handoff",
            "current_value": packets_in_sync,
            "required_value": 1,
            "owner_action": "Refresh promotion docs after profile writeback before opening publication.",
            "evidence_required": "Profile completion gate packetsInSync is true.",
            "command": "python3 tools/promotion_daily_ops_refresh.py",
            "stop_condition": "Do not publish from stale action sheets after tracker writeback.",
        },
        {
            "step_id": "launch_readiness_open",
            "phase": "handoff",
            "current_value": ready_to_publish,
            "required_value": 1,
            "owner_action": "Confirm launch readiness opens first-batch publishing.",
            "evidence_required": "launch-readiness-gate.json readiness.readyToPublishPosts is true.",
            "command": "python3 tools/promotion_launch_readiness_gate.py --check",
            "stop_condition": "Stop if profile links are incomplete, campaign UTM is invalid, or assets are not ready.",
        },
        {
            "step_id": "first_batch_action_sheet_ready",
            "phase": "publish",
            "current_value": first_batch_ready,
            "required_value": first_batch_rows,
            "owner_action": "Publish only the first batch rows that become ready after the profile gate opens.",
            "evidence_required": "First-batch publish action sheet has three ready rows and zero issues.",
            "command": "python3 tools/promotion_first_batch_publish_action_sheet.py --check",
            "stop_condition": "Do not publish if any row remains blocked_until_profile_links.",
        },
        {
            "step_id": "single_current_blocker_visible",
            "phase": "stage_control",
            "current_value": current_blockers,
            "required_value": 1,
            "owner_action": "Keep the stage matrix exposing exactly one current blocker before advancing.",
            "evidence_required": "stage-transition-matrix has one current_blocker and no issues.",
            "command": "python3 tools/promotion_stage_transition_matrix.py --check",
            "stop_condition": "Stop if multiple current blockers appear or if later stages become next before profile handoff.",
        },
    ]
    for index, row in enumerate(rows):
        current = int(row["current_value"] or 0)
        required = int(row["required_value"] or 0)
        if current >= required:
            row["status"] = "complete"
        elif any(previous.get("status") != "complete" for previous in rows[:index]):
            row["status"] = "blocked_upstream"
        else:
            row["status"] = "current_blocker"
    return rows


def build_handoff() -> dict:
    rows = build_rows()
    issues = validate_rows(rows)
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "profileActionSheet": str(PROFILE_ACTION.relative_to(ROOT)),
            "profileCompletionGate": str(PROFILE_COMPLETION.relative_to(ROOT)),
            "launchReadinessGate": str(LAUNCH_READINESS.relative_to(ROOT)),
            "firstBatchActionSheet": str(FIRST_BATCH_ACTION.relative_to(ROOT)),
            "stageTransitionMatrix": str(STAGE_MATRIX.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "completeRows": sum(1 for row in rows if row["status"] == "complete"),
            "currentBlockers": sum(1 for row in rows if row["status"] == "current_blocker"),
            "blockedUpstreamRows": sum(1 for row in rows if row["status"] == "blocked_upstream"),
            "readyToPublish": 1 if all(row["status"] == "complete" for row in rows) else 0,
            "issues": len(issues),
        },
        "policy": {
            "noProfileProofNoPublish": True,
            "refreshAfterWriteback": True,
            "firstBatchOnlyAfterGate": True,
            "emptyDataModeUntilKpi": True,
        },
        "rows": rows,
        "issues": issues,
    }


def validate_rows(rows: list[dict[str, object]]) -> list[str]:
    issues: list[str] = []
    if len(rows) != 7:
        issues.append(f"expected 7 handoff rows, got {len(rows)}")
    statuses = {str(row.get("status", "")) for row in rows}
    if not statuses <= {"complete", "current_blocker", "blocked_upstream"}:
        issues.append("handoff rows contain invalid statuses")
    current_blockers = sum(1 for row in rows if row.get("status") == "current_blocker")
    if current_blockers != 1:
        issues.append("handoff should expose exactly one current blocker")
    for row in rows:
        label = str(row.get("step_id", "<missing>"))
        if not row.get("command") or not row.get("stop_condition"):
            issues.append(f"{label}: missing command or stop condition")
        if int(row.get("required_value", 0) or 0) < 1:
            issues.append(f"{label}: required value must be positive")
    return issues


def render_markdown(handoff: dict) -> str:
    metrics = handoff["metrics"]
    lines = [
        "# LoveTypes Profile to Publish Handoff",
        "",
        f"- 產生日期：{handoff['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- complete rows：{metrics['completeRows']}",
        f"- current blockers：{metrics['currentBlockers']}",
        f"- blocked upstream rows：{metrics['blockedUpstreamRows']}",
        f"- ready to publish：{metrics['readyToPublish']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rule",
        "",
        "- Profile proof must be written back before first-batch publishing.",
        "- Run the daily ops refresh after profile writeback before using publish sheets.",
        "- Keep KPI and product decisions in empty-data mode until real post URLs and metric proof exist.",
        "",
        "## Handoff Steps",
        "",
    ]
    for row in handoff["rows"]:
        lines.extend([
            f"### `{row['step_id']}`",
            "",
            f"- phase：`{row['phase']}`",
            f"- status：`{row['status']}`",
            f"- value：{row['current_value']} / {row['required_value']}",
            f"- action：{row['owner_action']}",
            f"- evidence：{row['evidence_required']}",
            f"- command：`{row['command']}`",
            f"- stop：{row['stop_condition']}",
            "",
        ])
    if handoff["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in handoff["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the profile-to-publish handoff checklist for LoveTypes promotion.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    handoff = build_handoff()
    metrics = handoff["metrics"]
    print(f"promotion_profile_publish_handoff_rows={metrics['rows']}")
    print(f"promotion_profile_publish_handoff_complete={metrics['completeRows']}")
    print(f"promotion_profile_publish_handoff_current_blockers={metrics['currentBlockers']}")
    print(f"promotion_profile_publish_handoff_blocked_upstream={metrics['blockedUpstreamRows']}")
    print(f"promotion_profile_publish_handoff_ready_to_publish={metrics['readyToPublish']}")
    print(f"promotion_profile_publish_handoff_issues={metrics['issues']}")
    for issue in handoff["issues"]:
        print(issue)
    if handoff["issues"]:
        return 1
    if not args.check:
        output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        output.write_text(render_markdown(handoff), encoding="utf-8")
        json_output.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, handoff["rows"])
        print(f"promotion_profile_publish_handoff={output.relative_to(ROOT)}")
        print(f"promotion_profile_publish_handoff_json={json_output.relative_to(ROOT)}")
        print(f"promotion_profile_publish_handoff_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
