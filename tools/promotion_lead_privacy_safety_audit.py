#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import tempfile
from datetime import date
from pathlib import Path

import promotion_lead_text_import as lead_import
import promotion_lead_writeback as writeback


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
DEFAULT_JSON_OUTPUT = SOURCE_DIR / "lead-privacy-safety-audit.json"
DEFAULT_MD_OUTPUT = SOURCE_DIR / "lead-privacy-safety-audit.md"
RAW_EMAIL = "requester@customer-mail.com"
PLACEHOLDER_EMAIL = "<REAL_REPLY_EMAIL>"
SAMPLE_EMAIL = "sample@example.com"
TODAY = date.today().isoformat()
SAFE_PROOF = f"email thread Gmail request checked {TODAY}"
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
    writeback.regenerate_dependent_docs = lambda: None


def sample_text(*, utm: str = "iris_silence", consent: str = "explicit_reply_ok") -> str:
    return lead_import.SAMPLE_TEXT.replace("iris_silence", utm).replace("explicit_reply_ok", consent)


def sample_text_with_email(email: str) -> str:
    return lead_import.SAMPLE_TEXT.replace(RAW_EMAIL, email)


def add_from_text(text: str, proof_note: str) -> str:
    data, issues = lead_import.parse_text(text)
    if issues:
        raise SystemExit("\n".join(issues))
    return lead_import.add_lead(data, proof_note=proof_note, request_date=TODAY)


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

        placeholder_email_rejected = expect_rejected(lambda: add_from_text(sample_text_with_email(PLACEHOLDER_EMAIL), SAFE_PROOF))
        sample_email_rejected = expect_rejected(lambda: add_from_text(sample_text_with_email(SAMPLE_EMAIL), SAFE_PROOF))
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
            "promotion_lead_privacy_placeholder_email_rejected": 1 if placeholder_email_rejected else 0,
            "promotion_lead_privacy_sample_email_rejected": 1 if sample_email_rejected else 0,
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


def build_report() -> dict:
    metrics = run_audit()
    issues: list[str] = []
    required_true = (
        "promotion_lead_privacy_placeholder_email_rejected",
        "promotion_lead_privacy_sample_email_rejected",
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
    return {
        "generatedAt": TODAY,
        "source": {
            "leadTracker": str((SOURCE_DIR / "lead-intake-tracker.csv").relative_to(ROOT)),
            "kpiTracker": str((SOURCE_DIR / "kpi-tracker.csv").relative_to(ROOT)),
            "profileTracker": str((SOURCE_DIR / "platform-profile-tracker.csv").relative_to(ROOT)),
        },
        "metrics": {**metrics, "promotion_lead_privacy_issues": len(issues)},
        "policy": {
            "rejectPlaceholderEmail": True,
            "rejectSampleEmail": True,
            "rejectDoNotContact": True,
            "rejectGenericProof": True,
            "doNotStoreRawReplyEmail": True,
            "unmatchedUtmRequiresManualReview": True,
            "matchedUtmMayIncrementKpi": True,
        },
        "issues": issues,
    }


def render_markdown(report: dict) -> str:
    metrics = report["metrics"]
    lines = [
        "# LoveTypes Lead Privacy Safety Audit",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- safe imports：{metrics['promotion_lead_privacy_safe_imports']}",
        f"- real rows in rehearsal：{metrics['promotion_lead_privacy_real_rows']}",
        f"- raw email hits：{metrics['promotion_lead_privacy_raw_email_hits']}",
        f"- profile raw email hits：{metrics['promotion_lead_privacy_profile_raw_email_hits']}",
        f"- issues：{metrics['promotion_lead_privacy_issues']}",
        "",
        "## Policy Checks",
        "",
    ]
    for key, value in report["policy"].items():
        lines.append(f"- {key}: `{int(bool(value))}`")
    lines.extend(["", "## Metrics", ""])
    for key, value in metrics.items():
        lines.append(f"- {key}: `{value}`")
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in report["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict, json_output: Path, md_output: Path) -> None:
    json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_output.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit LoveTypes lead privacy import/writeback behavior.")
    parser.add_argument("--check", action="store_true", help="Validate without writing generated outputs.")
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    args = parser.parse_args()

    report = build_report()
    metrics = report["metrics"]
    issues = report["issues"]
    if not args.check:
        write_outputs(report, Path(args.json_output), Path(args.output))
        print(f"promotion_lead_privacy_safety_audit={args.output}")
        print(f"promotion_lead_privacy_safety_audit_json={args.json_output}")

    for key, value in metrics.items():
        if key != "promotion_lead_privacy_issues":
            print(f"{key}={value}")
    print(f"promotion_lead_privacy_issues={metrics['promotion_lead_privacy_issues']}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
