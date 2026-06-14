#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from promotion_proof_note_policy import has_traceable_evidence, proof_note_issue


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
DOC_SUFFIXES = (".md", ".json", ".csv")
GENERIC_NOTES = (
    "manual profile link verified",
    "manual post URL verified",
    "post URL and first metrics verified",
    "email request verified",
    "verified",
)
GENERIC_DOC_NOTES = tuple(note for note in GENERIC_NOTES if note != "verified")
FORBIDDEN_GENERATED_PROOF_PHRASES = (
    "public URL and analytics source checked 20",
    "public URL and analytics source checked YYYY-MM-DD",
    "platform analytics checked 20",
)
TRACEABLE_NOTES = (
    "screenshot profile-youtube_shorts-2026-06-15.png verified",
    "public URL post checked 2026-06-15",
    "email thread Gmail abc123 checked 2026-06-15",
    "https://www.youtube.com/shorts/lovetypes-proof-url-123 opened in public browser",
)
SAFE_POST_URL = "https://www.youtube.com/shorts/lovetypes-proof-url-123"
SAFE_PROFILE_URL = "https://lovetypes.tw/start/?utm_source=youtube&utm_medium=social_profile&utm_campaign=first_round_quiz_completion&utm_content=youtube_shorts_bio"


def run_command(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    generic_rejected = 0
    traceable_accepted = 0
    for note in GENERIC_NOTES:
        if has_traceable_evidence(note):
            issues.append(f"generic note should be rejected: {note}")
        else:
            generic_rejected += 1
    for note in TRACEABLE_NOTES:
        if has_traceable_evidence(note) and not proof_note_issue(note):
            traceable_accepted += 1
        else:
            issues.append(f"traceable note should be accepted: {note}")

    generic_profile_code, _ = run_command([
        sys.executable,
        "tools/promotion_profile_writeback.py",
        "update",
        "--platform",
        "youtube_shorts",
        "--status",
        "set",
        "--set-date",
        "2026-06-15",
        "--proof-note",
        "manual profile link verified",
    ])
    generic_post_code, _ = run_command([
        sys.executable,
        "tools/promotion_post_writeback.py",
        "update",
        "--platform",
        "youtube_shorts",
        "--task-id",
        "publish-lt-s01-iris-silence",
        "--status",
        "published",
        "--published-date",
        "2026-06-15",
        "--post-url",
        SAFE_POST_URL,
        "--proof-note",
        "manual post URL verified",
    ])
    if generic_profile_code == 0:
        issues.append("profile writeback should reject generic proof note")
    if generic_post_code == 0:
        issues.append("post writeback should reject generic proof note")
    docs_checked = 0
    doc_hits = 0
    for path in sorted(PROMOTION_DIR.glob("*")):
        if path.suffix not in DOC_SUFFIXES:
            continue
        docs_checked += 1
        text = path.read_text(encoding="utf-8")
        for note in GENERIC_DOC_NOTES:
            if note in text:
                doc_hits += 1
                issues.append(f"{path.relative_to(ROOT)} should not contain generic proof note: {note}")
        for phrase in FORBIDDEN_GENERATED_PROOF_PHRASES:
            if phrase in text:
                doc_hits += 1
                issues.append(f"{path.relative_to(ROOT)} should not contain scaffold proof phrase: {phrase}")

    return {
        "genericNotes": len(GENERIC_NOTES),
        "genericRejected": generic_rejected,
        "traceableNotes": len(TRACEABLE_NOTES),
        "traceableAccepted": traceable_accepted,
        "genericProfileRejected": 1 if generic_profile_code != 0 else 0,
        "genericPostRejected": 1 if generic_post_code != 0 else 0,
        "docsChecked": docs_checked,
        "docHits": doc_hits,
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_proof_note_generic_checked={metrics['genericNotes']}")
    print(f"promotion_proof_note_generic_rejected={metrics['genericRejected']}")
    print(f"promotion_proof_note_traceable_checked={metrics['traceableNotes']}")
    print(f"promotion_proof_note_traceable_accepted={metrics['traceableAccepted']}")
    print(f"promotion_proof_note_profile_writeback_rejected={metrics['genericProfileRejected']}")
    print(f"promotion_proof_note_post_writeback_rejected={metrics['genericPostRejected']}")
    print(f"promotion_proof_note_docs_checked={metrics['docsChecked']}")
    print(f"promotion_proof_note_doc_hits={metrics['docHits']}")
    print(f"promotion_proof_note_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
