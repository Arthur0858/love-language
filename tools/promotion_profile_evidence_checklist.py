#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_PACKET_PATH = PROMOTION_DIR / "profile-verification-packet.json"
PROOF_TEMPLATES_PATH = PROMOTION_DIR / "operation-proof-templates.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "profile-evidence-checklist.csv"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-evidence-checklist.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-evidence-checklist.md"

FIELDNAMES = [
    "platform",
    "label",
    "check_id",
    "required_evidence",
    "expected_value",
    "proof_file",
    "check_command",
    "write_command",
    "evidence_value",
    "operator_status",
    "notes",
]

EXPECTED_VALUES = {
    "platform_account_visible": "The correct platform account/profile page is visible before editing.",
    "profile_link_visible_or_clickable": "The platform profile, website field, description, or pinned comment visibly contains the tracked /start/ link.",
    "start_url_resolves": "Clicking or copying the platform link reaches https://lovetypes.tw/start/ without 404.",
    "utm_parameters_preserved": "utm_source, utm_medium, utm_campaign, and utm_content are still present after platform handling.",
    "quiz_only_copy": "Bio/comment copy only promotes the 15-question guardian quiz; no Luna, affiliate, paid, diagnosis, or treatment promise.",
    "proof_note_present": "A traceable proof note exists, such as screenshot filename, public clicked URL, or screen recording filename.",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def proof_rows_by_platform() -> dict[str, dict]:
    data = read_json(PROOF_TEMPLATES_PATH)
    rows = {}
    for row in data.get("rows", []):
        if row.get("kind") == "profile_setup":
            rows[str(row.get("platform", ""))] = row
    return rows


def build_rows() -> list[dict[str, str]]:
    packet = read_json(PROFILE_PACKET_PATH)
    proof_rows = proof_rows_by_platform()
    rows: list[dict[str, str]] = []
    for platform in packet.get("platforms", []):
        platform_id = str(platform.get("platform", ""))
        proof = proof_rows.get(platform_id, {})
        required_evidence = list(proof.get("requiredEvidence", [])) or [
            evidence_to_check_id(evidence)
            for evidence in platform.get("evidenceRequirements", [])
        ]
        for check_id in EXPECTED_VALUES:
            if check_id not in required_evidence:
                required_evidence.append(check_id)
        proof_file = str(proof.get("path", "")) or f"docs/promotion/first-round/proof-{platform_id}.txt"
        check_command = str(proof.get("checkCommand", "")) or f"python3 tools/promotion_profile_text_import.py check --input {proof_file}"
        write_command = str(proof.get("writeCommand", "")) or f"python3 tools/promotion_profile_text_import.py add --input {proof_file} --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\""
        for index, check_id in enumerate(required_evidence, start=1):
            rows.append({
                "platform": platform_id,
                "label": str(platform.get("label", platform_id)),
                "check_id": f"{platform_id}-{index:02d}-{check_id}",
                "required_evidence": check_id,
                "expected_value": expected_value(check_id, ""),
                "proof_file": proof_file,
                "check_command": check_command,
                "write_command": write_command,
                "evidence_value": "",
                "operator_status": "pending",
                "notes": platform_note_for_check(platform, check_id),
            })
    return rows


def evidence_to_check_id(text: str) -> str:
    if "實際貼到" in text:
        return "platform_account_visible"
    if "抵達 https://lovetypes.tw/start/" in text:
        return "start_url_resolves"
    if "UTM" in text:
        return "utm_parameters_preserved"
    if "只有測驗 CTA" in text:
        return "quiz_only_copy"
    if "proof note" in text or "可追溯" in text:
        return "proof_note_present"
    return "profile_link_visible_or_clickable"


def expected_value(check_id: str, fallback: str) -> str:
    return EXPECTED_VALUES.get(check_id, fallback)


def platform_note_for_check(platform: dict, check_id: str) -> str:
    evidence_requirements = platform.get("evidenceRequirements", [])
    if check_id == "platform_account_visible":
        return str(evidence_requirements[0]) if evidence_requirements else ""
    if check_id == "profile_link_visible_or_clickable":
        return f"Link location: {platform.get('profileLinkLabel', '')}; URL: {platform.get('profileLink', '')}"
    if check_id == "start_url_resolves":
        return "從平台畫面點擊或複製連結後，仍可抵達 https://lovetypes.tw/start/。"
    if check_id == "utm_parameters_preserved":
        return "UTM source / medium / campaign / content 沒有被平台移除或改寫。"
    if check_id == "quiz_only_copy":
        return "Bio 與置頂留言只導向 15 題測驗，沒有導購、療效或診斷承諾。"
    if check_id == "proof_note_present":
        return "留下可追溯 proof note，例如平台、設定時間、截圖檔名或手動驗證紀錄。"
    return ""


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    platforms = {row["platform"] for row in rows}
    if not platforms:
        issues.append("expected at least 1 launch platform")
    for platform in sorted(platforms):
        platform_rows = [row for row in rows if row["platform"] == platform]
        if len(platform_rows) != len(EXPECTED_VALUES):
            issues.append(f"{platform}: expected {len(EXPECTED_VALUES)} evidence rows, got {len(platform_rows)}")
        required = {row["required_evidence"] for row in platform_rows}
        missing = set(EXPECTED_VALUES) - required
        if missing:
            issues.append(f"{platform}: missing evidence checks {sorted(missing)}")
    for row in rows:
        label = row["check_id"]
        if not row["proof_file"].endswith(f"proof-{row['platform']}.txt"):
            issues.append(f"{label}: proof_file should point to platform profile proof template")
        if "promotion_profile_text_import.py check" not in row["check_command"]:
            issues.append(f"{label}: missing profile proof check command")
        if "promotion_profile_text_import.py add" not in row["write_command"]:
            issues.append(f"{label}: missing profile proof write command")
        if row["operator_status"] != "pending":
            issues.append(f"{label}: generated checklist rows should start pending")
    return issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes Profile Evidence Checklist",
        "",
        f"- Generated: `{payload['generatedAt']}`",
        f"- Platforms: `{payload['platforms']}`",
        f"- Evidence rows: `{payload['rows']}`",
        f"- Pending rows: `{payload['pendingRows']}`",
        f"- Issues: `{len(payload['issues'])}`",
        "",
        "## Rule",
        "",
        "- Do not write profile `set/live` until all six checks for that platform have real evidence.",
        "- Keep the generated `proof-<platform>.txt` file as the structured writeback input.",
        "- Evidence value can be a screenshot filename, clicked public URL, screen recording filename, or platform-visible note.",
        "",
    ]
    by_platform: dict[str, list[dict[str, str]]] = {}
    for row in payload["items"]:
        by_platform.setdefault(row["platform"], []).append(row)
    for platform, rows in by_platform.items():
        label = rows[0]["label"] if rows else platform
        lines.extend([f"## {label} (`{platform}`)", ""])
        lines.append(f"- Proof file: `{rows[0]['proof_file']}`")
        lines.append(f"- Check: `{rows[0]['check_command']}`")
        lines.append(f"- Write: `{rows[0]['write_command']}`")
        lines.append("")
        for row in rows:
            lines.append(f"- [ ] `{row['required_evidence']}`：{row['expected_value']}")
        lines.append("")
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fillable evidence checklist before marking LoveTypes launch profiles set/live.")
    parser.add_argument("--check", action="store_true", help="Validate current generated rows without writing outputs.")
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    args = parser.parse_args()

    rows = build_rows()
    issues = validate_rows(rows)
    payload = {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "profileVerificationPacket": str(PROFILE_PACKET_PATH.relative_to(ROOT)),
            "proofTemplates": str(PROOF_TEMPLATES_PATH.relative_to(ROOT)),
        },
        "platforms": len({row["platform"] for row in rows}),
        "rows": len(rows),
        "pendingRows": sum(1 for row in rows if row["operator_status"] == "pending"),
        "items": rows,
        "issues": issues,
    }
    print(f"promotion_profile_evidence_checklist_platforms={payload['platforms']}")
    print(f"promotion_profile_evidence_checklist_rows={payload['rows']}")
    print(f"promotion_profile_evidence_checklist_pending={payload['pendingRows']}")
    print(f"promotion_profile_evidence_checklist_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        write_csv(rows, Path(args.csv_output))
        Path(args.json_output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        Path(args.output).write_text(render_markdown(payload), encoding="utf-8")
        print(f"promotion_profile_evidence_checklist_csv={Path(args.csv_output).relative_to(ROOT)}")
        print(f"promotion_profile_evidence_checklist_json={Path(args.json_output).relative_to(ROOT)}")
        print(f"promotion_profile_evidence_checklist_md={Path(args.output).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
