#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KIT_PATH = ROOT / "promotion-kit.json"
TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"

FIELDNAMES = [
    "week",
    "slot",
    "task_id",
    "date",
    "platform",
    "post_url",
    "script_id",
    "guardian_id",
    "guardian_name",
    "content_angle",
    "utm_content",
    "tracked_url",
    "views",
    "likes",
    "comments",
    "shares",
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
    "notes",
]
PRESERVE_FIELDS = {
    "date",
    "platform",
    "post_url",
    "views",
    "likes",
    "comments",
    "shares",
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
    "notes",
}


def load_tasks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("publishingTasks", [])
    if not isinstance(tasks, list):
        return []
    return sorted(tasks, key=lambda task: (int(task.get("week", 0) or 0), int(task.get("slot", 0) or 0)))


def read_existing(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {
        row.get("script_id", ""): row
        for row in rows
        if row.get("script_id")
    }


def task_row(task: dict, existing: dict[str, str] | None = None) -> dict[str, str]:
    existing = existing or {}
    row = {field: "" for field in FIELDNAMES}
    row.update({
        "week": str(task.get("week", "")),
        "slot": str(task.get("slot", "")),
        "task_id": str(task.get("taskId", "")),
        "script_id": str(task.get("scriptId", "")),
        "guardian_id": str(task.get("guardianId", "")),
        "guardian_name": str(task.get("guardianName", "")),
        "content_angle": str(task.get("contentAngle", "")),
        "utm_content": str(task.get("utmContent", "")),
        "tracked_url": str(task.get("trackedUrl", "")),
    })
    for field in PRESERVE_FIELDS:
        if existing.get(field):
            row[field] = existing[field]
    if not row["notes"]:
        row["notes"] = str(task.get("notes", ""))
    return row


def build_rows(tasks: list[dict], existing: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    return [task_row(task, existing.get(str(task.get("scriptId", "")))) for task in tasks]


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    if len(rows) != 15:
        issues.append(f"expected 15 tracker rows, got {len(rows)}")
    seen_scripts: set[str] = set()
    for row in rows:
        script_id = row.get("script_id", "")
        if not script_id:
            issues.append("tracker row missing script_id")
        elif script_id in seen_scripts:
            issues.append(f"duplicate script_id {script_id}")
        seen_scripts.add(script_id)
        for field in ("week", "slot", "task_id", "guardian_id", "guardian_name", "content_angle", "utm_content", "tracked_url"):
            if not row.get(field):
                issues.append(f"{script_id or '<unknown>'}: missing {field}")
        if row.get("tracked_url") and f"utm_content={row.get('utm_content')}" not in row["tracked_url"]:
            issues.append(f"{script_id}: tracked_url should contain matching utm_content")
    return issues


def write_tracker(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync LoveTypes KPI tracker rows from promotion-kit publishing tasks.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--tracker", default=str(TRACKER_PATH))
    parser.add_argument("--check", action="store_true", help="Validate expected tracker rows without writing.")
    args = parser.parse_args()

    tasks = load_tasks(Path(args.kit))
    rows = build_rows(tasks, read_existing(Path(args.tracker)))
    issues = validate_rows(rows)
    if args.check:
        print(f"promotion_kpi_tracker_rows={len(rows)}")
        print(f"promotion_kpi_tracker_fields={len(FIELDNAMES)}")
        print(f"promotion_kpi_tracker_issues={len(issues)}")
        for issue in issues:
            print(issue)
        return 1 if issues else 0
    if issues:
        for issue in issues:
            print(issue)
        return 1
    write_tracker(Path(args.tracker), rows)
    print(f"promotion_kpi_tracker={args.tracker}")
    print(f"promotion_kpi_tracker_rows={len(rows)}")
    print(f"promotion_kpi_tracker_fields={len(FIELDNAMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
