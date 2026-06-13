#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"
EVIDENCE_LEDGER = PROMOTION_DIR / "evidence-ledger.json"
OFFER_PLAN = PROMOTION_DIR / "offer-experiment-plan.json"
MD_OUTPUT = PROMOTION_DIR / "lead-demand-gate.md"
JSON_OUTPUT = PROMOTION_DIR / "lead-demand-gate.json"
REPEAT_DEMAND_THRESHOLD = 2
GUARDIANS = ("iris", "noah", "vivian", "claire", "dora")
INTAKE_TYPES = ("owned_asset_request", "luna_scene_request", "repair_or_contact_request")
INTAKE_TO_EXPERIMENT = {
    "owned_asset_request": "owned_lead",
    "luna_scene_request": "luna_soft_offer",
    "repair_or_contact_request": "identity_save",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def real_leads(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if (row.get("status") or "").strip() != "template"]


def lead_evidence_rows(evidence: dict) -> dict[str, dict]:
    rows = evidence.get("rows", [])
    if not isinstance(rows, list):
        return {}
    return {
        str(row.get("record_id", "")): row
        for row in rows
        if row.get("evidence_type") == "lead"
    }


def offer_ready_lookup(plan: dict) -> set[tuple[str, str]]:
    experiments = plan.get("experiments", [])
    if not isinstance(experiments, list):
        return set()
    return {
        (str(row.get("guardianId", "")), str(row.get("experimentType", "")))
        for row in experiments
        if row.get("status") == "READY"
    }


def build_gate() -> dict:
    rows = real_leads(read_csv(LEAD_TRACKER))
    evidence = lead_evidence_rows(load_json(EVIDENCE_LEDGER))
    ready_experiments = offer_ready_lookup(load_json(OFFER_PLAN))
    demand_counts: Counter[tuple[str, str]] = Counter()
    consent_ok = 0
    traceable = 0
    matched_utm = 0
    rows_by_pair: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        guardian = (row.get("guardian_id") or "").strip()
        intake = (row.get("intake_type") or "").strip()
        pair = (guardian, intake)
        demand_counts[pair] += 1
        rows_by_pair[pair].append(row)
        if row.get("consent_status") == "explicit_reply_ok":
            consent_ok += 1
        proof = evidence.get(row.get("request_id", ""))
        if proof and proof.get("evidence_status") == "traceable":
            traceable += 1
        if (row.get("utm_content") or "").strip():
            matched_utm += 1

    routes = []
    for guardian in GUARDIANS:
        for intake in INTAKE_TYPES:
            count = demand_counts[(guardian, intake)]
            experiment_type = INTAKE_TO_EXPERIMENT[intake]
            repeat_ready = count >= REPEAT_DEMAND_THRESHOLD
            offer_ready = (guardian, experiment_type) in ready_experiments
            route_ready = repeat_ready and offer_ready
            routes.append({
                "guardianId": guardian,
                "intakeType": intake,
                "experimentType": experiment_type,
                "leadCount": count,
                "repeatDemandReady": repeat_ready,
                "offerExperimentReady": offer_ready,
                "routeReady": route_ready,
                "relatedRequestIds": [row.get("request_id", "") for row in rows_by_pair[(guardian, intake)]],
                "nextAction": (
                    "Prepare the smallest owned asset or Luna scene, then QA safety boundaries."
                    if route_ready
                    else "Keep collecting real requests; do not create paid or priority offer from this signal yet."
                ),
            })

    real_count = len(rows)
    evidence_complete = real_count == traceable
    consent_complete = real_count == consent_ok
    repeated_routes = sum(1 for route in routes if route["repeatDemandReady"])
    ready_routes = sum(1 for route in routes if route["routeReady"])
    blockers: list[dict[str, str]] = []
    if real_count == 0:
        blockers.append({
            "id": "no_real_leads",
            "message": "No real Contact / keepsake / Luna requests have been written back yet.",
            "release": "Add real lead rows only after a user request with explicit reply consent arrives.",
        })
    if not evidence_complete:
        blockers.append({
            "id": "lead_evidence_incomplete",
            "message": f"traceable lead evidence {traceable}/{real_count}.",
            "release": "Every real lead row has a traceable email thread, message id, or checked proof note.",
        })
    if not consent_complete:
        blockers.append({
            "id": "lead_consent_incomplete",
            "message": f"explicit reply consent {consent_ok}/{real_count}.",
            "release": "Do not use requests without explicit_reply_ok for product decisions.",
        })
    if repeated_routes == 0:
        blockers.append({
            "id": "no_repeated_guardian_demand",
            "message": f"No guardian/intake pair has reached {REPEAT_DEMAND_THRESHOLD} real requests.",
            "release": "Wait for repeated same-guardian demand before prioritizing owned assets or Luna packs.",
        })
    if repeated_routes and ready_routes == 0:
        blockers.append({
            "id": "offer_experiment_not_ready",
            "message": "Repeated lead demand exists, but the offer experiment plan has not opened a matching READY experiment.",
            "release": "Refresh KPI and week decision gates before moving lead demand into offer production.",
        })

    issues: list[str] = []
    if any(row.get("guardian_id") not in GUARDIANS for row in rows):
        issues.append("real lead has unknown guardian")
    if any(row.get("intake_type") not in INTAKE_TYPES for row in rows):
        issues.append("real lead has unknown intake type")
    if traceable > real_count or consent_ok > real_count:
        issues.append("lead evidence or consent count cannot exceed real lead count")
    if ready_routes and blockers:
        issues.append("routeReady cannot coexist with blockers")
    return {
        "generatedAt": date.today().isoformat(),
        "sources": {
            "leadTracker": str(LEAD_TRACKER.relative_to(ROOT)),
            "evidenceLedger": str(EVIDENCE_LEDGER.relative_to(ROOT)),
            "offerExperimentPlan": str(OFFER_PLAN.relative_to(ROOT)),
        },
        "metrics": {
            "realLeads": real_count,
            "traceableEvidence": traceable,
            "explicitConsent": consent_ok,
            "matchedUtmRows": matched_utm,
            "repeatedDemandRoutes": repeated_routes,
            "readyRoutes": ready_routes,
            "blockers": len(blockers),
            "issues": len(issues),
        },
        "policy": {
            "repeatDemandThreshold": REPEAT_DEMAND_THRESHOLD,
            "requiresTraceableEvidence": True,
            "requiresExplicitConsent": True,
            "doNotStoreRawEmail": True,
            "commercialBoundary": "Lead demand can prioritize free owned assets or Luna aftercare only after repeated same-guardian demand and matching offer readiness.",
        },
        "routes": routes,
        "blockers": blockers,
        "issues": issues,
    }


def render_markdown(gate: dict) -> str:
    metrics = gate["metrics"]
    policy = gate["policy"]
    lines = [
        "# LoveTypes Lead Demand Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- real leads：{metrics['realLeads']}",
        f"- traceable evidence：{metrics['traceableEvidence']} / {metrics['realLeads']}",
        f"- explicit consent：{metrics['explicitConsent']} / {metrics['realLeads']}",
        f"- repeated demand routes：{metrics['repeatedDemandRoutes']}",
        f"- ready routes：{metrics['readyRoutes']}",
        f"- blockers：{metrics['blockers']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Policy",
        "",
        f"- Same guardian / intake must reach at least {policy['repeatDemandThreshold']} real requests.",
        "- Every real request needs explicit reply consent and traceable proof.",
        "- Raw email content is not stored in the tracker.",
        f"- {policy['commercialBoundary']}",
        "",
        "## Routes",
        "",
    ]
    for route in gate["routes"]:
        lines.extend([
            f"### {route['guardianId']} / {route['intakeType']}",
            "",
            f"- experiment：`{route['experimentType']}`",
            f"- leads：{route['leadCount']}",
            f"- repeated demand：`{int(route['repeatDemandReady'])}`",
            f"- offer ready：`{int(route['offerExperimentReady'])}`",
            f"- route ready：`{int(route['routeReady'])}`",
            f"- next：{route['nextAction']}",
            "",
        ])
    lines.extend(["## Blockers", ""])
    if gate["blockers"]:
        for blocker in gate["blockers"]:
            lines.append(f"- `{blocker['id']}`：{blocker['message']} 解除條件：{blocker['release']}")
    else:
        lines.append("- 無。")
    if gate["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in gate["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(gate: dict) -> None:
    JSON_OUTPUT.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUTPUT.write_text(render_markdown(gate), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether real lead demand is strong enough for owned/Luna offer work.")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write generated outputs.")
    args = parser.parse_args()

    gate = build_gate()
    if not args.check:
        write_outputs(gate)
        print(f"promotion_lead_demand_gate={MD_OUTPUT}")
        print(f"promotion_lead_demand_gate_json={JSON_OUTPUT}")
    metrics = gate["metrics"]
    print(f"promotion_lead_demand_real_leads={metrics['realLeads']}")
    print(f"promotion_lead_demand_traceable_evidence={metrics['traceableEvidence']}")
    print(f"promotion_lead_demand_explicit_consent={metrics['explicitConsent']}")
    print(f"promotion_lead_demand_matched_utm_rows={metrics['matchedUtmRows']}")
    print(f"promotion_lead_demand_repeated_routes={metrics['repeatedDemandRoutes']}")
    print(f"promotion_lead_demand_ready_routes={metrics['readyRoutes']}")
    print(f"promotion_lead_demand_blockers={metrics['blockers']}")
    print(f"promotion_lead_demand_issues={metrics['issues']}")
    for issue in gate["issues"]:
        print(issue)
    return 1 if metrics["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
