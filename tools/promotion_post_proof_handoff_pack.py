#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PUBLISH_READINESS = PROMOTION_DIR / "first-batch-publish-readiness-pack.json"
POST_OPS = PROMOTION_DIR / "post-ops-readiness-pack.json"
WRITEBACK = PROMOTION_DIR / "post-writeback-playbook.json"
LAUNCH_RUN_SHEET = PROMOTION_DIR / "launch-day-run-sheet.json"
OUTPUT_MD = PROMOTION_DIR / "post-proof-handoff-pack.md"
OUTPUT_JSON = PROMOTION_DIR / "post-proof-handoff-pack.json"
OUTPUT_TXT = PROMOTION_DIR / "post-proof-handoff-pack.txt"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def run_import_check(proof_file: str) -> tuple[str, str]:
    result = subprocess.run(
        [sys.executable, "tools/promotion_post_text_import.py", "check", "--input", proof_file],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout.strip()
    if result.returncode == 0:
        return "ready_to_import", output
    if "published status requires non-placeholder https post_url" in output:
        return "template_safely_rejected", output
    return "invalid_proof_text", output


def post_ops_lookup(post_ops: dict) -> dict[tuple[str, str], dict]:
    lookup: dict[tuple[str, str], dict] = {}
    for row in post_ops.get("rows", []):
        if isinstance(row, dict):
            lookup[(str(row.get("platform", "")), str(row.get("task_id", "")))] = row
    return lookup


def build_pack() -> dict:
    publish = load_json(PUBLISH_READINESS)
    post_ops = load_json(POST_OPS)
    writeback = load_json(WRITEBACK)
    launch = load_json(LAUNCH_RUN_SHEET)
    ops_lookup = post_ops_lookup(post_ops)
    rows: list[dict[str, str]] = []
    for row in publish.get("rows", []):
        platform = str(row.get("platform", ""))
        task_id = str(row.get("task_id", ""))
        proof_file = str(row.get("post_proof_file", ""))
        proof_path = ROOT / proof_file
        proof_exists = proof_path.exists()
        import_status, import_output = run_import_check(proof_file) if proof_exists else ("missing_proof_file", "")
        ops = ops_lookup.get((platform, task_id), {})
        ready_to_import = import_status == "ready_to_import"
        safe_template = import_status == "template_safely_rejected"
        placeholder_proof = safe_template
        real_proof_ready = ready_to_import
        rows.append({
            "platform": platform,
            "task_id": task_id,
            "script_id": str(row.get("script_id", "")),
            "title": str(row.get("title", "")),
            "proof_file": proof_file,
            "proof_exists": "1" if proof_exists else "0",
            "import_status": import_status,
            "ready_to_import": "1" if ready_to_import else "0",
            "template_safely_rejected": "1" if safe_template else "0",
            "placeholder_proof": "1" if placeholder_proof else "0",
            "real_proof_ready": "1" if real_proof_ready else "0",
            "post_ops_status": str(ops.get("status", "")),
            "post_url": str(ops.get("post_url", "")),
            "check_command": f"python3 tools/promotion_post_text_import.py check --input {proof_file}",
            "write_command": f"python3 tools/promotion_post_text_import.py add --input {proof_file}",
            "fallback_writeback_command": str(ops.get("kpi_command", "")),
            "next_action": (
                "Run the write command only after confirming the proof text contains the real public post URL and checked KPI source."
                if ready_to_import
                else "Replace the placeholder post_url and proof_note date, then rerun the check command."
                if safe_template
                else "Repair the proof text before writeback."
            ),
            "stop_condition": (
                "Stop if the URL is still a placeholder, the platform domain does not match, or zero metrics lack checked-source proof."
            ),
            "import_output": import_output.replace("\n", " | "),
        })

    metrics = {
        "rows": len(rows),
        "proofFiles": sum(1 for row in rows if row["proof_exists"] == "1"),
        "readyToImport": sum(1 for row in rows if row["ready_to_import"] == "1"),
        "templatesSafelyRejected": sum(1 for row in rows if row["template_safely_rejected"] == "1"),
        "placeholderProofRows": sum(1 for row in rows if row["placeholder_proof"] == "1"),
        "realProofReadyRows": sum(1 for row in rows if row["real_proof_ready"] == "1"),
        "blockedUntilPostUrl": sum(1 for row in rows if row["post_ops_status"] == "blocked_until_post_url"),
        "writebackCommands": sum(1 for row in rows if row["write_command"]),
        "launchDayPostOpsRows": int(launch.get("metrics", {}).get("postOpsRows", 0) or 0),
        "postOpsRows": int(post_ops.get("metrics", {}).get("rows", 0) or 0),
        "postWritebackFirstBatch": len(writeback.get("firstBatch", [])),
    }
    issues: list[str] = []
    if metrics["rows"] != 3:
        issues.append(f"expected 3 first-batch proof handoff rows, got {metrics['rows']}")
    if metrics["proofFiles"] != metrics["rows"]:
        issues.append("all first-batch proof files should exist")
    if metrics["readyToImport"] + metrics["templatesSafelyRejected"] != metrics["rows"]:
        issues.append("each proof file should either be import-ready or safely rejected as a placeholder template")
    if metrics["placeholderProofRows"] + metrics["realProofReadyRows"] != metrics["rows"]:
        issues.append("each proof file should be explicitly placeholder or real proof ready")
    if metrics["realProofReadyRows"] != metrics["readyToImport"]:
        issues.append("real proof ready rows should match import-ready rows")
    if metrics["postOpsRows"] != metrics["rows"]:
        issues.append("post ops rows should match first-batch proof rows")
    if metrics["postWritebackFirstBatch"] != metrics["rows"]:
        issues.append("post writeback first-batch rows should match proof rows")
    if metrics["launchDayPostOpsRows"] and metrics["launchDayPostOpsRows"] != metrics["rows"]:
        issues.append("launch day post ops rows should match proof rows")

    return {
        "generatedAt": today(),
        "sources": {
            "firstBatchPublishReadinessPack": str(PUBLISH_READINESS.relative_to(ROOT)),
            "postOpsReadinessPack": str(POST_OPS.relative_to(ROOT)),
            "postWritebackPlaybook": str(WRITEBACK.relative_to(ROOT)),
            "launchDayRunSheet": str(LAUNCH_RUN_SHEET.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Proof text is the handoff surface between external publishing and local KPI writeback.",
            "Placeholder proof files must fail the import check until a real public post URL is pasted in.",
            "Run the check command before the write command for every platform.",
            "Do not write zero KPI values unless the proof note names the checked analytics source.",
        ],
        "issues": issues,
    }


def render_markdown(pack: dict) -> str:
    metrics = pack["metrics"]
    lines = [
        "# LoveTypes Post Proof Handoff Pack",
        "",
        f"- 產生日期：{pack['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- proof files：{metrics['proofFiles']}",
        f"- ready to import：{metrics['readyToImport']}",
        f"- templates safely rejected：{metrics['templatesSafelyRejected']}",
        f"- placeholder proof rows：{metrics['placeholderProofRows']}",
        f"- real proof ready rows：{metrics['realProofReadyRows']}",
        f"- blocked until post URL：{metrics['blockedUntilPostUrl']}",
        f"- writeback commands：{metrics['writebackCommands']}",
        f"- issues：{len(pack['issues'])}",
        "",
        "## Rule",
        "",
    ]
    lines.extend(f"- {rule}" for rule in pack["rules"])
    lines.extend(["", "## Rows", ""])
    for row in pack["rows"]:
        lines.extend([
            f"### {row['platform']} · `{row['task_id']}`",
            "",
            f"- status：`{row['import_status']}`",
            f"- proof：placeholder={row['placeholder_proof']} / real_ready={row['real_proof_ready']}",
            f"- post ops：`{row['post_ops_status']}`",
            f"- proof：`{row['proof_file']}`",
            f"- title：{row['title']}",
            f"- check：`{row['check_command']}`",
            f"- write：`{row['write_command']}`",
            f"- fallback：`{row['fallback_writeback_command']}`" if row["fallback_writeback_command"] else "- fallback：",
            f"- next：{row['next_action']}",
            f"- stop：{row['stop_condition']}",
            "",
        ])
    if pack["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in pack["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_text(pack: dict) -> str:
    lines = [
        "LoveTypes post proof handoff",
        f"generated_at: {pack['generatedAt']}",
        f"rows: {pack['metrics']['rows']}",
        f"ready_to_import: {pack['metrics']['readyToImport']}",
        f"templates_safely_rejected: {pack['metrics']['templatesSafelyRejected']}",
        f"placeholder_proof_rows: {pack['metrics']['placeholderProofRows']}",
        f"real_proof_ready_rows: {pack['metrics']['realProofReadyRows']}",
        "",
    ]
    for row in pack["rows"]:
        lines.extend([
            f"[{row['platform']}] {row['task_id']}",
            f"proof: {row['proof_file']}",
            f"check: {row['check_command']}",
            f"write: {row['write_command']}",
            f"next: {row['next_action']}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(pack: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(pack), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_TXT.write_text(render_text(pack), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the first-batch platform post proof handoff pack.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    pack = build_pack()
    metrics = pack["metrics"]
    if not args.check:
        write_outputs(pack)
        print(f"promotion_post_proof_handoff_pack={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_post_proof_handoff_pack_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_post_proof_handoff_pack_txt={OUTPUT_TXT.relative_to(ROOT)}")
    print(f"promotion_post_proof_handoff_rows={metrics['rows']}")
    print(f"promotion_post_proof_handoff_proof_files={metrics['proofFiles']}")
    print(f"promotion_post_proof_handoff_ready_to_import={metrics['readyToImport']}")
    print(f"promotion_post_proof_handoff_templates_safely_rejected={metrics['templatesSafelyRejected']}")
    print(f"promotion_post_proof_handoff_placeholder_proof_rows={metrics['placeholderProofRows']}")
    print(f"promotion_post_proof_handoff_real_proof_ready_rows={metrics['realProofReadyRows']}")
    print(f"promotion_post_proof_handoff_blocked_until_post_url={metrics['blockedUntilPostUrl']}")
    print(f"promotion_post_proof_handoff_writeback_commands={metrics['writebackCommands']}")
    print(f"promotion_post_proof_handoff_post_ops_rows={metrics['postOpsRows']}")
    print(f"promotion_post_proof_handoff_writeback_first_batch={metrics['postWritebackFirstBatch']}")
    print(f"promotion_post_proof_handoff_issues={len(pack['issues'])}")
    for issue in pack["issues"]:
        print(issue)
    return 1 if pack["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
