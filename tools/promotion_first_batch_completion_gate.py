#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
FIRST_BATCH_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
EVIDENCE_LEDGER = PROMOTION_DIR / "evidence-ledger.json"
PUBLISHING_STATUS = PROMOTION_DIR / "publishing-status.json"
KPI_CONSISTENCY = PROMOTION_DIR / "attribution-reconciliation.json"
MD_OUTPUT = PROMOTION_DIR / "first-batch-completion-gate.md"
JSON_OUTPUT = PROMOTION_DIR / "first-batch-completion-gate.json"
MINIMUM_KPI_FIELDS = ("site_clicks", "quiz_starts", "quiz_completions")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def first_batch_evidence_rows(evidence: dict) -> list[dict]:
    rows = evidence.get("rows", [])
    if not isinstance(rows, list):
        return []
    return [
        row for row in rows
        if row.get("evidence_type") == "post"
        and str(row.get("record_id", "")).startswith("publish-lt-s01-iris-silence")
    ]


def row_has_minimum_kpi(row: dict) -> bool:
    values = row.get("minimumKpis", {})
    if not isinstance(values, dict):
        return False
    # Zero is valid only after the row is published, because it means the platform was checked.
    return all(field in values for field in MINIMUM_KPI_FIELDS)


def build_gate() -> dict:
    first_batch = load_json(FIRST_BATCH_PACKET)
    evidence = load_json(EVIDENCE_LEDGER)
    publishing = load_json(PUBLISHING_STATUS)
    attribution = load_json(KPI_CONSISTENCY)

    rows = first_batch.get("rows", []) if isinstance(first_batch.get("rows"), list) else []
    expected_platform_count = max(1, int(first_batch.get("rowCount") or len(rows) or 0))
    published_rows = int(first_batch.get("publishedRows") or 0)
    minimum_kpi_rows = int(first_batch.get("minimumKpiRows") or 0)
    evidence_rows = first_batch_evidence_rows(evidence)
    traceable_post_evidence = sum(1 for row in evidence_rows if row.get("evidence_status") == "traceable")
    generic_post_evidence = sum(1 for row in evidence_rows if row.get("evidence_status") == "generic")
    missing_post_evidence = sum(1 for row in evidence_rows if row.get("required") == "1" and row.get("evidence_status") == "missing")
    publishing_ready = bool(publishing.get("readyForWeeklyDecision"))
    attribution_filled_rows = int(attribution.get("metrics", {}).get("filledKpiRows") or 0) if isinstance(attribution.get("metrics"), dict) else 0

    first_batch_published = published_rows == expected_platform_count
    evidence_complete = traceable_post_evidence >= published_rows and generic_post_evidence == 0 and missing_post_evidence == 0
    minimum_kpi_complete = minimum_kpi_rows == expected_platform_count
    row_shape_complete = len(rows) == expected_platform_count and all(row_has_minimum_kpi(row) for row in rows)
    ready_for_weekly_review = first_batch_published and evidence_complete and minimum_kpi_complete and publishing_ready

    blockers: list[dict[str, str]] = []
    if not first_batch_published:
        blockers.append({
            "id": "first_batch_not_published",
            "message": f"published rows {published_rows}/{expected_platform_count}; publish each platform post and write back post_url.",
            "release": "All first-batch rows are marked published/live/posted with real post_url values.",
        })
    if not evidence_complete:
        blockers.append({
            "id": "post_evidence_incomplete",
            "message": f"traceable post evidence {traceable_post_evidence}/{published_rows}; generic {generic_post_evidence}, missing {missing_post_evidence}.",
            "release": "Every published first-batch post has a traceable proof note.",
        })
    if not minimum_kpi_complete:
        blockers.append({
            "id": "minimum_kpi_not_backfilled",
            "message": f"minimum KPI rows {minimum_kpi_rows}/{expected_platform_count}; fill or verified-zero site_clicks, quiz_starts, quiz_completions.",
            "release": "Every first-batch platform row has checked minimum KPI values.",
        })
    if first_batch_published and not publishing_ready:
        blockers.append({
            "id": "publishing_status_not_ready",
            "message": "publishing-status has not opened weekly decision even though first batch may be published.",
            "release": "Run promotion_daily_ops_refresh.py and resolve publishing-status warnings.",
        })

    issues: list[str] = []
    if len(rows) != expected_platform_count:
        issues.append(f"expected {expected_platform_count} first-batch rows, got {len(rows)}")
    if published_rows > expected_platform_count:
        issues.append("publishedRows cannot exceed expected platform count")
    if minimum_kpi_rows > expected_platform_count:
        issues.append("minimumKpiRows cannot exceed expected platform count")
    if traceable_post_evidence > published_rows and published_rows:
        issues.append("traceable post evidence should not exceed published first-batch rows")
    if first_batch_published and not row_shape_complete:
        issues.append("published first-batch rows should expose minimumKpis for all required fields")
    if ready_for_weekly_review and blockers:
        issues.append("readyForWeeklyReview cannot be true while blockers exist")

    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "firstBatchPacket": str(FIRST_BATCH_PACKET.relative_to(ROOT)),
            "evidenceLedger": str(EVIDENCE_LEDGER.relative_to(ROOT)),
            "publishingStatus": str(PUBLISHING_STATUS.relative_to(ROOT)),
            "attributionReconciliation": str(KPI_CONSISTENCY.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "expectedRows": expected_platform_count,
            "publishedRows": published_rows,
            "minimumKpiRows": minimum_kpi_rows,
            "traceablePostEvidence": traceable_post_evidence,
            "genericPostEvidence": generic_post_evidence,
            "missingPostEvidence": missing_post_evidence,
            "attributionFilledRows": attribution_filled_rows,
            "blockers": len(blockers),
            "issues": len(issues),
        },
        "state": {
            "firstBatchPublished": first_batch_published,
            "evidenceComplete": evidence_complete,
            "minimumKpiComplete": minimum_kpi_complete,
            "publishingStatusReady": publishing_ready,
            "readyForWeeklyReview": ready_for_weekly_review,
            "emptyDataMode": minimum_kpi_rows == 0,
        },
        "nextAction": (
            "Run weekly review and week decision gates."
            if ready_for_weekly_review
            else "Publish first-batch posts, write back real post URLs, then fill or verified-zero minimum KPI."
        ),
        "minimumKpiFields": list(MINIMUM_KPI_FIELDS),
        "blockers": blockers,
        "issues": issues,
    }


def render_markdown(gate: dict) -> str:
    metrics = gate["metrics"]
    state = gate["state"]
    lines = [
        "# LoveTypes First Batch Completion Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- first batch published：{metrics['publishedRows']} / {metrics['expectedRows']}",
        f"- minimum KPI rows：{metrics['minimumKpiRows']} / {metrics['expectedRows']}",
        f"- traceable post evidence：{metrics['traceablePostEvidence']} / {metrics['publishedRows']}",
        f"- generic / missing evidence：{metrics['genericPostEvidence']} / {metrics['missingPostEvidence']}",
        f"- ready for weekly review：{int(state['readyForWeeklyReview'])}",
        f"- blockers：{metrics['blockers']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Required Minimum KPI",
        "",
    ]
    lines.extend(f"- `{field}`" for field in gate["minimumKpiFields"])
    lines.extend([
        "",
        "## State",
        "",
        f"- firstBatchPublished：`{int(state['firstBatchPublished'])}`",
        f"- evidenceComplete：`{int(state['evidenceComplete'])}`",
        f"- minimumKpiComplete：`{int(state['minimumKpiComplete'])}`",
        f"- publishingStatusReady：`{int(state['publishingStatusReady'])}`",
        f"- emptyDataMode：`{int(state['emptyDataMode'])}`",
        "",
        "## Next Action",
        "",
        f"- {gate['nextAction']}",
        "",
        "## Blockers",
        "",
    ])
    if gate["blockers"]:
        for blocker in gate["blockers"]:
            lines.append(f"- `{blocker['id']}`：{blocker['message']} 解除條件：{blocker['release']}")
    else:
        lines.append("- 無。")
    if gate["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in gate["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(gate: dict) -> None:
    JSON_OUTPUT.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(render_markdown(gate), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether first-batch publication has enough evidence and KPI for weekly review.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    args = parser.parse_args()

    gate = build_gate()
    if not args.check:
        write_outputs(gate)
        print(f"promotion_first_batch_completion_gate={MD_OUTPUT}")
        print(f"promotion_first_batch_completion_gate_json={JSON_OUTPUT}")
    metrics = gate["metrics"]
    state = gate["state"]
    print(f"promotion_first_batch_completion_rows={metrics['rows']}")
    print(f"promotion_first_batch_completion_published={metrics['publishedRows']}")
    print(f"promotion_first_batch_completion_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_first_batch_completion_traceable_evidence={metrics['traceablePostEvidence']}")
    print(f"promotion_first_batch_completion_generic_evidence={metrics['genericPostEvidence']}")
    print(f"promotion_first_batch_completion_missing_evidence={metrics['missingPostEvidence']}")
    print(f"promotion_first_batch_completion_ready_for_weekly={int(state['readyForWeeklyReview'])}")
    print(f"promotion_first_batch_completion_blockers={metrics['blockers']}")
    print(f"promotion_first_batch_completion_issues={metrics['issues']}")
    for issue in gate["issues"]:
        print(issue)
    return 1 if gate["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
