#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
RUNBOOK_PATH = PROMOTION_DIR / "profile-setup-runbook.json"
IDENTITY_PATH = PROMOTION_DIR / "platform-account-identity-checklist.json"
EVIDENCE_PATH = PROMOTION_DIR / "profile-evidence-checklist.json"
COMPLETION_GATE_PATH = PROMOTION_DIR / "profile-completion-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-setup-action-sheet.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-setup-action-sheet.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "profile-setup-action-sheet.csv"

FIELDNAMES = [
    "platform",
    "label",
    "status",
    "action_status",
    "profile_link_location",
    "profile_link",
    "bio",
    "pinned_comment",
    "identity_checks",
    "evidence_checks",
    "proof_file",
    "proof_note",
    "check_command",
    "write_command",
    "stop_condition",
]


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def group_counts(items: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        platform = str(item.get(key, ""))
        if not platform:
            continue
        counts[platform] = counts.get(platform, 0) + 1
    return counts


def group_status_counts(items: list[dict], key: str) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for item in items:
        platform = str(item.get(key, ""))
        status = str(item.get("operator_status", "pending"))
        if not platform:
            continue
        counts.setdefault(platform, {})
        counts[platform][status] = counts[platform].get(status, 0) + 1
    return counts


def build_rows() -> tuple[list[dict[str, str]], dict[str, object], list[str]]:
    runbook = read_json(RUNBOOK_PATH)
    identity = read_json(IDENTITY_PATH)
    evidence = read_json(EVIDENCE_PATH)
    completion = read_json(COMPLETION_GATE_PATH)

    identity_counts = group_counts(identity.get("items", []), "platform")
    identity_status = group_status_counts(identity.get("items", []), "platform")
    evidence_counts = group_counts(evidence.get("items", []), "platform")
    evidence_status = group_status_counts(evidence.get("items", []), "platform")
    issues: list[str] = []
    rows: list[dict[str, str]] = []

    for platform in runbook.get("platforms", []):
        platform_id = str(platform.get("platform", ""))
        configured = bool(platform.get("configured"))
        identity_pending = identity_status.get(platform_id, {}).get("pending", 0)
        evidence_pending = evidence_status.get(platform_id, {}).get("pending", 0)
        suggested_proof_note = f"screenshot profile-{platform_id}-{today()}.png verified"
        action_status = "complete" if configured else "ready_to_configure"
        if identity_pending == 0 and evidence_pending == 0 and not configured:
            action_status = "ready_to_writeback"
        rows.append({
            "platform": platform_id,
            "label": str(platform.get("label", platform_id)),
            "status": str(platform.get("status", "")),
            "action_status": action_status,
            "profile_link_location": str(platform.get("profileLinkLabel", "")),
            "profile_link": str(platform.get("profileLink", "")),
            "bio": str(platform.get("bio", "")),
            "pinned_comment": str(platform.get("pinnedComment", "")),
            "identity_checks": str(identity_counts.get(platform_id, 0)),
            "evidence_checks": str(evidence_counts.get(platform_id, 0)),
            "proof_file": f"docs/promotion/first-round/proof-{platform_id}.txt",
            "proof_note": suggested_proof_note,
            "check_command": f"python3 tools/promotion_profile_text_import.py check --input docs/promotion/first-round/proof-{platform_id}.txt",
            "write_command": f"python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-{platform_id}.txt --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\"",
            "stop_condition": "Stop if account/profile is not visibly LoveTypes, edit permission is missing, /start/ UTM is changed, or Bio copy adds paid/diagnosis claims.",
        })

    if len(rows) != int(runbook.get("platformCount", 0) or 0):
        issues.append("action sheet row count should match profile setup runbook platform count")
    for row in rows:
        platform = row["platform"]
        if int(row["identity_checks"] or 0) != 7:
            issues.append(f"{platform}: expected 7 identity checks")
        if int(row["evidence_checks"] or 0) != 6:
            issues.append(f"{platform}: expected 6 evidence checks")
        if "/start/" not in row["profile_link"] or "utm_campaign=first_round_quiz_completion" not in row["profile_link"]:
            issues.append(f"{platform}: profile link should be the first-round /start/ campaign URL")
        if not row["bio"]:
            issues.append(f"{platform}: missing bio copy")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in row["write_command"]:
            issues.append(f"{platform}: write command must force real proof replacement")
        if row["proof_note"] in row["write_command"]:
            issues.append(f"{platform}: write command must not reuse the scaffold proof note")
    if int(completion.get("metrics", {}).get("issues", 0) or 0) != 0:
        issues.append("profile completion gate reports issues")

    metrics = {
        "rows": len(rows),
        "readyToConfigure": sum(1 for row in rows if row["action_status"] == "ready_to_configure"),
        "readyToWriteback": sum(1 for row in rows if row["action_status"] == "ready_to_writeback"),
        "configured": sum(1 for row in rows if row["action_status"] == "complete"),
        "identityChecks": sum(int(row["identity_checks"] or 0) for row in rows),
        "evidenceChecks": sum(int(row["evidence_checks"] or 0) for row in rows),
        "profileGateReady": int(bool(completion.get("state", {}).get("readyForFirstBatchPublish"))),
    }
    return rows, metrics, issues


def render_markdown(rows: list[dict[str, str]], metrics: dict[str, object], issues: list[str]) -> str:
    lines = [
        "# LoveTypes Profile Setup Action Sheet",
        "",
        f"- 產生日期：{today()}",
        f"- platforms：{metrics.get('rows', 0)}",
        f"- ready to configure：{metrics.get('readyToConfigure', 0)}",
        f"- ready to writeback：{metrics.get('readyToWriteback', 0)}",
        f"- configured：{metrics.get('configured', 0)}",
        f"- identity checks：{metrics.get('identityChecks', 0)}",
        f"- evidence checks：{metrics.get('evidenceChecks', 0)}",
        f"- profile gate ready：{metrics.get('profileGateReady', 0)}",
        f"- issues：{len(issues)}",
        "",
        "## Rule",
        "",
        "- 先確認帳號與公開頁是 LoveTypes，再貼 profile link。",
        "- 每個平台都要完成 7 個帳號身份檢查與 6 個 profile 證據檢查。",
        "- 沒有截圖、公開點擊或可追溯 proof note 時，不回填 `set/live`。",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['label']}（`{row['platform']}`）",
            "",
            f"- action status：`{row['action_status']}`",
            f"- current tracker status：`{row['status']}`",
            f"- link location：{row['profile_link_location']}",
            f"- profile link：{row['profile_link']}",
            f"- identity / evidence checks：{row['identity_checks']} / {row['evidence_checks']}",
            "",
            "Bio:",
            "",
            "```text",
            row["bio"],
            "```",
            "",
            "Pinned / first comment:",
            "",
            "```text",
            row["pinned_comment"],
            "```",
            "",
            f"- proof file：`{row['proof_file']}`",
            f"- suggested proof note：`{row['proof_note']}`",
            f"- check：`{row['check_command']}`",
            f"- write：`{row['write_command']}`",
            f"- stop：{row['stop_condition']}",
            "",
        ])
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the LoveTypes platform profile setup action sheet.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    rows, metrics, issues = build_rows()
    print(f"promotion_profile_setup_action_rows={metrics['rows']}")
    print(f"promotion_profile_setup_action_ready_configure={metrics['readyToConfigure']}")
    print(f"promotion_profile_setup_action_ready_writeback={metrics['readyToWriteback']}")
    print(f"promotion_profile_setup_action_configured={metrics['configured']}")
    print(f"promotion_profile_setup_action_identity_checks={metrics['identityChecks']}")
    print(f"promotion_profile_setup_action_evidence_checks={metrics['evidenceChecks']}")
    print(f"promotion_profile_setup_action_gate_ready={metrics['profileGateReady']}")
    print(f"promotion_profile_setup_action_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1
    if not args.check:
        payload = {
            "generatedAt": today(),
            "sources": {
                "runbook": str(RUNBOOK_PATH.relative_to(ROOT)),
                "identity": str(IDENTITY_PATH.relative_to(ROOT)),
                "evidence": str(EVIDENCE_PATH.relative_to(ROOT)),
                "profileCompletionGate": str(COMPLETION_GATE_PATH.relative_to(ROOT)),
            },
            "metrics": metrics,
            "rows": rows,
            "issues": issues,
        }
        md_output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        md_output.write_text(render_markdown(rows, metrics, issues), encoding="utf-8")
        json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, rows)
        print(f"promotion_profile_setup_action_md={md_output.relative_to(ROOT)}")
        print(f"promotion_profile_setup_action_json={json_output.relative_to(ROOT)}")
        print(f"promotion_profile_setup_action_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
