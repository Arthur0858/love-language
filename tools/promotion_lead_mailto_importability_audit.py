#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_multilingual_site.py"
OUTPUT_MD = ROOT / "docs" / "promotion" / "first-round" / "lead-mailto-importability-audit.md"
OUTPUT_JSON = ROOT / "docs" / "promotion" / "first-round" / "lead-mailto-importability-audit.json"
EVENTS = {
    "collector_supply_mailto",
    "free_keepsake_asset_request",
    "guardian_snapshot_supply_request",
    "supply_product_owned_request",
    "supply_wishlist_mailto",
}
HREF_RE = re.compile(r'<a\b(?=[^>]*data-funnel-event="(?P<event>[^"]+)")[^>]*href="(?P<href>mailto:contact@lovetypes\.tw\?[^"]+)"', re.S)


def load_generator():
    spec = importlib.util.spec_from_file_location("lovetypes_generator_for_mailto_audit", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def localized_path(lang: str, slug: str) -> Path:
    return ROOT / slug / "index.html" if lang == "zh" else ROOT / lang / slug / "index.html"


def body_from_href(href: str) -> str:
    parsed = urlparse(unescape(href))
    query = parse_qs(parsed.query)
    return unquote(query.get("body", [""])[0])


def add_real_email(text: str, email_labels: set[str]) -> str:
    lines = []
    replaced = False
    for line in text.splitlines():
        stripped = line.strip()
        for label in email_labels:
            prefix = f"{label}:"
            if stripped.startswith(prefix):
                value = stripped[len(prefix):].strip()
                if "@" not in value:
                    lines.append(f"{label}: traveler@realmail.com")
                    replaced = True
                    break
        else:
            lines.append(line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def run_import_check(text: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, "tools/promotion_lead_text_import.py", "check", "--input", str(temp_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = result.stdout.strip()
        return result.returncode == 0 and "promotion_lead_text_import_issues=0" in output, output
    finally:
        temp_path.unlink(missing_ok=True)


def audit() -> dict:
    generator = load_generator()
    email_labels = {copy["email"] for copy in generator.LEAD_INTAKE_FORM.values()}
    pages = []
    for lang in generator.LANGS:
        pages.append(localized_path(lang, "resources"))
        pages.append(localized_path(lang, "keepsakes"))
        for slug in generator.GUARDIANS:
            pages.append(localized_path(lang, f"characters/{slug}"))
    rows = []
    issues = []
    for path in pages:
        if not path.exists():
            issues.append(f"missing page {path.relative_to(ROOT)}")
            continue
        html = path.read_text(encoding="utf-8")
        for match in HREF_RE.finditer(html):
            event = match.group("event")
            if event not in EVENTS:
                continue
            body = body_from_href(match.group("href"))
            body_with_email = add_real_email(body, email_labels)
            ok, output = run_import_check(body_with_email)
            row_issues = []
            if not ok:
                row_issues.append("mailto body is not importable after real email insertion")
            for required in ("consent_status: explicit_reply_ok", "owned_asset_request"):
                if required not in body:
                    row_issues.append(f"missing {required}")
            if "Campaign content" not in body and "推廣內容" not in body and "utm_content" not in body:
                row_issues.append("missing campaign content field")
            issues.extend(f"{path.relative_to(ROOT)} {event}: {issue}" for issue in row_issues)
            rows.append({
                "path": str(path.relative_to(ROOT)),
                "event": event,
                "importable": 0 if row_issues else 1,
                "issues": len(row_issues),
                "detail": output.splitlines()[-1] if row_issues and output else "",
            })
    expected_minimum = len(generator.LANGS) * (len(generator.GUARDIANS) * 3 + len(generator.GUARDIANS))
    metrics = {
        "pagesChecked": len(pages),
        "mailtoRows": len(rows),
        "importableRows": sum(int(row["importable"]) for row in rows),
        "eventsCovered": len({row["event"] for row in rows}),
        "expectedMinimumRows": expected_minimum,
    }
    if metrics["mailtoRows"] < expected_minimum:
        issues.append(f"expected at least {expected_minimum} lead mailto rows, got {metrics['mailtoRows']}")
    if not EVENTS.issubset({row["event"] for row in rows}):
        missing = sorted(EVENTS - {row["event"] for row in rows})
        issues.append("missing lead mailto events: " + ", ".join(missing))
    return {
        "generatedAt": generator.TODAY if hasattr(generator, "TODAY") else "",
        "metrics": metrics,
        "rows": rows,
        "issues": issues,
    }


def render_md(report: dict) -> str:
    metrics = report["metrics"]
    lines = [
        "# LoveTypes Lead Mailto Importability Audit",
        "",
        f"- pages checked：{metrics['pagesChecked']}",
        f"- mailto rows：{metrics['mailtoRows']}",
        f"- importable rows：{metrics['importableRows']}",
        f"- events covered：{metrics['eventsCovered']}",
        f"- issues：{len(report['issues'])}",
        "",
        "## Rule",
        "",
        "- Legacy lead mailto links must produce structured request bodies.",
        "- After the traveler fills a real reply email, the body must pass lead text import check.",
        "- Campaign content and explicit reply consent must remain visible in the message body.",
        "",
    ]
    if report["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in report["issues"][:100])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict) -> None:
    public = {
        "generatedAt": report["generatedAt"],
        "metrics": report["metrics"],
        "rows": [
            {key: row[key] for key in ("path", "event", "importable", "issues")}
            for row in report["rows"]
        ],
        "issues": report["issues"],
    }
    OUTPUT_MD.write_text(render_md(report), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(public, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit structured lead mailto links for importability.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = audit()
    if not args.check:
        write_outputs(report)
        print(f"promotion_lead_mailto_importability={OUTPUT_MD.relative_to(ROOT)}")
        print(f"promotion_lead_mailto_importability_json={OUTPUT_JSON.relative_to(ROOT)}")
    metrics = report["metrics"]
    print(f"promotion_lead_mailto_importability_pages_checked={metrics['pagesChecked']}")
    print(f"promotion_lead_mailto_importability_rows={metrics['mailtoRows']}")
    print(f"promotion_lead_mailto_importability_importable_rows={metrics['importableRows']}")
    print(f"promotion_lead_mailto_importability_events_covered={metrics['eventsCovered']}")
    print(f"promotion_lead_mailto_importability_issues={len(report['issues'])}")
    for issue in report["issues"][:100]:
        print(issue)
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
