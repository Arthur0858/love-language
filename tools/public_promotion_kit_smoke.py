#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
EXPECTED_GUARDIANS = {"iris", "noah", "vivian", "claire", "dora"}
EXPECTED_CAMPAIGN = "first_round_quiz_completion"
EXPECTED_KPI_FIELDS = {
    "views",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "luna_clicks",
    "notes",
}
EXPECTED_PLAYBOOK_SEQUENCE = [
    "identity_retention_first",
    "owned_supply_lead",
    "luna_pack_revenue",
    "affiliate_book_revenue",
]
EXPECTED_BRIDGE_EVENTS = {
    "quiz_complete",
    "free_keepsake_download",
    "supply_route_asset_request",
    "luna_gumroad_pack_click",
    "supply_route_affiliate_book",
}


def request_json(base_url: str) -> tuple[dict, str]:
    url = urljoin(base_url.rstrip("/") + "/", "promotion-kit.json")
    request = Request(url, headers={"User-Agent": "LoveTypes promotion kit smoke/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=20) as response:
        text = response.read().decode("utf-8")
        return json.loads(text), response.headers.get("content-type", "")


def local_calendar_rows() -> list[dict[str, str]]:
    path = ROOT / "docs" / "promotion" / "first-round" / "publishing-calendar.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_tracked_url(source: str, value: str) -> list[str]:
    issues: list[str] = []
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
        issues.append(f"{source}: trackedUrl should point to https://lovetypes.tw/start/")
    expected = {
        "utm_source": "shorts",
        "utm_medium": "social",
        "utm_campaign": EXPECTED_CAMPAIGN,
    }
    for key, expected_value in expected.items():
        if query.get(key, [""])[0] != expected_value:
            issues.append(f"{source}: trackedUrl missing {key}={expected_value}")
    if not query.get("utm_content", [""])[0]:
        issues.append(f"{source}: trackedUrl missing utm_content")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes promotion kit metadata.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/") or DEFAULT_BASE_URL
    issues: list[str] = []
    kit, content_type = request_json(base_url)
    if "json" not in content_type:
        issues.append(f"/promotion-kit.json: expected JSON content type, got {content_type!r}")

    local_rows = local_calendar_rows()
    calendar = kit.get("publishingCalendar")
    if not isinstance(calendar, list) or len(calendar) != 15:
        issues.append(f"/promotion-kit.json: expected 15 publishingCalendar rows, got {len(calendar) if isinstance(calendar, list) else 'invalid'}")
        calendar = []
    if len(local_rows) != len(calendar):
        issues.append(f"/promotion-kit.json: local calendar has {len(local_rows)} rows, public kit has {len(calendar)}")

    if kit.get("campaignId") != "lovetypes-first-round-quiz-completion":
        issues.append("/promotion-kit.json: campaignId should match the scripts library campaign id")
    if kit.get("utmCampaign") != EXPECTED_CAMPAIGN:
        issues.append(f"/promotion-kit.json: utmCampaign should be {EXPECTED_CAMPAIGN}")
    if kit.get("primaryUrl") != "https://lovetypes.tw/start/":
        issues.append("/promotion-kit.json: primaryUrl should be the dedicated quiz start URL")
    if kit.get("scriptCount") != 15 or kit.get("campaignCount") != 15:
        issues.append("/promotion-kit.json: scriptCount and campaignCount should both be 15")
    if kit.get("taskCount") != 15:
        issues.append("/promotion-kit.json: taskCount should be 15")
    if kit.get("guardianCount") != 5:
        issues.append("/promotion-kit.json: guardianCount should be 5")
    kpi_fields = kit.get("kpiFields")
    if not isinstance(kpi_fields, list) or not EXPECTED_KPI_FIELDS.issubset(kpi_fields):
        issues.append("/promotion-kit.json: missing expected KPI fields")
    measurement = kit.get("measurementPlan")
    if not isinstance(measurement, dict):
        issues.append("/promotion-kit.json: measurementPlan should be an object")
        measurement = {}
    if measurement.get("primaryKpi") != "quiz_completions":
        issues.append("/promotion-kit.json: measurementPlan.primaryKpi should be quiz_completions")
    secondary = measurement.get("secondaryKpis")
    if not isinstance(secondary, list) or not {"site_clicks", "quiz_starts", "luna_clicks", "keepsake_clicks"}.issubset(secondary):
        issues.append("/promotion-kit.json: measurementPlan.secondaryKpis missing required fields")
    derived = measurement.get("derivedRates")
    if not isinstance(derived, list) or len(derived) < 4:
        issues.append("/promotion-kit.json: measurementPlan.derivedRates should include at least four rates")
    else:
        expected_rate_ids = {"site_click_rate", "quiz_start_rate", "quiz_completion_rate", "route_interest_rate"}
        rate_ids = {item.get("id") for item in derived if isinstance(item, dict)}
        if not expected_rate_ids.issubset(rate_ids):
            issues.append("/promotion-kit.json: measurementPlan.derivedRates missing required rate ids")
        for item in derived:
            if not isinstance(item, dict) or not item.get("formula") or not item.get("use"):
                issues.append("/promotion-kit.json: measurementPlan derived rates should include formula and use")
                break
    rules = measurement.get("decisionRules")
    if not isinstance(rules, list) or len(rules) < 5:
        issues.append("/promotion-kit.json: measurementPlan.decisionRules should include at least five rules")
    else:
        rule_ids = {item.get("id") for item in rules if isinstance(item, dict)}
        if not {"scale_guardian", "fix_landing", "fix_quiz_flow", "monetize_route", "pause_angle"}.issubset(rule_ids):
            issues.append("/promotion-kit.json: measurementPlan.decisionRules missing required rule ids")
    weekly = measurement.get("weeklyReviewChecklist")
    if not isinstance(weekly, list) or len(weekly) < 5:
        issues.append("/promotion-kit.json: measurementPlan.weeklyReviewChecklist should include at least five steps")

    seen_scripts: set[str] = set()
    seen_guardians: set[str] = set()
    seen_contents: set[str] = set()
    for index, row in enumerate(calendar, start=1):
        source = f"/promotion-kit.json:publishingCalendar[{index}]"
        guardian = row.get("guardianId")
        script_id = row.get("scriptId")
        utm_content = row.get("utmContent")
        if guardian not in EXPECTED_GUARDIANS:
            issues.append(f"{source}: unexpected guardianId {guardian!r}")
        else:
            seen_guardians.add(guardian)
        if not isinstance(script_id, str) or not script_id.startswith("lt-s"):
            issues.append(f"{source}: invalid scriptId {script_id!r}")
        elif script_id in seen_scripts:
            issues.append(f"{source}: duplicate scriptId {script_id}")
        else:
            seen_scripts.add(script_id)
        if not utm_content:
            issues.append(f"{source}: missing utmContent")
        elif utm_content in seen_contents:
            issues.append(f"{source}: duplicate utmContent {utm_content}")
        else:
            seen_contents.add(utm_content)
        if row.get("utmCampaign") != EXPECTED_CAMPAIGN:
            issues.append(f"{source}: unexpected utmCampaign {row.get('utmCampaign')!r}")
        tracked = row.get("trackedUrl", "")
        issues.extend(validate_tracked_url(source, tracked))
        if utm_content and parse_qs(urlparse(tracked).query).get("utm_content", [""])[0] != utm_content:
            issues.append(f"{source}: trackedUrl utm_content should match utmContent")

    if seen_guardians != EXPECTED_GUARDIANS:
        issues.append(f"/promotion-kit.json: missing guardians {sorted(EXPECTED_GUARDIANS - seen_guardians)}")

    tasks = kit.get("publishingTasks")
    if not isinstance(tasks, list) or len(tasks) != 15:
        issues.append(f"/promotion-kit.json: expected 15 publishingTasks, got {len(tasks) if isinstance(tasks, list) else 'invalid'}")
        tasks = []
    task_script_ids: set[str] = set()
    task_utm_contents: set[str] = set()
    for index, task in enumerate(tasks, start=1):
        source = f"/promotion-kit.json:publishingTasks[{index}]"
        if not isinstance(task, dict):
            issues.append(f"{source}: task should be an object")
            continue
        script_id = task.get("scriptId")
        utm_content = task.get("utmContent")
        task_script_ids.add(script_id)
        task_utm_contents.add(utm_content)
        if task.get("taskId") != f"publish-{script_id}":
            issues.append(f"{source}: taskId should be publish-{script_id}")
        if task.get("guardianId") not in EXPECTED_GUARDIANS:
            issues.append(f"{source}: unexpected guardianId {task.get('guardianId')!r}")
        if task.get("utmCampaign") != EXPECTED_CAMPAIGN:
            issues.append(f"{source}: unexpected utmCampaign {task.get('utmCampaign')!r}")
        if task.get("primaryCta") != "完成 15 題測驗，找到你的情感守護者":
            issues.append(f"{source}: primaryCta should use the first-round CTA")
        for key in ("title", "hook", "commentCta"):
            if not isinstance(task.get(key), str) or not task[key]:
                issues.append(f"{source}: missing {key}")
        if not isinstance(task.get("subtitleLines"), list) or len(task["subtitleLines"]) < 5:
            issues.append(f"{source}: subtitleLines should include at least five lines")
        if not isinstance(task.get("visualSuggestions"), list) or len(task["visualSuggestions"]) < 2:
            issues.append(f"{source}: visualSuggestions should include at least two items")
        conversion_path = task.get("conversionPath")
        if not isinstance(conversion_path, dict):
            issues.append(f"{source}: conversionPath should be an object")
            conversion_path = {}
        guardian_id = task.get("guardianId")
        expected_paths = {
            "quizEntry": "https://lovetypes.tw/start/",
            "guardianProfile": f"https://lovetypes.tw/characters/{guardian_id}/",
            "supplyRoute": f"https://lovetypes.tw/resources/#supply-{guardian_id}",
            "repairPlan": f"https://lovetypes.tw/repair-plan/#plan-{guardian_id}",
            "lunaScene": f"https://lovetypes.tw/luna-yoga-music/#luna-{guardian_id}",
            "keepsake": f"https://lovetypes.tw/keepsakes/#keepsake-{guardian_id}",
            "contactRequest": "https://lovetypes.tw/contact/#luna-supply-request",
        }
        for key, expected_value in expected_paths.items():
            if conversion_path.get(key) != expected_value:
                issues.append(f"{source}: conversionPath.{key} should be {expected_value}")
        bridge = task.get("monetizationBridge")
        if not isinstance(bridge, dict):
            issues.append(f"{source}: monetizationBridge should be an object")
            bridge = {}
        if bridge.get("playbookSequence") != EXPECTED_PLAYBOOK_SEQUENCE:
            issues.append(f"{source}: monetizationBridge.playbookSequence should match revenue playbook order")
        if bridge.get("primaryFreeItemId") != f"free-keepsake-{guardian_id}":
            issues.append(f"{source}: monetizationBridge.primaryFreeItemId should match guardian")
        if bridge.get("ownedLeadItemId") != f"supply-wishlist-{guardian_id}":
            issues.append(f"{source}: monetizationBridge.ownedLeadItemId should match guardian")
        luna_products = bridge.get("lunaProductIds")
        if not isinstance(luna_products, list) or len(luna_products) < 6 or not all(isinstance(item, str) and item.startswith("luna-") for item in luna_products):
            issues.append(f"{source}: monetizationBridge.lunaProductIds should include Luna product item ids")
        affiliate_items = bridge.get("affiliateItemIds")
        if not isinstance(affiliate_items, list) or len(affiliate_items) < 4 or not all(isinstance(item, str) and item.startswith("affiliate-book-") for item in affiliate_items):
            issues.append(f"{source}: monetizationBridge.affiliateItemIds should include affiliate item ids")
        bridge_events = bridge.get("successEvents")
        if not isinstance(bridge_events, list) or not EXPECTED_BRIDGE_EVENTS.issubset(set(bridge_events)):
            issues.append(f"{source}: monetizationBridge.successEvents missing required events")
        for key in ("recommendedFirstAction", "safetyNote"):
            if not isinstance(bridge.get(key), str) or not bridge[key]:
                issues.append(f"{source}: monetizationBridge missing {key}")
        checklist = task.get("publishChecklist")
        if not isinstance(checklist, list) or len(checklist) < 4:
            issues.append(f"{source}: publishChecklist should include four guardrails")
        kpi_task_fields = task.get("kpiFieldsToFill")
        if not isinstance(kpi_task_fields, list) or not EXPECTED_KPI_FIELDS.issubset(kpi_task_fields):
            issues.append(f"{source}: kpiFieldsToFill missing expected fields")
        tracked = task.get("trackedUrl", "")
        issues.extend(validate_tracked_url(source, tracked))
        if utm_content and parse_qs(urlparse(tracked).query).get("utm_content", [""])[0] != utm_content:
            issues.append(f"{source}: trackedUrl utm_content should match utmContent")
    if task_script_ids != seen_scripts:
        issues.append("/promotion-kit.json: publishingTasks scriptIds should match publishingCalendar")
    if task_utm_contents != seen_contents:
        issues.append("/promotion-kit.json: publishingTasks utmContents should match publishingCalendar")

    print(f"public_promotion_kit_campaigns_checked={len(calendar)}")
    print(f"public_promotion_kit_tasks_checked={len(tasks)}")
    print(f"public_promotion_kit_guardians_checked={len(seen_guardians)}")
    print(f"public_promotion_kit_scripts_checked={len(seen_scripts)}")
    print(f"public_promotion_kit_utm_contents_checked={len(seen_contents)}")
    print(f"public_promotion_kit_kpi_fields_checked={len(kpi_fields) if isinstance(kpi_fields, list) else 0}")
    print(f"public_promotion_kit_measurement_rules_checked={len(measurement.get('decisionRules', [])) if isinstance(measurement, dict) else 0}")
    print(f"public_promotion_kit_monetization_bridges_checked={sum(1 for task in tasks if isinstance(task, dict) and isinstance(task.get('monetizationBridge'), dict))}")
    print(f"public_promotion_kit_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
