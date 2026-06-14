#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import promotion_attribution_reconciliation as attribution
import promotion_kpi_schema_audit as schema_audit
import promotion_kpi_writeback_consistency_audit as writeback_audit


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
OUTPUT_MD = PROMOTION_DIR / "kpi-attribution-health-report.md"
OUTPUT_JSON = PROMOTION_DIR / "kpi-attribution-health-report.json"


def today() -> str:
    return date.today().isoformat()


def attribution_metrics() -> tuple[dict[str, int], list[str]]:
    kit = attribution.read_json(attribution.KIT_PATH)
    launch = attribution.read_json(attribution.LAUNCH_LINK_QA_PATH)
    kpi_fields, kpi_rows = attribution.read_csv(attribution.KPI_TRACKER_PATH)
    rows = attribution.build_rows(kit, launch.get("rows", []), kpi_rows)
    payload = {
        "rowCount": len(rows),
        "profileRows": sum(1 for row in rows if row["source_type"] == "profile"),
        "shortsRows": sum(1 for row in rows if row["source_type"] == "shorts"),
        "expectedRows": launch.get("rowCount", len(launch.get("rows", []))),
        "expectedProfileRows": launch.get("profileLinks"),
        "expectedShortsRows": launch.get("shortsLinks"),
        "kpiRows": len(kpi_rows),
        "filledKpiRows": sum(1 for row in kpi_rows if attribution.is_filled(row)),
        "attributionPolicy": attribution.attribution_policy(),
        "rows": rows,
    }
    issues = attribution.validate_payload(payload, launch, kpi_fields)
    return {
        "rows": int(payload["rowCount"]),
        "profileRows": int(payload["profileRows"]),
        "shortsRows": int(payload["shortsRows"]),
        "kpiRows": int(payload["kpiRows"]),
        "filledKpiRows": int(payload["filledKpiRows"]),
    }, issues


def build_report() -> dict:
    schema_metrics, schema_issues = schema_audit.validate()
    writeback_metrics, writeback_issues = writeback_audit.validate()
    attribution_stats, attribution_issues = attribution_metrics()
    issues = [*schema_issues, *writeback_issues, *attribution_issues]
    return {
        "generatedAt": today(),
        "sources": {
            "promotionKit": "promotion-kit.json",
            "funnelEvents": "funnel-events.json",
            "commerceCatalog": "commerce-catalog.json",
            "kpiTracker": "docs/promotion/first-round/kpi-tracker.csv",
            "platformKpiTracker": "docs/promotion/first-round/platform-kpi-tracker.csv",
            "platformProfileTracker": "docs/promotion/first-round/platform-profile-tracker.csv",
            "attributionReconciliation": "docs/promotion/first-round/attribution-reconciliation.csv",
        },
        "schemaMetrics": schema_metrics,
        "writebackMetrics": writeback_metrics,
        "attributionMetrics": attribution_stats,
        "issues": issues,
    }


def render_markdown(report: dict) -> str:
    schema = report["schemaMetrics"]
    writeback = report["writebackMetrics"]
    attr = report["attributionMetrics"]
    lines = [
        "# LoveTypes KPI Attribution Health Report",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- KPI fields：{schema['promotion_kpi_schema_fields']}",
        f"- post / profile metrics：{schema['promotion_kpi_schema_post_metrics']} / {schema['promotion_kpi_schema_profile_metrics']}",
        f"- event KPIs / event names：{schema['promotion_kpi_schema_event_kpis']} / {schema['promotion_kpi_schema_event_names']}",
        f"- catalog events：{schema['promotion_kpi_schema_catalog_events']}",
        f"- revenue bridge KPIs：{schema['promotion_kpi_schema_revenue_bridge_kpis']}",
        f"- posting / platform / script rows：{writeback['postingRows']} / {writeback['platformRows']} / {writeback['scriptRows']}",
        f"- published / filled script rows：{writeback['publishedRows']} / {writeback['filledScriptRows']}",
        f"- attribution rows：{attr['rows']}",
        f"- profile / shorts attribution rows：{attr['profileRows']} / {attr['shortsRows']}",
        f"- filled KPI rows：{attr['filledKpiRows']}",
        f"- issues：{len(report['issues'])}",
        "",
        "## Rule",
        "",
        "- KPI tracker headers must match promotion-kit fields before any writeback.",
        "- Funnel events, commerce catalog conversions, and revenue bridge KPIs must stay mapped.",
        "- Posting queue, platform KPI tracker, script KPI tracker, weekly summary, and attribution rows must agree.",
        "- Empty KPI data must not become a decision signal.",
        "",
    ]
    if report["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in report["issues"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict) -> None:
    OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or check LoveTypes KPI attribution health report.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    report = build_report()
    schema = report["schemaMetrics"]
    writeback = report["writebackMetrics"]
    attr = report["attributionMetrics"]
    if not args.check:
        write_outputs(report)
        print(f"promotion_kpi_attribution_health_report={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_kpi_attribution_health_report_json={OUTPUT_JSON.relative_to(ROOT)}")
    print(f"promotion_kpi_attribution_health_kpi_fields={schema['promotion_kpi_schema_fields']}")
    print(f"promotion_kpi_attribution_health_event_kpis={schema['promotion_kpi_schema_event_kpis']}")
    print(f"promotion_kpi_attribution_health_catalog_events={schema['promotion_kpi_schema_catalog_events']}")
    print(f"promotion_kpi_attribution_health_posting_rows={writeback['postingRows']}")
    print(f"promotion_kpi_attribution_health_platform_rows={writeback['platformRows']}")
    print(f"promotion_kpi_attribution_health_script_rows={writeback['scriptRows']}")
    print(f"promotion_kpi_attribution_health_attribution_rows={attr['rows']}")
    print(f"promotion_kpi_attribution_health_filled_kpi_rows={attr['filledKpiRows']}")
    print(f"promotion_kpi_attribution_health_issues={len(report['issues'])}")
    for issue in report["issues"]:
        print(issue)
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
