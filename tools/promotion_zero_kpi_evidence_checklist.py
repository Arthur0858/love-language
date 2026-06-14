#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
FIRST_BATCH_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
OUTPUT_MD = PROMOTION_DIR / "zero-kpi-evidence-checklist.md"
OUTPUT_JSON = PROMOTION_DIR / "zero-kpi-evidence-checklist.json"
OUTPUT_CSV = PROMOTION_DIR / "zero-kpi-evidence-checklist.csv"

ZERO_CHECK_METRICS = {
    "site_clicks": "Cloudflare/Web analytics, platform link analytics, or tracked UTM report.",
    "quiz_starts": "Funnel event catalog/report, analytics event export, or manual verified source.",
    "quiz_completions": "Funnel event catalog/report, analytics event export, or manual verified source.",
}


def today() -> str:
    return date.today().isoformat()


def load_packet() -> dict:
    return json.loads(FIRST_BATCH_PACKET.read_text(encoding="utf-8"))


def row_status(post: dict, metric: str) -> tuple[str, str]:
    if not post.get("published"):
        return "pending_publish", "貼文尚未公開；不可回填 0 或正數。"
    minimum_kpis = post.get("minimumKpis", {}) if isinstance(post.get("minimumKpis"), dict) else {}
    value = minimum_kpis.get(metric)
    notes = str(post.get("notes", ""))
    if value is None:
        return "missing", "missing metric value"
    if int(value or 0) == 0:
        if "verified:" in notes and ("analytics" in notes.lower() or "checked" in notes.lower()):
            return "complete", "0 value has traceable checked-source note."
        return "needs_source_proof", "0 value requires checked source date and proof note."
    return "complete", "positive metric value recorded; keep source note for weekly review."


def build_payload() -> dict:
    packet = load_packet()
    rows: list[dict[str, str]] = []
    for post in packet.get("rows", []):
        for metric, source in ZERO_CHECK_METRICS.items():
            status, evidence = row_status(post, metric)
            rows.append({
                "platform": str(post.get("platform", "")),
                "task_id": str(post.get("taskId", "")),
                "script_id": str(post.get("scriptId", "")),
                "guardian_id": str(post.get("guardianId", "")),
                "metric_id": metric,
                "metric_value": str((post.get("minimumKpis") or {}).get(metric, "")),
                "required_source": source,
                "published_status": "published" if post.get("published") else "pending",
                "post_url": str(post.get("postUrl", "")),
                "utm_content": str(post.get("utmContent", "")),
                "operator_status": status,
                "evidence_note": evidence,
                "proof_note_template": f"analytics source checked {today()} for {post.get('platform', '')}/{post.get('taskId', '')}/{metric}",
            })
    return {
        "generatedAt": today(),
        "source": str(FIRST_BATCH_PACKET.relative_to(ROOT)),
        "metrics": {
            "posts": len(packet.get("rows", [])),
            "metricTypes": len(ZERO_CHECK_METRICS),
            "rows": len(rows),
            "publishedPosts": sum(1 for post in packet.get("rows", []) if post.get("published")),
            "pendingPublishRows": sum(1 for row in rows if row["operator_status"] == "pending_publish"),
            "needsSourceProofRows": sum(1 for row in rows if row["operator_status"] == "needs_source_proof"),
            "completeRows": sum(1 for row in rows if row["operator_status"] == "complete"),
            "missingRows": sum(1 for row in rows if row["operator_status"] == "missing"),
        },
        "policy": {
            "zeroIsNotBlank": True,
            "zeroRequiresSourceProof": True,
            "weeklyReviewRequiresCheckedZeroes": True,
        },
        "items": rows,
    }


def validate(payload: dict) -> list[str]:
    issues: list[str] = []
    metrics = payload["metrics"]
    if metrics["posts"] < 1:
        issues.append("expected at least 1 first-batch post")
    if metrics["rows"] != metrics["posts"] * metrics["metricTypes"]:
        issues.append("zero KPI evidence row count mismatch")
    if metrics["missingRows"]:
        issues.append(f"zero KPI rows missing metric values: {metrics['missingRows']}")
    for row in payload["items"]:
        if not row["platform"] or not row["task_id"] or row["metric_id"] not in ZERO_CHECK_METRICS:
            issues.append("zero KPI row missing platform, task_id, or metric_id")
        if row["operator_status"] not in {"pending_publish", "needs_source_proof", "complete", "missing"}:
            issues.append(f"{row['platform']}/{row['task_id']}/{row['metric_id']}: invalid operator_status")
    if not payload["policy"].get("zeroRequiresSourceProof"):
        issues.append("policy must require source proof for zero KPI")
    return issues


def render_markdown(payload: dict, issues: list[str]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes Zero KPI Evidence Checklist",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- first-batch posts：{metrics['posts']}",
        f"- published posts：{metrics['publishedPosts']}",
        f"- checklist rows：{metrics['rows']}",
        f"- pending publish rows：{metrics['pendingPublishRows']}",
        f"- needs source proof rows：{metrics['needsSourceProofRows']}",
        f"- missing rows：{metrics['missingRows']}",
        "- 用途：避免把 `site_clicks`、`quiz_starts`、`quiz_completions` 的 0 當作空資料或猜測值。",
        "",
        "## Rule",
        "",
        "- 0 是有效數據，但只有在來源已檢查並留下 proof note 後才有效。",
        "- 未發布貼文不能回填 0，也不能進週回顧。",
        "- 沒有來源證據時，不調整商品、Luna、聯盟或守護者優先序。",
        "",
    ]
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in payload["items"]:
        grouped.setdefault((row["platform"], row["task_id"]), []).append(row)
    for (platform, task_id), rows in grouped.items():
        lines.extend([
            f"## {platform} · `{task_id}`",
            "",
            f"- script：`{rows[0]['script_id']}`",
            f"- guardian：`{rows[0]['guardian_id']}`",
            f"- post URL：{rows[0]['post_url'] or '(pending)'}",
            "",
        ])
        for row in rows:
            marker = "x" if row["operator_status"] == "complete" else " "
            lines.append(
                f"- [{marker}] `{row['metric_id']}`：value `{row['metric_value'] or '(pending)'}`；"
                f"{row['required_source']}（{row['operator_status']}）"
            )
        lines.append("")
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict, issues: list[str]) -> None:
    OUTPUT_JSON.write_text(json.dumps({**payload, "issues": issues}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload, issues), encoding="utf-8")
    fieldnames = [
        "platform",
        "task_id",
        "script_id",
        "guardian_id",
        "metric_id",
        "metric_value",
        "required_source",
        "published_status",
        "post_url",
        "utm_content",
        "operator_status",
        "evidence_note",
        "proof_note_template",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(payload["items"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a source-proof checklist for zero first-batch KPI values.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    issues = validate(payload)
    if not args.check:
        write_outputs(payload, issues)
        print(f"promotion_zero_kpi_evidence_csv={OUTPUT_CSV}")
        print(f"promotion_zero_kpi_evidence_json={OUTPUT_JSON}")
        print(f"promotion_zero_kpi_evidence_md={OUTPUT_MD}")
    metrics = payload["metrics"]
    print(f"promotion_zero_kpi_evidence_posts={metrics['posts']}")
    print(f"promotion_zero_kpi_evidence_published={metrics['publishedPosts']}")
    print(f"promotion_zero_kpi_evidence_rows={metrics['rows']}")
    print(f"promotion_zero_kpi_evidence_pending_publish={metrics['pendingPublishRows']}")
    print(f"promotion_zero_kpi_evidence_needs_source_proof={metrics['needsSourceProofRows']}")
    print(f"promotion_zero_kpi_evidence_complete={metrics['completeRows']}")
    print(f"promotion_zero_kpi_evidence_missing={metrics['missingRows']}")
    print(f"promotion_zero_kpi_evidence_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
