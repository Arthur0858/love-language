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
PUBLIC_URL = PROMOTION_DIR / "public-post-url-checklist.json"
ZERO_KPI = PROMOTION_DIR / "zero-kpi-evidence-checklist.json"
KPI_ACTION = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
WRITEBACK = PROMOTION_DIR / "post-writeback-playbook.json"
COMPLETION = PROMOTION_DIR / "first-batch-completion-gate.json"
OUTPUT_MD = PROMOTION_DIR / "post-ops-readiness-pack.md"
OUTPUT_JSON = PROMOTION_DIR / "post-ops-readiness-pack.json"
OUTPUT_CSV = PROMOTION_DIR / "post-ops-readiness-pack.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def grouped_status(items: list[dict], key_fields: tuple[str, str]) -> dict[tuple[str, str], Counter[str]]:
    grouped: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for item in items:
        key = tuple(str(item.get(field, "")) for field in key_fields)
        grouped[key][str(item.get("operator_status", ""))] += 1
    return grouped


def build_pack() -> dict:
    public = load_json(PUBLIC_URL)
    zero = load_json(ZERO_KPI)
    kpi_action = load_json(KPI_ACTION)
    writeback = load_json(WRITEBACK)
    completion = load_json(COMPLETION)
    public_grouped = grouped_status(public.get("items", []), ("platform", "task_id"))
    zero_grouped = grouped_status(zero.get("items", []), ("platform", "task_id"))
    kpi_rows = {
        (str(row.get("platform", "")), str(row.get("task_id", ""))): row
        for row in kpi_action.get("rows", [])
        if isinstance(row, dict)
    }
    rows: list[dict[str, str]] = []
    for first in writeback.get("firstBatch", []):
        platform = str(first.get("platform", ""))
        task_id = str(first.get("taskId", ""))
        key = (platform, task_id)
        public_counts = public_grouped.get(key, Counter())
        zero_counts = zero_grouped.get(key, Counter())
        kpi = kpi_rows.get(key, {})
        published = str(kpi.get("published", "0")) in {"1", "true", "True"}
        post_url = str(kpi.get("post_url", ""))
        public_ready = public_counts.get("complete", 0) >= 4 and public_counts.get("pending_publish", 0) == 0
        zero_ready = zero_counts.get("complete", 0) == 3
        if not published:
            status = "blocked_until_post_url"
        elif not public_ready:
            status = "needs_public_url_verification"
        elif not zero_ready:
            status = "needs_kpi_source_proof"
        else:
            status = "ready_for_weekly_review"
        rows.append({
            "platform": platform,
            "task_id": task_id,
            "script_id": str(first.get("scriptId", "")),
            "title": str(first.get("title", "")),
            "status": status,
            "published": "1" if published else "0",
            "post_url": post_url,
            "public_pending": str(public_counts.get("pending_publish", 0)),
            "public_complete": str(public_counts.get("complete", 0)),
            "public_operator_verify": str(public_counts.get("operator_verify", 0)),
            "zero_pending": str(zero_counts.get("pending_publish", 0)),
            "zero_needs_source": str(zero_counts.get("needs_source_proof", 0)),
            "zero_complete": str(zero_counts.get("complete", 0)),
            "kpi_command": str(kpi.get("kpi_command", "")),
            "next_action": (
                "Publish the post and replace the placeholder URL with a real public post URL."
                if status == "blocked_until_post_url"
                else "Verify public URL and CTA from a public browser."
                if status == "needs_public_url_verification"
                else "Attach checked-source proof for site_clicks, quiz_starts and quiz_completions."
                if status == "needs_kpi_source_proof"
                else "Run weekly summary and decision evidence checklist."
            ),
        })
    metrics = {
        "rows": len(rows),
        "published": sum(1 for row in rows if row["published"] == "1"),
        "blocked": sum(1 for row in rows if row["status"].startswith("blocked")),
        "needsPublicVerification": sum(1 for row in rows if row["status"] == "needs_public_url_verification"),
        "needsKpiSourceProof": sum(1 for row in rows if row["status"] == "needs_kpi_source_proof"),
        "readyForWeeklyReview": sum(1 for row in rows if row["status"] == "ready_for_weekly_review"),
        "publicPendingRows": int(public.get("metrics", {}).get("pendingPublishRows", 0) or 0),
        "zeroPendingRows": int(zero.get("metrics", {}).get("pendingPublishRows", 0) or 0),
        "completionReady": 1 if completion.get("state", {}).get("readyForWeekly") else 0,
    }
    issues: list[str] = []
    if metrics["rows"] != 3:
        issues.append(f"expected 3 post ops rows, got {metrics['rows']}")
    if metrics["published"] == 0 and metrics["readyForWeeklyReview"] != 0:
        issues.append("cannot be ready for weekly review before any first-batch posts are published")
    if metrics["blocked"] and metrics["publicPendingRows"] == 0:
        issues.append("blocked post rows should correspond to pending public URL rows")
    if metrics["completionReady"] and metrics["readyForWeeklyReview"] != metrics["rows"]:
        issues.append("completion gate cannot be ready unless all post ops rows are ready")
    return {
        "generatedAt": today(),
        "sources": {
            "publicPostUrlChecklist": str(PUBLIC_URL.relative_to(ROOT)),
            "zeroKpiEvidenceChecklist": str(ZERO_KPI.relative_to(ROOT)),
            "firstBatchKpiActionSheet": str(KPI_ACTION.relative_to(ROOT)),
            "postWritebackPlaybook": str(WRITEBACK.relative_to(ROOT)),
            "firstBatchCompletionGate": str(COMPLETION.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Post URL writeback comes before KPI interpretation.",
            "A placeholder URL must never pass public URL verification.",
            "Zero KPI values are valid only with checked-source proof.",
            "Weekly review stays closed until all three first-batch rows pass URL and KPI evidence checks.",
        ],
        "issues": issues,
    }


def render_markdown(pack: dict) -> str:
    metrics = pack["metrics"]
    lines = [
        "# LoveTypes Post Ops Readiness Pack",
        "",
        f"- 產生日期：{pack['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- published：{metrics['published']}",
        f"- blocked：{metrics['blocked']}",
        f"- needs public verification：{metrics['needsPublicVerification']}",
        f"- needs KPI source proof：{metrics['needsKpiSourceProof']}",
        f"- ready for weekly review：{metrics['readyForWeeklyReview']}",
        f"- public pending rows：{metrics['publicPendingRows']}",
        f"- zero KPI pending rows：{metrics['zeroPendingRows']}",
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
            f"- status：`{row['status']}`",
            f"- script：`{row['script_id']}`",
            f"- title：{row['title']}",
            f"- published：{row['published']}",
            f"- post URL：{row['post_url'] or '(pending)'}",
            f"- public complete / pending / verify：{row['public_complete']} / {row['public_pending']} / {row['public_operator_verify']}",
            f"- zero complete / pending / needs source：{row['zero_complete']} / {row['zero_pending']} / {row['zero_needs_source']}",
            f"- next：{row['next_action']}",
            f"- KPI command：`{row['kpi_command']}`",
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
        "title",
        "status",
        "published",
        "post_url",
        "public_pending",
        "public_complete",
        "public_operator_verify",
        "zero_pending",
        "zero_needs_source",
        "zero_complete",
        "next_action",
        "kpi_command",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in pack["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a post URL and starter KPI readiness pack.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    pack = build_pack()
    metrics = pack["metrics"]
    if not args.check:
        write_outputs(pack)
        print(f"promotion_post_ops_readiness_pack={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_post_ops_readiness_pack_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_post_ops_readiness_pack_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_post_ops_readiness_rows={metrics['rows']}")
    print(f"promotion_post_ops_readiness_published={metrics['published']}")
    print(f"promotion_post_ops_readiness_blocked={metrics['blocked']}")
    print(f"promotion_post_ops_readiness_needs_public_verification={metrics['needsPublicVerification']}")
    print(f"promotion_post_ops_readiness_needs_kpi_source_proof={metrics['needsKpiSourceProof']}")
    print(f"promotion_post_ops_readiness_ready_weekly={metrics['readyForWeeklyReview']}")
    print(f"promotion_post_ops_readiness_public_pending_rows={metrics['publicPendingRows']}")
    print(f"promotion_post_ops_readiness_zero_pending_rows={metrics['zeroPendingRows']}")
    print(f"promotion_post_ops_readiness_completion_ready={metrics['completionReady']}")
    print(f"promotion_post_ops_readiness_issues={len(pack['issues'])}")
    for issue in pack["issues"]:
        print(issue)
    return 1 if pack["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
