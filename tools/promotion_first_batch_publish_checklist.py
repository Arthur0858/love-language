#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
ASSET_QA_PATH = PROMOTION_DIR / "first-batch-asset-qa.json"
PROOF_TEMPLATES_PATH = PROMOTION_DIR / "operation-proof-templates.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "first-batch-publish-checklist.csv"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-publish-checklist.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-publish-checklist.md"

FIELDNAMES = [
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "phase",
    "check_id",
    "required_evidence",
    "expected_value",
    "tracked_url",
    "proof_file",
    "check_command",
    "write_command",
    "evidence_value",
    "operator_status",
    "notes",
]

POST_PUBLISH_CHECKS = [
    {
        "id": "profile_gate_passed",
        "expected": "launch readiness ready_to_publish=1 after all active profile links are set/live.",
    },
    {
        "id": "public_post_url_present",
        "expected": "The platform post has a public HTTPS URL.",
    },
    {
        "id": "post_url_is_not_placeholder",
        "expected": "post_url is not <REAL_...>, example.com, or any other placeholder.",
    },
    {
        "id": "quiz_cta_preserved",
        "expected": "Published caption still uses the 15-question guardian quiz as the primary CTA.",
    },
    {
        "id": "utm_content_preserved",
        "expected": "The published post keeps the planned first-round UTM content.",
    },
    {
        "id": "proof_note_present",
        "expected": "A traceable proof note exists, such as public post URL checked, screenshot, or platform timestamp.",
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
    asset_qa = read_json(ASSET_QA_PATH)
    proof_rows = post_proof_rows()
    rows: list[dict[str, str]] = []
    for item in asset_qa.get("rows", []):
        platform = str(item.get("platform", ""))
        task_id = str(item.get("taskId", ""))
        proof = proof_rows.get((platform, task_id), {})
        proof_path = str(proof.get("path") or f"docs/promotion/first-round/proof-{platform}-{task_id}.txt")
        common = {
            "platform": platform,
            "task_id": task_id,
            "script_id": str(item.get("scriptId", "")),
            "guardian_id": str(item.get("guardianId", "")),
            "tracked_url": str(item.get("trackedUrl", "")),
            "proof_file": proof_path,
            "check_command": str(proof.get("checkCommand") or f"python3 tools/promotion_post_text_import.py check --input {proof_path}"),
            "write_command": str(proof.get("writeCommand") or f"python3 tools/promotion_post_text_import.py add --input {proof_path} --proof-note \"<REAL_PUBLIC_POST_AND_ANALYTICS_PROOF_NOTE> verified\""),
            "evidence_value": "",
            "operator_status": "pending",
        }
        for qa in item.get("qaItems", []):
            rows.append({
                **common,
                "phase": "pre_publish_asset_qa",
                "check_id": f"{platform}-{task_id}-{qa.get('id', '')}",
                "required_evidence": str(qa.get("id", "")),
                "expected_value": str(qa.get("check", "")),
                "notes": str(qa.get("evidence", "")),
            })
        for check in POST_PUBLISH_CHECKS:
            rows.append({
                **common,
                "phase": "post_publish_writeback",
                "check_id": f"{platform}-{task_id}-{check['id']}",
                "required_evidence": check["id"],
                "expected_value": check["expected"],
                "notes": "Complete after the public post exists; then validate the proof text before writeback.",
            })
    return rows


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    tasks = {(row["platform"], row["task_id"]) for row in rows}
    if not tasks:
        issues.append("expected at least 1 platform post task")
    expected_rows = len(tasks) * (8 + len(POST_PUBLISH_CHECKS))
    if len(rows) != expected_rows:
        issues.append(f"expected {expected_rows} first-batch publish checklist rows, got {len(rows)}")
    for platform, task_id in sorted(tasks):
        task_rows = [row for row in rows if row["platform"] == platform and row["task_id"] == task_id]
        pre = [row for row in task_rows if row["phase"] == "pre_publish_asset_qa"]
        post = [row for row in task_rows if row["phase"] == "post_publish_writeback"]
        if len(pre) != 8:
            issues.append(f"{platform}/{task_id}: expected 8 pre-publish checks, got {len(pre)}")
        if len(post) != 6:
            issues.append(f"{platform}/{task_id}: expected 6 post-publish checks, got {len(post)}")
        if {row["required_evidence"] for row in post} != {item["id"] for item in POST_PUBLISH_CHECKS}:
            issues.append(f"{platform}/{task_id}: missing post-publish proof checks")
    for row in rows:
        label = row["check_id"]
        if row["operator_status"] != "pending":
            issues.append(f"{label}: generated rows should start pending")
        if row["phase"] == "post_publish_writeback":
            if not row["proof_file"].endswith(f"proof-{row['platform']}-{row['task_id']}.txt"):
                issues.append(f"{label}: proof_file should point to platform post proof template")
            if "promotion_post_text_import.py check" not in row["check_command"]:
                issues.append(f"{label}: missing post proof check command")
            if "promotion_post_text_import.py add" not in row["write_command"]:
                issues.append(f"{label}: missing post proof write command")
        if "https://lovetypes.tw/start/?" not in row["tracked_url"]:
            issues.append(f"{label}: tracked_url should point to /start/")
    return issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes First Batch Publish Checklist",
        "",
        f"- Generated: `{payload['generatedAt']}`",
        f"- Tasks: `{payload['tasks']}`",
        f"- Checklist rows: `{payload['rows']}`",
        f"- Pre-publish rows: `{payload['prePublishRows']}`",
        f"- Post-publish rows: `{payload['postPublishRows']}`",
        f"- Pending rows: `{payload['pendingRows']}`",
        f"- Issues: `{len(payload['issues'])}`",
        "",
        "## Rule",
        "",
        "- Do not publish until profile gate is ready and all pre-publish checks have evidence.",
        "- Do not write post URL or KPI until the public post exists and the post proof template passes check.",
        "- Zero KPI values require a checked source; do not use empty data as a product decision.",
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
            f"- Tracked URL: {rows[0]['tracked_url']}",
            f"- Proof file: `{rows[0]['proof_file']}`",
            "",
            "### Pre-Publish",
            "",
        ])
        for row in rows:
            if row["phase"] == "pre_publish_asset_qa":
                lines.append(f"- [ ] `{row['required_evidence']}`：{row['expected_value']}")
        lines.extend(["", "### Post-Publish", ""])
        for row in rows:
            if row["phase"] == "post_publish_writeback":
                lines.append(f"- [ ] `{row['required_evidence']}`：{row['expected_value']}")
        lines.append("")
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fillable checklist for the first LoveTypes publishing batch.")
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
            "assetQa": str(ASSET_QA_PATH.relative_to(ROOT)),
            "proofTemplates": str(PROOF_TEMPLATES_PATH.relative_to(ROOT)),
        },
        "tasks": len({(row["platform"], row["task_id"]) for row in rows}),
        "rows": len(rows),
        "prePublishRows": sum(1 for row in rows if row["phase"] == "pre_publish_asset_qa"),
        "postPublishRows": sum(1 for row in rows if row["phase"] == "post_publish_writeback"),
        "pendingRows": sum(1 for row in rows if row["operator_status"] == "pending"),
        "items": rows,
        "issues": issues,
    }
    print(f"promotion_first_batch_publish_checklist_tasks={payload['tasks']}")
    print(f"promotion_first_batch_publish_checklist_rows={payload['rows']}")
    print(f"promotion_first_batch_publish_checklist_pre_publish={payload['prePublishRows']}")
    print(f"promotion_first_batch_publish_checklist_post_publish={payload['postPublishRows']}")
    print(f"promotion_first_batch_publish_checklist_pending={payload['pendingRows']}")
    print(f"promotion_first_batch_publish_checklist_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        write_csv(rows, Path(args.csv_output))
        Path(args.json_output).write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        Path(args.output).write_text(render_markdown(payload), encoding="utf-8")
        print(f"promotion_first_batch_publish_checklist_csv={Path(args.csv_output).relative_to(ROOT)}")
        print(f"promotion_first_batch_publish_checklist_json={Path(args.json_output).relative_to(ROOT)}")
        print(f"promotion_first_batch_publish_checklist_md={Path(args.output).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
