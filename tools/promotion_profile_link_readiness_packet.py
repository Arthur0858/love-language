#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
ACTION_SHEET_PATH = PROMOTION_DIR / "profile-setup-action-sheet.json"
LINK_QA_PATH = PROMOTION_DIR / "launch-link-qa.json"
PROFILE_COMPLETION_PATH = PROMOTION_DIR / "profile-completion-gate.json"
DEFAULT_MD_OUTPUT = PROMOTION_DIR / "profile-link-readiness-packet.md"
DEFAULT_JSON_OUTPUT = PROMOTION_DIR / "profile-link-readiness-packet.json"
DEFAULT_CSV_OUTPUT = PROMOTION_DIR / "profile-link-readiness-packet.csv"

FIELDNAMES = [
    "platform",
    "status",
    "profile_link",
    "public_ready",
    "action_status",
    "profile_configured",
    "write_command",
]


def today() -> str:
    return date.today().isoformat()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_metrics(output: str) -> dict[str, int]:
    metrics: dict[str, int] = {}
    for line in output.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        try:
            metrics[key.strip()] = int(value.strip())
        except ValueError:
            continue
    return metrics


def run_profile_public_smoke() -> tuple[dict[str, int], str, int]:
    proc = subprocess.run(
        [sys.executable, "tools/public_launch_link_smoke.py", "--source-type", "profile"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return parse_metrics(output), output, proc.returncode


def build_rows(action_sheet: dict, profile_completion: dict, public_ready: bool) -> list[dict[str, str]]:
    configured = int(profile_completion.get("metrics", {}).get("profileConfigured", 0) or 0)
    rows: list[dict[str, str]] = []
    for row in action_sheet.get("rows", []):
        platform = str(row.get("platform", ""))
        rows.append({
            "platform": platform,
            "status": str(row.get("status", "")),
            "profile_link": str(row.get("profile_link", "")),
            "public_ready": "1" if public_ready else "0",
            "action_status": str(row.get("action_status", "")),
            "profile_configured": "1" if str(row.get("action_status", "")) == "complete" else "0",
            "write_command": str(row.get("write_command", "")),
        })
    if configured and configured != sum(1 for row in rows if row["profile_configured"] == "1"):
        # Keep row data authoritative for operator display, but expose mismatch as an issue elsewhere.
        pass
    return rows


def validate(
    action_sheet: dict,
    link_qa: dict,
    profile_completion: dict,
    smoke_metrics: dict[str, int],
    smoke_code: int,
    rows: list[dict[str, str]],
) -> list[str]:
    issues: list[str] = []
    expected_rows = len(rows)
    if expected_rows < 1:
        issues.append("expected at least one active profile readiness row")
    if int(action_sheet.get("metrics", {}).get("rows", 0) or 0) != expected_rows:
        issues.append("profile setup action sheet should match active profile rows")
    if int(link_qa.get("profileLinks", 0) or 0) != expected_rows:
        issues.append("launch-link-qa should match active profile links")
    if smoke_code != 0:
        issues.append("profile public launch link smoke failed")
    if smoke_metrics.get("public_launch_link_checked") != expected_rows:
        issues.append("profile public launch link smoke should check all active links")
    if smoke_metrics.get("public_launch_link_profile_checked") != expected_rows:
        issues.append("profile public launch link smoke should report active profile links")
    if smoke_metrics.get("public_launch_link_quiz_entries") != expected_rows:
        issues.append("all profile links should expose quiz entry signals")
    if smoke_metrics.get("public_launch_link_safety_navs") != expected_rows:
        issues.append("all profile links should expose safety footer links")
    if smoke_metrics.get("public_launch_link_utm_checks") != expected_rows * 4:
        issues.append("profile public launch link smoke should validate UTM fields for all active links")
    if smoke_metrics.get("public_launch_link_issues", 1) != 0:
        issues.append("profile public launch link smoke reported issues")
    if int(profile_completion.get("metrics", {}).get("profileConfigured", 0) or 0) != 0 and not profile_completion.get("state", {}).get("readyForFirstBatchPublish"):
        issues.append("profile completion metrics and ready state are inconsistent")
    for row in rows:
        if row["public_ready"] != "1":
            issues.append(f"{row['platform']}: profile link is not public-ready")
        if row["action_status"] not in {"ready_to_configure", "ready_to_writeback", "complete"}:
            issues.append(f"{row['platform']}: unexpected action status {row['action_status']}")
    return issues


def render_markdown(payload: dict) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes Profile Link Readiness Packet",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- profile links：{metrics['rows']}",
        f"- public checked：{metrics['publicChecked']}",
        f"- public ready：{metrics['publicReady']}",
        f"- ready to configure：{metrics['readyToConfigure']}",
        f"- configured：{metrics['configured']}",
        f"- profile gate ready：{metrics['profileGateReady']}",
        f"- issues：{metrics['issues']}",
        "",
        "## Rule",
        "",
        "- `public ready` 只代表 LoveTypes `/start/` 追蹤連結可用，不代表平台 profile 已設定。",
        "- 只有完成外部平台設定、保存 proof note，並回填 profile tracker 後，才能解除 `profile_setup` gate。",
        "- 啟用平台 profile 都 set/live 前，不發布第一批 Shorts。",
        "",
        "## Rows",
        "",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"### {row['platform']}",
            "",
            f"- status：`{row['status']}`",
            f"- action：`{row['action_status']}`",
            f"- public ready：`{row['public_ready']}`",
            f"- configured：`{row['profile_configured']}`",
            f"- profile link：{row['profile_link']}",
            f"- write：`{row['write_command']}`",
            "",
        ])
    if payload["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
        lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a public-readiness packet for LoveTypes profile launch links.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_MD_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    args = parser.parse_args()

    action_sheet = read_json(ACTION_SHEET_PATH)
    link_qa = read_json(LINK_QA_PATH)
    profile_completion = read_json(PROFILE_COMPLETION_PATH)
    smoke_metrics, smoke_output, smoke_code = run_profile_public_smoke()
    public_ready = smoke_code == 0 and smoke_metrics.get("public_launch_link_issues") == 0
    rows = build_rows(action_sheet, profile_completion, public_ready)
    issues = validate(action_sheet, link_qa, profile_completion, smoke_metrics, smoke_code, rows)
    metrics = {
        "rows": len(rows),
        "publicChecked": smoke_metrics.get("public_launch_link_checked", 0),
        "publicProfileChecked": smoke_metrics.get("public_launch_link_profile_checked", 0),
        "publicReady": sum(1 for row in rows if row["public_ready"] == "1"),
        "readyToConfigure": sum(1 for row in rows if row["action_status"] == "ready_to_configure"),
        "readyToWriteback": sum(1 for row in rows if row["action_status"] == "ready_to_writeback"),
        "configured": sum(1 for row in rows if row["profile_configured"] == "1"),
        "profileGateReady": int(bool(profile_completion.get("state", {}).get("readyForFirstBatchPublish"))),
        "issues": len(issues),
    }

    print(f"promotion_profile_link_readiness_rows={metrics['rows']}")
    print(f"promotion_profile_link_readiness_public_checked={metrics['publicChecked']}")
    print(f"promotion_profile_link_readiness_public_ready={metrics['publicReady']}")
    print(f"promotion_profile_link_readiness_ready_configure={metrics['readyToConfigure']}")
    print(f"promotion_profile_link_readiness_ready_writeback={metrics['readyToWriteback']}")
    print(f"promotion_profile_link_readiness_configured={metrics['configured']}")
    print(f"promotion_profile_link_readiness_gate_ready={metrics['profileGateReady']}")
    print(f"promotion_profile_link_readiness_issues={metrics['issues']}")
    for issue in issues:
        print(issue)
    if issues:
        print(smoke_output.rstrip())
        return 1

    if not args.check:
        payload = {
            "generatedAt": today(),
            "sources": {
                "actionSheet": str(ACTION_SHEET_PATH.relative_to(ROOT)),
                "launchLinkQa": str(LINK_QA_PATH.relative_to(ROOT)),
                "profileCompletionGate": str(PROFILE_COMPLETION_PATH.relative_to(ROOT)),
            },
            "smoke": smoke_metrics,
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
        print(f"promotion_profile_link_readiness_md={md_output.relative_to(ROOT)}")
        print(f"promotion_profile_link_readiness_json={json_output.relative_to(ROOT)}")
        print(f"promotion_profile_link_readiness_csv={csv_output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
