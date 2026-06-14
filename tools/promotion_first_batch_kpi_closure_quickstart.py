#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KPI_QUICKSTART = PROMOTION_DIR / "first-batch-kpi-quickstart.json"
ZERO_EVIDENCE = PROMOTION_DIR / "zero-kpi-evidence-checklist.json"
KPI_ACTION = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
POST_OPS = PROMOTION_DIR / "post-ops-readiness-pack.json"
COMPLETION_GATE = PROMOTION_DIR / "first-batch-completion-gate.json"
PUBLISH_KPI_HANDOFF = PROMOTION_DIR / "publish-kpi-handoff.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-kpi-closure-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-kpi-closure-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "first-batch-kpi-closure-quickstart.txt"
MINIMUM_KPIS = ("site_clicks", "quiz_starts", "quiz_completions")


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def metric(payload: dict, key: str) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return 0
    try:
        return int(values.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def state_bool(payload: dict, key: str) -> bool:
    state = payload.get("state", {})
    return bool(state.get(key)) if isinstance(state, dict) else False


def rows_by_platform(payload: dict) -> dict[str, dict]:
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return {}
    return {str(row.get("platform", "")): row for row in rows if isinstance(row, dict) and row.get("platform")}


def active_platforms(payload: dict) -> tuple[str, ...]:
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return ("youtube_shorts",)
    platforms = tuple(str(row.get("platform", "")) for row in rows if isinstance(row, dict) and row.get("platform"))
    return platforms or ("youtube_shorts",)


def zero_checks_by_platform(payload: dict, platforms: tuple[str, ...]) -> dict[str, list[dict]]:
    grouped = {platform: [] for platform in platforms}
    items = payload.get("items", [])
    if not isinstance(items, list):
        return grouped
    for item in items:
        if not isinstance(item, dict):
            continue
        platform = str(item.get("platform", ""))
        metric_id = str(item.get("metric_id", ""))
        if platform in grouped and metric_id in MINIMUM_KPIS:
            grouped[platform].append({
                "metric": metric_id,
                "status": str(item.get("operator_status", "")),
                "source": str(item.get("required_source", "")),
                "value": str(item.get("metric_value", "")),
                "proofNoteTemplate": str(item.get("proof_note_template", "")),
            })
    return grouped


def closure_steps(metrics: dict, platforms: tuple[str, ...]) -> list[dict[str, str]]:
    active_count = len(platforms)
    post_urls_ready = metrics["publishedRows"] == active_count
    kpi_ready = metrics["readyForKpi"] == active_count
    minimum_kpi_ready = metrics["minimumKpiRows"] == active_count
    weekly_ready = bool(metrics["weeklyReady"])
    return [
        {
            "id": "post_url_writeback_complete",
            "status": "complete" if post_urls_ready else "current_blocker",
            "command": "python3 tools/promotion_first_batch_publish_closure_quickstart.py --check && python3 tools/promotion_post_ops_readiness_pack.py --check",
            "release": "All active first-batch posts have real public HTTPS post_url values.",
            "stop": "Do not continue with KPI proof while post_url fields are blank, scheduled-only, private, or placeholders.",
        },
        {
            "id": "verify_zero_kpi_sources",
            "status": "complete" if kpi_ready else "blocked_until_public_url",
            "command": "python3 tools/promotion_zero_kpi_evidence_checklist.py --check",
            "release": "Each platform row has checked-source proof for site_clicks, quiz_starts, and quiz_completions.",
            "stop": "Do not treat zero as data until a named analytics source has actually been checked.",
        },
        {
            "id": "writeback_minimum_kpis",
            "status": "complete" if minimum_kpi_ready else "blocked_until_source_proof",
            "command": "python3 tools/promotion_post_writeback.py update ... --site-clicks <REAL_OR_CHECKED_ZERO> --quiz-starts <REAL_OR_CHECKED_ZERO> --quiz-completions <REAL_OR_CHECKED_ZERO>",
            "release": "All first-batch rows include checked minimum KPI values.",
            "stop": "Do not write estimates, drafts, or unverified copied counts.",
        },
        {
            "id": "refresh_ops_docs",
            "status": "complete" if minimum_kpi_ready else "blocked_until_kpi_writeback",
            "command": "python3 tools/promotion_daily_ops_refresh.py",
            "release": "Generated launch, KPI, weekly, and handoff docs reflect the written KPI rows.",
            "stop": "Do not run a decision from stale generated docs.",
        },
        {
            "id": "open_weekly_review",
            "status": "complete" if weekly_ready else "blocked_until_minimum_kpi",
            "command": "python3 tools/promotion_first_batch_completion_gate.py --check && python3 tools/promotion_weekly_review_packet.py --check",
            "release": "Weekly review is open only after publication, URL proof, and minimum KPI proof all pass.",
            "stop": "Do not make product or channel decisions while emptyDataMode is still true.",
        },
    ]


def build_closure() -> dict:
    kpi_quickstart = read_json(KPI_QUICKSTART)
    zero_evidence = read_json(ZERO_EVIDENCE)
    kpi_action = read_json(KPI_ACTION)
    post_ops = read_json(POST_OPS)
    completion = read_json(COMPLETION_GATE)
    handoff = read_json(PUBLISH_KPI_HANDOFF)
    weekly = read_json(WEEKLY_REVIEW)
    master = read_json(MASTER_GATE)

    kpi_rows = rows_by_platform(kpi_quickstart)
    action_rows = rows_by_platform(kpi_action)
    post_ops_rows = rows_by_platform(post_ops)
    platforms = active_platforms(kpi_quickstart)
    zero_checks = zero_checks_by_platform(zero_evidence, platforms)
    rows: list[dict] = []
    for platform in platforms:
        kpi = kpi_rows.get(platform, {})
        action = action_rows.get(platform, {})
        ops = post_ops_rows.get(platform, {})
        task_id = str(kpi.get("taskId") or action.get("task_id") or ops.get("task_id") or "")
        published = int(kpi.get("published", 0) or 0)
        ready_for_kpi = bool(kpi.get("readyForKpi"))
        rows.append({
            "platform": platform,
            "taskId": task_id,
            "scriptId": str(kpi.get("scriptId") or action.get("script_id") or ops.get("script_id") or ""),
            "guardianId": str(kpi.get("guardianId") or action.get("guardian_id") or ""),
            "postOpsStatus": str(ops.get("status", "")),
            "actionStatus": str(kpi.get("actionStatus") or action.get("action_status") or ""),
            "published": published,
            "readyForKpi": int(ready_for_kpi),
            "postUrl": str(kpi.get("postUrl") or action.get("post_url") or ops.get("post_url") or ""),
            "blockedBy": str(kpi.get("blockedBy") or action.get("blocked_by") or ops.get("status") or ""),
            "zeroChecks": zero_checks.get(platform, []),
            "minimumKpis": list(MINIMUM_KPIS),
            "writeCommand": str(kpi.get("writeCommand") or action.get("kpi_command") or ops.get("kpi_command") or ""),
            "proofTemplate": str(kpi.get("proofTemplate") or ""),
            "nextAction": str(ops.get("next_action") or "Publish and write back the real public post URL before KPI checks."),
        })

    metrics = {
        "rows": len(rows),
        "readyForKpi": metric(kpi_quickstart, "readyForKpi"),
        "blockedRows": metric(kpi_quickstart, "blockedRows"),
        "publishedRows": metric(kpi_quickstart, "publishedRows"),
        "zeroPendingRows": metric(zero_evidence, "pendingPublishRows"),
        "zeroNeedsSourceProofRows": metric(zero_evidence, "needsSourceProofRows"),
        "zeroSourceProofCompleteRows": metric(zero_evidence, "completeRows"),
        "zeroSourceProofMissingRows": metric(zero_evidence, "missingRows"),
        "minimumKpiRows": metric(completion, "minimumKpiRows"),
        "weeklyReady": 1 if state_bool(weekly, "readyForWeeklyDecision") else 0,
        "completionReady": 1 if state_bool(completion, "readyForWeeklyReview") else 0,
        "emptyData": 1 if state_bool(weekly, "emptyDataMode") or state_bool(completion, "emptyDataMode") else 0,
        "masterStage": str(master.get("stage", "")),
        "masterProfileConfigured": metric(master, "profileConfigured"),
        "handoffReadyForWeekly": metric(handoff, "readyForWeeklyReview"),
    }
    steps = closure_steps(metrics, platforms)
    issues = validate(rows, metrics, steps, platforms)
    metrics["issues"] = len(issues)
    return {
        "generatedAt": today(),
        "sources": {
            "firstBatchKpiQuickstart": str(KPI_QUICKSTART.relative_to(ROOT)),
            "zeroKpiEvidenceChecklist": str(ZERO_EVIDENCE.relative_to(ROOT)),
            "firstBatchKpiActionSheet": str(KPI_ACTION.relative_to(ROOT)),
            "postOpsReadinessPack": str(POST_OPS.relative_to(ROOT)),
            "firstBatchCompletionGate": str(COMPLETION_GATE.relative_to(ROOT)),
            "publishKpiHandoff": str(PUBLISH_KPI_HANDOFF.relative_to(ROOT)),
            "weeklyReviewPacket": str(WEEKLY_REVIEW.relative_to(ROOT)),
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rules": [
            "Public post URL writeback is the first gate; KPI source checks are not valid before it.",
            "Zero values are acceptable only as checked zeroes with source proof.",
            "The minimum KPI set is site_clicks, quiz_starts, and quiz_completions.",
            "Weekly review remains closed while emptyData is true.",
            "Keep commerce and product decisions locked until first-batch KPI rows exist.",
        ],
        "steps": steps,
        "rows": rows,
        "issues": issues,
    }


def validate(rows: list[dict], metrics: dict, steps: list[dict], platforms: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    active_count = len(platforms)
    if metrics["rows"] != active_count:
        issues.append(f"expected {active_count} first-batch KPI closure rows, got {metrics['rows']}")
    row_platforms = {str(row.get("platform", "")) for row in rows}
    if row_platforms != set(platforms):
        issues.append("first-batch KPI closure rows must cover all active platforms")
    if metrics["publishedRows"] == 0 and metrics["readyForKpi"] != 0:
        issues.append("readyForKpi must stay zero before public post URLs exist")
    if metrics["publishedRows"] == 0 and metrics["zeroSourceProofCompleteRows"] != 0:
        issues.append("zero source proof cannot be complete before public posts exist")
    if metrics["zeroPendingRows"] + metrics["zeroNeedsSourceProofRows"] + metrics["zeroSourceProofCompleteRows"] + metrics["zeroSourceProofMissingRows"] != active_count * len(MINIMUM_KPIS):
        issues.append("zero KPI evidence rows must partition into pending, needs-source, complete, or missing")
    if metrics["minimumKpiRows"] == 0 and metrics["weeklyReady"]:
        issues.append("weeklyReady cannot be true before minimum KPI rows exist")
    if metrics["completionReady"] and metrics["minimumKpiRows"] != active_count:
        issues.append("completionReady cannot be true until all first-batch KPI rows are complete")
    if not metrics["emptyData"] and not metrics["weeklyReady"]:
        issues.append("emptyData must stay true until weekly review is ready")
    step_ids = {step.get("id") for step in steps}
    required_steps = {
        "post_url_writeback_complete",
        "verify_zero_kpi_sources",
        "writeback_minimum_kpis",
        "refresh_ops_docs",
        "open_weekly_review",
    }
    if step_ids != required_steps:
        issues.append("closure steps must include post URL, zero proof, KPI writeback, refresh, and weekly review")
    for row in rows:
        label = f"{row.get('platform', '<platform>')}/{row.get('taskId', '<task>')}"
        checks = row.get("zeroChecks", [])
        check_metrics = {str(check.get("metric", "")) for check in checks}
        if check_metrics != set(MINIMUM_KPIS):
            issues.append(f"{label}: zero checks must cover site_clicks, quiz_starts, and quiz_completions")
        command = str(row.get("writeCommand", ""))
        if not all(flag in command for flag in ("--site-clicks", "--quiz-starts", "--quiz-completions")):
            issues.append(f"{label}: write command must include all minimum KPI flags")
        if not row.get("published") and "<REAL_" not in command:
            issues.append(f"{label}: unpublished row should keep a real URL placeholder in the write command")
        if row.get("readyForKpi") and not str(row.get("postUrl", "")).startswith("https://"):
            issues.append(f"{label}: ready KPI row needs a real HTTPS post URL")
        if not row.get("readyForKpi") and not row.get("blockedBy"):
            issues.append(f"{label}: blocked row must explain the current blocker")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes First Batch KPI Closure Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready for KPI：{metrics['readyForKpi']}",
        f"- blocked rows：{metrics['blockedRows']}",
        f"- published rows：{metrics['publishedRows']}",
        f"- zero pending rows：{metrics['zeroPendingRows']}",
        f"- zero source proof needs / complete / missing：{metrics['zeroNeedsSourceProofRows']} / {metrics['zeroSourceProofCompleteRows']} / {metrics['zeroSourceProofMissingRows']}",
        f"- minimum KPI rows：{metrics['minimumKpiRows']}",
        f"- weekly ready：{metrics['weeklyReady']}",
        f"- empty data：{metrics['emptyData']}",
        f"- master stage：`{metrics['masterStage']}`",
        f"- master profile configured：{metrics['masterProfileConfigured']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Closure Steps", ""])
    for step in data["steps"]:
        lines.extend([
            f"### `{step['id']}`",
            "",
            f"- status：`{step['status']}`",
            f"- command：`{step['command']}`",
            f"- release：{step['release']}",
            f"- stop：{step['stop']}",
            "",
        ])
    lines.extend(["## Platform Rows", ""])
    for row in data["rows"]:
        lines.extend([
            f"### {row['platform']} · `{row['taskId']}`",
            "",
            f"- status：`{row['postOpsStatus'] or row['actionStatus']}`",
            f"- published：{row['published']}",
            f"- ready for KPI：{row['readyForKpi']}",
            f"- post URL：{row['postUrl'] or '(not published)'}",
            f"- blocked by：{row['blockedBy'] or '(none)'}",
            f"- minimum KPIs：`{', '.join(row['minimumKpis'])}`",
            "",
            "Zero checks:",
            "",
        ])
        for check in row["zeroChecks"]:
            lines.append(f"- `{check['metric']}`：status `{check['status']}`；source：{check['source']}")
        lines.extend([
            "",
            "Writeback command after source proof:",
            "",
            "```text",
            row["writeCommand"],
            "```",
            "",
            "Proof template:",
            "",
            "```text",
            row["proofTemplate"] or "(available after first-batch KPI quickstart refresh)",
            "```",
            "",
            f"- next：{row['nextAction']}",
            "",
        ])
    if data["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes first batch KPI closure quickstart",
        f"generated: {data['generatedAt']}",
        f"rows: {metrics['rows']}",
        f"ready for KPI: {metrics['readyForKpi']}",
        f"published rows: {metrics['publishedRows']}",
        f"zero pending rows: {metrics['zeroPendingRows']}",
        f"zero source proof needs rows: {metrics['zeroNeedsSourceProofRows']}",
        f"zero source proof complete rows: {metrics['zeroSourceProofCompleteRows']}",
        f"zero source proof missing rows: {metrics['zeroSourceProofMissingRows']}",
        f"minimum KPI rows: {metrics['minimumKpiRows']}",
        f"weekly ready: {metrics['weeklyReady']}",
        f"empty data: {metrics['emptyData']}",
        "",
        "Closure steps:",
    ]
    for step in data["steps"]:
        lines.extend([
            "",
            f"{step['id']}: {step['status']}",
            f"command: {step['command']}",
            f"release: {step['release']}",
            f"stop: {step['stop']}",
        ])
    for row in data["rows"]:
        lines.extend([
            "",
            f"=== {row['platform']} / {row['taskId']} ===",
            f"status: {row['postOpsStatus'] or row['actionStatus']}",
            f"published: {row['published']}",
            f"ready for KPI: {row['readyForKpi']}",
            f"post URL: {row['postUrl'] or '(not published)'}",
            f"blocked by: {row['blockedBy'] or '(none)'}",
            "zero checks:",
        ])
        for check in row["zeroChecks"]:
            lines.append(f"- {check['metric']}: {check['status']} | {check['source']}")
        lines.extend([
            "writeback command after source proof:",
            row["writeCommand"],
        ])
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the first-batch KPI closure quickstart for LoveTypes promotion launch.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_closure()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_first_batch_kpi_closure_quickstart={args.output}")
        print(f"promotion_first_batch_kpi_closure_quickstart_json={args.json_output}")
        print(f"promotion_first_batch_kpi_closure_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_first_batch_kpi_closure_quickstart_rows={metrics['rows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_ready_for_kpi={metrics['readyForKpi']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_published_rows={metrics['publishedRows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_zero_pending_rows={metrics['zeroPendingRows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_zero_needs_source_proof_rows={metrics['zeroNeedsSourceProofRows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_zero_source_proof_complete_rows={metrics['zeroSourceProofCompleteRows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_zero_source_proof_missing_rows={metrics['zeroSourceProofMissingRows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_weekly_ready={metrics['weeklyReady']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_empty_data={metrics['emptyData']}")
    print(f"promotion_first_batch_kpi_closure_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
