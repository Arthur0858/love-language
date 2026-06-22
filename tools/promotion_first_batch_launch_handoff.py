#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMO = ROOT / "docs" / "promotion" / "first-round"
READINESS = PROMO / "first-batch-publish-readiness-pack.json"
ASSETS = PROMO / "first-batch-asset-qa.json"
ACTIONS = PROMO / "first-batch-publish-action-sheet.json"
PROOF = PROMO / "launch-proof-control-sheet.json"
POST_BATCH = PROMO / "post-batch-import-quickstart.json"
OUTPUT_MD = PROMO / "first-batch-launch-handoff.md"
OUTPUT_JSON = PROMO / "first-batch-launch-handoff.json"


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def by_key(rows: list[dict], platform_key: str = "platform") -> dict[tuple[str, str], dict]:
    return {
        (str(r.get(platform_key, "")), str(r.get("task_id") or r.get("taskId") or "")): r
        for r in rows
        if isinstance(r, dict)
    }


def task_from_file(value: str) -> str:
    name = Path(value).name
    return name.removesuffix(".txt").split("-", 2)[2] if name.startswith("proof-") and name.endswith(".txt") else ""


def post_batch_by_key(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(str(r.get("p", "")), task_from_file(str(r.get("file", "")))): r for r in rows}


def start_url_ok(value: str) -> bool:
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "lovetypes.tw"
        and parsed.path == "/start/"
        and query.get("utm_medium") == ["social"]
        and query.get("utm_campaign") == ["first_round_quiz_completion"]
        and bool(query.get("utm_content", [""])[0])
    )


def build() -> dict:
    readiness = load(READINESS)
    assets = by_key(load(ASSETS).get("rows", []))
    actions = by_key(load(ACTIONS).get("rows", []))
    proof = load(PROOF)
    post_batch = load(POST_BATCH)
    post_batch_rows = post_batch_by_key(post_batch.get("rows", []))
    proof_metrics = proof.get("metrics", {}) if isinstance(proof.get("metrics"), dict) else {}
    rows: list[dict[str, str | int]] = []
    issues: list[str] = []

    for source in readiness.get("rows", []):
        platform, task_id = str(source.get("platform", "")), str(source.get("task_id", ""))
        key = (platform, task_id)
        action, asset, batch = actions.get(key, {}), assets.get(key, {}), post_batch_rows.get(key, {})
        row = {
            "platform": platform,
            "taskId": task_id,
            "scriptId": str(source.get("script_id", "")),
            "guardianId": str(source.get("guardian_id", "")),
            "title": str(source.get("title", "")),
            "schedule": f"{source.get('scheduled_date', '')} {source.get('scheduled_time', '')} Asia/Taipei",
            "status": str(source.get("operator_status", "")),
            "profileReady": 1 if str(source.get("profile_gate_ready", "0")) == "1" else 0,
            "assetReady": 1 if str(source.get("asset_qa_ready", "0")) == "1" else 0,
            "publishReady": 1 if str(source.get("operator_status", "")) == "ready_to_publish" else 0,
            "postBatchReady": 1 if int(batch.get("ready", 0) or 0) == 1 else 0,
            "trackedUrl": str(source.get("tracked_url") or action.get("tracked_url") or asset.get("trackedUrl") or ""),
            "proofFile": str(action.get("proof_file") or source.get("post_proof_file") or batch.get("file") or ""),
            "checkCommand": str(action.get("check_command", "")),
            "writeCommand": str(action.get("write_command", "")),
            "captionSource": "docs/promotion/first-round/first-batch-publish-action-sheet.md",
            "stop": str(source.get("stop_condition", "")),
        }
        rows.append(row)

    metrics = {
        "rows": len(rows),
        "profileGateReady": sum(int(r["profileReady"]) for r in rows),
        "assetReady": sum(int(r["assetReady"]) for r in rows),
        "publishReady": sum(int(r["publishReady"]) for r in rows),
        "postBatchReady": sum(int(r["postBatchReady"]) for r in rows),
        "postProofBlocked": int(proof_metrics.get("postBlocked", 0) or 0),
    }
    if metrics["rows"] < 1:
        issues.append("expected at least one launch handoff row")
    if metrics["assetReady"] != metrics["rows"]:
        issues.append("all first-batch assets must be prepared")
    if metrics["publishReady"] and metrics["profileGateReady"] != metrics["rows"]:
        issues.append("publish-ready rows require all active profile proofs")
    if metrics["postBatchReady"] and metrics["postProofBlocked"]:
        issues.append("post batch cannot be ready while proof control is blocked")
    for row in rows:
        label = f"{row['platform']}/{row['taskId']}"
        is_published = str(row["status"]) == "published"
        if not start_url_ok(str(row["trackedUrl"])):
            issues.append(f"{label}: trackedUrl must be /start/ with social first-round UTM")
        if not is_published and not str(row["proofFile"]).endswith(".txt"):
            issues.append(f"{label}: proofFile must be a .txt proof file")
        if not is_published and "promotion_post_text_import.py check" not in str(row["checkCommand"]):
            issues.append(f"{label}: missing proof check command")
        if not is_published and "promotion_post_text_import.py add" not in str(row["writeCommand"]):
            issues.append(f"{label}: missing proof write command")
        if not row["stop"]:
            issues.append(f"{label}: missing stop condition")
    return {
        "generatedAt": date.today().isoformat(),
        "sources": [str(p.relative_to(ROOT)) for p in [READINESS, ASSETS, ACTIONS, PROOF, POST_BATCH]],
        "commands": [
            "python3 tools/promotion_profile_batch_import.py --check",
            "python3 tools/promotion_profile_batch_import.py --add",
            "python3 tools/promotion_post_batch_import.py --check",
            "python3 tools/promotion_post_batch_import.py --add",
            "python3 tools/promotion_daily_ops_refresh.py && python3 tools/promotion_launch_sequence_dry_run.py",
        ],
        "metrics": metrics,
        "rows": rows,
        "issues": issues,
    }


def render_md(payload: dict) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes First Batch Launch Handoff",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- profile gate ready：{metrics['profileGateReady']}",
        f"- asset ready：{metrics['assetReady']}",
        f"- publish ready：{metrics['publishReady']}",
        f"- post batch ready：{metrics['postBatchReady']}",
        f"- post proof blocked：{metrics['postProofBlocked']}",
        f"- issues：{len(payload['issues'])}",
        "",
        "## Commands",
    ]
    lines += [f"- `{command}`" for command in payload["commands"]]
    lines += ["", "## Rows", ""]
    for row in payload["rows"]:
        lines += [
            f"### {row['platform']} · `{row['taskId']}`",
            f"- status：`{row['status']}`",
            f"- guardian：`{row['guardianId']}`",
            f"- schedule：{row['schedule']}",
            f"- tracked URL：{row['trackedUrl']}",
            f"- proof：`{row['proofFile']}`",
            f"- check：`{row['checkCommand']}`",
            f"- write：`{row['writeCommand']}`",
            f"- caption source：`{row['captionSource']}`",
            f"- stop：{row['stop']}",
            "",
        ]
    if payload["issues"]:
        lines += ["## Issues", *[f"- {issue}" for issue in payload["issues"]]]
    return "\n".join(lines).rstrip() + "\n"


def write(payload: dict) -> None:
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a compact first-batch launch handoff.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    metrics = payload["metrics"]
    if not args.check:
        write(payload)
        print(f"promotion_first_batch_launch_handoff={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_first_batch_launch_handoff_json={OUTPUT_JSON.relative_to(ROOT)}")
    for key, value in [
        ("rows", metrics["rows"]),
        ("profile_gate_ready", metrics["profileGateReady"]),
        ("asset_ready", metrics["assetReady"]),
        ("publish_ready", metrics["publishReady"]),
        ("post_batch_ready", metrics["postBatchReady"]),
        ("post_proof_blocked", metrics["postProofBlocked"]),
        ("issues", len(payload["issues"])),
    ]:
        print(f"promotion_first_batch_launch_handoff_{key}={value}")
    for issue in payload["issues"]:
        print(issue)
    return 1 if payload["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
