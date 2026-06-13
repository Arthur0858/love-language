#!/usr/bin/env python3
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import promotion_offer_experiment_plan as offer_plan
import promotion_offer_experiment_queue as offer_queue


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
MATRIX_PATH = PROMOTION_DIR / "revenue-decision-matrix.json"
GATE_PATH = PROMOTION_DIR / "week-decision-gate.json"
BOARD_PATH = PROMOTION_DIR / "offer-hypothesis-board.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def matrix_with_iris_metrics(metrics: dict[str, int]) -> dict:
    matrix = load_json(MATRIX_PATH)
    for row in matrix.get("guardians", []):
        if row.get("guardianId") == "iris":
            row["metrics"] = {**row.get("metrics", {}), **metrics}
    matrix.setdefault("dataState", {})["emptyDataMode"] = False
    return matrix


def gate_payload(*, blocked: bool) -> dict:
    gate = load_json(GATE_PATH)
    gate["blockers"] = ["scenario blocker"] if blocked else []
    gate.setdefault("safety", {})["emptyDataFailClosed"] = blocked
    return gate


def ready_count(plan: dict, experiment_type: str) -> int:
    return sum(
        1
        for row in plan.get("experiments", [])
        if row.get("guardianId") == "iris"
        and row.get("experimentType") == experiment_type
        and row.get("status") == "READY"
    )


def build_scenario(metrics: dict[str, int], *, blocked: bool) -> tuple[dict, dict]:
    plan = offer_plan.build_plan(matrix_with_iris_metrics(metrics), gate_payload(blocked=blocked), deepcopy(load_json(BOARD_PATH)))
    queue = offer_queue.build_queue(plan)
    return plan, queue


def main() -> int:
    issues: list[str] = []
    blocked_plan, blocked_queue = build_scenario(
        {"quiz_completions": 10, "free_keepsake_downloads": 2, "keepsake_clicks": 0},
        blocked=True,
    )
    low_quiz_plan, low_quiz_queue = build_scenario(
        {"quiz_completions": 9, "free_keepsake_downloads": 2, "keepsake_clicks": 0},
        blocked=False,
    )
    ready_plan, ready_queue = build_scenario(
        {"quiz_completions": 10, "free_keepsake_downloads": 2, "keepsake_clicks": 0},
        blocked=False,
    )
    luna_plan, luna_queue = build_scenario(
        {"quiz_completions": 10, "luna_pack_clicks": 1, "luna_clicks": 0},
        blocked=False,
    )

    checks = {
        "blocked_gate_holds_ready": blocked_plan["readyExperiments"] == 0 and blocked_queue["readyRows"] == 0,
        "low_quiz_holds_ready": low_quiz_plan["readyExperiments"] == 0 and low_quiz_queue["readyRows"] == 0,
        "identity_ready_threshold": ready_count(ready_plan, "identity_save") == 1,
        "identity_queue_ready_steps": ready_queue["readyRows"] == 4,
        "luna_ready_threshold": ready_count(luna_plan, "luna_soft_offer") == 1,
        "luna_queue_ready_steps": luna_queue["readyRows"] == 4,
    }
    for name, ok in checks.items():
        if not ok:
            issues.append(name)

    print(f"promotion_offer_experiment_scenario_blocked_ready={blocked_plan['readyExperiments']}")
    print(f"promotion_offer_experiment_scenario_blocked_queue_ready={blocked_queue['readyRows']}")
    print(f"promotion_offer_experiment_scenario_low_quiz_ready={low_quiz_plan['readyExperiments']}")
    print(f"promotion_offer_experiment_scenario_identity_ready={ready_count(ready_plan, 'identity_save')}")
    print(f"promotion_offer_experiment_scenario_identity_queue_ready={ready_queue['readyRows']}")
    print(f"promotion_offer_experiment_scenario_luna_ready={ready_count(luna_plan, 'luna_soft_offer')}")
    print(f"promotion_offer_experiment_scenario_luna_queue_ready={luna_queue['readyRows']}")
    print(f"promotion_offer_experiment_scenario_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
