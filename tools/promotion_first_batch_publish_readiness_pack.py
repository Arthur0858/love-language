#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_GATE = PROMOTION_DIR / "profile-completion-gate.json"
ASSET_QA = PROMOTION_DIR / "first-batch-asset-qa.json"
PUBLISH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
PUBLICATION_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
PROOF_TEMPLATES = PROMOTION_DIR / "operation-proof-templates.json"
OUTPUT_MD = PROMOTION_DIR / "first-batch-publish-readiness-pack.md"
OUTPUT_JSON = PROMOTION_DIR / "first-batch-publish-readiness-pack.json"
OUTPUT_CSV = PROMOTION_DIR / "first-batch-publish-readiness-pack.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def run_post_import_check(path: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "tools/promotion_post_text_import.py", "check", "--input", path],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout.strip()
    safely_rejected = (
        result.returncode != 0
        and "published status requires non-placeholder https post_url" in output
    )
    return safely_rejected, output


def post_proof_path(platform: str, task_id: str) -> str:
    return f"docs/promotion/first-round/proof-{platform}-{task_id}.txt"


def by_platform_task(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {
        (str(row.get("platform", "")), str(row.get("taskId") or row.get("task_id") or "")): row
        for row in rows
        if isinstance(row, dict)
    }


def build_pack() -> dict:
    profile_gate = load_json(PROFILE_GATE)
    asset_qa = load_json(ASSET_QA)
    publish_action = load_json(PUBLISH_ACTION)
    publication = load_json(PUBLICATION_PACKET)
    proof_templates = load_json(PROOF_TEMPLATES)
    asset_lookup = by_platform_task(asset_qa.get("rows", []))
    action_lookup = by_platform_task(publish_action.get("rows", []))
    rows: list[dict[str, str]] = []
    for pub in publication.get("rows", []):
        platform = str(pub.get("platform", ""))
        task_id = str(pub.get("taskId", ""))
        key = (platform, task_id)
        asset = asset_lookup.get(key, {})
        action = action_lookup.get(key, {})
        proof_path = post_proof_path(platform, task_id)
        safely_rejected, import_output = run_post_import_check(proof_path)
        profile_ready = bool(profile_gate.get("state", {}).get("readyForFirstBatchPublish"))
        asset_ready = str(asset.get("assetReadyStatus", "")) == "ready"
        public_url_ready = bool(pub.get("postUrl"))
        row_status = "ready_to_publish" if profile_ready and asset_ready else "blocked_until_profile_gate"
        if public_url_ready:
            row_status = "published"
        rows.append({
            "platform": platform,
            "task_id": task_id,
            "script_id": str(pub.get("scriptId", "")),
            "guardian_id": str(pub.get("guardianId", "")),
            "title": str(pub.get("title", "")),
            "scheduled_date": str(pub.get("scheduledDate", "")),
            "scheduled_time": str(pub.get("scheduledTime", "")),
            "profile_gate_ready": "1" if profile_ready else "0",
            "asset_qa_ready": "1" if asset_ready else "0",
            "publish_action_status": str(action.get("action_status", "")),
            "post_url_ready": "1" if public_url_ready else "0",
            "post_proof_file": proof_path,
            "post_proof_template_safely_rejected": "1" if safely_rejected else "0",
            "operator_status": row_status,
            "caption_ready": "1" if "完成 15 題測驗" in str(pub.get("caption", "")) else "0",
            "tracked_url": str(pub.get("trackedUrl", "")),
            "stop_condition": "Stop if profile gate is not ready, post URL is still placeholder, caption changes CTA, or platform preview adds commercial claims.",
            "import_output": import_output.replace("\n", " | "),
        })
    proof_metrics = proof_templates.get("metrics", {}) if isinstance(proof_templates.get("metrics"), dict) else {}
    metrics = {
        "rows": len(rows),
        "profileGateReady": 1 if profile_gate.get("state", {}).get("readyForFirstBatchPublish") else 0,
        "assetQaReady": sum(1 for row in rows if row["asset_qa_ready"] == "1"),
        "readyToPublish": sum(1 for row in rows if row["operator_status"] == "ready_to_publish"),
        "blocked": sum(1 for row in rows if row["operator_status"].startswith("blocked")),
        "published": sum(1 for row in rows if row["operator_status"] == "published"),
        "proofFiles": sum(1 for row in rows if (ROOT / row["post_proof_file"]).exists()),
        "proofTemplatesSafelyRejected": sum(1 for row in rows if row["post_proof_template_safely_rejected"] == "1"),
        "operationProofPostSafelyRejected": int(proof_metrics.get("postSafelyRejected", 0) or 0),
    }
    issues: list[str] = []
    if metrics["rows"] != 3:
        issues.append(f"expected 3 first-batch publish readiness rows, got {metrics['rows']}")
    if metrics["assetQaReady"] != metrics["rows"]:
        issues.append("all first-batch asset QA rows should be ready")
    if metrics["proofFiles"] != metrics["rows"]:
        issues.append("all post proof template files should exist")
    if metrics["proofTemplatesSafelyRejected"] != metrics["rows"]:
        issues.append("all post proof templates should be safely rejected until real post URLs exist")
    if metrics["profileGateReady"] == 0 and metrics["readyToPublish"] != 0:
        issues.append("no row can be ready_to_publish before profile gate is ready")
    if metrics["operationProofPostSafelyRejected"] and metrics["operationProofPostSafelyRejected"] != metrics["rows"]:
        issues.append("operation proof template post rejection count should match first batch rows")
    return {
        "generatedAt": today(),
        "sources": {
            "profileGate": str(PROFILE_GATE.relative_to(ROOT)),
            "assetQa": str(ASSET_QA.relative_to(ROOT)),
            "publishAction": str(PUBLISH_ACTION.relative_to(ROOT)),
            "publicationPacket": str(PUBLICATION_PACKET.relative_to(ROOT)),
            "proofTemplates": str(PROOF_TEMPLATES.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Asset QA ready does not authorize publishing until profile gate is ready.",
            "Post proof templates must remain safely rejected while post_url is a placeholder.",
            "Only real public post URLs may move a row from blocked/ready to published.",
            "After publish, backfill minimum KPI with checked-source zeros or real values.",
        ],
        "issues": issues,
    }


def render_markdown(pack: dict) -> str:
    metrics = pack["metrics"]
    lines = [
        "# LoveTypes First Batch Publish Readiness Pack",
        "",
        f"- 產生日期：{pack['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- profile gate ready：{metrics['profileGateReady']}",
        f"- asset QA ready：{metrics['assetQaReady']}",
        f"- ready to publish：{metrics['readyToPublish']}",
        f"- blocked：{metrics['blocked']}",
        f"- published：{metrics['published']}",
        f"- proof templates safely rejected：{metrics['proofTemplatesSafelyRejected']}",
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
            f"- status：`{row['operator_status']}`",
            f"- script：`{row['script_id']}`",
            f"- guardian：`{row['guardian_id']}`",
            f"- title：{row['title']}",
            f"- schedule：{row['scheduled_date']} {row['scheduled_time']} Asia/Taipei",
            f"- profile gate ready：{row['profile_gate_ready']}",
            f"- asset QA ready：{row['asset_qa_ready']}",
            f"- publish action status：`{row['publish_action_status']}`",
            f"- post URL ready：{row['post_url_ready']}",
            f"- post proof file：`{row['post_proof_file']}`",
            f"- proof template safely rejected：{row['post_proof_template_safely_rejected']}",
            f"- tracked URL：{row['tracked_url']}",
            f"- stop：{row['stop_condition']}",
            "",
        ])
    if pack["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in pack["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(pack: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(pack), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fieldnames = [
        "platform",
        "task_id",
        "script_id",
        "guardian_id",
        "scheduled_date",
        "scheduled_time",
        "profile_gate_ready",
        "asset_qa_ready",
        "publish_action_status",
        "post_url_ready",
        "post_proof_file",
        "post_proof_template_safely_rejected",
        "operator_status",
        "caption_ready",
        "tracked_url",
        "stop_condition",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in pack["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a first-batch publish readiness pack.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    pack = build_pack()
    metrics = pack["metrics"]
    if not args.check:
        write_outputs(pack)
        print(f"promotion_first_batch_publish_readiness_pack={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_first_batch_publish_readiness_pack_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_first_batch_publish_readiness_pack_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_first_batch_publish_readiness_rows={metrics['rows']}")
    print(f"promotion_first_batch_publish_readiness_profile_gate_ready={metrics['profileGateReady']}")
    print(f"promotion_first_batch_publish_readiness_asset_qa_ready={metrics['assetQaReady']}")
    print(f"promotion_first_batch_publish_readiness_ready_to_publish={metrics['readyToPublish']}")
    print(f"promotion_first_batch_publish_readiness_blocked={metrics['blocked']}")
    print(f"promotion_first_batch_publish_readiness_published={metrics['published']}")
    print(f"promotion_first_batch_publish_readiness_proof_files={metrics['proofFiles']}")
    print(f"promotion_first_batch_publish_readiness_templates_safely_rejected={metrics['proofTemplatesSafelyRejected']}")
    print(f"promotion_first_batch_publish_readiness_issues={len(pack['issues'])}")
    for issue in pack["issues"]:
        print(issue)
    return 1 if pack["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
