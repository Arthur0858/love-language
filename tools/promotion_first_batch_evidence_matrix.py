#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
FIRST_BATCH = PROMOTION_DIR / "first-batch-publication-packet.json"
PUBLIC_URL = PROMOTION_DIR / "public-post-url-checklist.json"
ZERO_KPI = PROMOTION_DIR / "zero-kpi-evidence-checklist.json"
POST_OPS = PROMOTION_DIR / "post-ops-readiness-pack.json"
COMPLETION = PROMOTION_DIR / "first-batch-completion-gate.json"
EVIDENCE = PROMOTION_DIR / "evidence-ledger.json"
OUTPUT_MD = PROMOTION_DIR / "first-batch-evidence-matrix.md"
OUTPUT_JSON = PROMOTION_DIR / "first-batch-evidence-matrix.json"
OUTPUT_CSV = PROMOTION_DIR / "first-batch-evidence-matrix.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def count_by_status(items: list[dict], key_fields: tuple[str, str], status_field: str = "operator_status") -> dict[tuple[str, str], Counter[str]]:
    grouped: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for item in items:
        key = tuple(str(item.get(field, "")) for field in key_fields)
        grouped[key][str(item.get(status_field, ""))] += 1
    return grouped


def evidence_by_post(ledger: dict) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for item in ledger.get("rows", []):
        if item.get("evidence_type") != "post":
            continue
        key = (str(item.get("platform", "")), str(item.get("record_id", "")))
        rows[key] = {
            "required": str(item.get("required", "")),
            "status": str(item.get("evidence_status", "")),
            "proofDate": str(item.get("proof_date", "")),
            "proofNote": str(item.get("proof_note", "")),
        }
    return rows


def status_for_row(published: bool, public_counts: Counter[str], zero_counts: Counter[str], post_ops_status: str, proof_status: str) -> str:
    if not published:
        return "blocked_until_publish"
    if public_counts.get("complete", 0) < 4:
        return "needs_public_url_evidence"
    if zero_counts.get("complete", 0) < 3:
        return "needs_kpi_source_evidence"
    if proof_status not in {"traceable", "not_required_yet"}:
        return "needs_traceable_proof"
    if post_ops_status == "ready_for_weekly_review":
        return "ready_for_weekly_review"
    return "needs_completion_gate_refresh"


def build_matrix() -> dict:
    first = load_json(FIRST_BATCH)
    public = load_json(PUBLIC_URL)
    zero = load_json(ZERO_KPI)
    post_ops = load_json(POST_OPS)
    completion = load_json(COMPLETION)
    ledger = load_json(EVIDENCE)
    public_grouped = count_by_status(public.get("items", []), ("platform", "task_id"))
    zero_grouped = count_by_status(zero.get("items", []), ("platform", "task_id"))
    proof_rows = evidence_by_post(ledger)
    post_ops_by_key = {
        (str(row.get("platform", "")), str(row.get("task_id", ""))): row
        for row in post_ops.get("rows", [])
        if isinstance(row, dict)
    }

    rows: list[dict[str, str]] = []
    for item in first.get("rows", []):
        platform = str(item.get("platform", ""))
        task_id = str(item.get("taskId", ""))
        key = (platform, task_id)
        public_counts = public_grouped.get(key, Counter())
        zero_counts = zero_grouped.get(key, Counter())
        proof = proof_rows.get(key, {"status": "not_required_yet", "required": "0", "proofDate": "", "proofNote": ""})
        post_ops_row = post_ops_by_key.get(key, {})
        published = bool(item.get("published"))
        row_status = status_for_row(
            published,
            public_counts,
            zero_counts,
            str(post_ops_row.get("status", "")),
            proof.get("status", ""),
        )
        rows.append({
            "platform": platform,
            "taskId": task_id,
            "scriptId": str(item.get("scriptId", "")),
            "guardianId": str(item.get("guardianId", "")),
            "title": str(item.get("title", "")),
            "scheduled": f"{item.get('scheduledDate', '')} {item.get('scheduledTime', '')} Asia/Taipei".strip(),
            "published": "1" if published else "0",
            "postUrl": str(item.get("postUrl", "")),
            "utmContent": str(item.get("utmContent", "")),
            "matrixStatus": row_status,
            "publicComplete": str(public_counts.get("complete", 0)),
            "publicPending": str(public_counts.get("pending_publish", 0)),
            "publicOperatorVerify": str(public_counts.get("operator_verify", 0)),
            "zeroComplete": str(zero_counts.get("complete", 0)),
            "zeroPending": str(zero_counts.get("pending_publish", 0)),
            "zeroNeedsSourceProof": str(zero_counts.get("needs_source_proof", 0)),
            "postOpsStatus": str(post_ops_row.get("status", "")),
            "proofStatus": proof.get("status", ""),
            "proofRequired": proof.get("required", ""),
            "proofDate": proof.get("proofDate", ""),
            "proofNote": proof.get("proofNote", ""),
            "checkCommand": f"python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-{platform}-{task_id}.txt",
            "writeCommand": str(post_ops_row.get("kpi_command", item.get("kpiExampleCommand", ""))),
            "nextAction": next_action(row_status),
        })

    counts = Counter(row["matrixStatus"] for row in rows)
    completion_state = completion.get("state", {}) if isinstance(completion.get("state"), dict) else {}
    metrics = {
        "rows": len(rows),
        "published": sum(1 for row in rows if row["published"] == "1"),
        "blockedUntilPublish": counts["blocked_until_publish"],
        "needsPublicUrlEvidence": counts["needs_public_url_evidence"],
        "needsKpiSourceEvidence": counts["needs_kpi_source_evidence"],
        "needsTraceableProof": counts["needs_traceable_proof"],
        "readyForWeeklyReview": counts["ready_for_weekly_review"],
        "completionReady": 1 if completion_state.get("readyForWeeklyReview") else 0,
        "publicPendingRows": int(public.get("metrics", {}).get("pendingPublishRows", 0) or 0),
        "zeroPendingRows": int(zero.get("metrics", {}).get("pendingPublishRows", 0) or 0),
    }
    issues = validate(rows, metrics)
    return {
        "generatedAt": today(),
        "sources": {
            "firstBatchPublicationPacket": str(FIRST_BATCH.relative_to(ROOT)),
            "publicPostUrlChecklist": str(PUBLIC_URL.relative_to(ROOT)),
            "zeroKpiEvidenceChecklist": str(ZERO_KPI.relative_to(ROOT)),
            "postOpsReadinessPack": str(POST_OPS.relative_to(ROOT)),
            "firstBatchCompletionGate": str(COMPLETION.relative_to(ROOT)),
            "evidenceLedger": str(EVIDENCE.relative_to(ROOT)),
        },
        "policy": {
            "postUrlBeforeKpi": True,
            "zeroKpiRequiresSource": True,
            "weeklyRequiresAllRowsReady": True,
            "noCommercialDecisionBeforeWeeklyReady": True,
        },
        "metrics": metrics,
        "rows": rows,
        "issues": issues,
    }


def next_action(status: str) -> str:
    if status == "blocked_until_publish":
        return "Publish the platform post, then write back the real HTTPS post URL and proof note."
    if status == "needs_public_url_evidence":
        return "Verify the public post URL, platform domain, caption CTA, tracked URL and UTM."
    if status == "needs_kpi_source_evidence":
        return "Check analytics source before writing zero or positive starter KPI values."
    if status == "needs_traceable_proof":
        return "Replace generic or missing proof with a traceable proof note."
    if status == "ready_for_weekly_review":
        return "Run weekly summary, weekly review packet and decision evidence checklist."
    return "Refresh post ops readiness and first-batch completion gate."


def validate(rows: list[dict[str, str]], metrics: dict[str, int]) -> list[str]:
    issues: list[str] = []
    if metrics["rows"] != 3:
        issues.append(f"expected 3 first-batch evidence rows, got {metrics['rows']}")
    if metrics["completionReady"] and metrics["readyForWeeklyReview"] != metrics["rows"]:
        issues.append("completion gate cannot be ready unless every matrix row is ready")
    if metrics["published"] == 0 and metrics["readyForWeeklyReview"] != 0:
        issues.append("unpublished first batch cannot be ready for weekly review")
    for row in rows:
        for field in ("platform", "taskId", "scriptId", "guardianId", "matrixStatus", "checkCommand", "writeCommand", "nextAction"):
            if not row.get(field):
                issues.append(f"{row.get('platform', '<platform>')}/{row.get('taskId', '<task>')}: missing {field}")
        if row["matrixStatus"] == "ready_for_weekly_review" and (row["publicComplete"] != "8" or row["zeroComplete"] != "3"):
            issues.append(f"{row['platform']}/{row['taskId']}: ready row must complete public and KPI checks")
    return issues


def render_markdown(matrix: dict) -> str:
    metrics = matrix["metrics"]
    lines = [
        "# LoveTypes First Batch Evidence Matrix",
        "",
        f"- 產生日期：{matrix['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- published：{metrics['published']}",
        f"- blocked until publish：{metrics['blockedUntilPublish']}",
        f"- needs public URL evidence：{metrics['needsPublicUrlEvidence']}",
        f"- needs KPI source evidence：{metrics['needsKpiSourceEvidence']}",
        f"- ready for weekly review：{metrics['readyForWeeklyReview']}",
        f"- completion ready：{metrics['completionReady']}",
        f"- issues：{len(matrix['issues'])}",
        "",
        "## Rule",
        "",
        "- 先取得真實公開 post URL，再回填 KPI。",
        "- 0 可以是有效 KPI，但必須先檢查來源並留下 proof note。",
        "- 三平台都完成公開 URL、proof note、starter KPI 後，才進週回顧與商品判斷。",
        "",
        "## Matrix",
        "",
    ]
    for row in matrix["rows"]:
        lines.extend([
            f"### {row['platform']} · `{row['taskId']}`",
            "",
            f"- status：`{row['matrixStatus']}`",
            f"- scheduled：{row['scheduled']}",
            f"- published：{row['published']}",
            f"- post URL：{row['postUrl'] or '(pending)'}",
            f"- public complete / pending / verify：{row['publicComplete']} / {row['publicPending']} / {row['publicOperatorVerify']}",
            f"- KPI complete / pending / needs source：{row['zeroComplete']} / {row['zeroPending']} / {row['zeroNeedsSourceProof']}",
            f"- proof：`{row['proofStatus']}`",
            f"- check：`{row['checkCommand']}`",
            f"- write：`{row['writeCommand']}`",
            f"- next：{row['nextAction']}",
            "",
        ])
    if matrix["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in matrix["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(matrix: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(matrix), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fieldnames = [
        "platform", "taskId", "scriptId", "guardianId", "title", "scheduled", "published", "postUrl",
        "utmContent", "matrixStatus", "publicComplete", "publicPending", "publicOperatorVerify",
        "zeroComplete", "zeroPending", "zeroNeedsSourceProof", "postOpsStatus", "proofStatus",
        "proofRequired", "proofDate", "proofNote", "checkCommand", "writeCommand", "nextAction",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in matrix["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a consolidated evidence matrix for first-batch publication and KPI handoff.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    matrix = build_matrix()
    metrics = matrix["metrics"]
    if not args.check:
        write_outputs(matrix)
        print(f"promotion_first_batch_evidence_matrix={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_first_batch_evidence_matrix_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_first_batch_evidence_matrix_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_first_batch_evidence_rows={metrics['rows']}")
    print(f"promotion_first_batch_evidence_published={metrics['published']}")
    print(f"promotion_first_batch_evidence_blocked_until_publish={metrics['blockedUntilPublish']}")
    print(f"promotion_first_batch_evidence_needs_public_url={metrics['needsPublicUrlEvidence']}")
    print(f"promotion_first_batch_evidence_needs_kpi_source={metrics['needsKpiSourceEvidence']}")
    print(f"promotion_first_batch_evidence_needs_traceable_proof={metrics['needsTraceableProof']}")
    print(f"promotion_first_batch_evidence_ready_weekly={metrics['readyForWeeklyReview']}")
    print(f"promotion_first_batch_evidence_completion_ready={metrics['completionReady']}")
    print(f"promotion_first_batch_evidence_issues={len(matrix['issues'])}")
    for issue in matrix["issues"]:
        print(issue)
    return 1 if matrix["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
