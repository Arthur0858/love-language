#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROMOTION_KIT_PATH = ROOT / "promotion-kit.json"
PLATFORM_TRACKER = "platform-kpi-tracker.csv"
SCRIPT_TRACKER = "kpi-tracker.csv"

STALE_PHRASES = (
    "After publishing, fill kpi-tracker.csv",
    "Fill kpi-tracker.csv for every published task",
    "發布後回填 posting-queue.csv 與 kpi-tracker.csv",
    "發布後先回填 posting-queue.csv，再回填 kpi-tracker.csv",
    "先回填 posting-queue.csv，再回填 kpi-tracker.csv",
    "同一天或隔天回填 kpi-tracker.csv",
    "kpi-tracker.csv: platform, post_url",
)

REQUIRED_DOCS = (
    "launch-readiness-gate.md",
    "launch-command-center.md",
    "now-asset-production-pack.md",
    "now-asset-production-queue.md",
    "now-asset-production-briefs.md",
    "platform-launch-brief-index.md",
    "execution-sheet-index.md",
    "week-asset-briefs-index.md",
    *(f"week-{week}-platform-launch-brief.md" for week in range(1, 6)),
    *(f"week-{week}-execution-sheet.md" for week in range(1, 6)),
    *(f"week-{week}-asset-briefs.md" for week in range(1, 6)),
    *(f"week-{week}-publish-pack.md" for week in range(1, 6)),
)
DOWNSTREAM_FIELDS = (
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
)
DOWNSTREAM_REQUIRED_DOCS = (
    "launch-command-center.md",
    "platform-launch-brief-index.md",
    "execution-sheet-index.md",
    "week-asset-briefs-index.md",
    *(f"week-{week}-platform-launch-brief.md" for week in range(1, 6)),
    *(f"week-{week}-execution-sheet.md" for week in range(1, 6)),
    *(f"week-{week}-asset-briefs.md" for week in range(1, 6)),
    *(f"week-{week}-publish-pack.md" for week in range(1, 6)),
)


def text_files_to_scan() -> list[Path]:
    paths = [PROMOTION_KIT_PATH]
    paths.extend(PROMOTION_DIR.glob("*.md"))
    paths.extend(PROMOTION_DIR.glob("*.json"))
    paths.extend(PROMOTION_DIR.glob("*.csv"))
    return sorted(path for path in paths if path.exists())


def main() -> int:
    issues: list[str] = []
    stale_phrase_hits = 0

    for path in text_files_to_scan():
        text = path.read_text(encoding="utf-8")
        for phrase in STALE_PHRASES:
            if phrase in text:
                stale_phrase_hits += 1
                issues.append(f"{path.relative_to(ROOT)}: stale writeback phrase found: {phrase}")

    docs_checked = 0
    docs_with_platform_tracker = 0
    docs_with_rollup = 0
    downstream_docs_checked = 0
    downstream_docs_complete = 0
    for name in REQUIRED_DOCS:
        path = PROMOTION_DIR / name
        if not path.exists():
            issues.append(f"{path.relative_to(ROOT)}: required promotion writeback doc missing")
            continue
        docs_checked += 1
        text = path.read_text(encoding="utf-8")
        if PLATFORM_TRACKER not in text:
            issues.append(f"{path.relative_to(ROOT)}: missing {PLATFORM_TRACKER} writeback guidance")
        else:
            docs_with_platform_tracker += 1
        if SCRIPT_TRACKER in text and ("週回顧" in text or "weekly" in text or "rollup" in text or "彙總" in text):
            docs_with_rollup += 1

    for name in DOWNSTREAM_REQUIRED_DOCS:
        path = PROMOTION_DIR / name
        if not path.exists():
            issues.append(f"{path.relative_to(ROOT)}: required downstream KPI doc missing")
            continue
        downstream_docs_checked += 1
        text = path.read_text(encoding="utf-8")
        missing = [field for field in DOWNSTREAM_FIELDS if field not in text]
        if missing:
            issues.append(f"{path.relative_to(ROOT)}: missing downstream KPI guidance fields {', '.join(missing)}")
        else:
            downstream_docs_complete += 1

    kit = json.loads(PROMOTION_KIT_PATH.read_text(encoding="utf-8"))
    kit_text = json.dumps(kit, ensure_ascii=False)
    if PLATFORM_TRACKER not in kit_text:
        issues.append("promotion-kit.json: missing platform-level KPI tracker guidance")
    if "Roll up kpi-tracker.csv" not in kit_text and "roll up kpi-tracker.csv" not in kit_text:
        issues.append("promotion-kit.json: missing script-level weekly rollup guidance")
    if "weeklyReviewChecklist" not in kit.get("measurementPlan", {}):
        issues.append("promotion-kit.json: missing measurementPlan.weeklyReviewChecklist")
    missing_kit_downstream = [field for field in DOWNSTREAM_FIELDS if field not in kit_text]
    if missing_kit_downstream:
        issues.append(f"promotion-kit.json: missing downstream KPI fields {', '.join(missing_kit_downstream)}")

    print(f"promotion_writeback_files_scanned={len(text_files_to_scan())}")
    print(f"promotion_writeback_docs_checked={docs_checked}")
    print(f"promotion_writeback_docs_with_platform_tracker={docs_with_platform_tracker}")
    print(f"promotion_writeback_docs_with_rollup={docs_with_rollup}")
    print(f"promotion_writeback_downstream_docs_checked={downstream_docs_checked}")
    print(f"promotion_writeback_downstream_docs_complete={downstream_docs_complete}")
    print(f"promotion_writeback_stale_phrase_hits={stale_phrase_hits}")
    print(f"promotion_writeback_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
