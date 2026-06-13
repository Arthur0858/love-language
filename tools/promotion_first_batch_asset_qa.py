#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
COMMAND_CENTER_PATH = PROMOTION_DIR / "launch-command-center.json"
FIRST_BATCH_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "first-batch-asset-qa.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "first-batch-asset-qa.json"
REQUIRED_QA_ITEMS = (
    "vertical_video",
    "subtitle_readability",
    "cover_or_first_frame",
    "guardian_universe_match",
    "caption_quiz_cta",
    "tracked_url_utm",
    "safety_boundary",
    "writeback_ready",
)
FORBIDDEN_FIRST_CTA = ("Luna", "Gumroad", "Amazon", "博客來", "購買", "buy")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def valid_start_url(value: str, utm_content: str) -> bool:
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "lovetypes.tw"
        and parsed.path == "/start/"
        and query.get("utm_source") == ["shorts"]
        and query.get("utm_medium") == ["social"]
        and query.get("utm_campaign") == ["first_round_quiz_completion"]
        and query.get("utm_content") == [utm_content]
    )


def qa_items(row: dict) -> list[dict[str, str]]:
    return [
        {
            "id": "vertical_video",
            "label": "直式影片檔",
            "check": "確認 9:16 直式影片可播放，長度符合 Shorts/Reels/TikTok 節奏。",
            "evidence": "實際影片檔路徑、平台預覽截圖或剪輯輸出紀錄。",
        },
        {
            "id": "subtitle_readability",
            "label": "字幕可讀性",
            "check": "字幕短句、無錯字、手機尺寸不遮擋主體，保留 A/B/C 互動。",
            "evidence": "手機預覽截圖或字幕 QA 記錄。",
        },
        {
            "id": "cover_or_first_frame",
            "label": "封面或首幀",
            "check": "首幀能在 1 秒內看懂情緒鉤子與守護者氛圍。",
            "evidence": "封面圖、首幀截圖或平台草稿預覽。",
        },
        {
            "id": "guardian_universe_match",
            "label": "守護者宇宙一致",
            "check": f"使用 {row.get('guardianName', '')} / {row.get('guardianId', '')} 的色彩、象徵物與情緒設定，不混用其他守護者。",
            "evidence": "畫面截圖或素材清單。",
        },
        {
            "id": "caption_quiz_cta",
            "label": "Caption 單一 CTA",
            "check": "Caption 主 CTA 維持完成 15 題測驗，不加入商品、Luna 或聯盟導購作為第一動作。",
            "evidence": "平台 caption 草稿。",
        },
        {
            "id": "tracked_url_utm",
            "label": "追蹤連結",
            "check": f"連結保留 utm_content={row.get('utmContent', '')}，且指向 /start/。",
            "evidence": "平台草稿中的連結或點擊後網址。",
        },
        {
            "id": "safety_boundary",
            "label": "安全邊界",
            "check": "無診斷、療效、保證修復、必須購買或危機支援承諾。",
            "evidence": "最終字幕與 caption 檢查紀錄。",
        },
        {
            "id": "writeback_ready",
            "label": "回填準備",
            "check": "發布後可取得 https post URL、發布日期、proof note，並使用 post text import 回填。",
            "evidence": "post text import 模板已準備。",
        },
    ]


def build_packet() -> dict:
    command_center = load_json(COMMAND_CENTER_PATH)
    first_batch = load_json(FIRST_BATCH_PATH)
    asset_rows = [
        row for row in command_center.get("rows", [])
        if row.get("phase") == "asset_ready_check"
    ]
    asset_lookup = {row.get("task_id"): row for row in asset_rows}
    rows = []
    for row in first_batch.get("rows", []):
        task_id = row.get("taskId", "")
        command_row = asset_lookup.get(task_id, {})
        rows.append({
            "taskId": task_id,
            "scriptId": row.get("scriptId", ""),
            "platform": row.get("platform", ""),
            "guardianId": row.get("guardianId", ""),
            "guardianName": row.get("guardianName", ""),
            "title": row.get("title", ""),
            "caption": row.get("caption", ""),
            "trackedUrl": row.get("trackedUrl", ""),
            "utmContent": row.get("utmContent", ""),
            "assetReadyStatus": command_row.get("status", ""),
            "assetReadyAction": command_row.get("action", ""),
            "assetReadySafety": command_row.get("safety", ""),
            "postImportTemplate": "\n".join([
                "LoveTypes platform post writeback",
                f"platform: {row.get('platform', '')}",
                f"task_id: {task_id}",
                "status: published",
                f"published_date: {date.today().isoformat()}",
                "post_url: https://example.com/post",
                "views: 0",
                "site_clicks: 0",
                "quiz_starts: 0",
                "quiz_completions: 0",
            ]),
            "qaItems": qa_items(row),
        })
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "launchCommandCenter": str(COMMAND_CENTER_PATH.relative_to(ROOT)),
            "firstBatchPublicationPacket": str(FIRST_BATCH_PATH.relative_to(ROOT)),
        },
        "rowCount": len(rows),
        "requiredQaItems": list(REQUIRED_QA_ITEMS),
        "rows": rows,
    }


def validate_packet(packet: dict) -> list[str]:
    issues: list[str] = []
    rows = packet.get("rows", [])
    if len(rows) != 3:
        issues.append(f"expected 3 first-batch asset QA rows, got {len(rows)}")
    for row in rows:
        label = f"{row.get('platform', '<platform>')}/{row.get('taskId', '<task>')}"
        if row.get("guardianId") != "iris":
            issues.append(f"{label}: first-batch asset QA should be Iris")
        if row.get("assetReadyStatus") != "ready":
            issues.append(f"{label}: asset ready status should be ready")
        if "完成 15 題測驗" not in row.get("caption", ""):
            issues.append(f"{label}: caption missing quiz CTA")
        for token in FORBIDDEN_FIRST_CTA:
            if token in row.get("caption", ""):
                issues.append(f"{label}: caption should not use {token} as first-batch CTA")
        if not valid_start_url(row.get("trackedUrl", ""), row.get("utmContent", "")):
            issues.append(f"{label}: tracked URL should point to /start/ with first-round UTM")
        item_ids = {item.get("id") for item in row.get("qaItems", [])}
        if item_ids != set(REQUIRED_QA_ITEMS):
            issues.append(f"{label}: QA items should cover every required item")
        if "promotion_post_text_import.py" not in row.get("postImportTemplate", "") and "LoveTypes platform post writeback" not in row.get("postImportTemplate", ""):
            issues.append(f"{label}: missing post import template")
    return issues


def render_markdown(packet: dict, issues: list[str]) -> str:
    lines = [
        "# LoveTypes First Batch Asset QA",
        "",
        f"- 產生日期：{packet['generatedAt']}",
        f"- QA rows：{packet['rowCount']}",
        f"- required QA items：{len(packet['requiredQaItems'])}",
        f"- issues：{len(issues)}",
        "",
        "## Rule",
        "",
        "- 這份文件只做發布前 QA，不把素材、profile、post URL 或 KPI 標成完成。",
        "- 發布前逐項留下 proof note；發布後再用 post text import 回填 URL 與初始 KPI。",
        "",
    ]
    for row in packet["rows"]:
        lines.extend([
            f"## {row['platform']} · `{row['taskId']}`",
            "",
            f"- script：`{row['scriptId']}`",
            f"- guardian：{row['guardianName']}（`{row['guardianId']}`）",
            f"- title：{row['title']}",
            f"- asset ready status：`{row['assetReadyStatus']}`",
            f"- tracked URL：{row['trackedUrl']}",
            "",
            "### QA Checklist",
            "",
        ])
        for item in row["qaItems"]:
            lines.extend([
                f"- `{item['id']}` {item['label']}：{item['check']}",
                f"  - evidence：{item['evidence']}",
            ])
        lines.extend([
            "",
            "### Post Import Template",
            "",
            "```text",
            row["postImportTemplate"],
            "```",
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(packet: dict, issues: list[str], output: Path, json_output: Path) -> None:
    json_output.write_text(json.dumps({**packet, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.write_text(render_markdown(packet, issues), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build first-batch pre-publish asset QA packet.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    issues = validate_packet(packet)
    if not args.check:
        write_outputs(packet, issues, Path(args.output), Path(args.json_output))
        print(f"promotion_first_batch_asset_qa={args.output}")
        print(f"promotion_first_batch_asset_qa_json={args.json_output}")
    print(f"promotion_first_batch_asset_qa_rows={packet['rowCount']}")
    print(f"promotion_first_batch_asset_qa_required_items={len(packet['requiredQaItems'])}")
    print(f"promotion_first_batch_asset_qa_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
