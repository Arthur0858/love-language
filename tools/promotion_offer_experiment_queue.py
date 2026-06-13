#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PLAN_PATH = PROMOTION_DIR / "offer-experiment-plan.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "offer-experiment-queue.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "offer-experiment-queue.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "offer-experiment-queue.csv"
CSV_FIELDS = [
    "queue_id",
    "experiment_id",
    "guardian_id",
    "guardian_name",
    "experiment_type",
    "status",
    "step",
    "deliverable",
    "asset_id",
    "target_url",
    "owner",
    "acceptance_check",
    "writeback",
    "safety_boundary",
]
STEPS = [
    {
        "step": "brief",
        "deliverable": "Write a one-page asset brief with guardian, scene, promise boundary, and CTA.",
        "owner": "content",
        "acceptanceCheck": "Brief keeps the Shorts CTA as quiz and places offer only after result route.",
        "writeback": "Update offer-experiment-plan after KPI review.",
    },
    {
        "step": "asset",
        "deliverable": "Produce the smallest useful asset or route copy for the experiment.",
        "owner": "creative",
        "acceptanceCheck": "Asset links to the existing target URL and does not claim diagnosis or therapeutic outcome.",
        "writeback": "Record fulfillment asset in lead-intake-tracker.csv when a real request exists.",
    },
    {
        "step": "qa",
        "deliverable": "Check safety copy, route, tracking event, and mobile presentation before publish.",
        "owner": "ops",
        "acceptanceCheck": "Public smoke remains clean and no paid CTA is added before the experiment is READY.",
        "writeback": "Run predeploy_check.py before deploy.",
    },
    {
        "step": "measure",
        "deliverable": "After the test window, backfill KPI fields and decide continue, revise, or stop.",
        "owner": "ops",
        "acceptanceCheck": "KPI row includes primary and secondary metric fields for the experiment.",
        "writeback": "Update kpi-tracker.csv, weekly-summary, decision gate, offer board, and experiment plan.",
    },
]
QUEUE_STATUSES = ("ready", "waiting_for_signal", "blocked_by_gate")


def queue_policy() -> dict[str, object]:
    return {
        "stepOrder": [step["step"] for step in STEPS],
        "stepCount": len(STEPS),
        "statuses": list(QUEUE_STATUSES),
        "blockedStatus": "blocked_by_gate",
        "readyStatus": "ready",
        "waitingStatus": "waiting_for_signal",
        "blockedGateReadyRowsMustBeZero": True,
        "rule": "只有 offer experiment plan 無 blocker 且實驗列為 READY 時，queue row 才可進入 ready；其餘維持 waiting 或 blocked。",
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def row_status(experiment: dict, blockers: list[str]) -> str:
    if blockers:
        return queue_policy()["blockedStatus"]
    if experiment.get("status") == "READY":
        return queue_policy()["readyStatus"]
    return queue_policy()["waitingStatus"]


def build_queue(plan: dict) -> dict:
    blockers = list(plan.get("blockers", []))
    rows = []
    for experiment in plan.get("experiments", []):
        status = row_status(experiment, blockers)
        for step in STEPS:
            rows.append({
                "queueId": f"{experiment['experimentId']}-{step['step']}",
                "experimentId": experiment["experimentId"],
                "guardianId": experiment["guardianId"],
                "guardianName": experiment["guardianName"],
                "experimentType": experiment["experimentType"],
                "status": status,
                "step": step["step"],
                "deliverable": step["deliverable"],
                "assetId": experiment["assetId"],
                "targetUrl": experiment["targetUrl"],
                "owner": step["owner"],
                "acceptanceCheck": step["acceptanceCheck"],
                "writeback": step["writeback"],
                "safetyBoundary": experiment["safetyBoundary"],
            })
    return {
        "generatedAt": date.today().isoformat(),
        "source": {"offerExperimentPlan": str(PLAN_PATH.relative_to(ROOT))},
        "queuePolicy": queue_policy(),
        "queueRows": rows,
        "experimentCount": len(plan.get("experiments", [])),
        "stepCount": len(STEPS),
        "expectedQueueRows": len(plan.get("experiments", [])) * len(STEPS),
        "readyRows": sum(1 for row in rows if row["status"] == "ready"),
        "waitingRows": sum(1 for row in rows if row["status"] == "waiting_for_signal"),
        "blockedRows": sum(1 for row in rows if row["status"] == "blocked_by_gate"),
        "blockers": blockers,
        "safety": {
            "noPaidCtaBeforeReady": True,
            "shortsCtaMustRemainQuiz": True,
            "doNotClaim": ["診斷", "療效", "保證修復", "必須購買"],
        },
    }


def render_markdown(queue: dict) -> str:
    policy = queue["queuePolicy"]
    lines = [
        "# LoveTypes 商品實驗執行佇列",
        "",
        f"- 產生日期：{queue['generatedAt']}",
        f"- ready rows：{queue['readyRows']}",
        f"- waiting rows：{queue['waitingRows']}",
        f"- blocked rows：{queue['blockedRows']}",
        f"- 規則：{policy['rule']}",
        f"- 步驟：{', '.join(policy['stepOrder'])}",
        "",
        "## 阻擋條件",
        "",
    ]
    lines.extend(f"- {item}" for item in queue["blockers"]) if queue["blockers"] else lines.append("- 無")
    lines.extend(["", "## 執行佇列", ""])
    for row in queue["queueRows"]:
        lines.extend([
            f"### {row['queueId']}",
            "",
            f"- 狀態：{row['status']}",
            f"- 守護者：{row['guardianName']}（{row['guardianId']}）",
            f"- 實驗：{row['experimentType']}",
            f"- 步驟：{row['step']} / owner: {row['owner']}",
            f"- 交付物：{row['deliverable']}",
            f"- 驗收：{row['acceptanceCheck']}",
            f"- 回填：{row['writeback']}",
            f"- 資產：`{row['assetId']}` -> {row['targetUrl']}",
            "",
        ])
    lines.extend([
        "## 安全邊界",
        "",
        "- 未達 READY 前，不新增或加重付費 CTA。",
        "- 每個實驗都必須保留測驗作為 Shorts 主 CTA。",
        "- 商品或聯盟只放在結果後路線、旅人補給、Luna 或 Contact 承接。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(queue: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(queue), encoding="utf-8")
    json_output.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in queue["queueRows"]:
            writer.writerow({
                "queue_id": row["queueId"],
                "experiment_id": row["experimentId"],
                "guardian_id": row["guardianId"],
                "guardian_name": row["guardianName"],
                "experiment_type": row["experimentType"],
                "status": row["status"],
                "step": row["step"],
                "deliverable": row["deliverable"],
                "asset_id": row["assetId"],
                "target_url": row["targetUrl"],
                "owner": row["owner"],
                "acceptance_check": row["acceptanceCheck"],
                "writeback": row["writeback"],
                "safety_boundary": row["safetyBoundary"],
            })


def validate_queue(queue: dict) -> list[str]:
    issues: list[str] = []
    rows = queue.get("queueRows", [])
    policy = queue.get("queuePolicy", {})
    expected_rows = int(queue.get("expectedQueueRows", 0) or 0)
    valid_statuses = set(policy.get("statuses", [])) if isinstance(policy, dict) else set()
    expected_step_count = int(policy.get("stepCount", 0) or 0) if isinstance(policy, dict) else 0
    if expected_step_count != len(STEPS) or valid_statuses != set(QUEUE_STATUSES):
        issues.append("queue policy does not match configured steps or statuses")
    if len(rows) != expected_rows:
        issues.append(f"expected {expected_rows} experiment queue rows, got {len(rows)}")
    if policy.get("blockedGateReadyRowsMustBeZero") and queue.get("blockers") and queue.get("readyRows", 0) != 0:
        issues.append("blocked gate must not expose ready experiment queue rows")
    for row in rows:
        if row.get("status") not in valid_statuses:
            issues.append(f"{row.get('queueId', '<unknown>')}: invalid status")
        if not row.get("assetId") or not row.get("targetUrl") or not row.get("acceptanceCheck"):
            issues.append(f"{row.get('queueId', '<unknown>')}: missing asset, target, or acceptance check")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes offer experiment execution queue.")
    parser.add_argument("--plan", default=str(PLAN_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    queue = build_queue(load_json(Path(args.plan)))
    issues = validate_queue(queue)
    if not args.check:
        write_outputs(queue, Path(args.output), Path(args.json_output), Path(args.csv_output))
        print(f"promotion_offer_experiment_queue={args.output}")
        print(f"promotion_offer_experiment_queue_json={args.json_output}")
        print(f"promotion_offer_experiment_queue_csv={args.csv_output}")
    print(f"promotion_offer_experiment_queue_rows={len(queue['queueRows'])}")
    print(f"promotion_offer_experiment_queue_ready={queue['readyRows']}")
    print(f"promotion_offer_experiment_queue_waiting={queue['waitingRows']}")
    print(f"promotion_offer_experiment_queue_blocked={queue['blockedRows']}")
    print(f"promotion_offer_experiment_queue_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
