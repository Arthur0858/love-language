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
ASSET_BACKLOG = PROMOTION_DIR / "asset-build-backlog.json"
LEAD_MAGNET = PROMOTION_DIR / "lead-magnet-inventory.json"
LEAD_TRACKER = PROMOTION_DIR / "lead-intake-tracker.csv"
LEAD_DEMAND = PROMOTION_DIR / "lead-demand-gate.json"
OFFER_QUEUE = PROMOTION_DIR / "offer-experiment-queue.json"
OUTPUT_MD = PROMOTION_DIR / "asset-fulfillment-gate.md"
OUTPUT_JSON = PROMOTION_DIR / "asset-fulfillment-gate.json"
OUTPUT_CSV = PROMOTION_DIR / "asset-fulfillment-gate.csv"

OWNED_REQUEST_TYPES = {"pdf_practice_card", "phone_wallpaper", "email_lead_template", "short_ritual"}
PAID_OR_COMMERCIAL_TYPES = {"luna_scene_cta", "affiliate_book_bundle"}
FREE_PUBLIC_TYPES = {"free_story_card_upgrade"}
CONTENT_TYPES = {"content_variant"}
REQUEST_ASSET_ALIASES = {
    "pdf_practice_card": ("pdf", "練習卡", "practice card", "tarjeta pdf", "練習カード", "연습 카드"),
    "phone_wallpaper": ("wallpaper", "桌布", "壁紙", "배경화면", "fondo"),
    "short_ritual": ("short ritual", "短儀式", "7 分鐘", "7-minute", "ritual", "儀式"),
    "email_lead_template": ("email", "contact", "聯絡", "來信", "需求", "template"),
}


def today() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def real_leads(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("status") != "template"]


def lead_counts(rows: list[dict[str, str]]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in real_leads(rows):
        counts[(row.get("guardian_id", ""), row.get("intake_type", ""))] += 1
    return counts


def requested_asset_types(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    requested: set[tuple[str, str]] = set()
    for row in real_leads(rows):
        guardian = (row.get("guardian_id") or "").strip()
        intake = (row.get("intake_type") or "").strip()
        text = f"{row.get('requested_asset', '')} {row.get('first_response', '')} {row.get('next_action', '')}".lower()
        if intake == "repair_or_contact_request":
            requested.add((guardian, "email_lead_template"))
        if intake != "owned_asset_request":
            continue
        for asset_type, tokens in REQUEST_ASSET_ALIASES.items():
            if asset_type == "email_lead_template":
                continue
            if any(token.lower() in text for token in tokens):
                requested.add((guardian, asset_type))
    return requested


def inventory_guardians(inventory: dict) -> set[tuple[str, str]]:
    present: set[tuple[str, str]] = set()
    for page in inventory.get("pages", []):
        lang = str(page.get("lang", ""))
        for item in page.get("guardians", []):
            if item.get("storyAssetExists") and item.get("anchor") and item.get("practiceAnchor"):
                present.add((lang, str(item.get("guardian", ""))))
    return present


def ready_offer_assets(queue: dict) -> set[str]:
    return {
        str(row.get("assetId", ""))
        for row in queue.get("queueRows", [])
        if row.get("status") == "ready" and row.get("step") in {"asset", "qa"}
    }


def demand_ready_pairs(demand: dict) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for route in demand.get("routes", []):
        if route.get("status") == "ready":
            pairs.add((str(route.get("guardianId", "")), str(route.get("intakeType", ""))))
    return pairs


def fulfillment_status(item: dict, context: dict) -> tuple[str, str, str]:
    asset_type = item.get("assetType", "")
    guardian = item.get("guardianId", "")
    asset_id = item.get("id", "")
    counts: Counter[tuple[str, str]] = context["leadCounts"]
    ready_assets: set[str] = context["readyOfferAssets"]
    requested_assets: set[tuple[str, str]] = context["requestedAssetTypes"]
    inventory_pairs: set[tuple[str, str]] = context["inventoryPairs"]

    if asset_type in CONTENT_TYPES:
        return (
            "ready_to_prepare",
            "Content variants can be prepared in empty-data mode as long as the Shorts CTA stays focused on the quiz.",
            "Do not publish as a winning variant until KPI rows exist.",
        )
    if asset_type in FREE_PUBLIC_TYPES:
        has_all_langs = all((lang, guardian) in inventory_pairs for lang in ("zh", "en", "ja", "ko", "es"))
        if has_all_langs:
            return (
                "public_free_ready",
                "Existing keepsake story card and practice-card route are present across all languages.",
                "Do not treat saves/downloads as demand until tracked externally.",
            )
        return (
            "blocked_missing_inventory",
            "Free public asset must exist across all language keepsake pages before fulfillment.",
            "Repair lead-magnet inventory before promoting this asset.",
        )
    if asset_type in OWNED_REQUEST_TYPES:
        if (guardian, asset_type) in requested_assets:
            return (
                "ready_after_real_request",
                "A real request specifically asked for this asset type; create the smallest requested fulfillment asset.",
                "Do not add a paid CTA; fulfill only the requested asset with safety copy.",
            )
        return (
            "blocked_until_real_request",
            "Owned assets require at least one traceable request for this specific asset type.",
            "Wait for lead-intake-tracker.csv evidence before building or sending.",
        )
    if asset_type in PAID_OR_COMMERCIAL_TYPES:
        if asset_id in ready_assets:
            return (
                "ready_after_offer_gate",
                "Offer experiment queue marks this asset ready for asset/QA work.",
                "Place CTA only after result route; do not make Shorts/profile sales-first.",
            )
        return (
            "blocked_until_offer_ready",
            "Commercial or Luna assets require a READY offer experiment.",
            "Keep Luna/affiliate as secondary routes until KPI evidence is non-empty.",
        )
    return (
        "hold",
        "Asset type is not mapped to a fulfillment rule.",
        "Add an explicit gate before fulfillment.",
    )


def build_gate() -> dict:
    backlog = load_json(ASSET_BACKLOG)
    inventory = load_json(LEAD_MAGNET)
    leads = read_csv(LEAD_TRACKER)
    demand = load_json(LEAD_DEMAND)
    queue = load_json(OFFER_QUEUE)
    context = {
        "leadCounts": lead_counts(leads),
        "requestedAssetTypes": requested_asset_types(leads),
        "inventoryPairs": inventory_guardians(inventory),
        "readyDemandPairs": demand_ready_pairs(demand),
        "readyOfferAssets": ready_offer_assets(queue),
    }
    rows = []
    for item in backlog.get("items", []):
        status, evidence, stop = fulfillment_status(item, context)
        rows.append({
            "assetId": item.get("id", ""),
            "guardianId": item.get("guardianId", ""),
            "guardianName": item.get("guardianName", ""),
            "assetType": item.get("assetType", ""),
            "priority": item.get("priority", ""),
            "targetUrl": item.get("targetUrl", ""),
            "fulfillmentStatus": status,
            "evidence": evidence,
            "stopCondition": stop,
            "safetyBoundary": item.get("safety", ""),
        })
    counts_by_status = Counter(row["fulfillmentStatus"] for row in rows)
    metrics = {
        "rows": len(rows),
        "readyToPrepare": counts_by_status["ready_to_prepare"],
        "publicFreeReady": counts_by_status["public_free_ready"],
        "readyAfterRealRequest": counts_by_status["ready_after_real_request"],
        "readyAfterOfferGate": counts_by_status["ready_after_offer_gate"],
        "blockedUntilRealRequest": counts_by_status["blocked_until_real_request"],
        "blockedUntilOfferReady": counts_by_status["blocked_until_offer_ready"],
        "blockedMissingInventory": counts_by_status["blocked_missing_inventory"],
        "realLeads": len(real_leads(leads)),
        "requestedAssetTypes": len(context["requestedAssetTypes"]),
        "readyOfferAssets": len(context["readyOfferAssets"]),
        "readyDemandPairs": len(context["readyDemandPairs"]),
    }
    issues = validate_rows(rows, metrics)
    return {
        "generatedAt": today(),
        "sources": {
            "assetBacklog": str(ASSET_BACKLOG.relative_to(ROOT)),
            "leadMagnetInventory": str(LEAD_MAGNET.relative_to(ROOT)),
            "leadTracker": str(LEAD_TRACKER.relative_to(ROOT)),
            "leadDemandGate": str(LEAD_DEMAND.relative_to(ROOT)),
            "offerExperimentQueue": str(OFFER_QUEUE.relative_to(ROOT)),
        },
        "policy": {
            "doNotFulfillWithoutEvidence": True,
            "freePublicAssetsCanExistBeforeDemand": True,
            "ownedAssetsRequireSpecificRealRequest": True,
            "commercialAssetsRequireReadyOfferGate": True,
            "emptyDataBoundary": "Only content variants and existing free public keepsakes may be prepared while real leads and KPI remain zero.",
        },
        "metrics": metrics,
        "rows": rows,
        "issues": issues,
    }


def validate_rows(rows: list[dict[str, str]], metrics: dict[str, int]) -> list[str]:
    issues: list[str] = []
    if metrics["rows"] != 40:
        issues.append(f"expected 40 fulfillment rows, got {metrics['rows']}")
    by_guardian: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_guardian[row["guardianId"]].append(row)
        for field in ("assetId", "guardianId", "assetType", "targetUrl", "fulfillmentStatus", "evidence", "stopCondition"):
            if not row.get(field):
                issues.append(f"{row.get('assetId', '<unknown>')}: missing {field}")
        if "不承諾療效" not in row.get("safetyBoundary", "") or "不替代諮商" not in row.get("safetyBoundary", ""):
            issues.append(f"{row.get('assetId', '<unknown>')}: missing safety boundary")
    for guardian, guardian_rows in by_guardian.items():
        if len(guardian_rows) != 8:
            issues.append(f"{guardian}: expected 8 fulfillment rows")
    if metrics["realLeads"] == 0 and metrics["readyAfterRealRequest"] != 0:
        issues.append("no real leads should not expose owned-asset fulfillment as ready")
    if metrics["readyOfferAssets"] == 0 and metrics["readyAfterOfferGate"] != 0:
        issues.append("no ready offer assets should not expose commercial fulfillment as ready")
    if metrics["blockedMissingInventory"] != 0:
        issues.append("free public inventory should be complete before fulfillment gate passes")
    return issues


def render_markdown(gate: dict) -> str:
    metrics = gate["metrics"]
    lines = [
        "# LoveTypes Asset Fulfillment Gate",
        "",
        f"- 產生日期：{gate['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready to prepare：{metrics['readyToPrepare']}",
        f"- public free ready：{metrics['publicFreeReady']}",
        f"- blocked until real request：{metrics['blockedUntilRealRequest']}",
        f"- blocked until offer ready：{metrics['blockedUntilOfferReady']}",
        f"- real leads：{metrics['realLeads']}",
        f"- issues：{len(gate['issues'])}",
        "",
        "## Rule",
        "",
        "- 空資料時只能準備內容變體與既有免費收藏物，不交付自有 PDF/桌布/Luna pack，也不加重付費 CTA。",
        "- 自有素材履約必須有真實需求，且只能解鎖使用者明確要求的素材類型。",
        "- Luna / 聯盟 / 商業資產必須等 offer experiment queue READY。",
        "- 所有履約都必須保留安全邊界：不診斷、不承諾療效、不替代諮商。",
        "",
        "## Rows",
        "",
    ]
    for row in gate["rows"]:
        lines.extend([
            f"### {row['guardianName']} · `{row['assetType']}`",
            "",
            f"- asset：`{row['assetId']}`",
            f"- status：`{row['fulfillmentStatus']}`",
            f"- priority：`{row['priority']}`",
            f"- target：{row['targetUrl']}",
            f"- evidence：{row['evidence']}",
            f"- stop：{row['stopCondition']}",
            "",
        ])
    if gate["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in gate["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(gate: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(gate), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fieldnames = [
        "assetId",
        "guardianId",
        "guardianName",
        "assetType",
        "priority",
        "targetUrl",
        "fulfillmentStatus",
        "evidence",
        "stopCondition",
        "safetyBoundary",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fieldnames} for row in gate["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate LoveTypes asset fulfillment against lead, inventory and offer evidence.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    gate = build_gate()
    metrics = gate["metrics"]
    if not args.check:
        write_outputs(gate)
        print(f"promotion_asset_fulfillment_gate={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_asset_fulfillment_gate_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_asset_fulfillment_gate_csv={OUTPUT_CSV.relative_to(ROOT)}")
    print(f"promotion_asset_fulfillment_rows={metrics['rows']}")
    print(f"promotion_asset_fulfillment_ready_to_prepare={metrics['readyToPrepare']}")
    print(f"promotion_asset_fulfillment_public_free_ready={metrics['publicFreeReady']}")
    print(f"promotion_asset_fulfillment_ready_after_real_request={metrics['readyAfterRealRequest']}")
    print(f"promotion_asset_fulfillment_ready_after_offer_gate={metrics['readyAfterOfferGate']}")
    print(f"promotion_asset_fulfillment_blocked_until_real_request={metrics['blockedUntilRealRequest']}")
    print(f"promotion_asset_fulfillment_blocked_until_offer_ready={metrics['blockedUntilOfferReady']}")
    print(f"promotion_asset_fulfillment_real_leads={metrics['realLeads']}")
    print(f"promotion_asset_fulfillment_requested_asset_types={metrics['requestedAssetTypes']}")
    print(f"promotion_asset_fulfillment_ready_offer_assets={metrics['readyOfferAssets']}")
    print(f"promotion_asset_fulfillment_issues={len(gate['issues'])}")
    for issue in gate["issues"]:
        print(issue)
    return 1 if gate["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
