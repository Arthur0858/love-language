#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "lead-intake-playbook.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "lead-intake-playbook.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "lead-intake-tracker.csv"
GUARDIAN_ORDER = ["iris", "noah", "vivian", "claire", "dora"]
INTAKE_TYPES = [
    {
        "type": "owned_asset_request",
        "requestedAsset": "guardian PDF / wallpaper / short ritual",
        "priority": "medium",
        "firstResponse": "確認想收到的守護者素材，回覆預計製作方向與安全邊界。",
        "nextAction": "累積同守護者重複需求後，排進 asset-build-backlog 的 build_owned_asset。",
    },
    {
        "type": "luna_scene_request",
        "requestedAsset": "Luna bedtime / conflict cooldown / quiz aftercare pack",
        "priority": "medium",
        "firstResponse": "確認使用情境，不承諾療效，只提供夜間整理或冷卻素材方向。",
        "nextAction": "若同守護者 Luna 需求重複，才測試結果後柔性商品承接。",
    },
    {
        "type": "repair_or_contact_request",
        "requestedAsset": "relationship repair prompt / supply route guidance",
        "priority": "high",
        "firstResponse": "回覆可提供的網站路線與自助素材，不收集敏感個資，不取代諮商。",
        "nextAction": "整理成 FAQ、修復計畫或 Contact 模板，不把個案內容公開。",
    },
]
CSV_FIELDS = [
    "request_id",
    "date",
    "source",
    "guardian_id",
    "guardian_name",
    "intake_type",
    "requested_asset",
    "related_route",
    "email_status",
    "consent_status",
    "priority",
    "status",
    "first_response",
    "next_action",
    "follow_up_deadline",
    "fulfillment_asset",
    "notes",
]


def load_tasks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("publishingTasks", [])
    return tasks if isinstance(tasks, list) else []


def group_guardians(tasks: list[dict]) -> dict[str, dict]:
    guardians: dict[str, dict] = {}
    for task in tasks:
        guardian_id = str(task.get("guardianId", "")).strip()
        if guardian_id not in GUARDIAN_ORDER or guardian_id in guardians:
            continue
        path = task.get("conversionPath", {}) if isinstance(task.get("conversionPath"), dict) else {}
        bridge = task.get("monetizationBridge", {}) if isinstance(task.get("monetizationBridge"), dict) else {}
        guardians[guardian_id] = {
            "guardianId": guardian_id,
            "guardianName": str(task.get("guardianName") or guardian_id),
            "conversionPath": path,
            "monetizationBridge": {
                "primaryFreeItemId": bridge.get("primaryFreeItemId"),
                "ownedLeadItemId": bridge.get("ownedLeadItemId"),
                "lunaProductIds": bridge.get("lunaProductIds", []),
                "affiliateItemIds": bridge.get("affiliateItemIds", []),
                "safetyNote": bridge.get("safetyNote", ""),
            },
        }
    return guardians


def route_for_intake(path: dict, intake_type: str) -> str:
    if intake_type == "owned_asset_request":
        return str(path.get("keepsake") or path.get("supplyRoute") or "")
    if intake_type == "luna_scene_request":
        return str(path.get("lunaScene") or path.get("contactRequest") or "")
    return str(path.get("contactRequest") or path.get("repairPlan") or "")


def build_playbook(tasks: list[dict]) -> dict:
    guardians_by_id = group_guardians(tasks)
    guardians = []
    rows = []
    for guardian_id in GUARDIAN_ORDER:
        guardian = guardians_by_id.get(guardian_id)
        if not guardian:
            continue
        path = guardian["conversionPath"]
        guardian_rows = []
        for intake in INTAKE_TYPES:
            request_id = f"template-{guardian_id}-{intake['type']}"
            row = {
                "request_id": request_id,
                "date": "",
                "source": "contact_or_waitlist",
                "guardian_id": guardian_id,
                "guardian_name": guardian["guardianName"],
                "intake_type": intake["type"],
                "requested_asset": intake["requestedAsset"],
                "related_route": route_for_intake(path, intake["type"]),
                "email_status": "not_received",
                "consent_status": "not_applicable_until_user_contacts",
                "priority": intake["priority"],
                "status": "template",
                "first_response": intake["firstResponse"],
                "next_action": intake["nextAction"],
                "follow_up_deadline": "",
                "fulfillment_asset": "",
                "notes": "No user data. Replace this template row only after a real request arrives.",
            }
            rows.append(row)
            guardian_rows.append(row)
        guardians.append({
            **guardian,
            "intakeRows": guardian_rows,
            "firstOwnedAsset": guardian["monetizationBridge"].get("ownedLeadItemId"),
            "recommendedPolicy": "只記錄守護者、需求類型、素材偏好與可回覆信箱；不要求測驗分數、敏感個資或關係細節。",
        })
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "promotionKit": str(KIT_PATH.relative_to(ROOT)),
            "csvTracker": str(DEFAULT_CSV_OUTPUT_PATH.relative_to(ROOT)),
        },
        "guardians": guardians,
        "trackerRows": rows,
        "intakeTypes": INTAKE_TYPES,
        "workflow": [
            "收到 Contact、收藏室等待清單或旅人補給願望後，先填 lead-intake-tracker.csv。",
            "同一守護者同一需求類型重複出現兩次以上，才排進自有素材製作。",
            "Luna 或聯盟需求只在測驗結果後路線測試，不把 Shorts CTA 改成購買。",
            "回覆時保持安全邊界：不診斷、不承諾療效、不要求敏感個資。",
        ],
        "safety": {
            "noFakeLeads": True,
            "doNotCollect": ["quiz score", "sensitive personal details", "emergency requests", "therapy replacement claims"],
            "firstResponseTone": "reflective, optional, non-therapeutic",
        },
    }


def render_markdown(playbook: dict) -> str:
    lines = [
        "# LoveTypes 名單承接 Playbook",
        "",
        f"- 產生日期：{playbook['generatedAt']}",
        f"- 模板列數：{len(playbook['trackerRows'])}",
        "- 用途：把 Contact、補給願望、收藏物等待清單與 Luna 需求轉成可回填、可排序、可履約的素材線索。",
        "",
        "## 使用規則",
        "",
    ]
    lines.extend(f"- {item}" for item in playbook["workflow"])
    lines.extend(["", "## 五守護者承接路線", ""])
    for guardian in playbook["guardians"]:
        lines.extend([
            f"### {guardian['guardianName']}（{guardian['guardianId']}）",
            "",
            f"- 名單資產 ID：{guardian['firstOwnedAsset']}",
            f"- 安全策略：{guardian['recommendedPolicy']}",
        ])
        for row in guardian["intakeRows"]:
            lines.append(f"- `{row['intake_type']}`：{row['requested_asset']} -> {row['related_route']}")
        lines.append("")
    lines.extend([
        "## 回填欄位",
        "",
        "- `request_id`: 真實需求發生後改成可追蹤 ID，例如 `2026-06-15-iris-owned-001`。",
        "- `source`: contact、keepsake_waitlist、resources_wishlist、luna_page 或 manual_reply。",
        "- `email_status`: not_received、received、replied、fulfilled、closed。",
        "- `consent_status`: not_applicable_until_user_contacts、explicit_reply_ok、do_not_contact。",
        "- `status`: template、new、triaged、queued、fulfilled、closed。",
        "",
        "## 安全邊界",
        "",
        "- 模板列不代表真實名單或需求，不可當成成效數據。",
        "- 不要求測驗分數、敏感個資、緊急求助內容或諮商替代承諾。",
        "- 同守護者同需求至少重複兩次，才提高自有素材或 Luna 商品承接優先級。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(playbook: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(playbook), encoding="utf-8")
    json_output.write_text(json.dumps(playbook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(playbook["trackerRows"])


def validate_playbook(playbook: dict) -> list[str]:
    issues: list[str] = []
    if len(playbook.get("guardians", [])) != 5:
        issues.append("expected five guardian intake sections")
    rows = playbook.get("trackerRows", [])
    if len(rows) != len(GUARDIAN_ORDER) * len(INTAKE_TYPES):
        issues.append("expected one template row per guardian and intake type")
    if any(row.get("email_status") != "not_received" for row in rows):
        issues.append("template rows must not imply received user emails")
    if any(row.get("status") != "template" for row in rows):
        issues.append("template rows must keep template status")
    for row in rows:
        if not row.get("guardian_id") or not row.get("intake_type") or not row.get("related_route"):
            issues.append(f"{row.get('request_id', '<unknown>')}: missing guardian, intake type, or route")
    if not playbook.get("safety", {}).get("noFakeLeads"):
        issues.append("playbook must mark noFakeLeads safety boundary")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes lead intake and owned-asset fulfillment playbook.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    playbook = build_playbook(load_tasks(Path(args.kit)))
    issues = validate_playbook(playbook)
    if not args.check:
        write_outputs(playbook, Path(args.output), Path(args.json_output), Path(args.csv_output))
        print(f"promotion_lead_intake_playbook={args.output}")
        print(f"promotion_lead_intake_json={args.json_output}")
        print(f"promotion_lead_intake_tracker={args.csv_output}")
    print(f"promotion_lead_intake_guardians={len(playbook['guardians'])}")
    print(f"promotion_lead_intake_template_rows={len(playbook['trackerRows'])}")
    print(f"promotion_lead_intake_types={len(playbook['intakeTypes'])}")
    print(f"promotion_lead_intake_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
