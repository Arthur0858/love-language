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
    "tools/accessibility_audit.py",
    "tools/image_asset_audit.py",
    "tools/performance_budget_audit.py",
    "tools/promotion_publish_pack.py",
    "tools/promotion_next_actions.py",
    "tools/promotion_sync_kpi_tracker.py",
    "tools/promotion_sync_posting_queue.py",
    "tools/promotion_publishing_status.py",
    "tools/promotion_launch_brief.py",
    "tools/promotion_revenue_decision_matrix.py",
    "tools/promotion_week_decision_gate.py",
    "tools/promotion_lead_intake_playbook.py",
    "tools/promotion_offer_hypothesis_board.py",
    "tools/promotion_offer_experiment_plan.py",
    "tools/promotion_offer_experiment_queue.py",
    "tools/promotion_asset_backlog.py",
    "tools/promotion_platform_profile_setup.py",
    "tools/promotion_platform_profile_tracker.py",
    "tools/promotion_week_execution_sheet.py",
    "tools/promotion_now_asset_pack.py",
    "tools/promotion_now_asset_queue.py",
    "tools/promotion_now_asset_briefs.py",
    "tools/promotion_weekly_summary.py",
    "tools/build_guardian_card_assets.py",
    "tools/public_deploy_smoke.py",
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
        run_step("accessibility audit", [sys.executable, "tools/accessibility_audit.py"])
        run_step("image asset audit", [sys.executable, "tools/image_asset_audit.py"])
        run_step("performance budget audit", [sys.executable, "tools/performance_budget_audit.py"])
        run_step("promotion spreadsheet workbook", [find_node(), "tools/build_promotion_spreadsheet.mjs"])
        run_step("promotion publish pack", [sys.executable, "tools/promotion_publish_pack.py", "--all", "--check"])
        run_step("promotion kpi tracker", [sys.executable, "tools/promotion_sync_kpi_tracker.py", "--check"])
        run_step("promotion posting queue", [sys.executable, "tools/promotion_sync_posting_queue.py", "--check"])
        run_step("promotion publishing status", [sys.executable, "tools/promotion_publishing_status.py", "--check"])
        run_step("promotion launch brief", [sys.executable, "tools/promotion_launch_brief.py", "--all", "--check"])
        run_step("promotion revenue decision matrix", [sys.executable, "tools/promotion_revenue_decision_matrix.py", "--check"])
        run_step("promotion week decision gate", [sys.executable, "tools/promotion_week_decision_gate.py", "--check"])
        run_step("promotion lead intake playbook", [sys.executable, "tools/promotion_lead_intake_playbook.py", "--check"])
        run_step("promotion offer hypothesis board", [sys.executable, "tools/promotion_offer_hypothesis_board.py", "--check"])
        run_step("promotion offer experiment plan", [sys.executable, "tools/promotion_offer_experiment_plan.py", "--check"])
        run_step("promotion offer experiment queue", [sys.executable, "tools/promotion_offer_experiment_queue.py", "--check"])
        run_step("promotion asset backlog", [sys.executable, "tools/promotion_asset_backlog.py", "--check"])
        run_step("promotion platform profile setup", [sys.executable, "tools/promotion_platform_profile_setup.py", "--check"])
        run_step("promotion platform profile tracker", [sys.executable, "tools/promotion_platform_profile_tracker.py", "--check"])
        run_step("promotion week execution sheet", [sys.executable, "tools/promotion_week_execution_sheet.py", "--all", "--check"])
        run_step("promotion now asset pack", [sys.executable, "tools/promotion_now_asset_pack.py", "--check"])
        run_step("promotion now asset queue", [sys.executable, "tools/promotion_now_asset_queue.py", "--check"])
        run_step("promotion now asset briefs", [sys.executable, "tools/promotion_now_asset_briefs.py", "--check"])
        run_step("promotion next actions", [sys.executable, "tools/promotion_next_actions.py", "--check"])
        run_step("promotion weekly summary", [sys.executable, "tools/promotion_weekly_summary.py", "--check"])
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
