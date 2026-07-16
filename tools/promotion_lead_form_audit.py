#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_multilingual_site.py"
LEAD_PLAYBOOK_PATH = ROOT / "docs" / "promotion" / "first-round" / "lead-intake-playbook.json"
LEAD_TRACKER_PATH = ROOT / "docs" / "promotion" / "first-round" / "lead-intake-tracker.csv"
FUNNEL_EVENTS_PATH = ROOT / "funnel-events.json"

REQUIRED_FORM_KEYS = {
    "title",
    "intro",
    "guardian",
    "unknown_guardian",
    "request_type",
    "asset",
    "email",
    "campaign",
    "context",
    "consent",
    "email_placeholder",
    "campaign_placeholder",
    "context_placeholder",
    "submit",
    "copy",
    "copied",
    "required",
    "invalid_email",
    "subject",
    "source_label",
    "source_contact",
    "source_keepsake",
    "body_header",
    "asset_options",
    "type_options",
}
REQUIRED_TRACKER_FIELDS = {
    "request_id",
    "date",
    "source",
    "utm_content",
    "contact_campaign_content",
    "guardian_id",
    "guardian_name",
    "intake_type",
    "requested_asset",
    "related_route",
    "kpi_writeback_field",
    "email_status",
    "consent_status",
    "priority",
    "status",
    "notes",
}
EXPECTED_FORM_SOURCES = {
    "contact": "contact_structured_request_mailto",
    "keepsake_waitlist": "keepsake_structured_request_mailto",
}
EXPECTED_COPY_EVENTS = {
    "contact_structured_request_copy",
    "keepsake_structured_request_copy",
}


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("lovetypes_generator_for_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def localized_path(lang: str, slug: str) -> Path:
    return ROOT / slug / "index.html" if lang == "zh" else ROOT / lang / slug / "index.html"


def read_csv_fieldnames(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or [])


def load_event_names(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for event in data.get("events", []):
        if isinstance(event, dict) and event.get("name"):
            names.add(str(event["name"]))
    return names


def audit() -> dict:
    generator = load_module(GENERATOR_PATH)
    lead_playbook = json.loads(LEAD_PLAYBOOK_PATH.read_text(encoding="utf-8"))
    tracker_fields = set(read_csv_fieldnames(LEAD_TRACKER_PATH))
    funnel_events = load_event_names(FUNNEL_EVENTS_PATH)
    langs = list(generator.LANGS.keys())
    guardians = set(generator.GUARDIANS.keys())
    intake_types = {item["type"] for item in lead_playbook.get("intakeTypes", [])}
    source_options = set(lead_playbook.get("sourceOptions", []))
    issues: list[str] = []

    if not REQUIRED_TRACKER_FIELDS.issubset(tracker_fields):
        missing = sorted(REQUIRED_TRACKER_FIELDS - tracker_fields)
        issues.append("lead-intake-tracker.csv missing fields: " + ", ".join(missing))
    if not {"contact", "keepsake_waitlist"}.issubset(source_options):
        issues.append("lead-intake playbook sourceOptions must include contact and keepsake_waitlist")

    configured_forms = 0
    rendered_forms = 0
    rendered_send_events = 0
    rendered_copy_events = 0
    rendered_required_fields = 0
    rendered_guardian_options = 0
    rendered_intake_options = 0

    for lang in langs:
        form = generator.LEAD_INTAKE_FORM.get(lang)
        if not form:
            issues.append(f"{lang}: missing LEAD_INTAKE_FORM copy")
            continue
        missing_keys = sorted(REQUIRED_FORM_KEYS - set(form))
        if missing_keys:
            issues.append(f"{lang}: lead form missing keys {', '.join(missing_keys)}")
            continue
        configured_forms += 1
        if set(form["type_options"]) != intake_types:
            issues.append(f"{lang}: lead form type_options do not match lead-intake playbook")
        if len(form.get("type_option_labels", [])) != len(form["type_options"]):
            issues.append(f"{lang}: lead form type option labels do not match configured values")
        if len(form["asset_options"]) < 5:
            issues.append(f"{lang}: lead form should offer at least five asset preferences")
        if "example.com" in form["email_placeholder"].lower() or "name@" in form["email_placeholder"].lower():
            issues.append(f"{lang}: lead form email placeholder should not use example/sample email text")
        if not any(token in form["invalid_email"].lower() for token in ("example", "test", "placeholder")):
            issues.append(f"{lang}: invalid_email text should mention blocked placeholder/test email domains")
        for safety_token in ("emergency", "診斷", "諮商", "diagnosis", "counseling", "緊急", "상담", "terapia"):
            if safety_token.lower() in form["consent"].lower():
                break
        else:
            issues.append(f"{lang}: consent text missing emergency/diagnosis/counseling boundary")

        for slug, source in (("contact", "contact"), ("keepsakes", "keepsake_waitlist")):
            html_path = localized_path(lang, slug)
            if not html_path.exists():
                issues.append(f"{lang}/{slug}: missing rendered page")
                continue
            html = html_path.read_text(encoding="utf-8")
            if 'placeholder="name@example.com"' in html:
                issues.append(f"{lang}/{slug}: rendered lead form should not use name@example.com placeholder")
            if 'name="campaign_content" type="hidden"' not in html:
                issues.append(f"{lang}/{slug}: campaign attribution should be hidden from the visitor form")
            for internal_value in intake_types:
                if f'>{internal_value}</option>' in html:
                    issues.append(f"{lang}/{slug}: internal request type is exposed as visible option text")
            if "blockedDomains" not in html or "setCustomValidity" not in html:
                issues.append(f"{lang}/{slug}: rendered lead form missing reserved email domain guard")
            source_marker = f'data-lead-intake-source="{source}"'
            if source_marker not in html:
                issues.append(f"{lang}/{slug}: missing {source_marker}")
                continue
            rendered_forms += 1
            event = EXPECTED_FORM_SOURCES[source]
            copy_event = event.replace("_mailto", "_copy")
            if f'data-funnel-event="{event}"' in html:
                rendered_send_events += 1
            else:
                issues.append(f"{lang}/{slug}: missing send funnel event {event}")
            if f'data-funnel-event="{copy_event}"' in html:
                rendered_copy_events += 1
            else:
                issues.append(f"{lang}/{slug}: missing copy funnel event {copy_event}")
            for field in ("guardian", "request_type", "asset", "reply_email", "campaign_content", "context", "consent"):
                if f'name="{field}"' in html:
                    rendered_required_fields += 1
                else:
                    issues.append(f"{lang}/{slug}: missing form field {field}")
            rendered_guardian_options += sum(1 for guardian in guardians if f'value="{guardian}"' in html)
            rendered_intake_options += sum(1 for intake in intake_types if f'value="{intake}"' in html)

    expected_rendered_forms = len(langs) * 2
    expected_required_fields = expected_rendered_forms * 7
    expected_guardian_options = expected_rendered_forms * len(guardians)
    expected_intake_options = expected_rendered_forms * len(intake_types)
    if rendered_forms != expected_rendered_forms:
        issues.append(f"expected {expected_rendered_forms} rendered lead forms, got {rendered_forms}")
    if rendered_required_fields != expected_required_fields:
        issues.append(f"expected {expected_required_fields} rendered lead fields, got {rendered_required_fields}")
    if rendered_guardian_options != expected_guardian_options:
        issues.append(f"expected {expected_guardian_options} guardian options, got {rendered_guardian_options}")
    if rendered_intake_options != expected_intake_options:
        issues.append(f"expected {expected_intake_options} intake options, got {rendered_intake_options}")
    expected_events = set(EXPECTED_FORM_SOURCES.values()) | EXPECTED_COPY_EVENTS
    missing_catalog_events = sorted(expected_events - funnel_events)
    if missing_catalog_events:
        issues.append("funnel-events.json missing lead form events: " + ", ".join(missing_catalog_events))

    return {
        "configuredForms": configured_forms,
        "renderedForms": rendered_forms,
        "renderedSendEvents": rendered_send_events,
        "renderedCopyEvents": rendered_copy_events,
        "renderedRequiredFields": rendered_required_fields,
        "renderedGuardianOptions": rendered_guardian_options,
        "renderedIntakeOptions": rendered_intake_options,
        "trackerFields": len(tracker_fields),
        "intakeTypes": len(intake_types),
        "sourceOptions": len(source_options),
        "issues": issues,
    }


def main() -> int:
    result = audit()
    print(f"promotion_lead_form_configured_forms={result['configuredForms']}")
    print(f"promotion_lead_form_rendered_forms={result['renderedForms']}")
    print(f"promotion_lead_form_rendered_send_events={result['renderedSendEvents']}")
    print(f"promotion_lead_form_rendered_copy_events={result['renderedCopyEvents']}")
    print(f"promotion_lead_form_rendered_required_fields={result['renderedRequiredFields']}")
    print(f"promotion_lead_form_rendered_guardian_options={result['renderedGuardianOptions']}")
    print(f"promotion_lead_form_rendered_intake_options={result['renderedIntakeOptions']}")
    print(f"promotion_lead_form_tracker_fields={result['trackerFields']}")
    print(f"promotion_lead_form_intake_types={result['intakeTypes']}")
    print(f"promotion_lead_form_source_options={result['sourceOptions']}")
    print(f"promotion_lead_form_issues={len(result['issues'])}")
    for issue in result["issues"]:
        print(issue)
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
