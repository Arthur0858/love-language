#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "lead-magnet-inventory.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "lead-magnet-inventory.json"
LANGS = ("zh", "en", "ja", "ko", "es")
GUARDIANS = {
    "iris": "艾莉絲",
    "noah": "諾雅",
    "vivian": "薇薇安",
    "claire": "克萊兒",
    "dora": "朵拉",
}
REQUIRED_PAGE_MARKERS = {
    "shelf": "data-keepsake-shelf",
    "ritual": "data-keepsake-ritual",
    "copy_template": "data-copy-contact-template",
    "supply_request": "collector_supply_mailto",
    "story_download": "collector_story_download",
    "practice_card": "collector_practice_card",
}
REQUIRED_GUARDIAN_MARKERS = (
    "keepsake-card-{guardian}",
    "keepsake-{guardian}",
    "practice-card-{guardian}",
    "{guardian}-story-{lang}.webp",
)


def lang_prefix(lang: str) -> str:
    return "" if lang == "zh" else f"{lang}/"


def keepsake_page_path(lang: str) -> Path:
    return ROOT / lang_prefix(lang) / "keepsakes" / "index.html"


def story_asset_path(lang: str, guardian: str) -> Path:
    return ROOT / "assets" / "lovetypes" / "share" / f"{guardian}-story-{lang}.webp"


def page_url(lang: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    return f"https://lovetypes.tw{prefix}/keepsakes/"


def build_inventory() -> dict:
    pages = []
    assets = []
    for lang in LANGS:
        page_path = keepsake_page_path(lang)
        html = page_path.read_text(encoding="utf-8") if page_path.exists() else ""
        page_entry = {
            "lang": lang,
            "path": str(page_path.relative_to(ROOT)),
            "url": page_url(lang),
            "exists": page_path.exists(),
            "markers": {name: marker in html for name, marker in REQUIRED_PAGE_MARKERS.items()},
            "guardians": [],
        }
        for guardian, guardian_name in GUARDIANS.items():
            asset_path = story_asset_path(lang, guardian)
            guardian_markers = {
                marker.format(guardian=guardian, lang=lang): marker.format(guardian=guardian, lang=lang) in html
                for marker in REQUIRED_GUARDIAN_MARKERS
            }
            page_entry["guardians"].append({
                "guardian": guardian,
                "guardianName": guardian_name,
                "anchor": f"{page_url(lang)}#keepsake-card-{guardian}",
                "practiceAnchor": f"{page_url(lang)}#practice-card-{guardian}",
                "storyAsset": str(asset_path.relative_to(ROOT)),
                "storyAssetExists": asset_path.exists(),
                "pageMarkers": guardian_markers,
                "leadMagnetTypes": [
                    "story_card_image",
                    "printable_practice_card",
                    "future_wallpaper_waitlist",
                    "luna_download_pack_waitlist",
                ],
                "contactHandoff": f"https://lovetypes.tw/{lang_prefix(lang)}contact/#luna-supply-request",
            })
            assets.append({
                "lang": lang,
                "guardian": guardian,
                "path": str(asset_path.relative_to(ROOT)),
                "exists": asset_path.exists(),
            })
        pages.append(page_entry)
    return {
        "generatedAt": date.today().isoformat(),
        "policy": {
            "expectedLanguages": len(LANGS),
            "expectedGuardians": len(GUARDIANS),
            "expectedStoryAssets": len(LANGS) * len(GUARDIANS),
            "minimumPerGuardian": "one savable story card plus one printable practice card route",
            "privacy": "Lead magnets must hand off to email/request templates without storing raw email in CSV.",
            "safety": "Free assets support reflection and repair practice; they do not diagnose, promise outcomes, or replace counseling.",
        },
        "pages": pages,
        "assets": assets,
    }


def validate_inventory(inventory: dict) -> list[str]:
    issues: list[str] = []
    pages = inventory.get("pages", [])
    assets = inventory.get("assets", [])
    expected_pages = len(LANGS)
    expected_assets = len(LANGS) * len(GUARDIANS)
    if len(pages) != expected_pages:
        issues.append(f"expected {expected_pages} keepsake pages, got {len(pages)}")
    if len(assets) != expected_assets:
        issues.append(f"expected {expected_assets} story assets, got {len(assets)}")
    for page in pages:
        lang = page.get("lang", "<unknown>")
        if not page.get("exists"):
            issues.append(f"{lang}: missing keepsake page {page.get('path')}")
            continue
        for name, present in page.get("markers", {}).items():
            if not present:
                issues.append(f"{lang}: missing keepsake page marker {name}")
        guardians = page.get("guardians", [])
        if len(guardians) != len(GUARDIANS):
            issues.append(f"{lang}: expected {len(GUARDIANS)} guardian lead magnets")
        for item in guardians:
            guardian = item.get("guardian", "<unknown>")
            if not item.get("storyAssetExists"):
                issues.append(f"{lang}/{guardian}: missing story asset {item.get('storyAsset')}")
            for marker, present in item.get("pageMarkers", {}).items():
                if not present:
                    issues.append(f"{lang}/{guardian}: missing page marker {marker}")
            types = set(item.get("leadMagnetTypes", []))
            if "story_card_image" not in types or "printable_practice_card" not in types:
                issues.append(f"{lang}/{guardian}: missing required free lead magnet types")
            if not item.get("contactHandoff"):
                issues.append(f"{lang}/{guardian}: missing contact handoff")
    return issues


def render_markdown(inventory: dict, issues: list[str]) -> str:
    policy = inventory["policy"]
    lines = [
        "# LoveTypes Lead Magnet Inventory",
        "",
        f"- 產生日期：{inventory['generatedAt']}",
        f"- 語言數：{policy['expectedLanguages']}",
        f"- 守護者數：{policy['expectedGuardians']}",
        f"- story card assets：{policy['expectedStoryAssets']}",
        f"- issues：{len(issues)}",
        "",
        "## Gate",
        "",
        f"- 每位守護者最低免費素材：{policy['minimumPerGuardian']}",
        f"- 隱私：{policy['privacy']}",
        f"- 安全邊界：{policy['safety']}",
        "",
        "## Inventory",
        "",
    ]
    for page in inventory["pages"]:
        lines.extend([
            f"### {page['lang']} · {page['url']}",
            "",
            f"- HTML：`{page['path']}`",
            f"- 頁面存在：{page['exists']}",
            f"- 頁面標記：{sum(1 for value in page['markers'].values() if value)}/{len(page['markers'])}",
            "",
        ])
        for item in page["guardians"]:
            marker_count = sum(1 for value in item["pageMarkers"].values() if value)
            lines.extend([
                f"- {item['guardianName']}（`{item['guardian']}`）",
                f"  - Story card：`{item['storyAsset']}`",
                f"  - 頁內標記：{marker_count}/{len(item['pageMarkers'])}",
                f"  - 收藏入口：{item['anchor']}",
                f"  - 練習卡入口：{item['practiceAnchor']}",
                f"  - 需求承接：{item['contactHandoff']}",
            ])
        lines.append("")
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(inventory: dict, issues: list[str], output: Path, json_output: Path) -> None:
    json_output.write_text(json.dumps({**inventory, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.write_text(render_markdown(inventory, issues), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit LoveTypes free guardian lead magnets and keepsake handoffs.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    inventory = build_inventory()
    issues = validate_inventory(inventory)
    if not args.check:
        write_outputs(inventory, issues, Path(args.output), Path(args.json_output))
        print(f"promotion_lead_magnet_inventory={args.output}")
        print(f"promotion_lead_magnet_inventory_json={args.json_output}")
    print(f"promotion_lead_magnet_inventory_languages={len(inventory['pages'])}")
    print(f"promotion_lead_magnet_inventory_guardians={len(GUARDIANS)}")
    print(f"promotion_lead_magnet_inventory_story_assets={sum(1 for item in inventory['assets'] if item['exists'])}")
    print(f"promotion_lead_magnet_inventory_expected_story_assets={inventory['policy']['expectedStoryAssets']}")
    print(f"promotion_lead_magnet_inventory_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
