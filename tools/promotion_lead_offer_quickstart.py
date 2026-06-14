#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
HANDOFF = PROMOTION_DIR / "weekly-lead-offer-handoff.json"
LEAD_OPS = PROMOTION_DIR / "lead-ops-action-sheet.json"
LEAD_DEMAND = PROMOTION_DIR / "lead-demand-gate.json"
ASSET_GATE = PROMOTION_DIR / "asset-fulfillment-gate.json"
OFFER_QUEUE = PROMOTION_DIR / "offer-experiment-queue.json"
OFFER_BOARD = PROMOTION_DIR / "offer-hypothesis-board.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "lead-offer-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "lead-offer-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "lead-offer-quickstart.txt"


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def metric(payload: dict, key: str) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        values = {}
    try:
        return int(values.get(key, payload.get(key, 0)) or 0)
    except (TypeError, ValueError):
        return 0


def build_quickstart() -> dict:
    handoff = read_json(HANDOFF)
    lead_ops = read_json(LEAD_OPS)
    lead_demand = read_json(LEAD_DEMAND)
    asset_gate = read_json(ASSET_GATE)
    offer_queue = read_json(OFFER_QUEUE)
    offer_board = read_json(OFFER_BOARD)
    rows = handoff.get("rows", []) if isinstance(handoff.get("rows"), list) else []
    lead_actions = lead_ops.get("rows", []) if isinstance(lead_ops.get("rows"), list) else []
    ready_assets = [
        row for row in asset_gate.get("rows", [])
        if (row.get("fulfillmentStatus") or row.get("status")) in {"public_free_ready", "ready_to_prepare"}
    ] if isinstance(asset_gate.get("rows"), list) else []
    blocked_assets = [
        row for row in asset_gate.get("rows", [])
        if str(row.get("fulfillmentStatus") or row.get("status", "")).startswith("blocked")
    ] if isinstance(asset_gate.get("rows"), list) else []
    data = {
        "generatedAt": today(),
        "sources": {
            "weeklyLeadOfferHandoff": str(HANDOFF.relative_to(ROOT)),
            "leadOpsAction": str(LEAD_OPS.relative_to(ROOT)),
            "leadDemandGate": str(LEAD_DEMAND.relative_to(ROOT)),
            "assetFulfillmentGate": str(ASSET_GATE.relative_to(ROOT)),
            "offerExperimentQueue": str(OFFER_QUEUE.relative_to(ROOT)),
            "offerHypothesisBoard": str(OFFER_BOARD.relative_to(ROOT)),
        },
        "metrics": {
            "handoffRows": len(rows),
            "handoffCurrentBlockers": metric(handoff, "currentBlockers"),
            "handoffBlockedUpstreamRows": metric(handoff, "blockedUpstreamRows"),
            "realLeads": metric(lead_demand, "realLeads"),
            "readyLeadRoutes": metric(lead_demand, "readyRoutes"),
            "repeatedRoutes": metric(lead_demand, "repeatedDemandRoutes"),
            "leadOpsReadyRows": metric(lead_ops, "readyRows"),
            "publicFreeAssets": metric(asset_gate, "publicFreeReady"),
            "readyToPrepareAssets": metric(asset_gate, "readyToPrepare"),
            "blockedAssets": len(blocked_assets),
            "offerQueueReady": metric(offer_queue, "readyRows"),
            "offerQueueBlocked": metric(offer_queue, "blockedRows"),
            "offerBoardReady": metric(offer_board, "readyRows"),
            "offerBoardHold": metric(offer_board, "holdRows"),
        },
        "rules": [
            "Do not build paid, Luna, affiliate, or priority offer experiments until weekly review and lead demand gates are open.",
            "Real lead demand requires explicit reply consent, traceable proof, and repeated same-guardian demand.",
            "Public free keepsakes and content variants can remain available, but they are not proof of purchase intent.",
            "Owned PDFs, wallpapers, email templates, and short rituals remain blocked until a real matching request exists.",
            "Offer queue rows must remain blocked while empty data mode or weekly review blockers are active.",
        ],
        "handoffRows": rows,
        "leadActions": lead_actions,
        "safeAssetsNow": ready_assets,
        "blockedAssets": blocked_assets[:10],
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    issues: list[str] = []
    metrics = data["metrics"]
    if metrics["handoffRows"] != 8:
        issues.append(f"expected 8 handoff rows, got {metrics['handoffRows']}")
    if metrics["handoffCurrentBlockers"] != 1:
        issues.append("lead offer quickstart should expose exactly one current handoff blocker")
    if metrics["realLeads"] == 0 and metrics["readyLeadRoutes"] != 0:
        issues.append("ready lead routes must stay zero without real leads")
    if metrics["realLeads"] == 0 and metrics["offerQueueReady"] != 0:
        issues.append("offer queue must stay blocked without real lead or KPI evidence")
    if metrics["publicFreeAssets"] < 5:
        issues.append("five public free assets should remain available as safe lead magnets")
    if not data["leadActions"]:
        issues.append("lead action rows missing")
    for row in data["handoffRows"]:
        label = row.get("step_id", "<handoff>")
        if not row.get("command") or not row.get("stop_condition"):
            issues.append(f"{label}: missing command or stop condition")
    for row in data["safeAssetsNow"]:
        label = row.get("asset_id") or row.get("asset") or "<asset>"
        status = row.get("fulfillmentStatus") or row.get("status")
        if status in {"public_free_ready", "ready_to_prepare"} and not row.get("targetUrl") and not row.get("target_url") and not row.get("target"):
            issues.append(f"{label}: safe asset missing target")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Lead and Offer Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- handoff rows：{metrics['handoffRows']}",
        f"- current blockers / blocked upstream：{metrics['handoffCurrentBlockers']} / {metrics['handoffBlockedUpstreamRows']}",
        f"- real leads：{metrics['realLeads']}",
        f"- ready lead routes：{metrics['readyLeadRoutes']}",
        f"- public free assets：{metrics['publicFreeAssets']}",
        f"- ready to prepare assets：{metrics['readyToPrepareAssets']}",
        f"- offer queue ready / blocked：{metrics['offerQueueReady']} / {metrics['offerQueueBlocked']}",
        f"- offer board ready / hold：{metrics['offerBoardReady']} / {metrics['offerBoardHold']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Handoff", ""])
    for row in data["handoffRows"]:
        lines.extend([
            f"### `{row.get('step_id', '')}`",
            "",
            f"- phase：`{row.get('phase', '')}`",
            f"- status：`{row.get('status', '')}`",
            f"- value：{row.get('current_value', '')} / {row.get('required_value', '')}",
            f"- action：{row.get('owner_action', '')}",
            f"- command：`{row.get('command', '')}`",
            f"- stop：{row.get('stop_condition', '')}",
            "",
        ])
    lines.extend(["## Lead Actions", ""])
    for row in data["leadActions"]:
        lines.append(f"- `{row.get('step_id', '')}` / `{row.get('status', '')}`：{row.get('owner_action', '') or row.get('operator_action', '') or row.get('action', '')}")
    lines.extend(["", "## Safe Assets Now", ""])
    for row in data["safeAssetsNow"]:
        label = row.get("assetId") or row.get("asset_id") or row.get("asset") or ""
        target = row.get("targetUrl") or row.get("target_url") or row.get("target") or ""
        status = row.get("fulfillmentStatus") or row.get("status") or ""
        lines.append(f"- `{label}` / `{status}`：{target}")
    lines.extend(["", "## Blocked Asset Examples", ""])
    for row in data["blockedAssets"]:
        label = row.get("assetId") or row.get("asset_id") or row.get("asset") or ""
        status = row.get("fulfillmentStatus") or row.get("status") or ""
        stop = row.get("stopCondition") or row.get("stop_condition") or row.get("stop", "")
        lines.append(f"- `{label}` / `{status}`：{stop}")
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes lead and offer quickstart",
        f"generated: {data['generatedAt']}",
        f"real leads: {metrics['realLeads']}",
        f"ready lead routes: {metrics['readyLeadRoutes']}",
        f"offer queue ready/blocked: {metrics['offerQueueReady']} / {metrics['offerQueueBlocked']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "Handoff:"])
    for row in data["handoffRows"]:
        lines.extend([
            "",
            f"=== {row.get('step_id', '')} ===",
            f"status: {row.get('status', '')}",
            f"action: {row.get('owner_action', '')}",
            f"command: {row.get('command', '')}",
            f"stop: {row.get('stop_condition', '')}",
        ])
    lines.extend(["", "Safe assets now:"])
    for row in data["safeAssetsNow"]:
        label = row.get("assetId") or row.get("asset_id") or row.get("asset") or ""
        target = row.get("targetUrl") or row.get("target_url") or row.get("target") or ""
        status = row.get("fulfillmentStatus") or row.get("status") or ""
        lines.append(f"- {label} / {status}: {target}")
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lead and offer quickstart packet for LoveTypes promotion decisions.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_lead_offer_quickstart={args.output}")
        print(f"promotion_lead_offer_quickstart_json={args.json_output}")
        print(f"promotion_lead_offer_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_lead_offer_quickstart_handoff_rows={metrics['handoffRows']}")
    print(f"promotion_lead_offer_quickstart_current_blockers={metrics['handoffCurrentBlockers']}")
    print(f"promotion_lead_offer_quickstart_real_leads={metrics['realLeads']}")
    print(f"promotion_lead_offer_quickstart_ready_routes={metrics['readyLeadRoutes']}")
    print(f"promotion_lead_offer_quickstart_public_free_assets={metrics['publicFreeAssets']}")
    print(f"promotion_lead_offer_quickstart_offer_queue_ready={metrics['offerQueueReady']}")
    print(f"promotion_lead_offer_quickstart_offer_queue_blocked={metrics['offerQueueBlocked']}")
    print(f"promotion_lead_offer_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
