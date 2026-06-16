#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
KPI_TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
PROFILE_TRACKER_PATH = PROMOTION_DIR / "platform-profile-tracker.csv"
DEFAULT_OUT_DIR = PROMOTION_DIR / "kpi-import-validation"

IDENTITY_ROUTE_FIELDS = [
    "guardian_result_clicks",
    "resources_clicks",
    "repair_plan_clicks",
    "luna_clicks",
    "keepsake_clicks",
]
REVENUE_BRIDGE_FIELDS = [
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]
POST_METRIC_FIELDS = [
    "views",
    "likes",
    "comments",
    "shares",
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    *IDENTITY_ROUTE_FIELDS,
    *REVENUE_BRIDGE_FIELDS,
]
PROFILE_METRIC_FIELDS = [
    "profile_clicks",
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    *IDENTITY_ROUTE_FIELDS,
    *REVENUE_BRIDGE_FIELDS,
]
REQUIRED_INPUT_FIELDS = ["utm_content"]
OPTIONAL_ID_FIELDS = ["target_type", "platform", "post_url", "tracked_url", "source_file", "notes"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a local LoveTypes KPI import CSV without writing back to trackers."
    )
    parser.add_argument("--input", required=True, help="CSV with utm_content and KPI metric columns")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_tracker_index(path: Path) -> dict[str, dict[str, str]]:
    return {row.get("utm_content", ""): row for row in read_csv(path) if row.get("utm_content")}


def as_nonnegative_int(value: str, field: str, row_number: int, issues: list[str]) -> int:
    if value == "" or value is None:
        return 0
    try:
        parsed = int(str(value).strip())
    except ValueError:
        issues.append(f"row {row_number}: {field} must be an integer")
        return 0
    if parsed < 0:
        issues.append(f"row {row_number}: {field} must be nonnegative")
        return 0
    return parsed


def utm_from_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    values = parse_qs(parsed.query).get("utm_content") or []
    return values[0] if values else ""


def validate_rows(rows: list[dict[str, str]]) -> dict:
    post_index = load_tracker_index(KPI_TRACKER_PATH)
    profile_index = load_tracker_index(PROFILE_TRACKER_PATH)
    known_post = set(post_index)
    known_profile = set(profile_index)
    known_any = known_post | known_profile

    issues: list[str] = []
    normalized: list[dict[str, str | int]] = []
    nonzero_rows = 0
    matched_post_rows = 0
    matched_profile_rows = 0

    if not rows:
        issues.append("input CSV has no data rows")

    input_fields = set(rows[0].keys()) if rows else set()
    for field in REQUIRED_INPUT_FIELDS:
        if field not in input_fields:
            issues.append(f"input CSV missing required field {field}")
    if not input_fields.intersection(POST_METRIC_FIELDS):
        issues.append("input CSV must include at least one KPI metric column")

    for index, row in enumerate(rows, start=2):
        utm_content = (row.get("utm_content") or "").strip()
        tracked_url = (row.get("tracked_url") or "").strip()
        inferred_utm = utm_from_url(tracked_url)
        if not utm_content and inferred_utm:
            utm_content = inferred_utm
        if not utm_content:
            issues.append(f"row {index}: utm_content is required")
            continue
        if inferred_utm and inferred_utm != utm_content:
            issues.append(f"row {index}: tracked_url utm_content {inferred_utm} does not match {utm_content}")
        if utm_content not in known_any:
            issues.append(f"row {index}: unknown utm_content {utm_content}")

        target_type = (row.get("target_type") or "").strip().lower()
        if not target_type:
            target_type = "profile" if utm_content in known_profile and utm_content not in known_post else "post"
        if target_type not in {"post", "profile"}:
            issues.append(f"row {index}: target_type must be post or profile")
            target_type = "post"

        metric_fields = PROFILE_METRIC_FIELDS if target_type == "profile" else POST_METRIC_FIELDS
        metrics: dict[str, int] = {}
        for field in metric_fields:
            if field in row:
                metrics[field] = as_nonnegative_int(row.get(field, ""), field, index, issues)
        nonzero = sum(1 for value in metrics.values() if value > 0)
        if nonzero:
            nonzero_rows += 1
        else:
            issues.append(f"row {index}: at least one KPI metric must be nonzero")

        if target_type == "profile":
            if utm_content not in known_profile:
                issues.append(f"row {index}: profile row {utm_content} not found in platform-profile-tracker.csv")
            else:
                matched_profile_rows += 1
        else:
            if utm_content not in known_post:
                issues.append(f"row {index}: post row {utm_content} not found in kpi-tracker.csv")
            else:
                matched_post_rows += 1

        normalized_row: dict[str, str | int] = {
            "target_type": target_type,
            "utm_content": utm_content,
            "platform": row.get("platform", ""),
            "post_url": row.get("post_url", ""),
            "tracked_url": tracked_url,
            "source_file": row.get("source_file", ""),
            "notes": row.get("notes", ""),
        }
        normalized_row.update(metrics)
        normalized.append(normalized_row)

    return {
        "ok": not issues,
        "issues": issues,
        "stats": {
            "input_rows": len(rows),
            "nonzero_rows": nonzero_rows,
            "matched_post_rows": matched_post_rows,
            "matched_profile_rows": matched_profile_rows,
            "known_post_utm_count": len(known_post),
            "known_profile_utm_count": len(known_profile),
        },
        "normalized_rows": normalized,
        "safety": {
            "does_not_write_trackers": True,
            "does_not_publish": True,
            "does_not_deploy": True,
            "does_not_login": True,
            "local_csv_validation_only": True,
        },
    }


def write_outputs(report: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "kpi-import-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = OPTIONAL_ID_FIELDS + sorted({key for row in report["normalized_rows"] for key in row if key not in OPTIONAL_ID_FIELDS})
    with (out_dir / "kpi-import-normalized-preview.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report["normalized_rows"])
    issue_lines = "\n".join(f"- {issue}" for issue in report["issues"]) if report["issues"] else "- none"
    stats = report["stats"]
    markdown = f"""# LoveTypes KPI Import Validation

- Result: {"PASS" if report["ok"] else "FAIL"}
- Input rows: `{stats["input_rows"]}`
- Nonzero rows: `{stats["nonzero_rows"]}`
- Matched post rows: `{stats["matched_post_rows"]}`
- Matched profile rows: `{stats["matched_profile_rows"]}`
- Safety: local validation only; no tracker writeback; no publish; no deploy; no login.

## Issues

{issue_lines}
"""
    (out_dir / "kpi-import-validation.md").write_text(markdown, encoding="utf-8")


def main() -> int:
    args = parse_args()
    rows = read_csv(Path(args.input))
    report = validate_rows(rows)
    report["input_path"] = str(Path(args.input))
    report["out_dir"] = args.out_dir
    write_outputs(report, Path(args.out_dir))
    print(json.dumps({"ok": report["ok"], **report["stats"], "out_dir": args.out_dir}, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
