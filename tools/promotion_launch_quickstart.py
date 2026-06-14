#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
STAGE_MATRIX = PROMOTION_DIR / "stage-transition-matrix.json"
PROFILE_QUICKSTART = PROMOTION_DIR / "profile-quickstart.json"
PUBLISH_QUICKSTART = PROMOTION_DIR / "first-batch-publish-quickstart.json"
KPI_QUICKSTART = PROMOTION_DIR / "first-batch-kpi-quickstart.json"
LEAD_OFFER_QUICKSTART = PROMOTION_DIR / "lead-offer-quickstart.json"
LAUNCH_CLIPBOARD = PROMOTION_DIR / "launch-clipboard.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "launch-quickstart.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "launch-quickstart.json"
DEFAULT_TXT_OUTPUT = PROMOTION_DIR / "launch-quickstart.txt"
FORBIDDEN_TERMS = ("診斷", "療效", "保證修復", "必須購買")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def metric(payload: dict, key: str, default: int = 0) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        values = {}
    try:
        return int(values.get(key, payload.get(key, default)) or default)
    except (TypeError, ValueError):
        return default


def proof_file_for(platform: str) -> str:
    return f"docs/promotion/first-round/proof-{platform}.txt"


def build_profile_actions(profile: dict) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for row in profile.get("platforms", []) if isinstance(profile.get("platforms"), list) else []:
        platform = str(row.get("platform", ""))
        actions.append({
            "kind": "profile",
            "platform": platform,
            "label": str(row.get("label", platform)),
            "status": str(row.get("actionStatus", "")),
            "copy": str(row.get("bio", "")).strip(),
            "profileLink": str(row.get("profileLink", "")),
            "proofFile": str(row.get("proofFile") or proof_file_for(platform)),
            "checkCommand": str(row.get("checkCommand", "")),
            "writeCommand": str(row.get("writeCommand", "")),
            "stopCondition": str(row.get("stopCondition", "")),
        })
    return actions


def build_next_actions(publish: dict, kpi: dict, lead_offer: dict) -> list[dict[str, str]]:
    publish_metrics = publish.get("metrics", {}) if isinstance(publish.get("metrics"), dict) else {}
    kpi_metrics = kpi.get("metrics", {}) if isinstance(kpi.get("metrics"), dict) else {}
    lead_metrics = lead_offer.get("metrics", {}) if isinstance(lead_offer.get("metrics"), dict) else {}
    return [
        {
            "kind": "publish",
            "status": "blocked_until_profile_links",
            "title": "First three platform posts",
            "current": f"{int(publish_metrics.get('readyRows', 0) or 0)} ready / {int(publish_metrics.get('blockedRows', 0) or 0)} blocked",
            "command": "python3 tools/promotion_first_batch_publish_quickstart.py --check",
            "stopCondition": "Do not publish until all three profile links are set/live and proof is written back.",
        },
        {
            "kind": "kpi",
            "status": "blocked_until_public_post_url",
            "title": "First-batch minimum KPI backfill",
            "current": f"{int(kpi_metrics.get('readyForKpi', 0) or 0)} ready / {int(kpi_metrics.get('blockedRows', 0) or 0)} blocked",
            "command": "python3 tools/promotion_first_batch_kpi_quickstart.py --check",
            "stopCondition": "Do not write KPI values until public post URLs and analytics source proof exist.",
        },
        {
            "kind": "lead_offer",
            "status": "blocked_until_real_leads",
            "title": "Lead, asset, Luna, and offer decisions",
            "current": (
                f"{int(lead_metrics.get('realLeads', 0) or 0)} real leads / "
                f"{int(lead_metrics.get('offerQueueReady', 0) or 0)} ready offers"
            ),
            "command": "python3 tools/promotion_lead_offer_quickstart.py --check",
            "stopCondition": "Do not create paid or priority offer experiments without repeated traceable demand.",
        },
    ]


def build_quickstart() -> dict:
    master = read_json(MASTER_GATE)
    stage = read_json(STAGE_MATRIX)
    profile = read_json(PROFILE_QUICKSTART)
    publish = read_json(PUBLISH_QUICKSTART)
    kpi = read_json(KPI_QUICKSTART)
    lead_offer = read_json(LEAD_OFFER_QUICKSTART)
    clipboard = read_json(LAUNCH_CLIPBOARD)

    profile_actions = build_profile_actions(profile)
    next_actions = build_next_actions(publish, kpi, lead_offer)
    data = {
        "generatedAt": today(),
        "sources": {
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
            "stageTransitionMatrix": str(STAGE_MATRIX.relative_to(ROOT)),
            "profileQuickstart": str(PROFILE_QUICKSTART.relative_to(ROOT)),
            "firstBatchPublishQuickstart": str(PUBLISH_QUICKSTART.relative_to(ROOT)),
            "firstBatchKpiQuickstart": str(KPI_QUICKSTART.relative_to(ROOT)),
            "leadOfferQuickstart": str(LEAD_OFFER_QUICKSTART.relative_to(ROOT)),
            "launchClipboard": str(LAUNCH_CLIPBOARD.relative_to(ROOT)),
        },
        "metrics": {
            "stageIndex": metric(master, "stageIndex"),
            "stage": str(master.get("stage") or master.get("currentStage") or "profile_setup"),
            "profileConfigured": metric(master, "profileConfigured"),
            "firstBatchPublished": metric(master, "firstBatchPublished"),
            "minimumKpiRows": metric(master, "firstBatchMinimumKpiRows"),
            "leadReadyRoutes": metric(master, "leadReadyRoutes"),
            "readyOfferExperiments": metric(master, "readyOfferExperiments"),
            "commandReadyRows": metric(master, "commandReadyRows"),
            "blockedDecisions": metric(master, "commandBlockedRows"),
            "stageCurrentBlockers": metric(stage, "currentBlockers"),
            "profileActions": len(profile_actions),
            "profileReadyToConfigure": metric(profile, "readyToConfigure"),
            "publishReadyRows": metric(publish, "readyRows"),
            "kpiReadyRows": metric(kpi, "readyForKpi"),
            "realLeads": metric(lead_offer, "realLeads"),
            "offerQueueReady": metric(lead_offer, "offerQueueReady"),
            "clipboardReadyBlocks": metric(clipboard, "readyBlocks"),
            "clipboardBlockedBlocks": metric(clipboard, "blockedBlocks"),
        },
        "rules": [
            "Current allowed work is profile setup only unless the master gate advances.",
            "Run check commands before write commands, then refresh daily ops after real writeback.",
            "Profile proof must be real external evidence: screenshot, clicked public link, or timestamped platform proof.",
            "Publishing, KPI, Luna, affiliate, and paid offer experiments remain blocked while profileConfigured is 0.",
            "Do not use empty KPI or lead data to choose winning guardians or commercial direction.",
        ],
        "nowActions": profile_actions,
        "nextActions": next_actions,
        "issues": [],
    }
    data["issues"] = validate(data)
    data["metrics"]["issues"] = len(data["issues"])
    return data


def validate(data: dict) -> list[str]:
    issues: list[str] = []
    metrics = data["metrics"]
    if metrics["stage"] != "profile_setup":
        issues.append(f"expected current stage profile_setup before launch, got {metrics['stage']}")
    if metrics["stageCurrentBlockers"] != 1:
        issues.append("launch quickstart should expose exactly one current stage blocker")
    if metrics["profileActions"] != 3:
        issues.append(f"expected three profile now-actions, got {metrics['profileActions']}")
    if metrics["profileConfigured"] == 0 and metrics["publishReadyRows"] != 0:
        issues.append("publish rows must not be ready while profiles are unconfigured")
    if metrics["firstBatchPublished"] == 0 and metrics["kpiReadyRows"] != 0:
        issues.append("KPI rows must not be ready before public post URLs exist")
    if metrics["realLeads"] == 0 and metrics["offerQueueReady"] != 0:
        issues.append("offer queue must stay blocked without real lead evidence")
    for action in data["nowActions"]:
        label = f"{action.get('kind')}/{action.get('platform')}"
        link = str(action.get("profileLink", ""))
        copy = str(action.get("copy", ""))
        if "/start/" not in link or "utm_campaign=first_round_quiz_completion" not in link:
            issues.append(f"{label}: profile link missing first-round /start/ campaign")
        if "15 題" not in copy and "五種愛之語測驗" not in copy:
            issues.append(f"{label}: profile copy should keep the quiz CTA")
        if not action.get("checkCommand") or not action.get("writeCommand"):
            issues.append(f"{label}: missing check or write command")
        if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in str(action.get("writeCommand", "")):
            issues.append(f"{label}: write command must require real proof replacement")
        if not action.get("stopCondition"):
            issues.append(f"{label}: missing stop condition")
        if any(term in copy for term in FORBIDDEN_TERMS):
            issues.append(f"{label}: profile copy contains forbidden claim language")
    for action in data["nextActions"]:
        label = action.get("kind", "<next>")
        if not action.get("command") or not action.get("stopCondition"):
            issues.append(f"{label}: missing command or stop condition")
        if not str(action.get("status", "")).startswith("blocked"):
            issues.append(f"{label}: downstream action should remain blocked in profile setup stage")
    return issues


def render_markdown(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "# LoveTypes Launch Quickstart",
        "",
        f"- 產生日期：{data['generatedAt']}",
        f"- current stage：`{metrics['stage']}`",
        f"- stage current blockers：{metrics['stageCurrentBlockers']}",
        f"- profile configured：{metrics['profileConfigured']}",
        f"- first batch published：{metrics['firstBatchPublished']}",
        f"- minimum KPI rows：{metrics['minimumKpiRows']}",
        f"- real leads / ready offers：{metrics['realLeads']} / {metrics['offerQueueReady']}",
        f"- command ready / blocked decisions：{metrics['commandReadyRows']} / {metrics['blockedDecisions']}",
        f"- clipboard ready / blocked：{metrics['clipboardReadyBlocks']} / {metrics['clipboardBlockedBlocks']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "## Now: Profile Setup Only", ""])
    for action in data["nowActions"]:
        lines.extend([
            f"### {action['label']} (`{action['platform']}`)",
            "",
            f"- status：`{action['status']}`",
            f"- profile link：{action['profileLink']}",
            f"- proof file：`{action['proofFile']}`",
            f"- check：`{action['checkCommand']}`",
            f"- write：`{action['writeCommand']}`",
            f"- stop：{action['stopCondition']}",
            "",
        ])
    lines.extend(["## Next: Still Blocked", ""])
    for action in data["nextActions"]:
        lines.extend([
            f"- `{action['kind']}` / `{action['status']}`：{action['title']}；current：{action['current']}；check：`{action['command']}`；stop：{action['stopCondition']}",
        ])
    if data["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(data: dict) -> str:
    metrics = data["metrics"]
    lines = [
        "LoveTypes launch quickstart",
        f"generated: {data['generatedAt']}",
        f"stage: {metrics['stage']}",
        f"profile configured: {metrics['profileConfigured']}",
        f"first batch published: {metrics['firstBatchPublished']}",
        f"minimum KPI rows: {metrics['minimumKpiRows']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in data["rules"])
    lines.extend(["", "Now:"])
    for action in data["nowActions"]:
        lines.extend([
            "",
            f"=== {action['label']} / {action['platform']} ===",
            f"status: {action['status']}",
            f"profile link: {action['profileLink']}",
            f"proof file: {action['proofFile']}",
            f"check: {action['checkCommand']}",
            f"write: {action['writeCommand']}",
            f"stop: {action['stopCondition']}",
        ])
    lines.extend(["", "Next blocked:"])
    for action in data["nextActions"]:
        lines.append(f"- {action['kind']} / {action['status']}: {action['current']}")
    if data["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in data["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(data: dict, md_output: Path, json_output: Path, txt_output: Path) -> None:
    md_output.write_text(render_markdown(data), encoding="utf-8")
    json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    txt_output.write_text(render_text(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a single operator quickstart for the current LoveTypes launch stage.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--txt-output", default=str(DEFAULT_TXT_OUTPUT))
    args = parser.parse_args()

    data = build_quickstart()
    if not args.check:
        write_outputs(data, Path(args.output), Path(args.json_output), Path(args.txt_output))
        print(f"promotion_launch_quickstart={args.output}")
        print(f"promotion_launch_quickstart_json={args.json_output}")
        print(f"promotion_launch_quickstart_txt={args.txt_output}")
    metrics = data["metrics"]
    print(f"promotion_launch_quickstart_stage={metrics['stage']}")
    print(f"promotion_launch_quickstart_current_blockers={metrics['stageCurrentBlockers']}")
    print(f"promotion_launch_quickstart_profile_configured={metrics['profileConfigured']}")
    print(f"promotion_launch_quickstart_first_batch_published={metrics['firstBatchPublished']}")
    print(f"promotion_launch_quickstart_minimum_kpi_rows={metrics['minimumKpiRows']}")
    print(f"promotion_launch_quickstart_profile_actions={metrics['profileActions']}")
    print(f"promotion_launch_quickstart_publish_ready_rows={metrics['publishReadyRows']}")
    print(f"promotion_launch_quickstart_kpi_ready_rows={metrics['kpiReadyRows']}")
    print(f"promotion_launch_quickstart_real_leads={metrics['realLeads']}")
    print(f"promotion_launch_quickstart_offer_queue_ready={metrics['offerQueueReady']}")
    print(f"promotion_launch_quickstart_issues={metrics['issues']}")
    for issue in data["issues"]:
        print(issue)
    return 1 if data["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
