#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO = ROOT / "docs" / "promotion" / "first-round"
ACTION_SHEET = PROMO / "first-batch-kpi-action-sheet.json"
OUTPUT_MD = PROMO / "kpi-zero-source-rehearsal.md"
OUTPUT_JSON = PROMO / "kpi-zero-source-rehearsal.json"
POST_URLS = {
    "youtube_shorts": "https://www.youtube.com/shorts/lovetypes-kpi-source-rehearsal",
    "tiktok": "https://www.tiktok.com/@lovetypes/video/7390000000000000000",
    "instagram_reels": "https://www.instagram.com/reel/lovetypeskpisource/",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)}; run promotion_daily_ops_refresh.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def proof_text(row: dict, proof_note: str) -> str:
    platform = str(row.get("platform", ""))
    return "\n".join([
        "LoveTypes platform post writeback",
        f"platform: {platform}",
        f"task_id: {row.get('task_id', '')}",
        "status: published",
        f"published_date: {date.today().isoformat()}",
        f"post_url: {POST_URLS.get(platform, '')}",
        "site_clicks: 0",
        "quiz_starts: 0",
        "quiz_completions: 0",
        f"proof_note: {proof_note}",
        "",
    ])


def run_check(text: str) -> tuple[int, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, "tools/promotion_post_text_import.py", "check", "--input", str(temp_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return result.returncode, result.stdout.strip()
    finally:
        temp_path.unlink(missing_ok=True)


def build_payload() -> dict:
    action = load_json(ACTION_SHEET)
    rows = []
    issues: list[str] = []
    reject_note = f"public post URL verified {date.today().isoformat()}"
    pass_note = f"public post URL and analytics source checked {date.today().isoformat()}"
    for source in action.get("rows", []):
        platform = str(source.get("platform", ""))
        task_id = str(source.get("task_id", ""))
        reject_code, reject_output = run_check(proof_text(source, reject_note))
        pass_code, pass_output = run_check(proof_text(source, pass_note))
        rejected_zero_without_source = (
            reject_code != 0
            and "must include an explicit checked analytics/source note" in reject_output
        )
        accepted_zero_with_source = pass_code == 0 and "promotion_post_text_import_issues=0" in pass_output
        row_issues = []
        if not rejected_zero_without_source:
            row_issues.append("zero KPI without analytics/source proof should be rejected")
        if not accepted_zero_with_source:
            row_issues.append("zero KPI with analytics/source proof should pass")
        if platform not in POST_URLS:
            row_issues.append(f"missing rehearsal post URL for {platform}")
        issues.extend(f"{platform}/{task_id}: {issue}" for issue in row_issues)
        rows.append({
            "platform": platform,
            "taskId": task_id,
            "scriptId": str(source.get("script_id", "")),
            "rejectsZeroWithoutSource": 1 if rejected_zero_without_source else 0,
            "acceptsZeroWithSource": 1 if accepted_zero_with_source else 0,
            "issues": row_issues,
        })
    metrics = {
        "rows": len(rows),
        "rejectsZeroWithoutSource": sum(int(row["rejectsZeroWithoutSource"]) for row in rows),
        "acceptsZeroWithSource": sum(int(row["acceptsZeroWithSource"]) for row in rows),
    }
    expected_rows = len(action.get("rows", []))
    if metrics["rows"] != expected_rows:
        issues.append(f"expected {expected_rows} first-batch KPI rows, got {metrics['rows']}")
    return {
        "generatedAt": date.today().isoformat(),
        "source": str(ACTION_SHEET.relative_to(ROOT)),
        "metrics": metrics,
        "rows": rows,
        "policy": {
            "zeroKpiRequiresAnalyticsSourceProof": True,
            "noTrackerMutation": True,
            "emptyDataMustRemainFailClosed": True,
        },
        "issues": issues,
    }


def render_md(payload: dict) -> str:
    metrics = payload["metrics"]
    lines = [
        "# LoveTypes KPI Zero Source Rehearsal",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- rows：{metrics['rows']}",
        f"- rejects zero without source：{metrics['rejectsZeroWithoutSource']}",
        f"- accepts zero with source：{metrics['acceptsZeroWithSource']}",
        f"- issues：{len(payload['issues'])}",
        "",
        "## Rule",
        "",
        "- This rehearsal runs check commands only and never writes KPI trackers.",
        "- Zero KPI values are valid only when the proof note says analytics/source was checked.",
        "- Missing source proof must keep weekly and commerce decisions locked.",
        "",
        "## Rows",
        "",
    ]
    for row in payload["rows"]:
        lines.append(
            f"- `{row['platform']}` / `{row['taskId']}`：reject={row['rejectsZeroWithoutSource']} pass={row['acceptsZeroWithSource']} issues={len(row['issues'])}"
        )
    if payload["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in payload["issues"])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict) -> None:
    public_payload = {
        "generatedAt": payload["generatedAt"],
        "source": payload["source"],
        "metrics": payload["metrics"],
        "rows": [
            {
                "platform": row["platform"],
                "taskId": row["taskId"],
                "rejectsZeroWithoutSource": row["rejectsZeroWithoutSource"],
                "acceptsZeroWithSource": row["acceptsZeroWithSource"],
                "issues": len(row["issues"]),
            }
            for row in payload["rows"]
        ],
        "policy": payload["policy"],
        "issues": payload["issues"],
    }
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(public_payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rehearse zero KPI source-proof validation without tracker writes.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if not args.check:
        write_outputs(payload)
        print(f"promotion_kpi_zero_source_rehearsal={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_kpi_zero_source_rehearsal_json={OUTPUT_JSON.relative_to(ROOT)}")
    metrics = payload["metrics"]
    print(f"promotion_kpi_zero_source_rehearsal_rows={metrics['rows']}")
    print(f"promotion_kpi_zero_source_rehearsal_rejects_zero_without_source={metrics['rejectsZeroWithoutSource']}")
    print(f"promotion_kpi_zero_source_rehearsal_accepts_zero_with_source={metrics['acceptsZeroWithSource']}")
    print(f"promotion_kpi_zero_source_rehearsal_issues={len(payload['issues'])}")
    for issue in payload["issues"]:
        print(issue)
    return 1 if payload["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
