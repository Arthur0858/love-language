#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
IDENTITY = PROMOTION_DIR / "platform-account-identity-checklist.json"
PROFILE_PROOF = PROMOTION_DIR / "profile-proof-readiness-pack.json"
FIRST_BATCH = PROMOTION_DIR / "first-batch-publication-packet.json"
EVIDENCE_MATRIX = PROMOTION_DIR / "first-batch-evidence-matrix.json"
POST_OPS = PROMOTION_DIR / "post-ops-readiness-pack.json"
EMPTY_DATA = PROMOTION_DIR / "weekly-review-packet.json"
OUTPUT_MD = PROMOTION_DIR / "launch-exception-runbook.md"
OUTPUT_JSON = PROMOTION_DIR / "launch-exception-runbook.json"
OUTPUT_CSV = PROMOTION_DIR / "launch-exception-runbook.csv"


EXCEPTIONS = [
    {
        "id": "wrong_platform_account",
        "phase": "profile_setup",
        "severity": "stop",
        "trigger": "Visible account, channel, public profile, or edit permission does not match the intended LoveTypes platform identity.",
        "stop": "Do not set profile link, do not publish, and do not write back profile status.",
        "recovery": "Switch to the correct account, rerun platform account identity checklist, then capture a traceable proof note.",
        "source": "platform-account-identity-checklist.json",
    },
    {
        "id": "profile_link_wrong_or_missing",
        "phase": "profile_setup",
        "severity": "stop",
        "trigger": "Profile link is not the planned /start/ UTM URL, is missing, or cannot be clicked from the public profile.",
        "stop": "Do not mark profile set/live and do not publish first-batch posts.",
        "recovery": "Fix the profile link, verify it opens lovetypes.tw/start/ with UTM preserved, then run profile text import check/add.",
        "source": "profile-proof-readiness-pack.json",
    },
    {
        "id": "publish_before_profile_gate",
        "phase": "publish_first_batch",
        "severity": "stop",
        "trigger": "A first-batch post is about to publish while ready_to_publish is false.",
        "stop": "Cancel or leave draft/scheduled; do not publish manually around the gate.",
        "recovery": "Complete all three profile rows, refresh launch readiness, then use the first-batch publish action sheet.",
        "source": "first-batch-publication-packet.json",
    },
    {
        "id": "post_not_public",
        "phase": "post_url_writeback",
        "severity": "hold",
        "trigger": "Post URL exists but is private, draft-only, login-only, or not reachable from a public browser.",
        "stop": "Do not write back post_url as published and do not count KPI.",
        "recovery": "Make the post public or replace with the correct public URL, then rerun public-post-url checks.",
        "source": "first-batch-evidence-matrix.json",
    },
    {
        "id": "wrong_post_url_or_platform",
        "phase": "post_url_writeback",
        "severity": "stop",
        "trigger": "Post URL domain does not match YouTube/TikTok/Instagram platform row, or URL points to the wrong post.",
        "stop": "Do not write back; do not reuse the URL in weekly review.",
        "recovery": "Find the correct public post URL for the platform row and rerun post text import check.",
        "source": "first-batch-evidence-matrix.json",
    },
    {
        "id": "paid_cta_or_affiliate_first_touch",
        "phase": "publish_first_batch",
        "severity": "stop",
        "trigger": "Caption/profile first action emphasizes Luna, affiliate books, paid products, or purchase before the quiz.",
        "stop": "Do not publish, or edit immediately before public verification/writeback.",
        "recovery": "Restore the single primary CTA: complete the 15-question quiz and find the emotional guardian.",
        "source": "first-batch-publication-packet.json",
    },
    {
        "id": "zero_kpi_without_source",
        "phase": "kpi_backfill",
        "severity": "hold",
        "trigger": "site_clicks, quiz_starts, or quiz_completions is entered as 0 without a checked analytics/platform source.",
        "stop": "Do not run weekly review and do not change commerce or content priority.",
        "recovery": "Check analytics source, add proof note, then rerun zero KPI evidence checklist.",
        "source": "post-ops-readiness-pack.json",
    },
    {
        "id": "duplicate_or_wrong_slot_post",
        "phase": "publish_first_batch",
        "severity": "hold",
        "trigger": "Same platform receives a duplicate first-batch post, wrong script, wrong slot, or wrong guardian.",
        "stop": "Do not write back as the planned task until operator decides keep/delete/repost.",
        "recovery": "If keeping, document exact task mapping; if deleting/reposting, only write back the final public post URL.",
        "source": "first-batch-publication-packet.json",
    },
    {
        "id": "unsafe_or_crisis_comment",
        "phase": "comment_or_lead_triage",
        "severity": "escalate",
        "trigger": "Comment/email asks for crisis support, diagnosis, therapy replacement, or sensitive personal data handling.",
        "stop": "Do not treat as promotion KPI or product lead.",
        "recovery": "Use safety-bounded reply; direct to appropriate emergency/local professional support where relevant.",
        "source": "weekly-review-packet.json",
    },
    {
        "id": "empty_data_commerce_change",
        "phase": "weekly_review",
        "severity": "stop",
        "trigger": "Offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian is changed while empty-data mode is true.",
        "stop": "Revert the commerce/content-priority change and keep collect_signal focus.",
        "recovery": "Wait until first-batch evidence, KPI rows, weekly review and decision gates are ready.",
        "source": "weekly-review-packet.json",
    },
]


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_runbook() -> dict:
    identity = load_json(IDENTITY)
    profile = load_json(PROFILE_PROOF)
    first = load_json(FIRST_BATCH)
    matrix = load_json(EVIDENCE_MATRIX)
    post_ops = load_json(POST_OPS)
    weekly = load_json(EMPTY_DATA)
    context = {
        "identityPendingRows": int(identity.get("metrics", {}).get("pendingRows", 0) or 0),
        "profileConfigured": int(profile.get("metrics", {}).get("configured", 0) or 0),
        "profileProofRows": int(profile.get("metrics", {}).get("rows", 0) or 0),
        "profileProofRealReadyRows": int(profile.get("metrics", {}).get("realProofReadyRows", 0) or 0),
        "profileProofPlaceholderRows": int(profile.get("metrics", {}).get("placeholderProofRows", 0) or 0),
        "readyToPublish": 1 if first.get("readyToPublish") else 0,
        "firstBatchPublished": int(first.get("publishedRows", 0) or 0),
        "evidenceReadyWeekly": int(matrix.get("metrics", {}).get("readyForWeeklyReview", 0) or 0),
        "postOpsReadyWeekly": int(post_ops.get("metrics", {}).get("readyForWeeklyReview", 0) or 0),
        "emptyDataMode": 1 if weekly.get("state", {}).get("emptyDataMode") else 0,
    }
    context["externalProfileProofBlockers"] = max(
        0,
        context["profileProofRows"] - context["profileProofRealReadyRows"],
    )
    rows = []
    for item in EXCEPTIONS:
        rows.append({
            **item,
            "status": "armed",
            "operatorAction": "If trigger appears, follow stop condition first, then recovery condition.",
        })
    severity_counts = Counter(row["severity"] for row in rows)
    metrics = {
        "rows": len(rows),
        "stopRows": severity_counts["stop"],
        "holdRows": severity_counts["hold"],
        "escalateRows": severity_counts["escalate"],
        **context,
    }
    issues = validate(rows, metrics)
    return {
        "generatedAt": today(),
        "sources": {
            "platformAccountIdentityChecklist": str(IDENTITY.relative_to(ROOT)),
            "profileProofReadinessPack": str(PROFILE_PROOF.relative_to(ROOT)),
            "firstBatchPublicationPacket": str(FIRST_BATCH.relative_to(ROOT)),
            "firstBatchEvidenceMatrix": str(EVIDENCE_MATRIX.relative_to(ROOT)),
            "postOpsReadinessPack": str(POST_OPS.relative_to(ROOT)),
            "weeklyReviewPacket": str(EMPTY_DATA.relative_to(ROOT)),
        },
        "policy": {
            "stopBeforeWriteback": True,
            "doNotDeleteWithoutOperatorDecision": True,
            "doNotCountUnsafeRequestsAsLeads": True,
            "emptyDataCommerceChangesBlocked": True,
        },
        "metrics": metrics,
        "rows": rows,
        "issues": issues,
    }


def validate(rows: list[dict[str, str]], metrics: dict[str, int]) -> list[str]:
    issues: list[str] = []
    if metrics["rows"] != 10:
        issues.append(f"expected 10 launch exception rows, got {metrics['rows']}")
    if metrics["stopRows"] < 5:
        issues.append("runbook should include at least five hard stop exceptions")
    if metrics["escalateRows"] < 1:
        issues.append("runbook should include a safety escalation exception")
    for row in rows:
        label = row.get("id", "<exception>")
        for field in ("id", "phase", "severity", "trigger", "stop", "recovery", "source", "operatorAction"):
            if not row.get(field):
                issues.append(f"{label}: missing {field}")
        if row.get("severity") not in {"stop", "hold", "escalate"}:
            issues.append(f"{label}: invalid severity")
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        issues.append("exception IDs must be unique")
    if metrics["emptyDataMode"] and not any(row["id"] == "empty_data_commerce_change" for row in rows):
        issues.append("empty-data mode must include commerce-change exception")
    if metrics["profileConfigured"] < 3 and metrics.get("externalProfileProofBlockers", 0) < 1:
        issues.append("profile setup exception context should expose external profile proof blockers")
    return issues


def render_markdown(runbook: dict) -> str:
    metrics = runbook["metrics"]
    lines = [
        "# LoveTypes Launch Exception Runbook",
        "",
        f"- 產生日期：{runbook['generatedAt']}",
        f"- exception rows：{metrics['rows']}",
        f"- hard stops：{metrics['stopRows']}",
        f"- holds：{metrics['holdRows']}",
        f"- escalations：{metrics['escalateRows']}",
        f"- profile configured：{metrics['profileConfigured']}",
        f"- real profile proof ready：{metrics['profileProofRealReadyRows']} / {metrics['profileProofRows']}",
        f"- placeholder proof rows：{metrics['profileProofPlaceholderRows']}",
        f"- external profile proof blockers：{metrics['externalProfileProofBlockers']}",
        f"- ready to publish：{metrics['readyToPublish']}",
        f"- first batch published：{metrics['firstBatchPublished']}",
        f"- empty data mode：{metrics['emptyDataMode']}",
        f"- issues：{len(runbook['issues'])}",
        "",
        "## Rule",
        "",
        "- 異常先停手，再回填；不要用修正後的意圖覆蓋原始證據缺口。",
        "- 錯帳號、錯 URL、錯 CTA、未驗證 KPI 都不能進週回顧。",
        "- 危機、診斷、諮商替代或敏感個資需求不當成推廣 lead。",
        "- 空資料時不改商品排序、付費 CTA、Luna / 聯盟優先序或勝出守護者。",
        "",
        "## Exceptions",
        "",
    ]
    for row in runbook["rows"]:
        lines.extend([
            f"### `{row['id']}`",
            "",
            f"- phase：`{row['phase']}`",
            f"- severity：`{row['severity']}`",
            f"- trigger：{row['trigger']}",
            f"- stop：{row['stop']}",
            f"- recovery：{row['recovery']}",
            f"- source：`{row['source']}`",
            "",
        ])
    if runbook["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in runbook["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(runbook: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(runbook), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(runbook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fieldnames = ["id", "phase", "severity", "status", "trigger", "stop", "recovery", "source", "operatorAction"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in runbook["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fail-closed exception runbook for LoveTypes launch operations.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    runbook = build_runbook()
    metrics = runbook["metrics"]
    if not args.check:
        write_outputs(runbook)
        print(f"promotion_launch_exception_runbook={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_launch_exception_runbook_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_launch_exception_runbook_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_launch_exception_rows={metrics['rows']}")
    print(f"promotion_launch_exception_stop_rows={metrics['stopRows']}")
    print(f"promotion_launch_exception_hold_rows={metrics['holdRows']}")
    print(f"promotion_launch_exception_escalate_rows={metrics['escalateRows']}")
    print(f"promotion_launch_exception_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_launch_exception_profile_proof_real_ready={metrics['profileProofRealReadyRows']}")
    print(f"promotion_launch_exception_profile_proof_placeholder_rows={metrics['profileProofPlaceholderRows']}")
    print(f"promotion_launch_exception_external_profile_proof_blockers={metrics['externalProfileProofBlockers']}")
    print(f"promotion_launch_exception_ready_to_publish={metrics['readyToPublish']}")
    print(f"promotion_launch_exception_first_batch_published={metrics['firstBatchPublished']}")
    print(f"promotion_launch_exception_empty_data_mode={metrics['emptyDataMode']}")
    print(f"promotion_launch_exception_issues={len(runbook['issues'])}")
    for issue in runbook["issues"]:
        print(issue)
    return 1 if runbook["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
