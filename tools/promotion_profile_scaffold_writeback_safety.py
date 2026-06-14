#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import promotion_launch_readiness_gate as readiness
import promotion_profile_text_import as profile_import


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_PROOF_FILES = (
    SOURCE_DIR / "proof-youtube_shorts.txt",
    SOURCE_DIR / "proof-tiktok.txt",
    SOURCE_DIR / "proof-instagram_reels.txt",
)
EXPECTED_REJECTION = "proof_note must replace placeholder proof text with real evidence"
TODAY = date.today().isoformat()
REAL_PROOF_BY_PLATFORM = {
    "youtube_shorts": f"screenshot actual-youtube-shorts-bio-{TODAY}.png profile URL clicked https://www.youtube.com/@lovetypes {TODAY}",
    "tiktok": f"screenshot actual-tiktok-bio-{TODAY}.png profile URL clicked https://www.tiktok.com/@lovetypes {TODAY}",
    "instagram_reels": f"screenshot actual-instagram-reels-bio-{TODAY}.png profile URL clicked https://www.instagram.com/lovetypes/ {TODAY}",
}


def run_tool(args: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, "tools/promotion_profile_text_import.py", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout


def patch_profile_paths(temp_root: Path, temp_docs: Path) -> None:
    writeback = profile_import.writeback
    writeback.ROOT = temp_root
    writeback.PROMOTION_DIR = temp_docs
    writeback.TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    writeback.PLAYBOOK_MD = temp_docs / "profile-writeback-playbook.md"
    writeback.PLAYBOOK_JSON = temp_docs / "profile-writeback-playbook.json"
    writeback.regenerate_dependent_docs = lambda: None
    readiness.ROOT = temp_root
    readiness.PROMOTION_DIR = temp_docs
    readiness.PROFILE_TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    readiness.POSTING_QUEUE_PATH = temp_docs / "posting-queue.csv"
    readiness.KPI_TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    readiness.COMMAND_CENTER_PATH = temp_docs / "launch-command-center.json"
    readiness.DEFAULT_OUTPUT_PATH = temp_docs / "launch-readiness-gate.md"
    readiness.DEFAULT_JSON_OUTPUT_PATH = temp_docs / "launch-readiness-gate.json"


def real_profile_text(text: str) -> str:
    data, issues = profile_import.parse_text(text)
    if issues:
        raise SystemExit("\n".join(issues))
    platform = data["platform"]
    lines = []
    for line in text.splitlines():
        lower = line.lower()
        if lower.startswith("proof_note:"):
            lines.append(f"proof_note: {REAL_PROOF_BY_PLATFORM[platform]}")
        elif lower.startswith("set_date:"):
            lines.append(f"set_date: {TODAY}")
        else:
            lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def build_readiness_state(temp_docs: Path) -> dict:
    return readiness.build_gate(
        readiness.read_csv(temp_docs / "platform-profile-tracker.csv"),
        readiness.read_csv(temp_docs / "posting-queue.csv"),
        readiness.read_csv(temp_docs / "kpi-tracker.csv"),
        readiness.read_json(temp_docs / "launch-command-center.json"),
    )


def main() -> int:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="lovetypes-profile-scaffold-") as temp_name:
        temp_root = Path(temp_name)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)

        checked = 0
        rejected = 0
        accepted = 0
        for proof_file in PROFILE_PROOF_FILES:
            temp_proof = temp_docs / proof_file.name
            code, output = run_tool(["check", "--input", str(temp_proof)], ROOT)
            checked += 1
            if code != 0 or "promotion_profile_text_import_issues=0" not in output:
                issues.append(f"{proof_file.name}: scaffold should remain checkable for formatting\n{output}")
            code, output = run_tool(["add", "--input", str(temp_proof)], ROOT)
            if code != 0 and EXPECTED_REJECTION in output:
                rejected += 1
            else:
                issues.append(f"{proof_file.name}: scaffold add should be rejected\n{output}")

        patch_profile_paths(temp_root, temp_docs)
        for proof_file in PROFILE_PROOF_FILES:
            text = real_profile_text(proof_file.read_text(encoding="utf-8"))
            data, parse_issues = profile_import.parse_text(text)
            if parse_issues:
                issues.append(f"{proof_file.name}: real proof should parse\n" + "\n".join(parse_issues))
                continue
            try:
                profile_import.add_profile(data, "")
            except SystemExit as exc:
                issues.append(f"{proof_file.name}: real proof add should be accepted\n{exc}")
                continue
            accepted += 1
        gate = build_readiness_state(temp_docs)
        profile_configured = int(gate.get("metrics", {}).get("profileConfigured") or 0)
        ready_to_publish = int(bool(gate.get("readiness", {}).get("readyToPublishPosts")))
        if profile_configured != 3:
            issues.append(f"real proof add should configure 3 profiles, got {profile_configured}")
        if ready_to_publish != 1:
            issues.append("real proof add should open ready_to_publish")

    print(f"promotion_profile_scaffold_writeback_safety_checked={checked}")
    print(f"promotion_profile_scaffold_writeback_safety_rejected={rejected}")
    print(f"promotion_profile_scaffold_writeback_safety_real_proof_accepted={accepted}")
    print(f"promotion_profile_scaffold_writeback_safety_profile_configured={profile_configured}")
    print(f"promotion_profile_scaffold_writeback_safety_ready_to_publish={ready_to_publish}")
    print(f"promotion_profile_scaffold_writeback_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
