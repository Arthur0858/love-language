#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
OUTPUT_MD_PATH = PROMOTION_DIR / "platform-profile-setup.md"
OUTPUT_JSON_PATH = PROMOTION_DIR / "platform-profile-setup.json"
PRIMARY_URL = "https://lovetypes.tw/start/"
CAMPAIGN = "first_round_quiz_completion"
PLATFORMS = {
    "youtube_shorts": {
        "label": "YouTube Shorts",
        "utm_source": "youtube",
        "profile_link_label": "Channel description / video description",
        "bio": "LoveTypes 心語庭園｜完成 15 題測驗，找到你的情感守護者。",
        "pinned_comment": "完成 15 題測驗，找到你的情感守護者：{url}\n留言 A/B/C，我們會用守護者路線回覆你。",
        "link_limit_note": "YouTube 說明欄可放完整追蹤連結；置頂留言也放同一條。",
    },
    "tiktok": {
        "label": "TikTok",
        "utm_source": "tiktok",
        "profile_link_label": "Profile website link",
        "bio": "五種愛之語測驗｜進入心語庭園，找到你的情感守護者。",
        "pinned_comment": "完成 15 題測驗，找到你的情感守護者。入口在個人頁連結。\n留言 A/B/C，選出最像你的心語。",
        "link_limit_note": "若 caption 不能放可點連結，Bio/個人頁連結必須使用平台專屬追蹤連結。",
    },
    "instagram_reels": {
        "label": "Instagram Reels",
        "utm_source": "instagram",
        "profile_link_label": "Profile link in bio",
        "bio": "LoveTypes 心語庭園｜15 題找到你的情感守護者。",
        "pinned_comment": "完成 15 題測驗，找到你的情感守護者。入口在個人檔案連結。\n留言你的 A/B/C，讓守護者把心語接住。",
        "link_limit_note": "IG Reels caption 以個人檔案連結承接；Bio 連結需先於發布前更新。",
    },
}


def tracked_url(platform_id: str, utm_source: str) -> str:
    query = urlencode({
        "utm_source": utm_source,
        "utm_medium": "social_profile",
        "utm_campaign": CAMPAIGN,
        "utm_content": f"{platform_id}_bio",
    })
    return f"{PRIMARY_URL}?{query}"


def validate_url(source: str, value: str, platform_id: str, utm_source: str) -> list[str]:
    issues: list[str] = []
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    expected = {
        "utm_source": utm_source,
        "utm_medium": "social_profile",
        "utm_campaign": CAMPAIGN,
        "utm_content": f"{platform_id}_bio",
    }
    if parsed.scheme != "https" or parsed.netloc != "lovetypes.tw" or parsed.path != "/start/":
        issues.append(f"{source}: link should point to https://lovetypes.tw/start/")
    for key, expected_value in expected.items():
        if query.get(key, [""])[0] != expected_value:
            issues.append(f"{source}: missing {key}={expected_value}")
    return issues


def build_setup() -> dict:
    platforms = []
    for platform_id, config in PLATFORMS.items():
        url = tracked_url(platform_id, config["utm_source"])
        platforms.append({
            "platformId": platform_id,
            "label": config["label"],
            "profileLinkLabel": config["profile_link_label"],
            "profileLink": url,
            "bio": config["bio"],
            "pinnedComment": config["pinned_comment"].format(url=url),
            "linkLimitNote": config["link_limit_note"],
            "launchChecklist": [
                "發布第一支 Shorts/Reels 前，先確認 profile link 使用平台專屬追蹤連結。",
                "Bio 不直接導購，只保留測驗與情感守護者入口。",
                "置頂留言或首則留言維持單一 CTA：完成 15 題測驗。",
                "發布後回填 profile_clicks、site_clicks、quiz_starts、quiz_completions。",
            ],
            "kpiFieldsToFill": [
                "profile_clicks",
                "site_clicks",
                "quiz_starts",
                "quiz_completions",
                "guardian_result_clicks",
                "resources_clicks",
                "luna_clicks",
            ],
        })
    return {
        "generatedAt": date.today().isoformat(),
        "primaryUrl": PRIMARY_URL,
        "utmCampaign": CAMPAIGN,
        "platformCount": len(platforms),
        "platforms": platforms,
        "safety": {
            "primaryCta": "完成 15 題測驗，找到你的情感守護者。",
            "doNotUse": ["診斷", "療效", "保證修復", "必須購買"],
            "commercialBoundary": "平台首頁先承接測驗完成量，不直接推 Luna、聯盟書卷或付費商品。",
        },
    }


def validate_setup(setup: dict) -> list[str]:
    issues: list[str] = []
    platforms = setup.get("platforms", [])
    if setup.get("platformCount") != 3:
        issues.append(f"expected 3 platform setups, got {setup.get('platformCount')}")
    if len(platforms) != setup.get("platformCount"):
        issues.append("platformCount should match platforms length")
    seen: set[str] = set()
    for item in platforms:
        platform_id = item.get("platformId", "")
        config = PLATFORMS.get(platform_id)
        label = platform_id or "<platform>"
        if not config:
            issues.append(f"{label}: unexpected platform")
            continue
        if platform_id in seen:
            issues.append(f"{label}: duplicate platform setup")
        seen.add(platform_id)
        issues.extend(validate_url(label, item.get("profileLink", ""), platform_id, config["utm_source"]))
        for field in ("bio", "pinnedComment", "profileLinkLabel", "linkLimitNote"):
            if not item.get(field):
                issues.append(f"{label}: missing {field}")
        text = f"{item.get('bio', '')} {item.get('pinnedComment', '')}"
        if "完成 15 題測驗" not in text:
            issues.append(f"{label}: setup should include quiz CTA")
        for forbidden in ("診斷", "療效", "保證修復", "必須購買"):
            if forbidden in item.get("bio", "") or forbidden in item.get("pinnedComment", ""):
                issues.append(f"{label}: forbidden claim {forbidden}")
        checklist = item.get("launchChecklist", [])
        if not isinstance(checklist, list) or len(checklist) < 4:
            issues.append(f"{label}: launchChecklist should include at least four items")
        kpis = set(item.get("kpiFieldsToFill", []))
        if not {"profile_clicks", "site_clicks", "quiz_starts", "quiz_completions"}.issubset(kpis):
            issues.append(f"{label}: missing core KPI fields")
    missing = set(PLATFORMS) - seen
    if missing:
        issues.append(f"missing platform setups: {', '.join(sorted(missing))}")
    return issues


def render_markdown(setup: dict) -> str:
    lines = [
        "# LoveTypes 平台首頁設定檢查包",
        "",
        f"- 產生日期：{setup['generatedAt']}",
        f"- 平台數：{setup['platformCount']}",
        f"- 主入口：{setup['primaryUrl']}",
        f"- UTM campaign：`{setup['utmCampaign']}`",
        "",
        "## 使用規則",
        "",
        "- 發布第一支 Shorts/Reels 前，先完成三個平台首頁設定。",
        "- 首頁 Bio 和置頂留言只導向測驗，不直接導購。",
        "- 平台若不能放可點連結，仍要在 Bio/個人頁連結使用平台專屬追蹤 URL。",
        "- 發布後把 profile_clicks 與 site_clicks 一起回填，才能判斷個人頁承接是否有效。",
        "",
    ]
    for item in setup["platforms"]:
        lines.extend([
            f"## {item['label']}",
            "",
            f"- 連結位置：{item['profileLinkLabel']}",
            f"- Profile link：{item['profileLink']}",
            f"- 限制備註：{item['linkLimitNote']}",
            "",
            "### Bio",
            "",
            "```text",
            item["bio"],
            "```",
            "",
            "### 置頂留言 / 首則留言",
            "",
            "```text",
            item["pinnedComment"],
            "```",
            "",
            "### 發布前檢查",
            "",
        ])
        lines.extend(f"- {check}" for check in item["launchChecklist"])
        lines.extend(["", "### KPI 回填欄位", ""])
        lines.extend(f"- `{field}`" for field in item["kpiFieldsToFill"])
        lines.append("")
    lines.extend([
        "## 商業邊界",
        "",
        f"- {setup['safety']['commercialBoundary']}",
        f"- 不使用：{', '.join(setup['safety']['doNotUse'])}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(setup: dict, md_path: Path, json_path: Path) -> None:
    md_path.write_text(render_markdown(setup), encoding="utf-8")
    json_path.write_text(json.dumps(setup, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes platform profile setup checklist for Shorts launch.")
    parser.add_argument("--output", default=str(OUTPUT_MD_PATH))
    parser.add_argument("--json-output", default=str(OUTPUT_JSON_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    setup = build_setup()
    issues = validate_setup(setup)
    if not args.check:
        write_outputs(setup, Path(args.output), Path(args.json_output))
        print(f"promotion_platform_profile_setup={args.output}")
        print(f"promotion_platform_profile_setup_json={args.json_output}")
    print(f"promotion_platform_profile_setup_platforms={setup['platformCount']}")
    print(f"promotion_platform_profile_setup_kpi_fields={sum(len(item['kpiFieldsToFill']) for item in setup['platforms'])}")
    print(f"promotion_platform_profile_setup_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
