#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

import promotion_post_writeback as post_writeback


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
LAUNCH_READINESS_PATH = PROMOTION_DIR / "launch-readiness-gate.json"
MASTER_GATE_PATH = PROMOTION_DIR / "master-gate.json"
WEEKLY_DECISION_PATH = PROMOTION_DIR / "weekly-decision-evidence-checklist.json"
LEAD_DEMAND_PATH = PROMOTION_DIR / "lead-demand-gate.json"
OFFER_EXPERIMENT_PATH = PROMOTION_DIR / "offer-experiment-plan.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "blocker-resolution-checklist.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "blocker-resolution-checklist.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "blocker-resolution-checklist.csv"


FIELDNAMES = [
    "phase",
    "blocker_id",
    "scope",
    "status",
    "owner_action",
    "release_condition",
    "evidence_source",
    "writeback_command",
]


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def today() -> str:
    return date.today().isoformat()


def profile_rows(launch: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in launch.get("platformChecklist", []):
        platform = str(item.get("platform", ""))
        configured = bool(item.get("configured"))
        rows.append({
            "phase": "profile_setup",
            "blocker_id": f"profile_link_{platform}",
            "scope": platform,
            "status": "complete" if configured else "ready_to_act",
            "owner_action": "Set the platform profile/Bio link to the listed /start/ URL, then verify the copied platform link still keeps UTM.",
            "release_condition": "platform-profile-tracker.csv row is set/live with profile_link_set_date and traceable proof note.",
            "evidence_source": str(item.get("profileLink", "")),
            "writeback_command": f"python3 tools/promotion_profile_text_import.py add --input docs/promotion/first-round/proof-{platform}.txt --proof-note \"<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE> verified\"",
        })
    return rows


def publish_rows(launch: dict, profile_configured: bool) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in launch.get("firstBatchSchedule", []):
        platform = str(item.get("platform", ""))
        task_id = str(item.get("taskId", ""))
        published = bool(item.get("published"))
        rows.append({
            "phase": "publish_first_batch",
            "blocker_id": f"publish_{platform}_{task_id}",
            "scope": f"{platform}:{task_id}",
            "status": "complete" if published else ("ready_to_act" if profile_configured else "blocked_until_profile_links"),
            "owner_action": "Publish or schedule the first-batch Shorts post with quiz-only CTA, then copy the real public post URL.",
            "release_condition": "posting-queue.csv and platform-kpi-tracker.csv have status=published, published_date, and a verified HTTPS post_url.",
            "evidence_source": str(item.get("trackedUrl", "")),
            "writeback_command": f"python3 tools/promotion_post_text_import.py add --input docs/promotion/first-round/proof-{platform}-{task_id}.txt --proof-note \"{post_writeback.POST_PROOF_NOTE_PLACEHOLDER}\"",
        })
    return rows


def decision_rows(weekly: dict, launch: dict) -> list[dict[str, str]]:
    metrics = launch.get("metrics", {})
    items = weekly.get("items", [])
    rows: list[dict[str, str]] = []
    for item in items:
        check_id = str(item.get("check_id", ""))
        if check_id in {"profiles_configured", "first_batch_published", "commerce_changes_still_blocked"}:
            continue
        rows.append({
            "phase": str(item.get("phase", "weekly_decision")),
            "blocker_id": check_id,
            "scope": "first_round",
            "status": "complete" if item.get("operator_status") == "complete" else "blocked_until_evidence",
            "owner_action": str(item.get("expected_value", "")),
            "release_condition": str(item.get("evidence_note", "")),
            "evidence_source": "docs/promotion/first-round/weekly-decision-evidence-checklist.json",
            "writeback_command": "python3 tools/promotion_daily_ops_refresh.py",
        })
    if int(metrics.get("filledKpiRows", 0) or 0) <= 0:
        rows.append({
            "phase": "kpi_backfill",
            "blocker_id": "first_batch_minimum_kpi_rows",
            "scope": "first_batch",
            "status": "blocked_until_post_urls",
            "owner_action": "After public URLs exist, check platform analytics and site analytics before entering site_clicks, quiz_starts, and quiz_completions.",
            "release_condition": "At least first-batch rows have real source-checked KPI values or source-checked zeros.",
            "evidence_source": "docs/promotion/first-round/platform-kpi-tracker.csv",
            "writeback_command": "python3 tools/promotion_post_text_import.py add --input <post-proof.txt> --proof-note \"<REAL_PUBLIC_POST_URL_AND_ANALYTICS_SOURCE_PROOF>\"",
        })
    return rows


def lead_and_offer_rows(lead: dict, offer: dict) -> list[dict[str, str]]:
    lead_metrics = lead.get("metrics", {})
    offer_metrics = offer.get("metrics", {})
    rows = [
        {
            "phase": "lead_collection",
            "blocker_id": "no_real_leads",
            "scope": "lead_intake",
            "status": "complete" if int(lead_metrics.get("realLeads", 0) or 0) > 0 else "blocked_until_real_request",
            "owner_action": "Collect a real Contact/Keepsakes/Luna request with guardian, request type, reply email, consent, and source.",
            "release_condition": "lead-intake-tracker.csv has at least one non-template row with explicit consent and traceable source.",
            "evidence_source": "docs/promotion/first-round/lead-intake-tracker.csv",
            "writeback_command": "python3 tools/promotion_lead_text_import.py add --input <lead-request.txt> --proof-note \"<REAL_EMAIL_THREAD_OR_FORM_REQUEST_PROOF>\"",
        },
        {
            "phase": "offer_experiment",
            "blocker_id": "no_ready_offer_experiment",
            "scope": "commerce",
            "status": "complete" if int(offer_metrics.get("readyRows", 0) or 0) > 0 else "blocked_until_repeated_intent",
            "owner_action": "Wait for repeated route, lead, Luna, or affiliate intent before creating a paid pack or changing offer order.",
            "release_condition": "offer-experiment-plan.json has a ready experiment selected from non-empty demand evidence.",
            "evidence_source": "docs/promotion/first-round/offer-experiment-plan.json",
            "writeback_command": "python3 tools/promotion_offer_experiment_plan.py",
        },
    ]
    return rows


def build_rows() -> tuple[list[dict[str, str]], dict[str, object], list[str]]:
    launch = read_json(LAUNCH_READINESS_PATH)
    master = read_json(MASTER_GATE_PATH)
    weekly = read_json(WEEKLY_DECISION_PATH)
    lead = read_json(LEAD_DEMAND_PATH)
    offer = read_json(OFFER_EXPERIMENT_PATH)

    configured_profiles = sum(1 for item in launch.get("platformChecklist", []) if item.get("configured"))
    expected_profiles = max(1, len(launch.get("platformChecklist", [])))
    profile_configured = configured_profiles >= expected_profiles
    rows = []
    rows.extend(profile_rows(launch))
    rows.extend(publish_rows(launch, profile_configured))
    rows.extend(decision_rows(weekly, launch))
    rows.extend(lead_and_offer_rows(lead, offer))

    issues: list[str] = []
    if not any(row["status"] == "ready_to_act" for row in rows):
        issues.append("at least one blocker row should be actionable for the current stage")
    if int(master.get("metrics", {}).get("issues", 0) or 0) != 0:
        issues.append("master gate reports issues")
    if int(launch.get("metrics", {}).get("issues", 0) or 0) != 0:
        issues.append("launch readiness gate reports issues")
    for row in rows:
        command = row.get("writeback_command", "")
        label = row.get("blocker_id", "<blocker>")
        if row.get("phase") == "profile_setup":
            if "<REAL_SCREENSHOT_OR_PROFILE_CLICK_NOTE>" not in command:
                issues.append(f"{label}: profile writeback command must force real screenshot/click proof replacement")
            if "screenshot profile-" in command:
                issues.append(f"{label}: profile writeback command must not include scaffold screenshot filename")
        if row.get("blocker_id") == "first_batch_minimum_kpi_rows" and "<REAL_PUBLIC_POST_URL_AND_ANALYTICS_SOURCE_PROOF>" not in command:
            issues.append(f"{label}: KPI writeback command must force real post URL and analytics source proof replacement")
        if row.get("phase") == "lead_collection" and "<REAL_EMAIL_THREAD_OR_FORM_REQUEST_PROOF>" not in command:
            issues.append(f"{label}: lead writeback command must force real email/form proof replacement")

    metrics = {
        "rows": len(rows),
        "activeBlockers": sum(1 for row in rows if row["status"] != "complete"),
        "readyNow": sum(1 for row in rows if row["status"] == "ready_to_act"),
        "profileRows": sum(1 for row in rows if row["phase"] == "profile_setup"),
        "publishRows": sum(1 for row in rows if row["blocker_id"].startswith("publish_")),
        "decisionRows": sum(1 for row in rows if row["phase"] in {"publish_first_batch", "kpi_backfill", "weekly_review", "weekly_decision"}),
        "leadRows": sum(1 for row in rows if row["phase"] == "lead_collection"),
        "offerRows": sum(1 for row in rows if row["phase"] == "offer_experiment"),
        "currentStage": master.get("stage", ""),
        "emptyDataMode": int(bool(master.get("safety", {}).get("emptyDataMode"))),
    }
    return rows, metrics, issues


def render_markdown(rows: list[dict[str, str]], metrics: dict[str, object], issues: list[str]) -> str:
    lines = [
        "# LoveTypes Blocker Resolution Checklist",
        "",
        f"- 產生日期：{today()}",
        f"- current stage：`{metrics.get('currentStage', '')}`",
        f"- rows：{metrics.get('rows', 0)}",
        f"- active blockers：{metrics.get('activeBlockers', 0)}",
        f"- ready now：{metrics.get('readyNow', 0)}",
        f"- empty data mode：{metrics.get('emptyDataMode', 0)}",
        f"- issues：{len(issues)}",
        "",
        "## Rule",
        "",
        "- 只解除有外部證據的 blocker；不可用預設模板當成已完成。",
        "- 啟用平台 Profile 完成前，不發布第一批貼文。",
        "- 公開 URL 與 KPI 來源確認前，不做週決策、商品化或 Luna / 聯盟權重調整。",
        "",
        "## Checklist",
        "",
    ]
    for row in rows:
        mark = "x" if row["status"] == "complete" else " "
        lines.extend([
            f"- [{mark}] `{row['blocker_id']}`（{row['phase']} / {row['status']}）",
            f"  - scope：`{row['scope']}`",
            f"  - action：{row['owner_action']}",
            f"  - release：{row['release_condition']}",
            f"  - evidence：`{row['evidence_source']}`",
            f"  - writeback：`{row['writeback_command']}`",
        ])
    if issues:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
    lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the LoveTypes first-round blocker resolution checklist.")
    parser.add_argument("--check", action="store_true", help="Validate without writing output files.")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    rows, metrics, issues = build_rows()
    print(f"promotion_blocker_resolution_rows={metrics['rows']}")
    print(f"promotion_blocker_resolution_active={metrics['activeBlockers']}")
    print(f"promotion_blocker_resolution_ready_now={metrics['readyNow']}")
    print(f"promotion_blocker_resolution_profile_rows={metrics['profileRows']}")
    print(f"promotion_blocker_resolution_publish_rows={metrics['publishRows']}")
    print(f"promotion_blocker_resolution_decision_rows={metrics['decisionRows']}")
    print(f"promotion_blocker_resolution_lead_rows={metrics['leadRows']}")
    print(f"promotion_blocker_resolution_offer_rows={metrics['offerRows']}")
    print(f"promotion_blocker_resolution_empty_data={metrics['emptyDataMode']}")
    print(f"promotion_blocker_resolution_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1

    if not args.check:
        result = {
            "generatedAt": today(),
            "sources": {
                "launchReadiness": str(LAUNCH_READINESS_PATH.relative_to(ROOT)),
                "masterGate": str(MASTER_GATE_PATH.relative_to(ROOT)),
                "weeklyDecisionEvidence": str(WEEKLY_DECISION_PATH.relative_to(ROOT)),
                "leadDemand": str(LEAD_DEMAND_PATH.relative_to(ROOT)),
                "offerExperimentPlan": str(OFFER_EXPERIMENT_PATH.relative_to(ROOT)),
            },
            "metrics": metrics,
            "rows": rows,
            "issues": issues,
        }
        md_output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        md_output.write_text(render_markdown(rows, metrics, issues), encoding="utf-8")
        json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, rows)
        print(f"promotion_blocker_resolution_md={md_output.relative_to(ROOT)}")
        print(f"promotion_blocker_resolution_json={json_output.relative_to(ROOT)}")
        print(f"promotion_blocker_resolution_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
