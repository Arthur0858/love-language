#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
FIRST_BATCH_PATH = PROMOTION_DIR / "first-batch-publication-packet.json"
PROOF_TEMPLATES_PATH = PROMOTION_DIR / "operation-proof-templates.json"
PROFILE_LINK_READINESS_PATH = PROMOTION_DIR / "profile-link-readiness-packet.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "first-batch-publish-action-sheet.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "first-batch-publish-action-sheet.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "first-batch-publish-action-sheet.csv"

FIELDNAMES = [
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "status",
    "action_status",
    "scheduled",
    "title",
    "tracked_url",
    "utm_content",
    "proof_file",
    "check_command",
    "write_command",
    "caption",
    "blocked_by",
]


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def post_proof_rows() -> dict[tuple[str, str], dict]:
    data = read_json(PROOF_TEMPLATES_PATH)
    rows = {}
    for row in data.get("rows", []):
        if row.get("kind") == "post_publish":
            rows[(str(row.get("platform", "")), str(row.get("taskId", "")))] = row
    return rows


def url_ok(value: str, expected_content: str) -> bool:
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "lovetypes.tw"
        and parsed.path == "/start/"
        and query.get("utm_medium") == ["social"]
        and query.get("utm_campaign") == ["first_round_quiz_completion"]
        and query.get("utm_content") == [expected_content]
    )


def build_rows() -> tuple[list[dict[str, str]], dict[str, int], list[str]]:
    packet = read_json(FIRST_BATCH_PATH)
    readiness = read_json(PROFILE_LINK_READINESS_PATH)
    proof_rows = post_proof_rows()
    profile_gate_ready = bool(packet.get("readyToPublish"))
    rows: list[dict[str, str]] = []
    issues: list[str] = []

    for item in packet.get("rows", []):
        platform = str(item.get("platform", ""))
        task_id = str(item.get("taskId", ""))
        proof = proof_rows.get((platform, task_id), {})
        published = bool(item.get("published"))
        action_status = "complete" if published else ("ready_to_publish" if profile_gate_ready else "blocked_until_profile_links")
        rows.append({
            "platform": platform,
            "task_id": task_id,
            "script_id": str(item.get("scriptId", "")),
            "guardian_id": str(item.get("guardianId", "")),
            "status": str(item.get("status", "")),
            "action_status": action_status,
            "scheduled": f"{item.get('scheduledDate', '')} {item.get('scheduledTime', '')} Asia/Taipei",
            "title": str(item.get("title", "")),
            "tracked_url": str(item.get("trackedUrl", "")),
            "utm_content": str(item.get("utmContent", "")),
            "proof_file": str(proof.get("path", "")),
            "check_command": str(proof.get("checkCommand", "")),
            "write_command": str(proof.get("writeCommand", "")),
            "caption": str(item.get("caption", "")),
            "blocked_by": "" if profile_gate_ready else "profile links are not all set/live",
        })

    if len(rows) < 1:
        issues.append("expected at least one first-batch publish row")
    if int(readiness.get("metrics", {}).get("publicReady", 0) or 0) != len(rows):
        issues.append("profile link readiness should match active first-batch platform count")
    if profile_gate_ready and int(readiness.get("metrics", {}).get("configured", 0) or 0) != len(rows):
        issues.append("profile gate cannot be ready unless all active profiles are configured")
    for row in rows:
        label = f"{row['platform']}/{row['task_id']}"
        is_complete = row["action_status"] == "complete"
        if not url_ok(row["tracked_url"], row["utm_content"]):
            issues.append(f"{label}: tracked_url should be /start/ with first-round social UTM")
        if "完成 15 題測驗" not in row["caption"] and "15-question quiz" not in row["caption"]:
            issues.append(f"{label}: caption should keep the quiz CTA")
        if any(forbidden in row["caption"] for forbidden in ("診斷", "療效", "必須購買")):
            issues.append(f"{label}: caption contains forbidden commercial or clinical claim")
        if not is_complete and "promotion_post_text_import.py check" not in row["check_command"]:
            issues.append(f"{label}: missing post text import check command")
        if not is_complete and "promotion_post_text_import.py add" not in row["write_command"]:
            issues.append(f"{label}: missing post text import add command")
        if not is_complete and not row["proof_file"].endswith(f"proof-{row['platform']}-{row['task_id']}.txt"):
            issues.append(f"{label}: proof file should match platform and task")

    metrics = {
        "rows": len(rows),
        "ready": sum(1 for row in rows if row["action_status"] == "ready_to_publish"),
        "blocked": sum(1 for row in rows if row["action_status"].startswith("blocked")),
        "complete": sum(1 for row in rows if row["action_status"] == "complete"),
        "profileLinksPublicReady": int(readiness.get("metrics", {}).get("publicReady", 0) or 0),
        "profileGateReady": int(profile_gate_ready),
    }
    return rows, metrics, issues


def render_markdown(payload: dict) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes First Batch Publish Action Sheet",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- ready：{metrics['ready']}",
        f"- blocked：{metrics['blocked']}",
        f"- complete：{metrics['complete']}",
        f"- profile links public ready：{metrics['profileLinksPublicReady']}",
        f"- profile gate ready：{metrics['profileGateReady']}",
        f"- issues：{len(payload['issues'])}",
        "",
        "## Rule",
        "",
        "- 啟用平台 profile link 都 set/live 且 gate ready 前，不發布首批貼文。",
        "- 發布後必須先用 proof text import `check` 驗證，再用 `add` 回填真實 post URL。",
        "- KPI 只能填平台或網站來源確認後的值；0 也必須是確認後的 0。",
        "",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"## {row['platform']} · `{row['task_id']}`",
            "",
            f"- action status：`{row['action_status']}`",
            f"- scheduled：{row['scheduled']}",
            f"- title：{row['title']}",
            f"- tracked URL：{row['tracked_url']}",
            f"- proof file：`{row['proof_file']}`",
            f"- check：`{row['check_command']}`",
            f"- write：`{row['write_command']}`",
        ])
        if row["blocked_by"]:
            lines.append(f"- blocked by：{row['blocked_by']}")
        lines.extend([
            "",
            "Caption:",
            "",
            "```text",
            row["caption"],
            "```",
            "",
        ])
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
        lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the first-batch publish action sheet after profile setup.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    rows, metrics, issues = build_rows()
    print(f"promotion_first_batch_publish_action_rows={metrics['rows']}")
    print(f"promotion_first_batch_publish_action_ready={metrics['ready']}")
    print(f"promotion_first_batch_publish_action_blocked={metrics['blocked']}")
    print(f"promotion_first_batch_publish_action_complete={metrics['complete']}")
    print(f"promotion_first_batch_publish_action_profile_public_ready={metrics['profileLinksPublicReady']}")
    print(f"promotion_first_batch_publish_action_profile_gate_ready={metrics['profileGateReady']}")
    print(f"promotion_first_batch_publish_action_issues={len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return 1

    if not args.check:
        payload = {
            "generatedAt": today(),
            "sources": {
                "firstBatchPublicationPacket": str(FIRST_BATCH_PATH.relative_to(ROOT)),
                "operationProofTemplates": str(PROOF_TEMPLATES_PATH.relative_to(ROOT)),
                "profileLinkReadiness": str(PROFILE_LINK_READINESS_PATH.relative_to(ROOT)),
            },
            "metrics": metrics,
            "rows": rows,
            "issues": issues,
        }
        md_output = Path(args.output)
        json_output = Path(args.json_output)
        csv_output = Path(args.csv_output)
        md_output.write_text(render_markdown(payload), encoding="utf-8")
        json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(csv_output, rows)
        print(f"promotion_first_batch_publish_action_md={md_output.relative_to(ROOT)}")
        print(f"promotion_first_batch_publish_action_json={json_output.relative_to(ROOT)}")
        print(f"promotion_first_batch_publish_action_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
