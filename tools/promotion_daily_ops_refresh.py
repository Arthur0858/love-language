#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
REFRESH_COMMANDS = [
    [sys.executable, "tools/promotion_sync_posting_queue.py"],
    [sys.executable, "tools/promotion_sync_kpi_tracker.py"],
    [sys.executable, "tools/promotion_metric_source_matrix.py"],
    [sys.executable, "tools/promotion_data_collection_sheet.py"],
    [sys.executable, "tools/promotion_platform_profile_setup.py"],
    [sys.executable, "tools/promotion_platform_profile_tracker.py"],
    [sys.executable, "tools/promotion_platform_kpi_tracker.py"],
    [sys.executable, "tools/promotion_profile_writeback.py", "check", "--write-playbook"],
    [sys.executable, "tools/promotion_profile_setup_runbook.py"],
    [sys.executable, "tools/promotion_launch_link_qa.py"],
    [sys.executable, "tools/promotion_profile_url_smoke.py"],
    [sys.executable, "tools/promotion_attribution_reconciliation.py"],
    [sys.executable, "tools/promotion_post_writeback.py", "check", "--write-playbook"],
    [sys.executable, "tools/promotion_publish_pack.py", "--all"],
    [sys.executable, "tools/promotion_launch_brief.py", "--all"],
    [sys.executable, "tools/promotion_week_execution_sheet.py", "--all"],
    [sys.executable, "tools/promotion_week_publication_runbook.py", "--week", "1"],
    [sys.executable, "tools/promotion_publishing_status.py"],
    [sys.executable, "tools/promotion_revenue_decision_matrix.py"],
    [sys.executable, "tools/promotion_weekly_summary.py"],
    [sys.executable, "tools/promotion_week_decision_gate.py"],
    [sys.executable, "tools/promotion_decision_readiness_checklist.py"],
    [sys.executable, "tools/promotion_decision_input_matrix.py"],
    [sys.executable, "tools/promotion_lead_intake_playbook.py"],
    [sys.executable, "tools/promotion_lead_writeback.py", "check", "--write-playbook"],
    [sys.executable, "tools/promotion_lead_request_proof_packet.py"],
    [sys.executable, "tools/promotion_lead_ops_action_sheet.py"],
    [sys.executable, "tools/promotion_lead_evidence_checklist.py"],
    [sys.executable, "tools/promotion_lead_magnet_inventory.py"],
    [sys.executable, "tools/promotion_lead_demand_gate.py"],
    [sys.executable, "tools/promotion_lead_tracker_summary.py"],
    [sys.executable, "tools/promotion_asset_backlog.py"],
    [sys.executable, "tools/promotion_asset_fulfillment_gate.py"],
    [sys.executable, "tools/promotion_offer_hypothesis_board.py"],
    [sys.executable, "tools/promotion_offer_experiment_plan.py"],
    [sys.executable, "tools/promotion_offer_experiment_queue.py"],
    [sys.executable, "tools/promotion_now_asset_pack.py"],
    [sys.executable, "tools/promotion_now_asset_queue.py"],
    [sys.executable, "tools/promotion_now_asset_briefs.py"],
    [sys.executable, "tools/promotion_week_asset_briefs.py", "--all"],
    [sys.executable, "tools/promotion_launch_command_center.py"],
    [sys.executable, "tools/promotion_launch_readiness_gate.py"],
    [sys.executable, "tools/promotion_evidence_ledger.py"],
    [sys.executable, "tools/promotion_profile_verification_packet.py"],
    [sys.executable, "tools/promotion_first_batch_publication_packet.py"],
    [sys.executable, "tools/promotion_profile_completion_gate.py"],
    [sys.executable, "tools/promotion_first_batch_completion_gate.py"],
    [sys.executable, "tools/promotion_first_batch_asset_qa.py"],
    [sys.executable, "tools/promotion_platform_account_identity_checklist.py"],
    [sys.executable, "tools/promotion_profile_setup_action_sheet.py"],
    [sys.executable, "tools/promotion_profile_quickstart.py"],
    [sys.executable, "tools/promotion_profile_link_readiness_packet.py"],
    [sys.executable, "tools/promotion_profile_proof_readiness_pack.py"],
    [sys.executable, "tools/promotion_first_batch_publish_action_sheet.py"],
    [sys.executable, "tools/promotion_first_batch_publish_readiness_pack.py"],
    [sys.executable, "tools/promotion_first_batch_publish_quickstart.py"],
    [sys.executable, "tools/promotion_first_batch_kpi_action_sheet.py"],
    [sys.executable, "tools/promotion_first_batch_kpi_quickstart.py"],
    [sys.executable, "tools/promotion_first_batch_publish_checklist.py"],
    [sys.executable, "tools/promotion_first_batch_kpi_checklist.py"],
    [sys.executable, "tools/promotion_profile_post_alignment_checklist.py"],
    [sys.executable, "tools/promotion_public_post_url_checklist.py"],
    [sys.executable, "tools/promotion_zero_kpi_evidence_checklist.py"],
    [sys.executable, "tools/promotion_post_ops_readiness_pack.py"],
    [sys.executable, "tools/promotion_first_batch_evidence_matrix.py"],
    [sys.executable, "tools/promotion_next_actions.py"],
    [sys.executable, "tools/promotion_weekly_review_packet.py"],
    [sys.executable, "tools/promotion_weekly_decision_evidence_checklist.py"],
    [sys.executable, "tools/promotion_weekly_review_action_sheet.py"],
    [sys.executable, "tools/promotion_weekly_review_quickstart.py"],
    [sys.executable, "tools/promotion_blocker_resolution_checklist.py"],
    [sys.executable, "tools/promotion_operator_handoff_packet.py"],
    [sys.executable, "tools/promotion_launch_ops_dashboard.py"],
    [sys.executable, "tools/promotion_launch_day_run_sheet.py"],
    [sys.executable, "tools/promotion_launch_exception_runbook.py"],
    [sys.executable, "tools/promotion_operation_proof_packet.py"],
    [sys.executable, "tools/promotion_operation_proof_templates.py"],
    [sys.executable, "tools/promotion_profile_evidence_checklist.py"],
    [sys.executable, "tools/promotion_launch_rehearsal_packet.py"],
    [sys.executable, "tools/promotion_master_gate.py"],
    [sys.executable, "tools/promotion_stage_transition_matrix.py"],
    [sys.executable, "tools/promotion_profile_publish_handoff.py"],
    [sys.executable, "tools/promotion_publish_kpi_handoff.py"],
    [sys.executable, "tools/promotion_weekly_lead_offer_handoff.py"],
    [sys.executable, "tools/promotion_lead_offer_quickstart.py"],
    [sys.executable, "tools/promotion_launch_clipboard.py"],
    [sys.executable, "tools/promotion_launch_quickstart.py"],
    [sys.executable, "tools/promotion_proof_rehearsal.py"],
]
DATE_ARG_PATTERN = re.compile(r"--(?:set-date|published-date) (\d{4}-\d{2}-\d{2})")


def today() -> str:
    return date.today().isoformat()


def target_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(PROMOTION_DIR.glob("*")):
        if path.suffix not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        if "產生日期" in text[:500] or '"generatedAt"' in text[:500]:
            files.append(path)
    return files


def read_generated_at(path: Path) -> str:
    if path.suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return ""
        return str(data.get("generatedAt", ""))
    for line in path.read_text(encoding="utf-8").splitlines()[:10]:
        if "產生日期" in line:
            return line.rsplit("：", 1)[-1].strip()
    return ""


def command_dates(path: Path) -> list[str]:
    return DATE_ARG_PATTERN.findall(path.read_text(encoding="utf-8"))


def inspect_docs(expected_date: str) -> dict:
    files = target_files()
    missing = [str(path.relative_to(ROOT)) for path in files if not path.exists()]
    stale_docs = []
    stale_commands = []
    for path in files:
        if not path.exists():
            continue
        generated_at = read_generated_at(path)
        if generated_at and generated_at != expected_date:
            stale_docs.append({
                "path": str(path.relative_to(ROOT)),
                "generatedAt": generated_at,
            })
        for command_date in command_dates(path):
            if command_date != expected_date:
                stale_commands.append({
                    "path": str(path.relative_to(ROOT)),
                    "commandDate": command_date,
                })
    return {
        "expectedDate": expected_date,
        "targetFiles": len(files),
        "missing": missing,
        "staleDocs": stale_docs,
        "staleCommands": stale_commands,
    }


def run_refresh() -> None:
    for command in REFRESH_COMMANDS:
        subprocess.run(command, cwd=ROOT, check=True)


def validate_inspection(inspection: dict, strict: bool) -> list[str]:
    issues: list[str] = []
    if inspection["missing"]:
        issues.append("missing daily ops docs: " + ", ".join(inspection["missing"]))
    if strict and inspection["staleDocs"]:
        issues.append(f"stale generatedAt docs: {len(inspection['staleDocs'])}")
    if strict and inspection["staleCommands"]:
        issues.append(f"stale date commands: {len(inspection['staleCommands'])}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh date-sensitive LoveTypes promotion operator packets.")
    parser.add_argument("--check", action="store_true", help="Inspect current docs without writing.")
    parser.add_argument("--strict-freshness", action="store_true", help="Fail when generated docs or embedded date commands are stale.")
    args = parser.parse_args()

    expected_date = today()
    if not args.check:
        run_refresh()
    inspection = inspect_docs(expected_date)
    issues = validate_inspection(inspection, strict=args.strict_freshness or not args.check)
    print(f"promotion_daily_ops_expected_date={inspection['expectedDate']}")
    print(f"promotion_daily_ops_target_files={inspection['targetFiles']}")
    print(f"promotion_daily_ops_missing_docs={len(inspection['missing'])}")
    print(f"promotion_daily_ops_stale_docs={len(inspection['staleDocs'])}")
    print(f"promotion_daily_ops_stale_commands={len(inspection['staleCommands'])}")
    print(f"promotion_daily_ops_refreshed={0 if args.check else 1}")
    print(f"promotion_daily_ops_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
