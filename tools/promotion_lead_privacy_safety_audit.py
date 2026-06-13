#!/usr/bin/env python3
from __future__ import annotations

import csv
import shutil
import tempfile
from pathlib import Path

import promotion_lead_text_import as lead_import
import promotion_lead_writeback as writeback


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
RAW_EMAIL = "sample@example.com"
SAFE_PROOF = "email thread Gmail request checked 2026-06-15"
GENERIC_PROOF = "email request verified"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    return int(float(text))


def count_real_leads(path: Path) -> int:
    return sum(1 for row in read_rows(path) if row.get("status") != "template")


def file_contains(root: Path, needle: str) -> int:
    hits = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if needle in path.read_text(encoding="utf-8", errors="ignore"):
            hits += 1
    return hits


def patch_paths(temp_root: Path, temp_docs: Path) -> None:
    writeback.ROOT = temp_root
    writeback.PROMOTION_DIR = temp_docs
    writeback.LEAD_TRACKER = temp_docs / "lead-intake-tracker.csv"
    writeback.ATTRIBUTION_PATH = temp_docs / "attribution-reconciliation.csv"
    writeback.KPI_TRACKER = temp_docs / "kpi-tracker.csv"
    writeback.PROFILE_TRACKER = temp_docs / "platform-profile-tracker.csv"
    writeback.PLAYBOOK_MD = temp_docs / "lead-writeback-playbook.md"
    writeback.PLAYBOOK_JSON = temp_docs / "lead-writeback-playbook.json"


def sample_text(*, utm: str = "iris_silence", consent: str = "explicit_reply_ok") -> str:
    return lead_import.SAMPLE_TEXT.replace("iris_silence", utm).replace("explicit_reply_ok", consent)


def add_from_text(text: str, proof_note: str) -> str:
    data, issues = lead_import.parse_text(text)
    if issues:
        raise SystemExit("\n".join(issues))
    return lead_import.add_lead(data, proof_note=proof_note, request_date="2026-06-15")


def expect_rejected(action) -> bool:
    try:
        action()
    except SystemExit:
        return True
    return False


def kpi_value(path: Path, script_id: str, field: str) -> int:
    for row in read_rows(path):
        if row.get("script_id") == script_id:
            return parse_int(row.get(field))
    raise SystemExit(f"missing KPI script row: {script_id}")


def run_audit() -> dict[str, int]:
    with tempfile.TemporaryDirectory() as tmp:
        temp_docs = Path(tmp) / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)
        patch_paths(Path(tmp), temp_docs)

        lead_tracker = temp_docs / "lead-intake-tracker.csv"
        kpi_tracker = temp_docs / "kpi-tracker.csv"
        profile_tracker = temp_docs / "platform-profile-tracker.csv"
        iris_script = "lt-s01-iris-silence"
        kpi_field = "supply_lead_requests"
        before_kpi = kpi_value(kpi_tracker, iris_script, kpi_field)

        matched_status = add_from_text(sample_text(utm="iris_silence"), SAFE_PROOF)
        after_kpi = kpi_value(kpi_tracker, iris_script, kpi_field)
        raw_email_hits = file_contains(temp_docs, RAW_EMAIL)
        real_rows_after_first = count_real_leads(lead_tracker)

        do_not_contact_rejected = expect_rejected(lambda: add_from_text(sample_text(consent="do_not_contact"), SAFE_PROOF))
        generic_proof_rejected = expect_rejected(lambda: add_from_text(sample_text(utm="iris_affirmation"), GENERIC_PROOF))
        kpi_before_unmatched = kpi_value(kpi_tracker, iris_script, kpi_field)
        unmatched_status = add_from_text(sample_text(utm="unmatched_campaign"), SAFE_PROOF)
        kpi_after_unmatched = kpi_value(kpi_tracker, iris_script, kpi_field)
        profile_raw_email_hits = RAW_EMAIL in profile_tracker.read_text(encoding="utf-8")

        return {
            "promotion_lead_privacy_safe_imports": 1 if matched_status == "kpi_tracker_incremented" else 0,
            "promotion_lead_privacy_real_rows": real_rows_after_first,
            "promotion_lead_privacy_raw_email_hits": raw_email_hits,
            "promotion_lead_privacy_do_not_contact_rejected": 1 if do_not_contact_rejected else 0,
            "promotion_lead_privacy_generic_proof_rejected": 1 if generic_proof_rejected else 0,
            "promotion_lead_privacy_matched_utm_incremented": 1 if after_kpi == before_kpi + 1 else 0,
            "promotion_lead_privacy_unmatched_utm_manual": 1 if unmatched_status == "manual_lead_unmatched_utm" else 0,
            "promotion_lead_privacy_unmatched_utm_no_kpi_increment": 1 if kpi_after_unmatched == kpi_before_unmatched else 0,
            "promotion_lead_privacy_profile_raw_email_hits": 1 if profile_raw_email_hits else 0,
        }


def main() -> int:
    metrics = run_audit()
    issues: list[str] = []
    required_true = (
        "promotion_lead_privacy_safe_imports",
        "promotion_lead_privacy_do_not_contact_rejected",
        "promotion_lead_privacy_generic_proof_rejected",
        "promotion_lead_privacy_matched_utm_incremented",
        "promotion_lead_privacy_unmatched_utm_manual",
        "promotion_lead_privacy_unmatched_utm_no_kpi_increment",
    )
    for key in required_true:
        if metrics.get(key) != 1:
            issues.append(f"{key} expected 1")
    if metrics["promotion_lead_privacy_real_rows"] != 1:
        issues.append("safe import should create exactly one real row before negative cases")
    if metrics["promotion_lead_privacy_raw_email_hits"] != 0:
        issues.append("raw reply email leaked into lead/KPI/playbook files")
    if metrics["promotion_lead_privacy_profile_raw_email_hits"] != 0:
        issues.append("raw reply email leaked into profile tracker")

    for key, value in metrics.items():
        print(f"{key}={value}")
    print(f"promotion_lead_privacy_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
