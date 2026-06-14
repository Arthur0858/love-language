#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from datetime import date
from pathlib import Path

import promotion_evidence_ledger as evidence_ledger
import promotion_first_batch_completion_gate as first_batch_completion
import promotion_first_batch_publication_packet as first_batch_packet
import promotion_launch_readiness_gate as readiness
import promotion_post_text_import as post_import
import promotion_post_writeback as post_writeback
import promotion_profile_completion_gate as profile_completion
import promotion_profile_text_import as profile_import
import promotion_profile_verification_packet as profile_packet
import promotion_profile_writeback as profile_writeback
import promotion_publishing_status as publishing_status


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
REPORT_MD = SOURCE_DIR / "launch-sequence-dry-run.md"
REPORT_JSON = SOURCE_DIR / "launch-sequence-dry-run.json"
PROFILE_PROOF_FILES = (
    SOURCE_DIR / "proof-youtube_shorts.txt",
    SOURCE_DIR / "proof-tiktok.txt",
    SOURCE_DIR / "proof-instagram_reels.txt",
)
POST_PROOF_FILES = (
    SOURCE_DIR / "proof-youtube_shorts-publish-lt-s01-iris-silence.txt",
    SOURCE_DIR / "proof-tiktok-publish-lt-s01-iris-silence.txt",
    SOURCE_DIR / "proof-instagram_reels-publish-lt-s01-iris-silence.txt",
)
SAMPLE_POST_URLS = {
    "youtube_shorts": "https://www.youtube.com/shorts/lovetypes-sequence-dry-run",
    "tiktok": "https://www.tiktok.com/@lovetypes/video/1234567890123456789",
    "instagram_reels": "https://www.instagram.com/reel/lovetypessequencedryrun/",
}
WATCHED_FILES = (
    SOURCE_DIR / "platform-profile-tracker.csv",
    SOURCE_DIR / "posting-queue.csv",
    SOURCE_DIR / "platform-kpi-tracker.csv",
    SOURCE_DIR / "kpi-tracker.csv",
)
TODAY = date.today().isoformat()


def file_hashes(paths: tuple[Path, ...]) -> dict[Path, str]:
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_paths(temp_root: Path, temp_docs: Path) -> None:
    profile_writeback.ROOT = temp_root
    profile_writeback.PROMOTION_DIR = temp_docs
    profile_writeback.TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    profile_writeback.PLAYBOOK_MD = temp_docs / "profile-writeback-playbook.md"
    profile_writeback.PLAYBOOK_JSON = temp_docs / "profile-writeback-playbook.json"

    readiness.ROOT = temp_root
    readiness.PROMOTION_DIR = temp_docs
    readiness.PROFILE_TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    readiness.POSTING_QUEUE_PATH = temp_docs / "posting-queue.csv"
    readiness.KPI_TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    readiness.COMMAND_CENTER_PATH = temp_docs / "launch-command-center.json"
    readiness.DEFAULT_OUTPUT_PATH = temp_docs / "launch-readiness-gate.md"
    readiness.DEFAULT_JSON_OUTPUT_PATH = temp_docs / "launch-readiness-gate.json"

    profile_packet.ROOT = temp_root
    profile_packet.PROMOTION_DIR = temp_docs
    profile_packet.TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    profile_packet.SETUP_PATH = temp_docs / "platform-profile-setup.json"
    profile_packet.READINESS_PATH = temp_docs / "launch-readiness-gate.json"
    profile_packet.DEFAULT_OUTPUT_PATH = temp_docs / "profile-verification-packet.md"
    profile_packet.DEFAULT_JSON_OUTPUT_PATH = temp_docs / "profile-verification-packet.json"

    profile_completion.ROOT = temp_root
    profile_completion.PROMOTION_DIR = temp_docs
    profile_completion.READINESS_PATH = temp_docs / "launch-readiness-gate.json"
    profile_completion.EVIDENCE_PATH = temp_docs / "evidence-ledger.json"
    profile_completion.PROFILE_PACKET_PATH = temp_docs / "profile-verification-packet.json"
    profile_completion.FIRST_BATCH_PACKET_PATH = temp_docs / "first-batch-publication-packet.json"
    profile_completion.MD_OUTPUT = temp_docs / "profile-completion-gate.md"
    profile_completion.JSON_OUTPUT = temp_docs / "profile-completion-gate.json"

    post_writeback.ROOT = temp_root
    post_writeback.PROMOTION_DIR = temp_docs
    post_writeback.QUEUE_PATH = temp_docs / "posting-queue.csv"
    post_writeback.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"
    post_writeback.SCRIPT_TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    post_writeback.PROFILE_TRACKER_PATH = temp_docs / "platform-profile-tracker.csv"
    post_writeback.PLAYBOOK_MD = temp_docs / "post-writeback-playbook.md"
    post_writeback.PLAYBOOK_JSON = temp_docs / "post-writeback-playbook.json"

    publishing_status.ROOT = temp_root
    publishing_status.PROMOTION_DIR = temp_docs
    publishing_status.QUEUE_PATH = temp_docs / "posting-queue.csv"
    publishing_status.TRACKER_PATH = temp_docs / "kpi-tracker.csv"
    publishing_status.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"
    publishing_status.DEFAULT_OUTPUT_PATH = temp_docs / "publishing-status.md"
    publishing_status.DEFAULT_JSON_OUTPUT_PATH = temp_docs / "publishing-status.json"

    first_batch_packet.ROOT = temp_root
    first_batch_packet.PROMOTION_DIR = temp_docs
    first_batch_packet.QUEUE_PATH = temp_docs / "posting-queue.csv"
    first_batch_packet.PLATFORM_TRACKER_PATH = temp_docs / "platform-kpi-tracker.csv"
    first_batch_packet.PUBLISHING_STATUS_PATH = temp_docs / "publishing-status.json"
    first_batch_packet.READINESS_PATH = temp_docs / "launch-readiness-gate.json"
    first_batch_packet.DEFAULT_OUTPUT_PATH = temp_docs / "first-batch-publication-packet.md"
    first_batch_packet.DEFAULT_JSON_OUTPUT_PATH = temp_docs / "first-batch-publication-packet.json"

    evidence_ledger.ROOT = temp_root
    evidence_ledger.PROMOTION_DIR = temp_docs
    evidence_ledger.PROFILE_TRACKER = temp_docs / "platform-profile-tracker.csv"
    evidence_ledger.POSTING_QUEUE = temp_docs / "posting-queue.csv"
    evidence_ledger.LEAD_TRACKER = temp_docs / "lead-intake-tracker.csv"
    evidence_ledger.CSV_OUTPUT = temp_docs / "evidence-ledger.csv"
    evidence_ledger.JSON_OUTPUT = temp_docs / "evidence-ledger.json"
    evidence_ledger.MD_OUTPUT = temp_docs / "evidence-ledger.md"

    first_batch_completion.ROOT = temp_root
    first_batch_completion.PROMOTION_DIR = temp_docs
    first_batch_completion.FIRST_BATCH_PACKET = temp_docs / "first-batch-publication-packet.json"
    first_batch_completion.EVIDENCE_LEDGER = temp_docs / "evidence-ledger.json"
    first_batch_completion.PUBLISHING_STATUS = temp_docs / "publishing-status.json"
    first_batch_completion.KPI_CONSISTENCY = temp_docs / "attribution-reconciliation.json"
    first_batch_completion.MD_OUTPUT = temp_docs / "first-batch-completion-gate.md"
    first_batch_completion.JSON_OUTPUT = temp_docs / "first-batch-completion-gate.json"


def build_readiness(temp_docs: Path) -> dict:
    gate = readiness.build_gate(
        readiness.read_csv(temp_docs / "platform-profile-tracker.csv"),
        readiness.read_csv(temp_docs / "posting-queue.csv"),
        readiness.read_csv(temp_docs / "kpi-tracker.csv"),
        readiness.read_json(temp_docs / "launch-command-center.json"),
    )
    write_json(temp_docs / "launch-readiness-gate.json", gate)
    return gate


def build_profile_packet(temp_docs: Path) -> dict:
    packet = profile_packet.build_packet()
    issues = profile_packet.validate_packet(packet)
    if issues:
        raise SystemExit("\n".join(issues))
    write_json(temp_docs / "profile-verification-packet.json", packet)
    return packet


def build_first_batch_packet(temp_docs: Path) -> dict:
    packet = first_batch_packet.build_packet()
    issues = first_batch_packet.validate_packet(packet)
    if issues:
        raise SystemExit("\n".join(issues))
    write_json(temp_docs / "first-batch-publication-packet.json", packet)
    return packet


def build_evidence(temp_docs: Path) -> dict:
    payload = evidence_ledger.summarize(evidence_ledger.build_rows())
    write_json(temp_docs / "evidence-ledger.json", payload)
    return payload


def build_publishing(temp_docs: Path) -> dict:
    report = publishing_status.build_report(
        *publishing_status.read_csv(temp_docs / "posting-queue.csv"),
        *publishing_status.read_csv(temp_docs / "kpi-tracker.csv"),
        *publishing_status.read_csv(temp_docs / "platform-kpi-tracker.csv"),
    )
    write_json(temp_docs / "publishing-status.json", report)
    return report


def update_profile_from_text(text: str, rows: list[dict[str, str]]) -> None:
    data, issues = profile_import.parse_text(text)
    if issues:
        raise SystemExit("\n".join(issues))
    profile_writeback.update_row(
        rows,
        data["platform"],
        data["status"],
        data["set_date"],
        data.get("proof_note", ""),
        {field: data.get(field, "") for field in profile_writeback.METRIC_FIELDS},
    )


def platform_from_text(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("platform:"):
            return line.split(":", 1)[1].strip()
    return ""


def sample_post_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
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


def update_post_from_text(
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


def run_sequence() -> dict[str, int]:
    before = file_hashes(WATCHED_FILES)
    with tempfile.TemporaryDirectory(prefix="lovetypes-launch-sequence-") as temp_name:
        temp_root = Path(temp_name)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)
        patch_paths(temp_root, temp_docs)

        profile_fields, profile_rows = read_csv(temp_docs / "platform-profile-tracker.csv")
        initial_readiness = build_readiness(temp_docs)
        profile_imports = 0
        for proof_file in PROFILE_PROOF_FILES:
            update_profile_from_text(proof_file.read_text(encoding="utf-8"), profile_rows)
            profile_imports += 1
        profile_issues = profile_writeback.validate_tracker(profile_fields, profile_rows)
        if profile_issues:
            raise SystemExit("\n".join(profile_issues))
        write_csv(temp_docs / "platform-profile-tracker.csv", profile_fields, profile_rows)

        profile_readiness = build_readiness(temp_docs)
        build_profile_packet(temp_docs)
        build_publishing(temp_docs)
        build_first_batch_packet(temp_docs)
        build_evidence(temp_docs)
        profile_gate = profile_completion.build_gate()
        write_json(temp_docs / "profile-completion-gate.json", profile_gate)

        queue_fields, queue_rows = read_csv(temp_docs / "posting-queue.csv")
        platform_fields, platform_rows = read_csv(temp_docs / "platform-kpi-tracker.csv")
        script_fields, script_rows = read_csv(temp_docs / "kpi-tracker.csv")
        post_imports = 0
        for proof_file in POST_PROOF_FILES:
            update_post_from_text(sample_post_text(proof_file), queue_rows, platform_rows, script_rows)
            post_imports += 1
        post_issues = post_writeback.validate_rows(queue_fields, queue_rows, platform_fields, platform_rows, script_fields, script_rows)
        if post_issues:
            raise SystemExit("\n".join(post_issues))
        write_csv(temp_docs / "posting-queue.csv", queue_fields, queue_rows)
        write_csv(temp_docs / "platform-kpi-tracker.csv", platform_fields, platform_rows)
        write_csv(temp_docs / "kpi-tracker.csv", script_fields, script_rows)

        publishing = build_publishing(temp_docs)
        first_packet = build_first_batch_packet(temp_docs)
        evidence = build_evidence(temp_docs)
        first_gate = first_batch_completion.build_gate()
        changed = before != file_hashes(WATCHED_FILES)

    return {
        "promotion_launch_sequence_dry_run_initial_ready_to_publish": int(bool(initial_readiness["readiness"]["readyToPublishPosts"])),
        "promotion_launch_sequence_dry_run_profile_imports": profile_imports,
        "promotion_launch_sequence_dry_run_profile_configured": int(profile_readiness["metrics"]["profileConfigured"]),
        "promotion_launch_sequence_dry_run_profile_ready_to_publish": int(bool(profile_readiness["readiness"]["readyToPublishPosts"])),
        "promotion_launch_sequence_dry_run_profile_gate_ready": int(bool(profile_gate["state"]["readyForFirstBatchPublish"])),
        "promotion_launch_sequence_dry_run_post_imports": post_imports,
        "promotion_launch_sequence_dry_run_first_batch_published": int(first_packet["publishedRows"]),
        "promotion_launch_sequence_dry_run_minimum_kpi_rows": int(first_packet["minimumKpiRows"]),
        "promotion_launch_sequence_dry_run_traceable_evidence": int(evidence["metrics"]["traceable"]),
        "promotion_launch_sequence_dry_run_required_evidence": int(evidence["metrics"]["required"]),
        "promotion_launch_sequence_dry_run_publishing_ready": int(bool(publishing["readyForWeeklyDecision"])),
        "promotion_launch_sequence_dry_run_weekly_ready": int(bool(first_gate["state"]["readyForWeeklyReview"])),
        "promotion_launch_sequence_dry_run_current_files_mutated": int(changed),
    }


def validate_metrics(metrics: dict[str, int]) -> list[str]:
    expected = {
        "promotion_launch_sequence_dry_run_initial_ready_to_publish": 0,
        "promotion_launch_sequence_dry_run_profile_imports": 3,
        "promotion_launch_sequence_dry_run_profile_configured": 3,
        "promotion_launch_sequence_dry_run_profile_ready_to_publish": 1,
        "promotion_launch_sequence_dry_run_profile_gate_ready": 1,
        "promotion_launch_sequence_dry_run_post_imports": 3,
        "promotion_launch_sequence_dry_run_first_batch_published": 3,
        "promotion_launch_sequence_dry_run_minimum_kpi_rows": 3,
        "promotion_launch_sequence_dry_run_publishing_ready": 1,
        "promotion_launch_sequence_dry_run_weekly_ready": 1,
        "promotion_launch_sequence_dry_run_current_files_mutated": 0,
    }
    issues = [f"{key} expected {value}, got {metrics.get(key)}" for key, value in expected.items() if metrics.get(key) != value]
    if metrics["promotion_launch_sequence_dry_run_traceable_evidence"] != metrics["promotion_launch_sequence_dry_run_required_evidence"]:
        issues.append("all required profile/post evidence should be traceable in the dry run")
    return issues


def render_markdown(report: dict) -> str:
    metrics = report["metrics"]
    lines = [
        "# LoveTypes Launch Sequence Dry Run",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- initial ready to publish：`{metrics['promotion_launch_sequence_dry_run_initial_ready_to_publish']}`",
        f"- profile imports：{metrics['promotion_launch_sequence_dry_run_profile_imports']}",
        f"- profile configured：{metrics['promotion_launch_sequence_dry_run_profile_configured']}",
        f"- profile ready to publish：`{metrics['promotion_launch_sequence_dry_run_profile_ready_to_publish']}`",
        f"- profile gate ready：`{metrics['promotion_launch_sequence_dry_run_profile_gate_ready']}`",
        f"- post imports：{metrics['promotion_launch_sequence_dry_run_post_imports']}",
        f"- first batch published：{metrics['promotion_launch_sequence_dry_run_first_batch_published']}",
        f"- minimum KPI rows：{metrics['promotion_launch_sequence_dry_run_minimum_kpi_rows']}",
        f"- traceable / required evidence：{metrics['promotion_launch_sequence_dry_run_traceable_evidence']} / {metrics['promotion_launch_sequence_dry_run_required_evidence']}",
        f"- publishing ready：`{metrics['promotion_launch_sequence_dry_run_publishing_ready']}`",
        f"- weekly ready：`{metrics['promotion_launch_sequence_dry_run_weekly_ready']}`",
        f"- current files mutated：`{metrics['promotion_launch_sequence_dry_run_current_files_mutated']}`",
        f"- issues：{len(report['issues'])}",
        "",
        "## Rule",
        "",
        "- This is a temporary-directory dry run; current promotion CSV files must not mutate.",
        "- Profile proof imports must open the profile gate before first-batch post imports.",
        "- Post proof imports must produce three published rows, three minimum KPI rows, and traceable evidence.",
        "- Weekly decision can open only after the simulated post URL and KPI evidence path is complete.",
        "",
    ]
    if report["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in report["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_report(metrics: dict[str, int], issues: list[str]) -> None:
    report = {
        "generatedAt": TODAY,
        "sources": {
            "profileProofFiles": [str(path.relative_to(ROOT)) for path in PROFILE_PROOF_FILES],
            "postProofFiles": [str(path.relative_to(ROOT)) for path in POST_PROOF_FILES],
            "watchedFiles": [str(path.relative_to(ROOT)) for path in WATCHED_FILES],
        },
        "metrics": metrics,
        "issues": issues,
    }
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run the LoveTypes profile to publish to KPI launch sequence.")
    parser.add_argument("--write-report", action="store_true", help="Write a dated md/json dry-run report.")
    args = parser.parse_args()
    metrics = run_sequence()
    issues = validate_metrics(metrics)
    if args.write_report:
        write_report(metrics, issues)
        print(f"promotion_launch_sequence_dry_run_report={REPORT_MD.relative_to(ROOT)}")
        print(f"promotion_launch_sequence_dry_run_report_json={REPORT_JSON.relative_to(ROOT)}")
    for key, value in metrics.items():
        print(f"{key}={value}")
    print(f"promotion_launch_sequence_dry_run_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
