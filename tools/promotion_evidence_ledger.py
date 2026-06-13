#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path

from promotion_proof_note_policy import has_traceable_evidence


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_TRACKER = PROMOTION_DIR / "platform-profile-tracker.csv"
POSTING_QUEUE = PROMOTION_DIR / "posting-queue.csv"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"
CSV_OUTPUT = PROMOTION_DIR / "evidence-ledger.csv"
JSON_OUTPUT = PROMOTION_DIR / "evidence-ledger.json"
MD_OUTPUT = PROMOTION_DIR / "evidence-ledger.md"
PROFILE_CONFIGURED_STATUSES = {"set", "live"}
POST_PUBLISHED_STATUSES = {"published", "live", "posted"}
VERIFIED_RE = re.compile(r"verified:(?P<date>20\d{2}-\d{2}-\d{2})\s+(?P<note>[^|]+)")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def extract_verified_notes(value: str) -> list[dict[str, str]]:
    notes = []
    for match in VERIFIED_RE.finditer(value or ""):
        note = match.group("note").strip()
        notes.append({
            "date": match.group("date"),
            "note": note,
            "traceable": "1" if has_traceable_evidence(note) else "0",
        })
    return notes


def best_proof(notes: list[dict[str, str]]) -> dict[str, str]:
    for note in reversed(notes):
        if note.get("traceable") == "1":
            return note
    if notes:
        return notes[-1]
    return {"date": "", "note": "", "traceable": "0"}


def evidence_status(required: bool, notes: list[dict[str, str]]) -> str:
    proof = best_proof(notes)
    if proof.get("traceable") == "1":
        return "traceable"
    if notes:
        return "generic"
    return "missing" if required else "not_required_yet"


def profile_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(PROFILE_TRACKER):
        status = (row.get("status") or "").strip()
        required = status in PROFILE_CONFIGURED_STATUSES
        notes = extract_verified_notes(row.get("notes", ""))
        proof = best_proof(notes)
        rows.append({
            "evidence_type": "profile",
            "platform": row.get("platform", ""),
            "record_id": row.get("platform", ""),
            "status": status,
            "required": "1" if required else "0",
            "evidence_status": evidence_status(required, notes),
            "proof_date": proof.get("date", ""),
            "proof_note": proof.get("note", ""),
            "source": str(PROFILE_TRACKER.relative_to(ROOT)),
        })
    return rows


def post_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(POSTING_QUEUE):
        status = (row.get("status") or "").strip()
        required = status in POST_PUBLISHED_STATUSES
        notes = extract_verified_notes(row.get("notes", ""))
        proof = best_proof(notes)
        rows.append({
            "evidence_type": "post",
            "platform": row.get("platform", ""),
            "record_id": row.get("task_id", ""),
            "status": status,
            "required": "1" if required else "0",
            "evidence_status": evidence_status(required, notes),
            "proof_date": proof.get("date", ""),
            "proof_note": proof.get("note", ""),
            "source": str(POSTING_QUEUE.relative_to(ROOT)),
        })
    return rows


def lead_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(LEAD_TRACKER):
        status = (row.get("status") or "").strip()
        required = status != "template"
        notes = extract_verified_notes(row.get("notes", ""))
        proof = best_proof(notes)
        rows.append({
            "evidence_type": "lead",
            "platform": row.get("source", ""),
            "record_id": row.get("request_id", ""),
            "status": status,
            "required": "1" if required else "0",
            "evidence_status": evidence_status(required, notes),
            "proof_date": proof.get("date", ""),
            "proof_note": proof.get("note", ""),
            "source": str(LEAD_TRACKER.relative_to(ROOT)),
        })
    return rows


def build_rows() -> list[dict[str, str]]:
    return profile_rows() + post_rows() + lead_rows()


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    required = [row for row in rows if row["required"] == "1"]
    traceable = [row for row in required if row["evidence_status"] == "traceable"]
    generic = [row for row in required if row["evidence_status"] == "generic"]
    missing = [row for row in required if row["evidence_status"] == "missing"]
    pending = [row for row in rows if row["required"] == "0"]
    issues = [
        f"{row['evidence_type']} {row['platform']}/{row['record_id']} requires traceable proof"
        for row in generic + missing
    ]
    return {
        "generatedAt": date.today().isoformat(),
        "sources": [
            str(PROFILE_TRACKER.relative_to(ROOT)),
            str(POSTING_QUEUE.relative_to(ROOT)),
            str(LEAD_TRACKER.relative_to(ROOT)),
        ],
        "metrics": {
            "rows": len(rows),
            "required": len(required),
            "traceable": len(traceable),
            "generic": len(generic),
            "missing": len(missing),
            "pending": len(pending),
            "issues": len(issues),
        },
        "rows": rows,
        "issues": issues,
    }


def write_csv_output(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "evidence_type",
        "platform",
        "record_id",
        "status",
        "required",
        "evidence_status",
        "proof_date",
        "proof_note",
        "source",
    ]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(data: dict[str, object]) -> str:
    metrics = data["metrics"]
    assert isinstance(metrics, dict)
    rows = data["rows"]
    assert isinstance(rows, list)
    lines = [
        "# LoveTypes Promotion Evidence Ledger",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- required / traceable：{metrics['required']} / {metrics['traceable']}",
        f"- generic / missing：{metrics['generic']} / {metrics['missing']}",
        f"- pending：{metrics['pending']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rule",
        "",
        "- `set/live` profile、`published/live/posted` 貼文、真實 lead 都必須有可追蹤 proof note。",
        "- proof note 需要能回頭稽核，例如截圖檔名、公開 URL、平台 URL、email thread、message id 或檢查日期。",
        "- planned/template 資料不需要證據，會列為 `not_required_yet`。",
        "",
        "## Required Evidence",
        "",
    ]
    required_rows = [row for row in rows if row["required"] == "1"]
    if not required_rows:
        lines.append("- 目前沒有已完成狀態需要證據；外部平台設定與發布仍待執行。")
    for row in required_rows:
        lines.extend([
            f"- `{row['evidence_type']}` `{row['platform']}` / `{row['record_id']}`：{row['evidence_status']}",
            f"  - proof：{row['proof_note'] or 'missing'}",
        ])
    lines.extend(["", "## Pending Setup / Publication", ""])
    pending_rows = [row for row in rows if row["required"] == "0" and row["evidence_status"] == "not_required_yet"]
    for row in pending_rows[:12]:
        lines.append(f"- `{row['evidence_type']}` `{row['platform']}` / `{row['record_id']}`：{row['status']}")
    if len(pending_rows) > 12:
        lines.append(f"- ... plus {len(pending_rows) - 12} pending rows")
    issues = data["issues"]
    assert isinstance(issues, list)
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict[str, object]) -> None:
    rows = data["rows"]
    assert isinstance(rows, list)
    write_csv_output(rows)
    JSON_OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(render_markdown(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and audit the LoveTypes promotion evidence ledger.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated ledger files.")
    args = parser.parse_args()

    rows = build_rows()
    data = summarize(rows)
    metrics = data["metrics"]
    assert isinstance(metrics, dict)
    if not args.check:
        write_outputs(data)
    print(f"promotion_evidence_ledger_rows={metrics['rows']}")
    print(f"promotion_evidence_ledger_required={metrics['required']}")
    print(f"promotion_evidence_ledger_traceable={metrics['traceable']}")
    print(f"promotion_evidence_ledger_generic={metrics['generic']}")
    print(f"promotion_evidence_ledger_missing={metrics['missing']}")
    print(f"promotion_evidence_ledger_pending={metrics['pending']}")
    print(f"promotion_evidence_ledger_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if metrics["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
