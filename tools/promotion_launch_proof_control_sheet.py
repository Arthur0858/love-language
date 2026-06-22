#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_BATCH = PROMOTION_DIR / "profile-batch-import-quickstart.json"
POST_BATCH = PROMOTION_DIR / "post-batch-import-quickstart.json"
LAUNCH_CLIPBOARD = PROMOTION_DIR / "launch-clipboard.json"
MASTER_GATE = PROMOTION_DIR / "master-gate.json"
BLOCKER_DIGEST = PROMOTION_DIR / "launch-blocker-digest.json"
PROFILE_QUICKSTART = PROMOTION_DIR / "profile-quickstart.json"
OUTPUT_MD = PROMOTION_DIR / "launch-proof-control-sheet.md"
OUTPUT_JSON = PROMOTION_DIR / "launch-proof-control-sheet.json"
OUTPUT_TXT = PROMOTION_DIR / "launch-proof-control-sheet.txt"


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def metric(payload: dict, key: str) -> int:
    values = payload.get("metrics", {})
    if not isinstance(values, dict):
        return 0
    try:
        return int(values.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def active_platforms() -> set[str]:
    if not PROFILE_QUICKSTART.exists():
        return {"youtube_shorts"}
    data = json.loads(PROFILE_QUICKSTART.read_text(encoding="utf-8"))
    platforms = {str(row.get("platform", "")) for row in data.get("platforms", []) if row.get("platform")}
    return platforms or {"youtube_shorts"}


def normalize_rows(rows: list[dict], proof_type: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in rows:
        platform = str(row.get("p") or row.get("platform") or "")
        file_path = str(row.get("file") or row.get("proofFile") or "")
        normalized.append({
            "proofType": proof_type,
            "platform": platform,
            "proofFile": file_path,
            "status": str(row.get("status", "")),
            "ready": str(row.get("ready", "0")),
            "issues": str(row.get("issues", "0")),
            "operatorAction": (
                "Replace placeholder proof note with real visible profile proof, then run profile batch check."
                if proof_type == "profile"
                else "Replace placeholder post_url and proof note with real public post proof, then run post batch check."
            ),
        })
    return normalized


def build_sheet() -> dict:
    profile = read_json(PROFILE_BATCH)
    post = read_json(POST_BATCH)
    clipboard = read_json(LAUNCH_CLIPBOARD)
    master = read_json(MASTER_GATE)
    blocker = read_json(BLOCKER_DIGEST)
    rows = normalize_rows(profile.get("rows", []), "profile") + normalize_rows(post.get("rows", []), "post")
    profile_ready = metric(profile, "readyRows")
    post_ready = metric(post, "readyRows")
    profile_blocked = metric(profile, "blockedRows")
    post_blocked = metric(post, "blockedRows")
    profile_placeholder = metric(profile, "placeholderProofRows")
    profile_real_ready = metric(profile, "realProofReadyRows")
    active_count = len(active_platforms())
    stage = str(master.get("stage") or blocker.get("stage") or "")
    master_metrics = master.get("metrics", {}) if isinstance(master.get("metrics"), dict) else {}
    master_profile_configured = int(master_metrics.get("profileConfigured", 0) or 0)
    master_first_batch_published = int(master_metrics.get("firstBatchPublished", 0) or 0)
    master_minimum_kpi_rows = int(master_metrics.get("firstBatchMinimumKpiRows", 0) or 0)
    steps = [
        {
            "id": "prepare_profile_proofs",
            "status": "complete" if profile_ready == active_count else "current_action",
            "command": "python3 tools/promotion_profile_batch_import.py --check",
            "release": f"profile batch readyRows is {active_count}.",
        },
        {
            "id": "write_profile_batch",
            "status": "complete" if master_profile_configured >= active_count else "blocked_until_profile_ready",
            "command": "python3 tools/promotion_profile_batch_import.py --add",
            "release": "master gate moves from profile_setup to first_batch_publish.",
        },
        {
            "id": "prepare_post_proofs",
            "status": "complete" if post_ready == active_count else "blocked_until_profile_gate",
            "command": "python3 tools/promotion_post_batch_import.py --check",
            "release": f"post batch readyRows is {active_count}.",
        },
        {
            "id": "write_post_batch",
            "status": "complete" if master_first_batch_published >= active_count else "blocked_until_post_ready",
            "command": "python3 tools/promotion_post_batch_import.py --add",
            "release": f"first batch has {active_count} published rows and minimum KPI rows.",
        },
        {
            "id": "refresh_and_review",
            "status": "complete" if master_minimum_kpi_rows >= active_count else "blocked_until_post_writeback",
            "command": "python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py",
            "release": "dry run stays green and weekly evidence gate can open.",
        },
    ]
    issues = validate(rows, steps, profile, post, clipboard, stage, master_profile_configured)
    return {
        "generatedAt": today(),
        "sources": {
            "profileBatch": str(PROFILE_BATCH.relative_to(ROOT)),
            "postBatch": str(POST_BATCH.relative_to(ROOT)),
            "launchClipboard": str(LAUNCH_CLIPBOARD.relative_to(ROOT)),
            "masterGate": str(MASTER_GATE.relative_to(ROOT)),
            "blockerDigest": str(BLOCKER_DIGEST.relative_to(ROOT)),
        },
        "metrics": {
            "rows": len(rows),
            "profileReady": profile_ready,
            "profileBlocked": profile_blocked,
            "profilePlaceholderProof": profile_placeholder,
            "profileRealProofReady": profile_real_ready,
            "postReady": post_ready,
            "postBlocked": post_blocked,
            "clipboardBlocks": metric(clipboard, "blocks"),
            "stage": stage,
            "issues": len(issues),
        },
        "rules": [
            "Profile proofs must be completed before post proofs are imported.",
            "Batch add commands are allowed only when all active rows in that batch are ready.",
            "Post proof requires a real public post URL and checked analytics/source note.",
            "No product, Luna, or affiliate decision is allowed while minimum KPI rows are empty.",
        ],
        "steps": steps,
        "rows": rows,
        "issues": issues,
    }


def validate(rows: list[dict[str, str]], steps: list[dict[str, str]], profile: dict, post: dict, clipboard: dict, stage: str, master_profile_configured: int) -> list[str]:
    issues: list[str] = []
    active = active_platforms()
    expected_rows = len(active) * 2
    if len(rows) != expected_rows:
        issues.append(f"expected {expected_rows} proof control rows, got {len(rows)}")
    if {row["proofType"] for row in rows} != {"profile", "post"}:
        issues.append("proof control rows must include profile and post rows")
    for proof_type in ("profile", "post"):
        platforms = {row["platform"] for row in rows if row["proofType"] == proof_type}
        if platforms != active:
            issues.append(f"{proof_type} rows must cover all active platforms")
    if len(steps) != 5:
        issues.append("proof control sheet must include five ordered steps")
    if master_profile_configured < len(active) and metric(profile, "readyRows") < len(active) and any(step["id"] == "write_profile_batch" and step["status"] == "complete" for step in steps):
        issues.append("profile write step cannot be complete before profile batch is ready")
    if stage in {"profile_setup", "first_batch_publish"} and metric(post, "readyRows") < len(active) and any(step["id"] == "write_post_batch" and step["status"] == "complete" for step in steps):
        issues.append("post write step cannot be complete before post batch is ready")
    if stage != "profile_setup" and metric(profile, "readyRows") == 0 and master_profile_configured < len(active):
        issues.append("stage cannot advance away from profile_setup while profile batch has no ready rows")
    for row in rows:
        if not row["proofFile"] or not row["status"] or not row["operatorAction"]:
            issues.append(f"{row['proofType']}/{row['platform']}: missing proof file, status, or operator action")
    return issues


def render_markdown(sheet: dict) -> str:
    metrics = sheet["metrics"]
    lines = [
        "# LoveTypes Launch Proof Control Sheet",
        "",
        f"- 產生日期：{sheet['generatedAt']}",
        f"- stage：`{metrics['stage']}`",
        f"- profile ready / blocked：{metrics['profileReady']} / {metrics['profileBlocked']}",
        f"- profile placeholder / real proof ready：{metrics['profilePlaceholderProof']} / {metrics['profileRealProofReady']}",
        f"- post ready / blocked：{metrics['postReady']} / {metrics['postBlocked']}",
        f"- proof rows：{metrics['rows']}",
        f"- clipboard blocks：{metrics['clipboardBlocks']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in sheet["rules"])
    lines.extend(["", "## Ordered Steps", ""])
    for step in sheet["steps"]:
        lines.extend([
            f"### `{step['id']}`",
            "",
            f"- status：`{step['status']}`",
            f"- command：`{step['command']}`",
            f"- release：{step['release']}",
            "",
        ])
    lines.extend(["## Proof Rows", ""])
    for row in sheet["rows"]:
        lines.append(
            f"- `{row['proofType']}` / `{row['platform']}`：`{row['status']}` ready={row['ready']} issues={row['issues']} file=`{row['proofFile']}`"
        )
    if sheet["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in sheet["issues"])
    return "\n".join(lines).rstrip() + "\n"


def render_text(sheet: dict) -> str:
    metrics = sheet["metrics"]
    lines = [
        f"generated: {sheet['generatedAt']}",
        f"stage: {metrics['stage']}",
        f"profile ready/blocked: {metrics['profileReady']}/{metrics['profileBlocked']}",
        f"profile placeholder/real proof ready: {metrics['profilePlaceholderProof']}/{metrics['profileRealProofReady']}",
        f"post ready/blocked: {metrics['postReady']}/{metrics['postBlocked']}",
        "",
        "steps:",
    ]
    lines.extend(f"- {step['id']}: {step['status']} | {step['command']}" for step in sheet["steps"])
    lines.extend(["", "proof rows:"])
    lines.extend(f"- {row['proofType']}/{row['platform']}: {row['status']} {row['proofFile']}" for row in sheet["rows"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(sheet: dict) -> None:
    public = {
        "generatedAt": sheet["generatedAt"],
        "metrics": sheet["metrics"],
        "steps": sheet["steps"],
        "rows": sheet["rows"],
        "issues": sheet["issues"],
    }
    OUTPUT_JSON.write_text(json.dumps(public, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(sheet), encoding="utf-8")
    OUTPUT_TXT.write_text(render_text(sheet), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one control sheet for LoveTypes launch profile/post proof import.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sheet = build_sheet()
    if not args.check:
        write_outputs(sheet)
        print(f"promotion_launch_proof_control_sheet={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_launch_proof_control_sheet_json={OUTPUT_JSON.relative_to(ROOT)}")
        print(f"promotion_launch_proof_control_sheet_txt={OUTPUT_TXT.relative_to(ROOT)}")
    metrics = sheet["metrics"]
    print(f"promotion_launch_proof_control_rows={metrics['rows']}")
    print(f"promotion_launch_proof_control_profile_ready={metrics['profileReady']}")
    print(f"promotion_launch_proof_control_profile_blocked={metrics['profileBlocked']}")
    print(f"promotion_launch_proof_control_profile_placeholder_proof={metrics['profilePlaceholderProof']}")
    print(f"promotion_launch_proof_control_profile_real_proof_ready={metrics['profileRealProofReady']}")
    print(f"promotion_launch_proof_control_post_ready={metrics['postReady']}")
    print(f"promotion_launch_proof_control_post_blocked={metrics['postBlocked']}")
    print(f"promotion_launch_proof_control_issues={metrics['issues']}")
    for issue in sheet["issues"]:
        print(issue)
    return 1 if sheet["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
