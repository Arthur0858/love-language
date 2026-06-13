#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
COMMERCE = ROOT / "commerce-catalog.json"
LEAD_MAGNET = PROMOTION_DIR / "lead-magnet-inventory.json"
ASSET_BACKLOG = PROMOTION_DIR / "asset-build-backlog.json"
OFFER_BOARD = PROMOTION_DIR / "offer-hypothesis-board.json"
OFFER_PLAN = PROMOTION_DIR / "offer-experiment-plan.json"
GUARDIANS = ("iris", "noah", "vivian", "claire", "dora")
REQUIRED_ASSET_TYPES = {
    "free_story_card_upgrade",
    "pdf_practice_card",
    "phone_wallpaper",
    "email_lead_template",
    "short_ritual",
    "luna_scene_cta",
    "affiliate_book_bundle",
    "content_variant",
}
EXPERIMENT_TO_ASSET = {
    "identity_save": "free_story_card_upgrade",
    "owned_lead": "email_lead_template",
    "luna_soft_offer": "luna_scene_cta",
    "affiliate_book": "affiliate_book_bundle",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def local_html_for(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.netloc != "lovetypes.tw":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if not parts:
        return ROOT / "index.html"
    if parts[0] in {"en", "ja", "ko", "es"}:
        return ROOT.joinpath(*parts, "index.html")
    return ROOT.joinpath(*parts, "index.html")


def url_anchor_exists(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.fragment:
        return True
    html_path = local_html_for(url)
    if not html_path or not html_path.exists():
        return False
    html = html_path.read_text(encoding="utf-8")
    return f'id="{parsed.fragment}"' in html or f"#{parsed.fragment}" in html or parsed.fragment in html


def commerce_by_guardian(catalog: dict) -> dict[str, dict[str, dict]]:
    grouped = {guardian: {} for guardian in GUARDIANS}
    for item in catalog.get("items", []):
        guardian = item.get("guardian")
        item_type = item.get("type")
        if guardian in grouped and item_type in {"free_keepsake", "owned_supply_waitlist"}:
            grouped[guardian][item_type] = item
    return grouped


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    commerce = load_json(COMMERCE)
    lead_magnet = load_json(LEAD_MAGNET)
    backlog = load_json(ASSET_BACKLOG)
    offer_board = load_json(OFFER_BOARD)
    offer_plan = load_json(OFFER_PLAN)

    commerce_guardians = commerce_by_guardian(commerce)
    backlog_items = backlog.get("items", [])
    backlog_by_id = {item.get("id"): item for item in backlog_items if isinstance(item, dict)}
    backlog_by_guardian: dict[str, list[dict]] = {guardian: [] for guardian in GUARDIANS}
    for item in backlog_items:
        guardian = item.get("guardianId")
        if guardian in backlog_by_guardian:
            backlog_by_guardian[guardian].append(item)
    lead_pages = lead_magnet.get("pages", [])
    lead_by_guardian: dict[str, list[dict]] = {guardian: [] for guardian in GUARDIANS}
    for page in lead_pages:
        for item in page.get("guardians", []):
            guardian = item.get("guardian")
            if guardian in lead_by_guardian:
                lead_by_guardian[guardian].append(item)
    board_by_guardian = {row.get("guardianId"): row for row in offer_board.get("rows", []) if isinstance(row, dict)}
    experiment_rows = offer_plan.get("experiments", [])

    commerce_pairs = 0
    backlog_links = 0
    lead_magnet_links = 0
    experiment_links = 0
    anchor_checks = 0

    for guardian in GUARDIANS:
        commerce_items = commerce_guardians.get(guardian, {})
        free_item = commerce_items.get("free_keepsake")
        supply_item = commerce_items.get("owned_supply_waitlist")
        if not free_item:
            issues.append(f"{guardian}: missing commerce free_keepsake")
        if not supply_item:
            issues.append(f"{guardian}: missing commerce owned_supply_waitlist")
        if free_item and supply_item:
            commerce_pairs += 1
            if free_item.get("playbookId") != "identity_retention_first":
                issues.append(f"{guardian}: free_keepsake should use identity_retention_first playbook")
            if supply_item.get("playbookId") != "owned_supply_lead":
                issues.append(f"{guardian}: owned_supply_waitlist should use owned_supply_lead playbook")
            for label, item in (("free", free_item), ("supply", supply_item)):
                anchor_checks += 1
                if not url_anchor_exists(str(item.get("url", ""))):
                    issues.append(f"{guardian}: commerce {label} URL anchor missing locally: {item.get('url')}")

        items = backlog_by_guardian.get(guardian, [])
        asset_types = {item.get("assetType") for item in items}
        if asset_types != REQUIRED_ASSET_TYPES:
            issues.append(f"{guardian}: backlog asset types mismatch")
        for item in items:
            if free_item and item.get("freeItemId") != free_item.get("id"):
                issues.append(f"{item.get('id')}: freeItemId should match commerce free_keepsake")
            if supply_item and item.get("leadItemId") != supply_item.get("id"):
                issues.append(f"{item.get('id')}: leadItemId should match commerce owned_supply_waitlist")
            if item.get("targetUrl"):
                backlog_links += 1
                anchor_checks += 1
                if not url_anchor_exists(str(item["targetUrl"])):
                    issues.append(f"{item.get('id')}: targetUrl anchor missing locally: {item.get('targetUrl')}")
            if "不承諾療效" not in str(item.get("safety", "")) or "不替代諮商" not in str(item.get("safety", "")):
                issues.append(f"{item.get('id')}: missing safety boundary")

        lead_items = lead_by_guardian.get(guardian, [])
        if len(lead_items) != int(lead_magnet.get("policy", {}).get("expectedLanguages", 0) or 0):
            issues.append(f"{guardian}: lead magnet inventory should include one row per language")
        for item in lead_items:
            types = set(item.get("leadMagnetTypes", []))
            if not {"story_card_image", "printable_practice_card"}.issubset(types):
                issues.append(f"{guardian}: missing required free lead magnet type")
            for field in ("anchor", "practiceAnchor", "contactHandoff"):
                if item.get(field):
                    lead_magnet_links += 1
                    anchor_checks += 1
                    if not url_anchor_exists(str(item[field])):
                        issues.append(f"{guardian}: lead magnet {field} anchor missing locally: {item[field]}")

        board = board_by_guardian.get(guardian)
        if not board:
            issues.append(f"{guardian}: missing offer hypothesis row")
        else:
            free_asset = board.get("freeAsset") if isinstance(board.get("freeAsset"), dict) else {}
            owned_asset = board.get("ownedAsset") if isinstance(board.get("ownedAsset"), dict) else {}
            if free_item and free_asset.get("freeItemId") != free_item.get("id"):
                issues.append(f"{guardian}: offer board freeAsset should match commerce free_keepsake")
            if supply_item and owned_asset.get("leadItemId") != supply_item.get("id"):
                issues.append(f"{guardian}: offer board ownedAsset should match commerce owned_supply_waitlist")
            if free_asset.get("id") not in backlog_by_id:
                issues.append(f"{guardian}: offer board freeAsset id missing from backlog")
            if owned_asset.get("id") not in backlog_by_id:
                issues.append(f"{guardian}: offer board ownedAsset id missing from backlog")
            if board.get("readiness") == "PASS":
                issues.append(f"{guardian}: offer board should not PASS while launch data is empty")

    for experiment in experiment_rows:
        guardian = experiment.get("guardianId")
        experiment_type = experiment.get("experimentType")
        expected_asset_type = EXPERIMENT_TO_ASSET.get(str(experiment_type))
        asset_id = experiment.get("assetId")
        asset = backlog_by_id.get(asset_id)
        if not asset:
            issues.append(f"{experiment.get('experimentId')}: assetId missing from backlog")
            continue
        experiment_links += 1
        if asset.get("guardianId") != guardian:
            issues.append(f"{experiment.get('experimentId')}: asset guardian mismatch")
        if expected_asset_type and asset.get("assetType") != expected_asset_type:
            issues.append(f"{experiment.get('experimentId')}: expected asset type {expected_asset_type}")
        if experiment.get("targetUrl") != asset.get("targetUrl"):
            issues.append(f"{experiment.get('experimentId')}: targetUrl should match backlog asset targetUrl")
        if experiment.get("status") != "HOLD":
            issues.append(f"{experiment.get('experimentId')}: experiment should remain HOLD before real signal")

    return {
        "guardians": len(GUARDIANS),
        "commercePairs": commerce_pairs,
        "backlogItems": len(backlog_items),
        "backlogLinks": backlog_links,
        "leadMagnetLinks": lead_magnet_links,
        "experimentLinks": experiment_links,
        "anchorChecks": anchor_checks,
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_asset_commerce_guardians={metrics['guardians']}")
    print(f"promotion_asset_commerce_pairs={metrics['commercePairs']}")
    print(f"promotion_asset_commerce_backlog_items={metrics['backlogItems']}")
    print(f"promotion_asset_commerce_backlog_links={metrics['backlogLinks']}")
    print(f"promotion_asset_commerce_lead_magnet_links={metrics['leadMagnetLinks']}")
    print(f"promotion_asset_commerce_experiment_links={metrics['experimentLinks']}")
    print(f"promotion_asset_commerce_anchor_checks={metrics['anchorChecks']}")
    print(f"promotion_asset_commerce_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
