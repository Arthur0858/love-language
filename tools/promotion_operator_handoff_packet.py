#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
NEXT_ACTIONS_PATH = PROMOTION_DIR / "next-actions.json"
PROFILE_PACKET_PATH = PROMOTION_DIR / "profile-verification-packet.json"
FIRST_BATCH_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
WEEKLY_REVIEW_PATH = PROMOTION_DIR / "weekly-review-packet.json"
READINESS_PATH = PROMOTION_DIR / "launch-readiness-gate.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "operator-handoff-packet.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "operator-handoff-packet.json"
POST_URL_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def post_url_placeholder(platform: str) -> str:
    return POST_URL_PLACEHOLDERS.get(platform, "<REAL_POST_URL>")


def build_profile_steps(profile_packet: dict) -> list[dict[str, object]]:
    steps = []
    for item in profile_packet.get("platforms", []):
        if item.get("configured"):
            continue
        steps.append({
            "phase": "profile_setup",
            "status": "ready",
            "priority": "high",
            "platform": item.get("platform", ""),
            "title": f"Set {item.get('label', item.get('platform', 'platform'))} profile link",
            "url": item.get("profileLink", ""),
            "copy": {
                "bio": item.get("bio", ""),
                "pinnedComment": item.get("pinnedComment", ""),
            },
            "evidenceRequired": item.get("evidenceRequirements", []),
            "writebackCommand": item.get("writebackCommand", ""),
            "blockedBy": "",
        })
    return steps


def build_publish_steps(first_batch: dict, readiness: dict) -> list[dict[str, object]]:
    steps = []
    ready_to_publish = bool(first_batch.get("readyToPublish")) or bool(readiness.get("readyToPublish"))
    for row in first_batch.get("rows", []):
        if row.get("published"):
            continue
        steps.append({
            "phase": "publish_first_batch",
            "status": "ready" if ready_to_publish else "blocked_until_profile_links",
            "priority": "high",
            "platform": row.get("platform", ""),
            "title": row.get("title", ""),
            "taskId": row.get("taskId", ""),
            "scriptId": row.get("scriptId", ""),
            "scheduled": f"{row.get('scheduledDate', '')} {row.get('scheduledTime', '')} Asia/Taipei".strip(),
            "trackedUrl": row.get("trackedUrl", ""),
            "caption": row.get("caption", ""),
            "writebackCommand": row.get("writebackCommand", ""),
            "blockedBy": "" if ready_to_publish else "profile links are not all set/live",
        })
    return steps


def build_kpi_steps(first_batch: dict) -> list[dict[str, object]]:
    steps = []
    for row in first_batch.get("rows", []):
        if not row.get("published"):
            continue
        if row.get("minimumKpiFilled"):
            continue
        steps.append({
            "phase": "minimum_kpi_backfill",
            "status": "ready",
            "priority": "high",
            "platform": row.get("platform", ""),
            "taskId": row.get("taskId", ""),
            "scriptId": row.get("scriptId", ""),
            "requiredFields": first_batch.get("minimumKpiFields", []),
            "writebackCommand": row.get("kpiExampleCommand", ""),
            "blockedBy": "",
        })
    return steps


def build_weekly_steps(weekly_review: dict) -> list[dict[str, object]]:
    state = weekly_review.get("state", {})
    if state.get("readyForWeeklyDecision"):
        status = "ready"
        blocked_by = ""
    else:
        status = "blocked_until_kpi_backfill"
        blocked_by = "; ".join(weekly_review.get("holdReasons", []))
    return [{
        "phase": "weekly_review",
        "status": status,
        "priority": "medium",
        "title": "Run weekly review and decision gates",
        "requiredFields": weekly_review.get("reviewFields", {}).get("minimum", []),
        "allowedDecisions": weekly_review.get("allowedDecisions", []),
        "blockedDecisions": weekly_review.get("blockedDecisions", []),
        "blockedBy": blocked_by,
    }]


def build_handoff() -> dict:
    next_actions = load_json(NEXT_ACTIONS_PATH)
    profile_packet = load_json(PROFILE_PACKET_PATH)
    first_batch = load_json(FIRST_BATCH_PATH)
    weekly_review = load_json(WEEKLY_REVIEW_PATH)
    readiness = load_json(READINESS_PATH)
    profile_steps = build_profile_steps(profile_packet)
    publish_steps = build_publish_steps(first_batch, readiness)
    kpi_steps = build_kpi_steps(first_batch)
    weekly_steps = build_weekly_steps(weekly_review)
    steps = [*profile_steps, *publish_steps, *kpi_steps, *weekly_steps]
    ready_steps = [step for step in steps if step.get("status") == "ready"]
    blocked_steps = [step for step in steps if str(step.get("status", "")).startswith("blocked")]
    first_profile = profile_steps[0] if profile_steps else {}
    first_publish = publish_steps[0] if publish_steps else {}
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "nextActions": str(NEXT_ACTIONS_PATH.relative_to(ROOT)),
            "profileVerificationPacket": str(PROFILE_PACKET_PATH.relative_to(ROOT)),
            "firstBatchPublicationPacket": str(FIRST_BATCH_PATH.relative_to(ROOT)),
            "weeklyReviewPacket": str(WEEKLY_REVIEW_PATH.relative_to(ROOT)),
            "launchReadiness": str(READINESS_PATH.relative_to(ROOT)),
        },
        "state": {
            "profileConfigured": int(profile_packet.get("configuredCount", 0) or 0),
            "profilePending": int(profile_packet.get("pendingCount", 0) or 0),
            "readyToPublish": bool(readiness.get("readyToPublish")) or bool(first_batch.get("readyToPublish")),
            "firstBatchPublished": int(first_batch.get("publishedRows", 0) or 0),
            "firstBatchPending": int(first_batch.get("pendingRows", 0) or 0),
            "weeklyReviewReady": bool(weekly_review.get("state", {}).get("readyForWeeklyDecision")),
            "emptyDataMode": bool(weekly_review.get("state", {}).get("emptyDataMode")),
            "nextActionsEmptyData": bool(next_actions.get("dataState", {}).get("emptyDataMode")),
        },
        "stepCount": len(steps),
        "readyCount": len(ready_steps),
        "blockedCount": len(blocked_steps),
        "steps": steps,
        "structuredImports": build_structured_imports(first_profile, first_publish),
        "doNotDo": [
            "Do not mark profiles set/live without platform evidence.",
            "Do not mark posts published without a verified https post URL.",
            "Do not fill KPI with guesses; use 0 only when the platform/source was checked and truly has 0.",
            "Do not change offer order, paid CTA, Luna emphasis, affiliate emphasis, or winning guardian in empty-data mode.",
        ],
        "completionCriteria": [
            "profileConfigured reaches 3",
            "readyToPublish becomes true",
            "firstBatchPublished reaches 3",
            "minimum KPI rows are backfilled or explicitly verified as 0",
            "weeklyReviewReady becomes true before any revenue decision",
        ],
    }


def build_structured_imports(first_profile: dict[str, object], first_publish: dict[str, object]) -> list[dict[str, str]]:
    profile_platform = str(first_profile.get("platform") or "youtube_shorts")
    profile_url = str(first_profile.get("url") or "https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio")
    publish_platform = str(first_publish.get("platform") or "youtube_shorts")
    publish_task = str(first_publish.get("taskId") or "publish-lt-s01-iris-silence")
    publish_placeholder = post_url_placeholder(publish_platform)
    return [
        {
            "id": "profile_setup_import",
            "title": "Profile setup proof import",
            "checkCommand": "python3 tools/promotion_profile_text_import.py check --input /path/to/profile.txt",
            "writeCommand": "python3 tools/promotion_profile_text_import.py add --input /path/to/profile.txt --proof-note \"screenshot profile-youtube_shorts-YYYY-MM-DD.png verified\"",
            "template": "\n".join([
                "LoveTypes profile setup writeback",
                f"platform: {profile_platform}",
                "status: set",
                f"set_date: {date.today().isoformat()}",
                f"profile_link: {profile_url}",
                "proof_note: screenshot profile-youtube_shorts-YYYY-MM-DD.png verified",
            ]),
        },
        {
            "id": "post_publish_import",
            "title": "Published post URL and starter KPI import",
            "checkCommand": "python3 tools/promotion_post_text_import.py check --input /path/to/post.txt",
            "writeCommand": "python3 tools/promotion_post_text_import.py add --input /path/to/post.txt --proof-note \"public URL post checked YYYY-MM-DD\"",
            "template": "\n".join([
                "LoveTypes platform post writeback",
                f"platform: {publish_platform}",
                f"task_id: {publish_task}",
                "status: published",
                f"published_date: {date.today().isoformat()}",
                f"post_url: {publish_placeholder}",
                "views: 0",
                "site_clicks: 0",
                "quiz_starts: 0",
                "quiz_completions: 0",
            ]),
        },
        {
            "id": "lead_request_import",
            "title": "Structured lead request import",
            "checkCommand": "python3 tools/promotion_lead_text_import.py check --input /path/to/request.txt",
            "writeCommand": "python3 tools/promotion_lead_text_import.py add --input /path/to/request.txt --proof-note \"email thread Gmail request checked YYYY-MM-DD\"",
            "template": "\n".join([
                "LoveTypes 結構化需求",
                "來源: 收藏室免費素材需求",
                "我的守護者: 艾莉絲 · 肯定的言詞",
                "需求類型: owned_asset_request",
                "素材偏好: PDF 練習卡",
                "可回覆 email: name@example.com",
                "Campaign content / 推廣內容: iris_silence",
                "使用情境或備註: 睡前整理，想要可列印版本",
                "consent_status: explicit_reply_ok",
                "page: https://lovetypes.tw/keepsakes/",
            ]),
        },
    ]


def validate_handoff(handoff: dict) -> list[str]:
    issues: list[str] = []
    state = handoff.get("state", {})
    steps = handoff.get("steps", [])
    if handoff.get("stepCount") != len(steps):
        issues.append("stepCount should match steps length")
    if state.get("profilePending", 0) > 0 and not any(step.get("phase") == "profile_setup" for step in steps):
        issues.append("pending profiles should create profile_setup steps")
    if state.get("firstBatchPending", 0) > 0 and not any(step.get("phase") == "publish_first_batch" for step in steps):
        issues.append("pending first batch should create publish steps")
    if state.get("emptyDataMode") and not any("empty-data" in item or "empty-data" in item.lower() for item in handoff.get("doNotDo", [])):
        issues.append("empty data mode should appear in do-not-do rules")
    if state.get("profilePending", 0) > 0 and state.get("readyToPublish"):
        issues.append("readyToPublish should not be true while profiles are pending")
    structured_imports = handoff.get("structuredImports", [])
    expected_import_ids = {"profile_setup_import", "post_publish_import", "lead_request_import"}
    actual_import_ids = {item.get("id") for item in structured_imports}
    if actual_import_ids != expected_import_ids:
        issues.append("structured imports should cover profile, post, and lead writeback")
    for item in structured_imports:
        label = item.get("id", "<import>")
        if " check --input " not in item.get("checkCommand", ""):
            issues.append(f"{label}: missing check command")
        if " add --input " not in item.get("writeCommand", "") or "--proof-note" not in item.get("writeCommand", ""):
            issues.append(f"{label}: missing proof-gated write command")
        if not item.get("template") or ":" not in item.get("template", ""):
            issues.append(f"{label}: missing structured text template")
        template = str(item.get("template", ""))
        if item.get("id") == "post_publish_import":
            if "replace-with-real" in template or "example.com" in template or "lovetypes-proof-url-123" in template:
                issues.append(f"{label}: post import template should not contain URL-like placeholders")
            if "<REAL_" not in template:
                issues.append(f"{label}: post import template should use explicit platform placeholder")
    for step in steps:
        label = f"{step.get('phase', '<phase>')}/{step.get('platform', step.get('taskId', ''))}"
        if not step.get("phase") or not step.get("status") or not step.get("priority"):
            issues.append(f"{label}: missing phase/status/priority")
        if step.get("phase") == "profile_setup":
            if "--proof-note" not in str(step.get("writebackCommand", "")):
                issues.append(f"{label}: profile writeback should require proof note")
            if len(step.get("evidenceRequired", [])) < 5:
                issues.append(f"{label}: profile evidence requirements incomplete")
        if step.get("phase") == "publish_first_batch":
            if step.get("status") == "ready" and "--proof-note" not in str(step.get("writebackCommand", "")):
                issues.append(f"{label}: publish writeback should require proof note")
            if not step.get("caption"):
                issues.append(f"{label}: publish step missing caption")
        if step.get("phase") == "weekly_review" and not step.get("blockedDecisions"):
            issues.append("weekly review should list blocked decisions")
    if len(handoff.get("completionCriteria", [])) < 5:
        issues.append("completion criteria are incomplete")
    return issues


def render_markdown(handoff: dict, issues: list[str]) -> str:
    state = handoff["state"]
    lines = [
        "# LoveTypes Operator Handoff Packet",
        "",
        f"- 產生日期：{handoff['generatedAt']}",
        f"- profile configured / pending：{state['profileConfigured']} / {state['profilePending']}",
        f"- ready to publish：{1 if state['readyToPublish'] else 0}",
        f"- first batch published / pending：{state['firstBatchPublished']} / {state['firstBatchPending']}",
        f"- weekly review ready：{1 if state['weeklyReviewReady'] else 0}",
        f"- empty data mode：{1 if state['emptyDataMode'] else 0}",
        f"- ready steps：{handoff['readyCount']}",
        f"- blocked steps：{handoff['blockedCount']}",
        f"- issues：{len(issues)}",
        "",
        "## Do Not Do",
        "",
    ]
    lines.extend(f"- {item}" for item in handoff["doNotDo"])
    lines.extend(["", "## Structured Import Templates", ""])
    for item in handoff["structuredImports"]:
        lines.extend([
            f"### {item['title']}",
            "",
            f"- check：`{item['checkCommand']}`",
            f"- write：`{item['writeCommand']}`",
            "",
            "```text",
            item["template"],
            "```",
            "",
        ])
    lines.extend(["", "## Steps", ""])
    for index, step in enumerate(handoff["steps"], start=1):
        lines.extend([
            f"### {index}. {step.get('title') or step.get('taskId') or step.get('phase')}",
            "",
            f"- phase：`{step.get('phase')}`",
            f"- status：`{step.get('status')}`",
            f"- priority：`{step.get('priority')}`",
        ])
        for field in ("platform", "taskId", "scriptId", "scheduled", "url", "trackedUrl"):
            if step.get(field):
                lines.append(f"- {field}：{step[field]}")
        if step.get("blockedBy"):
            lines.append(f"- blocked by：{step['blockedBy']}")
        if step.get("writebackCommand"):
            lines.append(f"- writeback：`{step['writebackCommand']}`")
        if step.get("evidenceRequired"):
            lines.extend(["", "Evidence:"])
            lines.extend(f"- {item}" for item in step["evidenceRequired"])
        if step.get("caption"):
            lines.extend(["", "Caption:", "", "```text", str(step["caption"]), "```"])
        lines.append("")
    lines.extend(["## Completion Criteria", ""])
    lines.extend(f"- {item}" for item in handoff["completionCriteria"])
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(handoff: dict, issues: list[str], output: Path, json_output: Path) -> None:
    json_output.write_text(json.dumps({**handoff, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.write_text(render_markdown(handoff, issues), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a daily operator handoff packet for LoveTypes promotion launch.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    handoff = build_handoff()
    issues = validate_handoff(handoff)
    if not args.check:
        write_outputs(handoff, issues, Path(args.output), Path(args.json_output))
        print(f"promotion_operator_handoff_packet={args.output}")
        print(f"promotion_operator_handoff_packet_json={args.json_output}")
    state = handoff["state"]
    print(f"promotion_operator_handoff_steps={handoff['stepCount']}")
    print(f"promotion_operator_handoff_ready={handoff['readyCount']}")
    print(f"promotion_operator_handoff_blocked={handoff['blockedCount']}")
    print(f"promotion_operator_handoff_profile_pending={state['profilePending']}")
    print(f"promotion_operator_handoff_first_batch_pending={state['firstBatchPending']}")
    print(f"promotion_operator_handoff_weekly_ready={1 if state['weeklyReviewReady'] else 0}")
    print(f"promotion_operator_handoff_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
