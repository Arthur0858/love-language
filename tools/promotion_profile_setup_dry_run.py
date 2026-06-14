#!/usr/bin/env python3
from __future__ import annotations

import csv
import shutil
import tempfile
from pathlib import Path

import promotion_launch_readiness_gate as readiness
import promotion_profile_text_import as text_import
import promotion_profile_writeback as writeback


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_PROOF_FILE_CANDIDATES = (
    SOURCE_DIR / "proof-youtube_shorts.txt",
    SOURCE_DIR / "proof-tiktok.txt",
    SOURCE_DIR / "proof-instagram_reels.txt",
)
GENERIC_PROOF = "profile link manually verified"
REAL_PROOF_BY_PLATFORM = {
    "youtube_shorts": "dry-run public profile URL clicked https://www.youtube.com/@lovetypes",
    "tiktok": "dry-run public profile URL clicked https://www.tiktok.com/@lovetypes",
    "instagram_reels": "dry-run public profile URL clicked https://www.instagram.com/lovetypes/",
}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def patch_paths(temp_root: Path, temp_docs: Path) -> None:
    writeback.ROOT = temp_root
    writeback.PROMOTION_DIR = temp_docs
    writeback.TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    writeback.PLAYBOOK_MD = temp_docs / "profile-writeback-playbook.md"
    writeback.PLAYBOOK_JSON = temp_docs / "profile-writeback-playbook.json"
    readiness.ROOT = temp_root
    readiness.PROMOTION_DIR = temp_docs
    readiness.PROFILE_TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    readiness.POSTING_QUEUE_PATH = temp_docs / "posting-queue.csv"
    readiness.KPI_TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    readiness.COMMAND_CENTER_PATH = temp_docs / "launch-command-center.json"
    readiness.DEFAULT_OUTPUT_PATH = temp_docs / "launch-readiness-gate.md"
    readiness.DEFAULT_JSON_OUTPUT_PATH = temp_docs / "launch-readiness-gate.json"


def update_from_text(text: str, rows: list[dict[str, str]]) -> None:
    data, issues = text_import.parse_text(text)
    if issues:
        raise SystemExit("\n".join(issues))
    writeback.update_row(
        rows,
        data["platform"],
        data["status"],
        data["set_date"],
        data.get("proof_note", ""),
        {field: data.get(field, "") for field in writeback.METRIC_FIELDS},
    )


def platform_from_text(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("platform:"):
            return line.split(":", 1)[1].strip()
    return ""


def current_profile_platforms() -> set[str]:
    _, rows = read_rows(SOURCE_DIR / "platform-profile-tracker.csv")
    return {
        (row.get("platform") or "").strip()
        for row in rows
        if (row.get("platform") or "").strip()
    }


def current_profile_proof_files() -> tuple[Path, ...]:
    active_platforms = current_profile_platforms()
    files: list[Path] = []
    for proof_file in PROFILE_PROOF_FILE_CANDIDATES:
        if platform_from_text(proof_file.read_text(encoding="utf-8")) in active_platforms:
            files.append(proof_file)
    return tuple(files)


def real_proof_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    platform = platform_from_text(text)
    lines = []
    for line in text.splitlines():
        if line.lower().startswith("proof_note:"):
            lines.append(f"proof_note: {REAL_PROOF_BY_PLATFORM[platform]}")
        else:
            lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def expect_rejected(action) -> bool:
    try:
        action()
    except SystemExit:
        return True
    return False


def build_readiness_state(temp_docs: Path) -> dict:
    return readiness.build_gate(
        readiness.read_csv(temp_docs / "platform-profile-tracker.csv"),
        readiness.read_csv(temp_docs / "posting-queue.csv"),
        readiness.read_csv(temp_docs / "kpi-tracker.csv"),
        readiness.read_json(temp_docs / "launch-command-center.json"),
    )


def wrong_platform_text() -> str:
    text = (SOURCE_DIR / "proof-youtube_shorts.txt").read_text(encoding="utf-8")
    return text.replace("utm_source=youtube", "utm_source=tiktok").replace("youtube_shorts_bio", "tiktok_bio")


def generic_proof_text() -> str:
    text = (SOURCE_DIR / "proof-youtube_shorts.txt").read_text(encoding="utf-8")
    lines = []
    for line in text.splitlines():
        if line.lower().startswith("proof_note:"):
            lines.append(f"proof_note: {GENERIC_PROOF}")
        else:
            lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def run_dry_run() -> dict[str, int]:
    watched_files = (SOURCE_DIR / "platform-profile-tracker.csv", SOURCE_DIR / "launch-readiness-gate.json")
    source_before = {path: path.read_text(encoding="utf-8") for path in watched_files}
    profile_proof_files = current_profile_proof_files()
    if not profile_proof_files:
        raise SystemExit("no current profile proof files found")
    with tempfile.TemporaryDirectory() as tmp:
        temp_root = Path(tmp)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)
        patch_paths(temp_root, temp_docs)

        tracker = temp_docs / "platform-profile-tracker.csv"
        fieldnames, rows = read_rows(tracker)
        for row in rows:
            row["status"] = "planned"
            row["profile_link_set_date"] = ""
        write_rows(tracker, fieldnames, rows)
        initial_gate = build_readiness_state(temp_docs)
        initial_ready = int(bool(initial_gate.get("readiness", {}).get("readyToPublishPosts")))

        placeholder_rejected = 0
        for proof_file in profile_proof_files:
            if expect_rejected(lambda proof_file=proof_file: update_from_text(proof_file.read_text(encoding="utf-8"), rows)):
                placeholder_rejected += 1

        imported = 0
        for proof_file in profile_proof_files:
            update_from_text(real_proof_text(proof_file), rows)
            imported += 1
        issues = writeback.validate_tracker(fieldnames, rows)
        if issues:
            raise SystemExit("\n".join(issues))
        write_rows(tracker, fieldnames, rows)
        final_gate = build_readiness_state(temp_docs)
        final_metrics = final_gate.get("metrics", {})
        final_readiness = final_gate.get("readiness", {})

        generic_rejected = expect_rejected(lambda: update_from_text(generic_proof_text(), rows))
        wrong_link_rejected = expect_rejected(lambda: update_from_text(wrong_platform_text(), rows))
        current_files_mutated = any(path.read_text(encoding="utf-8") != before for path, before in source_before.items())

        return {
            "promotion_profile_setup_dry_run_placeholder_rejected": placeholder_rejected,
            "promotion_profile_setup_dry_run_imports": imported,
            "promotion_profile_setup_dry_run_initial_ready": initial_ready,
            "promotion_profile_setup_dry_run_configured": int(final_metrics.get("profileConfigured") or 0),
            "promotion_profile_setup_dry_run_ready_to_publish": int(bool(final_readiness.get("readyToPublishPosts"))),
            "promotion_profile_setup_dry_run_generic_proof_rejected": int(generic_rejected),
            "promotion_profile_setup_dry_run_wrong_link_rejected": int(wrong_link_rejected),
            "promotion_profile_setup_dry_run_current_files_mutated": int(current_files_mutated),
        }


def main() -> int:
    metrics = run_dry_run()
    expected_profiles = len(current_profile_proof_files())
    issues: list[str] = []
    if metrics["promotion_profile_setup_dry_run_placeholder_rejected"] != expected_profiles:
        issues.append(f"expected {expected_profiles} placeholder profile proof import(s) to be rejected")
    if metrics["promotion_profile_setup_dry_run_imports"] != expected_profiles:
        issues.append(f"expected {expected_profiles} profile proof import(s)")
    if metrics["promotion_profile_setup_dry_run_initial_ready"] != 0:
        issues.append("profile dry run should start with publishing closed")
    if metrics["promotion_profile_setup_dry_run_configured"] != expected_profiles:
        issues.append(f"dry run should configure all {expected_profiles} profile(s)")
    if metrics["promotion_profile_setup_dry_run_ready_to_publish"] != 1:
        issues.append(f"all {expected_profiles} profile proof(s) should open ready_to_publish in dry run")
    if metrics["promotion_profile_setup_dry_run_generic_proof_rejected"] != 1:
        issues.append("generic proof note should be rejected")
    if metrics["promotion_profile_setup_dry_run_wrong_link_rejected"] != 1:
        issues.append("wrong platform profile link should be rejected")
    if metrics["promotion_profile_setup_dry_run_current_files_mutated"] != 0:
        issues.append("dry run mutated current tracker files")

    for key, value in metrics.items():
        print(f"{key}={value}")
    print(f"promotion_profile_setup_dry_run_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
