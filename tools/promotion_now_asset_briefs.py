#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PACK_PATH = PROMOTION_DIR / "now-asset-production-pack.json"
BRIEFS_MD_PATH = PROMOTION_DIR / "now-asset-production-briefs.md"
BRIEFS_JSON_PATH = PROMOTION_DIR / "now-asset-production-briefs.json"
GUARDIAN_TAGS = {
    "iris": ["#艾莉絲", "#肯定言詞", "#文字型戀人"],
    "noah": ["#諾雅", "#優質時光", "#陪伴感"],
    "vivian": ["#薇薇安", "#接受禮物", "#儀式感"],
    "claire": ["#克萊兒", "#服務行動", "#被分擔"],
    "dora": ["#朵拉", "#身體接觸", "#安全感"],
}
COMMON_TAGS = ["#LoveTypes", "#五種愛之語", "#情感守護者", "#心語庭園"]
PLATFORMS = ("youtube_shorts",)
SCENE_SUBTITLE_GROUP_SIZE = 3
MIN_SCENE_CARDS_PER_BRIEF = 3


def scene_card_policy() -> dict[str, int | str]:
    return {
        "subtitleLinesPerScene": SCENE_SUBTITLE_GROUP_SIZE,
        "minSceneCardsPerBrief": MIN_SCENE_CARDS_PER_BRIEF,
        "timingStepSeconds": 7,
        "targetMaxSeconds": 24,
        "rule": "每支短片至少三段場景卡，字幕以三行內一組，方便 9:16 手機剪輯。",
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def chunks(lines: list[str]) -> list[list[str]]:
    if len(lines) <= SCENE_SUBTITLE_GROUP_SIZE:
        return [lines]
    first = lines[:SCENE_SUBTITLE_GROUP_SIZE]
    second = lines[SCENE_SUBTITLE_GROUP_SIZE : SCENE_SUBTITLE_GROUP_SIZE * 2]
    third = lines[SCENE_SUBTITLE_GROUP_SIZE * 2 :]
    return [part for part in (first, second, third) if part]


def caption_for(script: dict, platform: str) -> str:
    tags = " ".join([*GUARDIAN_TAGS.get(script["guardian_id"], []), *COMMON_TAGS])
    cta = "完成 15 題測驗，找到你的情感守護者。"
    if platform == "youtube_shorts":
        link_line = f"{cta}\n測驗入口：{script['tracked_url']}"
    else:
        link_line = f"{cta}\n測驗入口：{script['tracked_url']}"
    return "\n".join([
        script["hook"],
        "",
        script["comment_cta"],
        link_line,
        tags,
    ])


def build_scene_cards(script: dict) -> list[dict]:
    subtitles = chunks([str(line) for line in script.get("full_subtitle_script", [])])
    visuals = [str(item) for item in script.get("visual_suggestions", [])]
    cards = []
    for index, subtitle_lines in enumerate(subtitles, start=1):
        visual = visuals[index - 1] if index <= len(visuals) else visuals[-1] if visuals else ""
        cards.append({
            "scene": index,
            "timing": f"{(index - 1) * 7:02d}-{min(index * 7, 24):02d}s",
            "visualPrompt": visual,
            "subtitleLines": subtitle_lines,
            "overlayText": subtitle_lines[0] if subtitle_lines else "",
        })
    return cards


def build_brief(script: dict) -> dict:
    guardian_id = script["guardian_id"]
    platform_captions = {platform: caption_for(script, platform) for platform in PLATFORMS}
    return {
        "scriptId": script["id"],
        "sourceTaskId": script.get("source_task_id", ""),
        "guardianId": guardian_id,
        "guardianName": script["guardian_name"],
        "guardianTheme": script["guardian_theme"],
        "title": script["title"],
        "hook": script["hook"],
        "format": {
            "aspectRatio": "9:16",
            "targetDuration": "20-30s",
            "primaryCTA": "完成 15 題測驗，找到你的情感守護者。",
            "trackedUrl": script["tracked_url"],
            "recommendedOutput": f"exports/lovetypes/{guardian_id}/{script['id']}.mp4",
        },
        "sceneCards": build_scene_cards(script),
        "captionByPlatform": platform_captions,
        "hashtags": [*GUARDIAN_TAGS.get(guardian_id, []), *COMMON_TAGS],
        "commentCTA": script["comment_cta"],
        "safetyChecklist": [
            "不宣稱診斷、療效或保證修復。",
            "不把短片 CTA 改成直接購買。",
            "不交換守護者名稱、愛之語、色系或象徵物。",
            "字幕維持短句，手機上單行可讀。",
            "發布後回填 posting-queue.csv 與 platform-kpi-tracker.csv；週回顧才彙總 kpi-tracker.csv。",
        ],
    }


def build_payload(pack: dict) -> dict:
    briefs = [build_brief(script) for script in pack.get("scripts", [])]
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "pack": str(PACK_PATH.relative_to(ROOT)),
        },
        "sceneCardPolicy": scene_card_policy(),
        "briefCount": len(briefs),
        "expectedBriefCount": int(pack.get("scriptCount", len(pack.get("scripts", []))) or 0),
        "platformCount": len(PLATFORMS),
        "sceneCardCount": sum(len(brief["sceneCards"]) for brief in briefs),
        "briefs": briefs,
    }


def validate_payload(payload: dict) -> list[str]:
    issues: list[str] = []
    expected_briefs = int(payload.get("expectedBriefCount", 0) or 0)
    if payload.get("briefCount") != expected_briefs:
        issues.append(f"expected {expected_briefs} production briefs, got {payload.get('briefCount')}")
    if payload.get("platformCount") != len(PLATFORMS):
        issues.append(f"expected {len(PLATFORMS)} platforms, got {payload.get('platformCount')}")
    policy = payload.get("sceneCardPolicy", {})
    min_scene_cards = int(policy.get("minSceneCardsPerBrief", 0) or 0) if isinstance(policy, dict) else 0
    if min_scene_cards < 1:
        issues.append("missing scene card policy")
    for brief in payload.get("briefs", []):
        label = brief.get("scriptId", "<unknown>")
        if len(brief.get("sceneCards", [])) < min_scene_cards:
            issues.append(f"{label}: expected at least {min_scene_cards} scene cards")
        captions = brief.get("captionByPlatform", {})
        for platform in PLATFORMS:
            caption = captions.get(platform, "")
            if not caption:
                issues.append(f"{label}: missing {platform} caption")
            if "完成 15 題測驗" not in caption:
                issues.append(f"{label}: {platform} caption missing quiz CTA")
        if "utm_campaign=first_round_quiz_completion" not in brief.get("format", {}).get("trackedUrl", ""):
            issues.append(f"{label}: tracked URL missing first_round_quiz_completion")
        safety_text = " ".join(brief.get("safetyChecklist", []))
        for required in ("不宣稱診斷", "不把短片 CTA 改成直接購買", "發布後回填"):
            if required not in safety_text:
                issues.append(f"{label}: safety checklist missing {required}")
    return issues


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes Now Asset Production Briefs",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- 製作手卡：{payload['briefCount']}",
        f"- 平台 caption：{payload['platformCount']} 種",
        f"- 場景卡：{payload['sceneCardCount']}",
        "",
        "## 使用方式",
        "",
        "- 每張手卡可直接交給剪輯或發布執行。",
        "- Shorts CTA 固定導向測驗，不直接導購。",
        "- 發布後先回填 posting-queue.csv，再回填 platform-kpi-tracker.csv；週回顧才彙總 kpi-tracker.csv。",
        "",
    ]
    for brief in payload["briefs"]:
        fmt = brief["format"]
        lines.extend([
            f"## {brief['guardianName']} · {brief['title']}",
            "",
            f"- 腳本 ID：`{brief['scriptId']}`",
            f"- 來源任務：`{brief['sourceTaskId']}`",
            f"- 守護者宇宙：{brief['guardianTheme']}",
            f"- 格式：{fmt['aspectRatio']} / {fmt['targetDuration']}",
            f"- 輸出檔：`{fmt['recommendedOutput']}`",
            f"- 追蹤連結：{fmt['trackedUrl']}",
            f"- 主 CTA：{fmt['primaryCTA']}",
            "",
            "### 場景卡",
            "",
        ])
        for card in brief["sceneCards"]:
            subtitles = " / ".join(card["subtitleLines"])
            lines.extend([
                f"- Scene {card['scene']}（{card['timing']}）",
                f"  - 畫面：{card['visualPrompt']}",
                f"  - 字幕：{subtitles}",
                f"  - 畫面字：{card['overlayText']}",
            ])
        lines.extend(["", "### 平台 Caption", ""])
        for platform, caption in brief["captionByPlatform"].items():
            lines.extend([
                f"#### {platform}",
                "",
                "```text",
                caption,
                "```",
                "",
            ])
        lines.extend(["### 安全檢查", ""])
        lines.extend(f"- {item}" for item in brief["safetyChecklist"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict, md_path: Path, json_path: Path) -> None:
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes now asset production briefs for editors and publishers.")
    parser.add_argument("--pack", default=str(PACK_PATH))
    parser.add_argument("--output", default=str(BRIEFS_MD_PATH))
    parser.add_argument("--json-output", default=str(BRIEFS_JSON_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload(load_json(Path(args.pack)))
    issues = validate_payload(payload)
    if not args.check:
        write_outputs(payload, Path(args.output), Path(args.json_output))
        print(f"promotion_now_asset_briefs={args.output}")
        print(f"promotion_now_asset_briefs_json={args.json_output}")
    print(f"promotion_now_asset_briefs_count={payload['briefCount']}")
    print(f"promotion_now_asset_briefs_platforms={payload['platformCount']}")
    print(f"promotion_now_asset_briefs_scene_cards={payload['sceneCardCount']}")
    print(f"promotion_now_asset_briefs_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
