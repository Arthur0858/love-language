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
KIT_PATH = ROOT / "promotion-kit.json"
LAUNCH_LINK_QA_PATH = PROMOTION_DIR / "launch-link-qa.json"
KPI_TRACKER_PATH = PROMOTION_DIR / "kpi-tracker.csv"
DEFAULT_OUTPUT_PATH = PROMOTION_DIR / "attribution-reconciliation.md"
DEFAULT_JSON_OUTPUT_PATH = PROMOTION_DIR / "attribution-reconciliation.json"
DEFAULT_CSV_OUTPUT_PATH = PROMOTION_DIR / "attribution-reconciliation.csv"

REVENUE_FIELDS = [
    "free_keepsake_downloads",
    "supply_lead_requests",
    "luna_pack_clicks",
    "affiliate_book_clicks",
    "contact_requests",
]
ROUTE_FIELDS = ["resources_clicks", "repair_plan_clicks", "luna_clicks", "keepsake_clicks"]
REQUIRED_KPI_FIELDS = [
    "site_clicks",
    "quiz_starts",
    "quiz_completions",
    "guardian_result_clicks",
    *ROUTE_FIELDS,
    *REVENUE_FIELDS,
]
CSV_FIELDS = [
    "source_type",
    "platform",
    "task_id",
    "script_id",
    "guardian_id",
    "guardian_name",
    "content_angle",
    "utm_content",
    "tracked_url",
    "kpi_row_status",
    "decision_stage",
    "next_writeback",
    "contact_email_match",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def parse_int(value: str | None) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def is_filled(row: dict[str, str]) -> bool:
    return bool((row.get("post_url") or "").strip()) and any(parse_int(row.get(field)) for field in REQUIRED_KPI_FIELDS)


def decision_stage(metrics: dict[str, int]) -> str:
    quiz = metrics.get("quiz_completions", 0)
    route = sum(metrics.get(field, 0) for field in ROUTE_FIELDS)
    lead = metrics.get("supply_lead_requests", 0) + metrics.get("contact_requests", 0)
    paid = metrics.get("luna_pack_clicks", 0) + metrics.get("affiliate_book_clicks", 0)
    free = metrics.get("free_keepsake_downloads", 0)
    if paid > 0:
        return "test_soft_offer"
    if lead > 0:
        return "build_owned_asset"
    if route > 0 or free > 0:
        return "deepen_identity_asset"
    if quiz > 0:
        return "scale_quiz_completion"
    return "collect_signal"


def stage_writeback(stage: str) -> str:
    if stage == "test_soft_offer":
        return "Keep quiz CTA first; note Luna or affiliate click source before testing a softer result-page offer."
    if stage == "build_owned_asset":
        return "Create or prioritize the matching free PDF, wallpaper, short ritual, or Luna request lead magnet."
    if stage == "deepen_identity_asset":
        return "Strengthen keepsake and guardian route prompts for this utm_content before adding paid emphasis."
    if stage == "scale_quiz_completion":
        return "Publish one nearby hook variation and watch result-to-route clicks before monetizing."
    return "Publish or backfill KPI first; do not pick a winning guardian from empty data."


def task_lookup(kit: dict) -> dict[str, dict]:
    tasks = kit.get("publishingTasks", [])
    if not isinstance(tasks, list):
        return {}
    return {str(task.get("utmContent", "")): task for task in tasks if task.get("utmContent")}


def kpi_lookup(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("utm_content", ""): row for row in rows if row.get("utm_content")}


def metrics_for(row: dict[str, str] | None) -> dict[str, int]:
    row = row or {}
    return {field: parse_int(row.get(field)) for field in REQUIRED_KPI_FIELDS}


def build_rows(kit: dict, launch_rows: list[dict], kpi_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    tasks_by_utm = task_lookup(kit)
    kpi_by_utm = kpi_lookup(kpi_rows)
    rows: list[dict[str, object]] = []
    for link in launch_rows:
        utm_content = str(link.get("utm_content", ""))
        source_type = str(link.get("source_type", ""))
        task = tasks_by_utm.get(utm_content, {})
        kpi = kpi_by_utm.get(utm_content)
        metrics = metrics_for(kpi)
        stage = decision_stage(metrics) if kpi else "collect_signal"
        guardian_id = str(task.get("guardianId") or link.get("guardian_id") or "")
        rows.append({
            "source_type": source_type,
            "platform": str(link.get("platform", "")),
            "task_id": str(task.get("taskId") or link.get("task_id") or ""),
            "script_id": str(task.get("scriptId") or link.get("script_id") or ""),
            "guardian_id": guardian_id,
            "guardian_name": str(task.get("guardianName", "")),
            "content_angle": str(task.get("contentAngle", "")),
            "utm_content": utm_content,
            "tracked_url": str(link.get("url", "")),
            "kpi_row_status": "filled" if kpi and is_filled(kpi) else ("ready_for_backfill" if kpi else "profile_link_only"),
            "decision_stage": stage,
            "next_writeback": stage_writeback(stage),
            "contact_email_match": f"Campaign content / 推廣內容 = {utm_content}",
            "metrics": metrics,
        })
    rows.sort(key=lambda row: (str(row["source_type"]), str(row["guardian_id"]), str(row["utm_content"]), str(row["platform"])))
    return rows


def validate_payload(payload: dict, launch: dict, kpi_fields: list[str]) -> list[str]:
    issues: list[str] = []
    rows = payload.get("rows", [])
    expected_total = launch.get("rowCount")
    expected_profile_rows = launch.get("profileLinks")
    expected_shorts_rows = launch.get("shortsLinks")
    if not isinstance(expected_total, int):
        expected_total = len(launch.get("rows", [])) if isinstance(launch.get("rows"), list) else 0
    if not isinstance(expected_profile_rows, int):
        expected_profile_rows = sum(1 for row in launch.get("rows", []) if row.get("source_type") == "profile") if isinstance(launch.get("rows"), list) else 0
    if not isinstance(expected_shorts_rows, int):
        expected_shorts_rows = sum(1 for row in launch.get("rows", []) if row.get("source_type") == "shorts") if isinstance(launch.get("rows"), list) else 0
    if len(rows) != expected_total:
        issues.append(f"expected {expected_total} attribution rows, got {len(rows)}")
    counts = Counter(str(row.get("source_type", "")) for row in rows)
    if counts.get("profile") != expected_profile_rows:
        issues.append(f"expected {expected_profile_rows} profile attribution rows, got {counts.get('profile', 0)}")
    if counts.get("shorts") != expected_shorts_rows:
        issues.append(f"expected {expected_shorts_rows} shorts attribution rows, got {counts.get('shorts', 0)}")
    missing_kpi = [field for field in REQUIRED_KPI_FIELDS if field not in kpi_fields]
    if missing_kpi:
        issues.append("KPI tracker missing fields: " + ", ".join(missing_kpi))
    seen_utm: set[str] = set()
    for row in rows:
        label = str(row.get("utm_content", "<missing>"))
        if not label:
            issues.append("attribution row missing utm_content")
        elif label in seen_utm:
            issues.append(f"duplicate utm_content {label}")
        seen_utm.add(label)
        if row.get("source_type") == "shorts":
            for field in ("task_id", "script_id", "guardian_id", "content_angle"):
                if not row.get(field):
                    issues.append(f"{label}: missing {field}")
        if label and label not in str(row.get("tracked_url", "")):
            issues.append(f"{label}: tracked_url should contain matching utm_content")
        if label and label not in str(row.get("contact_email_match", "")):
            issues.append(f"{label}: contact_email_match should name the same utm_content")
        if row.get("decision_stage") not in {"collect_signal", "scale_quiz_completion", "deepen_identity_asset", "build_owned_asset", "test_soft_offer"}:
            issues.append(f"{label}: unknown decision_stage {row.get('decision_stage')}")
    return issues


def render_markdown(payload: dict) -> str:
    lines = [
        "# LoveTypes Attribution Reconciliation",
        "",
        f"- 產生日期：{payload['generatedAt']}",
        f"- Attribution rows：{payload['rowCount']}",
        f"- Profile rows：{payload['profileRows']}",
        f"- Shorts rows：{payload['shortsRows']}",
        f"- 已有 KPI row：{payload['kpiRows']}",
        f"- 已完整回填 KPI row：{payload['filledKpiRows']}",
        "",
        "## 使用方式",
        "",
        "- 發布或收到 Contact 信後，先找信件中的 `推廣內容 / Campaign content`，對回本表 `utm_content`。",
        "- 若是 Shorts row，把 `post_url` 與平台數據回填到 `kpi-tracker.csv` 的同一個 `utm_content`。",
        "- 若是 Profile row，把平台首頁數據回填到 `platform-profile-tracker.csv`，不要混進單支影片 KPI。",
        "- 沒有 KPI 前只維持 `collect_signal`，不判定優勝守護者、不加重付費 CTA。",
        "",
        "## Decision Stages",
        "",
        "- `collect_signal`: 先發布或回填資料。",
        "- `scale_quiz_completion`: 有測驗完成，先放大相近 hook。",
        "- `deepen_identity_asset`: 有路線或收藏興趣，先強化免費守護者資產。",
        "- `build_owned_asset`: 有補給或 Contact 意圖，優先做 Email/免費素材承接。",
        "- `test_soft_offer`: 有 Luna 或聯盟點擊，再測柔性商品承接。",
        "",
        "## Rows",
        "",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"### {row['utm_content']}",
            "",
            f"- type：`{row['source_type']}`",
            f"- platform：`{row['platform']}`",
            f"- guardian：`{row['guardian_id']}` {row['guardian_name']}",
            f"- angle：{row['content_angle']}",
            f"- KPI status：`{row['kpi_row_status']}`",
            f"- decision：`{row['decision_stage']}`",
            f"- Contact 對照：`{row['contact_email_match']}`",
            f"- 下一步：{row['next_writeback']}",
            f"- URL：{row['tracked_url']}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def write_outputs(payload: dict, output: Path, json_output: Path, csv_output: Path) -> None:
    output.write_text(render_markdown(payload), encoding="utf-8")
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(payload["rows"], csv_output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Map LoveTypes UTM attribution, Contact handoff, and KPI rows into one monetization reconciliation sheet.")
    parser.add_argument("--kit", default=str(KIT_PATH))
    parser.add_argument("--launch-link-qa", default=str(LAUNCH_LINK_QA_PATH))
    parser.add_argument("--kpi-tracker", default=str(KPI_TRACKER_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT_PATH))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    kit = read_json(Path(args.kit))
    launch = read_json(Path(args.launch_link_qa))
    kpi_fields, kpi_rows = read_csv(Path(args.kpi_tracker))
    rows = build_rows(kit, launch.get("rows", []), kpi_rows)
    payload = {
        "generatedAt": date.today().isoformat(),
        "source": {
            "promotionKit": str(Path(args.kit).resolve().relative_to(ROOT)),
            "launchLinkQa": str(Path(args.launch_link_qa).resolve().relative_to(ROOT)),
            "kpiTracker": str(Path(args.kpi_tracker).resolve().relative_to(ROOT)),
        },
        "rowCount": len(rows),
        "profileRows": sum(1 for row in rows if row["source_type"] == "profile"),
        "shortsRows": sum(1 for row in rows if row["source_type"] == "shorts"),
        "expectedRows": launch.get("rowCount", len(launch.get("rows", []))),
        "expectedProfileRows": launch.get("profileLinks"),
        "expectedShortsRows": launch.get("shortsLinks"),
        "kpiRows": len(kpi_rows),
        "filledKpiRows": sum(1 for row in kpi_rows if is_filled(row)),
        "decisionRule": "Do not intensify paid or affiliate CTAs until quiz completions create route, lead, Luna, or affiliate intent for the same utm_content.",
        "rows": rows,
    }
    issues = validate_payload(payload, launch, kpi_fields)
    payload["issues"] = issues
    if not args.check:
        write_outputs(payload, Path(args.output), Path(args.json_output), Path(args.csv_output))
        print(f"promotion_attribution_reconciliation={args.output}")
        print(f"promotion_attribution_reconciliation_json={args.json_output}")
        print(f"promotion_attribution_reconciliation_csv={args.csv_output}")
    print(f"promotion_attribution_reconciliation_rows={payload['rowCount']}")
    print(f"promotion_attribution_reconciliation_profile_rows={payload['profileRows']}")
    print(f"promotion_attribution_reconciliation_shorts_rows={payload['shortsRows']}")
    print(f"promotion_attribution_reconciliation_kpi_rows={payload['kpiRows']}")
    print(f"promotion_attribution_reconciliation_filled_kpi_rows={payload['filledKpiRows']}")
    print(f"promotion_attribution_reconciliation_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
