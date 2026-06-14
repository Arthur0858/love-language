#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from datetime import date
from pathlib import Path

import promotion_first_batch_publication_packet as first_batch_packet
import promotion_post_text_import as post_import
import promotion_post_writeback as post_writeback
import promotion_profile_writeback as profile_writeback
import promotion_publishing_status as publishing_status


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
POST_PROOF_FILE_CANDIDATES = (
    SOURCE_DIR / "proof-youtube_shorts-publish-lt-s01-iris-silence.txt",
    SOURCE_DIR / "proof-tiktok-publish-lt-s01-iris-silence.txt",
    SOURCE_DIR / "proof-instagram_reels-publish-lt-s01-iris-silence.txt",
)
SAMPLE_POST_URLS = {
    "youtube_shorts": "https://www.youtube.com/shorts/lovetypes-first-batch-dry-run",
    "tiktok": "https://www.tiktok.com/@lovetypes/video/1234567890123456789",
    "instagram_reels": "https://www.instagram.com/reel/lovetypesdryrun/",
}
TODAY = date.today().isoformat()


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
    post_writeback.ROOT = temp_root
    post_writeback.PROMOTION_DIR = temp_docs
    post_writeback.QUEUE_PATH = temp_docs / "posting-queue.csv"
    post_writeback.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"
    post_writeback.SCRIPT_TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    post_writeback.PROFILE_TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    post_writeback.PLAYBOOK_MD = temp_docs / "post-writeback-playbook.md"
    post_writeback.PLAYBOOK_JSON = temp_docs / "post-writeback-playbook.json"
    profile_writeback.ROOT = temp_root
    profile_writeback.PROMOTION_DIR = temp_docs
    profile_writeback.TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    first_batch_packet.ROOT = temp_root
    first_batch_packet.PROMOTION_DIR = temp_docs
    first_batch_packet.QUEUE_PATH = temp_docs / "posting-queue.csv"
    first_batch_packet.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"
    first_batch_packet.PUBLISHING_STATUS_PATH = temp_docs / "publishing-status.json"
    first_batch_packet.READINESS_PATH = temp_docs / "launch-readiness-gate.json"
    publishing_status.ROOT = temp_root
    publishing_status.PROMOTION_DIR = temp_docs
    publishing_status.QUEUE_PATH = temp_docs / "posting-queue.csv"
    publishing_status.TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    publishing_status.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"


def platform_from_text(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("platform:"):
            return line.split(":", 1)[1].strip()
    return ""


def task_id_from_text(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("task_id:"):
            return line.split(":", 1)[1].strip()
    return ""


def current_first_batch_tasks() -> set[tuple[str, str]]:
    _, rows = read_rows(SOURCE_DIR / "posting-queue.csv")
    return {
        ((row.get("platform") or "").strip(), (row.get("task_id") or "").strip())
        for row in rows
        if row.get("week") == "1"
        and row.get("slot") == "1"
        and (row.get("platform") or "").strip()
        and (row.get("task_id") or "").strip()
    }


def current_post_proof_files() -> tuple[Path, ...]:
    active_tasks = current_first_batch_tasks()
    files: list[Path] = []
    for proof_file in POST_PROOF_FILE_CANDIDATES:
        text = proof_file.read_text(encoding="utf-8")
        if (platform_from_text(text), task_id_from_text(text)) in active_tasks:
            files.append(proof_file)
    return tuple(files)


def sample_post_text(path: Path, *, generic_proof: bool = False, wrong_platform: bool = False) -> str:
    text = path.read_text(encoding="utf-8")
    platform = platform_from_text(text)
    replacement = SAMPLE_POST_URLS[platform]
    if wrong_platform:
        replacement = SAMPLE_POST_URLS["tiktok"] if platform != "tiktok" else SAMPLE_POST_URLS["youtube_shorts"]
    lines = []
    for line in text.splitlines():
        lower = line.lower()
        if lower.startswith("post_url:"):
            lines.append(f"post_url: {replacement}")
        elif lower.startswith("published_date:"):
            lines.append(f"published_date: {TODAY}")
        elif lower.startswith("proof_note:"):
            note = "verified" if generic_proof else f"public URL and analytics source checked {TODAY}"
            lines.append(f"proof_note: {note}")
        else:
            lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def update_from_text(
    text: str,
    queue_rows: list[dict[str, str]],
    platform_rows: list[dict[str, str]],
    script_rows: list[dict[str, str]],
) -> None:
    data, issues = post_import.parse_text(text)
    if issues:
        raise SystemExit("\n".join(issues))
    metrics = {field: data.get(field, "") for field in post_writeback.METRIC_FIELDS}
    queue_row = post_writeback.update_platform_rows(
        queue_rows,
        data["platform"],
        data["task_id"],
        data["status"],
        data["published_date"],
        data["post_url"],
        data.get("proof_note", ""),
        metrics,
    )
    post_writeback.update_platform_rows(
        platform_rows,
        data["platform"],
        data["task_id"],
        data["status"],
        data["published_date"],
        data["post_url"],
        data.get("proof_note", ""),
        metrics,
    )
    post_writeback.rollup_script_tracker(script_rows, platform_rows, queue_row["script_id"])


def configure_profile_gate(temp_docs: Path) -> None:
    fields, rows = read_rows(temp_docs / "platform-profile-tracker.csv")
    for row in rows:
        row["status"] = "set"
        row["profile_link_set_date"] = TODAY
        row["notes"] = f"verified:{TODAY} dry-run profile link proof checked"
    issues = profile_writeback.validate_tracker(fields, rows)
    if issues:
        raise SystemExit("\n".join(issues))
    write_rows(temp_docs / "platform-profile-tracker.csv", fields, rows)


def expect_rejected(action) -> bool:
    try:
        action()
    except SystemExit:
        return True
    return False


def published_first_batch(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("week") == "1" and row.get("slot") == "1" and row.get("status") in post_writeback.PUBLISH_STATUSES
    )


def platform_minimum_rows(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("week") == "1"
        and row.get("slot") == "1"
        and all((row.get(field) or "").strip() != "" for field in post_writeback.MINIMUM_KPI_FIELDS)
    )


def script_rollup_ready(rows: list[dict[str, str]]) -> int:
    for row in rows:
        if row.get("script_id") != "lt-s01-iris-silence":
            continue
        has_publish = all((row.get(field) or "").strip() for field in ("date", "platform", "post_url"))
        has_minimum = all((row.get(field) or "").strip() != "" for field in post_writeback.MINIMUM_KPI_FIELDS)
        return int(has_publish and has_minimum)
    return 0


def run_dry_run() -> dict[str, int]:
    watched_files = (
        SOURCE_DIR / "posting-queue.csv",
        SOURCE_DIR / "platform-kpi-tracker.csv",
        SOURCE_DIR / "kpi-tracker.csv",
    )
    source_before = {path: path.read_text(encoding="utf-8") for path in watched_files}
    post_proof_files = current_post_proof_files()
    if not post_proof_files:
        raise SystemExit("no current first-batch proof files found")
    with tempfile.TemporaryDirectory() as tmp:
        temp_root = Path(tmp)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)
        patch_paths(temp_root, temp_docs)
        configure_profile_gate(temp_docs)

        queue_fields, queue_rows = read_rows(temp_docs / "posting-queue.csv")
        platform_fields, platform_rows = read_rows(temp_docs / "platform-kpi-tracker.csv")
        script_fields, script_rows = read_rows(temp_docs / "kpi-tracker.csv")

        placeholder_rejected = sum(
            1
            for proof_file in post_proof_files
            if post_import.parse_text(proof_file.read_text(encoding="utf-8"))[1]
        )
        generic_proof_rejected = expect_rejected(
            lambda: update_from_text(sample_post_text(post_proof_files[0], generic_proof=True), queue_rows, platform_rows, script_rows)
        )
        wrong_platform_rejected = expect_rejected(
            lambda: update_from_text(sample_post_text(post_proof_files[0], wrong_platform=True), queue_rows, platform_rows, script_rows)
        )

        imports = 0
        for proof_file in post_proof_files:
            update_from_text(sample_post_text(proof_file), queue_rows, platform_rows, script_rows)
            imports += 1
        issues = post_writeback.validate_rows(queue_fields, queue_rows, platform_fields, platform_rows, script_fields, script_rows)
        if issues:
            raise SystemExit("\n".join(issues))
        write_rows(temp_docs / "posting-queue.csv", queue_fields, queue_rows)
        write_rows(temp_docs / "platform-kpi-tracker.csv", platform_fields, platform_rows)
        write_rows(temp_docs / "kpi-tracker.csv", script_fields, script_rows)

        status = publishing_status.build_report(
            *publishing_status.read_csv(temp_docs / "posting-queue.csv"),
            *publishing_status.read_csv(temp_docs / "kpi-tracker.csv"),
            *publishing_status.read_csv(temp_docs / "platform-kpi-tracker.csv"),
        )
        (temp_docs / "publishing-status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        packet = first_batch_packet.build_packet()
        current_files_mutated = any(path.read_text(encoding="utf-8") != before for path, before in source_before.items())

        return {
            "promotion_first_batch_publish_dry_run_imports": imports,
            "promotion_first_batch_publish_dry_run_placeholder_rejected": placeholder_rejected,
            "promotion_first_batch_publish_dry_run_generic_proof_rejected": int(generic_proof_rejected),
            "promotion_first_batch_publish_dry_run_wrong_platform_rejected": int(wrong_platform_rejected),
            "promotion_first_batch_publish_dry_run_published_rows": published_first_batch(queue_rows),
            "promotion_first_batch_publish_dry_run_minimum_kpi_rows": platform_minimum_rows(platform_rows),
            "promotion_first_batch_publish_dry_run_script_rollup_ready": script_rollup_ready(script_rows),
            "promotion_first_batch_publish_dry_run_status_ready": int(bool(status.get("readyForWeeklyDecision"))),
            "promotion_first_batch_publish_dry_run_packet_published": int(packet.get("publishedRows") or 0),
            "promotion_first_batch_publish_dry_run_packet_minimum_kpi": int(packet.get("minimumKpiRows") or 0),
            "promotion_first_batch_publish_dry_run_current_files_mutated": int(current_files_mutated),
        }


def main() -> int:
    metrics = run_dry_run()
    expected_first_batch_rows = len(current_post_proof_files())
    expected = {
        "promotion_first_batch_publish_dry_run_imports": expected_first_batch_rows,
        "promotion_first_batch_publish_dry_run_placeholder_rejected": expected_first_batch_rows,
        "promotion_first_batch_publish_dry_run_generic_proof_rejected": 1,
        "promotion_first_batch_publish_dry_run_wrong_platform_rejected": 1,
        "promotion_first_batch_publish_dry_run_published_rows": expected_first_batch_rows,
        "promotion_first_batch_publish_dry_run_minimum_kpi_rows": expected_first_batch_rows,
        "promotion_first_batch_publish_dry_run_script_rollup_ready": 1,
        "promotion_first_batch_publish_dry_run_status_ready": 1,
        "promotion_first_batch_publish_dry_run_packet_published": expected_first_batch_rows,
        "promotion_first_batch_publish_dry_run_packet_minimum_kpi": expected_first_batch_rows,
        "promotion_first_batch_publish_dry_run_current_files_mutated": 0,
    }
    issues = [f"{key} expected {value}" for key, value in expected.items() if metrics.get(key) != value]
    for key, value in metrics.items():
        print(f"{key}={value}")
    print(f"promotion_first_batch_publish_dry_run_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
