#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import promotion_lead_form_audit as form_audit
import promotion_lead_form_importability_audit as import_audit


ROOT = Path(__file__).resolve().parents[1]
PROMOTION_DIR = ROOT / "docs" / "promotion" / "first-round"
OUTPUT_MD = PROMOTION_DIR / "lead-form-health-report.md"
OUTPUT_JSON = PROMOTION_DIR / "lead-form-health-report.json"


def today() -> str:
    return date.today().isoformat()


def build_report() -> dict:
    form = form_audit.audit()
    import_metrics, import_issues = import_audit.validate()
    issues = [*form["issues"], *import_issues]
    return {
        "generatedAt": today(),
        "sources": {
            "generator": "tools/generate_multilingual_site.py",
            "leadIntakePlaybook": "docs/promotion/first-round/lead-intake-playbook.json",
            "leadIntakeTracker": "docs/promotion/first-round/lead-intake-tracker.csv",
            "funnelEvents": "funnel-events.json",
            "importTool": "tools/promotion_lead_text_import.py",
        },
        "formMetrics": {
            "configuredForms": form["configuredForms"],
            "renderedForms": form["renderedForms"],
            "renderedSendEvents": form["renderedSendEvents"],
            "renderedCopyEvents": form["renderedCopyEvents"],
            "renderedRequiredFields": form["renderedRequiredFields"],
            "renderedGuardianOptions": form["renderedGuardianOptions"],
            "renderedIntakeOptions": form["renderedIntakeOptions"],
            "trackerFields": form["trackerFields"],
            "intakeTypes": form["intakeTypes"],
            "sourceOptions": form["sourceOptions"],
        },
        "importMetrics": import_metrics,
        "issues": issues,
    }


def render_markdown(report: dict) -> str:
    form = report["formMetrics"]
    imports = report["importMetrics"]
    lines = [
        "# LoveTypes Lead Form Health Report",
        "",
        f"- 產生日期：{report['generatedAt']}",
        f"- configured forms：{form['configuredForms']}",
        f"- rendered forms：{form['renderedForms']}",
        f"- send / copy events：{form['renderedSendEvents']} / {form['renderedCopyEvents']}",
        f"- required fields：{form['renderedRequiredFields']}",
        f"- guardian options：{form['renderedGuardianOptions']}",
        f"- intake options：{form['renderedIntakeOptions']}",
        f"- tracker fields：{form['trackerFields']}",
        f"- import languages：{imports['languages']}",
        f"- import sources：{imports['sources']}",
        f"- checked / valid sample texts：{imports['checkedTexts']} / {imports['validTexts']}",
        f"- issues：{len(report['issues'])}",
        "",
        "## Rule",
        "",
        "- Contact and keepsakes must both render structured lead request forms in every supported language.",
        "- Send and copy funnel events must exist before treating requests as attributable leads.",
        "- Generated structured request text must be importable before operators write lead tracker rows.",
        "- The form must keep consent, emergency, diagnosis, and counseling boundaries visible.",
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
    parser = argparse.ArgumentParser(description="Build or check the LoveTypes lead form health report.")
    parser.add_argument("--check", action="store_true", help="Validate without writing outputs.")
    args = parser.parse_args()
    report = build_report()
    form = report["formMetrics"]
    imports = report["importMetrics"]
    if not args.check:
        write_outputs(report)
        print(f"promotion_lead_form_health_report={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_lead_form_health_report_json={OUTPUT_JSON.relative_to(ROOT)}")
    print(f"promotion_lead_form_health_configured_forms={form['configuredForms']}")
    print(f"promotion_lead_form_health_rendered_forms={form['renderedForms']}")
    print(f"promotion_lead_form_health_send_events={form['renderedSendEvents']}")
    print(f"promotion_lead_form_health_copy_events={form['renderedCopyEvents']}")
    print(f"promotion_lead_form_health_required_fields={form['renderedRequiredFields']}")
    print(f"promotion_lead_form_health_import_checked_texts={imports['checkedTexts']}")
    print(f"promotion_lead_form_health_import_valid_texts={imports['validTexts']}")
    print(f"promotion_lead_form_health_issues={len(report['issues'])}")
    for issue in report["issues"]:
        print(issue)
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
