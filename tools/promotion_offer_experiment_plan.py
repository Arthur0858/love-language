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
OFFER_BOARD_PATH = PROMOTION_DIR / "offer-hypothesis-board.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "offer-experiment-plan.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "offer-experiment-plan.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "offer-experiment-plan.csv"
EXPERIMENTS = [
    {
        "experimentType": "identity_save",
        "assetColumn": "freeAsset",
        "hypothesis": "免費收藏物能提高守護者認同、保存與回訪。",
        "primaryMetric": "free_keepsake_downloads",
        "secondaryMetric": "keepsake_clicks",
        "minimumSignal": 2,
        "minimumQuizCompletions": 10,
        "nextAction": "製作或升級故事卡、PDF 練習卡或手機桌布。",
    },
    {
        "experimentType": "owned_lead",
        "assetColumn": "ownedAsset",
        "hypothesis": "重複補給或 Contact 需求可轉成自有 Email 素材。",
        "primaryMetric": "supply_lead_requests",
        "secondaryMetric": "contact_requests",
        "minimumSignal": 2,
        "minimumQuizCompletions": 10,
        "nextAction": "製作最小 PDF、短儀式或等待清單回覆模板。",
    },
    {
        "experimentType": "luna_soft_offer",
        "assetColumn": "lunaTest",
        "hypothesis": "Luna 使用場景可在結果後路線承接夜間整理需求。",
        "primaryMetric": "luna_pack_clicks",
        "secondaryMetric": "luna_clicks",
        "minimumSignal": 1,
        "minimumQuizCompletions": 10,
        "nextAction": "只在結果後路線測試 Luna starter，不把 Shorts CTA 改成購買。",
    },
    {
        "experimentType": "affiliate_book",
        "assetColumn": "affiliateTest",
        "hypothesis": "延伸書卷可承接願意深讀的使用者，但不應取代免費路線。",
        "primaryMetric": "affiliate_book_clicks",
        "secondaryMetric": "resources_clicks",
        "minimumSignal": 2,
        "minimumQuizCompletions": 10,
        "nextAction": "在旅人補給路線調整書卷排序與說明，不放回首頁全域導購。",
    },
]
CSV_FIELDS = [
    "experiment_id",
    "guardian_id",
    "guardian_name",
    "experiment_type",
    "status",
    "hypothesis",
    "primary_metric",
    "primary_value",
    "secondary_metric",
    "secondary_value",
    "minimum_signal",
    "minimum_quiz_completions",
    "quiz_completions",
    "asset_id",
    "target_url",
    "next_action",
    "safety_boundary",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def board_by_guardian(board: dict) -> dict[str, dict]:
    return {str(row.get("guardianId", "")): row for row in board.get("rows", [])}


def matrix_by_guardian(matrix: dict) -> dict[str, dict]:
    return {str(row.get("guardianId", "")): row for row in matrix.get("guardians", [])}


def metric_value(metrics: dict, field: str) -> int:
    value = metrics.get(field, 0)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def experiment_status(blocked: bool, metrics: dict, spec: dict) -> str:
    if blocked:
        return "HOLD"
    quiz = metric_value(metrics, "quiz_completions")
    primary = metric_value(metrics, spec["primaryMetric"])
    secondary = metric_value(metrics, spec["secondaryMetric"])
    if quiz < int(spec["minimumQuizCompletions"]):
        return "HOLD"
    if primary + secondary < int(spec["minimumSignal"]):
        return "HOLD"
    return "READY"


def asset_payload(board_row: dict, spec: dict) -> tuple[str, str]:
    asset = board_row.get(spec["assetColumn"], {}) if isinstance(board_row.get(spec["assetColumn"]), dict) else {}
    return str(asset.get("id") or ""), str(asset.get("targetUrl") or "")


def build_plan(matrix: dict, gate: dict, offer_board: dict) -> dict:
    blocked = bool(gate.get("blockers")) or bool(gate.get("safety", {}).get("emptyDataFailClosed"))
    board_rows = board_by_guardian(offer_board)
    matrix_rows = matrix_by_guardian(matrix)
    rows = []
    for guardian_id, matrix_row in matrix_rows.items():
        board_row = board_rows.get(guardian_id, {})
        metrics = matrix_row.get("metrics", {}) if isinstance(matrix_row.get("metrics"), dict) else {}
        for spec in EXPERIMENTS:
            asset_id, target_url = asset_payload(board_row, spec)
            status = experiment_status(blocked, metrics, spec)
            rows.append({
                "experimentId": f"{guardian_id}-{spec['experimentType']}",
                "guardianId": guardian_id,
                "guardianName": matrix_row.get("guardianName", guardian_id),
                "stage": matrix_row.get("stage", "collect_signal"),
                "experimentType": spec["experimentType"],
                "status": status,
                "hypothesis": spec["hypothesis"],
                "primaryMetric": spec["primaryMetric"],
                "primaryValue": metric_value(metrics, spec["primaryMetric"]),
                "secondaryMetric": spec["secondaryMetric"],
                "secondaryValue": metric_value(metrics, spec["secondaryMetric"]),
                "minimumSignal": spec["minimumSignal"],
                "minimumQuizCompletions": spec["minimumQuizCompletions"],
                "quizCompletions": metric_value(metrics, "quiz_completions"),
                "assetId": asset_id,
                "targetUrl": target_url,
                "nextAction": spec["nextAction"] if status == "READY" else "先發布與回填 KPI；未達門檻前不製作或加強此商品假設。",
                "safetyBoundary": "只在結果後、旅人補給、Luna 或 Contact 路線測試；不診斷、不承諾療效、不要求購買。",
            })
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "revenueDecisionMatrix": str(MATRIX_PATH.relative_to(ROOT)),
            "weekDecisionGate": str(GATE_PATH.relative_to(ROOT)),
            "offerHypothesisBoard": str(OFFER_BOARD_PATH.relative_to(ROOT)),
        },
        "experiments": rows,
        "readyExperiments": sum(1 for row in rows if row["status"] == "READY"),
        "holdExperiments": sum(1 for row in rows if row["status"] == "HOLD"),
        "blockers": list(gate.get("blockers", [])),
        "thresholds": EXPERIMENTS,
        "safety": {
            "emptyDataFailClosed": blocked,
            "shortsCtaMustRemainQuiz": True,
            "doNotClaim": ["診斷", "療效", "保證修復", "必須購買"],
        },
    }


def render_markdown(plan: dict) -> str:
    lines = [
        "# LoveTypes 商品實驗計畫",
        "",
        f"- 產生日期：{plan['generatedAt']}",
        f"- READY 實驗：{plan['readyExperiments']}",
        f"- HOLD 實驗：{plan['holdExperiments']}",
        "",
        "## 門檻規則",
        "",
    ]
    for spec in plan["thresholds"]:
        lines.append(
            f"- `{spec['experimentType']}`: 測驗完成 >= {spec['minimumQuizCompletions']}，"
            f"`{spec['primaryMetric']}` + `{spec['secondaryMetric']}` >= {spec['minimumSignal']}。"
        )
    lines.extend(["", "## 阻擋條件", ""])
    lines.extend(f"- {item}" for item in plan["blockers"]) if plan["blockers"] else lines.append("- 無")
    lines.extend(["", "## 實驗列表", ""])
    for row in plan["experiments"]:
        lines.extend([
            f"### {row['guardianName']} / {row['experimentType']}",
            "",
            f"- 狀態：{row['status']}",
            f"- 假設：{row['hypothesis']}",
            f"- 目前數據：quiz={row['quizCompletions']}，{row['primaryMetric']}={row['primaryValue']}，{row['secondaryMetric']}={row['secondaryValue']}",
            f"- 資產：`{row['assetId']}` -> {row['targetUrl']}",
            f"- 下一步：{row['nextAction']}",
            "",
        ])
    lines.extend([
        "## 安全邊界",
        "",
        "- 未達 READY 前，不新增或加重付費 CTA。",
        "- Shorts CTA 維持測驗完成，不直接導購。",
        "- 商品實驗只放在結果後路線、旅人補給、Luna 或 Contact 承接。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(plan: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(plan), encoding="utf-8")
    json_output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in plan["experiments"]:
            writer.writerow({
                "experiment_id": row["experimentId"],
                "guardian_id": row["guardianId"],
                "guardian_name": row["guardianName"],
                "experiment_type": row["experimentType"],
                "status": row["status"],
                "hypothesis": row["hypothesis"],
                "primary_metric": row["primaryMetric"],
                "primary_value": row["primaryValue"],
                "secondary_metric": row["secondaryMetric"],
                "secondary_value": row["secondaryValue"],
                "minimum_signal": row["minimumSignal"],
                "minimum_quiz_completions": row["minimumQuizCompletions"],
                "quiz_completions": row["quizCompletions"],
                "asset_id": row["assetId"],
                "target_url": row["targetUrl"],
                "next_action": row["nextAction"],
                "safety_boundary": row["safetyBoundary"],
            })


def validate_plan(plan: dict) -> list[str]:
    issues: list[str] = []
    experiments = plan.get("experiments", [])
    if len(experiments) != 20:
        issues.append("expected 20 guardian offer experiments")
    if any(row.get("status") not in {"READY", "HOLD"} for row in experiments):
        issues.append("experiment status must be READY or HOLD")
    if plan.get("blockers") and any(row.get("status") == "READY" for row in experiments):
        issues.append("blocked weekly gate must hold every experiment")
    for row in experiments:
        if not row.get("assetId") or not row.get("targetUrl"):
            issues.append(f"{row.get('experimentId', '<unknown>')}: missing asset or target")
        if int(row.get("minimumQuizCompletions", 0)) < 1 or int(row.get("minimumSignal", 0)) < 1:
            issues.append(f"{row.get('experimentId', '<unknown>')}: invalid thresholds")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes offer experiment plan with guarded KPI thresholds.")
    parser.add_argument("--matrix", default=str(MATRIX_PATH))
    parser.add_argument("--gate", default=str(GATE_PATH))
    parser.add_argument("--offer-board", default=str(OFFER_BOARD_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    plan = build_plan(load_json(Path(args.matrix)), load_json(Path(args.gate)), load_json(Path(args.offer_board)))
    issues = validate_plan(plan)
    if not args.check:
        write_outputs(plan, Path(args.output), Path(args.json_output), Path(args.csv_output))
        print(f"promotion_offer_experiment_plan={args.output}")
        print(f"promotion_offer_experiment_json={args.json_output}")
        print(f"promotion_offer_experiment_csv={args.csv_output}")
    print(f"promotion_offer_experiment_rows={len(plan['experiments'])}")
    print(f"promotion_offer_experiment_ready={plan['readyExperiments']}")
    print(f"promotion_offer_experiment_hold={plan['holdExperiments']}")
    print(f"promotion_offer_experiment_blockers={len(plan['blockers'])}")
    print(f"promotion_offer_experiment_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
