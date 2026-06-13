#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
FIRST_BATCH_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
KPI_CHECKLIST_PATH = PROMOTION_DIR / "first-batch-kpi-checklist.json"
ZERO_EVIDENCE_PATH = PROMOTION_DIR / "zero-kpi-evidence-checklist.json"
PUBLISH_ACTION_PATH = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-kpi-action-sheet.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "first-batch-kpi-action-sheet.csv"

MINIMUM_KPIS = ("site_clicks", "quiz_starts", "quiz_completions")
FIELDNAMES = [
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "action_status",
    "published",
    "post_url",
    "minimum_kpis",
    "zero_source_rows",
    "proof_note_template",
    "kpi_command",
    "blocked_by",
]


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def kpi_rows_by_task(kpi: dict) -> dict[tuple[str, str], list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in kpi.get("items", []):
        grouped.setdefault((str(row.get("platform", "")), str(row.get("task_id", ""))), []).append(row)
    return grouped


def zero_rows_by_task(zero: dict) -> dict[tuple[str, str], list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in zero.get("items", []):
        grouped.setdefault((str(row.get("platform", "")), str(row.get("task_id", ""))), []).append(row)
    return grouped


def build_rows() -> tuple[list[dict[str, str]], dict[str, int], list[str]]:
    first_batch = read_json(FIRST_BATCH_PATH)
    kpi_checklist = read_json(KPI_CHECKLIST_PATH)
    zero_evidence = read_json(ZERO_EVIDENCE_PATH)
    publish_action = read_json(PUBLISH_ACTION_PATH)
    kpi_by_task = kpi_rows_by_task(kpi_checklist)
    zero_by_task = zero_rows_by_task(zero_evidence)
    publish_ready = int(publish_action.get("metrics", {}).get("ready", 0) or 0)
    issues: list[str] = []
    rows: list[dict[str, str]] = []

    for item in first_batch.get("rows", []):
        platform = str(item.get("platform", ""))
        task_id = str(item.get("taskId", ""))
        task_key = (platform, task_id)
        kpi_rows = kpi_by_task.get(task_key, [])
        zero_rows = zero_by_task.get(task_key, [])
        published = bool(item.get("published"))
        post_url = str(item.get("postUrl", ""))
        if published:
            action_status = "ready_for_kpi_source_check"
            blocked_by = ""
        else:
            action_status = "blocked_until_public_post_url"
            blocked_by = "first-batch post is not published"
        rows.append({
            "platform": platform,
            "task_id": task_id,
            "script_id": str(item.get("scriptId", "")),
            "guardian_id": str(item.get("guardianId", "")),
            "action_status": action_status,
            "published": "1" if published else "0",
            "post_url": post_url,
            "minimum_kpis": ",".join(MINIMUM_KPIS),
            "zero_source_rows": str(sum(1 for row in zero_rows if row.get("metric_id") in MINIMUM_KPIS)),
            "proof_note_template": f"platform analytics checked {today()} for {platform}/{task_id}",
            "kpi_command": str(item.get("kpiExampleCommand", "")),
            "blocked_by": blocked_by,
        })

        if len(kpi_rows) != 7:
            issues.append(f"{platform}/{task_id}: expected 7 KPI checklist rows")
        if len(zero_rows) != 3:
            issues.append(f"{platform}/{task_id}: expected 3 zero KPI evidence rows")

    if len(rows) != 3:
        issues.append(f"expected 3 first-batch KPI action rows, got {len(rows)}")
    for row in rows:
        label = f"{row['platform']}/{row['task_id']}"
        if row["published"] == "0" and row["action_status"] != "blocked_until_public_post_url":
            issues.append(f"{label}: unpublished rows must stay blocked")
        if row["published"] == "1" and not row["post_url"].startswith("https://"):
            issues.append(f"{label}: published rows require real HTTPS post_url")
        if "<REAL_" in row["kpi_command"]:
            # Expected while blocked; once published, the generated packet should have a real URL.
            if row["published"] == "1":
                issues.append(f"{label}: published KPI command still contains placeholder post URL")
        if "site-clicks" not in row["kpi_command"] or "quiz-starts" not in row["kpi_command"] or "quiz-completions" not in row["kpi_command"]:
            issues.append(f"{label}: KPI command should include minimum KPI flags")
    metrics = {
        "rows": len(rows),
        "ready": sum(1 for row in rows if row["action_status"] == "ready_for_kpi_source_check"),
        "blocked": sum(1 for row in rows if row["action_status"].startswith("blocked")),
        "published": sum(1 for row in rows if row["published"] == "1"),
        "zeroSourceRows": sum(int(row["zero_source_rows"]) for row in rows),
        "publishActionReady": publish_ready,
    }
    return rows, metrics, issues


def render_markdown(payload: dict) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes First Batch KPI Action Sheet",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready：{metrics['ready']}",
        f"- blocked：{metrics['blocked']}",
        f"- published：{metrics['published']}",
        f"- zero source rows：{metrics['zeroSourceRows']}",
        f"- publish action ready：{metrics['publishActionReady']}",
        f"- issues：{len(payload['issues'])}",
        "",
        "## Rule",
        "",
        "- 沒有真實公開 post URL 前，不回填 KPI，也不把 0 視為有效數據。",
        "- `site_clicks`、`quiz_starts`、`quiz_completions` 即使是 0，也必須有平台或網站來源確認。",
        "- 三平台最小 KPI 未回填前，不做週決策、商品化、Luna 或聯盟權重調整。",
        "",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"## {row['platform']} · `{row['task_id']}`",
            "",
            f"- action status：`{row['action_status']}`",
            f"- published：`{row['published']}`",
            f"- post URL：{row['post_url'] or '(not published)'}",
            f"- minimum KPI：`{row['minimum_kpis']}`",
            f"- zero-source rows：{row['zero_source_rows']}",
            f"- proof note：`{row['proof_note_template']}`",
            f"- KPI writeback：`{row['kpi_command']}`",
        ])
        if row["blocked_by"]:
            lines.append(f"- blocked by：{row['blocked_by']}")
        lines.append("")
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
        lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the first-batch KPI action sheet after publishing.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    rows, metrics, issues = build_rows()
    print(f"promotion_first_batch_kpi_action_rows={metrics['rows']}")
    print(f"promotion_first_batch_kpi_action_ready={metrics['ready']}")
    print(f"promotion_first_batch_kpi_action_blocked={metrics['blocked']}")
    print(f"promotion_first_batch_kpi_action_published={metrics['published']}")
    print(f"promotion_first_batch_kpi_action_zero_source_rows={metrics['zeroSourceRows']}")
    print(f"promotion_first_batch_kpi_action_publish_ready={metrics['publishActionReady']}")
    print(f"promotion_first_batch_kpi_action_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1

    if not args.check:
        payload = {
            "generatedAt": today(),
            "sources": {
                "firstBatchPublicationPacket": str(FIRST_BATCH_PATH.relative_to(ROOT)),
                "firstBatchKpiChecklist": str(KPI_CHECKLIST_PATH.relative_to(ROOT)),
                "zeroKpiEvidence": str(ZERO_EVIDENCE_PATH.relative_to(ROOT)),
                "firstBatchPublishAction": str(PUBLISH_ACTION_PATH.relative_to(ROOT)),
            },
            "metrics": metrics,
            "rows": rows,
            "issues": issues,
        }
        md_output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        md_output.write_text(render_markdown(payload), encoding="utf-8")
        json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, rows)
        print(f"promotion_first_batch_kpi_action_md={md_output.relative_to(ROOT)}")
        print(f"promotion_first_batch_kpi_action_json={json_output.relative_to(ROOT)}")
        print(f"promotion_first_batch_kpi_action_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
