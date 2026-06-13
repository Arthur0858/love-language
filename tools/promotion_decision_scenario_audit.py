#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"

sys.path.insert(0, str(ROOT / "tools"))

from promotion_next_actions import build_actions  # noqa: E402
from promotion_revenue_decision_matrix import build_matrix  # noqa: E402
from promotion_week_decision_gate import build_gate  # noqa: E402
from promotion_weekly_summary import build_report  # noqa: E402


SCENARIOS = [
    {
        "id": "identity_only",
        "guardian": "iris",
        "metrics": {"site_clicks": 20, "quiz_starts": 12, "quiz_completions": 8, "guardian_result_clicks": 5},
        "expectedStage": "deepen_identity_asset",
        "expectedFocus": "deepen_identity_asset",
        "expectedGate": "deepenIdentityAsset",
    },
    {
        "id": "route_only",
        "guardian": "noah",
        "metrics": {"site_clicks": 20, "quiz_starts": 12, "quiz_completions": 8, "resources_clicks": 4},
        "expectedStage": "deepen_identity_asset",
        "expectedFocus": "deepen_identity_asset",
        "expectedGate": "deepenIdentityAsset",
    },
    {
        "id": "owned_lead",
        "guardian": "vivian",
        "metrics": {"site_clicks": 20, "quiz_starts": 12, "quiz_completions": 8, "supply_lead_requests": 2},
        "expectedStage": "build_owned_asset",
        "expectedFocus": "build_owned_asset",
        "expectedGate": "buildOwnedLeadAsset",
    },
    {
        "id": "paid_intent",
        "guardian": "claire",
        "metrics": {"site_clicks": 20, "quiz_starts": 12, "quiz_completions": 8, "affiliate_book_clicks": 2},
        "expectedStage": "test_soft_offer",
        "expectedFocus": "test_soft_offer",
        "expectedGate": "testSoftOffer",
    },
    {
        "id": "scale_quiz",
        "guardian": "dora",
        "metrics": {"site_clicks": 30, "quiz_starts": 20, "quiz_completions": 12},
        "expectedStage": "publish_guardian_variants",
        "expectedFocus": "scale_content",
        "expectedGate": "scaleContent",
    },
]
PROFILE_SCENARIOS = [
    {
        "id": "profile_identity_only",
        "metrics": {"profile_clicks": 30, "site_clicks": 20, "quiz_starts": 12, "quiz_completions": 8, "guardian_result_clicks": 5},
        "expectedProfileStage": "deepen_identity_asset",
        "expectedFocus": "deepen_identity_asset",
        "expectedGate": "deepenIdentityAsset",
    },
    {
        "id": "profile_owned_lead",
        "metrics": {"profile_clicks": 30, "site_clicks": 20, "quiz_starts": 12, "quiz_completions": 8, "contact_requests": 2},
        "expectedProfileStage": "build_owned_asset",
        "expectedFocus": "build_owned_asset",
        "expectedGate": "buildOwnedLeadAsset",
    },
    {
        "id": "profile_paid_intent",
        "metrics": {"profile_clicks": 30, "site_clicks": 20, "quiz_starts": 12, "quiz_completions": 8, "luna_pack_clicks": 2},
        "expectedProfileStage": "test_soft_offer",
        "expectedFocus": "test_soft_offer",
        "expectedGate": "testSoftOffer",
    },
]


def read_fields(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or [])


def load_tasks() -> list[dict]:
    data = json.loads(KIT_PATH.read_text(encoding="utf-8"))
    tasks = data.get("publishingTasks", [])
    return tasks if isinstance(tasks, list) else []


def task_for_guardian(tasks: list[dict], guardian: str) -> dict:
    for task in tasks:
        if task.get("guardianId") == guardian:
            return task
    raise RuntimeError(f"missing promotion task for guardian {guardian}")


def scenario_row(fields: list[str], task: dict, metrics: dict[str, int]) -> dict[str, str]:
    row = {field: "" for field in fields}
    row.update({
        "week": str(task.get("week", "1")),
        "slot": str(task.get("slot", "1")),
        "task_id": str(task.get("taskId", "")),
        "date": "2026-06-20",
        "platform": "youtube_shorts",
        "post_url": f"https://example.com/{task.get('taskId', 'post')}",
        "script_id": str(task.get("scriptId", "")),
        "guardian_id": str(task.get("guardianId", "")),
        "guardian_name": str(task.get("guardianName", "")),
        "content_angle": str(task.get("contentAngle", "")),
        "utm_content": str(task.get("utmContent", "")),
        "tracked_url": str(task.get("trackedUrl", "")),
        "views": "100",
    })
    for field, value in metrics.items():
        row[field] = str(value)
    return row


def profile_scenario_row(fields: list[str], metrics: dict[str, int]) -> dict[str, str]:
    row = {field: "" for field in fields}
    row.update({
        "platform": "youtube_shorts",
        "label": "YouTube Shorts",
        "profile_link": "https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio",
        "utm_source": "youtube",
        "utm_medium": "social_profile",
        "utm_campaign": "first_round_quiz_completion",
        "utm_content": "youtube_shorts_bio",
        "status": "live",
        "profile_link_set_date": "2026-06-20",
    })
    for field, value in metrics.items():
        row[field] = str(value)
    return row


def profile_fields() -> list[str]:
    return read_fields(PROFILE_TRACKER_PATH)


def assert_condition(issues: list[str], condition: bool, message: str) -> None:
    if not condition:
        issues.append(message)


def run_scenario(fields: list[str], profile_fieldnames: list[str], tasks: list[dict], scenario: dict) -> list[str]:
    issues: list[str] = []
    task = task_for_guardian(tasks, str(scenario["guardian"]))
    rows = [scenario_row(fields, task, scenario["metrics"])]
    profile_rows: list[dict[str, str]] = []

    weekly = build_report(fields, rows, tasks, profile_fieldnames, profile_rows)
    matrix = build_matrix(fields, rows, tasks, profile_fieldnames, profile_rows)
    actions = build_actions(fields, rows, tasks, profile_fieldnames, profile_rows)
    gate = build_gate(
        {"readyForWeeklyDecision": True},
        weekly,
        matrix,
        actions,
    )

    guardian_row = next((item for item in matrix.get("guardians", []) if item.get("guardianId") == scenario["guardian"]), {})
    expected_stage = scenario["expectedStage"]
    expected_focus = scenario["expectedFocus"]
    expected_gate = scenario["expectedGate"]
    label = scenario["id"]

    assert_condition(
        issues,
        guardian_row.get("stage") == expected_stage,
        f"{label}: expected matrix stage {expected_stage}, got {guardian_row.get('stage')}",
    )
    assert_condition(
        issues,
        gate.get("recommendedFocus") == expected_focus,
        f"{label}: expected gate focus {expected_focus}, got {gate.get('recommendedFocus')}",
    )
    assert_condition(
        issues,
        bool(gate.get("gates", {}).get(expected_gate)),
        f"{label}: expected gate {expected_gate} to pass",
    )
    assert_condition(
        issues,
        not gate.get("blockers"),
        f"{label}: expected no gate blockers, got {gate.get('blockers')}",
    )

    identity = int(weekly.get("computedTotals", {}).get("identityInterest", 0) or 0)
    route = int(weekly.get("computedTotals", {}).get("routeInterest", 0) or 0)
    identity_route = int(weekly.get("computedTotals", {}).get("identityRouteInterest", 0) or 0)
    assert_condition(
        issues,
        identity_route == identity + route,
        f"{label}: identityRouteInterest should equal identityInterest plus routeInterest",
    )

    if label == "identity_only":
        assert_condition(issues, identity > 0, f"{label}: identity interest should be positive")
        assert_condition(issues, route == 0, f"{label}: route interest should remain zero")
        assert_condition(
            issues,
            "guardian_result_clicks" in matrix.get("identityFields", []),
            f"{label}: matrix should declare guardian_result_clicks as identity field",
        )
    if label == "paid_intent":
        assert_condition(
            issues,
            not gate.get("gates", {}).get("buildOwnedLeadAsset"),
            f"{label}: paid intent should not be misrouted to owned lead gate",
        )
    if label == "owned_lead":
        assert_condition(
            issues,
            not gate.get("gates", {}).get("testSoftOffer"),
            f"{label}: owned lead should not be misrouted to soft offer gate",
        )
    return issues


def run_profile_scenario(fields: list[str], profile_fieldnames: list[str], tasks: list[dict], scenario: dict) -> list[str]:
    issues: list[str] = []
    rows: list[dict[str, str]] = []
    profile_rows = [profile_scenario_row(profile_fieldnames, scenario["metrics"])]

    weekly = build_report(fields, rows, tasks, profile_fieldnames, profile_rows)
    matrix = build_matrix(fields, rows, tasks, profile_fieldnames, profile_rows)
    actions = build_actions(fields, rows, tasks, profile_fieldnames, profile_rows)
    gate = build_gate(
        {"readyForWeeklyDecision": True},
        weekly,
        matrix,
        actions,
    )

    label = scenario["id"]
    expected_profile_stage = scenario["expectedProfileStage"]
    expected_focus = scenario["expectedFocus"]
    expected_gate = scenario["expectedGate"]
    profile_intent = matrix.get("platformProfileIntent", {})

    assert_condition(
        issues,
        profile_intent.get("stage") == expected_profile_stage,
        f"{label}: expected platform profile stage {expected_profile_stage}, got {profile_intent.get('stage')}",
    )
    assert_condition(
        issues,
        profile_intent.get("scope") == "platform_profile_unassigned",
        f"{label}: platform profile intent should remain unassigned",
    )
    assert_condition(
        issues,
        gate.get("recommendedFocus") == expected_focus,
        f"{label}: expected gate focus {expected_focus}, got {gate.get('recommendedFocus')}",
    )
    assert_condition(
        issues,
        bool(gate.get("gates", {}).get(expected_gate)),
        f"{label}: expected gate {expected_gate} to pass",
    )
    assert_condition(
        issues,
        not gate.get("blockers"),
        f"{label}: expected no gate blockers, got {gate.get('blockers')}",
    )

    assigned_guardian_stages = {
        item.get("guardianId"): item.get("stage")
        for item in matrix.get("guardians", [])
        if item.get("stage") != "collect_signal"
    }
    assert_condition(
        issues,
        not assigned_guardian_stages,
        f"{label}: profile-only data should not assign guardian stages, got {assigned_guardian_stages}",
    )

    identity = int(weekly.get("computedTotals", {}).get("identityInterest", 0) or 0)
    route = int(weekly.get("computedTotals", {}).get("routeInterest", 0) or 0)
    identity_route = int(weekly.get("computedTotals", {}).get("identityRouteInterest", 0) or 0)
    assert_condition(
        issues,
        identity_route == identity + route,
        f"{label}: identityRouteInterest should equal identityInterest plus routeInterest",
    )
    return issues


def main() -> int:
    fields = read_fields(TRACKER_PATH)
    profile_fieldnames = profile_fields()
    tasks = load_tasks()
    issues: list[str] = []
    scenarios_checked = 0
    profile_scenarios_checked = 0
    for scenario in SCENARIOS:
        scenario_issues = run_scenario(fields, profile_fieldnames, tasks, scenario)
        issues.extend(scenario_issues)
        scenarios_checked += 1
    for scenario in PROFILE_SCENARIOS:
        scenario_issues = run_profile_scenario(fields, profile_fieldnames, tasks, scenario)
        issues.extend(scenario_issues)
        profile_scenarios_checked += 1

    print(f"promotion_decision_scenarios_checked={scenarios_checked}")
    print(f"promotion_decision_profile_scenarios_checked={profile_scenarios_checked}")
    print(f"promotion_decision_scenario_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
