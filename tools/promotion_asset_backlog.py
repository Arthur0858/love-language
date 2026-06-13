#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
DECISION_MATRIX_PATH = PROMOTION_DIR / "revenue-decision-matrix.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "asset-build-backlog.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "asset-build-backlog.json"
GUARDIAN_ORDER = ["iris", "noah", "vivian", "claire", "dora"]
ASSET_TYPES = [
    "free_story_card_upgrade",
    "pdf_practice_card",
    "phone_wallpaper",
    "email_lead_template",
    "short_ritual",
    "luna_scene_cta",
    "affiliate_book_bundle",
    "content_variant",
]
STAGE_TO_ASSETS = {
    "collect_signal": ["content_variant"],
    "publish_guardian_variants": ["content_variant", "free_story_card_upgrade"],
    "deepen_identity_asset": ["free_story_card_upgrade", "pdf_practice_card", "phone_wallpaper"],
    "build_owned_asset": ["email_lead_template", "pdf_practice_card", "short_ritual"],
    "test_soft_offer": ["luna_scene_cta", "affiliate_book_bundle", "email_lead_template"],
}
ASSET_COPY = {
    "free_story_card_upgrade": {
        "title": "免費守護者故事卡升級",
        "format": "1080x1920 story card / share card",
        "trigger": "free_keepsake_downloads 或 keepsake_clicks 開始出現",
    },
    "pdf_practice_card": {
        "title": "PDF 練習卡",
        "format": "1 頁可列印 PDF",
        "trigger": "supply_lead_requests 或 contact_requests 開始出現",
    },
    "phone_wallpaper": {
        "title": "手機桌布",
        "format": "1170x2532 / 1290x2796 wallpaper",
        "trigger": "收藏物保存或分享明顯高於其他路線",
    },
    "email_lead_template": {
        "title": "Email 名單承接模板",
        "format": "subject + body + thank-you copy",
        "trigger": "supply_lead_requests 或 contact_requests 大於 0",
    },
    "short_ritual": {
        "title": "7 分鐘短儀式",
        "format": "短文案 + 步驟卡 + Luna 引導入口",
        "trigger": "修復計畫或補給路線點擊開始累積",
    },
    "luna_scene_cta": {
        "title": "Luna 場景 CTA",
        "format": "睡前 / 衝突後 / 測驗後承接文案",
        "trigger": "luna_clicks 或 luna_pack_clicks 大於 0",
    },
    "affiliate_book_bundle": {
        "title": "聯盟書卷組合",
        "format": "每位守護者 1-3 本延伸書卷包裝",
        "trigger": "affiliate_book_clicks 大於 0",
    },
    "content_variant": {
        "title": "短影片痛點變體",
        "format": "同守護者不同情境 hook / subtitle / CTA",
        "trigger": "quiz_completions 有累積但尚無明確獲利意圖",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_tasks(path: Path) -> list[dict]:
    data = load_json(path)
    tasks = data.get("publishingTasks", [])
    return tasks if isinstance(tasks, list) else []


def tasks_by_guardian(tasks: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for task in tasks:
        grouped[str(task.get("guardianId", ""))].append(task)
    for guardian in grouped:
        grouped[guardian].sort(key=lambda task: (int(task.get("week", 0) or 0), int(task.get("slot", 0) or 0)))
    return grouped


def matrix_by_guardian(matrix: dict) -> dict[str, dict]:
    return {str(item.get("guardianId", "")): item for item in matrix.get("guardians", [])}


def guardian_name(tasks: list[dict], fallback: str) -> str:
    for task in tasks:
        if task.get("guardianName"):
            return str(task["guardianName"])
    return fallback


def build_item(guardian: str, name: str, asset_type: str, task: dict, matrix_item: dict) -> dict:
    meta = ASSET_COPY[asset_type]
    bridge = task.get("monetizationBridge", {}) if isinstance(task.get("monetizationBridge"), dict) else {}
    path = task.get("conversionPath", {}) if isinstance(task.get("conversionPath"), dict) else {}
    target_url = target_for_asset(asset_type, path)
    return {
        "id": f"{guardian}-{asset_type}",
        "guardianId": guardian,
        "guardianName": name,
        "assetType": asset_type,
        "title": meta["title"],
        "format": meta["format"],
        "trigger": meta["trigger"],
        "stage": matrix_item.get("stage", "collect_signal"),
        "priority": "now" if asset_type in STAGE_TO_ASSETS.get(matrix_item.get("stage", "collect_signal"), []) else "later",
        "sourceTaskId": task.get("taskId"),
        "sourceTitle": task.get("title"),
        "sourceTrackedUrl": task.get("trackedUrl"),
        "freeItemId": bridge.get("primaryFreeItemId"),
        "leadItemId": bridge.get("ownedLeadItemId"),
        "keepsakeUrl": path.get("keepsake"),
        "supplyUrl": path.get("supplyRoute"),
        "repairUrl": path.get("repairPlan"),
        "lunaUrl": path.get("lunaScene"),
        "contactUrl": path.get("contactRequest"),
        "targetUrl": target_url,
        "safety": "不承諾療效，不替代諮商，不把短影片 CTA 改成直接購買。",
    }


def target_for_asset(asset_type: str, path: dict) -> str:
    if asset_type in {"free_story_card_upgrade", "pdf_practice_card", "phone_wallpaper"}:
        return str(path.get("keepsake") or "")
    if asset_type == "email_lead_template":
        return str(path.get("contactRequest") or path.get("supplyRoute") or "")
    if asset_type == "short_ritual":
        return str(path.get("repairPlan") or path.get("lunaScene") or "")
    if asset_type == "luna_scene_cta":
        return str(path.get("lunaScene") or "")
    if asset_type == "affiliate_book_bundle":
        return str(path.get("supplyRoute") or "")
    if asset_type == "content_variant":
        return str(path.get("quizEntry") or path.get("guardianProfile") or "")
    return str(path.get("quizEntry") or "")


def build_backlog(tasks: list[dict], matrix: dict) -> dict:
    grouped_tasks = tasks_by_guardian(tasks)
    grouped_matrix = matrix_by_guardian(matrix)
    expected_guardians = [guardian for guardian in GUARDIAN_ORDER if guardian in grouped_tasks]
    items = []
    for guardian in GUARDIAN_ORDER:
        guardian_tasks = grouped_tasks.get(guardian, [])
        if not guardian_tasks:
            continue
        matrix_item = grouped_matrix.get(guardian, {})
        name = guardian_name(guardian_tasks, guardian)
        source_task = guardian_tasks[0]
        for asset_type in ASSET_TYPES:
            items.append(build_item(guardian, name, asset_type, source_task, matrix_item))
    priority_counts = defaultdict(int)
    for item in items:
        priority_counts[item["priority"]] += 1
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "promotionKit": str(KIT_PATH.relative_to(ROOT)),
            "decisionMatrix": str(DECISION_MATRIX_PATH.relative_to(ROOT)),
        },
        "itemCount": len(items),
        "guardianCount": len({item["guardianId"] for item in items}),
        "expectedGuardianCount": len(expected_guardians),
        "expectedItemCount": len(expected_guardians) * len(ASSET_TYPES),
        "assetTypes": ASSET_TYPES,
        "priorityCounts": dict(sorted(priority_counts.items())),
        "items": items,
        "safety": {
            "shortsCta": "完成 15 題測驗，找到你的情感守護者",
            "doNotClaim": ["診斷", "療效", "保證修復", "必須購買"],
            "emptyDataBoundary": "空資料時只準備資產，不提前改公開商品優先序。",
        },
    }


def render_markdown(backlog: dict) -> str:
    lines = [
        "# LoveTypes 守護者獲利資產 Backlog",
        "",
        f"- 產生日期：{backlog['generatedAt']}",
        f"- 任務數：{backlog['itemCount']}",
        f"- 守護者數：{backlog['guardianCount']}",
        f"- 立即任務：{backlog['priorityCounts'].get('now', 0)}",
        f"- 後續任務：{backlog['priorityCounts'].get('later', 0)}",
        "",
        "## 使用方式",
        "",
        "- 先看 `revenue-decision-matrix.md` 的階段，再看本 backlog 的 `priority=now`。",
        "- 空資料時只準備資產，不調整網站商品排序或短影片 CTA。",
        "- 有名單、Luna、聯盟點擊後，再把對應守護者的 later 任務拉到 now。",
        "",
    ]
    for guardian in GUARDIAN_ORDER:
        guardian_items = [item for item in backlog["items"] if item["guardianId"] == guardian]
        if not guardian_items:
            continue
        lines.extend([f"## {guardian_items[0]['guardianName']}（{guardian}）", ""])
        for item in guardian_items:
            lines.extend([
                f"### {item['title']}",
                "",
                f"- ID：`{item['id']}`",
                f"- 優先序：`{item['priority']}`",
                f"- 階段：`{item['stage']}`",
                f"- 格式：{item['format']}",
                f"- 觸發條件：{item['trigger']}",
                f"- 來源腳本：{item['sourceTaskId']} · {item['sourceTitle']}",
                f"- 追蹤連結：{item['sourceTrackedUrl']}",
                f"- 免費資產 ID：{item['freeItemId']}",
                f"- 名單資產 ID：{item['leadItemId']}",
                f"- 入口：{item['targetUrl']}",
                f"- 安全邊界：{item['safety']}",
                "",
            ])
    lines.extend([
        "## 安全邊界",
        "",
        f"- Shorts CTA：{backlog['safety']['shortsCta']}",
        "- 不使用診斷、療效、保證修復或必須購買的說法。",
        f"- {backlog['safety']['emptyDataBoundary']}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def validate_backlog(backlog: dict) -> list[str]:
    issues: list[str] = []
    expected_guardians = int(backlog.get("expectedGuardianCount", 0) or 0)
    if backlog.get("guardianCount") != expected_guardians:
        issues.append(f"expected {expected_guardians} guardians in asset backlog")
    expected_items = int(backlog.get("expectedItemCount", 0) or 0)
    if backlog.get("itemCount") != expected_items:
        issues.append(f"expected {expected_items} asset backlog items")
    by_guardian = defaultdict(list)
    for item in backlog.get("items", []):
        by_guardian[item.get("guardianId")].append(item)
        for field in ("id", "assetType", "title", "format", "trigger", "priority", "sourceTrackedUrl", "freeItemId", "leadItemId", "targetUrl"):
            if not item.get(field):
                issues.append(f"{item.get('id', '<unknown>')}: missing {field}")
        if item.get("priority") not in {"now", "later"}:
            issues.append(f"{item.get('id', '<unknown>')}: invalid priority")
    for guardian in GUARDIAN_ORDER:
        if len(by_guardian.get(guardian, [])) != len(ASSET_TYPES):
            issues.append(f"{guardian}: expected {len(ASSET_TYPES)} asset tasks")
    return issues


def write_outputs(backlog: dict, output: Path, json_output: Path) -> None:
    output.write_text(render_markdown(backlog), encoding="utf-8")
    json_output.write_text(json.dumps(backlog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes guardian monetization asset backlog.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--matrix", default=str(DECISION_MATRIX_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    backlog = build_backlog(load_tasks(Path(args.kit)), load_json(Path(args.matrix)))
    issues = validate_backlog(backlog)
    if not args.check:
        write_outputs(backlog, Path(args.output), Path(args.json_output))
        print(f"promotion_asset_backlog={args.output}")
        print(f"promotion_asset_backlog_json={args.json_output}")
    print(f"promotion_asset_backlog_guardians={backlog['guardianCount']}")
    print(f"promotion_asset_backlog_items={backlog['itemCount']}")
    print(f"promotion_asset_backlog_now={backlog['priorityCounts'].get('now', 0)}")
    print(f"promotion_asset_backlog_later={backlog['priorityCounts'].get('later', 0)}")
    print(f"promotion_asset_backlog_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
