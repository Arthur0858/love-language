#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import shutil
import tempfile
from pathlib import Path

import promotion_asset_fulfillment_gate as fulfillment


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
TRACKED_FILES = (
    SOURCE_DIR / "lead-intake-tracker.csv",
    SOURCE_DIR / "asset-build-backlog.json",
    SOURCE_DIR / "lead-magnet-inventory.json",
    SOURCE_DIR / "lead-demand-gate.json",
    SOURCE_DIR / "offer-experiment-queue.json",
)


def file_hashes(paths: tuple[Path, ...]) -> dict[Path, str]:
    hashes: dict[Path, str] = {}
    for path in paths:
        hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def append_pdf_request(tracker: Path) -> None:
    with tracker.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0].keys())
    template = next(row for row in rows if row["request_id"] == "template-iris-owned_asset_request")
    request = dict(template)
    request.update({
        "request_id": "2026-06-15-iris-owned_asset_request-001",
        "date": "2026-06-15",
        "source": "keepsake_waitlist",
        "utm_content": "iris_silence",
        "contact_campaign_content": "iris_silence",
        "requested_asset": "PDF 練習卡",
        "email_status": "received",
        "consent_status": "explicit_reply_ok",
        "status": "new",
        "notes": "verified:2026-06-15 email thread pdf request checked 2026-06-15",
    })
    rows.append(request)
    with tracker.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_temp_gate(temp_root: Path) -> dict:
    temp_docs = temp_root / "docs" / "promotion" / "first-round"
    fulfillment.ROOT = temp_root
    fulfillment.PROMOTION_DIR = temp_docs
    fulfillment.ASSET_BACKLOG = temp_docs / "asset-build-backlog.json"
    fulfillment.LEAD_MAGNET = temp_docs / "lead-magnet-inventory.json"
    fulfillment.LEAD_TRACKER = temp_docs / "lead-intake-tracker.csv"
    fulfillment.LEAD_DEMAND = temp_docs / "lead-demand-gate.json"
    fulfillment.OFFER_QUEUE = temp_docs / "offer-experiment-queue.json"
    return fulfillment.build_gate()


def row_status(gate: dict, asset_id: str) -> str:
    for row in gate["rows"]:
        if row["assetId"] == asset_id:
            return row["fulfillmentStatus"]
    return ""


def main() -> int:
    before = file_hashes(TRACKED_FILES)
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="lovetypes-asset-fulfillment-") as temp_name:
        temp_root = Path(temp_name)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)
        append_pdf_request(temp_docs / "lead-intake-tracker.csv")
        gate = run_temp_gate(temp_root)

    after = file_hashes(TRACKED_FILES)
    mutated = before != after
    metrics = gate["metrics"]
    statuses = {
        "pdf": row_status(gate, "iris-pdf_practice_card"),
        "wallpaper": row_status(gate, "iris-phone_wallpaper"),
        "short_ritual": row_status(gate, "iris-short_ritual"),
        "email_template": row_status(gate, "iris-email_lead_template"),
    }
    commercial_ready = sum(
        1
        for row in gate["rows"]
        if row["assetType"] in fulfillment.PAID_OR_COMMERCIAL_TYPES
        and row["fulfillmentStatus"] == "ready_after_offer_gate"
    )
    checks = {
        "real_leads": metrics["realLeads"] == 1,
        "requested_asset_types": metrics["requestedAssetTypes"] == 1,
        "ready_after_real_request": metrics["readyAfterRealRequest"] == 1,
        "pdf_ready": statuses["pdf"] == "ready_after_real_request",
        "wallpaper_blocked": statuses["wallpaper"] == "blocked_until_real_request",
        "short_ritual_blocked": statuses["short_ritual"] == "blocked_until_real_request",
        "email_template_blocked": statuses["email_template"] == "blocked_until_real_request",
        "commercial_ready": commercial_ready == 0,
        "current_files_mutated": not mutated,
    }
    for name, ok in checks.items():
        if not ok:
            issues.append(name)
    issues.extend(gate["issues"])

    print(f"promotion_asset_fulfillment_dry_run_real_leads={metrics['realLeads']}")
    print(f"promotion_asset_fulfillment_dry_run_requested_asset_types={metrics['requestedAssetTypes']}")
    print(f"promotion_asset_fulfillment_dry_run_ready_after_real_request={metrics['readyAfterRealRequest']}")
    print(f"promotion_asset_fulfillment_dry_run_pdf_ready={1 if checks['pdf_ready'] else 0}")
    print(f"promotion_asset_fulfillment_dry_run_wallpaper_blocked={1 if checks['wallpaper_blocked'] else 0}")
    print(f"promotion_asset_fulfillment_dry_run_short_ritual_blocked={1 if checks['short_ritual_blocked'] else 0}")
    print(f"promotion_asset_fulfillment_dry_run_email_template_blocked={1 if checks['email_template_blocked'] else 0}")
    print(f"promotion_asset_fulfillment_dry_run_commercial_ready={commercial_ready}")
    print(f"promotion_asset_fulfillment_dry_run_current_files_mutated={1 if mutated else 0}")
    print(f"promotion_asset_fulfillment_dry_run_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
