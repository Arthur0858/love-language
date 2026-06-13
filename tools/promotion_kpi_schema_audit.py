#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
FUNNEL_EVENTS_PATH = ROOT / "funnel-events.json"
COMMERCE_CATALOG_PATH = ROOT / "commerce-catalog.json"
KPI_TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PLATFORM_KPI_TRACKER_PATH = PROMOTION_DIR / "platform-kpi-tracker.csv"
PLATFORM_PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
ATTRIBUTION_RECONCILIATION_PATH = PROMOTION_DIR / "attribution-reconciliation.csv"

IDENTITY_ROUTE_FIELDS = [
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
]
REVENUE_BRIDGE_FIELDS = [
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]
POST_METRIC_FIELDS = [
    "views",
    "likes",
    "comments",
    "shares",
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    *IDENTITY_ROUTE_FIELDS,
    *REVENUE_BRIDGE_FIELDS,
]
PROFILE_METRIC_FIELDS = [
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    *IDENTITY_ROUTE_FIELDS,
    *REVENUE_BRIDGE_FIELDS,
]
ATTRIBUTION_REQUIRED_FIELDS = [
    "source_type",
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "content_angle",
    "utm_content",
    "tracked_url",
    "kpi_row_status",
    "decision_stage",
    "next_writeback",
    "contact_email_match",
]
ATTRIBUTION_STATUS_VALUES = {"filled", "ready_for_backfill", "profile_link_only"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def csv_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def missing(required: list[str] | set[str], available: list[str] | set[str]) -> list[str]:
    return sorted(set(required).difference(available))


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    kit = load_json(KIT_PATH)
    commerce = load_json(COMMERCE_CATALOG_PATH)
    funnel_catalog = load_json(FUNNEL_EVENTS_PATH)
    catalog_events = {
        str(item.get("name", "")): item
        for item in funnel_catalog.get("events", [])
        if isinstance(item, dict) and item.get("name")
    }
    kpi_fields = list(kit.get("kpiFields") or [])
    measurement = kit.get("measurementPlan") if isinstance(kit.get("measurementPlan"), dict) else {}
    secondary_kpis = set(measurement.get("secondaryKpis") or [])
    event_kpi_map = measurement.get("eventKpiMap") if isinstance(measurement.get("eventKpiMap"), list) else []
    event_kpis = {str(item.get("kpi", "")) for item in event_kpi_map if isinstance(item, dict)}
    event_names = [
        str(event)
        for item in event_kpi_map
        if isinstance(item, dict)
        for event in item.get("events", [])
    ]
    revenue_bridge = measurement.get("revenueBridgeKpis") if isinstance(measurement.get("revenueBridgeKpis"), list) else []
    revenue_bridge_kpis = {str(item.get("field", "")) for item in revenue_bridge if isinstance(item, dict)}
    derived_rate_ids = {
        str(item.get("id", ""))
        for item in measurement.get("derivedRates", [])
        if isinstance(item, dict)
    }
    decision_rule_ids = {
        str(item.get("id", ""))
        for item in measurement.get("decisionRules", [])
        if isinstance(item, dict)
    }

    kpi_header = csv_header(KPI_TRACKER_PATH)
    platform_header = csv_header(PLATFORM_KPI_TRACKER_PATH)
    profile_header = csv_header(PLATFORM_PROFILE_TRACKER_PATH)
    attribution_header = csv_header(ATTRIBUTION_RECONCILIATION_PATH)
    attribution_rows = csv_rows(ATTRIBUTION_RECONCILIATION_PATH)
    commerce_items = commerce.get("items") if isinstance(commerce.get("items"), list) else []
    commerce_playbook = commerce.get("revenuePlaybook") if isinstance(commerce.get("revenuePlaybook"), list) else []
    commerce_item_ids = {str(item.get("id", "")) for item in commerce_items if isinstance(item, dict)}

    if kpi_header != kpi_fields:
        issues.append("kpi-tracker.csv header must exactly match promotion-kit.json kpiFields")
    for field in POST_METRIC_FIELDS:
        if field not in kpi_fields:
            issues.append(f"promotion-kit kpiFields missing post metric {field}")
    for field in missing(POST_METRIC_FIELDS, platform_header):
        issues.append(f"platform-kpi-tracker.csv missing metric field {field}")
    for field in missing(PROFILE_METRIC_FIELDS, profile_header):
        issues.append(f"platform-profile-tracker.csv missing profile metric field {field}")
    for field in missing(ATTRIBUTION_REQUIRED_FIELDS, attribution_header):
        issues.append(f"attribution-reconciliation.csv missing required field {field}")

    expected_event_kpis = set(["site_clicks", "quiz_starts", "quiz_completions", *IDENTITY_ROUTE_FIELDS, *REVENUE_BRIDGE_FIELDS])
    for field in missing(expected_event_kpis, event_kpis):
        issues.append(f"measurementPlan.eventKpiMap missing KPI {field}")
    for field in missing(REVENUE_BRIDGE_FIELDS, revenue_bridge_kpis):
        issues.append(f"measurementPlan.revenueBridgeKpis missing KPI {field}")
    for field in missing(set(["site_clicks", "quiz_starts", *IDENTITY_ROUTE_FIELDS, *REVENUE_BRIDGE_FIELDS]), secondary_kpis):
        issues.append(f"measurementPlan.secondaryKpis missing KPI {field}")

    for field in ("lead_capture_rate", "revenue_intent_rate", "keepsake_save_rate", "route_interest_rate"):
        if field not in derived_rate_ids:
            issues.append(f"measurementPlan.derivedRates missing {field}")
    for field in ("build_owned_asset", "test_soft_offer", "scale_guardian"):
        if field not in decision_rule_ids:
            issues.append(f"measurementPlan.decisionRules missing {field}")

    for item in event_kpi_map:
        if not isinstance(item, dict):
            continue
        kpi = str(item.get("kpi", ""))
        if kpi in expected_event_kpis and not item.get("events"):
            issues.append(f"eventKpiMap {kpi} must list source events")
        for event_name in item.get("events", []):
            event = catalog_events.get(str(event_name))
            if not event:
                issues.append(f"eventKpiMap {kpi} references missing funnel event {event_name}")
                continue
            if int(event.get("count") or 0) <= 0:
                issues.append(f"eventKpiMap {kpi} references zero-count funnel event {event_name}")
            if not event.get("category") or not event.get("role"):
                issues.append(f"funnel event {event_name} must include category and role")
            if not event.get("pages"):
                issues.append(f"funnel event {event_name} must list pages")
        if kpi in REVENUE_BRIDGE_FIELDS and not item.get("manualSources"):
            issues.append(f"eventKpiMap {kpi} must list manual sources")
        if kpi in REVENUE_BRIDGE_FIELDS and not item.get("reviewUse"):
            issues.append(f"eventKpiMap {kpi} must explain review use")

    for play in commerce_playbook:
        if not isinstance(play, dict):
            continue
        play_id = str(play.get("id", ""))
        for event_name in play.get("primaryEvents", []):
            if str(event_name) not in catalog_events:
                issues.append(f"commerce revenue playbook {play_id} references missing funnel event {event_name}")

    for item in commerce_items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", ""))
        conversion = str(item.get("conversion", ""))
        if conversion and conversion not in catalog_events:
            issues.append(f"commerce item {item_id} references missing conversion event {conversion}")

    for task in kit.get("publishingTasks", []):
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("taskId", "<unknown>"))
        bridge = task.get("monetizationBridge") if isinstance(task.get("monetizationBridge"), dict) else {}
        for event_name in bridge.get("successEvents", []):
            if str(event_name) not in catalog_events:
                issues.append(f"publishing task {task_id} monetizationBridge references missing funnel event {event_name}")
        for field in ("primaryFreeItemId", "ownedLeadItemId"):
            item_id = str(bridge.get(field, ""))
            if item_id not in commerce_item_ids:
                issues.append(f"publishing task {task_id} monetizationBridge.{field} missing from commerce catalog")
        for item_id in bridge.get("lunaProductIds", []) + bridge.get("affiliateItemIds", []):
            if str(item_id) not in commerce_item_ids:
                issues.append(f"publishing task {task_id} monetizationBridge item {item_id} missing from commerce catalog")

    attribution_statuses = {row.get("kpi_row_status", "") for row in attribution_rows}
    if not attribution_statuses.issubset(ATTRIBUTION_STATUS_VALUES):
        issues.append(f"attribution-reconciliation.csv has unsupported kpi_row_status values: {sorted(attribution_statuses)}")
    if not any(row.get("source_type") == "profile" for row in attribution_rows):
        issues.append("attribution-reconciliation.csv must include profile rows")
    if not any(row.get("source_type") == "shorts" for row in attribution_rows):
        issues.append("attribution-reconciliation.csv must include shorts rows")

    stats = {
        "promotion_kpi_schema_fields": len(kpi_fields),
        "promotion_kpi_schema_post_metrics": len(POST_METRIC_FIELDS),
        "promotion_kpi_schema_profile_metrics": len(PROFILE_METRIC_FIELDS),
        "promotion_kpi_schema_event_kpis": len(event_kpis),
        "promotion_kpi_schema_event_names": len(event_names),
        "promotion_kpi_schema_catalog_events": len(catalog_events),
        "promotion_kpi_schema_revenue_bridge_kpis": len(revenue_bridge_kpis),
        "promotion_kpi_schema_commerce_items": len(commerce_item_ids),
        "promotion_kpi_schema_commerce_playbooks": len(commerce_playbook),
        "promotion_kpi_schema_attribution_rows": len(attribution_rows),
        "promotion_kpi_schema_issues": len(issues),
    }
    return stats, issues


def main() -> int:
    stats, issues = validate()
    for key, value in stats.items():
        print(f"{key}={value}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
