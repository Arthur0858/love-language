#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import promotion_profile_text_import as text_import
import promotion_profile_writeback as writeback
from promotion_proof_note_policy import proof_note_issue


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROOF_FILES = {
    "youtube_shorts": PROMOTION_DIR / "proof-youtube_shorts.txt",
    "tiktok": PROMOTION_DIR / "proof-tiktok.txt",
    "instagram_reels": PROMOTION_DIR / "proof-instagram_reels.txt",
}
OUTPUT_MD = PROMOTION_DIR / "profile-batch-import-quickstart.md"
OUTPUT_JSON = PROMOTION_DIR / "profile-batch-import-quickstart.json"
OUTPUT_TXT = PROMOTION_DIR / "profile-batch-import-quickstart.txt"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def classify_proof(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "platform": "",
            "proofFile": str(path.relative_to(ROOT)),
            "status": "missing_file",
            "ready": 0,
            "issues": [f"missing proof file {path.relative_to(ROOT)}"],
        }
    text = path.read_text(encoding="utf-8")
    data, parse_issues = text_import.parse_text(text)
    platform = data.get("platform", "")
    issues: list[str] = [str(issue) for issue in parse_issues]
    status = "ready"
    proof = data.get("proof_note", "")
    proof_issue = proof_note_issue(proof) if proof else "proof_note is missing"
    scaffold_issue = text_import.scaffold_proof_issue(proof)
    if proof_issue or scaffold_issue:
        status = "blocked_until_real_proof"
        if proof_issue:
            issues.append(proof_issue)
        if scaffold_issue:
            issues.append(scaffold_issue)
    if platform not in PROOF_FILES:
        status = "invalid"
        issues.append(f"unexpected platform {platform!r}")
    elif path != PROOF_FILES[platform]:
        status = "invalid"
        issues.append(f"{platform}: proof file path does not match platform")
    return {
        "platform": platform,
        "proofFile": str(path.relative_to(ROOT)),
        "status": status,
        "ready": 1 if status == "ready" and not issues else 0,
        "data": data,
        "issues": issues,
    }


def build_packet() -> dict:
    rows = [classify_proof(path) for path in PROOF_FILES.values()]
    ready_rows = sum(int(row["ready"]) for row in rows)
    blocked_rows = sum(1 for row in rows if row["status"] == "blocked_until_real_proof")
    invalid_rows = sum(1 for row in rows if row["status"] not in {"ready", "blocked_until_real_proof"})
    duplicate_platforms = len({str(row.get("platform", "")) for row in rows if row.get("platform")}) != ready_rows + blocked_rows
    issues: list[str] = []
    if len(rows) != len(PROOF_FILES):
        issues.append("expected exactly three profile proof files")
    if invalid_rows:
        issues.append(f"invalid profile proof rows: {invalid_rows}")
    if duplicate_platforms:
        issues.append("profile proof files contain duplicate or missing platforms")
    return {
        "generatedAt": text_import.TODAY,
        "proofFiles": [str(path.relative_to(ROOT)) for path in PROOF_FILES.values()],
        "metrics": {
            "proofFiles": len(rows),
            "readyRows": ready_rows,
            "blockedRows": blocked_rows,
            "invalidRows": invalid_rows,
            "issues": len(issues),
        },
        "rows": rows,
        "rules": [
            "Use this batch only after all three external profile links are visibly set and verified.",
            "Placeholder proof notes are allowed in check mode and treated as blocked, not ready.",
            "The add mode writes all three profile rows together, then runs the full daily ops refresh once.",
            "If any proof file is blocked or invalid, add mode stops without writing tracker rows.",
        ],
        "commands": {
            "check": "python3 tools/promotion_profile_batch_import.py --check",
            "writeDocs": "python3 tools/promotion_profile_batch_import.py",
            "addAll": "python3 tools/promotion_profile_batch_import.py --add",
        },
        "issues": issues,
    }


def apply_batch(packet: dict) -> None:
    metrics = packet["metrics"]
    if metrics["readyRows"] != len(PROOF_FILES) or metrics["issues"]:
        details = []
        for row in packet["rows"]:
            if row["issues"]:
                details.append(f"{row.get('platform') or row.get('proofFile')}: " + "; ".join(row["issues"]))
        raise SystemExit("profile batch import requires all three proof files ready\n" + "\n".join(details))

    fieldnames, tracker_rows = read_rows(writeback.TRACKER_PATH)
    candidate = [dict(row) for row in tracker_rows]
    for row in packet["rows"]:
        data = row["data"]
        writeback.update_row(
            candidate,
            data["platform"],
            data["status"],
            data["set_date"],
            data.get("proof_note", ""),
            {field: data.get(field, "") for field in writeback.METRIC_FIELDS},
        )
    issues = writeback.validate_tracker(fieldnames, candidate)
    if issues:
        raise SystemExit("\n".join(issues))
    write_rows(writeback.TRACKER_PATH, fieldnames, candidate)
    writeback.regenerate_dependent_docs()


def render_markdown(packet: dict) -> str:
    metrics = packet["metrics"]
    lines = [
        "# LoveTypes Profile Batch Import Quickstart",
        "",
        f"- 產生日期：{packet['generatedAt']}",
        f"- 狀態：ready={metrics['readyRows']} / blocked={metrics['blockedRows']} / invalid={metrics['invalidRows']} / issues={metrics['issues']}",
        f"- check：`{packet['commands']['check']}`",
        f"- add all：`{packet['commands']['addAll']}`",
        "",
        "## Proof Files",
        "",
    ]
    for row in packet["rows"]:
        issue_count = len(row["issues"])
        lines.append(
            f"- `{row['proofFile']}`：`{row.get('platform') or 'unknown'}` / `{row['status']}` / ready={row['ready']} / issues={issue_count}"
        )
    if packet["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in packet["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(packet: dict) -> str:
    metrics = packet["metrics"]
    lines = [
        f"generated: {packet['generatedAt']}",
        f"ready={metrics['readyRows']} blocked={metrics['blockedRows']} invalid={metrics['invalidRows']} issues={metrics['issues']}",
        f"check: {packet['commands']['check']}",
        f"add: {packet['commands']['addAll']}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(packet: dict) -> None:
    public_packet = {
        "generatedAt": packet["generatedAt"],
        "metrics": packet["metrics"],
        "rows": [
            {
                "p": row.get("platform", ""),
                "file": row["proofFile"],
                "status": row["status"],
                "ready": row["ready"],
                "issues": len(row["issues"]),
            }
            for row in packet["rows"]
        ],
        "issues": packet["issues"],
    }
    OUTPUT_JSON.write_text(json.dumps(public_packet, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    OUTPUT_TXT.write_text(render_text(packet), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or import all three LoveTypes profile proof files as one guarded batch.")
    parser.add_argument("--check", action="store_true", help="Validate current proof files without writing generated docs.")
    parser.add_argument("--add", action="store_true", help="Import all three ready proof files and refresh downstream ops docs.")
    args = parser.parse_args()

    packet = build_packet()
    if args.add:
        apply_batch(packet)
        packet = build_packet()
    if not args.check:
        write_outputs(packet)
        print(f"promotion_profile_batch_import_md={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_profile_batch_import_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_profile_batch_import_txt={OUTPUT_TXT.relative_to(ROOT)}")
    metrics = packet["metrics"]
    print(f"promotion_profile_batch_import_proof_files={metrics['proofFiles']}")
    print(f"promotion_profile_batch_import_ready_rows={metrics['readyRows']}")
    print(f"promotion_profile_batch_import_blocked_rows={metrics['blockedRows']}")
    print(f"promotion_profile_batch_import_invalid_rows={metrics['invalidRows']}")
    print(f"promotion_profile_batch_import_issues={metrics['issues']}")
    for issue in packet["issues"]:
        print(issue)
    return 1 if packet["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
