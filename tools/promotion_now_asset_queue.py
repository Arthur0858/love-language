#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
PACK_PATH = PROMOTION_DIR / "now-asset-production-pack.json"
QUEUE_CSV_PATH = PROMOTION_DIR / "now-asset-production-queue.csv"
QUEUE_JSON_PATH = PROMOTION_DIR / "now-asset-production-queue.json"
QUEUE_MD_PATH = PROMOTION_DIR / "now-asset-production-queue.md"
STEPS = [
    ("script_review", "腳本審核", "確認 Hook、字幕、留言引導與安全邊界。"),
    ("visual_prompt", "畫面提示整理", "把畫面建議整理成可交給生成或剪輯的鏡頭提示。"),
    ("asset_collection", "素材收集", "確認守護者圖、背景、字卡、音樂或素材來源。"),
    ("edit_cut", "剪輯製作", "完成 20-30 秒直式短片初版。"),
    ("subtitle_qa", "字幕 QA", "確認字幕短句、無錯字、手機可讀。"),
    ("safety_qa", "安全邊界 QA", "確認無診斷、療效、保證修復或必須購買說法。"),
    ("schedule_publish", "排程發布", "依平台發布簡報排程上片或排程。"),
    ("kpi_backfill", "KPI 回填", "發布後回填 posting-queue.csv 與 kpi-tracker.csv。"),
]
FIELDNAMES = [
    "guardian_id",
    "guardian_name",
    "script_id",
    "backlog_item_id",
    "step_id",
    "step_name",
    "status",
    "owner",
    "due_date",
    "title",
    "tracked_url",
    "output_file",
    "notes",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_rows(pack: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for script in pack.get("scripts", []):
        guardian = str(script.get("guardian_id", ""))
        script_id = str(script.get("id", ""))
        for step_id, step_name, step_note in STEPS:
            rows.append({
                "guardian_id": guardian,
                "guardian_name": str(script.get("guardian_name", "")),
                "script_id": script_id,
                "backlog_item_id": str(script.get("backlog_item_id", "")),
                "step_id": step_id,
                "step_name": step_name,
                "status": "planned",
                "owner": "",
                "due_date": "",
                "title": str(script.get("title", "")),
                "tracked_url": str(script.get("tracked_url", "")),
                "output_file": f"exports/lovetypes/{guardian}/{script_id}.mp4" if step_id == "edit_cut" else "",
                "notes": step_note,
            })
    return rows


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    expected = 5 * len(STEPS)
    if len(rows) != expected:
        issues.append(f"expected {expected} queue rows, got {len(rows)}")
    by_script = Counter(row.get("script_id", "") for row in rows)
    for script_id, count in by_script.items():
        if count != len(STEPS):
            issues.append(f"{script_id}: expected {len(STEPS)} steps, got {count}")
    for row in rows:
        label = f"{row.get('script_id', '<script>')}/{row.get('step_id', '<step>')}"
        for field in ("guardian_id", "guardian_name", "script_id", "backlog_item_id", "step_id", "step_name", "status", "title", "tracked_url", "notes"):
            if not row.get(field):
                issues.append(f"{label}: missing {field}")
        if row.get("status") not in {"planned", "in_progress", "done", "blocked", "skipped"}:
            issues.append(f"{label}: invalid status {row.get('status')}")
        if row.get("tracked_url") and "utm_campaign=first_round_quiz_completion" not in row["tracked_url"]:
            issues.append(f"{label}: tracked_url should include first_round_quiz_completion")
    return issues


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(rows: list[dict[str, str]]) -> str:
    scripts = {}
    for row in rows:
        scripts.setdefault(row["script_id"], []).append(row)
    lines = [
        "# LoveTypes Now Asset Production Queue",
        "",
        f"- 產生日期：{date.today().isoformat()}",
        f"- 腳本數：{len(scripts)}",
        f"- 製作步驟：{len(STEPS)}",
        f"- 佇列列數：{len(rows)}",
        "",
        "## 使用方式",
        "",
        "- 每支腳本依序完成腳本審核、素材、剪輯、字幕、安全 QA、排程與 KPI 回填。",
        "- `output_file` 是建議輸出路徑，可在剪輯完成後改成實際檔案。",
        "- 卡住時把 `status` 改為 `blocked`，並在 `notes` 補原因。",
        "",
    ]
    for script_id, script_rows in scripts.items():
        first = script_rows[0]
        lines.extend([
            f"## {first['guardian_name']} · {first['title']}",
            "",
            f"- 腳本 ID：`{script_id}`",
            f"- 追蹤連結：{first['tracked_url']}",
            "",
        ])
        for row in script_rows:
            lines.append(f"- [{row['status']}] {row['step_name']}：{row['notes']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(rows: list[dict[str, str]], csv_path: Path, json_path: Path, md_path: Path) -> None:
    write_csv(rows, csv_path)
    payload = {
        "generatedAt": date.today().isoformat(),
        "stepCount": len(STEPS),
        "rowCount": len(rows),
        "scriptCount": len({row["script_id"] for row in rows}),
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(rows), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LoveTypes now asset production queue.")
    parser.add_argument("--pack", default=str(PACK_PATH))
    parser.add_argument("--csv-output", default=str(QUEUE_CSV_PATH))
    parser.add_argument("--json-output", default=str(QUEUE_JSON_PATH))
    parser.add_argument("--md-output", default=str(QUEUE_MD_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows = build_rows(load_json(Path(args.pack)))
    issues = validate_rows(rows)
    if not args.check:
        write_outputs(rows, Path(args.csv_output), Path(args.json_output), Path(args.md_output))
        print(f"promotion_now_asset_queue={args.csv_output}")
        print(f"promotion_now_asset_queue_json={args.json_output}")
        print(f"promotion_now_asset_queue_md={args.md_output}")
    print(f"promotion_now_asset_queue_scripts={len({row['script_id'] for row in rows})}")
    print(f"promotion_now_asset_queue_steps={len(STEPS)}")
    print(f"promotion_now_asset_queue_rows={len(rows)}")
    print(f"promotion_now_asset_queue_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
