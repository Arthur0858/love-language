#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
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
from promotion_launch_day_run_sheet import build_run_sheet as build_launch_day_run_sheet  # noqa: E402
from promotion_launch_exception_runbook import build_runbook as build_launch_exception_runbook  # noqa: E402
from promotion_operation_proof_packet import build_packet as build_operation_proof_packet  # noqa: E402
from promotion_profile_publish_handoff import build_handoff as build_profile_publish_handoff  # noqa: E402
from promotion_publish_kpi_handoff import build_handoff as build_publish_kpi_handoff  # noqa: E402
from promotion_stage_transition_matrix import build_matrix  # noqa: E402
from promotion_weekly_lead_offer_handoff import build_handoff as build_weekly_lead_offer_handoff  # noqa: E402


SnapshotBuilder = Callable[[], dict]


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

    print(f"promotion_core_snapshot_checked={checked}")
    print(f"promotion_core_snapshot_fresh={fresh}")
    print(f"promotion_core_snapshot_missing={missing}")
    print(f"promotion_core_snapshot_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
