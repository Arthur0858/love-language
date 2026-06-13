#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_PACKET_PATH = PROMOTION_DIR / "profile-verification-packet.json"
FIRST_BATCH_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
HANDOFF_PATH = PROMOTION_DIR / "operator-handoff-packet.json"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "operation-proof-packet.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "operation-proof-packet.json"

PROFILE_REQUIRED_EVIDENCE = (
    "platform_account_visible",
    "profile_link_visible_or_clickable",
    "start_url_resolves",
    "utm_parameters_preserved",
    "quiz_only_copy",
    "proof_note_present",
)
POST_REQUIRED_EVIDENCE = (
    "profile_gate_passed",
    "public_post_url_present",
    "post_url_is_not_placeholder",
    "quiz_cta_preserved",
    "utm_content_preserved",
    "no_paid_or_affiliate_primary_cta",
    "proof_note_present",
)
KPI_REQUIRED_EVIDENCE = (
    "source_checked",
    "metric_date_recorded",
    "zero_values_are_verified_zero",
    "quiz_start_and_completion_fields_present",
)
POST_URL_PLACEHOLDERS = {
    "youtube_shorts": "<REAL_YOUTUBE_SHORTS_URL>",
    "tiktok": "<REAL_TIKTOK_VIDEO_URL>",
    "instagram_reels": "<REAL_INSTAGRAM_REEL_URL>",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def profile_template(item: dict) -> str:
    return "\n".join([
        "LoveTypes profile setup writeback",
        f"platform: {item.get('platform', '')}",
        "status: set",
        f"set_date: {date.today().isoformat()}",
        f"profile_link: {item.get('profileLink', '')}",
        "proof_note: screenshot profile-platform-YYYY-MM-DD.png saved",
    ])


def post_url_placeholder(platform: str) -> str:
    return POST_URL_PLACEHOLDERS.get(platform, "<REAL_POST_URL>")


def post_template(row: dict) -> str:
    return "\n".join([
        "LoveTypes platform post writeback",
        f"platform: {row.get('platform', '')}",
        f"task_id: {row.get('taskId', '')}",
        "status: published",
        f"published_date: {date.today().isoformat()}",
        f"post_url: {post_url_placeholder(row.get('platform', ''))}",
        "views: 0",
        "site_clicks: 0",
        "quiz_starts: 0",
        "quiz_completions: 0",
        "proof_note: public URL post checked YYYY-MM-DD",
    ])


def build_profile_proofs(profile_packet: dict) -> list[dict[str, object]]:
    proofs = []
    for item in profile_packet.get("platforms", []):
        if item.get("configured"):
            continue
        platform = item.get("platform", "")
        proofs.append({
            "kind": "profile_setup",
            "status": "needs_evidence",
            "platform": platform,
            "label": item.get("label", platform),
            "targetUrl": item.get("profileLink", ""),
            "copyFields": {
                "bio": item.get("bio", ""),
                "pinnedComment": item.get("pinnedComment", ""),
            },
            "requiredEvidence": list(PROFILE_REQUIRED_EVIDENCE),
            "minimumProofNote": "platform + set time + screenshot filename or manually clicked live link",
            "checkCommand": f"python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-{platform}.txt",
            "writeCommand": f"python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-{platform}.txt --proof-note \"screenshot profile-{platform}-{date.today().isoformat()}.png verified\"",
            "template": profile_template(item),
        })
    return proofs


def build_post_proofs(first_batch: dict, handoff: dict) -> list[dict[str, object]]:
    ready_to_publish = bool(first_batch.get("readyToPublish")) or bool(handoff.get("state", {}).get("readyToPublish"))
    proofs = []
    for row in first_batch.get("rows", []):
        if row.get("published"):
            continue
        platform = row.get("platform", "")
        task_id = row.get("taskId", "")
        blocked_by = "" if ready_to_publish else "profile links are not all set/live"
        proofs.append({
            "kind": "post_publish",
            "status": "needs_evidence" if ready_to_publish else "blocked_until_profile_gate",
            "platform": platform,
            "taskId": task_id,
            "scriptId": row.get("scriptId", ""),
            "title": row.get("title", ""),
            "trackedUrl": row.get("trackedUrl", ""),
            "scheduled": f"{row.get('scheduledDate', '')} {row.get('scheduledTime', '')} Asia/Taipei".strip(),
            "requiredEvidence": list(POST_REQUIRED_EVIDENCE),
            "minimumKpiEvidence": list(KPI_REQUIRED_EVIDENCE),
            "blockedBy": blocked_by,
            "checkCommand": f"python3 tools/promotion_post_text_import.py check --input docs/promotion/first-round/proof-{platform}-{task_id}.txt",
            "writeCommand": f"python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-{platform}-{task_id}.txt --proof-note \"public URL post checked {date.today().isoformat()}\"",
            "template": post_template(row),
        })
    return proofs


def build_packet() -> dict[str, object]:
    profile_packet = load_json(PROFILE_PACKET_PATH)
    first_batch = load_json(FIRST_BATCH_PATH)
    handoff = load_json(HANDOFF_PATH)
    profile_proofs = build_profile_proofs(profile_packet)
    post_proofs = build_post_proofs(first_batch, handoff)
    return {
        "generatedAt": date.today().isoformat(),
        "source": {
            "profileVerificationPacket": str(PROFILE_PACKET_PATH.relative_to(ROOT)),
            "firstBatchPublicationPacket": str(FIRST_BATCH_PATH.relative_to(ROOT)),
            "operatorHandoffPacket": str(HANDOFF_PATH.relative_to(ROOT)),
        },
        "state": {
            "profileConfigured": int(profile_packet.get("configuredCount", 0) or 0),
            "profilePending": int(profile_packet.get("pendingCount", 0) or 0),
            "firstBatchPublished": int(first_batch.get("publishedRows", 0) or 0),
            "firstBatchPending": int(first_batch.get("pendingRows", 0) or 0),
            "readyToPublish": bool(first_batch.get("readyToPublish")) or bool(handoff.get("state", {}).get("readyToPublish")),
            "emptyDataMode": bool(handoff.get("state", {}).get("emptyDataMode")),
        },
        "proofPolicy": {
            "checkBeforeWrite": True,
            "noPlaceholderUrls": True,
            "zeroMetricsRequireSourceCheck": True,
            "profileRequiredEvidence": list(PROFILE_REQUIRED_EVIDENCE),
            "postRequiredEvidence": list(POST_REQUIRED_EVIDENCE),
            "kpiRequiredEvidence": list(KPI_REQUIRED_EVIDENCE),
        },
        "profileProofCount": len(profile_proofs),
        "postProofCount": len(post_proofs),
        "proofs": [*profile_proofs, *post_proofs],
    }


def validate_packet(packet: dict[str, object]) -> list[str]:
    issues: list[str] = []
    state = packet.get("state", {})
    proofs = packet.get("proofs", [])
    policy = packet.get("proofPolicy", {})
    if not isinstance(proofs, list):
        return ["proofs should be a list"]
    if int(packet.get("profileProofCount", 0) or 0) != sum(1 for item in proofs if item.get("kind") == "profile_setup"):
        issues.append("profileProofCount should match profile proofs")
    if int(packet.get("postProofCount", 0) or 0) != sum(1 for item in proofs if item.get("kind") == "post_publish"):
        issues.append("postProofCount should match post proofs")
    if state.get("profilePending", 0) and not any(item.get("kind") == "profile_setup" for item in proofs):
        issues.append("pending profiles should have proof rows")
    if state.get("firstBatchPending", 0) and not any(item.get("kind") == "post_publish" for item in proofs):
        issues.append("pending first-batch posts should have proof rows")
    if not policy.get("checkBeforeWrite") or not policy.get("noPlaceholderUrls") or not policy.get("zeroMetricsRequireSourceCheck"):
        issues.append("proof policy should require check-before-write, no placeholders, and verified zero metrics")
    for item in proofs:
        label = f"{item.get('kind', '<kind>')}/{item.get('platform', '<platform>')}/{item.get('taskId', '')}"
        if " check --input " not in str(item.get("checkCommand", "")):
            issues.append(f"{label}: missing check command")
        if " add --input " not in str(item.get("writeCommand", "")) or "--proof-note" not in str(item.get("writeCommand", "")):
            issues.append(f"{label}: missing proof-gated write command")
        template = str(item.get("template", ""))
        if "proof_note:" not in template:
            issues.append(f"{label}: template should include proof_note")
        if item.get("kind") == "profile_setup":
            required = set(PROFILE_REQUIRED_EVIDENCE)
            if not required.issubset(set(item.get("requiredEvidence", []))):
                issues.append(f"{label}: profile evidence checklist is incomplete")
            if "/start/?" not in str(item.get("targetUrl", "")):
                issues.append(f"{label}: profile target should point to tracked /start/")
        if item.get("kind") == "post_publish":
            required = set(POST_REQUIRED_EVIDENCE)
            if not required.issubset(set(item.get("requiredEvidence", []))):
                issues.append(f"{label}: post evidence checklist is incomplete")
            if set(KPI_REQUIRED_EVIDENCE) != set(item.get("minimumKpiEvidence", [])):
                issues.append(f"{label}: minimum KPI evidence checklist is incomplete")
            expected_placeholder = post_url_placeholder(str(item.get("platform", "")))
            if f"post_url: {expected_placeholder}" not in template:
                issues.append(f"{label}: template should use platform-specific post URL placeholder")
            if "replace-with-real" in template or "example.com" in template:
                issues.append(f"{label}: template should not contain URL-like placeholders")
            if not state.get("readyToPublish") and item.get("status") != "blocked_until_profile_gate":
                issues.append(f"{label}: pending post should stay blocked while profile gate is false")
    return issues


def render_markdown(packet: dict[str, object], issues: list[str]) -> str:
    state = packet.get("state", {})
    lines = [
        "# LoveTypes Operation Proof Packet",
        "",
        f"- Generated: `{packet.get('generatedAt', '')}`",
        f"- Profile pending: `{state.get('profilePending', 0)}`",
        f"- First batch pending: `{state.get('firstBatchPending', 0)}`",
        f"- Ready to publish: `{1 if state.get('readyToPublish') else 0}`",
        f"- Empty data mode: `{1 if state.get('emptyDataMode') else 0}`",
        f"- Issues: `{len(issues)}`",
        "",
        "## Proof Rules",
        "",
        "- Run the check command before any write command.",
        "- Do not write back placeholder post URLs.",
        "- A zero metric is valid only after the platform or analytics source was checked.",
        "- Keep the first launch CTA focused on the 15-question quiz; do not turn launch posts into paid offers.",
        "",
        "## Proof Rows",
        "",
    ]
    for item in packet.get("proofs", []):
        lines.extend([
            f"### {item.get('kind', '')}: {item.get('platform', '')} {item.get('taskId', '')}".strip(),
            "",
            f"- Status: `{item.get('status', '')}`",
            f"- Check: `{item.get('checkCommand', '')}`",
            f"- Write: `{item.get('writeCommand', '')}`",
        ])
        if item.get("blockedBy"):
            lines.append(f"- Blocked by: `{item.get('blockedBy', '')}`")
        lines.extend([
            "- Required evidence:",
            *[f"  - `{evidence}`" for evidence in item.get("requiredEvidence", [])],
            "- Template:",
            "",
            "```text",
            str(item.get("template", "")),
            "```",
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the LoveTypes launch operation proof packet.")
    parser.add_argument("--check", action="store_true", help="Validate without writing output files.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    args = parser.parse_args()

    packet = build_packet()
    issues = validate_packet(packet)
    print(f"promotion_operation_proof_profile_rows={packet.get('profileProofCount', 0)}")
    print(f"promotion_operation_proof_post_rows={packet.get('postProofCount', 0)}")
    print(f"promotion_operation_proof_total_rows={len(packet.get('proofs', []))}")
    print(f"promotion_operation_proof_ready_to_publish={1 if packet.get('state', {}).get('readyToPublish') else 0}")
    print(f"promotion_operation_proof_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        json_output = Path(args.json_output)
        md_output = Path(args.output)
        json_output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_output.write_text(render_markdown(packet, issues), encoding="utf-8")
        print(f"promotion_operation_proof_json={json_output.relative_to(ROOT)}")
        print(f"promotion_operation_proof_md={md_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
