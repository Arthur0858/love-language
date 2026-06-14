#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
ACTION_SHEET = PROMOTION_DIR / "profile-setup-action-sheet.json"
READINESS = PROMOTION_DIR / "profile-link-readiness-packet.json"
COMPLETION = PROMOTION_DIR / "profile-completion-gate.json"
OUTPUT_MD = PROMOTION_DIR / "profile-proof-readiness-pack.md"
OUTPUT_JSON = PROMOTION_DIR / "profile-proof-readiness-pack.json"
OUTPUT_CSV = PROMOTION_DIR / "profile-proof-readiness-pack.csv"


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "set", "live", "ready"}
    return False


def run_import_check(proof_file: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "tools/promotion_profile_text_import.py", "check", "--input", proof_file],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout.strip()
    ok = (
        result.returncode == 0
        and "promotion_profile_text_import_has_profile_link=1" in output
        and "promotion_profile_text_import_issues=0" in output
    )
    return ok, output


def proof_template_text(row: dict[str, str]) -> str:
    return "\n".join([
        "LoveTypes profile setup writeback",
        f"platform: {row['platform']}",
        "status: set",
        f"set_date: {today()}",
        f"profile_link: {row['profile_link']}",
        f"proof_note: {row['proof_note']}",
        "",
    ])


def build_pack() -> dict:
    action = load_json(ACTION_SHEET)
    readiness = load_json(READINESS)
    completion = load_json(COMPLETION)
    readiness_by_platform = {
        str(row.get("platform", "")): row
        for row in readiness.get("rows", [])
        if isinstance(row, dict)
    }
    rows: list[dict[str, str]] = []
    for action_row in action.get("rows", []):
        platform = str(action_row.get("platform", ""))
        proof_file = str(action_row.get("proof_file", ""))
        proof_path = ROOT / proof_file
        import_ok, import_output = run_import_check(proof_file) if proof_file else (False, "missing proof file")
        readiness_row = readiness_by_platform.get(platform, {})
        configured = truthy(readiness_row.get("profile_configured"))
        public_ready = truthy(readiness_row.get("public_ready"))
        row = {
            "platform": platform,
            "label": str(action_row.get("label", platform)),
            "proof_file": proof_file,
            "proof_file_exists": "1" if proof_path.exists() else "0",
            "proof_template_importable": "1" if import_ok else "0",
            "public_profile_link_ready": "1" if public_ready else "0",
            "profile_configured": "1" if configured else "0",
            "operator_status": "ready_to_configure" if public_ready and not configured else ("complete" if configured else "blocked"),
            "template_text": proof_template_text(action_row),
            "check_command": str(action_row.get("check_command", "")),
            "write_command": str(action_row.get("write_command", "")),
            "evidence_required": "A real platform screenshot/click proof must exist before running the write command.",
            "import_output": import_output.replace("\n", " | "),
        }
        rows.append(row)
    metrics = {
        "rows": len(rows),
        "proofFiles": sum(1 for row in rows if row["proof_file_exists"] == "1"),
        "importableTemplates": sum(1 for row in rows if row["proof_template_importable"] == "1"),
        "publicReady": sum(1 for row in rows if row["public_profile_link_ready"] == "1"),
        "configured": sum(1 for row in rows if row["profile_configured"] == "1"),
        "readyToConfigure": sum(1 for row in rows if row["operator_status"] == "ready_to_configure"),
        "readyToWriteback": sum(1 for row in rows if row["operator_status"] == "ready_to_writeback"),
        "profileGateReady": int(bool(completion.get("state", {}).get("readyForFirstBatchPublish"))),
    }
    issues: list[str] = []
    if metrics["rows"] != 3:
        issues.append(f"expected 3 profile proof rows, got {metrics['rows']}")
    if metrics["proofFiles"] != metrics["rows"]:
        issues.append("all profile proof files should exist")
    if metrics["importableTemplates"] != metrics["rows"]:
        issues.append("all profile proof templates should be importable")
    if metrics["publicReady"] != metrics["rows"]:
        issues.append("all profile links should be publicly ready before operator setup")
    if metrics["profileGateReady"] and metrics["configured"] != metrics["rows"]:
        issues.append("profile gate cannot be ready unless all platforms are configured")
    return {
        "generatedAt": today(),
        "sources": {
            "actionSheet": str(ACTION_SHEET.relative_to(ROOT)),
            "readiness": str(READINESS.relative_to(ROOT)),
            "completion": str(COMPLETION.relative_to(ROOT)),
        },
        "metrics": metrics,
        "rows": rows,
        "rules": [
            "Importable proof text is not proof of setup; it only means the writeback format is valid.",
            "Run the write command only after the platform profile link is actually set and verified.",
            "Keep status planned until there is a real screenshot, public click, or platform-time proof note.",
            "After all three profile rows are set/live, rerun launch readiness before publishing first batch.",
        ],
        "issues": issues,
    }


def render_markdown(pack: dict) -> str:
    metrics = pack["metrics"]
    lines = [
        "# LoveTypes Profile Proof Readiness Pack",
        "",
        f"- 產生日期：{pack['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- proof files：{metrics['proofFiles']}",
        f"- importable templates：{metrics['importableTemplates']}",
        f"- public ready：{metrics['publicReady']}",
        f"- configured：{metrics['configured']}",
        f"- ready to configure：{metrics['readyToConfigure']}",
        f"- profile gate ready：{metrics['profileGateReady']}",
        f"- issues：{len(pack['issues'])}",
        "",
        "## Rule",
        "",
    ]
    lines.extend(f"- {rule}" for rule in pack["rules"])
    lines.extend(["", "## Platform Proof Blocks", ""])
    for row in pack["rows"]:
        lines.extend([
            f"### {row['label']}（`{row['platform']}`）",
            "",
            f"- operator status：`{row['operator_status']}`",
            f"- proof file：`{row['proof_file']}`",
            f"- proof file exists：{row['proof_file_exists']}",
            f"- template importable：{row['proof_template_importable']}",
            f"- public profile link ready：{row['public_profile_link_ready']}",
            f"- profile configured：{row['profile_configured']}",
            f"- evidence required：{row['evidence_required']}",
            f"- check：`{row['check_command']}`",
            f"- write：`{row['write_command']}`",
            "",
            "Structured proof text:",
            "",
            "```text",
            row["template_text"].rstrip(),
            "```",
            "",
        ])
    if pack["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in pack["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(pack: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(pack), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "platform",
            "label",
            "proof_file",
            "proof_file_exists",
            "proof_template_importable",
            "public_profile_link_ready",
            "profile_configured",
            "operator_status",
            "check_command",
            "write_command",
            "evidence_required",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in pack["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a profile proof readiness pack for LoveTypes launch operations.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    pack = build_pack()
    metrics = pack["metrics"]
    if not args.check:
        write_outputs(pack)
        print(f"promotion_profile_proof_readiness_pack={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_profile_proof_readiness_pack_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_profile_proof_readiness_pack_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_profile_proof_readiness_rows={metrics['rows']}")
    print(f"promotion_profile_proof_readiness_proof_files={metrics['proofFiles']}")
    print(f"promotion_profile_proof_readiness_importable_templates={metrics['importableTemplates']}")
    print(f"promotion_profile_proof_readiness_public_ready={metrics['publicReady']}")
    print(f"promotion_profile_proof_readiness_configured={metrics['configured']}")
    print(f"promotion_profile_proof_readiness_ready_configure={metrics['readyToConfigure']}")
    print(f"promotion_profile_proof_readiness_ready_writeback={metrics['readyToWriteback']}")
    print(f"promotion_profile_proof_readiness_gate_ready={metrics['profileGateReady']}")
    print(f"promotion_profile_proof_readiness_issues={len(pack['issues'])}")
    for issue in pack["issues"]:
        print(issue)
    return 1 if pack["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
