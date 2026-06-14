#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import promotion_profile_batch_import as batch_import
import promotion_profile_text_import as text_import
import promotion_profile_writeback as writeback
from promotion_proof_note_policy import proof_note_issue


ROOT = Path(__file__).resolve().parents[1]
PROMO = ROOT / "docs" / "promotion" / "first-round"
OUTPUT_MD = PROMO / "profile-unlock-rehearsal.md"
OUTPUT_JSON = PROMO / "profile-unlock-rehearsal.json"


def read_tracker() -> tuple[list[str], list[dict[str, str]]]:
    with writeback.TRACKER_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def proof_with_real_note(path: Path, platform: str) -> str:
    text = path.read_text(encoding="utf-8")
    note = f"screenshot lovetypes-{platform}-profile-{date.today().isoformat()}.png verified"
    lines = []
    replaced = False
    for line in text.splitlines():
        if line.strip().lower().startswith("proof_note:"):
            lines.append(f"proof_note: {note}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append(f"proof_note: {note}")
    return "\n".join(lines) + "\n"


def run_command(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return result.returncode, result.stdout.strip()


def build_payload() -> dict:
    current_packet = batch_import.build_packet()
    fieldnames, tracker_rows = read_tracker()
    candidate = [dict(row) for row in tracker_rows]
    rows: list[dict[str, object]] = []
    issues: list[str] = []

    for platform, path in batch_import.PROOF_FILES.items():
        text = proof_with_real_note(path, platform)
        data, parse_issues = text_import.parse_text(text)
        proof_note = data.get("proof_note", "")
        note_issue = proof_note_issue(proof_note)
        scaffold_issue = text_import.scaffold_proof_issue(proof_note)
        row_issues = [str(issue) for issue in parse_issues]
        if note_issue:
            row_issues.append(note_issue)
        if scaffold_issue:
            row_issues.append(scaffold_issue)
        if data.get("platform") != platform:
            row_issues.append(f"expected platform {platform}, got {data.get('platform', '')}")
        if not row_issues:
            writeback.update_row(
                candidate,
                data["platform"],
                data["status"],
                data["set_date"],
                proof_note,
                {field: data.get(field, "") for field in writeback.METRIC_FIELDS},
            )
        rows.append({
            "platform": platform,
            "proofFile": str(path.relative_to(ROOT)),
            "syntheticReady": 0 if row_issues else 1,
            "syntheticProofNote": proof_note,
            "issues": row_issues,
        })

    tracker_issues = writeback.validate_tracker(fieldnames, candidate)
    issues.extend(tracker_issues)
    launch_code, launch_output = run_command([sys.executable, "tools/promotion_launch_sequence_dry_run.py"])
    dry_run_issues = []
    if launch_code != 0:
        dry_run_issues.append("launch sequence dry run failed")
    if "promotion_launch_sequence_dry_run_issues=0" not in launch_output:
        dry_run_issues.append("launch sequence dry run did not report issues=0")
    if "promotion_launch_sequence_dry_run_current_files_mutated=0" not in launch_output:
        dry_run_issues.append("launch sequence dry run must not mutate current files")
    issues.extend(dry_run_issues)

    current_metrics = current_packet.get("metrics", {})
    metrics = {
        "proofFiles": len(rows),
        "currentReadyRows": int(current_metrics.get("readyRows", 0) or 0),
        "currentBlockedRows": int(current_metrics.get("blockedRows", 0) or 0),
        "syntheticReadyRows": sum(int(row["syntheticReady"]) for row in rows),
        "candidateTrackerValid": 0 if tracker_issues else 1,
        "launchDryRunGreen": 0 if dry_run_issues else 1,
    }
    if metrics["proofFiles"] != 3:
        issues.append(f"expected 3 profile proof files, got {metrics['proofFiles']}")
    if metrics["currentBlockedRows"] != 3 and metrics["currentReadyRows"] != 3:
        issues.append("current profile proof state should be either all blocked or all ready")
    if metrics["syntheticReadyRows"] != 3:
        issues.append("synthetic real-proof rehearsal should make all three rows ready")
    return {
        "generatedAt": date.today().isoformat(),
        "sources": [
            "docs/promotion/first-round/proof-youtube_shorts.txt",
            "docs/promotion/first-round/proof-tiktok.txt",
            "docs/promotion/first-round/proof-instagram_reels.txt",
            str(writeback.TRACKER_PATH.relative_to(ROOT)),
        ],
        "metrics": metrics,
        "rows": rows,
        "commands": [
            "python3 tools/promotion_profile_batch_import.py --check",
            "python3 tools/promotion_profile_batch_import.py --add",
            "python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py",
        ],
        "issues": issues,
    }


def render_md(payload: dict) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes Profile Unlock Rehearsal",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- proof files：{metrics['proofFiles']}",
        f"- current ready / blocked：{metrics['currentReadyRows']} / {metrics['currentBlockedRows']}",
        f"- synthetic ready：{metrics['syntheticReadyRows']}",
        f"- candidate tracker valid：{metrics['candidateTrackerValid']}",
        f"- launch dry run green：{metrics['launchDryRunGreen']}",
        f"- issues：{len(payload['issues'])}",
        "",
        "## Rule",
        "",
        "- This rehearsal does not write tracker rows.",
        "- It proves that replacing placeholder proof notes with traceable profile evidence would unlock the guarded profile batch path.",
        "- Real add still requires actual screenshot, clicked public link, recording, or platform URL proof.",
        "",
        "## Commands After Real Proof",
        "",
    ]
    lines.extend(f"- `{command}`" for command in payload["commands"])
    lines.extend(["", "## Rows", ""])
    for row in payload["rows"]:
        lines.extend([
            f"- `{row['platform']}`：ready={row['syntheticReady']} file=`{row['proofFile']}` issues={len(row['issues'])}",
        ])
    if payload["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict) -> None:
    public_payload = {
        "generatedAt": payload["generatedAt"],
        "sources": payload["sources"],
        "metrics": payload["metrics"],
        "rows": [
            {
                "platform": row["platform"],
                "proofFile": row["proofFile"],
                "syntheticReady": row["syntheticReady"],
                "issues": len(row["issues"]),
            }
            for row in payload["rows"]
        ],
        "commands": payload["commands"],
        "issues": payload["issues"],
    }
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(public_payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rehearse the profile proof unlock path without mutating tracker rows.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if not args.check:
        write_outputs(payload)
        print(f"promotion_profile_unlock_rehearsal={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_profile_unlock_rehearsal_json={OUTPUT_JSON.relative_to(ROOT)}")
    metrics = payload["metrics"]
    print(f"promotion_profile_unlock_rehearsal_proof_files={metrics['proofFiles']}")
    print(f"promotion_profile_unlock_rehearsal_current_ready_rows={metrics['currentReadyRows']}")
    print(f"promotion_profile_unlock_rehearsal_current_blocked_rows={metrics['currentBlockedRows']}")
    print(f"promotion_profile_unlock_rehearsal_synthetic_ready_rows={metrics['syntheticReadyRows']}")
    print(f"promotion_profile_unlock_rehearsal_candidate_tracker_valid={metrics['candidateTrackerValid']}")
    print(f"promotion_profile_unlock_rehearsal_launch_dry_run_green={metrics['launchDryRunGreen']}")
    print(f"promotion_profile_unlock_rehearsal_issues={len(payload['issues'])}")
    for issue in payload["issues"]:
        print(issue)
    return 1 if payload["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
