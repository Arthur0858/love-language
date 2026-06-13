#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path

import promotion_lead_demand_gate as lead_demand


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_paths(temp_root: Path, temp_docs: Path) -> None:
    lead_demand.ROOT = temp_root
    lead_demand.PROMOTION_DIR = temp_docs
    lead_demand.LEAD_TRACKER = temp_docs / "lead-intake-tracker.csv"
    lead_demand.EVIDENCE_LEDGER = temp_docs / "evidence-ledger.json"
    lead_demand.OFFER_PLAN = temp_docs / "offer-experiment-plan.json"
    lead_demand.MD_OUTPUT = temp_docs / "lead-demand-gate.md"
    lead_demand.JSON_OUTPUT = temp_docs / "lead-demand-gate.json"


def lead_row(template: dict[str, str], index: int) -> dict[str, str]:
    row = dict(template)
    row.update({
        "request_id": f"2026-06-15-iris-owned_asset_request-{index:03d}",
        "date": "2026-06-15",
        "source": "keepsake_waitlist",
        "utm_content": "iris_silence",
        "contact_campaign_content": "iris_silence",
        "guardian_id": "iris",
        "guardian_name": "艾莉絲",
        "intake_type": "owned_asset_request",
        "requested_asset": "PDF 練習卡",
        "kpi_writeback_field": "supply_lead_requests",
        "email_status": "received",
        "consent_status": "explicit_reply_ok",
        "status": "new",
        "notes": f"verified:2026-06-15 email thread iris-owned request {index} checked 2026-06-15",
    })
    return row


def set_real_leads(temp_docs: Path, count: int) -> list[str]:
    tracker = temp_docs / "lead-intake-tracker.csv"
    fields, rows = read_csv(tracker)
    template = next(row for row in rows if row.get("request_id") == "template-iris-owned_asset_request")
    rows = [row for row in rows if row.get("status") == "template"]
    request_ids = []
    for index in range(1, count + 1):
        row = lead_row(template, index)
        rows.append({field: row.get(field, "") for field in fields})
        request_ids.append(row["request_id"])
    write_csv(tracker, fields, rows)
    return request_ids


def set_evidence(temp_docs: Path, request_ids: list[str]) -> None:
    rows = [
        {
            "evidence_type": "lead",
            "platform": "keepsake_waitlist",
            "record_id": request_id,
            "status": "new",
            "required": "1",
            "evidence_status": "traceable",
            "proof_date": "2026-06-15",
            "proof_note": "email thread Gmail request checked 2026-06-15",
            "source": "docs/promotion/first-round/lead-intake-tracker.csv",
        }
        for request_id in request_ids
    ]
    write_json(temp_docs / "evidence-ledger.json", {
        "generatedAt": "2026-06-15",
        "metrics": {
            "rows": len(rows),
            "required": len(rows),
            "traceable": len(rows),
            "generic": 0,
            "missing": 0,
            "pending": 0,
            "issues": 0,
        },
        "rows": rows,
        "issues": [],
    })


def set_offer_ready(temp_docs: Path, ready: bool) -> None:
    path = temp_docs / "offer-experiment-plan.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    for row in plan.get("experiments", []):
        if row.get("guardianId") == "iris" and row.get("experimentType") == "owned_lead":
            row["status"] = "READY" if ready else "HOLD"
    write_json(path, plan)


def run_scenario(temp_docs: Path, *, leads: int, offer_ready: bool) -> dict:
    request_ids = set_real_leads(temp_docs, leads)
    set_evidence(temp_docs, request_ids)
    set_offer_ready(temp_docs, offer_ready)
    return lead_demand.build_gate()


def metric(gate: dict, key: str) -> int:
    return int(gate.get("metrics", {}).get(key, 0) or 0)


def main() -> int:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="lovetypes-lead-demand-scenario-") as temp_name:
        temp_root = Path(temp_name)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)
        patch_paths(temp_root, temp_docs)

        one_lead = run_scenario(temp_docs, leads=1, offer_ready=True)
        two_without_offer = run_scenario(temp_docs, leads=2, offer_ready=False)
        two_with_offer = run_scenario(temp_docs, leads=2, offer_ready=True)

    checks = {
        "one_lead_not_repeated": metric(one_lead, "repeatedDemandRoutes") == 0 and metric(one_lead, "readyRoutes") == 0,
        "two_leads_repeated": metric(two_without_offer, "repeatedDemandRoutes") == 1,
        "two_leads_without_offer_blocked": metric(two_without_offer, "readyRoutes") == 0 and metric(two_without_offer, "blockers") >= 1,
        "two_leads_with_offer_ready": metric(two_with_offer, "readyRoutes") == 1 and metric(two_with_offer, "blockers") == 0,
        "traceable_evidence_required": metric(two_with_offer, "traceableEvidence") == 2,
        "explicit_consent_required": metric(two_with_offer, "explicitConsent") == 2,
    }
    for name, ok in checks.items():
        if not ok:
            issues.append(name)

    print(f"promotion_lead_demand_scenario_one_lead_ready={int(metric(one_lead, 'readyRoutes') > 0)}")
    print(f"promotion_lead_demand_scenario_two_leads_repeated={metric(two_without_offer, 'repeatedDemandRoutes')}")
    print(f"promotion_lead_demand_scenario_two_without_offer_ready={metric(two_without_offer, 'readyRoutes')}")
    print(f"promotion_lead_demand_scenario_two_with_offer_ready={metric(two_with_offer, 'readyRoutes')}")
    print(f"promotion_lead_demand_scenario_traceable_evidence={metric(two_with_offer, 'traceableEvidence')}")
    print(f"promotion_lead_demand_scenario_explicit_consent={metric(two_with_offer, 'explicitConsent')}")
    print(f"promotion_lead_demand_scenario_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
