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
PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
POSTING_QUEUE_PATH = PROMOTION_DIR / "posting-queue.csv"
KPI_TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PLATFORM_KPI_TRACKER_PATH = PROMOTION_DIR / "platform-kpi-tracker.csv"
COMMAND_CENTER_PATH = PROMOTION_DIR / "launch-command-center.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "launch-readiness-gate.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "launch-readiness-gate.json"

EXPECTED_PLATFORM_ORDER = ("youtube_shorts",)
EXPECTED_PLATFORMS = set(EXPECTED_PLATFORM_ORDER)
CAMPAIGN = "first_round_quiz_completion"
REQUIRED_KPI_FIELDS = ("site_clicks", "quiz_starts", "quiz_completions")
CONFIGURED_PROFILE_STATUSES = ("set", "live")
BLOCKER_ORDER = ("set_platform_profile_links", "publish_first_batch", "backfill_first_batch_kpis")
BLOCKER_SEVERITY_BY_ID = {
    "set_platform_profile_links": "launch_blocker",
    "publish_first_batch": "measurement_blocker",
    "backfill_first_batch_kpis": "decision_blocker",
}
PLATFORM_LABELS = {
    "youtube_shorts": "YouTube Shorts",
    "tiktok": "TikTok",
    "instagram_reels": "Instagram Reels",
}


def readiness_policy() -> dict[str, object]:
    return {
        "expectedPlatformCount": len(EXPECTED_PLATFORMS),
        "expectedPlatforms": list(EXPECTED_PLATFORM_ORDER),
        "campaign": CAMPAIGN,
        "startPath": "/start/",
        "configuredProfileStatuses": list(CONFIGURED_PROFILE_STATUSES),
        "requiredKpiFields": list(REQUIRED_KPI_FIELDS),
        "firstBatchWeek": 1,
        "firstBatchSlot": 1,
        "minimumAssetPreparedChecks": len(EXPECTED_PLATFORMS),
        "blockerOrder": list(BLOCKER_ORDER),
        "blockerSeverityById": BLOCKER_SEVERITY_BY_ID,
        "blockerReleaseConditions": {
            "set_platform_profile_links": "All platform-profile-tracker.csv rows are marked set/live with valid /start/ campaign profile links.",
            "publish_first_batch": "The first-batch posting-queue.csv platform rows are marked published and have post_url values.",
            "backfill_first_batch_kpis": "At least the first-batch KPI rows have source-checked values for site_clicks, quiz_starts, and quiz_completions.",
        },
        "rule": "YouTube profile link 設定完成後才發布首批；首批發布與 KPI 回填前維持空資料安全模式。",
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def is_start_campaign_url(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
        return False
    query = parse_qs(parsed.query)
    return query.get("utm_campaign") == [CAMPAIGN]


def is_profile_configured(row: dict[str, str]) -> bool:
    return (row.get("status") or "").strip() in CONFIGURED_PROFILE_STATUSES


def is_kpi_filled(row: dict[str, str]) -> bool:
    return any(parse_int(row.get(field)) > 0 for field in REQUIRED_KPI_FIELDS)


def count_first_batch_kpi_rows(rows: list[dict[str, str]], policy: dict[str, object]) -> int:
    return sum(
        1
        for row in rows
        if (row.get("week") or "").strip() == str(policy["firstBatchWeek"])
        and (row.get("slot") or "").strip() == str(policy["firstBatchSlot"])
        and is_kpi_filled(row)
    )


def count_asset_prepared(command_center: dict) -> int:
    rows = command_center.get("rows", [])
    if not isinstance(rows, list):
        return 0
    return sum(
        1
        for row in rows
        if isinstance(row, dict)
        and row.get("phase") == "asset_ready_check"
        and row.get("status") in {"prepared", "ready"}
    )


def platform_checklist(profile_rows: list[dict[str, str]]) -> list[dict[str, str | bool]]:
    rows = []
    order = {platform: index for index, platform in enumerate(EXPECTED_PLATFORM_ORDER)}
    for row in sorted(profile_rows, key=lambda item: order.get(item.get("platform") or "", len(order))):
        platform = (row.get("platform") or "").strip()
        profile_link = (row.get("profile_link") or "").strip()
        status = (row.get("status") or "").strip() or "planned"
        rows.append({
            "platform": platform,
            "label": row.get("label") or PLATFORM_LABELS.get(platform, platform),
            "status": status,
            "profileLink": profile_link,
            "profileLinkValid": is_start_campaign_url(profile_link),
            "configured": status in {"set", "live"},
            "writeback": "platform-profile-tracker.csv: status=set/live, profile_link_set_date, profile_clicks, site_clicks, quiz_starts, quiz_completions",
        })
    return rows


def first_batch_schedule(posting_rows: list[dict[str, str]]) -> list[dict[str, str | bool]]:
    rows = []
    first_batch_rows = [
        row
        for row in posting_rows
        if (row.get("week") or "").strip() == "1" and (row.get("slot") or "").strip() == "1"
    ]
    for row in sorted(first_batch_rows, key=lambda item: (item.get("scheduled_date") or "", item.get("scheduled_time") or "", item.get("platform") or "")):
        tracked_url = (row.get("tracked_url") or "").strip()
        rows.append({
            "platform": (row.get("platform") or "").strip(),
            "label": PLATFORM_LABELS.get((row.get("platform") or "").strip(), (row.get("platform") or "").strip()),
            "taskId": (row.get("task_id") or "").strip(),
            "scriptId": (row.get("script_id") or "").strip(),
            "guardianId": (row.get("guardian_id") or "").strip(),
            "guardianName": (row.get("guardian_name") or "").strip(),
            "title": (row.get("title") or "").strip(),
            "scheduledDate": (row.get("scheduled_date") or "").strip(),
            "scheduledTime": (row.get("scheduled_time") or "").strip(),
            "timezone": (row.get("timezone") or "Asia/Taipei").strip(),
            "trackedUrl": tracked_url,
            "trackedUrlValid": is_start_campaign_url(tracked_url),
            "primaryCta": (row.get("primary_cta") or "").strip(),
            "writeback": "posting-queue.csv: status=published, published_date, post_url; platform-kpi-tracker.csv: same platform row post_url, site_clicks, quiz_starts, quiz_completions; kpi-tracker.csv: script-level weekly rollup",
        })
    return rows


def build_gate(
    profile_rows: list[dict[str, str]],
    posting_rows: list[dict[str, str]],
    kpi_rows: list[dict[str, str]],
    command_center: dict,
    platform_kpi_rows: list[dict[str, str]] | None = None,
) -> dict:
    policy = readiness_policy()
    expected_platform_count = int(policy["expectedPlatformCount"])
    profile_platforms = {(row.get("platform") or "").strip() for row in profile_rows}
    profile_links_valid = sum(1 for row in profile_rows if is_start_campaign_url(row.get("profile_link", "")))
    profile_configured = sum(1 for row in profile_rows if is_profile_configured(row))

    first_batch_rows = [
        row
        for row in posting_rows
        if (row.get("week") or "").strip() == str(policy["firstBatchWeek"])
        and (row.get("slot") or "").strip() == str(policy["firstBatchSlot"])
    ]
    first_week_rows = [row for row in posting_rows if (row.get("week") or "").strip() == "1"]
    expected_first_week_rows = len(first_week_rows)
    first_batch_scheduled = sum(
        1
        for row in first_batch_rows
        if row.get("scheduled_date") and row.get("scheduled_time") and is_start_campaign_url(row.get("tracked_url", ""))
    )
    first_week_scheduled = sum(
        1
        for row in first_week_rows
        if row.get("scheduled_date") and row.get("scheduled_time") and is_start_campaign_url(row.get("tracked_url", ""))
    )
    published_rows = sum(1 for row in posting_rows if (row.get("status") or "").strip() == "published")
    filled_kpi_rows = (
        count_first_batch_kpi_rows(platform_kpi_rows, policy)
        if platform_kpi_rows is not None
        else sum(1 for row in kpi_rows if is_kpi_filled(row))
    )
    asset_prepared = count_asset_prepared(command_center)
    platform_rows = platform_checklist(profile_rows)
    first_batch = first_batch_schedule(posting_rows)

    structure_ready = (
        profile_platforms == EXPECTED_PLATFORMS
        and len(profile_rows) == expected_platform_count
        and profile_links_valid == expected_platform_count
        and len(first_batch_rows) == expected_platform_count
        and first_batch_scheduled == expected_platform_count
        and asset_prepared >= expected_platform_count
    )
    ready_to_start_setup = structure_ready
    ready_to_publish_posts = structure_ready and profile_configured == expected_platform_count
    ready_for_kpi_decision = filled_kpi_rows >= expected_platform_count

    blockers: list[dict[str, str]] = []
    if profile_configured < expected_platform_count:
        blockers.append({
            "id": "set_platform_profile_links",
            "phase": "profile_setup",
            "severity": BLOCKER_SEVERITY_BY_ID["set_platform_profile_links"],
            "message": f"{expected_platform_count} 個平台個人頁仍未全部標記為 set/live；發布前先把 Bio/Profile link 設為平台專屬 /start/ 追蹤連結。",
        })
    if published_rows < expected_platform_count:
        blockers.append({
            "id": "publish_first_batch",
            "phase": "publish",
            "severity": BLOCKER_SEVERITY_BY_ID["publish_first_batch"],
            "message": f"首批 {expected_platform_count} 個平台貼文尚未全部標記 published；沒有 post_url 前不能開始 KPI 判讀。",
        })
    if filled_kpi_rows < expected_platform_count:
        blockers.append({
            "id": "backfill_first_batch_kpis",
            "phase": "measurement",
            "severity": BLOCKER_SEVERITY_BY_ID["backfill_first_batch_kpis"],
            "message": f"KPI 尚未回填到前 {expected_platform_count} 筆；保持測驗 CTA，不調整商品、Luna 或聯盟權重。",
        })

    issues: list[str] = []
    if len(profile_rows) != expected_platform_count:
        issues.append(f"expected {expected_platform_count} platform profile rows, got {len(profile_rows)}")
    if profile_platforms != EXPECTED_PLATFORMS:
        issues.append(f"profile platforms should be {sorted(EXPECTED_PLATFORMS)}, got {sorted(profile_platforms)}")
    if profile_links_valid != expected_platform_count:
        issues.append(f"expected {expected_platform_count} valid profile /start/ campaign links, got {profile_links_valid}")
    if len(first_batch_rows) != expected_platform_count:
        issues.append(f"expected {expected_platform_count} first-batch platform rows, got {len(first_batch_rows)}")
    if first_batch_scheduled != expected_platform_count:
        issues.append(f"expected {expected_platform_count} scheduled first-batch rows with campaign links, got {first_batch_scheduled}")
    if first_week_scheduled != expected_first_week_rows:
        issues.append(f"expected {expected_first_week_rows} scheduled first-week platform rows, got {first_week_scheduled}")
    if asset_prepared < expected_platform_count:
        issues.append(f"expected at least {expected_platform_count} prepared asset checks, got {asset_prepared}")
    if filled_kpi_rows == 0 and not blockers:
        issues.append("empty data mode must produce explicit measurement blockers")
    if expected_platform_count != len(EXPECTED_PLATFORM_ORDER):
        issues.append("readiness policy platform count does not match expected platform order")
    if tuple(policy.get("requiredKpiFields", [])) != REQUIRED_KPI_FIELDS:
        issues.append("readiness policy KPI fields do not match required KPI fields")
    if tuple(policy.get("blockerOrder", [])) != BLOCKER_ORDER:
        issues.append("readiness policy blocker order does not match blocker policy")
    blocker_ids = tuple(blocker["id"] for blocker in blockers)
    if blocker_ids != tuple(blocker_id for blocker_id in BLOCKER_ORDER if blocker_id in blocker_ids):
        issues.append("blockers should follow readiness policy order")
    for blocker in blockers:
        expected_severity = BLOCKER_SEVERITY_BY_ID.get(blocker["id"])
        if blocker.get("severity") != expected_severity:
            issues.append(f"{blocker['id']}: blocker severity should be {expected_severity}")

    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "profileTracker": rel(PROFILE_TRACKER_PATH),
            "postingQueue": rel(POSTING_QUEUE_PATH),
            "kpiTracker": rel(KPI_TRACKER_PATH),
            "platformKpiTracker": rel(PLATFORM_KPI_TRACKER_PATH),
            "launchCommandCenter": rel(COMMAND_CENTER_PATH),
        },
        "readinessPolicy": policy,
        "metrics": {
            "profileRows": len(profile_rows),
            "profileLinksValid": profile_links_valid,
            "profileConfigured": profile_configured,
            "firstBatchRows": len(first_batch_rows),
            "firstBatchScheduled": first_batch_scheduled,
            "firstWeekRows": expected_first_week_rows,
            "firstWeekScheduled": first_week_scheduled,
            "assetReady": asset_prepared,
            "assetPrepared": asset_prepared,
            "publishedRows": published_rows,
            "filledKpiRows": filled_kpi_rows,
            "platformChecklistRows": len(platform_rows),
            "firstBatchScheduleRows": len(first_batch),
            "blockers": len(blockers),
            "issues": len(issues),
        },
        "readiness": {
            "structureReady": structure_ready,
            "readyToStartSetup": ready_to_start_setup,
            "readyToPublishPosts": ready_to_publish_posts,
            "readyForKpiDecision": ready_for_kpi_decision,
            "emptyDataMode": filled_kpi_rows == 0,
        },
        "nextDecision": (
            "先設定 YouTube 頻道個人頁連結；完成 set/live 後發布首批 YouTube Shorts。"
            if not ready_to_publish_posts
            else "可發布首批 YouTube Shorts；發布後立即回填 post_url 與最小 KPI。"
        ),
        "platformChecklist": platform_rows,
        "firstBatchSchedule": first_batch,
        "blockers": blockers,
        "safety": {
            "quizOnlyCta": True,
            "doNotChangeOffersFromEmptyData": filled_kpi_rows == 0,
            "doNotChangeGuardianPriorityBeforeKpi": not ready_for_kpi_decision,
        },
        "issues": issues,
    }


def render_markdown(gate: dict) -> str:
    metrics = gate["metrics"]
    readiness = gate["readiness"]
    policy = gate["readinessPolicy"]
    lines = [
        "# LoveTypes Launch Readiness Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- 結構就緒：`{int(readiness['structureReady'])}`",
        f"- 可開始設定平台入口：`{int(readiness['readyToStartSetup'])}`",
        f"- 可發布首批貼文：`{int(readiness['readyToPublishPosts'])}`",
        f"- 可做 KPI/商品判斷：`{int(readiness['readyForKpiDecision'])}`",
        f"- 空資料模式：`{int(readiness['emptyDataMode'])}`",
        f"- 規則：{policy['rule']}",
        f"- blocker 順序：{', '.join(f'`{item}`' for item in policy['blockerOrder'])}",
        "",
        "## 目前數字",
        "",
        f"- 平台個人頁：{metrics['profileConfigured']} / {metrics['profileRows']} 已標記 set/live",
        f"- 平台追蹤連結：{metrics['profileLinksValid']} / {metrics['profileRows']} 有效",
        f"- 首批排程：{metrics['firstBatchScheduled']} / {metrics['firstBatchRows']} 有效",
        f"- 首週排程：{metrics['firstWeekScheduled']} / {metrics['firstWeekRows']} 有效",
        f"- 素材預備檢查：{metrics['assetPrepared']}",
        f"- 已發布平台列：{metrics['publishedRows']}",
        f"- 已回填 KPI 列：{metrics['filledKpiRows']}",
        f"- 必填 KPI 欄位：{', '.join(f'`{field}`' for field in policy['requiredKpiFields'])}",
        "",
        "## 平台入口清單",
        "",
    ]
    for row in gate["platformChecklist"]:
        status = "完成" if row["configured"] else "待設定"
        valid = "有效" if row["profileLinkValid"] else "需修正"
        lines.extend([
            f"### {row['label']}",
            "",
            f"- 狀態：`{row['status']}` ({status})",
            f"- Profile link：{row['profileLink']}",
            f"- 連結檢查：{valid}",
            f"- 回填：{row['writeback']}",
            "",
        ])
    lines.extend([
        "## 首批發文清單",
        "",
    ])
    for row in gate["firstBatchSchedule"]:
        valid = "有效" if row["trackedUrlValid"] else "需修正"
        lines.extend([
            f"### {row['label']} · {row['guardianName']} · {row['title']}",
            "",
            f"- 排程：{row['scheduledDate']} {row['scheduledTime']} {row['timezone']}",
            f"- task：`{row['taskId']}`",
            f"- script：`{row['scriptId']}`",
            f"- CTA：{row['primaryCta']}",
            f"- tracked URL：{row['trackedUrl']}",
            f"- 連結檢查：{valid}",
            f"- 回填：{row['writeback']}",
            "",
        ])
    lines.extend([
        "## 下一個決策",
        "",
        f"- {gate['nextDecision']}",
        "",
        "## 阻擋項",
        "",
    ])
    if gate["blockers"]:
        for blocker in gate["blockers"]:
            release = policy["blockerReleaseConditions"].get(blocker["id"], "")
            lines.append(f"- `{blocker['id']}` ({blocker['severity']})：{blocker['message']} 解除條件：{release}")
    else:
        lines.append("- 無阻擋項。")
    lines.extend([
        "",
        "## 安全界線",
        "",
        "- 空資料模式下不改商品排序、不加重 Luna 或聯盟 CTA。",
        "- Shorts 與個人頁入口維持單一 CTA：完成 15 題測驗，找到你的情感守護者。",
        "- KPI 未回填前，不判定優勝守護者，不承諾療效，不寫診斷式文案。",
        "",
    ])
    return "\n".join(lines)


def write_outputs(gate: dict, output: Path, json_output: Path) -> None:
    output.write_text(render_markdown(gate), encoding="utf-8")
    json_output.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check LoveTypes first-round promotion launch readiness.")
    parser.add_argument("--profile-tracker", default=str(PROFILE_TRACKER_PATH))
    parser.add_argument("--posting-queue", default=str(POSTING_QUEUE_PATH))
    parser.add_argument("--kpi-tracker", default=str(KPI_TRACKER_PATH))
    parser.add_argument("--platform-kpi-tracker", default=str(PLATFORM_KPI_TRACKER_PATH))
    parser.add_argument("--command-center", default=str(COMMAND_CENTER_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    gate = build_gate(
        read_csv(Path(args.profile_tracker)),
        read_csv(Path(args.posting_queue)),
        read_csv(Path(args.kpi_tracker)),
        read_json(Path(args.command_center)),
        read_csv(Path(args.platform_kpi_tracker)),
    )
    if not args.check:
        write_outputs(gate, Path(args.output), Path(args.json_output))
        print(f"promotion_launch_readiness_gate={args.output}")
        print(f"promotion_launch_readiness_gate_json={args.json_output}")

    metrics = gate["metrics"]
    readiness = gate["readiness"]
    print(f"promotion_launch_readiness_profile_rows={metrics['profileRows']}")
    print(f"promotion_launch_readiness_profile_links_valid={metrics['profileLinksValid']}")
    print(f"promotion_launch_readiness_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_launch_readiness_first_batch_rows={metrics['firstBatchRows']}")
    print(f"promotion_launch_readiness_first_batch_scheduled={metrics['firstBatchScheduled']}")
    print(f"promotion_launch_readiness_first_week_scheduled={metrics['firstWeekScheduled']}")
    print(f"promotion_launch_readiness_asset_ready={metrics['assetReady']}")
    print(f"promotion_launch_readiness_asset_prepared={metrics['assetPrepared']}")
    print(f"promotion_launch_readiness_published_rows={metrics['publishedRows']}")
    print(f"promotion_launch_readiness_filled_kpi_rows={metrics['filledKpiRows']}")
    print(f"promotion_launch_readiness_platform_checklist_rows={metrics['platformChecklistRows']}")
    print(f"promotion_launch_readiness_first_batch_schedule_rows={metrics['firstBatchScheduleRows']}")
    print(f"promotion_launch_readiness_ready_to_start_setup={int(readiness['readyToStartSetup'])}")
    print(f"promotion_launch_readiness_ready_to_publish={int(readiness['readyToPublishPosts'])}")
    print(f"promotion_launch_readiness_ready_for_kpi_decision={int(readiness['readyForKpiDecision'])}")
    print(f"promotion_launch_readiness_empty_data_mode={int(readiness['emptyDataMode'])}")
    print(f"promotion_launch_readiness_blockers={metrics['blockers']}")
    print(f"promotion_launch_readiness_issues={metrics['issues']}")
    for issue in gate["issues"]:
        print(issue)
    return 1 if gate["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
