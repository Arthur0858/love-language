#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "site-health.md"
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_:-]+)=(.*)$")


CHECKS = [
    ("predeploy", [sys.executable, "tools/predeploy_check.py"], 180, False),
    ("cloudflare_dry_run", [sys.executable, "tools/deploy_cloudflare_pages.py", "--dry-run"], 120, False),
    ("public_accessibility_smoke", [sys.executable, "tools/public_accessibility_smoke.py"], 240, True),
    ("public_asset_integrity_smoke", [sys.executable, "tools/public_asset_integrity_smoke.py"], 240, True),
    ("public_deploy_smoke", [sys.executable, "tools/public_deploy_smoke.py"], 240, True),
    ("public_contact_smoke", [sys.executable, "tools/public_contact_smoke.py"], 120, True),
    ("public_discovery_smoke", [sys.executable, "tools/public_discovery_smoke.py"], 180, True),
    ("public_external_link_smoke", [sys.executable, "tools/public_external_link_smoke.py"], 120, True),
    ("public_headers_smoke", [sys.executable, "tools/public_headers_smoke.py"], 120, True),
    ("public_indexability_smoke", [sys.executable, "tools/public_indexability_smoke.py"], 240, True),
    ("public_internal_link_smoke", [sys.executable, "tools/public_internal_link_smoke.py"], 300, True),
    ("public_locale_route_smoke", [sys.executable, "tools/public_locale_route_smoke.py"], 240, True),
    ("public_locale_ui_smoke", [sys.executable, "tools/public_locale_ui_smoke.py"], 240, True),
    ("public_metadata_smoke", [sys.executable, "tools/public_metadata_smoke.py"], 240, True),
    ("public_quiz_conversion_smoke", [sys.executable, "tools/public_quiz_conversion_smoke.py"], 240, True),
    ("public_quiz_data_smoke", [sys.executable, "tools/public_quiz_data_smoke.py"], 120, True),
    ("public_schema_smoke", [sys.executable, "tools/public_schema_smoke.py"], 240, True),
    ("public_schema_url_smoke", [sys.executable, "tools/public_schema_url_smoke.py"], 240, True),
    ("public_sitemap_smoke", [sys.executable, "tools/public_sitemap_smoke.py"], 240, True),
    ("public_not_found_smoke", ["node", "tools/public_not_found_smoke.mjs"], 120, True),
    ("public_visual_smoke", ["node", "tools/public_visual_smoke.mjs"], 1500, True),
    ("csp_runtime_smoke", ["node", "tools/csp_runtime_smoke.mjs"], 120, True),
    ("public_trust_smoke", [sys.executable, "tools/public_trust_smoke.py"], 180, True),
    ("public_versioned_asset_smoke", [sys.executable, "tools/public_versioned_asset_smoke.py"], 240, True),
    ("runtime_performance_smoke", ["node", "tools/runtime_performance_smoke.mjs"], 120, True),
    ("keyboard_navigation_smoke", ["node", "tools/keyboard_navigation_smoke.mjs"], 120, True),
    ("tap_target_smoke", ["node", "tools/tap_target_smoke.mjs"], 120, True),
    ("contrast_smoke", ["node", "tools/contrast_smoke.mjs"], 120, True),
    ("user_preferences_smoke", ["node", "tools/user_preferences_smoke.mjs"], 120, True),
    ("storage_privacy_smoke", ["node", "tools/storage_privacy_smoke.mjs"], 120, True),
]
RETRY_ON_FAILURE = {"csp_runtime_smoke", "public_locale_ui_smoke", "runtime_performance_smoke", "tap_target_smoke"}


def safe_timeout_output(error: subprocess.TimeoutExpired) -> str:
    output = error.stdout or ""
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    return output.rstrip() + f"\ntimed_out=1\nerror=command timed out after {error.timeout} seconds\n"


def run(command: list[str], timeout: int = 180) -> tuple[int, str]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        return 124, safe_timeout_output(error)
    return result.returncode, result.stdout


def git_value(*args: str) -> str:
    code, output = run(["git", *args], timeout=30)
    return output.strip() if code == 0 else ""


def parse_key_values(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in output.splitlines():
        match = KEY_VALUE_RE.match(line.strip())
        if match:
            values[match.group(1)] = match.group(2)
    return values


def check_status(code: int, values: dict[str, str]) -> str:
    if code != 0:
        return "failed"
    issue_keys = [key for key in values if key.endswith("issues") or key.endswith("_issues")]
    if any(values.get(key) not in {"0", ""} for key in issue_keys):
        return "issues"
    if values.get("predeploy_checks") == "ok":
        return "ok"
    return "ok"


def render_section(name: str, code: int, values: dict[str, str]) -> list[str]:
    status = check_status(code, values)
    lines = [f"## {name}", "", f"- status: `{status}`"]
    important_keys = [
        "predeploy_checks",
        "issues",
        "content_uniqueness_issues",
        "multilingual_route_issues",
        "guardian_conversion_issues",
        "accessibility_issues",
        "image_asset_issues",
        "performance_budget_issues",
        "runtime_performance_issues",
        "keyboard_navigation_issues",
        "tap_target_issues",
        "contrast_issues",
        "user_preference_issues",
        "storage_privacy_issues",
        "deploy_manifest_issues",
        "public_accessibility_issues",
        "public_asset_issues",
        "public_deploy_issues",
        "public_contact_issues",
        "public_discovery_issues",
        "public_external_link_issues",
        "public_header_issues",
        "public_indexability_issues",
        "public_internal_link_issues",
        "public_locale_route_issues",
        "public_locale_issues",
        "public_metadata_issues",
        "public_quiz_conversion_issues",
        "public_quiz_issues",
        "public_schema_issues",
        "public_schema_url_issues",
        "public_sitemap_issues",
        "public_not_found_issues",
        "public_visual_issues",
        "csp_runtime_issues",
        "public_trust_issues",
        "public_versioned_asset_issues",
        "Remote missing hashes",
        "Commit dirty",
        "pages",
        "indexable_pages",
        "sitemap_urls",
        "sitemap_alternates",
        "affiliate_pages",
        "affiliate_links",
        "public_accessibility_pages_checked",
        "public_accessibility_links_checked",
        "public_accessibility_buttons_checked",
        "public_accessibility_images_checked",
        "public_accessibility_controls_checked",
        "public_accessibility_skip_links_checked",
        "public_accessibility_main_targets_checked",
        "public_accessibility_navs_checked",
        "public_accessibility_idrefs_checked",
        "public_accessibility_aria_current_checked",
        "public_asset_pages_checked",
        "public_asset_refs_seen",
        "public_asset_unique_assets_checked",
        "public_asset_immutable_assets_checked",
        "public_pages_checked",
        "public_external_links_checked",
        "public_affiliate_links_checked",
        "public_home_universe_gate_sections_checked",
        "public_home_universe_gate_cards_checked",
        "public_characters_universe_map_sections_checked",
        "public_characters_universe_map_cards_checked",
        "public_garden_map_sections_checked",
        "public_garden_map_guardian_cards_checked",
        "public_garden_map_guide_cards_checked",
        "public_garden_map_route_cards_checked",
        "public_supply_safety_sections_checked",
        "public_supply_starter_cards_checked",
        "public_supply_wishlist_cards_checked",
        "public_contact_pages_checked",
        "public_contact_anchor_targets_checked",
        "public_contact_mailto_links_checked",
        "public_contact_protected_email_links_checked",
        "public_contact_subjects_checked",
        "public_contact_source_routes_checked",
        "public_discovery_feed_items",
        "public_discovery_feed_links_checked",
        "public_discovery_feed_item_metadata_checked",
        "public_discovery_manifest_icons_checked",
        "public_discovery_manifest_icon_dimensions_checked",
        "public_discovery_manifest_shortcuts",
        "public_discovery_manifest_shortcut_links_checked",
        "public_discovery_manifest_expected_shortcuts_checked",
        "public_discovery_llms_sections_checked",
        "public_discovery_llms_snippets_checked",
        "public_discovery_llms_high_value_urls_checked",
        "public_discovery_llms_urls_checked",
        "public_discovery_llms_url_canonicals_checked",
        "public_discovery_text_files_checked",
        "public_discovery_security_fields_checked",
        "public_discovery_robots_lines_checked",
        "public_discovery_robots_sitemap_links_checked",
        "public_external_unique_links_checked",
        "public_external_hosts_checked",
        "public_external_anchors_checked",
        "public_external_blank_target_rel_checked",
        "public_external_affiliate_links_checked",
        "public_external_affiliate_anchors_checked",
        "public_external_affiliate_disclosure_pages_checked",
        "public_header_cases_checked",
        "public_header_core_html_cases_checked",
        "public_indexability_sitemap_urls_listed",
        "public_indexability_sitemap_pages_checked",
        "public_indexability_noindex_pages_checked",
        "public_indexability_redirects_checked",
        "public_indexability_sitemap_absence_checked",
        "public_internal_link_pages_checked",
        "public_internal_links_seen",
        "public_internal_unique_links_checked",
        "public_internal_anchor_targets_checked",
        "public_internal_redirects_followed",
        "public_locale_route_pages_checked",
        "public_locale_route_primary_nav_links_checked",
        "public_locale_route_footer_links_checked",
        "public_locale_route_language_links_checked",
        "public_locale_route_language_matches_checked",
        "public_locale_route_nav_matches_checked",
        "public_locale_route_footer_matches_checked",
        "public_locale_pages_checked",
        "public_locale_nav_labels_checked",
        "public_locale_footer_labels_checked",
        "public_locale_language_menu_labels_checked",
        "public_locale_active_language_links_checked",
        "public_metadata_pages_checked",
        "public_metadata_social_cards_checked",
        "public_metadata_hreflang_links_checked",
        "public_metadata_jsonld_blocks_checked",
        "public_metadata_images_checked",
        "public_metadata_image_dimensions_checked",
        "public_quiz_conversion_assets_checked",
        "public_quiz_conversion_results_checked",
        "public_quiz_conversion_internal_urls_checked",
        "public_quiz_conversion_anchor_targets_checked",
        "public_quiz_conversion_images_checked",
        "public_quiz_conversion_affiliate_links_checked",
        "public_quiz_conversion_pass_fields_checked",
        "public_quiz_conversion_home_saved_template_checks",
        "public_quiz_conversion_resume_template_pages_checked",
        "public_quiz_conversion_resume_template_checks",
        "public_quiz_assets_checked",
        "public_quiz_questions_checked",
        "public_quiz_results_checked",
        "public_quiz_starter_steps_checked",
        "public_schema_pages_checked",
        "public_schema_jsonld_blocks_checked",
        "public_schema_organization_entities_checked",
        "public_schema_primary_entities_checked",
        "public_schema_date_modified_entities_checked",
        "public_schema_breadcrumb_entities_checked",
        "public_schema_article_entities_checked",
        "public_schema_howto_entities_checked",
        "public_schema_itemlist_entities_checked",
        "public_schema_core_page_types_checked",
        "public_schema_guardian_profile_types_checked",
        "public_schema_url_pages_checked",
        "public_schema_url_jsonld_blocks_checked",
        "public_schema_url_values_checked",
        "public_schema_url_internal_urls_checked",
        "public_schema_url_image_urls_checked",
        "public_schema_url_external_urls_checked",
        "public_schema_url_sitemap_page_urls_checked",
        "public_schema_url_unique_targets_checked",
        "public_sitemap_pages_checked",
        "public_sitemap_core_universe_routes_expected",
        "public_sitemap_core_universe_routes_checked",
        "public_sitemap_lastmod_checked",
        "public_sitemap_changefreq_checked",
        "public_sitemap_priority_checked",
        "public_sitemap_hreflang_links_checked",
        "public_not_found_cases_checked",
        "public_not_found_localized_cases",
        "public_not_found_safe_route_links_checked",
        "public_visual_attempts",
        "public_visual_cases_checked",
        "public_visual_screenshots",
        "public_visual_quiz_flow_cases",
        "public_visual_conversion_cases",
        "public_visual_garden_map_cases",
        "public_visual_language_menu_cases",
        "public_visual_redirect_cases",
        "public_visual_worksheet_cases",
        "public_visual_copy_cases",
        "public_visual_anchor_focus_cases",
        "public_visual_saved_resume_cases",
        "public_visual_horizontal_overflow_issues",
        "public_visual_console_error_cases",
        "public_visual_page_error_cases",
        "csp_runtime_pages_checked",
        "csp_runtime_violations",
        "public_trust_pages_checked",
        "public_trust_boundary_texts_checked",
        "public_trust_policy_compass_cards_checked",
        "public_trust_policy_detail_cards_checked",
        "public_trust_about_cards_checked",
        "public_trust_theory_domain_cards_checked",
        "public_trust_action_routes_checked",
        "public_trust_contact_route_anchors_checked",
        "public_trust_noncommercial_pages_checked",
        "public_versioned_asset_pages_checked",
        "public_versioned_asset_css_refs_checked",
        "public_versioned_asset_interaction_refs_checked",
        "public_versioned_asset_affiliate_refs_checked",
        "public_versioned_asset_quiz_data_refs_checked",
        "public_versioned_asset_root_refs_checked",
        "public_versioned_asset_stale_refs",
        "runtime_performance_pages_checked",
        "runtime_performance_attempts",
        "runtime_performance_worst_lcp_ms",
        "runtime_performance_worst_cls",
        "runtime_performance_max_transfer_bytes",
        "keyboard_navigation_cases_checked",
        "keyboard_navigation_tab_stops_checked",
        "keyboard_navigation_named_focuses_checked",
        "tap_target_pages_checked",
        "tap_targets_checked",
        "contrast_pages_checked",
        "contrast_text_nodes_checked",
        "user_preference_pages_checked",
        "user_preference_checks",
        "storage_privacy_checks",
        "storage_privacy_local_keys_checked",
        "internal_refs",
        "external_links",
        "anchor_accessible_names",
        "primary_nav_links",
        "footer_guardian_links",
        "language_menu_links",
        "language_hreflang_matches",
        "canonical_links",
        "hreflang_links",
        "jsonld_blocks",
        "primary_jsonld_entities",
        "social_cards",
        "social_locale_tags",
        "mailto_links",
        "home_quiz_entry_pages",
        "guide_action_bridge_pages",
        "character_result_resume_pages",
        "resources_supply_entry_pages",
        "trust_action_route_pages",
        "current_css_asset_refs",
        "current_interaction_asset_refs",
        "current_affiliate_asset_refs",
        "current_quiz_data_asset_refs",
        "image_assets_checked",
        "priority_images_checked",
        "image_preloads_checked",
        "deploy_manifest_files",
        "timed_out",
        "error",
    ]
    for key in important_keys:
        if key in values:
            lines.append(f"- {key}: `{values[key]}`")
    return lines


def parse_cloudflare_dry_run(output: str) -> dict[str, str]:
    values = parse_key_values(output)
    for line in output.splitlines():
        for label in ("Commit hash", "Commit message", "Commit dirty", "Static assets", "Remote missing hashes"):
            prefix = f"{label}: "
            if line.startswith(prefix):
                values[label] = line.removeprefix(prefix).strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a LoveTypes health summary from current checks.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown output path.")
    parser.add_argument(
        "--skip-public",
        action="store_true",
        help="Skip public smoke checks and only summarize local checks plus Cloudflare dry-run.",
    )
    parser.add_argument(
        "--timeout-scale",
        type=float,
        default=1.0,
        help="Multiplier applied to per-check timeouts. Use 0.5 for faster failure or 2 for slow networks.",
    )
    args = parser.parse_args()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    head = git_value("rev-parse", "--short", "HEAD")
    full_head = git_value("rev-parse", "HEAD")
    branch = git_value("status", "--short", "--branch").splitlines()[0]
    remote = git_value("ls-remote", "origin", "refs/heads/main").split()
    remote_sha = remote[0] if remote else ""

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sections: list[str] = [
        "# LoveTypes Site Health",
        "",
        f"- generated_at_utc: `{generated_at}`",
        f"- commit_short: `{head}`",
        f"- commit_full: `{full_head}`",
        f"- origin_main: `{remote_sha}`",
        f"- branch_status: `{branch}`",
        f"- production: `https://lovetypes.tw/`",
        f"- cloudflare_project: `lovetypes`",
        "",
    ]

    failed = False
    for name, command, timeout, is_public in CHECKS:
        if args.skip_public and is_public:
            print(f"site_health_step={name} status=skipped", flush=True)
            sections.extend([f"## {name}", "", "- status: `skipped`", ""])
            continue
        effective_timeout = max(1, int(timeout * args.timeout_scale))
        print(f"site_health_step={name} status=running timeout={effective_timeout}", flush=True)
        code, output = run(command, timeout=effective_timeout)
        if name == "cloudflare_dry_run":
            values = parse_cloudflare_dry_run(output)
        else:
            values = parse_key_values(output)
        status = check_status(code, values)
        if status != "ok" and name in RETRY_ON_FAILURE:
            print(f"site_health_step={name} status=retrying", flush=True)
            retry_code, retry_output = run(command, timeout=effective_timeout)
            if name == "cloudflare_dry_run":
                retry_values = parse_cloudflare_dry_run(retry_output)
            else:
                retry_values = parse_key_values(retry_output)
            retry_status = check_status(retry_code, retry_values)
            if retry_status == "ok":
                code = retry_code
                values = retry_values
                status = retry_status
            values[f"{name.removesuffix('_smoke')}_attempts"] = "2"
        else:
            values[f"{name.removesuffix('_smoke')}_attempts"] = "1"
        print(f"site_health_step={name} status={status}", flush=True)
        sections.extend(render_section(name, code, values))
        sections.append("")
        if status != "ok":
            failed = True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"site_health_output={output_path}")
    print(f"site_health_status={'failed' if failed else 'ok'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
