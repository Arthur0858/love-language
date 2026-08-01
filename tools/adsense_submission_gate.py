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
REQUIRED_GATES = frozenset({
    "gscFullAccess",
    "sitemapAccepted",
    "importantPagesRecrawled",
    "legacyUrlsLeavingIndex",
    "adsTxtRecognizedByAdsense",
    "reviewActionAvailable",
    "gscPagesWithImpressions",
    "gscManualActionsClear",
    "gscSecurityIssuesClear",
    "adsensePolicyCenterClear",
    "productionAuditGreen",
})
GSC_GATES = frozenset({
    "gscFullAccess",
    "sitemapAccepted",
    "importantPagesRecrawled",
    "legacyUrlsLeavingIndex",
    "gscPagesWithImpressions",
    "gscManualActionsClear",
    "gscSecurityIssuesClear",
})
ADSENSE_GATES = frozenset({"adsTxtRecognizedByAdsense", "reviewActionAvailable", "adsensePolicyCenterClear"})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate state and evidence contracts without requiring every submission gate to be satisfied.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Report current readiness without treating expected pending external gates as a command failure.",
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


def checked_date(item: dict) -> date | None:
    value = item.get("checkedAt")
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def evidence_freshness_issue(name: str, item: dict, today: date, maximum_age: int) -> str | None:
    observed = checked_date(item)
    if observed is None:
        return f"external evidence has no valid observation date: {name}"
    age = (today - observed).days
    if age < 0:
        return f"external evidence observation is in the future: {name}"
    if age > maximum_age:
        return f"external evidence is stale: {name} age={age}d max={maximum_age}d"
    return None


def shared_evidence_issues(gates: dict, names: frozenset[str], label: str) -> list[str]:
    references = {
        item.get("evidence")
        for name in names
        if isinstance((item := gates.get(name)), dict) and isinstance(item.get("evidence"), str)
    }
    if len(references) != 1:
        return [f"{label} gates must share one evidence snapshot"]
    return []


def cross_evidence_issues(state: dict, gates: dict) -> list[str]:
    issues = [
        *shared_evidence_issues(gates, GSC_GATES, "GSC"),
        *shared_evidence_issues(gates, ADSENSE_GATES, "AdSense"),
    ]
    gsc = read_local_evidence(object_value(gates.get("gscFullAccess")))
    production = read_local_evidence(object_value(gates.get("productionAuditGreen")))
    adsense = read_local_evidence(object_value(gates.get("reviewActionAvailable")))
    if gsc is not None and production is not None:
        material = object_value(gsc.get("latestMaterialDeployment"))
        deployment = object_value(production.get("cloudflareDeployment"))
        if production.get("reviewSurfaceCommit") != material.get("commit"):
            issues.append("GSC and production evidence disagree on the material commit")
        if deployment.get("id") != material.get("cloudflareDeployment"):
            issues.append("GSC and production evidence disagree on the Cloudflare deployment")
        if production.get("checkedAt") != material.get("productionVerifiedAt"):
            issues.append("GSC and production evidence disagree on the production verification time")
        created_at = material.get("commitCreatedAt")
        try:
            material_date = datetime.fromisoformat(str(created_at).replace("Z", "+00:00")).date()
        except ValueError:
            issues.append("GSC material deployment has an invalid commit timestamp")
        else:
            if state.get("lastMaterialChange") != material_date.isoformat():
                issues.append("lastMaterialChange does not match the latest material commit date")
    if adsense is not None:
        dashboard = object_value(adsense.get("dashboard"))
        if dashboard.get("reviewSubmitted") is not state.get("reviewSubmitted"):
            issues.append("state and AdSense evidence disagree on reviewSubmitted")
    return issues


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
    elif name == "gscManualActionsClear":
        manual_actions = object_value(payload.get("manualActions"))
        if manual_actions.get("status") != "clear" or manual_actions.get("issuesDetected") is not False:
            issues.append("GSC evidence does not prove a clear manual-actions report")
    elif name == "gscSecurityIssuesClear":
        security = object_value(payload.get("securityIssues"))
        if security.get("status") != "clear" or security.get("issuesDetected") is not False:
            issues.append("GSC evidence does not prove a clear security-issues report")
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
    elif name == "adsensePolicyCenterClear":
        policy_center = object_value(payload.get("policyCenter"))
        if policy_center.get("status") != "clear" or policy_center.get("issuesDetected") is not False:
            issues.append("AdSense evidence does not prove a clear policy center")
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
    try:
        maximum_evidence_age = int(state["maximumEvidenceAgeDays"])
        if not 1 <= maximum_evidence_age <= 3:
            issues.append("maximumEvidenceAgeDays must be between 1 and 3")
    except (KeyError, TypeError, ValueError):
        issues.append("maximumEvidenceAgeDays must be an integer")

    gates = state.get("externalGates", {})
    if not isinstance(gates, dict):
        return [*issues, "externalGates must be an object"]
    missing = sorted(REQUIRED_GATES - set(gates))
    if missing:
        issues.append(f"external gate definitions missing: {', '.join(missing)}")

    for name in sorted(REQUIRED_GATES & set(gates)):
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
    if not missing:
        issues.extend(cross_evidence_issues(state, gates))
    return issues


def submission_issues(state: dict, today: date, validation_issues: list[str] | None = None) -> tuple[date, list[str]]:
    issues = list(validation_issues if validation_issues is not None else state_validation_issues(state))

    try:
        changed = date.fromisoformat(state["lastMaterialChange"])
    except (KeyError, TypeError, ValueError):
        changed = today
    try:
        minimum_days = int(state["minimumStableDays"])
    except (KeyError, TypeError, ValueError):
        minimum_days = 14
    try:
        maximum_evidence_age = int(state["maximumEvidenceAgeDays"])
    except (KeyError, TypeError, ValueError):
        maximum_evidence_age = 3
    earliest = changed + timedelta(days=minimum_days)
    if today < earliest:
        issues.append(f"stable observation period incomplete: earliest={earliest.isoformat()}")

    gates = object_value(state.get("externalGates"))
    for name in sorted(REQUIRED_GATES & set(gates)):
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
        freshness_issue = evidence_freshness_issue(name, item, today, maximum_evidence_age)
        if freshness_issue:
            issues.append(freshness_issue)
            continue
        if name == "gscPagesWithImpressions":
            value = integer_value(item.get("value"), 0)
            minimum = integer_value(item.get("minimum"), 5)
            if value < minimum:
                issues.append(f"GSC impression pages below threshold: {value} < {minimum}")

    return earliest, issues


def bool_text(value: object) -> str:
    return "true" if value is True else "false"


def evidence_refresh_issues(state: dict, today: date) -> list[str]:
    try:
        maximum_age = int(state["maximumEvidenceAgeDays"])
    except (KeyError, TypeError, ValueError):
        maximum_age = 3
    gates = object_value(state.get("externalGates"))
    snapshots: dict[str, dict] = {}
    for name in sorted(REQUIRED_GATES & set(gates)):
        item = object_value(gates.get(name))
        evidence = item.get("evidence")
        if isinstance(evidence, str) and evidence:
            snapshots.setdefault(evidence, item)

    issues: list[str] = []
    for evidence, item in sorted(snapshots.items()):
        issue = evidence_freshness_issue(evidence, item, today, maximum_age)
        if issue:
            issues.append(issue)
    return issues


def report_only(state: dict, today: date, display_state: object, validation_issues: list[str]) -> int:
    earliest, pending = submission_issues(state, today, validation_issues)
    refresh_due = evidence_refresh_issues(state, today)
    gates = object_value(state.get("externalGates"))
    ads_txt = object_value(gates.get("adsTxtRecognizedByAdsense")).get("confirmed")
    review_action = object_value(gates.get("reviewActionAvailable")).get("confirmed")
    print(f"adsense_submission_state={display_state}")
    print(f"adsense_submission_today={today.isoformat()}")
    print(f"adsense_submission_earliest={earliest.isoformat()}")
    print(f"adsense_submission_validation_issues={len(validation_issues)}")
    print(f"adsense_submission_pending_conditions={len(pending)}")
    for issue in pending:
        print(f"- pending: {issue}")
    print(f"adsense_submission_evidence_refresh_due={len(refresh_due)}")
    for issue in refresh_due:
        print(f"- refresh: {issue}")
    print(f"adsense_submission_ready={bool_text(not pending)}")
    print(f"adsense_review_submitted={bool_text(state.get('reviewSubmitted'))}")
    print(f"adsense_review_action_available={bool_text(review_action)}")
    print(f"adsense_ads_txt_recognized={bool_text(ads_txt)}")
    return 0 if not validation_issues else 1


def main() -> int:
    args = parse_args()
    if args.validate_only and args.report_only:
        raise SystemExit("--validate-only and --report-only are mutually exclusive")
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

    if args.report_only:
        return report_only(state, args.today, display_state, validation_issues)

    earliest, issues = submission_issues(state, args.today, validation_issues)

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
