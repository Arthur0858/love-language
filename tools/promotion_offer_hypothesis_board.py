#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
MATRIX_PATH = PROMOTION_DIR / "revenue-decision-matrix.json"
GATE_PATH = PROMOTION_DIR / "week-decision-gate.json"
LEAD_INTAKE_PATH = PROMOTION_DIR / "lead-intake-playbook.json"
BACKLOG_PATH = PROMOTION_DIR / "asset-build-backlog.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "offer-hypothesis-board.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "offer-hypothesis-board.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "offer-hypothesis-board.csv"
GUARDIAN_ORDER = ["iris", "noah", "vivian", "claire", "dora"]
CSV_FIELDS = [
    "guardian_id",
    "guardian_name",
    "stage",
    "offer_hypothesis",
    "free_asset",
    "owned_asset",
    "luna_test",
    "affiliate_test",
    "readiness",
    "next_validation",
    "target_url",
    "safety_boundary",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def by_guardian(items: list[dict], key: str = "guardianId") -> dict[str, dict]:
    return {str(item.get(key, "")): item for item in items}


def backlog_items(backlog: dict, guardian_id: str) -> list[dict]:
    return [item for item in backlog.get("items", []) if item.get("guardianId") == guardian_id]


def first_asset(items: list[dict], asset_type: str) -> dict:
    return next((item for item in items if item.get("assetType") == asset_type), {})


def intake_rows(playbook: dict, guardian_id: str) -> list[dict]:
    return [row for row in playbook.get("trackerRows", []) if row.get("guardian_id") == guardian_id]


def readiness_for(stage: str, gate: dict) -> str:
    gates = gate.get("gates", {})
    if stage == "test_soft_offer":
        return "PASS" if gates.get("testSoftOffer") else "HOLD"
    if stage == "build_owned_asset":
        return "PASS" if gates.get("buildOwnedLeadAsset") else "HOLD"
    if stage == "deepen_identity_asset":
        return "PASS" if gates.get("deepenIdentityAsset") else "HOLD"
    if stage == "publish_guardian_variants":
        return "PASS" if gates.get("scaleContent") else "HOLD"
    return "HOLD"


def validation_step(stage: str, readiness: str) -> str:
    if readiness == "PASS" and stage == "test_soft_offer":
        return "在結果後路線測試 Luna starter 或聯盟書卷，不改 Shorts CTA。"
    if readiness == "PASS" and stage == "build_owned_asset":
        return "製作一個最小自有素材，回填 fulfilled 與後續點擊。"
    if readiness == "PASS" and stage == "deepen_identity_asset":
        return "強化免費收藏物，觀察保存、分享與回訪。"
    if readiness == "PASS":
        return "放大同守護者內容變體，觀察測驗完成。"
    return "先發布與回填 KPI；不新增付費 CTA，不改商品排序。"


def build_board(matrix: dict, gate: dict, playbook: dict, backlog: dict) -> dict:
    matrix_guardians = by_guardian(matrix.get("guardians", []))
    expected_guardians = [guardian for guardian in GUARDIAN_ORDER if guardian in matrix_guardians]
    expected_intake_templates = len(playbook.get("intakeTypes", [])) if isinstance(playbook.get("intakeTypes"), list) else 0
    rows = []
    for guardian_id in GUARDIAN_ORDER:
        item = matrix_guardians.get(guardian_id, {})
        if not item:
            continue
        stage = str(item.get("stage") or "collect_signal")
        items = backlog_items(backlog, guardian_id)
        free_asset = first_asset(items, "free_story_card_upgrade") or first_asset(items, "pdf_practice_card")
        owned_asset = first_asset(items, "email_lead_template") or first_asset(items, "short_ritual")
        luna_asset = first_asset(items, "luna_scene_cta")
        affiliate_asset = first_asset(items, "affiliate_book_bundle")
        bridge = item.get("monetizationBridge", {}) if isinstance(item.get("monetizationBridge"), dict) else {}
        path = item.get("conversionPath", {}) if isinstance(item.get("conversionPath"), dict) else {}
        readiness = readiness_for(stage, gate)
        offer_hypothesis = {
            "collect_signal": "目前只驗證測驗完成與守護者認同，不提出商品假設。",
            "publish_guardian_variants": "同守護者痛點變體可提高測驗完成後，再判斷是否值得做保存物。",
            "deepen_identity_asset": "免費收藏物若被保存或分享，可延伸成 PDF、桌布或故事卡。",
            "build_owned_asset": "重複名單需求可轉成 Email 素材、PDF 練習卡或短儀式。",
            "test_soft_offer": "Luna 或聯盟點擊出現後，只在結果後路線測試柔性商品承接。",
        }.get(stage, "先收集訊號。")
        rows.append({
            "guardianId": guardian_id,
            "guardianName": item.get("guardianName", guardian_id),
            "stage": stage,
            "offerHypothesis": offer_hypothesis,
            "freeAsset": {
                "id": free_asset.get("id"),
                "targetUrl": free_asset.get("targetUrl") or path.get("keepsake"),
                "freeItemId": bridge.get("primaryFreeItemId"),
            },
            "ownedAsset": {
                "id": owned_asset.get("id"),
                "targetUrl": owned_asset.get("targetUrl") or path.get("contactRequest"),
                "leadItemId": bridge.get("ownedLeadItemId"),
                "intakeTemplates": len(intake_rows(playbook, guardian_id)),
            },
            "lunaTest": {
                "id": luna_asset.get("id"),
                "targetUrl": luna_asset.get("targetUrl") or path.get("lunaScene"),
                "productIds": bridge.get("lunaProductIds", []),
            },
            "affiliateTest": {
                "id": affiliate_asset.get("id"),
                "targetUrl": affiliate_asset.get("targetUrl") or path.get("supplyRoute"),
                "itemIds": bridge.get("affiliateItemIds", []),
            },
            "readiness": readiness,
            "nextValidation": validation_step(stage, readiness),
            "targetUrl": path.get("quizEntry") if readiness == "HOLD" else (item.get("recommendedAction", {}) or {}).get("target", path.get("quizEntry")),
            "safetyBoundary": "商品假設只能在測驗結果後或補給路線測試；不得承諾療效、診斷或必須購買。",
        })
    blockers = list(gate.get("blockers", []))
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "revenueDecisionMatrix": str(MATRIX_PATH.relative_to(ROOT)),
            "weekDecisionGate": str(GATE_PATH.relative_to(ROOT)),
            "leadIntakePlaybook": str(LEAD_INTAKE_PATH.relative_to(ROOT)),
            "assetBuildBacklog": str(BACKLOG_PATH.relative_to(ROOT)),
        },
        "rows": rows,
        "expectedRowCount": len(expected_guardians),
        "expectedIntakeTemplatesPerGuardian": expected_intake_templates,
        "readyRows": sum(1 for row in rows if row["readiness"] == "PASS"),
        "holdRows": sum(1 for row in rows if row["readiness"] == "HOLD"),
        "blockers": blockers,
        "safety": {
            "shortsCtaMustRemainQuiz": True,
            "emptyDataFailClosed": all(row["readiness"] == "HOLD" for row in rows) if blockers else False,
            "doNotClaim": ["診斷", "療效", "保證修復", "必須購買"],
        },
    }


def render_markdown(board: dict) -> str:
    lines = [
        "# LoveTypes 商品假設板",
        "",
        f"- 產生日期：{board['generatedAt']}",
        f"- PASS 列數：{board['readyRows']}",
        f"- HOLD 列數：{board['holdRows']}",
        "",
        "## 阻擋條件",
        "",
    ]
    lines.extend(f"- {item}" for item in board["blockers"]) if board["blockers"] else lines.append("- 無")
    lines.extend(["", "## 守護者商品假設", ""])
    for row in board["rows"]:
        lines.extend([
            f"### {row['guardianName']}（{row['guardianId']}）",
            "",
            f"- 階段：`{row['stage']}`",
            f"- Readiness：{row['readiness']}",
            f"- 商品假設：{row['offerHypothesis']}",
            f"- 免費資產：`{row['freeAsset']['id']}` -> {row['freeAsset']['targetUrl']}",
            f"- 名單資產：`{row['ownedAsset']['id']}` -> {row['ownedAsset']['targetUrl']}（模板 {row['ownedAsset']['intakeTemplates']}）",
            f"- Luna 測試：`{row['lunaTest']['id']}` -> {row['lunaTest']['targetUrl']}",
            f"- 聯盟測試：`{row['affiliateTest']['id']}` -> {row['affiliateTest']['targetUrl']}",
            f"- 下一步驗證：{row['nextValidation']}",
            f"- 目標入口：{row['targetUrl']}",
            "",
        ])
    lines.extend([
        "## 安全邊界",
        "",
        "- Shorts CTA 維持測驗，不直接導購。",
        "- 只有結果後路線、旅人補給、Luna 或 Contact 承接可測試商品假設。",
        "- 不使用診斷、療效、保證修復或必須購買說法。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(board: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(board), encoding="utf-8")
    json_output.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in board["rows"]:
            writer.writerow({
                "guardian_id": row["guardianId"],
                "guardian_name": row["guardianName"],
                "stage": row["stage"],
                "offer_hypothesis": row["offerHypothesis"],
                "free_asset": row["freeAsset"]["id"],
                "owned_asset": row["ownedAsset"]["id"],
                "luna_test": row["lunaTest"]["id"],
                "affiliate_test": row["affiliateTest"]["id"],
                "readiness": row["readiness"],
                "next_validation": row["nextValidation"],
                "target_url": row["targetUrl"],
                "safety_boundary": row["safetyBoundary"],
            })


def validate_board(board: dict) -> list[str]:
    issues: list[str] = []
    rows = board.get("rows", [])
    expected_rows = int(board.get("expectedRowCount", 0) or 0)
    if len(rows) != expected_rows:
        issues.append(f"expected {expected_rows} guardian offer hypothesis rows, got {len(rows)}")
    if any(row.get("readiness") not in {"PASS", "HOLD"} for row in rows):
        issues.append("readiness must be PASS or HOLD")
    if board.get("blockers") and any(row.get("readiness") == "PASS" for row in rows):
        issues.append("blocked gate must not pass offer rows")
    for row in rows:
        guardian = row.get("guardianId", "<unknown>")
        if not row.get("offerHypothesis") or not row.get("nextValidation") or not row.get("targetUrl"):
            issues.append(f"{guardian}: missing hypothesis, validation, or target")
        if not row.get("ownedAsset", {}).get("leadItemId"):
            issues.append(f"{guardian}: missing owned lead item id")
        expected_intake_templates = int(board.get("expectedIntakeTemplatesPerGuardian", 0) or 0)
        if row.get("ownedAsset", {}).get("intakeTemplates") != expected_intake_templates:
            issues.append(f"{guardian}: expected {expected_intake_templates} intake templates")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes monetization offer hypothesis board.")
    parser.add_argument("--matrix", default=str(MATRIX_PATH))
    parser.add_argument("--gate", default=str(GATE_PATH))
    parser.add_argument("--lead-intake", default=str(LEAD_INTAKE_PATH))
    parser.add_argument("--backlog", default=str(BACKLOG_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    board = build_board(load_json(Path(args.matrix)), load_json(Path(args.gate)), load_json(Path(args.lead_intake)), load_json(Path(args.backlog)))
    issues = validate_board(board)
    if not args.check:
        write_outputs(board, Path(args.output), Path(args.json_output), Path(args.csv_output))
        print(f"promotion_offer_hypothesis_board={args.output}")
        print(f"promotion_offer_hypothesis_json={args.json_output}")
        print(f"promotion_offer_hypothesis_csv={args.csv_output}")
    print(f"promotion_offer_hypothesis_rows={len(board['rows'])}")
    print(f"promotion_offer_hypothesis_ready={board['readyRows']}")
    print(f"promotion_offer_hypothesis_hold={board['holdRows']}")
    print(f"promotion_offer_hypothesis_blockers={len(board['blockers'])}")
    print(f"promotion_offer_hypothesis_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
