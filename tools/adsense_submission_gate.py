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
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate state and evidence contracts without requiring every submission gate to be satisfied.",
    )
    return parser.parse_args()


def evidence_path(item: dict) -> Path | None:
    evidence = item.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        return None
    if evidence.startswith(("https://", "http://")):
        return None
    return ROOT / evidence


def has_evidence_reference(item: dict) -> bool:
    checked_at = item.get("checkedAt")
    evidence = item.get("evidence")
    if not isinstance(checked_at, str) or not checked_at:
        return False
    try:
        datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if not isinstance(evidence, str) or not evidence.strip():
        return False
    if evidence.startswith(("https://", "http://")):
        return True
    return (ROOT / evidence).is_file()


def read_local_evidence(item: dict) -> dict | None:
    path = evidence_path(item)
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def object_value(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def integer_value(value: object, default: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def evidence_contract_issues(name: str, item: dict) -> list[str]:
    payload = read_local_evidence(item)
    if payload is None:
        return [f"{name} requires valid local machine-readable evidence"]

    issues: list[str] = []
    if name == "gscFullAccess":
        prop = object_value(payload.get("property"))
        if prop.get("confirmed") is not True or prop.get("access") != "verified_owner":
            issues.append("GSC evidence does not prove verified-owner access")
    elif name == "sitemapAccepted":
        sitemap = object_value(payload.get("sitemap"))
        if (
            sitemap.get("accepted") is not True
            or sitemap.get("status") != "success"
            or sitemap.get("discoveredPages") != 38
        ):
            issues.append("GSC evidence does not prove a successful 38-page sitemap")
    elif name == "importantPagesRecrawled":
        inspection = object_value(payload.get("urlInspection"))
        external = object_value(payload.get("externalGates"))
        if (
            external.get("importantPagesRecrawledAfterMaterialDeployment") is not True
            or integer_value(inspection.get("postMaterialDeploymentRecrawledPages"), 0) < 10
        ):
            issues.append("GSC evidence does not prove ten post-deployment recrawls")
    elif name == "legacyUrlsLeavingIndex":
        external = object_value(payload.get("externalGates"))
        if external.get("legacyUrlsLeavingIndex") is not True:
            issues.append("GSC evidence does not prove legacy URL index exit")
    elif name == "gscPagesWithImpressions":
        external = object_value(payload.get("externalGates"))
        search_performance = object_value(payload.get("searchPerformance"))
        performance = object_value(search_performance.get("sevenDayWindow"))
        proven = integer_value(performance.get("postMaterialDeploymentEditorialPagesWithImpressions"), 0)
        if external.get("gscPagesWithPostDeploymentImpressions") is not True:
            issues.append("GSC evidence does not prove post-deployment editorial impressions")
        if proven < integer_value(item.get("minimum"), 5):
            issues.append("GSC evidence page count is below the configured impression threshold")
    elif name == "adsTxtRecognizedByAdsense":
        status = object_value(payload.get("dashboard")).get("adsTxtStatus")
        if status not in {"authorized", "found", "recognized"}:
            issues.append("AdSense evidence does not prove ads.txt recognition")
    elif name == "reviewActionAvailable":
        dashboard = object_value(payload.get("dashboard"))
        if (
            dashboard.get("submissionRestrictionActive") is not False
            or dashboard.get("reviewActionAvailable") is not True
            or dashboard.get("reviewCheckboxChecked") is not False
            or dashboard.get("reviewSubmitted") is not False
        ):
            issues.append("AdSense evidence does not prove an available, unsubmitted review action")
    elif name == "productionAuditGreen":
        checks = object_value(payload.get("productionChecks"))
        if payload.get("result") != "pass" or integer_value(checks.get("issues")) != 0:
            issues.append("production evidence does not prove a zero-issue audit")
    return issues


def state_validation_issues(state: dict) -> list[str]:
    issues: list[str] = []
    if state.get("schemaVersion") != 1:
        issues.append("unsupported submission-state schemaVersion")
    if state.get("reviewSubmitted") is not False:
        issues.append("reviewSubmitted must remain false before a new submission")
    try:
        date.fromisoformat(state["lastMaterialChange"])
    except (KeyError, TypeError, ValueError):
        issues.append("lastMaterialChange must be an ISO date")
    try:
        if int(state["minimumStableDays"]) < 14:
            issues.append("minimumStableDays must be at least 14")
    except (KeyError, TypeError, ValueError):
        issues.append("minimumStableDays must be an integer")

    gates = state.get("externalGates", {})
    required = {
        "gscFullAccess",
        "sitemapAccepted",
        "importantPagesRecrawled",
        "legacyUrlsLeavingIndex",
        "adsTxtRecognizedByAdsense",
        "reviewActionAvailable",
        "gscPagesWithImpressions",
        "productionAuditGreen",
    }
    if not isinstance(gates, dict):
        return [*issues, "externalGates must be an object"]
    missing = sorted(required - set(gates))
    if missing:
        issues.append(f"external gate definitions missing: {', '.join(missing)}")

    for name in sorted(required & set(gates)):
        item = gates[name]
        if not isinstance(item, dict):
            issues.append(f"external gate must be an object: {name}")
            continue
        if not isinstance(item.get("confirmed"), bool):
            issues.append(f"external gate confirmed must be boolean: {name}")
            continue
        has_partial_reference = bool(item.get("checkedAt") or item.get("evidence"))
        if (item["confirmed"] or has_partial_reference) and not has_evidence_reference(item):
            issues.append(f"external evidence reference is invalid: {name}")
        if item["confirmed"] and has_evidence_reference(item):
            issues.extend(evidence_contract_issues(name, item))
        if name == "gscPagesWithImpressions":
            try:
                value = int(item.get("value", 0))
                minimum = int(item.get("minimum", 5))
            except (TypeError, ValueError):
                issues.append("GSC impression values must be integers")
            else:
                if value < 0 or minimum < 5:
                    issues.append("GSC impression values violate the configured minimum")
    return issues


def main() -> int:
    args = parse_args()
    state = json.loads(args.state.read_text(encoding="utf-8"))
    validation_issues = state_validation_issues(state)

    try:
        display_state = args.state.resolve().relative_to(ROOT)
    except ValueError:
        display_state = args.state.resolve()
    if args.validate_only:
        print(f"adsense_submission_state={display_state}")
        print(f"adsense_submission_validation_issues={len(validation_issues)}")
        for issue in validation_issues:
            print(f"- {issue}")
        valid = not validation_issues
        print(f"adsense_submission_state_valid={'true' if valid else 'false'}")
        return 0 if valid else 1

    issues: list[str] = []
    issues.extend(validation_issues)

    try:
        changed = date.fromisoformat(state["lastMaterialChange"])
    except (KeyError, TypeError, ValueError):
        changed = args.today
    try:
        minimum_days = int(state["minimumStableDays"])
    except (KeyError, TypeError, ValueError):
        minimum_days = 14
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
        "reviewActionAvailable",
        "gscPagesWithImpressions",
        "productionAuditGreen",
    }
    for name in sorted(required & set(gates)):
        item = gates[name]
        if not isinstance(item, dict):
            issues.append(f"external evidence pending or incomplete: {name}")
            continue
        if item.get("confirmed") is not True:
            reason = item.get("reason")
            detail = f" ({reason})" if isinstance(reason, str) and reason else ""
            if has_evidence_reference(item):
                issues.append(f"external gate not satisfied: {name}{detail}")
            else:
                issues.append(f"external evidence pending or incomplete: {name}")
            continue
        if not has_evidence_reference(item):
            issues.append(f"external evidence pending or incomplete: {name}")
            continue
        if name == "gscPagesWithImpressions":
            value = int(item.get("value", 0))
            minimum = int(item.get("minimum", 5))
            if value < minimum:
                issues.append(f"GSC impression pages below threshold: {value} < {minimum}")

    print(f"adsense_submission_state={display_state}")
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
