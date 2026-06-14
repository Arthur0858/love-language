#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
CSV_OUTPUT = PROMOTION_DIR / "platform-profile-tracker.csv"
JSON_OUTPUT = PROMOTION_DIR / "platform-profile-tracker.json"
MD_OUTPUT = PROMOTION_DIR / "platform-profile-tracker.md"
FIELDNAMES = [
    "platform",
    "label",
    "profile_link",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "status",
    "profile_link_set_date",
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
    "notes",
]
NUMERIC_FIELDS = FIELDNAMES[9:23]
STATUS_VALUES = ("planned", "set", "live", "paused", "blocked")
CONFIGURED_STATUSES = ("set", "live")
MINIMUM_WEEKLY_FIELDS = ("profile_clicks", "site_clicks", "quiz_starts", "quiz_completions")
DEFAULT_PLATFORM_ORDER = ("youtube_shorts",)


def expected_platform_sources(kit: dict) -> dict[str, str]:
    sources: dict[str, str] = {}
    for item in kit.get("platformProfileSetup", []):
        platform = str(item.get("platformId", ""))
        if platform:
            sources[platform] = parse_utm(str(item.get("profileLink", ""))).get("utm_source", "")
    return sources


def profile_tracker_policy(platform_sources: dict[str, str]) -> dict[str, object]:
    platform_order = tuple(platform for platform in DEFAULT_PLATFORM_ORDER if platform in platform_sources)
    platform_order = platform_order + tuple(platform for platform in platform_sources if platform not in platform_order)
    return {
        "statusValues": list(STATUS_VALUES),
        "configuredStatuses": list(CONFIGURED_STATUSES),
        "platformOrder": list(platform_order),
        "expectedPlatformSources": platform_sources,
        "minimumWeeklyFields": list(MINIMUM_WEEKLY_FIELDS),
        "numericFields": list(NUMERIC_FIELDS),
        "rule": "Bio/Profile link performance stays in platform-profile-tracker.csv; single-video post performance stays in platform-kpi-tracker.csv and kpi-tracker.csv.",
        "setLiveRequiresDate": True,
        "startPath": "/start/",
        "campaign": "first_round_quiz_completion",
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_utm(url: str) -> dict[str, str]:
    query = parse_qs(urlparse(url).query)
    return {key: query.get(key, [""])[0] for key in ("utm_source", "utm_medium", "utm_campaign", "utm_content")}


def read_existing(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {row.get("platform", ""): row for row in rows if row.get("platform")}


def build_rows(kit: dict, existing: dict[str, dict[str, str]] | None = None) -> list[dict[str, str]]:
    existing = existing or {}
    rows: list[dict[str, str]] = []
    for item in kit.get("platformProfileSetup", []):
        platform = str(item.get("platformId", ""))
        profile_link = str(item.get("profileLink", ""))
        utm = parse_utm(profile_link)
        previous = existing.get(platform, {})
        row = {
            "platform": platform,
            "label": str(item.get("label", "")),
            "profile_link": profile_link,
            "utm_source": utm["utm_source"],
            "utm_medium": utm["utm_medium"],
            "utm_campaign": utm["utm_campaign"],
            "utm_content": utm["utm_content"],
            "status": previous.get("status", "planned") or "planned",
            "profile_link_set_date": previous.get("profile_link_set_date", ""),
            "notes": previous.get("notes", str(item.get("linkLimitNote", ""))),
        }
        for field in NUMERIC_FIELDS:
            row[field] = previous.get(field, "")
        rows.append({field: row.get(field, "") for field in FIELDNAMES})
    platform_sources = expected_platform_sources(kit)
    platform_order = tuple(platform for platform in DEFAULT_PLATFORM_ORDER if platform in platform_sources)
    platform_order = platform_order + tuple(platform for platform in platform_sources if platform not in platform_order)
    rows.sort(key=lambda row: platform_order.index(row["platform"]) if row["platform"] in platform_order else 99)
    return rows


def validate_rows(rows: list[dict[str, str]], kit: dict) -> list[str]:
    issues: list[str] = []
    platform_sources = expected_platform_sources(kit)
    platform_order = tuple(platform for platform in DEFAULT_PLATFORM_ORDER if platform in platform_sources)
    platform_order = platform_order + tuple(platform for platform in platform_sources if platform not in platform_order)
    policy = profile_tracker_policy(platform_sources)
    if tuple(policy["statusValues"]) != STATUS_VALUES:
        issues.append("profileTrackerPolicy.statusValues does not match generator policy")
    if tuple(policy["configuredStatuses"]) != CONFIGURED_STATUSES:
        issues.append("profileTrackerPolicy.configuredStatuses does not match generator policy")
    if tuple(policy["platformOrder"]) != platform_order:
        issues.append("profileTrackerPolicy.platformOrder does not match generator policy")
    if tuple(policy["minimumWeeklyFields"]) != MINIMUM_WEEKLY_FIELDS:
        issues.append("profileTrackerPolicy.minimumWeeklyFields does not match generator policy")
    if len(rows) != len(platform_sources):
        issues.append(f"expected {len(platform_sources)} platform tracker rows, got {len(rows)}")
    seen: set[str] = set()
    for row in rows:
        platform = row.get("platform", "")
        label = platform or "<platform>"
        if platform not in platform_sources:
            issues.append(f"{label}: unexpected platform")
            continue
        if platform in seen:
            issues.append(f"{label}: duplicate tracker row")
        seen.add(platform)
        parsed = urlparse(row.get("profile_link", ""))
        if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
            issues.append(f"{label}: profile_link should point to https://lovetypes.tw/start/")
        expected = {
            "utm_source": platform_sources[platform],
            "utm_medium": "social_profile",
            "utm_campaign": "first_round_quiz_completion",
            "utm_content": f"{platform}_bio",
        }
        for key, expected_value in expected.items():
            if row.get(key) != expected_value:
                issues.append(f"{label}: {key} should be {expected_value}")
        if row.get("status") not in STATUS_VALUES:
            issues.append(f"{label}: invalid status {row.get('status')}")
        if row.get("status") in CONFIGURED_STATUSES and not (row.get("profile_link_set_date") or "").strip():
            issues.append(f"{label}: status {row.get('status')} requires profile_link_set_date")
        for field in NUMERIC_FIELDS:
            value = (row.get(field) or "").strip()
            if value:
                try:
                    if int(float(value.replace(",", ""))) < 0:
                        issues.append(f"{label}: {field} should not be negative")
                except ValueError:
                    issues.append(f"{label}: {field} should be numeric if filled")
    missing = set(platform_sources) - seen
    if missing:
        issues.append(f"missing platform tracker rows: {', '.join(sorted(missing))}")
    return issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(rows: list[dict[str, str]]) -> str:
    lines = [
        "# LoveTypes 平台首頁 KPI 追蹤表",
        "",
        f"- 產生日期：{date.today().isoformat()}",
        f"- 平台數：{len(rows)}",
        "- 用途：追蹤 Bio/Profile link 帶來的測驗與收益承接，不和單支 Shorts 成效混在一起。",
        f"- 狀態規則：{', '.join(f'`{status}`' for status in STATUS_VALUES)}；`set/live` 必須填 `profile_link_set_date`。",
        f"- 每週最小回填欄位：{', '.join(f'`{field}`' for field in MINIMUM_WEEKLY_FIELDS)}。",
        "",
        "## 使用方式",
        "",
        "- 完成平台首頁設定後，把 `status` 改成 `set` 或 `live`，並填入 `profile_link_set_date`。",
        "- 每週回填 `profile_clicks`、`site_clicks`、`quiz_starts`、`quiz_completions`。",
        "- 若 Bio/Profile link 也帶來收藏、補給、Luna、聯盟或 Contact 意圖，回填對應欄位。",
        "- 單支影片成效仍回填 `kpi-tracker.csv`；本表只看平台首頁承接。",
        "",
        "## 平台",
        "",
    ]
    for row in rows:
        lines.extend([
            f"### {row['label']}（`{row['platform']}`）",
            "",
            f"- 狀態：`{row['status']}`",
            f"- Profile link：{row['profile_link']}",
            f"- UTM：`{row['utm_source']} / {row['utm_medium']} / {row['utm_campaign']} / {row['utm_content']}`",
            f"- 設定日期：{row['profile_link_set_date'] or '尚未回填'}",
            f"- 備註：{row['notes']}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(rows: list[dict[str, str]], kit: dict, csv_path: Path, json_path: Path, md_path: Path) -> None:
    write_csv(rows, csv_path)
    payload = {
        "generatedAt": date.today().isoformat(),
        "source": {
            "promotionKit": str(KIT_PATH.relative_to(ROOT)),
        },
        "rowCount": len(rows),
        "profileTrackerPolicy": profile_tracker_policy(expected_platform_sources(kit)),
        "numericFields": NUMERIC_FIELDS,
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(rows), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes platform profile KPI tracker from promotion-kit platformProfileSetup.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--csv-output", default=str(CSV_OUTPUT))
    parser.add_argument("--json-output", default=str(JSON_OUTPUT))
    parser.add_argument("--md-output", default=str(MD_OUTPUT))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    kit = load_json(Path(args.kit))
    rows = build_rows(kit, read_existing(Path(args.csv_output)))
    issues = validate_rows(rows, kit)
    if not args.check:
        write_outputs(rows, kit, Path(args.csv_output), Path(args.json_output), Path(args.md_output))
        print(f"promotion_platform_profile_tracker={args.csv_output}")
        print(f"promotion_platform_profile_tracker_json={args.json_output}")
        print(f"promotion_platform_profile_tracker_md={args.md_output}")
    print(f"promotion_platform_profile_tracker_rows={len(rows)}")
    print(f"promotion_platform_profile_tracker_numeric_fields={len(NUMERIC_FIELDS)}")
    print(f"promotion_platform_profile_tracker_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
