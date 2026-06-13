#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
NEXT_ACTIONS_PATH = PROMOTION_DIR / "next-actions.json"
WEEK_EXECUTION_PATH = PROMOTION_DIR / "week-1-execution-sheet.json"
PUBLISHING_STATUS_PATH = PROMOTION_DIR / "publishing-status.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "launch-command-center.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "launch-command-center.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "launch-command-center.csv"

FIELDNAMES = [
    "sequence",
    "phase",
    "status",
    "priority",
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "guardian_name",
    "title",
    "scheduled_date",
    "scheduled_time",
    "tracked_url",
    "action",
    "writeback",
    "blocked_by",
    "safety_note",
]
PHASE_ORDER = ("profile_setup", "asset_ready_check", "publish_post", "kpi_backfill")
PLATFORM_ORDER = ("youtube_shorts", "tiktok", "instagram_reels", "all")
BLOCKED_STATUS_BY_PHASE = {
    "publish_post": "blocked_until_ready",
    "kpi_backfill": "blocked_until_published",
}
MINIMUM_KPI_BACKFILL_FIELDS = ["post_url", "site_clicks", "quiz_starts", "quiz_completions"]
DOWNSTREAM_KPI_BACKFILL_FIELDS = [
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
]


def command_center_policy() -> dict[str, object]:
    return {
        "phaseOrder": list(PHASE_ORDER),
        "readyPhases": ["profile_setup", "asset_ready_check"],
        "blockedPhases": ["publish_post", "kpi_backfill"],
        "publishBlockedBy": ["profile_setup", "asset_ready_check"],
        "kpiBackfillBlockedBy": ["post_url"],
        "minimumKpiBackfillFields": MINIMUM_KPI_BACKFILL_FIELDS,
        "downstreamKpiBackfillFields": DOWNSTREAM_KPI_BACKFILL_FIELDS,
        "profileWritebackFields": ["status=set/live", "profile_link_set_date", "profile_clicks", "site_clicks", "quiz_starts", "quiz_completions"],
        "rule": "Run profile_setup and asset_ready_check first; keep publish_post blocked until both are done; keep kpi_backfill blocked until post_url exists.",
        "emptyDataSafety": "Before KPI backfill, do not change offers, paid CTA, product order, Luna emphasis, affiliate emphasis, or winning guardian.",
        "ctaRule": "Every launch command keeps the CTA on the 15-question guardian quiz.",
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def profile_rows(week_execution: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for gate in week_execution.get("profileGates", []):
        platform = str(gate.get("platform", ""))
        label = str(gate.get("label", platform))
        status = str(gate.get("status", ""))
        ready = bool(gate.get("ready"))
        rows.append({
            "sequence": "",
            "phase": "profile_setup",
            "status": "done" if ready else "ready",
            "priority": "high",
            "platform": platform,
            "task_id": f"profile-{platform}",
            "script_id": "",
            "guardian_id": "",
            "guardian_name": "",
            "title": f"設定 {label} 個人頁入口",
            "scheduled_date": "",
            "scheduled_time": "",
            "tracked_url": str(gate.get("profileLink", "")),
            "action": f"把 Bio/Profile link 設為 {gate.get('profileLinkLabel', 'profile link')}，並放上置頂留言。",
            "writeback": ", ".join(gate.get("writeback", [])),
            "blocked_by": "" if status in {"planned", "set", "live"} else "platform_profile_status_unknown",
            "safety_note": "入口只導向 15 題測驗，不導購、不承諾療效。",
        })
    return rows


def asset_check_rows(week_execution: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for script in week_execution.get("scripts", []):
        rows.append({
            "sequence": "",
            "phase": "asset_ready_check",
            "status": "ready",
            "priority": "high",
            "platform": "all",
            "task_id": str(script.get("taskId", "")),
            "script_id": str(script.get("scriptId", "")),
            "guardian_id": str(script.get("guardianId", "")),
            "guardian_name": str(script.get("guardianName", "")),
            "title": str(script.get("title", "")),
            "scheduled_date": "",
            "scheduled_time": "",
            "tracked_url": str(script.get("platforms", [{}])[0].get("trackedUrl", "")) if script.get("platforms") else "",
            "action": "確認直式影片、字幕、封面或首幀、caption、留言 CTA 與安全邊界都可發布。",
            "writeback": "mark asset ready before platform posting",
            "blocked_by": "",
            "safety_note": "短片 CTA 維持測驗入口，不把素材改成直接購買。",
        })
    return rows


def publish_and_backfill_rows(week_execution: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for script in week_execution.get("scripts", []):
        for platform in script.get("platforms", []):
            platform_id = str(platform.get("platform", ""))
            base = {
                "sequence": "",
                "priority": "high",
                "platform": platform_id,
                "task_id": str(script.get("taskId", "")),
                "script_id": str(script.get("scriptId", "")),
                "guardian_id": str(script.get("guardianId", "")),
                "guardian_name": str(script.get("guardianName", "")),
                "title": str(script.get("title", "")),
                "scheduled_date": str(platform.get("scheduledDate", "")),
                "scheduled_time": str(platform.get("scheduledTime", "")),
                "tracked_url": str(platform.get("trackedUrl", "")),
                "safety_note": "只使用單一 CTA：完成 15 題測驗，找到你的情感守護者。",
            }
            rows.append({
                **base,
                "phase": "publish_post",
                "status": "blocked_until_ready",
                "action": f"依 {platform.get('label', platform_id)} caption 發布，確認連結與 UTM 未被改寫。",
                "writeback": "posting-queue.csv: status=published, published_date, post_url",
                "blocked_by": "profile_setup, asset_ready_check",
            })
            rows.append({
                **base,
                "phase": "kpi_backfill",
                "status": "blocked_until_published",
                "action": "發布後先回填平台貼文 URL 與最小 KPI；有結果後互動時補齊守護者、補給、修復計畫、Luna、收藏、名單、聯盟與 Contact 欄位；週回顧再彙總到腳本級 KPI。",
                "writeback": "platform-kpi-tracker.csv: platform row post_url, site_clicks, quiz_starts, quiz_completions, guardian_result_clicks, resources_clicks, repair_plan_clicks, luna_clicks, keepsake_clicks, free_keepsake_downloads, supply_lead_requests, luna_pack_clicks, affiliate_book_clicks, contact_requests; kpi-tracker.csv: script-level weekly rollup",
                "blocked_by": "post_url",
            })
    return rows


def assign_sequence(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    phase_index = {phase: index for index, phase in enumerate(PHASE_ORDER)}
    platform_index = {platform: index for index, platform in enumerate(PLATFORM_ORDER)}
    rows = sorted(
        rows,
        key=lambda row: (
            phase_index.get(str(row.get("phase", "")), 99),
            str(row.get("scheduled_date", "")),
            str(row.get("scheduled_time", "")),
            platform_index.get(str(row.get("platform", "")), 99),
            str(row.get("task_id", "")),
        ),
    )
    ordered = []
    for index, row in enumerate(rows, start=1):
        ordered.append({**row, "sequence": str(index)})
    return ordered


def build_center(next_actions: dict, week_execution: dict, publishing_status: dict) -> dict:
    profile_gate_count = len(week_execution.get("profileGates", []))
    script_count = len(week_execution.get("scripts", []))
    platform_post_count = sum(len(script.get("platforms", [])) for script in week_execution.get("scripts", []))
    rows = assign_sequence([
        *profile_rows(week_execution),
        *asset_check_rows(week_execution),
        *publish_and_backfill_rows(week_execution),
    ])
    status_counts: dict[str, int] = {}
    phase_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
        phase_counts[row["phase"]] = phase_counts.get(row["phase"], 0) + 1
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "nextActions": str(NEXT_ACTIONS_PATH.relative_to(ROOT)),
            "weekExecutionSheet": str(WEEK_EXECUTION_PATH.relative_to(ROOT)),
            "publishingStatus": str(PUBLISHING_STATUS_PATH.relative_to(ROOT)),
        },
        "week": week_execution.get("week"),
        "dataState": next_actions.get("dataState", {}),
        "publishingReadyForWeeklyDecision": bool(publishing_status.get("readyForWeeklyDecision")),
        "rowCount": len(rows),
        "readyRows": sum(1 for row in rows if row["status"] == "ready"),
        "blockedRows": sum(1 for row in rows if row["status"].startswith("blocked")),
        "statusCounts": status_counts,
        "phaseCounts": phase_counts,
        "expectedPhaseCounts": {
            "profile_setup": profile_gate_count,
            "asset_ready_check": script_count,
            "publish_post": platform_post_count,
            "kpi_backfill": platform_post_count,
        },
        "commandCenterPolicy": command_center_policy(),
        "nextDecision": "先完成 profile_setup 與 asset_ready_check，再發布 Week 1 三支 Shorts；未回填 KPI 前不調整商品或付費 CTA。",
        "rows": rows,
        "safety": {
            "quizOnlyCta": True,
            "doNotChangeOffersFromEmptyData": bool(next_actions.get("safety", {}).get("doNotChangeOffersFromEmptyData")),
            "doNotUseDiagnosisClaims": True,
        },
    }


def validate_center(center: dict) -> list[str]:
    issues: list[str] = []
    rows = center.get("rows", [])
    expected_phase_counts = center.get("expectedPhaseCounts", {})
    policy = center.get("commandCenterPolicy", {})
    if not isinstance(policy, dict):
        issues.append("center missing commandCenterPolicy")
        policy = {}
    if policy.get("phaseOrder") != list(PHASE_ORDER):
        issues.append("commandCenterPolicy.phaseOrder does not match generator policy")
    if policy.get("minimumKpiBackfillFields") != MINIMUM_KPI_BACKFILL_FIELDS:
        issues.append("commandCenterPolicy.minimumKpiBackfillFields does not match generator policy")
    if policy.get("downstreamKpiBackfillFields") != DOWNSTREAM_KPI_BACKFILL_FIELDS:
        issues.append("commandCenterPolicy.downstreamKpiBackfillFields does not match generator policy")
    if not isinstance(expected_phase_counts, dict):
        expected_phase_counts = {}
    expected_row_count = sum(int(value) for value in expected_phase_counts.values() if isinstance(value, int))
    expected_ready_rows = int(expected_phase_counts.get("profile_setup", 0)) + int(expected_phase_counts.get("asset_ready_check", 0))
    if len(rows) != expected_row_count:
        issues.append(f"expected {expected_row_count} command rows, got {len(rows)}")
    if center.get("readyRows", 0) < expected_ready_rows:
        issues.append(f"expected at least {expected_ready_rows} ready rows for profile setup and asset checks")
    if not center.get("blockedRows"):
        issues.append("publish/backfill rows should stay blocked until prerequisites are done")
    phases = center.get("phaseCounts", {})
    for phase, expected_count in expected_phase_counts.items():
        if phases.get(phase) != expected_count:
            issues.append(f"expected {expected_count} {phase} rows, got {phases.get(phase, 0)}")
    row_phase_order = [row.get("phase") for row in rows]
    phase_index = {phase: index for index, phase in enumerate(PHASE_ORDER)}
    if row_phase_order != sorted(row_phase_order, key=lambda phase: phase_index.get(str(phase), 99)):
        issues.append("rows should be sorted by command center phase order")
    for row in rows:
        label = f"{row.get('sequence', '?')}:{row.get('phase', '<phase>')}"
        for field in ("sequence", "phase", "status", "priority", "task_id", "title", "action", "safety_note"):
            if not row.get(field):
                issues.append(f"{label}: missing {field}")
        if row.get("phase") in {"publish_post", "kpi_backfill", "asset_ready_check"} and not row.get("tracked_url"):
            issues.append(f"{label}: missing tracked_url")
        if row.get("tracked_url") and "first_round_quiz_completion" not in row["tracked_url"]:
            issues.append(f"{label}: tracked_url missing campaign marker")
        if row.get("phase") in {"publish_post", "kpi_backfill"} and not row.get("blocked_by"):
            issues.append(f"{label}: publish/backfill rows must declare blocked_by")
        expected_status = BLOCKED_STATUS_BY_PHASE.get(str(row.get("phase", "")))
        if expected_status and row.get("status") != expected_status:
            issues.append(f"{label}: expected status {expected_status}")
        if row.get("phase") == "publish_post" and row.get("blocked_by") != ", ".join(policy.get("publishBlockedBy", [])):
            issues.append(f"{label}: publish row blocked_by should match policy")
        if row.get("phase") == "kpi_backfill" and row.get("blocked_by") != ", ".join(policy.get("kpiBackfillBlockedBy", [])):
            issues.append(f"{label}: kpi row blocked_by should match policy")
    return issues


def render_markdown(center: dict) -> str:
    rows = center["rows"]
    lines = [
        "# LoveTypes Launch Command Center",
        "",
        f"- 產生日期：{center['generatedAt']}",
        f"- 週次：Week {center['week']}",
        f"- 指揮列數：{center['rowCount']}",
        f"- 可立即執行：{center['readyRows']}",
        f"- 等待前置條件：{center['blockedRows']}",
        f"- 週決策：{'可判讀' if center['publishingReadyForWeeklyDecision'] else '尚不可'}",
        f"- 指揮板規則：{center['commandCenterPolicy']['rule']}",
        f"- 空資料安全：{center['commandCenterPolicy']['emptyDataSafety']}",
        "",
        "## 今日決策",
        "",
        f"- {center['nextDecision']}",
        "",
        "## 執行順序",
        "",
    ]
    for row in rows:
        lines.extend([
            f"### {row['sequence']}. {row['title']}",
            "",
            f"- phase：`{row['phase']}`",
            f"- status：`{row['status']}`",
            f"- priority：`{row['priority']}`",
            f"- platform：`{row['platform']}`",
            f"- task：`{row['task_id']}`",
        ])
        if row["scheduled_date"]:
            lines.append(f"- schedule：{row['scheduled_date']} {row['scheduled_time']} Asia/Taipei")
        if row["tracked_url"]:
            lines.append(f"- tracked URL：{row['tracked_url']}")
        lines.extend([
            f"- action：{row['action']}",
            f"- writeback：{row['writeback']}",
        ])
        if row["blocked_by"]:
            lines.append(f"- blocked by：{row['blocked_by']}")
        lines.extend([
            f"- safety：{row['safety_note']}",
            "",
        ])
    lines.extend([
        "## 不做事項",
        "",
        "- 未有發布與 KPI 回填前，不改商品排序、不加重付費 CTA、不判定優勝守護者。",
        "- 不把測驗結果寫成診斷，不承諾療效，不用恐嚇式文案。",
        "- 若平台不允許長連結，使用 `/start/`，但 KPI 回填仍要保留對應 `utm_content`。",
        "",
    ])
    return "\n".join(lines)


def write_outputs(center: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(center), encoding="utf-8")
    json_output.write_text(json.dumps(center, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(center["rows"], csv_output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a LoveTypes first-round launch command center.")
    parser.add_argument("--next-actions", default=str(NEXT_ACTIONS_PATH))
    parser.add_argument("--week-execution", default=str(WEEK_EXECUTION_PATH))
    parser.add_argument("--publishing-status", default=str(PUBLISHING_STATUS_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    center = build_center(
        load_json(Path(args.next_actions)),
        load_json(Path(args.week_execution)),
        load_json(Path(args.publishing_status)),
    )
    issues = validate_center(center)
    if not args.check:
        write_outputs(center, Path(args.output), Path(args.json_output), Path(args.csv_output))
        print(f"promotion_launch_command_center={args.output}")
        print(f"promotion_launch_command_center_json={args.json_output}")
        print(f"promotion_launch_command_center_csv={args.csv_output}")
    print(f"promotion_launch_command_rows={center['rowCount']}")
    print(f"promotion_launch_command_ready={center['readyRows']}")
    print(f"promotion_launch_command_blocked={center['blockedRows']}")
    print(f"promotion_launch_command_profile_rows={center['phaseCounts'].get('profile_setup', 0)}")
    print(f"promotion_launch_command_publish_rows={center['phaseCounts'].get('publish_post', 0)}")
    print(f"promotion_launch_command_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
