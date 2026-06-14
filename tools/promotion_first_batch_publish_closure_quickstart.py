#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import promotion_post_writeback as post_writeback


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
PUBLISH_QUICKSTART = PROMOTION_DIR / "first-batch-publish-quickstart.json"
PUBLICATION_PACKET = PROMOTION_DIR / "first-batch-publication-packet.json"
PUBLIC_URL_CHECKLIST = PROMOTION_DIR / "public-post-url-checklist.json"
POST_OPS = PROMOTION_DIR / "post-ops-readiness-pack.json"
COMPLETION_GATE = PROMOTION_DIR / "first-batch-completion-gate.json"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-publish-closure-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-publish-closure-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "first-batch-publish-closure-quickstart.txt"
REQUIRED_PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def metric(payload: dict, key: str, default: int = 0) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        values = {}
    try:
        return int(values.get(key, payload.get(key, default)) or default)
    except (TypeError, ValueError):
        return default


def state(payload: dict, key: str) -> int:
    values = payload.get("state", {})
    return 1 if isinstance(values, dict) and values.get(key) else 0


def by_platform(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("platform", "")): row for row in rows if row.get("platform")}


def public_counts(public: dict) -> dict[tuple[str, str], Counter[str]]:
    counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for item in public.get("items", []) if isinstance(public.get("items"), list) else []:
        key = (str(item.get("platform", "")), str(item.get("task_id", "")))
        counts[key][str(item.get("operator_status", ""))] += 1
    return counts


def build_rows(publish: dict, packet: dict, public: dict, post_ops: dict) -> list[dict]:
    publish_by_platform = by_platform(publish.get("rows", []))
    packet_by_platform = by_platform(packet.get("rows", []))
    ops_by_platform = by_platform(post_ops.get("rows", []))
    counts = public_counts(public)
    rows: list[dict] = []
    for platform in REQUIRED_PLATFORMS:
        publish_row = publish_by_platform.get(platform, {})
        packet_row = packet_by_platform.get(platform, {})
        ops_row = ops_by_platform.get(platform, {})
        task_id = str(publish_row.get("taskId") or packet_row.get("taskId") or ops_row.get("task_id", ""))
        status_counts = counts.get((platform, task_id), Counter())
        rows.append({
            "platform": platform,
            "taskId": task_id,
            "scriptId": str(publish_row.get("scriptId") or packet_row.get("scriptId", "")),
            "guardianId": str(publish_row.get("guardianId") or packet_row.get("guardianId", "")),
            "title": str(publish_row.get("title") or packet_row.get("title", "")),
            "scheduled": str(publish_row.get("scheduled") or f"{packet_row.get('scheduledDate', '')} {packet_row.get('scheduledTime', '')}".strip()),
            "readyToPublish": int(bool(publish_row.get("readyToPublish"))),
            "actionStatus": str(publish_row.get("actionStatus", "")),
            "blockedBy": str(publish_row.get("blockedBy", "")),
            "trackedUrl": str(publish_row.get("trackedUrl") or packet_row.get("trackedUrl", "")),
            "postUrl": str(packet_row.get("postUrl", "")),
            "postUrlPlaceholder": str(packet_row.get("postUrlPlaceholder", "")),
            "published": int(bool(packet_row.get("published"))),
            "proofFile": str(publish_row.get("proofFile", "")),
            "checkCommand": str(publish_row.get("checkCommand", "")),
            "writeCommand": str(publish_row.get("writeCommand", "")),
            "writebackCommand": str(packet_row.get("writebackCommand", "")),
            "kpiExampleCommand": str(packet_row.get("kpiExampleCommand", "")),
            "publicPending": int(status_counts.get("pending_publish", 0)),
            "publicComplete": int(status_counts.get("complete", 0)),
            "publicVerify": int(status_counts.get("operator_verify", 0)),
            "postOpsStatus": str(ops_row.get("status", "")),
            "caption": str(publish_row.get("caption") or packet_row.get("caption", "")),
            "stopCondition": str(publish_row.get("stopCondition", "")),
        })
    return rows


def build_quickstart() -> dict:
    handoff = read_json(PROFILE_HANDOFF)
    publish = read_json(PUBLISH_QUICKSTART)
    packet = read_json(PUBLICATION_PACKET)
    public = read_json(PUBLIC_URL_CHECKLIST)
    post_ops = read_json(POST_OPS)
    completion = read_json(COMPLETION_GATE)
    master = read_json(MASTER_GATE)
    rows = build_rows(publish, packet, public, post_ops)
    data = {
        "generatedAt": today(),
        "sources": {
            "profilePublishHandoff": str(PROFILE_HANDOFF.relative_to(ROOT)),
            "firstBatchPublishQuickstart": str(PUBLISH_QUICKSTART.relative_to(ROOT)),
            "firstBatchPublicationPacket": str(PUBLICATION_PACKET.relative_to(ROOT)),
            "publicPostUrlChecklist": str(PUBLIC_URL_CHECKLIST.relative_to(ROOT)),
            "postOpsReadinessPack": str(POST_OPS.relative_to(ROOT)),
            "firstBatchCompletionGate": str(COMPLETION_GATE.relative_to(ROOT)),
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "profileHandoffReady": metric(handoff, "readyToPublish"),
            "readyRows": metric(publish, "readyRows"),
            "blockedRows": metric(publish, "blockedRows"),
            "publishedRows": int(packet.get("publishedRows", 0) or 0),
            "pendingRows": int(packet.get("pendingRows", 0) or 0),
            "publicPendingRows": metric(public, "pendingPublishRows"),
            "postOpsBlocked": metric(post_ops, "blocked"),
            "minimumKpiRows": int(packet.get("minimumKpiRows", 0) or 0),
            "completionReady": state(completion, "readyForWeeklyReview"),
            "masterStageIndex": metric(master, "stageIndex"),
            "masterProfileConfigured": metric(master, "profileConfigured"),
            "masterFirstBatchPublished": metric(master, "firstBatchPublished"),
        },
        "rules": [
            "First-batch publishing stays blocked until profile handoff is open.",
            "Publish only the first Iris script across YouTube Shorts, TikTok, and Instagram Reels.",
            "Do not write post_url with placeholders, private drafts, scheduled previews, or login-only links.",
            "After each post URL writeback, refresh daily ops before trusting KPI or weekly review packets.",
            "KPI interpretation remains blocked until public URL checks and checked-source KPI proof are complete.",
        ],
        "closureSteps": [
            {
                "stepId": "profile_publish_handoff_open",
                "status": "current_blocker" if not metric(handoff, "readyToPublish") else "complete",
                "command": "python3 tools/promotion_profile_publish_handoff.py --check",
                "stopCondition": "Do not publish while profile_writeback_complete remains blocked.",
            },
            {
                "stepId": "publish_first_batch_posts",
                "status": "blocked_until_profile_gate" if not metric(publish, "readyRows") else "ready",
                "command": "python3 tools/promotion_first_batch_publish_quickstart.py --check",
                "stopCondition": "Publish only rows with readyToPublish=1 and unchanged quiz CTA.",
            },
            {
                "stepId": "writeback_public_post_urls",
                "status": "blocked_until_public_url" if not int(packet.get("publishedRows", 0) or 0) else "ready_after_publish",
                "command": f"python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-<platform>-publish-lt-s01-iris-silence.txt --proof-note \"{post_writeback.POST_PROOF_NOTE_PLACEHOLDER}\"",
                "stopCondition": "Replace <REAL_...> with a real public HTTPS post URL before writeback.",
            },
            {
                "stepId": "verify_public_post_urls",
                "status": "blocked_until_post_url" if metric(public, "pendingPublishRows") else "ready",
                "command": "python3 tools/promotion_public_post_url_checklist.py --check && python3 tools/promotion_post_ops_readiness_pack.py --check",
                "stopCondition": "Stop if platform domain, public view, caption CTA, UTM, or proof note is not traceable.",
            },
            {
                "stepId": "open_kpi_backfill",
                "status": "blocked_until_public_url" if not int(packet.get("publishedRows", 0) or 0) else "ready_after_public_verification",
                "command": "python3 tools/promotion_first_batch_kpi_quickstart.py --check",
                "stopCondition": "Do not interpret zero KPI values until the analytics source was actually checked.",
            },
        ],
        "rows": rows,
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    issues: list[str] = []
    metrics = data["metrics"]
    if metrics["rows"] != 3:
        issues.append(f"expected 3 first-batch publish rows, got {metrics['rows']}")
    if metrics["profileHandoffReady"] == 0 and metrics["readyRows"] != 0:
        issues.append("publish rows cannot be ready while profile handoff is closed")
    if metrics["publishedRows"] == 0 and metrics["completionReady"]:
        issues.append("completion gate cannot be ready before first-batch posts are published")
    if metrics["publishedRows"] == 0 and metrics["minimumKpiRows"] != 0:
        issues.append("minimum KPI rows must stay zero before public posts exist")
    if metrics["masterFirstBatchPublished"] != metrics["publishedRows"]:
        issues.append("master gate first-batch published count should match publication packet")
    seen = {row["platform"] for row in data["rows"]}
    if seen != set(REQUIRED_PLATFORMS):
        issues.append(f"unexpected platforms {sorted(seen)}")
    for row in data["rows"]:
        label = f"{row['platform']}/{row['taskId']}"
        if not row["proofFile"] or not row["checkCommand"] or not row["writeCommand"]:
            issues.append(f"{label}: missing proof, check, or write command")
        if "<REAL_" not in row["writebackCommand"] or "<REAL_" not in row["kpiExampleCommand"]:
            issues.append(f"{label}: writeback templates must keep real URL placeholders before publish")
        if "15 題" not in row["caption"] and "五種愛之語測驗" not in row["caption"]:
            issues.append(f"{label}: caption should keep quiz CTA")
        if "/start/" not in row["trackedUrl"] or "utm_campaign=first_round_quiz_completion" not in row["trackedUrl"]:
            issues.append(f"{label}: tracked URL must use first-round /start/ campaign")
        if row["published"] and not row["postUrl"]:
            issues.append(f"{label}: published row requires post URL")
        if row["publicPending"] and row["published"]:
            issues.append(f"{label}: published row still has pending public URL checks")
    for step in data["closureSteps"]:
        if not step.get("command") or not step.get("stopCondition"):
            issues.append(f"{step.get('stepId', '<step>')}: missing command or stop condition")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes First Batch Publish Closure Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- profile handoff ready：{metrics['profileHandoffReady']}",
        f"- ready / blocked rows：{metrics['readyRows']} / {metrics['blockedRows']}",
        f"- published / pending rows：{metrics['publishedRows']} / {metrics['pendingRows']}",
        f"- public pending rows：{metrics['publicPendingRows']}",
        f"- minimum KPI rows：{metrics['minimumKpiRows']}",
        f"- completion ready：{metrics['completionReady']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Closure Steps", ""])
    for step in data["closureSteps"]:
        lines.extend([
            f"- `{step['stepId']}` / `{step['status']}`：`{step['command']}`",
            f"  Stop: {step['stopCondition']}",
        ])
    lines.extend(["", "## Platform Publish Rows", ""])
    for row in data["rows"]:
        lines.extend([
            f"### {row['platform']} · `{row['taskId']}`",
            "",
            f"- status：`{row['actionStatus']}`",
            f"- ready to publish：{row['readyToPublish']}",
            f"- blocked by：{row['blockedBy'] or '(none)'}",
            f"- schedule：{row['scheduled']}",
            f"- post URL：{row['postUrl'] or '(pending)'}",
            f"- placeholder：`{row['postUrlPlaceholder']}`",
            f"- public complete / pending / verify：{row['publicComplete']} / {row['publicPending']} / {row['publicVerify']}",
            f"- proof file：`{row['proofFile']}`",
            f"- check：`{row['checkCommand']}`",
            f"- write：`{row['writeCommand']}`",
            f"- URL writeback：`{row['writebackCommand']}`",
            f"- KPI example：`{row['kpiExampleCommand']}`",
            f"- stop：{row['stopCondition']}",
            "",
        ])
    if data["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes first batch publish closure quickstart",
        f"generated: {data['generatedAt']}",
        f"profile handoff ready: {metrics['profileHandoffReady']}",
        f"ready/blocked rows: {metrics['readyRows']} / {metrics['blockedRows']}",
        f"published/pending rows: {metrics['publishedRows']} / {metrics['pendingRows']}",
        "",
        "Closure steps:",
    ]
    for step in data["closureSteps"]:
        lines.append(f"- {step['stepId']} / {step['status']}: {step['command']}")
    lines.extend(["", "Rows:"])
    for row in data["rows"]:
        lines.extend([
            "",
            f"=== {row['platform']} / {row['taskId']} ===",
            f"status: {row['actionStatus']}",
            f"ready: {row['readyToPublish']}",
            f"blocked by: {row['blockedBy']}",
            f"proof file: {row['proofFile']}",
            f"write: {row['writeCommand']}",
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
    parser = argparse.ArgumentParser(description="Build a first-batch publish closure quickstart for LoveTypes post URL and KPI handoff.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_first_batch_publish_closure_quickstart={args.output}")
        print(f"promotion_first_batch_publish_closure_quickstart_json={args.json_output}")
        print(f"promotion_first_batch_publish_closure_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_first_batch_publish_closure_quickstart_rows={metrics['rows']}")
    print(f"promotion_first_batch_publish_closure_quickstart_profile_handoff_ready={metrics['profileHandoffReady']}")
    print(f"promotion_first_batch_publish_closure_quickstart_ready_rows={metrics['readyRows']}")
    print(f"promotion_first_batch_publish_closure_quickstart_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_first_batch_publish_closure_quickstart_published_rows={metrics['publishedRows']}")
    print(f"promotion_first_batch_publish_closure_quickstart_public_pending_rows={metrics['publicPendingRows']}")
    print(f"promotion_first_batch_publish_closure_quickstart_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_first_batch_publish_closure_quickstart_completion_ready={metrics['completionReady']}")
    print(f"promotion_first_batch_publish_closure_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
