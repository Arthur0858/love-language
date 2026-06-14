#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import os
import socket
import subprocess
import sys
import time
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_TOOLS = [
    "tools/generate_multilingual_site.py",
    "tools/site_quality_audit.py",
    "tools/check_generated_fresh.py",
    "tools/content_uniqueness_audit.py",
    "tools/multilingual_route_audit.py",
    "tools/guardian_conversion_audit.py",
    "tools/affiliate_locale_audit.py",
    "tools/accessibility_audit.py",
    "tools/image_asset_audit.py",
    "tools/performance_budget_audit.py",
    "tools/promotion_publish_pack.py",
    "tools/promotion_next_actions.py",
    "tools/promotion_sync_kpi_tracker.py",
    "tools/promotion_metric_source_matrix.py",
    "tools/promotion_data_collection_sheet.py",
    "tools/promotion_kpi_schema_audit.py",
    "tools/promotion_kpi_attribution_health_report.py",
    "tools/promotion_sync_posting_queue.py",
    "tools/promotion_platform_kpi_tracker.py",
    "tools/promotion_post_writeback.py",
    "tools/promotion_post_text_import.py",
    "tools/promotion_post_scaffold_writeback_safety.py",
    "tools/promotion_first_batch_publish_dry_run.py",
    "tools/promotion_placeholder_url_safety_audit.py",
    "tools/promotion_proof_note_policy.py",
    "tools/promotion_proof_note_safety_audit.py",
    "tools/promotion_refresh.py",
    "tools/promotion_temporal_writeback_safety_audit.py",
    "tools/promotion_evidence_ledger.py",
    "tools/promotion_first_batch_publication_packet.py",
    "tools/promotion_first_batch_completion_gate.py",
    "tools/promotion_first_batch_asset_qa.py",
    "tools/promotion_first_batch_publish_checklist.py",
    "tools/promotion_first_batch_kpi_checklist.py",
    "tools/promotion_profile_post_alignment_checklist.py",
    "tools/promotion_public_post_url_checklist.py",
    "tools/promotion_zero_kpi_evidence_checklist.py",
    "tools/promotion_post_ops_readiness_pack.py",
    "tools/promotion_post_proof_handoff_pack.py",
    "tools/promotion_first_batch_evidence_matrix.py",
    "tools/promotion_publishing_status.py",
    "tools/promotion_kpi_writeback_consistency_audit.py",
    "tools/promotion_writeback_flow_audit.py",
    "tools/promotion_writeback_refresh_audit.py",
    "tools/promotion_launch_brief.py",
    "tools/promotion_revenue_decision_matrix.py",
    "tools/promotion_week_decision_gate.py",
    "tools/promotion_decision_readiness_checklist.py",
    "tools/promotion_decision_input_matrix.py",
    "tools/promotion_lead_intake_playbook.py",
    "tools/promotion_lead_form_audit.py",
    "tools/promotion_lead_form_importability_audit.py",
    "tools/promotion_lead_form_health_report.py",
    "tools/promotion_lead_text_import.py",
    "tools/promotion_lead_writeback.py",
    "tools/promotion_lead_data_minimization_audit.py",
    "tools/promotion_lead_privacy_safety_audit.py",
    "tools/promotion_lead_request_proof_packet.py",
    "tools/promotion_lead_ops_action_sheet.py",
    "tools/promotion_lead_evidence_checklist.py",
    "tools/promotion_lead_magnet_inventory.py",
    "tools/promotion_lead_demand_gate.py",
    "tools/promotion_lead_tracker_summary.py",
    "tools/promotion_lead_demand_scenario_audit.py",
    "tools/promotion_offer_hypothesis_board.py",
    "tools/promotion_offer_experiment_plan.py",
    "tools/promotion_offer_experiment_queue.py",
    "tools/promotion_offer_experiment_scenario_audit.py",
    "tools/promotion_asset_backlog.py",
    "tools/promotion_asset_fulfillment_gate.py",
    "tools/promotion_asset_fulfillment_dry_run.py",
    "tools/promotion_asset_commerce_bridge_audit.py",
    "tools/promotion_trust_commerce_safety_audit.py",
    "tools/promotion_platform_profile_setup.py",
    "tools/promotion_platform_profile_tracker.py",
    "tools/promotion_profile_writeback.py",
    "tools/promotion_profile_text_import.py",
    "tools/promotion_profile_scaffold_writeback_safety.py",
    "tools/promotion_profile_setup_runbook.py",
    "tools/promotion_profile_verification_packet.py",
    "tools/promotion_profile_completion_gate.py",
    "tools/promotion_week_execution_sheet.py",
    "tools/promotion_platform_account_identity_checklist.py",
    "tools/promotion_profile_setup_action_sheet.py",
    "tools/promotion_profile_quickstart.py",
    "tools/promotion_profile_link_readiness_packet.py",
    "tools/promotion_profile_proof_readiness_pack.py",
    "tools/promotion_profile_proof_capture_quickstart.py",
    "tools/promotion_profile_batch_import.py",
    "tools/promotion_profile_setup_handoff_pack.py",
    "tools/promotion_profile_writeback_closure_quickstart.py",
    "tools/promotion_post_batch_import.py",
    "tools/promotion_launch_proof_control_sheet.py",
    "tools/promotion_profile_unlock_rehearsal.py",
    "tools/promotion_profile_setup_dry_run.py",
    "tools/promotion_launch_sequence_dry_run.py",
    "tools/promotion_first_batch_publish_action_sheet.py",
    "tools/promotion_first_batch_publish_readiness_pack.py",
    "tools/promotion_first_batch_launch_handoff.py",
    "tools/promotion_first_batch_publish_quickstart.py",
    "tools/promotion_first_batch_publish_closure_quickstart.py",
    "tools/promotion_first_batch_kpi_action_sheet.py",
    "tools/promotion_first_batch_kpi_quickstart.py",
    "tools/promotion_first_batch_kpi_closure_quickstart.py",
    "tools/promotion_kpi_zero_source_rehearsal.py",
    "tools/promotion_week_publication_runbook.py",
    "tools/promotion_now_asset_pack.py",
    "tools/promotion_now_asset_queue.py",
    "tools/promotion_now_asset_briefs.py",
    "tools/promotion_week_asset_briefs.py",
    "tools/promotion_launch_command_center.py",
    "tools/promotion_ops_closure_audit.py",
    "tools/promotion_operation_proof_packet.py",
    "tools/promotion_operation_proof_templates.py",
    "tools/promotion_profile_evidence_checklist.py",
    "tools/promotion_launch_rehearsal_packet.py",
    "tools/promotion_launch_readiness_gate.py",
    "tools/promotion_launch_link_qa.py",
    "tools/promotion_profile_url_smoke.py",
    "tools/promotion_attribution_reconciliation.py",
    "tools/promotion_weekly_summary.py",
    "tools/promotion_weekly_review_packet.py",
    "tools/promotion_weekly_decision_evidence_checklist.py",
    "tools/promotion_weekly_review_action_sheet.py",
    "tools/promotion_weekly_review_quickstart.py",
    "tools/promotion_blocker_resolution_checklist.py",
    "tools/promotion_launch_blocker_digest.py",
    "tools/promotion_operator_handoff_packet.py",
    "tools/promotion_launch_ops_dashboard.py",
    "tools/promotion_launch_day_run_sheet.py",
    "tools/promotion_launch_exception_runbook.py",
    "tools/promotion_operator_import_template_audit.py",
    "tools/promotion_operator_handoff_consistency_audit.py",
    "tools/promotion_empty_data_safety_audit.py",
    "tools/promotion_daily_ops_refresh.py",
    "tools/promotion_master_gate.py",
    "tools/promotion_stage_transition_matrix.py",
    "tools/promotion_core_snapshot_consistency_audit.py",
    "tools/promotion_profile_publish_handoff.py",
    "tools/promotion_publish_kpi_handoff.py",
    "tools/promotion_weekly_lead_offer_handoff.py",
    "tools/promotion_lead_offer_quickstart.py",
    "tools/promotion_lead_intake_closure_quickstart.py",
    "tools/promotion_launch_clipboard.py",
    "tools/promotion_launch_quickstart.py",
    "tools/promotion_launch_execution_closure_quickstart.py",
    "tools/promotion_proof_rehearsal.py",
    "tools/promotion_proof_import_closure_quickstart.py",
    "tools/promotion_operator_next_action_closure_quickstart.py",
    "tools/promotion_decision_scenario_audit.py",
    "tools/build_guardian_card_assets.py",
    "tools/public_deploy_smoke.py",
    "tools/public_launch_link_smoke.py",
    "tools/public_headers_smoke.py",
    "tools/public_sitemap_smoke.py",
    "tools/site_health_config_audit.py",
    "tools/site_health_summary.py",
    "tools/deploy_cloudflare_pages.py",
    "tools/deploy_manifest_audit.py",
]


def run_step(name: str, command: list[str], env: dict[str, str] | None = None) -> None:
    print(f"== {name} ==", flush=True)
    subprocess.run(command, cwd=ROOT, check=True, env=env)


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(port: int) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"Local preview server did not start on port {port}")


def find_node() -> str:
    if os.environ.get("NODE_BIN"):
        return os.environ["NODE_BIN"]

    candidates = [
        shutil.which("node"),
        "/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    raise RuntimeError("Node.js was not found. Install Node.js or set NODE_BIN.")


@contextlib.contextmanager
def local_preview_server():
    port = find_free_port()
    print(f"== local preview server http://127.0.0.1:{port} ==", flush=True)
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        wait_for_server(port)
        yield f"http://127.0.0.1:{port}"
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LoveTypes pre-deploy quality checks.")
    parser.add_argument(
        "--visual",
        action="store_true",
        help="Also run tools/visual_check.mjs. Start a local server or set BASE_URL first.",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="BASE_URL for the optional visual check. If omitted with --visual, a temporary local server is started.",
    )
    parser.add_argument(
        "--visual-only",
        action="store_true",
        help="Run only tools/visual_check.mjs, starting a temporary local server unless --base-url is set.",
    )
    args = parser.parse_args()

    if not args.visual_only:
        run_step("python compile", [sys.executable, "-m", "py_compile", *PYTHON_TOOLS])
        run_step("generated freshness", [sys.executable, "tools/check_generated_fresh.py"])
        run_step("site quality audit", [sys.executable, "tools/site_quality_audit.py"])
        run_step("content uniqueness audit", [sys.executable, "tools/content_uniqueness_audit.py"])
        run_step("multilingual route audit", [sys.executable, "tools/multilingual_route_audit.py"])
        run_step("guardian conversion audit", [sys.executable, "tools/guardian_conversion_audit.py"])
        run_step("affiliate locale audit", [sys.executable, "tools/affiliate_locale_audit.py"])
        run_step("accessibility audit", [sys.executable, "tools/accessibility_audit.py"])
        run_step("image asset audit", [sys.executable, "tools/image_asset_audit.py"])
        run_step("performance budget audit", [sys.executable, "tools/performance_budget_audit.py"])
        run_step("promotion spreadsheet workbook", [find_node(), "tools/build_promotion_spreadsheet.mjs", "--check"])
        run_step("promotion publish pack", [sys.executable, "tools/promotion_publish_pack.py", "--all", "--check"])
        run_step("promotion kpi tracker", [sys.executable, "tools/promotion_sync_kpi_tracker.py", "--check"])
        run_step("promotion metric source matrix", [sys.executable, "tools/promotion_metric_source_matrix.py", "--check"])
        run_step("promotion data collection sheet", [sys.executable, "tools/promotion_data_collection_sheet.py", "--check"])
        run_step("promotion kpi schema audit", [sys.executable, "tools/promotion_kpi_schema_audit.py"])
        run_step("promotion KPI attribution health report", [sys.executable, "tools/promotion_kpi_attribution_health_report.py", "--check"])
        run_step("promotion posting queue", [sys.executable, "tools/promotion_sync_posting_queue.py", "--check"])
        run_step("promotion platform kpi tracker", [sys.executable, "tools/promotion_platform_kpi_tracker.py", "--check"])
        run_step("promotion post writeback", [sys.executable, "tools/promotion_post_writeback.py", "check"])
        run_step("promotion post text import", [sys.executable, "tools/promotion_post_text_import.py", "check"])
        run_step("promotion post scaffold writeback safety", [sys.executable, "tools/promotion_post_scaffold_writeback_safety.py"])
        run_step("promotion first batch publish dry run", [sys.executable, "tools/promotion_first_batch_publish_dry_run.py"])
        run_step("promotion placeholder URL safety audit", [sys.executable, "tools/promotion_placeholder_url_safety_audit.py"])
        run_step("promotion proof note safety audit", [sys.executable, "tools/promotion_proof_note_safety_audit.py"])
        run_step("promotion temporal writeback safety audit", [sys.executable, "tools/promotion_temporal_writeback_safety_audit.py"])
        run_step("promotion evidence ledger", [sys.executable, "tools/promotion_evidence_ledger.py", "--check"])
        run_step("promotion first batch publication packet", [sys.executable, "tools/promotion_first_batch_publication_packet.py", "--check"])
        run_step("promotion first batch completion gate", [sys.executable, "tools/promotion_first_batch_completion_gate.py", "--check"])
        run_step("promotion first batch asset qa", [sys.executable, "tools/promotion_first_batch_asset_qa.py", "--check"])
        run_step("promotion first batch publish checklist", [sys.executable, "tools/promotion_first_batch_publish_checklist.py", "--check"])
        run_step("promotion first batch kpi checklist", [sys.executable, "tools/promotion_first_batch_kpi_checklist.py", "--check"])
        run_step("promotion profile post alignment checklist", [sys.executable, "tools/promotion_profile_post_alignment_checklist.py", "--check"])
        run_step("promotion public post URL checklist", [sys.executable, "tools/promotion_public_post_url_checklist.py", "--check"])
        run_step("promotion zero KPI evidence checklist", [sys.executable, "tools/promotion_zero_kpi_evidence_checklist.py", "--check"])
        run_step("promotion post ops readiness pack", [sys.executable, "tools/promotion_post_ops_readiness_pack.py", "--check"])
        run_step("promotion post proof handoff pack", [sys.executable, "tools/promotion_post_proof_handoff_pack.py", "--check"])
        run_step("promotion first batch evidence matrix", [sys.executable, "tools/promotion_first_batch_evidence_matrix.py", "--check"])
        run_step("promotion publishing status", [sys.executable, "tools/promotion_publishing_status.py", "--check"])
        run_step("promotion KPI writeback consistency audit", [sys.executable, "tools/promotion_kpi_writeback_consistency_audit.py"])
        run_step("promotion writeback flow audit", [sys.executable, "tools/promotion_writeback_flow_audit.py"])
        run_step("promotion writeback refresh audit", [sys.executable, "tools/promotion_writeback_refresh_audit.py"])
        run_step("promotion launch brief", [sys.executable, "tools/promotion_launch_brief.py", "--all", "--check"])
        run_step("promotion revenue decision matrix", [sys.executable, "tools/promotion_revenue_decision_matrix.py", "--check"])
        run_step("promotion week decision gate", [sys.executable, "tools/promotion_week_decision_gate.py", "--check"])
        run_step("promotion decision readiness checklist", [sys.executable, "tools/promotion_decision_readiness_checklist.py", "--check"])
        run_step("promotion decision input matrix", [sys.executable, "tools/promotion_decision_input_matrix.py", "--check"])
        run_step("promotion lead intake playbook", [sys.executable, "tools/promotion_lead_intake_playbook.py", "--check"])
        run_step("promotion lead form audit", [sys.executable, "tools/promotion_lead_form_audit.py"])
        run_step("promotion lead form importability audit", [sys.executable, "tools/promotion_lead_form_importability_audit.py"])
        run_step("promotion lead form health report", [sys.executable, "tools/promotion_lead_form_health_report.py", "--check"])
        run_step("lead intake browser smoke", [find_node(), "tools/lead_intake_browser_smoke.mjs"])
        run_step("promotion lead text import", [sys.executable, "tools/promotion_lead_text_import.py", "check"])
        run_step("promotion lead writeback", [sys.executable, "tools/promotion_lead_writeback.py", "check"])
        run_step("promotion lead data minimization audit", [sys.executable, "tools/promotion_lead_data_minimization_audit.py"])
        run_step("promotion lead privacy safety audit", [sys.executable, "tools/promotion_lead_privacy_safety_audit.py"])
        run_step("promotion lead request proof packet", [sys.executable, "tools/promotion_lead_request_proof_packet.py", "--check"])
        run_step("promotion lead ops action sheet", [sys.executable, "tools/promotion_lead_ops_action_sheet.py", "--check"])
        run_step("promotion lead evidence checklist", [sys.executable, "tools/promotion_lead_evidence_checklist.py", "--check"])
        run_step("promotion lead magnet inventory", [sys.executable, "tools/promotion_lead_magnet_inventory.py", "--check"])
        run_step("promotion lead demand gate", [sys.executable, "tools/promotion_lead_demand_gate.py", "--check"])
        run_step("promotion lead tracker summary", [sys.executable, "tools/promotion_lead_tracker_summary.py", "--check"])
        run_step("promotion lead demand scenario audit", [sys.executable, "tools/promotion_lead_demand_scenario_audit.py"])
        run_step("promotion offer hypothesis board", [sys.executable, "tools/promotion_offer_hypothesis_board.py", "--check"])
        run_step("promotion offer experiment plan", [sys.executable, "tools/promotion_offer_experiment_plan.py", "--check"])
        run_step("promotion offer experiment queue", [sys.executable, "tools/promotion_offer_experiment_queue.py", "--check"])
        run_step("promotion offer experiment scenario audit", [sys.executable, "tools/promotion_offer_experiment_scenario_audit.py"])
        run_step("promotion asset backlog", [sys.executable, "tools/promotion_asset_backlog.py", "--check"])
        run_step("promotion asset fulfillment gate", [sys.executable, "tools/promotion_asset_fulfillment_gate.py", "--check"])
        run_step("promotion asset fulfillment dry run", [sys.executable, "tools/promotion_asset_fulfillment_dry_run.py"])
        run_step("promotion asset commerce bridge audit", [sys.executable, "tools/promotion_asset_commerce_bridge_audit.py"])
        run_step("promotion trust commerce safety audit", [sys.executable, "tools/promotion_trust_commerce_safety_audit.py"])
        run_step("promotion platform profile setup", [sys.executable, "tools/promotion_platform_profile_setup.py", "--check"])
        run_step("promotion platform profile tracker", [sys.executable, "tools/promotion_platform_profile_tracker.py", "--check"])
        run_step("promotion profile writeback", [sys.executable, "tools/promotion_profile_writeback.py", "check"])
        run_step("promotion profile text import", [sys.executable, "tools/promotion_profile_text_import.py", "check"])
        run_step("promotion profile scaffold writeback safety", [sys.executable, "tools/promotion_profile_scaffold_writeback_safety.py"])
        run_step("promotion profile setup runbook", [sys.executable, "tools/promotion_profile_setup_runbook.py", "--check"])
        run_step("promotion profile verification packet", [sys.executable, "tools/promotion_profile_verification_packet.py", "--check"])
        run_step("promotion profile completion gate", [sys.executable, "tools/promotion_profile_completion_gate.py", "--check"])
        run_step("promotion week execution sheet", [sys.executable, "tools/promotion_week_execution_sheet.py", "--all", "--check"])
        run_step("promotion platform account identity checklist", [sys.executable, "tools/promotion_platform_account_identity_checklist.py", "--check"])
        run_step("promotion profile setup action sheet", [sys.executable, "tools/promotion_profile_setup_action_sheet.py", "--check"])
        run_step("promotion profile quickstart", [sys.executable, "tools/promotion_profile_quickstart.py", "--check"])
        run_step("promotion profile link readiness packet", [sys.executable, "tools/promotion_profile_link_readiness_packet.py", "--check"])
        run_step("promotion profile proof readiness pack", [sys.executable, "tools/promotion_profile_proof_readiness_pack.py", "--check"])
        run_step("promotion profile proof capture quickstart", [sys.executable, "tools/promotion_profile_proof_capture_quickstart.py", "--check"])
        run_step("promotion profile batch import", [sys.executable, "tools/promotion_profile_batch_import.py", "--check"])
        run_step("promotion profile setup handoff pack", [sys.executable, "tools/promotion_profile_setup_handoff_pack.py", "--check"])
        run_step("promotion profile writeback closure quickstart", [sys.executable, "tools/promotion_profile_writeback_closure_quickstart.py", "--check"])
        run_step("promotion post batch import", [sys.executable, "tools/promotion_post_batch_import.py", "--check"])
        run_step("promotion launch proof control sheet", [sys.executable, "tools/promotion_launch_proof_control_sheet.py", "--check"])
        run_step("promotion profile unlock rehearsal", [sys.executable, "tools/promotion_profile_unlock_rehearsal.py", "--check"])
        run_step("promotion profile setup dry run", [sys.executable, "tools/promotion_profile_setup_dry_run.py"])
        run_step("promotion launch sequence dry run", [sys.executable, "tools/promotion_launch_sequence_dry_run.py"])
        run_step("promotion first batch publish action sheet", [sys.executable, "tools/promotion_first_batch_publish_action_sheet.py", "--check"])
        run_step("promotion first batch publish readiness pack", [sys.executable, "tools/promotion_first_batch_publish_readiness_pack.py", "--check"])
        run_step("promotion first batch launch handoff", [sys.executable, "tools/promotion_first_batch_launch_handoff.py", "--check"])
        run_step("promotion first batch publish quickstart", [sys.executable, "tools/promotion_first_batch_publish_quickstart.py", "--check"])
        run_step("promotion first batch publish closure quickstart", [sys.executable, "tools/promotion_first_batch_publish_closure_quickstart.py", "--check"])
        run_step("promotion first batch kpi action sheet", [sys.executable, "tools/promotion_first_batch_kpi_action_sheet.py", "--check"])
        run_step("promotion first batch KPI quickstart", [sys.executable, "tools/promotion_first_batch_kpi_quickstart.py", "--check"])
        run_step("promotion first batch KPI closure quickstart", [sys.executable, "tools/promotion_first_batch_kpi_closure_quickstart.py", "--check"])
        run_step("promotion KPI zero source rehearsal", [sys.executable, "tools/promotion_kpi_zero_source_rehearsal.py", "--check"])
        run_step("promotion week publication runbook", [sys.executable, "tools/promotion_week_publication_runbook.py", "--week", "1", "--check"])
        run_step("promotion now asset pack", [sys.executable, "tools/promotion_now_asset_pack.py", "--check"])
        run_step("promotion now asset queue", [sys.executable, "tools/promotion_now_asset_queue.py", "--check"])
        run_step("promotion now asset briefs", [sys.executable, "tools/promotion_now_asset_briefs.py", "--check"])
        run_step("promotion week asset briefs", [sys.executable, "tools/promotion_week_asset_briefs.py", "--all", "--check"])
        run_step("promotion launch command center", [sys.executable, "tools/promotion_launch_command_center.py", "--check"])
        run_step("promotion ops closure audit", [sys.executable, "tools/promotion_ops_closure_audit.py"])
        run_step("promotion operation proof packet", [sys.executable, "tools/promotion_operation_proof_packet.py", "--check"])
        run_step("promotion operation proof templates", [sys.executable, "tools/promotion_operation_proof_templates.py", "--check"])
        run_step("promotion profile evidence checklist", [sys.executable, "tools/promotion_profile_evidence_checklist.py", "--check"])
        run_step("promotion launch rehearsal packet", [sys.executable, "tools/promotion_launch_rehearsal_packet.py", "--check"])
        run_step("promotion launch readiness gate", [sys.executable, "tools/promotion_launch_readiness_gate.py", "--check"])
        run_step("promotion launch link qa", [sys.executable, "tools/promotion_launch_link_qa.py", "--check"])
        run_step("promotion profile URL smoke", [sys.executable, "tools/promotion_profile_url_smoke.py", "--check"])
        run_step("promotion attribution reconciliation", [sys.executable, "tools/promotion_attribution_reconciliation.py", "--check"])
        run_step("promotion next actions", [sys.executable, "tools/promotion_next_actions.py", "--check"])
        run_step("promotion weekly summary", [sys.executable, "tools/promotion_weekly_summary.py", "--check"])
        run_step("promotion weekly review packet", [sys.executable, "tools/promotion_weekly_review_packet.py", "--check"])
        run_step("promotion weekly decision evidence checklist", [sys.executable, "tools/promotion_weekly_decision_evidence_checklist.py", "--check"])
        run_step("promotion weekly review action sheet", [sys.executable, "tools/promotion_weekly_review_action_sheet.py", "--check"])
        run_step("promotion weekly review quickstart", [sys.executable, "tools/promotion_weekly_review_quickstart.py", "--check"])
        run_step("promotion blocker resolution checklist", [sys.executable, "tools/promotion_blocker_resolution_checklist.py", "--check"])
        run_step("promotion launch blocker digest", [sys.executable, "tools/promotion_launch_blocker_digest.py", "--check"])
        run_step("promotion operator handoff packet", [sys.executable, "tools/promotion_operator_handoff_packet.py", "--check"])
        run_step("promotion launch ops dashboard", [sys.executable, "tools/promotion_launch_ops_dashboard.py", "--check"])
        run_step("promotion launch day run sheet", [sys.executable, "tools/promotion_launch_day_run_sheet.py", "--check"])
        run_step("promotion launch exception runbook", [sys.executable, "tools/promotion_launch_exception_runbook.py", "--check"])
        run_step("promotion operator import template audit", [sys.executable, "tools/promotion_operator_import_template_audit.py"])
        run_step("promotion operator handoff consistency audit", [sys.executable, "tools/promotion_operator_handoff_consistency_audit.py"])
        run_step("promotion empty data safety audit", [sys.executable, "tools/promotion_empty_data_safety_audit.py"])
        run_step("promotion daily ops refresh", [sys.executable, "tools/promotion_daily_ops_refresh.py", "--check", "--strict-freshness"])
        run_step("promotion master gate", [sys.executable, "tools/promotion_master_gate.py", "--check"])
        run_step("promotion stage transition matrix", [sys.executable, "tools/promotion_stage_transition_matrix.py", "--check"])
        run_step("promotion core snapshot consistency audit", [sys.executable, "tools/promotion_core_snapshot_consistency_audit.py"])
        run_step("promotion profile publish handoff", [sys.executable, "tools/promotion_profile_publish_handoff.py", "--check"])
        run_step("promotion publish KPI handoff", [sys.executable, "tools/promotion_publish_kpi_handoff.py", "--check"])
        run_step("promotion weekly lead offer handoff", [sys.executable, "tools/promotion_weekly_lead_offer_handoff.py", "--check"])
        run_step("promotion lead offer quickstart", [sys.executable, "tools/promotion_lead_offer_quickstart.py", "--check"])
        run_step("promotion lead intake closure quickstart", [sys.executable, "tools/promotion_lead_intake_closure_quickstart.py", "--check"])
        run_step("promotion launch clipboard", [sys.executable, "tools/promotion_launch_clipboard.py", "--check"])
        run_step("promotion launch quickstart", [sys.executable, "tools/promotion_launch_quickstart.py", "--check"])
        run_step("promotion launch execution closure quickstart", [sys.executable, "tools/promotion_launch_execution_closure_quickstart.py", "--check"])
        run_step("promotion proof rehearsal", [sys.executable, "tools/promotion_proof_rehearsal.py", "--check"])
        run_step("promotion proof import closure quickstart", [sys.executable, "tools/promotion_proof_import_closure_quickstart.py", "--check"])
        run_step("promotion operator next action closure quickstart", [sys.executable, "tools/promotion_operator_next_action_closure_quickstart.py", "--check"])
        run_step("promotion decision scenario audit", [sys.executable, "tools/promotion_decision_scenario_audit.py"])
        run_step("deploy manifest audit", [sys.executable, "tools/deploy_manifest_audit.py"])
        run_step("site health config audit", [sys.executable, "tools/site_health_config_audit.py"])

    if args.visual or args.visual_only:
        node = find_node()
        env = os.environ.copy()
        if args.base_url:
            env["BASE_URL"] = args.base_url
            run_step("browser visual check", [node, "tools/visual_check.mjs"], env=env)
            run_step("tap target smoke", [node, "tools/tap_target_smoke.mjs"], env=env)
            run_step("contrast smoke", [node, "tools/contrast_smoke.mjs"], env=env)
            run_step("user preferences smoke", [node, "tools/user_preferences_smoke.mjs"], env=env)
            run_step("storage privacy smoke", [node, "tools/storage_privacy_smoke.mjs"], env=env)
        else:
            with local_preview_server() as base_url:
                env["BASE_URL"] = base_url
                run_step("browser visual check", [node, "tools/visual_check.mjs"], env=env)
                run_step("tap target smoke", [node, "tools/tap_target_smoke.mjs"], env=env)
                run_step("contrast smoke", [node, "tools/contrast_smoke.mjs"], env=env)
                run_step("user preferences smoke", [node, "tools/user_preferences_smoke.mjs"], env=env)
                run_step("storage privacy smoke", [node, "tools/storage_privacy_smoke.mjs"], env=env)

    print("predeploy_checks=ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
