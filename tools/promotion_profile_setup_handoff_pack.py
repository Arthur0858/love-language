#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
ACTION_SHEET = PROMOTION_DIR / "profile-setup-action-sheet.json"
QUICKSTART = PROMOTION_DIR / "profile-quickstart.json"
LINK_READINESS = PROMOTION_DIR / "profile-link-readiness-packet.json"
PROOF_READINESS = PROMOTION_DIR / "profile-proof-readiness-pack.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-setup-handoff-pack.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-setup-handoff-pack.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "profile-setup-handoff-pack.txt"
REQUIRED_PLATFORMS = ("youtube_shorts", "tiktok", "instagram_reels")
FORBIDDEN_TERMS = ("診斷", "療效", "保證修復", "必須購買")


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def by_platform(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("platform", "")): row for row in rows if row.get("platform")}


def build_pack() -> dict:
    action = read_json(ACTION_SHEET)
    quickstart = read_json(QUICKSTART)
    link = read_json(LINK_READINESS)
    proof = read_json(PROOF_READINESS)
    action_rows = by_platform(action.get("rows", []))
    quick_rows = by_platform(quickstart.get("platforms", []))
    link_rows = by_platform(link.get("rows", []))
    proof_rows = by_platform(proof.get("rows", []))
    rows: list[dict[str, object]] = []
    for platform in REQUIRED_PLATFORMS:
        action_row = action_rows.get(platform, {})
        quick_row = quick_rows.get(platform, {})
        link_row = link_rows.get(platform, {})
        proof_row = proof_rows.get(platform, {})
        profile_link = str(action_row.get("profile_link") or quick_row.get("profileLink") or link_row.get("profile_link") or "")
        rows.append({
            "platform": platform,
            "label": str(action_row.get("label") or quick_row.get("label") or proof_row.get("label") or platform),
            "trackerStatus": str(action_row.get("status", "")),
            "actionStatus": str(action_row.get("action_status", "")),
            "linkPublicReady": str(link_row.get("public_ready", "0")),
            "proofStatus": str(proof_row.get("operator_status", "")),
            "profileLinkLocation": str(action_row.get("profile_link_location") or quick_row.get("profileLinkLocation") or ""),
            "profileLink": profile_link,
            "bio": str(action_row.get("bio") or quick_row.get("bio") or ""),
            "pinnedComment": str(action_row.get("pinned_comment") or quick_row.get("pinnedComment") or ""),
            "proofFile": str(action_row.get("proof_file") or quick_row.get("proofFile") or f"docs/promotion/first-round/proof-{platform}.txt"),
            "proofTemplate": str(quick_row.get("proofTemplate", "")),
            "checkCommand": str(action_row.get("check_command") or proof_row.get("check_command") or quick_row.get("checkCommand") or ""),
            "writeCommand": str(action_row.get("write_command") or proof_row.get("write_command") or quick_row.get("writeCommand") or ""),
            "stopCondition": str(action_row.get("stop_condition") or quick_row.get("stopCondition") or ""),
            "identityChecks": int(action_row.get("identity_checks", 0) or 0),
            "evidenceChecks": int(action_row.get("evidence_checks", 0) or 0),
            "pendingEvidenceChecks": int(quick_row.get("pendingEvidenceChecks", 0) or 0),
        })
    issues = validate_rows(rows, action, quickstart, link, proof)
    return {
        "generatedAt": today(),
        "sources": {
            "profileSetupActionSheet": str(ACTION_SHEET.relative_to(ROOT)),
            "profileQuickstart": str(QUICKSTART.relative_to(ROOT)),
            "profileLinkReadiness": str(LINK_READINESS.relative_to(ROOT)),
            "profileProofReadiness": str(PROOF_READINESS.relative_to(ROOT)),
        },
        "metrics": {
            "platforms": len(rows),
            "readyToConfigure": sum(1 for row in rows if row["actionStatus"] == "ready_to_configure"),
            "readyToWriteback": sum(1 for row in rows if row["actionStatus"] == "ready_to_writeback"),
            "configured": sum(1 for row in rows if row["trackerStatus"] in {"set", "live"}),
            "publicReady": sum(1 for row in rows if row["linkPublicReady"] == "1"),
            "pendingEvidenceChecks": sum(int(row["pendingEvidenceChecks"]) for row in rows),
            "proofReadyRows": sum(1 for row in rows if row["proofStatus"] in {"ready_to_configure", "ready_to_writeback", "complete"}),
            "issues": len(issues),
        },
        "rules": [
            "Use this handoff pack as the single operator view for platform profile setup.",
            "Public-ready means the LoveTypes /start/ URL works; it does not prove the external platform profile is set.",
            "Run checkCommand before writeCommand, and only after replacing proof placeholders with real screenshot/click proof.",
            "Do not publish first-batch Shorts/Reels until all three tracker statuses are set or live.",
            "Keep all profile copy quiz-only; do not add Luna, affiliate, paid, diagnosis, or treatment claims.",
        ],
        "rows": rows,
        "issues": issues,
    }


def validate_rows(rows: list[dict[str, object]], action: dict, quickstart: dict, link: dict, proof: dict) -> list[str]:
    issues: list[str] = []
    platforms = {str(row.get("platform", "")) for row in rows}
    if platforms != set(REQUIRED_PLATFORMS):
        issues.append("handoff pack must cover YouTube Shorts, TikTok, and Instagram Reels")
    if int(action.get("metrics", {}).get("rows", 0) or 0) != len(REQUIRED_PLATFORMS):
        issues.append("profile setup action sheet should contain three rows")
    if int(quickstart.get("metrics", {}).get("platforms", 0) or 0) != len(REQUIRED_PLATFORMS):
        issues.append("profile quickstart should contain three platforms")
    if int(link.get("metrics", {}).get("publicReady", 0) or 0) != len(REQUIRED_PLATFORMS):
        issues.append("profile links should all be public-ready before operator handoff")
    if int(proof.get("metrics", {}).get("proofFiles", 0) or 0) != len(REQUIRED_PLATFORMS):
        issues.append("profile proof readiness should expose three proof files")
    for row in rows:
        platform = str(row.get("platform", "<platform>"))
        profile_link = str(row.get("profileLink", ""))
        profile_copy = f"{row.get('bio', '')}\n{row.get('pinnedComment', '')}"
        if "/start/" not in profile_link or "utm_campaign=first_round_quiz_completion" not in profile_link:
            issues.append(f"{platform}: profile link must use first-round /start/ UTM URL")
        if row.get("linkPublicReady") != "1":
            issues.append(f"{platform}: profile link is not public-ready")
        if row.get("actionStatus") not in {"ready_to_configure", "ready_to_writeback", "complete"}:
            issues.append(f"{platform}: invalid action status {row.get('actionStatus')}")
        if row.get("proofStatus") not in {"ready_to_configure", "ready_to_writeback", "complete"}:
            issues.append(f"{platform}: invalid proof status {row.get('proofStatus')}")
        if "15 題" not in profile_copy:
            issues.append(f"{platform}: profile copy should keep the 15-question quiz CTA")
        if any(term in profile_copy for term in FORBIDDEN_TERMS):
            issues.append(f"{platform}: profile copy contains forbidden claim language")
        if int(row.get("identityChecks", 0) or 0) != 7:
            issues.append(f"{platform}: expected 7 identity checks")
        if int(row.get("evidenceChecks", 0) or 0) != 6:
            issues.append(f"{platform}: expected 6 evidence checks")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in str(row.get("proofTemplate", "")):
            issues.append(f"{platform}: proof template should force real proof replacement")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in str(row.get("writeCommand", "")):
            issues.append(f"{platform}: write command should force real proof replacement")
        if "--proof-note" not in str(row.get("writeCommand", "")):
            issues.append(f"{platform}: write command should require proof note")
        if not row.get("checkCommand") or not row.get("stopCondition"):
            issues.append(f"{platform}: missing check command or stop condition")
    return issues


def render_markdown(pack: dict) -> str:
    metrics = pack["metrics"]
    lines = [
        "# LoveTypes Profile Setup Handoff Pack",
        "",
        f"- 產生日期：{pack['generatedAt']}",
        f"- platforms：{metrics['platforms']}",
        f"- ready to configure：{metrics['readyToConfigure']}",
        f"- ready to writeback：{metrics['readyToWriteback']}",
        f"- configured：{metrics['configured']}",
        f"- public ready：{metrics['publicReady']}",
        f"- pending evidence checks：{metrics['pendingEvidenceChecks']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in pack["rules"])
    for row in pack["rows"]:
        lines.extend([
            "",
            f"## {row['label']}（`{row['platform']}`）",
            "",
            f"- tracker status：`{row['trackerStatus']}`",
            f"- action status：`{row['actionStatus']}`",
            f"- proof status：`{row['proofStatus']}`",
            f"- public ready：`{row['linkPublicReady']}`",
            f"- link location：{row['profileLinkLocation']}",
            f"- profile link：{row['profileLink']}",
            f"- identity / evidence checks：{row['identityChecks']} / {row['evidenceChecks']}",
            f"- pending evidence checks：{row['pendingEvidenceChecks']}",
            "",
            "### Bio",
            "",
            "```text",
            str(row["bio"]),
            "```",
            "",
            "### Pinned / First Comment",
            "",
            "```text",
            str(row["pinnedComment"]),
            "```",
            "",
            "### Proof Text",
            "",
            f"Save to `{row['proofFile']}` after real platform verification:",
            "",
            "```text",
            str(row["proofTemplate"]),
            "```",
            "",
            f"- check：`{row['checkCommand']}`",
            f"- write：`{row['writeCommand']}`",
            f"- stop：{row['stopCondition']}",
        ])
    if pack["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in pack["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(pack: dict) -> str:
    lines = [
        "LoveTypes profile setup handoff",
        f"generated: {pack['generatedAt']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in pack["rules"])
    for row in pack["rows"]:
        lines.extend([
            "",
            f"=== {row['label']} / {row['platform']} ===",
            f"status: tracker={row['trackerStatus']} action={row['actionStatus']} proof={row['proofStatus']} public={row['linkPublicReady']}",
            f"location: {row['profileLinkLocation']}",
            f"profile link: {row['profileLink']}",
            "",
            "BIO:",
            str(row["bio"]),
            "",
            "PINNED / FIRST COMMENT:",
            str(row["pinnedComment"]),
            "",
            f"PROOF FILE: {row['proofFile']}",
            str(row["proofTemplate"]),
            "",
            f"CHECK: {row['checkCommand']}",
            f"WRITE: {row['writeCommand']}",
            f"STOP: {row['stopCondition']}",
        ])
    if pack["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in pack["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(pack: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(pack), encoding="utf-8")
    json_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(pack), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the LoveTypes profile setup operator handoff pack.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    pack = build_pack()
    metrics = pack["metrics"]
    print(f"promotion_profile_setup_handoff_platforms={metrics['platforms']}")
    print(f"promotion_profile_setup_handoff_ready_configure={metrics['readyToConfigure']}")
    print(f"promotion_profile_setup_handoff_ready_writeback={metrics['readyToWriteback']}")
    print(f"promotion_profile_setup_handoff_configured={metrics['configured']}")
    print(f"promotion_profile_setup_handoff_public_ready={metrics['publicReady']}")
    print(f"promotion_profile_setup_handoff_pending_evidence={metrics['pendingEvidenceChecks']}")
    print(f"promotion_profile_setup_handoff_proof_ready={metrics['proofReadyRows']}")
    print(f"promotion_profile_setup_handoff_issues={metrics['issues']}")
    for issue in pack["issues"]:
        print(issue)
    if pack["issues"]:
        return 1
    if not args.check:
        write_outputs(pack, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_profile_setup_handoff_md={Path(args.output).relative_to(ROOT)}")
        print(f"promotion_profile_setup_handoff_json={Path(args.json_output).relative_to(ROOT)}")
        print(f"promotion_profile_setup_handoff_txt={Path(args.txt_output).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
