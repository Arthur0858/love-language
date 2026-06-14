#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from io import StringIO
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
sys.path.insert(0, str(TOOLS))

from promotion_master_gate import build_gate  # noqa: E402
from promotion_profile_completion_gate import build_gate as build_profile_completion_gate  # noqa: E402
from promotion_first_batch_completion_gate import build_gate as build_first_batch_completion_gate  # noqa: E402
from promotion_weekly_review_packet import build_packet as build_weekly_review_packet  # noqa: E402
from promotion_weekly_review_packet import validate_packet as validate_weekly_review_packet  # noqa: E402
from promotion_lead_demand_gate import build_gate as build_lead_demand_gate  # noqa: E402
from promotion_offer_experiment_plan import build_plan as build_offer_experiment_plan  # noqa: E402
from promotion_offer_experiment_plan import load_json as load_offer_json  # noqa: E402
from promotion_operator_handoff_packet import build_handoff as build_operator_handoff  # noqa: E402
from promotion_operator_handoff_packet import validate_handoff as validate_operator_handoff  # noqa: E402
from promotion_launch_clipboard import build_clipboard as build_launch_clipboard  # noqa: E402
from promotion_launch_ops_dashboard import build_dashboard as build_launch_ops_dashboard  # noqa: E402
from promotion_launch_ops_dashboard import render_markdown as render_launch_ops_dashboard_markdown  # noqa: E402
from promotion_launch_day_run_sheet import build_run_sheet as build_launch_day_run_sheet  # noqa: E402
from promotion_launch_day_run_sheet import render_markdown as render_launch_day_run_sheet_markdown  # noqa: E402
from promotion_launch_exception_runbook import build_runbook as build_launch_exception_runbook  # noqa: E402
from promotion_launch_exception_runbook import render_markdown as render_launch_exception_runbook_markdown  # noqa: E402
from promotion_operation_proof_packet import build_packet as build_operation_proof_packet  # noqa: E402
from promotion_proof_rehearsal import build_rehearsal as build_proof_rehearsal  # noqa: E402
from promotion_profile_publish_handoff import build_handoff as build_profile_publish_handoff  # noqa: E402
from promotion_profile_publish_handoff import CSV_FIELDS as PROFILE_PUBLISH_CSV_FIELDS  # noqa: E402
from promotion_profile_publish_handoff import render_markdown as render_profile_publish_handoff_markdown  # noqa: E402
from promotion_publish_kpi_handoff import build_handoff as build_publish_kpi_handoff  # noqa: E402
from promotion_publish_kpi_handoff import CSV_FIELDS as PUBLISH_KPI_CSV_FIELDS  # noqa: E402
from promotion_publish_kpi_handoff import render_markdown as render_publish_kpi_handoff_markdown  # noqa: E402
from promotion_stage_transition_matrix import build_matrix  # noqa: E402
from promotion_stage_transition_matrix import CSV_FIELDS as STAGE_TRANSITION_CSV_FIELDS  # noqa: E402
from promotion_stage_transition_matrix import render_markdown as render_stage_transition_markdown  # noqa: E402
from promotion_stage_transition_matrix import validate_matrix as validate_stage_transition_matrix  # noqa: E402
from promotion_weekly_lead_offer_handoff import build_handoff as build_weekly_lead_offer_handoff  # noqa: E402
from promotion_weekly_lead_offer_handoff import CSV_FIELDS as WEEKLY_LEAD_OFFER_CSV_FIELDS  # noqa: E402
from promotion_weekly_lead_offer_handoff import render_markdown as render_weekly_lead_offer_handoff_markdown  # noqa: E402


SnapshotBuilder = Callable[[], dict]
CsvBuilder = Callable[[], tuple[list[str], list[dict[str, object]]]]
MdBuilder = Callable[[], str]


def build_weekly_review_snapshot() -> dict:
    packet = build_weekly_review_packet()
    return {**packet, "issues": validate_weekly_review_packet(packet)}


def build_offer_experiment_snapshot() -> dict:
    from promotion_offer_experiment_plan import GATE_PATH, MATRIX_PATH, OFFER_BOARD_PATH  # noqa: E402

    return build_offer_experiment_plan(
        load_offer_json(MATRIX_PATH),
        load_offer_json(GATE_PATH),
        load_offer_json(OFFER_BOARD_PATH),
    )


def build_operator_handoff_snapshot() -> dict:
    handoff = build_operator_handoff()
    return {**handoff, "issues": validate_operator_handoff(handoff)}


def rows_csv(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return buffer.getvalue()


def read_csv_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def stage_transition_csv_rows() -> tuple[list[str], list[dict[str, object]]]:
    rows = build_matrix()["rows"]
    return list(STAGE_TRANSITION_CSV_FIELDS), [
        {
            "from_stage": row["fromStage"],
            "to_stage": row["toStage"],
            "gate_id": row["gateId"],
            "status": row["status"],
            "current_value": row["currentValue"],
            "required_value": row["requiredValue"],
            "active_stage": row["activeStage"],
            "release_condition": row["releaseCondition"],
            "next_command": row["nextCommand"],
            "fallback_action": row["fallbackAction"],
            "blocker": row["blocker"],
        }
        for row in rows
    ]


def profile_publish_csv_rows() -> tuple[list[str], list[dict[str, object]]]:
    return list(PROFILE_PUBLISH_CSV_FIELDS), build_profile_publish_handoff()["rows"]


def publish_kpi_csv_rows() -> tuple[list[str], list[dict[str, object]]]:
    return list(PUBLISH_KPI_CSV_FIELDS), build_publish_kpi_handoff()["rows"]


def weekly_lead_offer_csv_rows() -> tuple[list[str], list[dict[str, object]]]:
    return list(WEEKLY_LEAD_OFFER_CSV_FIELDS), build_weekly_lead_offer_handoff()["rows"]


def launch_ops_dashboard_csv_rows() -> tuple[list[str], list[dict[str, object]]]:
    return ["area", "status", "ready", "blocked", "next_action", "evidence", "safety"], build_launch_ops_dashboard()["rows"]


def launch_day_run_sheet_csv_rows() -> tuple[list[str], list[dict[str, object]]]:
    fields = ["order", "phase", "platform", "task", "status", "action", "check_command", "write_command", "success_signal", "stop_condition"]
    return fields, build_launch_day_run_sheet()["rows"]


def launch_exception_runbook_csv_rows() -> tuple[list[str], list[dict[str, object]]]:
    fields = ["id", "phase", "severity", "status", "trigger", "stop", "recovery", "source", "operatorAction"]
    return fields, build_launch_exception_runbook()["rows"]


def stage_transition_md() -> str:
    matrix = build_matrix()
    return render_stage_transition_markdown(matrix, validate_stage_transition_matrix(matrix))


def profile_publish_md() -> str:
    return render_profile_publish_handoff_markdown(build_profile_publish_handoff())


def publish_kpi_md() -> str:
    return render_publish_kpi_handoff_markdown(build_publish_kpi_handoff())


def weekly_lead_offer_md() -> str:
    return render_weekly_lead_offer_handoff_markdown(build_weekly_lead_offer_handoff())


def launch_ops_dashboard_md() -> str:
    return render_launch_ops_dashboard_markdown(build_launch_ops_dashboard())


def launch_day_run_sheet_md() -> str:
    return render_launch_day_run_sheet_markdown(build_launch_day_run_sheet())


def launch_exception_runbook_md() -> str:
    return render_launch_exception_runbook_markdown(build_launch_exception_runbook())


SNAPSHOTS: tuple[tuple[str, Path, SnapshotBuilder], ...] = (
    ("profile_completion_gate", PROMOTION_DIR / "profile-completion-gate.json", build_profile_completion_gate),
    ("first_batch_completion_gate", PROMOTION_DIR / "first-batch-completion-gate.json", build_first_batch_completion_gate),
    ("weekly_review_packet", PROMOTION_DIR / "weekly-review-packet.json", build_weekly_review_snapshot),
    ("lead_demand_gate", PROMOTION_DIR / "lead-demand-gate.json", build_lead_demand_gate),
    ("offer_experiment_plan", PROMOTION_DIR / "offer-experiment-plan.json", build_offer_experiment_snapshot),
    ("master_gate", PROMOTION_DIR / "master-gate.json", build_gate),
    ("stage_transition_matrix", PROMOTION_DIR / "stage-transition-matrix.json", build_matrix),
    ("profile_publish_handoff", PROMOTION_DIR / "profile-publish-handoff.json", build_profile_publish_handoff),
    ("publish_kpi_handoff", PROMOTION_DIR / "publish-kpi-handoff.json", build_publish_kpi_handoff),
    ("weekly_lead_offer_handoff", PROMOTION_DIR / "weekly-lead-offer-handoff.json", build_weekly_lead_offer_handoff),
    ("operator_handoff_packet", PROMOTION_DIR / "operator-handoff-packet.json", build_operator_handoff_snapshot),
    ("launch_clipboard", PROMOTION_DIR / "launch-clipboard.json", build_launch_clipboard),
    ("launch_ops_dashboard", PROMOTION_DIR / "launch-ops-dashboard.json", build_launch_ops_dashboard),
    ("launch_day_run_sheet", PROMOTION_DIR / "launch-day-run-sheet.json", build_launch_day_run_sheet),
    ("launch_exception_runbook", PROMOTION_DIR / "launch-exception-runbook.json", build_launch_exception_runbook),
    ("operation_proof_packet", PROMOTION_DIR / "operation-proof-packet.json", build_operation_proof_packet),
    ("proof_rehearsal", PROMOTION_DIR / "proof-rehearsal.json", build_proof_rehearsal),
)

CSV_SNAPSHOTS: tuple[tuple[str, Path, CsvBuilder], ...] = (
    ("stage_transition_matrix_csv", PROMOTION_DIR / "stage-transition-matrix.csv", stage_transition_csv_rows),
    ("profile_publish_handoff_csv", PROMOTION_DIR / "profile-publish-handoff.csv", profile_publish_csv_rows),
    ("publish_kpi_handoff_csv", PROMOTION_DIR / "publish-kpi-handoff.csv", publish_kpi_csv_rows),
    ("weekly_lead_offer_handoff_csv", PROMOTION_DIR / "weekly-lead-offer-handoff.csv", weekly_lead_offer_csv_rows),
    ("launch_ops_dashboard_csv", PROMOTION_DIR / "launch-ops-dashboard.csv", launch_ops_dashboard_csv_rows),
    ("launch_day_run_sheet_csv", PROMOTION_DIR / "launch-day-run-sheet.csv", launch_day_run_sheet_csv_rows),
    ("launch_exception_runbook_csv", PROMOTION_DIR / "launch-exception-runbook.csv", launch_exception_runbook_csv_rows),
)

MD_SNAPSHOTS: tuple[tuple[str, Path, MdBuilder], ...] = (
    ("stage_transition_matrix_md", PROMOTION_DIR / "stage-transition-matrix.md", stage_transition_md),
    ("profile_publish_handoff_md", PROMOTION_DIR / "profile-publish-handoff.md", profile_publish_md),
    ("publish_kpi_handoff_md", PROMOTION_DIR / "publish-kpi-handoff.md", publish_kpi_md),
    ("weekly_lead_offer_handoff_md", PROMOTION_DIR / "weekly-lead-offer-handoff.md", weekly_lead_offer_md),
    ("launch_ops_dashboard_md", PROMOTION_DIR / "launch-ops-dashboard.md", launch_ops_dashboard_md),
    ("launch_day_run_sheet_md", PROMOTION_DIR / "launch-day-run-sheet.md", launch_day_run_sheet_md),
    ("launch_exception_runbook_md", PROMOTION_DIR / "launch-exception-runbook.md", launch_exception_runbook_md),
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def normalize(payload: dict) -> dict:
    normalized = dict(payload)
    normalized.pop("generatedAt", None)
    return normalized


def main() -> int:
    issues: list[str] = []
    checked = 0
    fresh = 0
    missing = 0

    for label, path, builder in SNAPSHOTS:
        checked += 1
        if not path.exists():
            missing += 1
            issues.append(f"{label}: missing snapshot {path.relative_to(ROOT)}")
            continue
        try:
            current = normalize(load_json(path))
        except json.JSONDecodeError as error:
            issues.append(f"{label}: invalid JSON {path.relative_to(ROOT)}: {error}")
            continue
        rebuilt = normalize(builder())
        if current == rebuilt:
            fresh += 1
        else:
            issues.append(f"{label}: generated snapshot is stale relative to current source data")

    for label, path, builder in CSV_SNAPSHOTS:
        checked += 1
        if not path.exists():
            missing += 1
            issues.append(f"{label}: missing snapshot {path.relative_to(ROOT)}")
            continue
        fieldnames, rows = builder()
        rebuilt = rows_csv(fieldnames, rows)
        current = read_csv_text(path)
        if current == rebuilt:
            fresh += 1
        else:
            issues.append(f"{label}: generated CSV snapshot is stale relative to current source data")

    for label, path, builder in MD_SNAPSHOTS:
        checked += 1
        if not path.exists():
            missing += 1
            issues.append(f"{label}: missing snapshot {path.relative_to(ROOT)}")
            continue
        rebuilt = builder()
        current = path.read_text(encoding="utf-8")
        if current == rebuilt:
            fresh += 1
        else:
            issues.append(f"{label}: generated Markdown snapshot is stale relative to current source data")

    print(f"promotion_core_snapshot_checked={checked}")
    print(f"promotion_core_snapshot_fresh={fresh}")
    print(f"promotion_core_snapshot_missing={missing}")
    print(f"promotion_core_snapshot_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
