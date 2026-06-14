#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PUBLISH_ACTION = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
READINESS_PACK = PROMOTION_DIR / "first-batch-publish-readiness-pack.json"
PROFILE_HANDOFF = PROMOTION_DIR / "profile-publish-handoff.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-publish-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-publish-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "first-batch-publish-quickstart.txt"
REQUIRED_PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
POST_URL_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}
FORBIDDEN_TERMS = ("診斷", "療效", "保證修復", "必須購買")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def rows_by_platform(payload: dict) -> dict[str, dict]:
    return {str(row.get("platform", "")): row for row in payload.get("rows", []) if row.get("platform")}


def metric(payload: dict, key: str) -> int:
    metrics = payload.get("metrics", {})
    if not isinstance(metrics, dict):
        return 0
    try:
        return int(metrics.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def proof_template(row: dict) -> str:
    platform = str(row.get("platform", ""))
    return "\n".join([
        "LoveTypes platform post writeback",
        f"platform: {platform}",
        f"task_id: {row.get('task_id', '')}",
        "status: published",
        f"published_date: {today()}",
        f"post_url: {POST_URL_PLACEHOLDERS.get(platform, '<REAL_POST_URL>')}",
        "views: 0",
        "site_clicks: 0",
        "quiz_starts: 0",
        "quiz_completions: 0",
        "proof_note: public URL and analytics source checked YYYY-MM-DD",
    ])


def write_command(row: dict) -> str:
    proof_file = str(row.get("proof_file", ""))
    return (
        "python3 tools/promotion_post_text_import.py add "
        f"--input {proof_file} "
        "--proof-note \"public URL and analytics source checked YYYY-MM-DD\""
    )


def build_quickstart() -> dict:
    action = read_json(PUBLISH_ACTION)
    readiness = read_json(READINESS_PACK)
    profile_handoff = read_json(PROFILE_HANDOFF)
    action_rows = rows_by_platform(action)
    readiness_rows = rows_by_platform(readiness)
    ready_to_publish = bool(profile_handoff.get("metrics", {}).get("readyToPublish")) or bool(action.get("metrics", {}).get("ready"))
    rows: list[dict] = []

    for platform in REQUIRED_PLATFORMS:
        row = action_rows.get(platform, {})
        readiness_row = readiness_rows.get(platform, {})
        blocked_by = str(row.get("blocked_by", ""))
        readiness_status = str(readiness_row.get("operator_status") or readiness_row.get("status") or "")
        rows.append({
            "platform": platform,
            "taskId": str(row.get("task_id", "")),
            "scriptId": str(row.get("script_id", "")),
            "guardianId": str(row.get("guardian_id", "")),
            "title": str(row.get("title", "")),
            "scheduled": str(row.get("scheduled", "")),
            "actionStatus": str(row.get("action_status", "")),
            "readinessStatus": readiness_status,
            "readyToPublish": bool(ready_to_publish and not blocked_by),
            "blockedBy": blocked_by or readiness_status,
            "trackedUrl": str(row.get("tracked_url", "")),
            "utmContent": str(row.get("utm_content", "")),
            "caption": str(row.get("caption", "")),
            "proofFile": str(row.get("proof_file", "")),
            "proofTemplate": proof_template(row),
            "checkCommand": str(row.get("check_command", "")),
            "writeCommand": write_command(row),
            "stopCondition": (
                "Stop if profile gate is not ready, post URL is still placeholder, "
                "caption changes CTA, or platform preview adds commercial claims."
            ),
        })

    issues = validate(rows, ready_to_publish)
    return {
        "generatedAt": today(),
        "sources": {
            "firstBatchPublishAction": str(PUBLISH_ACTION.relative_to(ROOT)),
            "firstBatchPublishReadiness": str(READINESS_PACK.relative_to(ROOT)),
            "profilePublishHandoff": str(PROFILE_HANDOFF.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "readyToPublish": int(ready_to_publish),
            "readyRows": sum(1 for row in rows if row["readyToPublish"]),
            "blockedRows": sum(1 for row in rows if not row["readyToPublish"]),
            "profileHandoffReady": metric(profile_handoff, "readyToPublish"),
            "actionReady": metric(action, "ready"),
            "readinessBlocked": metric(readiness, "blocked"),
            "issues": len(issues),
        },
        "rules": [
            "Use this packet only after profile-publish handoff opens.",
            "Do not publish while any row remains blocked_until_profile_links or blocked_until_profile_gate.",
            "Replace the post URL placeholder with the real public HTTPS URL before writeback.",
            "Keep the CTA focused on the 15-question guardian quiz.",
            "Do not add paid, affiliate, diagnosis, treatment, or guaranteed-repair claims.",
        ],
        "rows": rows,
        "issues": issues,
    }


def validate(rows: list[dict], ready_to_publish: bool) -> list[str]:
    issues: list[str] = []
    seen = {row.get("platform") for row in rows}
    if seen != set(REQUIRED_PLATFORMS):
        issues.append("first-batch publish quickstart must include YouTube Shorts, TikTok, and Instagram Reels")
    for row in rows:
        label = f"{row.get('platform', '<platform>')}/{row.get('taskId', '<task>')}"
        caption = str(row.get("caption", ""))
        tracked_url = str(row.get("trackedUrl", ""))
        proof = str(row.get("proofTemplate", ""))
        if "完成 15 題測驗" not in caption and "15 題" not in caption:
            issues.append(f"{label}: caption should keep the 15-question quiz CTA")
        if "/start/" not in tracked_url or "utm_campaign=first_round_quiz_completion" not in tracked_url:
            issues.append(f"{label}: tracked URL should use the first-round /start/ campaign")
        if any(term in caption for term in FORBIDDEN_TERMS):
            issues.append(f"{label}: caption contains forbidden claim language")
        if "<REAL_" not in proof:
            issues.append(f"{label}: proof template must keep a real public post URL placeholder")
        if not row.get("proofFile") or not row.get("checkCommand"):
            issues.append(f"{label}: missing proof file or check command")
        if not row.get("writeCommand") or "<REAL_" not in proof:
            issues.append(f"{label}: missing safe writeback template")
        if not ready_to_publish and row.get("readyToPublish"):
            issues.append(f"{label}: row must not be ready while profile handoff is closed")
        if row.get("readyToPublish") and str(row.get("blockedBy", "")).strip():
            issues.append(f"{label}: ready row should not have blocked_by text")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes First Batch Publish Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready to publish：{metrics['readyToPublish']}",
        f"- ready / blocked rows：{metrics['readyRows']} / {metrics['blockedRows']}",
        f"- profile handoff ready：{metrics['profileHandoffReady']}",
        f"- action ready：{metrics['actionReady']}",
        f"- readiness blocked：{metrics['readinessBlocked']}",
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
            f"- readiness：`{row['readinessStatus']}`",
            f"- action status：`{row['actionStatus']}`",
            f"- ready to publish：`{1 if row['readyToPublish'] else 0}`",
            f"- blocked by：{row['blockedBy'] or '(none)'}",
            f"- script：`{row['scriptId']}`",
            f"- guardian：`{row['guardianId']}`",
            f"- title：{row['title']}",
            f"- scheduled：{row['scheduled']}",
            f"- tracked URL：{row['trackedUrl']}",
            f"- proof file：`{row['proofFile']}`",
            "",
            "Caption:",
            "",
            "```text",
            row["caption"],
            "```",
            "",
            "Proof text to save after the post is public:",
            "",
            "```text",
            row["proofTemplate"],
            "```",
            "",
            f"- check：`{row['checkCommand']}`",
            f"- write：`{row['writeCommand']}`",
            f"- stop：{row['stopCondition']}",
        ])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    lines = [
        "LoveTypes first batch publish quickstart",
        f"generated: {data['generatedAt']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    for row in data["rows"]:
        lines.extend([
            "",
            f"=== {row['platform']} / {row['taskId']} ===",
            f"ready: {1 if row['readyToPublish'] else 0}",
            f"blocked by: {row['blockedBy'] or '(none)'}",
            f"scheduled: {row['scheduled']}",
            f"tracked URL: {row['trackedUrl']}",
            "",
            "CAPTION:",
            row["caption"],
            "",
            f"Save this proof text to {row['proofFile']} after the post is public:",
            row["proofTemplate"],
            "",
            f"CHECK: {row['checkCommand']}",
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
    parser = argparse.ArgumentParser(description="Build a first-batch publish quickstart packet for LoveTypes promotion launch.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_first_batch_publish_quickstart={args.output}")
        print(f"promotion_first_batch_publish_quickstart_json={args.json_output}")
        print(f"promotion_first_batch_publish_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_first_batch_publish_quickstart_rows={metrics['rows']}")
    print(f"promotion_first_batch_publish_quickstart_ready_to_publish={metrics['readyToPublish']}")
    print(f"promotion_first_batch_publish_quickstart_ready_rows={metrics['readyRows']}")
    print(f"promotion_first_batch_publish_quickstart_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_first_batch_publish_quickstart_profile_ready={metrics['profileHandoffReady']}")
    print(f"promotion_first_batch_publish_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
