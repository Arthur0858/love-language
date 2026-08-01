#!/usr/bin/env python3
"""Read-only AdSense submission gate backed by explicit external evidence."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "config" / "adsense-submission-gate.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    return parser.parse_args()


def has_evidence(item: dict) -> bool:
    checked_at = item.get("checkedAt")
    evidence = item.get("evidence")
    if not item.get("confirmed") or not isinstance(checked_at, str) or not checked_at:
        return False
    try:
        datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return isinstance(evidence, str) and bool(evidence.strip())


def main() -> int:
    args = parse_args()
    state = json.loads(args.state.read_text(encoding="utf-8"))
    issues: list[str] = []

    if state.get("reviewSubmitted") is not False:
        issues.append("reviewSubmitted must remain false before a new submission")

    changed = date.fromisoformat(state["lastMaterialChange"])
    minimum_days = int(state["minimumStableDays"])
    earliest = changed + timedelta(days=minimum_days)
    if args.today < earliest:
        issues.append(f"stable observation period incomplete: earliest={earliest.isoformat()}")

    gates = state.get("externalGates", {})
    required = {
        "gscFullAccess",
        "sitemapAccepted",
        "importantPagesRecrawled",
        "legacyUrlsLeavingIndex",
        "adsTxtRecognizedByAdsense",
        "gscPagesWithImpressions",
        "productionAuditGreen",
    }
    missing = sorted(required - set(gates))
    if missing:
        issues.append(f"external gate definitions missing: {', '.join(missing)}")

    for name in sorted(required & set(gates)):
        item = gates[name]
        if not isinstance(item, dict) or not has_evidence(item):
            issues.append(f"external evidence pending or incomplete: {name}")
            continue
        if name == "gscPagesWithImpressions":
            value = int(item.get("value", 0))
            minimum = int(item.get("minimum", 5))
            if value < minimum:
                issues.append(f"GSC impression pages below threshold: {value} < {minimum}")

    print(f"adsense_submission_state={args.state.relative_to(ROOT)}")
    print(f"adsense_submission_today={args.today.isoformat()}")
    print(f"adsense_submission_earliest={earliest.isoformat()}")
    print(f"adsense_submission_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    ready = not issues
    print(f"adsense_submission_ready={'true' if ready else 'false'}")
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
