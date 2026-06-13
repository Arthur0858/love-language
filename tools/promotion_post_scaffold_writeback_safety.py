#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
from datetime import date
from pathlib import Path

import promotion_post_text_import as post_import
import promotion_publishing_status as publishing_status
import promotion_profile_writeback as profile_writeback


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
POST_PROOF_FILES = (
    SOURCE_DIR / "proof-youtube_shorts-publish-lt-s01-iris-silence.txt",
    SOURCE_DIR / "proof-tiktok-publish-lt-s01-iris-silence.txt",
    SOURCE_DIR / "proof-instagram_reels-publish-lt-s01-iris-silence.txt",
)
SAMPLE_POST_URLS = {
    "youtube_shorts": "https://www.youtube.com/shorts/lovetypes-real-proof-dry-run",
    "tiktok": "https://www.tiktok.com/@lovetypes/video/1234567890123456789",
    "instagram_reels": "https://www.instagram.com/reel/lovetypesrealproofdryrun/",
}
WATCHED_FILES = (
    SOURCE_DIR / "posting-queue.csv",
    SOURCE_DIR / "platform-kpi-tracker.csv",
    SOURCE_DIR / "kpi-tracker.csv",
)
TODAY = date.today().isoformat()


def file_hashes(paths: tuple[Path, ...]) -> dict[Path, str]:
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def platform_from_text(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("platform:"):
            return line.split(":", 1)[1].strip()
    return ""


def real_post_text(text: str) -> str:
    platform = platform_from_text(text)
    lines = []
    for line in text.splitlines():
        lower = line.lower()
        if lower.startswith("post_url:"):
            lines.append(f"post_url: {SAMPLE_POST_URLS[platform]}")
        elif lower.startswith("published_date:"):
            lines.append(f"published_date: {TODAY}")
        elif lower.startswith("proof_note:"):
            lines.append(f"proof_note: public URL and analytics source checked {TODAY}")
        else:
            lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def patch_paths(temp_root: Path, temp_docs: Path) -> None:
    writeback = post_import.writeback
    writeback.ROOT = temp_root
    writeback.PROMOTION_DIR = temp_docs
    writeback.QUEUE_PATH = temp_docs / "posting-queue.csv"
    writeback.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"
    writeback.SCRIPT_TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    writeback.PROFILE_TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    writeback.PLAYBOOK_MD = temp_docs / "post-writeback-playbook.md"
    writeback.PLAYBOOK_JSON = temp_docs / "post-writeback-playbook.json"
    writeback.regenerate_dependent_docs = lambda: None
    profile_writeback.ROOT = temp_root
    profile_writeback.PROMOTION_DIR = temp_docs
    profile_writeback.TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    publishing_status.ROOT = temp_root
    publishing_status.PROMOTION_DIR = temp_docs
    publishing_status.QUEUE_PATH = temp_docs / "posting-queue.csv"
    publishing_status.TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    publishing_status.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def configure_profile_gate(temp_docs: Path) -> None:
    fields, rows = read_csv(temp_docs / "platform-profile-tracker.csv")
    for row in rows:
        row["status"] = "set"
        row["profile_link_set_date"] = TODAY
        row["notes"] = f"verified:{TODAY} dry-run profile link proof checked"
    issues = profile_writeback.validate_tracker(fields, rows)
    if issues:
        raise SystemExit("\n".join(issues))
    write_csv(temp_docs / "platform-profile-tracker.csv", fields, rows)


def build_publishing_status(temp_docs: Path) -> dict:
    return publishing_status.build_report(
        *publishing_status.read_csv(temp_docs / "posting-queue.csv"),
        *publishing_status.read_csv(temp_docs / "kpi-tracker.csv"),
        *publishing_status.read_csv(temp_docs / "platform-kpi-tracker.csv"),
    )


def main() -> int:
    issues: list[str] = []
    before = file_hashes(WATCHED_FILES)
    with tempfile.TemporaryDirectory(prefix="lovetypes-post-scaffold-") as temp_name:
        temp_root = Path(temp_name)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)
        patch_paths(temp_root, temp_docs)

        scaffold_checked = 0
        scaffold_rejected = 0
        profile_gate_rejected = 0
        real_accepted = 0
        real_texts: list[tuple[str, str]] = []
        for proof_file in POST_PROOF_FILES:
            text = proof_file.read_text(encoding="utf-8")
            _, scaffold_issues = post_import.parse_text(text)
            scaffold_checked += 1
            if scaffold_issues and any("non-placeholder https post_url" in issue for issue in scaffold_issues):
                scaffold_rejected += 1
            else:
                issues.append(f"{proof_file.name}: scaffold post URL should be rejected before add")

            real_text = real_post_text(text)
            real_texts.append((proof_file.name, real_text))
            data, parse_issues = post_import.parse_text(real_text)
            if parse_issues:
                issues.append(f"{proof_file.name}: real post proof should parse\n" + "\n".join(parse_issues))
                continue
            try:
                post_import.add_post(data, "")
            except SystemExit as exc:
                if "all platform profile links must be set/live" in str(exc):
                    profile_gate_rejected += 1
                else:
                    issues.append(f"{proof_file.name}: real post add should be blocked only by profile gate before profile setup\n{exc}")
            else:
                issues.append(f"{proof_file.name}: real post add should be rejected before profile gate is configured")

        configure_profile_gate(temp_docs)

        for proof_name, real_text in real_texts:
            data, parse_issues = post_import.parse_text(real_text)
            if parse_issues:
                continue
            try:
                post_import.add_post(data, "")
            except SystemExit as exc:
                issues.append(f"{proof_name}: real post add should be accepted after profile gate\n{exc}")
                continue
            real_accepted += 1

        _, queue_rows = read_csv(temp_docs / "posting-queue.csv")
        _, platform_rows = read_csv(temp_docs / "platform-kpi-tracker.csv")
        _, script_rows = read_csv(temp_docs / "kpi-tracker.csv")
        published_rows = sum(1 for row in queue_rows if row.get("week") == "1" and row.get("slot") == "1" and row.get("status") == "published")
        platform_minimum_rows = sum(
            1 for row in platform_rows
            if row.get("week") == "1"
            and row.get("slot") == "1"
            and all((row.get(field) or "").strip() != "" for field in post_import.writeback.MINIMUM_KPI_FIELDS)
        )
        script_rollup_ready = sum(
            1 for row in script_rows
            if row.get("script_id") == "lt-s01-iris-silence"
            and row.get("post_url")
            and all((row.get(field) or "").strip() != "" for field in post_import.writeback.MINIMUM_KPI_FIELDS)
        )
        publishing = build_publishing_status(temp_docs)
        current_files_mutated = before != file_hashes(WATCHED_FILES)

    if published_rows != 3:
        issues.append(f"real post add should publish 3 first-batch rows, got {published_rows}")
    if platform_minimum_rows != 3:
        issues.append(f"real post add should fill 3 minimum KPI rows, got {platform_minimum_rows}")
    if profile_gate_rejected != 3:
        issues.append(f"real post add should reject 3 rows before profile gate, got {profile_gate_rejected}")
    if script_rollup_ready != 1:
        issues.append("real post add should roll up the Iris script tracker")
    if not publishing.get("readyForWeeklyDecision"):
        issues.append("real post add should open publishing readyForWeeklyDecision in dry run")
    if current_files_mutated:
        issues.append("post scaffold writeback safety mutated current tracker files")

    print(f"promotion_post_scaffold_writeback_safety_scaffold_checked={scaffold_checked}")
    print(f"promotion_post_scaffold_writeback_safety_scaffold_rejected={scaffold_rejected}")
    print(f"promotion_post_scaffold_writeback_safety_profile_gate_rejected={profile_gate_rejected}")
    print(f"promotion_post_scaffold_writeback_safety_real_proof_accepted={real_accepted}")
    print(f"promotion_post_scaffold_writeback_safety_published_rows={published_rows}")
    print(f"promotion_post_scaffold_writeback_safety_minimum_kpi_rows={platform_minimum_rows}")
    print(f"promotion_post_scaffold_writeback_safety_script_rollup_ready={script_rollup_ready}")
    print(f"promotion_post_scaffold_writeback_safety_publishing_ready={int(bool(publishing.get('readyForWeeklyDecision')))}")
    print(f"promotion_post_scaffold_writeback_safety_current_files_mutated={int(current_files_mutated)}")
    print(f"promotion_post_scaffold_writeback_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
