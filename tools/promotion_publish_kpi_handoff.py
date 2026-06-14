#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
FIRST_BATCH_PUBLISH = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
FIRST_BATCH_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
FIRST_BATCH_KPI = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
FIRST_BATCH_COMPLETION = PROMOTION_DIR / "first-batch-completion-gate.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
STAGE_MATRIX = PROMOTION_DIR / "stage-transition-matrix.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "publish-kpi-handoff.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "publish-kpi-handoff.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "publish-kpi-handoff.csv"

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
    values = data.get("metrics", {})
    if not isinstance(values, dict):
        return default
    try:
        return int(values.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def state(data: dict, key: str) -> int:
    values = data.get("state", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def build_rows() -> list[dict[str, object]]:
    profile_handoff = load_json(PROFILE_HANDOFF)
    publish_action = load_json(FIRST_BATCH_PUBLISH)
    first_batch = load_json(FIRST_BATCH_PACKET)
    kpi_action = load_json(FIRST_BATCH_KPI)
    completion = load_json(FIRST_BATCH_COMPLETION)
    weekly = load_json(WEEKLY_REVIEW)
    stage = load_json(STAGE_MATRIX)

    profile_ready = metric(profile_handoff, "readyToPublish")
    publish_ready = metric(publish_action, "ready")
    publish_rows = metric(publish_action, "rows", 3)
    published_rows = int(first_batch.get("publishedRows", 0) or 0)
    minimum_kpi_rows = int(first_batch.get("minimumKpiRows", 0) or 0)
    kpi_ready = metric(kpi_action, "ready")
    kpi_blocked = metric(kpi_action, "blocked")
    traceable_evidence = metric(completion, "traceablePostEvidence")
    ready_for_weekly = state(completion, "readyForWeeklyReview")
    weekly_ready = state(weekly, "readyForWeeklyDecision")
    empty_data = state(weekly, "emptyDataMode")
    stage_current_blockers = metric(stage, "currentBlockers")

    rows: list[dict[str, object]] = [
        {
            "step_id": "profile_publish_handoff_open",
            "phase": "profile_to_publish",
            "current_value": profile_ready,
            "required_value": 1,
            "owner_action": "Only continue after the profile handoff says first-batch publishing is open.",
            "evidence_required": "profile-publish-handoff readyToPublish is true after profile proof writeback and refresh.",
            "command": "python3 tools/promotion_profile_publish_handoff.py --check",
            "stop_condition": "Do not publish first-batch posts while profile_writeback_complete is still blocked.",
        },
        {
            "step_id": "first_batch_publish_sheet_ready",
            "phase": "publish",
            "current_value": publish_ready,
            "required_value": publish_rows,
            "owner_action": "Confirm three first-batch rows are ready before opening platform publishing.",
            "evidence_required": "first-batch publish action sheet has three ready rows and zero issues.",
            "command": "python3 tools/promotion_first_batch_publish_action_sheet.py --check",
            "stop_condition": "Do not publish if any row remains blocked_until_profile_links.",
        },
        {
            "step_id": "post_url_writeback_complete",
            "phase": "post_writeback",
            "current_value": published_rows,
            "required_value": 3,
            "owner_action": "After each platform post is public, write back real HTTPS post_url with proof.",
            "evidence_required": "posting-queue.csv and platform-kpi-tracker.csv have published status, date, post_url, and proof note.",
            "command": "python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt",
            "stop_condition": "Do not mark published with placeholder URLs, private URLs, or unverified scheduled drafts.",
        },
        {
            "step_id": "post_evidence_traceable",
            "phase": "post_writeback",
            "current_value": traceable_evidence,
            "required_value": max(published_rows, 3),
            "owner_action": "Confirm every first-batch post has traceable public URL evidence.",
            "evidence_required": "first-batch completion gate traceablePostEvidence matches all three published rows.",
            "command": "python3 tools/promotion_first_batch_completion_gate.py --check",
            "stop_condition": "Stop if proof is generic, missing, or not tied to platform/date/post URL.",
        },
        {
            "step_id": "minimum_kpi_source_check",
            "phase": "kpi_writeback",
            "current_value": minimum_kpi_rows,
            "required_value": 3,
            "owner_action": "Backfill site_clicks, quiz_starts, quiz_completions or verified-zero proof for each platform.",
            "evidence_required": "first-batch KPI action sheet has three ready rows before source checks, then minimumKpiRows reaches three.",
            "command": "python3 tools/promotion_first_batch_kpi_action_sheet.py --check",
            "stop_condition": "Do not treat 0 as data unless the platform or site analytics source was checked.",
        },
        {
            "step_id": "weekly_review_open",
            "phase": "weekly_review",
            "current_value": ready_for_weekly,
            "required_value": 1,
            "owner_action": "Open weekly review only after post URLs, proof, and minimum KPI are complete.",
            "evidence_required": "first-batch-completion-gate readyForWeeklyReview is true.",
            "command": "python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_week_decision_gate.py --check",
            "stop_condition": "Do not rank guardians, offers, Luna, or affiliate routes while empty data mode is true.",
        },
        {
            "step_id": "empty_data_safety_locked",
            "phase": "decision_safety",
            "current_value": 1 if empty_data and not weekly_ready and stage_current_blockers == 1 else 0,
            "required_value": 1,
            "owner_action": "Keep commercial decisions locked until weekly review opens with real data.",
            "evidence_required": "weekly-review remains empty-data mode and stage matrix exposes exactly one current blocker.",
            "command": "python3 tools/promotion_weekly_review_packet.py --check && python3 tools/promotion_stage_transition_matrix.py --check",
            "stop_condition": "Stop if commercial or paid CTA decisions become allowed before KPI proof.",
        },
    ]
    # Keep the safety row complete while upstream work is blocked; it is a guardrail, not an advancement gate.
    for index, row in enumerate(rows):
        current = int(row["current_value"] or 0)
        required = int(row["required_value"] or 0)
        if current >= required:
            row["status"] = "complete"
        elif any(previous.get("status") != "complete" for previous in rows[:index]):
            row["status"] = "blocked_upstream"
        else:
            row["status"] = "current_blocker"
    if kpi_blocked and published_rows == 0:
        rows[4]["owner_action"] = "Keep KPI rows blocked until real post URLs are written back."
    if kpi_ready:
        rows[4]["owner_action"] = "Run source checks and write back minimum KPI or verified-zero proof for each platform."
    return rows


def validate_rows(rows: list[dict[str, object]]) -> list[str]:
    issues: list[str] = []
    if len(rows) != 7:
        issues.append(f"expected 7 handoff rows, got {len(rows)}")
    statuses = {str(row.get("status", "")) for row in rows}
    if not statuses <= {"complete", "current_blocker", "blocked_upstream"}:
        issues.append("handoff rows contain invalid statuses")
    current_blockers = sum(1 for row in rows if row.get("status") == "current_blocker")
    if current_blockers != 1:
        issues.append("publish KPI handoff should expose exactly one current blocker")
    for row in rows:
        label = str(row.get("step_id", "<missing>"))
        if not row.get("command") or not row.get("stop_condition"):
            issues.append(f"{label}: missing command or stop condition")
        if int(row.get("required_value", 0) or 0) < 1:
            issues.append(f"{label}: required value must be positive")
    return issues


def build_handoff() -> dict:
    rows = build_rows()
    issues = validate_rows(rows)
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "profileHandoff": str(PROFILE_HANDOFF.relative_to(ROOT)),
            "firstBatchPublishAction": str(FIRST_BATCH_PUBLISH.relative_to(ROOT)),
            "firstBatchPublicationPacket": str(FIRST_BATCH_PACKET.relative_to(ROOT)),
            "firstBatchKpiAction": str(FIRST_BATCH_KPI.relative_to(ROOT)),
            "firstBatchCompletionGate": str(FIRST_BATCH_COMPLETION.relative_to(ROOT)),
            "weeklyReviewPacket": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "stageTransitionMatrix": str(STAGE_MATRIX.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "completeRows": sum(1 for row in rows if row["status"] == "complete"),
            "currentBlockers": sum(1 for row in rows if row["status"] == "current_blocker"),
            "blockedUpstreamRows": sum(1 for row in rows if row["status"] == "blocked_upstream"),
            "publishedRows": int(load_json(FIRST_BATCH_PACKET).get("publishedRows", 0) or 0),
            "minimumKpiRows": int(load_json(FIRST_BATCH_PACKET).get("minimumKpiRows", 0) or 0),
            "readyForWeeklyReview": state(load_json(FIRST_BATCH_COMPLETION), "readyForWeeklyReview"),
            "issues": len(issues),
        },
        "policy": {
            "profileBeforePublish": True,
            "publicPostUrlBeforeKpi": True,
            "verifiedZeroBeforeDecision": True,
            "weeklyReviewBeforeCommerce": True,
        },
        "rows": rows,
        "issues": issues,
    }


def render_markdown(handoff: dict) -> str:
    metrics = handoff["metrics"]
    lines = [
        "# LoveTypes Publish to KPI Handoff",
        "",
        f"- 產生日期：{handoff['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- complete rows：{metrics['completeRows']}",
        f"- current blockers：{metrics['currentBlockers']}",
        f"- blocked upstream rows：{metrics['blockedUpstreamRows']}",
        f"- published rows：{metrics['publishedRows']} / 3",
        f"- minimum KPI rows：{metrics['minimumKpiRows']} / 3",
        f"- ready for weekly review：{metrics['readyForWeeklyReview']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rule",
        "",
        "- Profile handoff must open before first-batch publishing.",
        "- Public post URLs and traceable proof must exist before KPI writeback.",
        "- Zero KPI values are valid only after source checks.",
        "- Weekly review must open before changing commerce, Luna, affiliate, or paid CTA priority.",
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
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the publish-to-KPI handoff checklist for LoveTypes promotion.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    handoff = build_handoff()
    metrics = handoff["metrics"]
    print(f"promotion_publish_kpi_handoff_rows={metrics['rows']}")
    print(f"promotion_publish_kpi_handoff_complete={metrics['completeRows']}")
    print(f"promotion_publish_kpi_handoff_current_blockers={metrics['currentBlockers']}")
    print(f"promotion_publish_kpi_handoff_blocked_upstream={metrics['blockedUpstreamRows']}")
    print(f"promotion_publish_kpi_handoff_published_rows={metrics['publishedRows']}")
    print(f"promotion_publish_kpi_handoff_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_publish_kpi_handoff_ready_for_weekly={metrics['readyForWeeklyReview']}")
    print(f"promotion_publish_kpi_handoff_issues={metrics['issues']}")
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
        print(f"promotion_publish_kpi_handoff={output.relative_to(ROOT)}")
        print(f"promotion_publish_kpi_handoff_json={json_output.relative_to(ROOT)}")
        print(f"promotion_publish_kpi_handoff_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
