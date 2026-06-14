#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KPI_ACTION = PROMOTION_DIR / "first-batch-kpi-action-sheet.json"
ZERO_EVIDENCE = PROMOTION_DIR / "zero-kpi-evidence-checklist.json"
PUBLISH_KPI_HANDOFF = PROMOTION_DIR / "publish-kpi-handoff.json"
WEEKLY_REVIEW = PROMOTION_DIR / "weekly-review-packet.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-kpi-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-kpi-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "first-batch-kpi-quickstart.txt"
REQUIRED_PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
MINIMUM_KPIS = ("site_clicks", "quiz_starts", "quiz_completions")
POST_URL_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def rows_by_platform(payload: dict) -> dict[str, dict]:
    return {str(row.get("platform", "")): row for row in payload.get("rows", []) if row.get("platform")}


def zero_rows_by_platform(payload: dict) -> dict[str, list[dict]]:
    grouped = {platform: [] for platform in REQUIRED_PLATFORMS}
    for row in payload.get("items", []):
        platform = str(row.get("platform", ""))
        if platform in grouped:
            grouped[platform].append(row)
    return grouped


def metric(payload: dict, key: str) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return 0
    try:
        return int(values.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def proof_template(row: dict) -> str:
    platform = str(row.get("platform", ""))
    task_id = str(row.get("task_id", ""))
    return "\n".join([
        "LoveTypes platform post writeback",
        f"platform: {platform}",
        f"task_id: {task_id}",
        "status: published",
        f"published_date: {today()}",
        f"post_url: {POST_URL_PLACEHOLDERS.get(platform, '<REAL_POST_URL>')}",
        "site_clicks: <CHECKED_SITE_CLICKS>",
        "quiz_starts: <CHECKED_QUIZ_STARTS>",
        "quiz_completions: <CHECKED_QUIZ_COMPLETIONS>",
        f"proof_note: analytics source checked {today()} for {platform}/{task_id}",
    ])


def build_quickstart() -> dict:
    action = read_json(KPI_ACTION)
    zero_evidence = read_json(ZERO_EVIDENCE)
    handoff = read_json(PUBLISH_KPI_HANDOFF)
    weekly = read_json(WEEKLY_REVIEW)
    action_rows = rows_by_platform(action)
    zero_rows = zero_rows_by_platform(zero_evidence)
    rows: list[dict] = []

    for platform in REQUIRED_PLATFORMS:
        row = action_rows.get(platform, {})
        checks = [
            {
                "metric": str(item.get("metric_id", "")),
                "status": str(item.get("operator_status", "")),
                "source": str(item.get("required_source") or item.get("source_required", "")),
                "value": str(item.get("value", "0")),
            }
            for item in zero_rows.get(platform, [])
            if item.get("metric_id") in MINIMUM_KPIS
        ]
        published = str(row.get("published", "0")) == "1"
        action_status = str(row.get("action_status", ""))
        rows.append({
            "platform": platform,
            "taskId": str(row.get("task_id", "")),
            "scriptId": str(row.get("script_id", "")),
            "guardianId": str(row.get("guardian_id", "")),
            "actionStatus": action_status,
            "readyForKpi": bool(published and action_status == "ready_for_kpi_source_check"),
            "published": int(published),
            "postUrl": str(row.get("post_url", "")),
            "minimumKpis": list(MINIMUM_KPIS),
            "zeroSourceRows": int(row.get("zero_source_rows", 0) or 0),
            "zeroChecks": checks,
            "proofTemplate": proof_template(row),
            "writeCommand": str(row.get("kpi_command", "")),
            "blockedBy": str(row.get("blocked_by", "")) or ("first-batch post is not published" if not published else ""),
            "stopCondition": (
                "Stop if the post URL is not public HTTPS, analytics source was not checked, "
                "or a zero value lacks source proof."
            ),
        })

    issues = validate(rows)
    return {
        "generatedAt": today(),
        "sources": {
            "firstBatchKpiAction": str(KPI_ACTION.relative_to(ROOT)),
            "zeroKpiEvidence": str(ZERO_EVIDENCE.relative_to(ROOT)),
            "publishKpiHandoff": str(PUBLISH_KPI_HANDOFF.relative_to(ROOT)),
            "weeklyReview": str(WEEKLY_REVIEW.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "readyForKpi": sum(1 for row in rows if row["readyForKpi"]),
            "blockedRows": sum(1 for row in rows if not row["readyForKpi"]),
            "publishedRows": sum(int(row["published"]) for row in rows),
            "zeroSourceRows": sum(int(row["zeroSourceRows"]) for row in rows),
            "handoffReadyForWeekly": metric(handoff, "readyForWeeklyReview"),
            "weeklyReady": 1 if weekly.get("state", {}).get("readyForWeeklyDecision") else 0,
            "emptyDataMode": 1 if weekly.get("state", {}).get("emptyDataMode") else 0,
            "issues": len(issues),
        },
        "rules": [
            "Do not run KPI writeback until the platform post has a real public HTTPS post URL.",
            "A zero KPI value is valid only after checking the named analytics source.",
            "Minimum KPI fields are site_clicks, quiz_starts, and quiz_completions.",
            "Weekly review and commerce decisions remain locked until all first-batch minimum KPIs are written back.",
            "Do not use guesses, private drafts, scheduled URLs, or placeholder post URLs.",
        ],
        "rows": rows,
        "issues": issues,
    }


def validate(rows: list[dict]) -> list[str]:
    issues: list[str] = []
    seen = {row.get("platform") for row in rows}
    if seen != set(REQUIRED_PLATFORMS):
        issues.append("first-batch KPI quickstart must include YouTube Shorts, TikTok, and Instagram Reels")
    for row in rows:
        label = f"{row.get('platform', '<platform>')}/{row.get('taskId', '<task>')}"
        checks = row.get("zeroChecks", [])
        if len(checks) != len(MINIMUM_KPIS):
            issues.append(f"{label}: expected three zero-source checks")
        check_metrics = {item.get("metric") for item in checks}
        if check_metrics != set(MINIMUM_KPIS):
            issues.append(f"{label}: zero-source checks must cover minimum KPIs")
        if row.get("readyForKpi") and not str(row.get("postUrl", "")).startswith("https://"):
            issues.append(f"{label}: ready KPI row needs real HTTPS post URL")
        if not row.get("readyForKpi") and not row.get("blockedBy"):
            issues.append(f"{label}: blocked KPI row should explain blocker")
        proof = str(row.get("proofTemplate", ""))
        if "<CHECKED_SITE_CLICKS>" not in proof or "<CHECKED_QUIZ_STARTS>" not in proof or "<CHECKED_QUIZ_COMPLETIONS>" not in proof:
            issues.append(f"{label}: proof template must force checked KPI values")
        command = str(row.get("writeCommand", ""))
        if "site-clicks" not in command or "quiz-starts" not in command or "quiz-completions" not in command:
            issues.append(f"{label}: write command must include minimum KPI flags")
        if row.get("published") and "<REAL_" in command:
            issues.append(f"{label}: published KPI command must not contain placeholder URL")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes First Batch KPI Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready for KPI：{metrics['readyForKpi']}",
        f"- blocked rows：{metrics['blockedRows']}",
        f"- published rows：{metrics['publishedRows']}",
        f"- zero-source rows：{metrics['zeroSourceRows']}",
        f"- weekly ready：{metrics['weeklyReady']}",
        f"- empty data mode：{metrics['emptyDataMode']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    for row in data["rows"]:
        lines.extend([
            "",
            f"## {row['platform']} · `{row['taskId']}`",
            "",
            f"- action status：`{row['actionStatus']}`",
            f"- ready for KPI：`{1 if row['readyForKpi'] else 0}`",
            f"- published：`{row['published']}`",
            f"- post URL：{row['postUrl'] or '(not published)'}",
            f"- blocked by：{row['blockedBy'] or '(none)'}",
            f"- minimum KPIs：`{', '.join(row['minimumKpis'])}`",
            f"- zero-source rows：{row['zeroSourceRows']}",
            "",
            "Zero-source checks:",
            "",
        ])
        for check in row["zeroChecks"]:
            lines.append(f"- `{check['metric']}`：status `{check['status']}`；source：{check['source']}")
        lines.extend([
            "",
            "Proof text after analytics source is checked:",
            "",
            "```text",
            row["proofTemplate"],
            "```",
            "",
            f"- write：`{row['writeCommand']}`",
            f"- stop：{row['stopCondition']}",
        ])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    lines = [
        "LoveTypes first batch KPI quickstart",
        f"generated: {data['generatedAt']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    for row in data["rows"]:
        lines.extend([
            "",
            f"=== {row['platform']} / {row['taskId']} ===",
            f"ready for KPI: {1 if row['readyForKpi'] else 0}",
            f"published: {row['published']}",
            f"post URL: {row['postUrl'] or '(not published)'}",
            f"blocked by: {row['blockedBy'] or '(none)'}",
            "",
            "ZERO-SOURCE CHECKS:",
        ])
        for check in row["zeroChecks"]:
            lines.append(f"- {check['metric']}: {check['status']} | {check['source']}")
        lines.extend([
            "",
            "PROOF TEXT AFTER ANALYTICS CHECK:",
            row["proofTemplate"],
            "",
            f"WRITE: {row['writeCommand']}",
            f"STOP: {row['stopCondition']}",
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
    parser = argparse.ArgumentParser(description="Build a first-batch KPI quickstart packet for LoveTypes promotion launch.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_first_batch_kpi_quickstart={args.output}")
        print(f"promotion_first_batch_kpi_quickstart_json={args.json_output}")
        print(f"promotion_first_batch_kpi_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_first_batch_kpi_quickstart_rows={metrics['rows']}")
    print(f"promotion_first_batch_kpi_quickstart_ready_for_kpi={metrics['readyForKpi']}")
    print(f"promotion_first_batch_kpi_quickstart_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_first_batch_kpi_quickstart_published_rows={metrics['publishedRows']}")
    print(f"promotion_first_batch_kpi_quickstart_zero_source_rows={metrics['zeroSourceRows']}")
    print(f"promotion_first_batch_kpi_quickstart_weekly_ready={metrics['weeklyReady']}")
    print(f"promotion_first_batch_kpi_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
