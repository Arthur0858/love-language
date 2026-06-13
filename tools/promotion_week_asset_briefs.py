#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
SCRIPTS_PATH = PROMOTION_DIR / "shorts-scripts.zh-TW.json"
DEFAULT_INDEX_PATH = PROMOTION_DIR / "week-asset-briefs-index.md"
DEFAULT_INDEX_JSON_PATH = PROMOTION_DIR / "week-asset-briefs-index.json"
PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def chunks(lines: list[str]) -> list[list[str]]:
    if len(lines) <= 3:
        return [lines]
    return [part for part in (lines[:3], lines[3:6], lines[6:]) if part]


def week_paths(week: int) -> tuple[Path, Path]:
    return (
        PROMOTION_DIR / f"week-{week}-asset-briefs.md",
        PROMOTION_DIR / f"week-{week}-asset-briefs.json",
    )


def execution_sheet_path(week: int) -> Path:
    return PROMOTION_DIR / f"week-{week}-execution-sheet.json"


def script_map(script_library: dict) -> dict[str, dict]:
    return {script["id"]: script for script in script_library.get("scripts", [])}


def build_scene_cards(script: dict) -> list[dict]:
    subtitle_groups = chunks([str(line) for line in script.get("full_subtitle_script", [])])
    visuals = [str(item) for item in script.get("visual_suggestions", [])]
    cards = []
    for index, subtitle_lines in enumerate(subtitle_groups, start=1):
        visual = visuals[index - 1] if index <= len(visuals) else visuals[-1] if visuals else ""
        cards.append({
            "scene": index,
            "timing": f"{(index - 1) * 7:02d}-{min(index * 7, 24):02d}s",
            "visualPrompt": visual,
            "subtitleLines": subtitle_lines,
            "overlayText": subtitle_lines[0] if subtitle_lines else "",
        })
    return cards


def build_brief(week: int, script_row: dict, source_script: dict) -> dict:
    platforms = []
    for platform in script_row.get("platforms", []):
        platforms.append({
            "platform": platform.get("platform", ""),
            "label": platform.get("label", ""),
            "scheduledDate": platform.get("scheduledDate", ""),
            "scheduledTime": platform.get("scheduledTime", ""),
            "timezone": platform.get("timezone", ""),
            "trackedUrl": platform.get("trackedUrl", ""),
            "caption": platform.get("caption", ""),
            "writeback": platform.get("writeback", []),
        })
    return {
        "week": week,
        "taskId": script_row.get("taskId", ""),
        "scriptId": script_row.get("scriptId", ""),
        "guardianId": script_row.get("guardianId", source_script.get("guardian_id", "")),
        "guardianName": script_row.get("guardianName", source_script.get("guardian_name", "")),
        "guardianTheme": source_script.get("guardian_theme", ""),
        "contentAngle": script_row.get("contentAngle", ""),
        "title": script_row.get("title", source_script.get("title", "")),
        "hook": source_script.get("hook", ""),
        "emotionTypes": source_script.get("emotion_types", []),
        "format": {
            "aspectRatio": "9:16",
            "targetDuration": "20-30s",
            "primaryCTA": script_row.get("primaryCta", "完成 15 題測驗，找到你的情感守護者"),
            "recommendedOutput": f"exports/lovetypes/week-{week}/{script_row.get('scriptId', '')}.mp4",
        },
        "sceneCards": build_scene_cards(source_script),
        "platforms": platforms,
        "commentCTA": source_script.get("comment_cta", ""),
        "safetyChecklist": [
            "不宣稱診斷、療效或保證修復。",
            "不把短片 CTA 改成直接購買。",
            "不交換守護者名稱、愛之語、色系或象徵物。",
            "Caption 與畫面 CTA 維持單一路徑：完成 15 題測驗。",
            "發布後先回填 posting-queue.csv，再回填 platform-kpi-tracker.csv；週回顧才彙總 kpi-tracker.csv。",
        ],
    }


def build_week_payload(week: int, script_library: dict, execution_sheet: dict) -> dict:
    scripts = script_map(script_library)
    briefs = []
    missing_scripts: list[str] = []
    for script_row in execution_sheet.get("scripts", []):
        script_id = script_row.get("scriptId", "")
        source_script = scripts.get(script_id)
        if not source_script:
            missing_scripts.append(script_id)
            continue
        briefs.append(build_brief(week, script_row, source_script))
    return {
        "generatedAt": date.today().isoformat(),
        "week": week,
        "source": {
            "scripts": str(SCRIPTS_PATH.relative_to(ROOT)),
            "executionSheet": str(execution_sheet_path(week).relative_to(ROOT)),
        },
        "briefCount": len(briefs),
        "sceneCardCount": sum(len(brief["sceneCards"]) for brief in briefs),
        "platformCaptionCount": sum(len(brief["platforms"]) for brief in briefs),
        "missingScripts": missing_scripts,
        "briefs": briefs,
    }


def validate_week_payload(payload: dict) -> list[str]:
    issues: list[str] = []
    week = payload.get("week")
    if payload.get("briefCount") != 3:
        issues.append(f"week {week}: expected 3 briefs, got {payload.get('briefCount')}")
    if payload.get("sceneCardCount", 0) < 9:
        issues.append(f"week {week}: expected at least 9 scene cards")
    if payload.get("platformCaptionCount") != 9:
        issues.append(f"week {week}: expected 9 platform captions, got {payload.get('platformCaptionCount')}")
    if payload.get("missingScripts"):
        issues.append(f"week {week}: missing scripts {', '.join(payload['missingScripts'])}")
    for brief in payload.get("briefs", []):
        label = brief.get("scriptId", "<script>")
        if len(brief.get("sceneCards", [])) < 3:
            issues.append(f"{label}: expected at least 3 scene cards")
        platforms = brief.get("platforms", [])
        platform_ids = {item.get("platform") for item in platforms}
        if platform_ids != set(PLATFORMS):
            issues.append(f"{label}: expected platform captions for {', '.join(PLATFORMS)}")
        for platform in platforms:
            caption = platform.get("caption", "")
            tracked_url = platform.get("trackedUrl", "")
            platform_label = platform.get("platform", "<platform>")
            if "完成 15 題測驗" not in caption:
                issues.append(f"{label}/{platform_label}: caption missing quiz CTA")
            if "utm_campaign=first_round_quiz_completion" not in tracked_url:
                issues.append(f"{label}/{platform_label}: tracked URL missing campaign marker")
        safety_text = " ".join(brief.get("safetyChecklist", []))
        for required in ("不宣稱診斷", "不把短片 CTA 改成直接購買", "發布後先回填"):
            if required not in safety_text:
                issues.append(f"{label}: safety checklist missing {required}")
    return issues


def render_week_markdown(payload: dict) -> str:
    lines = [
        f"# LoveTypes Week {payload['week']} Asset Briefs",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- 製作手卡：{payload['briefCount']}",
        f"- 場景卡：{payload['sceneCardCount']}",
        f"- 平台 caption：{payload['platformCaptionCount']}",
        "",
        "## 使用方式",
        "",
        "- 每支影片先依場景卡完成 9:16 初版，再使用對應平台 caption 發布。",
        "- 發布 CTA 固定導向 15 題測驗；商品、Luna、聯盟連結只由網站結果頁承接。",
        "- 發布後先回填 `posting-queue.csv`，再回填 `platform-kpi-tracker.csv`；週回顧才彙總 `kpi-tracker.csv`。",
        "",
    ]
    for brief in payload["briefs"]:
        fmt = brief["format"]
        lines.extend([
            f"## {brief['guardianName']} · {brief['title']}",
            "",
            f"- 任務：`{brief['taskId']}`",
            f"- 腳本：`{brief['scriptId']}`",
            f"- 守護者宇宙：{brief['guardianTheme']}",
            f"- 內容角度：{brief['contentAngle']}",
            f"- 格式：{fmt['aspectRatio']} / {fmt['targetDuration']}",
            f"- 輸出檔：`{fmt['recommendedOutput']}`",
            f"- 主 CTA：{fmt['primaryCTA']}",
            f"- 留言引導：{brief['commentCTA']}",
            "",
            "### 場景卡",
            "",
        ])
        for card in brief["sceneCards"]:
            lines.extend([
                f"- Scene {card['scene']}（{card['timing']}）",
                f"  - 畫面：{card['visualPrompt']}",
                f"  - 字幕：{' / '.join(card['subtitleLines'])}",
                f"  - 畫面字：{card['overlayText']}",
            ])
        lines.extend(["", "### 平台 Caption", ""])
        for platform in brief["platforms"]:
            lines.extend([
                f"#### {platform['label']} · {platform['scheduledDate']} {platform['scheduledTime']} {platform['timezone']}",
                "",
                f"- 追蹤連結：{platform['trackedUrl']}",
                "",
                "```text",
                platform["caption"].strip(),
                "```",
                "",
                f"- 回填：{', '.join(f'`{item}`' for item in platform.get('writeback', []))}",
                "",
            ])
        lines.extend(["### 安全檢查", ""])
        lines.extend(f"- {item}" for item in brief["safetyChecklist"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_week_payload(payload: dict, md_path: Path, json_path: Path) -> None:
    md_path.write_text(render_week_markdown(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_index(week_payloads: list[dict], issues: list[str]) -> dict:
    return {
        "generatedAt": date.today().isoformat(),
        "weekCount": len(week_payloads),
        "briefCount": sum(payload["briefCount"] for payload in week_payloads),
        "sceneCardCount": sum(payload["sceneCardCount"] for payload in week_payloads),
        "platformCaptionCount": sum(payload["platformCaptionCount"] for payload in week_payloads),
        "weeks": [
            {
                "week": payload["week"],
                "briefCount": payload["briefCount"],
                "sceneCardCount": payload["sceneCardCount"],
                "platformCaptionCount": payload["platformCaptionCount"],
                "markdown": str(week_paths(payload["week"])[0].relative_to(ROOT)),
                "json": str(week_paths(payload["week"])[1].relative_to(ROOT)),
            }
            for payload in week_payloads
        ],
        "issues": issues,
    }


def render_index_markdown(index: dict) -> str:
    lines = [
        "# LoveTypes Weekly Asset Briefs Index",
        "",
        f"- 產生日期：{index['generatedAt']}",
        f"- 週次：{index['weekCount']}",
        f"- 製作手卡：{index['briefCount']}",
        f"- 場景卡：{index['sceneCardCount']}",
        f"- 平台 caption：{index['platformCaptionCount']}",
        "",
        "## Week Files",
        "",
    ]
    for item in index["weeks"]:
        lines.extend([
            f"- Week {item['week']}: `{item['markdown']}` / `{item['json']}`",
        ])
    if index["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in index["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_index(index: dict, md_path: Path, json_path: Path) -> None:
    md_path.write_text(render_index_markdown(index), encoding="utf-8")
    json_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build weekly LoveTypes asset briefs from scripts and execution sheets.")
    parser.add_argument("--week", type=int, default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--scripts", default=str(SCRIPTS_PATH))
    parser.add_argument("--index-output", default=str(DEFAULT_INDEX_PATH))
    parser.add_argument("--index-json-output", default=str(DEFAULT_INDEX_JSON_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    weeks = list(range(1, 6)) if args.all or args.week is None else [args.week]
    script_library = load_json(Path(args.scripts))
    week_payloads = []
    issues: list[str] = []
    for week in weeks:
        execution_sheet = load_json(execution_sheet_path(week))
        payload = build_week_payload(week, script_library, execution_sheet)
        week_issues = validate_week_payload(payload)
        issues.extend(week_issues)
        week_payloads.append(payload)
        if not args.check:
            write_week_payload(payload, *week_paths(week))
    index = build_index(week_payloads, issues)
    if not args.check:
        write_index(index, Path(args.index_output), Path(args.index_json_output))
        print(f"promotion_week_asset_briefs_index={args.index_output}")
        print(f"promotion_week_asset_briefs_index_json={args.index_json_output}")
    print(f"promotion_week_asset_briefs_weeks={index['weekCount']}")
    print(f"promotion_week_asset_briefs_count={index['briefCount']}")
    print(f"promotion_week_asset_briefs_scene_cards={index['sceneCardCount']}")
    print(f"promotion_week_asset_briefs_platform_captions={index['platformCaptionCount']}")
    print(f"promotion_week_asset_briefs_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
