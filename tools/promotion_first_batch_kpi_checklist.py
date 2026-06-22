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
PROOF_TEMPLATES_PATH = PROMOTION_DIR / "operation-proof-templates.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "first-batch-kpi-checklist.csv"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-kpi-checklist.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-kpi-checklist.md"

FIELDNAMES = [
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "metric_id",
    "required_for_weekly_review",
    "expected_value",
    "allowed_empty",
    "zero_requires_source_check",
    "source_to_check",
    "proof_file",
    "check_command",
    "write_command",
    "evidence_value",
    "operator_status",
    "notes",
]

KPI_ROWS = [
    {
        "metric_id": "post_url",
        "required": "1",
        "expected": "Real public HTTPS post URL from the platform.",
        "allowed_empty": "0",
        "zero_requires_source_check": "0",
        "source": "Published platform post page.",
    },
    {
        "metric_id": "published_date",
        "required": "1",
        "expected": "YYYY-MM-DD date when the platform post became public.",
        "allowed_empty": "0",
        "zero_requires_source_check": "0",
        "source": "Platform post timestamp or publishing dashboard.",
    },
    {
        "metric_id": "proof_note",
        "required": "1",
        "expected": "Traceable analytics proof such as screenshot filename, platform analytics URL, report export, platform timestamp, or checked source note.",
        "allowed_empty": "0",
        "zero_requires_source_check": "0",
        "source": "Public URL check, screenshot, or platform dashboard.",
    },
    {
        "metric_id": "site_clicks",
        "required": "1",
        "expected": "Number of visits/clicks from this platform post or verified 0.",
        "allowed_empty": "0",
        "zero_requires_source_check": "1",
        "source": "Cloudflare/Web analytics, platform link analytics, or tracked UTM report.",
    },
    {
        "metric_id": "quiz_starts",
        "required": "1",
        "expected": "Number of quiz starts attributed to this post or verified 0.",
        "allowed_empty": "0",
        "zero_requires_source_check": "1",
        "source": "Funnel event catalog/report, analytics event export, or manual verified source.",
    },
    {
        "metric_id": "quiz_completions",
        "required": "1",
        "expected": "Number of quiz completions attributed to this post or verified 0.",
        "allowed_empty": "0",
        "zero_requires_source_check": "1",
        "source": "Funnel event catalog/report, analytics event export, or manual verified source.",
    },
    {
        "metric_id": "source_checked",
        "required": "1",
        "expected": "Name/date of the source checked before accepting metrics, especially zeros.",
        "allowed_empty": "0",
        "zero_requires_source_check": "0",
        "source": "Operator note from the platform or analytics source check.",
    },
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def post_proof_rows() -> dict[tuple[str, str], dict]:
    data = read_json(PROOF_TEMPLATES_PATH)
    rows = {}
    for row in data.get("rows", []):
        if row.get("kind") == "post_publish":
            rows[(str(row.get("platform", "")), str(row.get("taskId", "")))] = row
    return rows


def build_rows() -> list[dict[str, str]]:
    first_batch = read_json(FIRST_BATCH_PATH)
    proof_rows = post_proof_rows()
    rows: list[dict[str, str]] = []
    for item in first_batch.get("rows", []):
        platform = str(item.get("platform", ""))
        task_id = str(item.get("taskId", ""))
        proof = proof_rows.get((platform, task_id), {})
        proof_path = str(proof.get("path") or f"docs/promotion/first-round/proof-{platform}-{task_id}.txt")
        for metric in KPI_ROWS:
            rows.append({
                "platform": platform,
                "task_id": task_id,
                "script_id": str(item.get("scriptId", "")),
                "guardian_id": str(item.get("guardianId", "")),
                "metric_id": metric["metric_id"],
                "required_for_weekly_review": metric["required"],
                "expected_value": metric["expected"],
                "allowed_empty": metric["allowed_empty"],
                "zero_requires_source_check": metric["zero_requires_source_check"],
                "source_to_check": metric["source"],
                "proof_file": proof_path,
                "check_command": str(proof.get("checkCommand") or f"python3 tools/promotion_post_text_import.py check --input {proof_path}"),
                "write_command": str(proof.get("writeCommand") or f"python3 tools/promotion_post_text_import.py add --input {proof_path} --proof-note \"<REAL_ANALYTICS_SOURCE_PROOF_NOTE> verified\""),
                "evidence_value": "",
                "operator_status": "pending",
                "notes": f"utm_content={item.get('utmContent', '')}; tracked_url={item.get('trackedUrl', '')}",
            })
    return rows


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    expected_metrics = {row["metric_id"] for row in KPI_ROWS}
    tasks = {(row["platform"], row["task_id"]) for row in rows}
    expected_row_count = len(tasks) * len(KPI_ROWS)
    if len(rows) != expected_row_count:
        issues.append(f"expected {expected_row_count} first-batch KPI checklist rows, got {len(rows)}")
    if not tasks:
        issues.append("expected at least 1 first-batch task")
    for platform, task_id in sorted(tasks):
        task_rows = [row for row in rows if row["platform"] == platform and row["task_id"] == task_id]
        metrics = {row["metric_id"] for row in task_rows}
        if metrics != expected_metrics:
            issues.append(f"{platform}/{task_id}: KPI checklist metrics mismatch")
    for row in rows:
        label = f"{row['platform']}/{row['task_id']}/{row['metric_id']}"
        if row["operator_status"] != "pending":
            issues.append(f"{label}: generated rows should start pending")
        if row["required_for_weekly_review"] != "1":
            issues.append(f"{label}: first-batch minimum KPI rows should be required")
        if row["allowed_empty"] != "0":
            issues.append(f"{label}: minimum KPI row should not allow empty values")
        if row["metric_id"] in {"site_clicks", "quiz_starts", "quiz_completions"} and row["zero_requires_source_check"] != "1":
            issues.append(f"{label}: zero metrics should require source check")
        if not row["proof_file"].endswith(f"proof-{row['platform']}-{row['task_id']}.txt"):
            issues.append(f"{label}: proof_file should point to platform post proof template")
        if "promotion_post_text_import.py check" not in row["check_command"]:
            issues.append(f"{label}: missing post text import check command")
        if "promotion_post_text_import.py add" not in row["write_command"]:
            issues.append(f"{label}: missing post text import write command")
    return issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes First Batch KPI Checklist",
        "",
        f"- Generated: `{payload['generatedAt']}`",
        f"- Tasks: `{payload['tasks']}`",
        f"- KPI rows: `{payload['rows']}`",
        f"- Zero-source-check rows: `{payload['zeroSourceCheckRows']}`",
        f"- Pending rows: `{payload['pendingRows']}`",
        f"- Issues: `{len(payload['issues'])}`",
        "",
        "## Rule",
        "",
        "- Do not run weekly review until every first-batch post has post_url, site_clicks, quiz_starts, and quiz_completions.",
        "- A zero value is acceptable only after the named source was checked.",
        "- Keep product, Luna, affiliate, and guardian-priority decisions blocked while these rows are empty.",
        "",
    ]
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in payload["items"]:
        grouped.setdefault((row["platform"], row["task_id"]), []).append(row)
    for (platform, task_id), rows in grouped.items():
        lines.extend([
            f"## {platform} · `{task_id}`",
            "",
            f"- Script: `{rows[0]['script_id']}`",
            f"- Guardian: `{rows[0]['guardian_id']}`",
            f"- Proof file: `{rows[0]['proof_file']}`",
            f"- Check: `{rows[0]['check_command']}`",
            f"- Write: `{rows[0]['write_command']}`",
            "",
        ])
        for row in rows:
            suffix = " Zero requires source check." if row["zero_requires_source_check"] == "1" else ""
            source = str(row["source_to_check"]).rstrip(".")
            lines.append(f"- [ ] `{row['metric_id']}`：{row['expected_value']} Source: {source}.{suffix}")
        lines.append("")
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the minimum KPI checklist required after the first LoveTypes publishing batch.")
    parser.add_argument("--check", action="store_true", help="Validate current generated rows without writing outputs.")
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    args = parser.parse_args()

    rows = build_rows()
    issues = validate_rows(rows)
    payload = {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "firstBatchPublicationPacket": str(FIRST_BATCH_PATH.relative_to(ROOT)),
            "proofTemplates": str(PROOF_TEMPLATES_PATH.relative_to(ROOT)),
        },
        "tasks": len({(row["platform"], row["task_id"]) for row in rows}),
        "rows": len(rows),
        "zeroSourceCheckRows": sum(1 for row in rows if row["zero_requires_source_check"] == "1"),
        "pendingRows": sum(1 for row in rows if row["operator_status"] == "pending"),
        "items": rows,
        "issues": issues,
    }
    print(f"promotion_first_batch_kpi_checklist_tasks={payload['tasks']}")
    print(f"promotion_first_batch_kpi_checklist_rows={payload['rows']}")
    print(f"promotion_first_batch_kpi_checklist_zero_source_check={payload['zeroSourceCheckRows']}")
    print(f"promotion_first_batch_kpi_checklist_pending={payload['pendingRows']}")
    print(f"promotion_first_batch_kpi_checklist_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        write_csv(rows, Path(args.csv_output))
        Path(args.json_output).write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        Path(args.output).write_text(render_markdown(payload), encoding="utf-8")
        print(f"promotion_first_batch_kpi_checklist_csv={Path(args.csv_output).relative_to(ROOT)}")
        print(f"promotion_first_batch_kpi_checklist_json={Path(args.json_output).relative_to(ROOT)}")
        print(f"promotion_first_batch_kpi_checklist_md={Path(args.output).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
