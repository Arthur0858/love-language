#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "site-health.md"
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_:-]+)=(.*)$")
PROGRESS_PREFIXES = ("[visual]", "[public-quiz-flow]", "[perf]", "[tap]", "[public-visual]")


CHECKS = [
    ("predeploy", [sys.executable, "tools/predeploy_check.py"], 180, False),
    ("cloudflare_dry_run", [sys.executable, "tools/deploy_cloudflare_pages.py", "--dry-run"], 120, False),
    ("public_accessibility_smoke", [sys.executable, "tools/public_accessibility_smoke.py"], 240, True),
    ("public_asset_integrity_smoke", [sys.executable, "tools/public_asset_integrity_smoke.py"], 240, True),
    ("public_deploy_smoke", [sys.executable, "tools/public_deploy_smoke.py"], 240, True),
    ("public_contact_smoke", [sys.executable, "tools/public_contact_smoke.py"], 120, True),
    ("public_discovery_smoke", [sys.executable, "tools/public_discovery_smoke.py"], 180, True),
    ("public_external_link_smoke", [sys.executable, "tools/public_external_link_smoke.py"], 120, True),
    ("public_garden_map_smoke", [sys.executable, "tools/public_garden_map_smoke.py"], 180, True),
    ("public_guide_smoke", [sys.executable, "tools/public_guide_smoke.py"], 300, True),
    ("public_guardian_smoke", [sys.executable, "tools/public_guardian_smoke.py"], 240, True),
    ("public_headers_smoke", [sys.executable, "tools/public_headers_smoke.py"], 120, True),
    ("public_home_smoke", [sys.executable, "tools/public_home_smoke.py"], 180, True),
    ("public_indexability_smoke", [sys.executable, "tools/public_indexability_smoke.py"], 240, True),
    ("public_internal_link_smoke", [sys.executable, "tools/public_internal_link_smoke.py"], 300, True),
    ("public_keepsake_smoke", [sys.executable, "tools/public_keepsake_smoke.py"], 180, True),
    ("public_locale_route_smoke", [sys.executable, "tools/public_locale_route_smoke.py"], 240, True),
    ("public_locale_ui_smoke", [sys.executable, "tools/public_locale_ui_smoke.py"], 240, True),
    ("public_luna_smoke", [sys.executable, "tools/public_luna_smoke.py"], 180, True),
    ("public_metadata_smoke", [sys.executable, "tools/public_metadata_smoke.py"], 240, True),
    ("public_quiz_conversion_smoke", [sys.executable, "tools/public_quiz_conversion_smoke.py"], 240, True),
    ("public_quiz_data_smoke", [sys.executable, "tools/public_quiz_data_smoke.py"], 120, True),
    ("public_quiz_flow_smoke", ["node", "tools/public_quiz_flow_smoke.mjs"], 180, True),
    ("public_revenue_path_smoke", [sys.executable, "tools/public_revenue_path_smoke.py"], 180, True),
    ("public_repair_plan_smoke", [sys.executable, "tools/public_repair_plan_smoke.py"], 180, True),
    ("public_schema_smoke", [sys.executable, "tools/public_schema_smoke.py"], 240, True),
    ("public_schema_url_smoke", [sys.executable, "tools/public_schema_url_smoke.py"], 240, True),
    ("public_sitemap_smoke", [sys.executable, "tools/public_sitemap_smoke.py"], 240, True),
    ("public_supply_smoke", [sys.executable, "tools/public_supply_smoke.py"], 180, True),
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
RETRY_ON_FAILURE = {
    "csp_runtime_smoke",
    "public_locale_ui_smoke",
    "public_quiz_flow_smoke",
    "runtime_performance_smoke",
    "tap_target_smoke",
}


def should_stream_progress(line: str) -> bool:
    stripped = line.strip()
    return any(stripped.startswith(prefix) for prefix in PROGRESS_PREFIXES)


def run(command: list[str], timeout: int = 180) -> tuple[int, str]:
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    output_lines: list[str] = []

    def collect_output() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            output_lines.append(line)
            if should_stream_progress(line):
                print(line.rstrip(), flush=True)

    reader = threading.Thread(target=collect_output, daemon=True)
    reader.start()
    try:
        code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        code = 124
        output_lines.append(f"\ntimed_out=1\nerror=command timed out after {timeout} seconds\n")
    reader.join(timeout=5)
    return code, "".join(output_lines)


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
        "generated_fresh_issues",
        "issues",
        "content_uniqueness_issues",
        "multilingual_route_issues",
        "guardian_conversion_issues",
        "accessibility_issues",
        "image_asset_issues",
        "performance_budget_issues",
        "runtime_performance_issues",
        "site_health_config_issues",
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
        "public_garden_map_issues",
        "public_guide_issues",
        "public_guardian_issues",
        "public_header_issues",
        "public_home_issues",
        "public_indexability_issues",
        "public_internal_link_issues",
        "public_keepsake_issues",
        "public_locale_route_issues",
        "public_locale_issues",
        "public_luna_issues",
        "public_metadata_issues",
        "public_quiz_conversion_issues",
        "public_quiz_flow_issues",
        "public_quiz_issues",
        "public_revenue_path_issues",
        "public_repair_plan_issues",
        "public_schema_issues",
        "public_schema_url_issues",
        "public_sitemap_issues",
        "public_supply_issues",
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
        "public_characters_universe_map_sections_checked",
        "public_characters_universe_map_cards_checked",
        "public_garden_map_sections_checked",
        "public_supply_starter_cards_checked",
        "public_contact_pages_checked",
        "public_contact_anchor_targets_checked",
        "public_contact_mailto_links_checked",
        "public_contact_mailto_bodies_checked",
        "public_contact_template_blocks_checked",
        "public_contact_template_buttons_checked",
        "public_contact_request_option_grids_checked",
        "public_contact_request_option_texts_checked",
        "public_contact_request_option_mailtos_checked",
        "public_contact_repair_option_mailtos_checked",
        "public_contact_protected_email_links_checked",
        "public_contact_source_routes_checked",
        "public_contact_saved_result_sections_checked",
        "public_contact_saved_result_actions_checked",
        "public_contact_quiz_data_refs_checked",
        "public_contact_funnel_summary_sections_checked",
        "public_contact_funnel_summary_actions_checked",
        "public_contact_funnel_summary_context_labels_checked",
        "public_contact_funnel_summary_context_fields_checked",
        "public_contact_funnel_summary_empty_actions_checked",
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
        "public_discovery_funnel_events_checked",
        "public_discovery_funnel_event_categories_checked",
        "public_discovery_funnel_event_roles_checked",
        "public_external_unique_links_checked",
        "public_external_hosts_checked",
        "public_external_anchors_checked",
        "public_external_blank_target_rel_checked",
        "public_external_affiliate_links_checked",
        "public_external_affiliate_anchors_checked",
        "public_external_affiliate_disclosure_pages_checked",
        "public_garden_map_pages_checked",
        "public_garden_map_quiz_scripts_checked",
        "public_garden_map_hero_actions_checked",
        "public_garden_map_saved_templates_checked",
        "public_garden_map_saved_actions_checked",
        "public_garden_map_handoff_cards_checked",
        "public_garden_map_route_cards_checked",
        "public_garden_map_tool_cards_checked",
        "public_garden_map_guardian_cards_checked",
        "public_garden_map_guide_cards_checked",
        "public_garden_map_trust_cards_checked",
        "public_garden_map_boundary_sections_checked",
        "public_guide_index_pages_checked",
        "public_guide_index_actions_checked",
        "public_guide_index_action_events_checked",
        "public_guide_index_compass_cards_checked",
        "public_guide_index_compass_events_checked",
        "public_guide_index_domain_cards_checked",
        "public_guide_index_domain_actions_checked",
        "public_guide_index_domain_events_checked",
        "public_guide_index_cards_checked",
        "public_guide_index_boundary_sections_checked",
        "public_guide_pages_checked",
        "public_guide_quiz_scripts_checked",
        "public_guide_resume_templates_checked",
        "public_guide_resume_events_checked",
        "public_guide_article_sections_checked",
        "public_guide_safety_callouts_checked",
        "public_guide_related_cards_checked",
        "public_guide_action_bridges_checked",
        "public_guide_action_cards_checked",
        "public_guide_action_events_checked",
        "public_guide_guardian_links_checked",
        "public_guide_supply_links_checked",
        "public_guide_repair_links_checked",
        "public_guide_luna_links_checked",
        "public_guide_anchor_targets_checked",
        "public_guardian_overview_pages_checked",
        "public_guardian_overview_map_cards_checked",
        "public_guardian_overview_map_events_checked",
        "public_guardian_overview_need_cards_checked",
        "public_guardian_overview_need_events_checked",
        "public_guardian_overview_entry_actions_checked",
        "public_guardian_overview_entry_events_checked",
        "public_guardian_pages_checked",
        "public_guardian_domain_markers_checked",
        "public_guardian_hero_supply_links_checked",
        "public_guardian_hero_events_checked",
        "public_guardian_route_snapshots_checked",
        "public_guardian_route_snapshot_events_checked",
        "public_guardian_guide_links_checked",
        "public_guardian_repair_links_checked",
        "public_guardian_supply_links_checked",
        "public_guardian_luna_links_checked",
        "public_guardian_affiliate_links_checked",
        "public_guardian_supply_panel_events_checked",
        "public_guardian_nav_cards_checked",
        "public_guardian_nav_events_checked",
        "public_guardian_resume_templates_checked",
        "public_guardian_resume_events_checked",
        "public_header_cases_checked",
        "public_header_core_html_cases_checked",
        "public_header_csp_tokens_checked",
        "public_home_pages_checked",
        "public_home_quiz_scripts_checked",
        "public_home_quiz_questions_checked",
        "public_home_quiz_results_checked",
        "public_home_quiz_labels_checked",
        "public_home_quiz_roots_checked",
        "public_home_quiz_start_buttons_checked",
        "public_home_saved_templates_checked",
        "public_home_saved_actions_checked",
        "public_home_saved_funnel_events_checked",
        "public_home_universe_gate_sections_checked",
        "public_home_universe_gate_cards_checked",
        "public_home_journey_sections_checked",
        "public_home_journey_cards_checked",
        "public_home_safety_sections_checked",
        "public_home_safety_links_checked",
        "public_home_hero_ctas_checked",
        "public_indexability_sitemap_urls_listed",
        "public_indexability_sitemap_pages_checked",
        "public_indexability_noindex_pages_checked",
        "public_indexability_redirects_checked",
        "public_indexability_sitemap_absence_checked",
        "public_internal_link_pages_checked",
        "public_internal_links_seen",
        "public_internal_unique_links_checked",
        "public_internal_html_targets_checked",
        "public_internal_canonical_targets_checked",
        "public_internal_redirects_followed",
        "public_keepsake_pages_checked",
        "public_keepsake_shelf_cards_checked",
        "public_keepsake_collector_cards_checked",
        "public_keepsake_story_images_checked",
        "public_keepsake_download_links_checked",
        "public_keepsake_collector_open_events_checked",
        "public_keepsake_collector_download_events_checked",
        "public_keepsake_story_buttons_checked",
        "public_keepsake_route_links_checked",
        "public_keepsake_plan_links_checked",
        "public_keepsake_practice_cards_checked",
        "public_keepsake_practice_plan_links_checked",
        "public_keepsake_practice_route_links_checked",
        "public_keepsake_practice_print_buttons_checked",
        "public_keepsake_free_asset_cards_checked",
        "public_keepsake_free_asset_events_checked",
        "public_keepsake_free_asset_request_mailtos_checked",
        "public_keepsake_safety_bridge_sections_checked",
        "public_keepsake_safety_bridge_links_checked",
        "public_keepsake_waitlist_cards_checked",
        "public_keepsake_waitlist_mailtos_checked",
        "public_keepsake_waitlist_option_mailtos_checked",
        "public_keepsake_waitlist_copy_buttons_checked",
        "public_locale_route_pages_checked",
        "public_locale_route_primary_nav_links_checked",
        "public_locale_route_footer_links_checked",
        "public_locale_route_language_links_checked",
        "public_locale_route_language_matches_checked",
        "public_locale_route_nav_matches_checked",
        "public_locale_route_footer_matches_checked",
        "public_locale_route_footer_exact_pages_checked",
        "public_locale_pages_checked",
        "public_locale_nav_labels_checked",
        "public_locale_footer_labels_checked",
        "public_locale_language_menu_labels_checked",
        "public_locale_active_language_links_checked",
        "public_luna_pages_checked",
        "public_luna_alias_redirects_checked",
        "public_luna_protocol_cards_checked",
        "public_luna_use_cases_checked",
        "public_luna_offer_cards_checked",
        "public_luna_guardian_cards_checked",
        "public_luna_guardian_repair_links_checked",
        "public_luna_guardian_supply_links_checked",
        "public_luna_hero_ctas_checked",
        "public_luna_use_case_ctas_checked",
        "public_luna_offer_ctas_checked",
        "public_luna_product_pack_cards_checked",
        "public_luna_product_pack_ctas_checked",
        "public_luna_resume_templates_checked",
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
        "public_quiz_flow_cases_checked",
        "public_quiz_flow_results_checked",
        "public_quiz_flow_ctas_checked",
        "public_quiz_flow_affiliate_links_checked",
        "public_quiz_flow_disclosures_checked",
        "public_revenue_path_pages_checked",
        "public_revenue_path_quiz_assets_checked",
        "public_revenue_path_results_checked",
        "public_revenue_path_result_url_fields_checked",
        "public_revenue_path_result_text_fields_checked",
        "public_revenue_path_internal_targets_checked",
        "public_revenue_path_affiliate_links_checked",
        "public_revenue_path_starter_kits_checked",
        "public_revenue_path_supply_product_packs_checked",
        "public_revenue_path_luna_pages_checked",
        "public_revenue_path_luna_product_links_checked",
        "public_revenue_path_luna_product_slugs_checked",
        "public_revenue_path_funnel_revenue_events_checked",
        "public_quiz_assets_checked",
        "public_quiz_questions_checked",
        "public_quiz_results_checked",
        "public_quiz_guide_urls_checked",
        "public_quiz_story_images_checked",
        "public_quiz_story_ctas_checked",
        "public_quiz_starter_steps_checked",
        "public_repair_plan_pages_checked",
        "public_repair_plan_hero_events_checked",
        "public_repair_plan_day_cards_checked",
        "public_repair_plan_worksheet_fields_checked",
        "public_repair_plan_worksheet_actions_checked",
        "public_repair_plan_asset_sections_checked",
        "public_repair_plan_asset_cards_checked",
        "public_repair_plan_asset_links_checked",
        "public_repair_plan_asset_events_checked",
        "public_repair_plan_guardian_cards_checked",
        "public_repair_plan_guardian_action_events_checked",
        "public_repair_plan_guardian_supply_links_checked",
        "public_repair_plan_guardian_character_links_checked",
        "public_repair_plan_guardian_luna_links_checked",
        "public_repair_plan_guardian_affiliate_links_checked",
        "public_repair_plan_resume_templates_checked",
        "public_repair_plan_resume_events_checked",
        "public_repair_plan_safety_sections_checked",
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
        "public_supply_pages_checked",
        "public_supply_hero_events_checked",
        "public_supply_entry_events_checked",
        "public_supply_quick_cards_checked",
        "public_supply_quick_events_checked",
        "public_supply_route_cards_checked",
        "public_supply_route_action_events_checked",
        "public_supply_guide_links_checked",
        "public_supply_luna_links_checked",
        "public_supply_route_request_mailtos_checked",
        "public_supply_route_product_stacks_checked",
        "public_supply_route_product_links_checked",
        "public_supply_route_product_events_checked",
        "public_supply_copy_buttons_checked",
        "public_supply_affiliate_links_checked",
        "public_supply_affiliate_book_cards_checked",
        "public_supply_affiliate_route_tags_checked",
        "public_supply_wishlist_cards_checked",
        "public_supply_wishlist_formats_checked",
        "public_supply_wishlist_mailtos_checked",
        "public_supply_decision_sections_checked",
        "public_supply_decision_cards_checked",
        "public_supply_decision_links_checked",
        "public_supply_safety_sections_checked",
        "public_supply_safety_bridge_sections_checked",
        "public_supply_safety_bridge_links_checked",
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
        "public_trust_about_garden_pass_cards_checked",
        "public_trust_about_hero_actions_checked",
        "public_trust_about_hero_events_checked",
        "public_trust_about_cards_checked",
        "public_trust_theory_domain_cards_checked",
        "public_trust_theory_domain_events_checked",
        "public_trust_theory_guardian_cards_checked",
        "public_trust_theory_faq_cards_checked",
        "public_trust_theory_hero_actions_checked",
        "public_trust_theory_hero_events_checked",
        "public_trust_about_theory_distinction_checks",
        "public_trust_action_routes_checked",
        "public_trust_action_events_checked",
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
        "funnel_event_catalogs_checked",
        "funnel_events_checked",
        "funnel_event_categories_checked",
        "funnel_event_roles_checked",
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
        "site_health_config_checks",
        "site_health_config_check_tuples_parsed",
        "site_health_config_commands",
        "site_health_config_scripts",
        "site_health_config_python_scripts_compiled",
        "site_health_config_node_scripts",
        "site_health_config_node_scripts_checked",
        "site_health_config_node_missing",
        "site_health_config_important_keys",
        "site_health_config_retry_names",
        "site_health_config_predeploy_scripts",
        "site_health_config_predeploy_python_scripts_compiled",
        "site_health_config_missing_predeploy_scripts",
        "site_health_config_issue_metric_keys",
        "site_health_config_duplicate_check_names",
        "site_health_config_duplicate_check_commands",
        "site_health_config_duplicate_script_paths",
        "site_health_config_missing_scripts",
        "site_health_config_duplicate_important_keys",
        "site_health_config_unknown_retry_names",
        "site_health_config_missing_issue_important_keys",
        "site_health_config_malformed_checks",
        "site_health_config_invalid_timeouts",
        "site_health_config_public_flag_mismatches",
        "timed_out",
        "error",
    ]
    emitted_keys: set[str] = set()
    for key in important_keys:
        if key in values:
            lines.append(f"- {key}: `{values[key]}`")
            emitted_keys.add(key)
    for key in sorted(values):
        if key in emitted_keys:
            continue
        if key.endswith("_attempts") or key.endswith("_retry_status"):
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
            values[f"{name.removesuffix('_smoke')}_retry_status"] = retry_status
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
