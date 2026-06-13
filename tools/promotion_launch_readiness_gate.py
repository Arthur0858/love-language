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
COMMAND_CENTER_PATH = PROMOTION_DIR / "launch-command-center.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "launch-readiness-gate.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "launch-readiness-gate.json"

EXPECTED_PLATFORMS = {"youtube_shorts", "tiktok", "instagram_reels"}
CAMPAIGN = "first_round_quiz_completion"
REQUIRED_KPI_FIELDS = ("post_url", "site_clicks", "quiz_starts", "quiz_completions")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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
    return (row.get("status") or "").strip() in {"set", "live"}


def is_kpi_filled(row: dict[str, str]) -> bool:
    if (row.get("post_url") or "").strip():
        return True
    return any(parse_int(row.get(field)) > 0 for field in REQUIRED_KPI_FIELDS if field != "post_url")


def count_asset_ready(command_center: dict) -> int:
    rows = command_center.get("rows", [])
    if not isinstance(rows, list):
        return 0
    return sum(
        1
        for row in rows
        if isinstance(row, dict)
        and row.get("phase") == "asset_ready_check"
        and row.get("status") == "ready"
    )


def build_gate(
    profile_rows: list[dict[str, str]],
    posting_rows: list[dict[str, str]],
    kpi_rows: list[dict[str, str]],
    command_center: dict,
) -> dict:
    profile_platforms = {(row.get("platform") or "").strip() for row in profile_rows}
    profile_links_valid = sum(1 for row in profile_rows if is_start_campaign_url(row.get("profile_link", "")))
    profile_configured = sum(1 for row in profile_rows if is_profile_configured(row))

    first_batch_rows = [
        row
        for row in posting_rows
        if (row.get("week") or "").strip() == "1" and (row.get("slot") or "").strip() == "1"
    ]
    first_week_rows = [row for row in posting_rows if (row.get("week") or "").strip() == "1"]
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
    filled_kpi_rows = sum(1 for row in kpi_rows if is_kpi_filled(row))
    asset_ready = count_asset_ready(command_center)

    structure_ready = (
        profile_platforms == EXPECTED_PLATFORMS
        and len(profile_rows) == len(EXPECTED_PLATFORMS)
        and profile_links_valid == len(EXPECTED_PLATFORMS)
        and len(first_batch_rows) == len(EXPECTED_PLATFORMS)
        and first_batch_scheduled == len(EXPECTED_PLATFORMS)
        and asset_ready >= len(EXPECTED_PLATFORMS)
    )
    ready_to_start_setup = structure_ready
    ready_to_publish_posts = structure_ready and profile_configured == len(EXPECTED_PLATFORMS)
    ready_for_kpi_decision = filled_kpi_rows >= 3

    blockers: list[dict[str, str]] = []
    if profile_configured < len(EXPECTED_PLATFORMS):
        blockers.append({
            "id": "set_platform_profile_links",
            "phase": "profile_setup",
            "severity": "launch_blocker",
            "message": "三個平台個人頁仍未標記為 set/live；發布前先把 Bio/Profile link 設為平台專屬 /start/ 追蹤連結。",
        })
    if published_rows < len(EXPECTED_PLATFORMS):
        blockers.append({
            "id": "publish_first_batch",
            "phase": "publish",
            "severity": "measurement_blocker",
            "message": "首批三平台貼文尚未標記 published；沒有 post_url 前不能開始 KPI 判讀。",
        })
    if filled_kpi_rows < 3:
        blockers.append({
            "id": "backfill_first_batch_kpis",
            "phase": "measurement",
            "severity": "decision_blocker",
            "message": "KPI 尚未回填到前三筆；保持測驗 CTA，不調整商品、Luna 或聯盟權重。",
        })

    issues: list[str] = []
    if len(profile_rows) != len(EXPECTED_PLATFORMS):
        issues.append(f"expected 3 platform profile rows, got {len(profile_rows)}")
    if profile_platforms != EXPECTED_PLATFORMS:
        issues.append(f"profile platforms should be {sorted(EXPECTED_PLATFORMS)}, got {sorted(profile_platforms)}")
    if profile_links_valid != len(EXPECTED_PLATFORMS):
        issues.append(f"expected 3 valid profile /start/ campaign links, got {profile_links_valid}")
    if len(first_batch_rows) != len(EXPECTED_PLATFORMS):
        issues.append(f"expected 3 first-batch platform rows, got {len(first_batch_rows)}")
    if first_batch_scheduled != len(EXPECTED_PLATFORMS):
        issues.append(f"expected 3 scheduled first-batch rows with campaign links, got {first_batch_scheduled}")
    if first_week_scheduled != 9:
        issues.append(f"expected 9 scheduled first-week platform rows, got {first_week_scheduled}")
    if asset_ready < len(EXPECTED_PLATFORMS):
        issues.append(f"expected at least 3 ready asset checks, got {asset_ready}")
    if filled_kpi_rows == 0 and not blockers:
        issues.append("empty data mode must produce explicit measurement blockers")

    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "profileTracker": str(PROFILE_TRACKER_PATH.relative_to(ROOT)),
            "postingQueue": str(POSTING_QUEUE_PATH.relative_to(ROOT)),
            "kpiTracker": str(KPI_TRACKER_PATH.relative_to(ROOT)),
            "launchCommandCenter": str(COMMAND_CENTER_PATH.relative_to(ROOT)),
        },
        "metrics": {
            "profileRows": len(profile_rows),
            "profileLinksValid": profile_links_valid,
            "profileConfigured": profile_configured,
            "firstBatchRows": len(first_batch_rows),
            "firstBatchScheduled": first_batch_scheduled,
            "firstWeekScheduled": first_week_scheduled,
            "assetReady": asset_ready,
            "publishedRows": published_rows,
            "filledKpiRows": filled_kpi_rows,
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
            "先設定三個平台個人頁連結；完成 set/live 後發布首批三平台貼文。"
            if not ready_to_publish_posts
            else "可發布首批三平台貼文；發布後立即回填 post_url 與最小 KPI。"
        ),
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
    lines = [
        "# LoveTypes Launch Readiness Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- 結構就緒：`{int(readiness['structureReady'])}`",
        f"- 可開始設定平台入口：`{int(readiness['readyToStartSetup'])}`",
        f"- 可發布首批貼文：`{int(readiness['readyToPublishPosts'])}`",
        f"- 可做 KPI/商品判斷：`{int(readiness['readyForKpiDecision'])}`",
        f"- 空資料模式：`{int(readiness['emptyDataMode'])}`",
        "",
        "## 目前數字",
        "",
        f"- 平台個人頁：{metrics['profileConfigured']} / {metrics['profileRows']} 已標記 set/live",
        f"- 平台追蹤連結：{metrics['profileLinksValid']} / 3 有效",
        f"- 首批排程：{metrics['firstBatchScheduled']} / {metrics['firstBatchRows']} 有效",
        f"- 首週排程：{metrics['firstWeekScheduled']} / 9 有效",
        f"- 素材就緒檢查：{metrics['assetReady']}",
        f"- 已發布平台列：{metrics['publishedRows']}",
        f"- 已回填 KPI 列：{metrics['filledKpiRows']}",
        "",
        "## 下一個決策",
        "",
        f"- {gate['nextDecision']}",
        "",
        "## 阻擋項",
        "",
    ]
    if gate["blockers"]:
        for blocker in gate["blockers"]:
            lines.append(f"- `{blocker['id']}`：{blocker['message']}")
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
    print(f"promotion_launch_readiness_published_rows={metrics['publishedRows']}")
    print(f"promotion_launch_readiness_filled_kpi_rows={metrics['filledKpiRows']}")
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
