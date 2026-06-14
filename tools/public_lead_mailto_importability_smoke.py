#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
CONTACT_EMAIL = "contact@lovetypes.tw"
EVENTS = {
    "collector_supply_mailto",
    "free_keepsake_asset_request",
    "guardian_snapshot_supply_request",
    "supply_product_owned_request",
    "supply_wishlist_mailto",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def localized_path(lang: str, slug: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    slug = slug.strip("/")
    return f"{prefix}/{slug}/" if prefix else f"/{slug}/"


def decode_cloudflare_email_href(href: str) -> str:
    if not href.startswith("/cdn-cgi/l/email-protection#"):
        return href
    encoded = href.split("#", 1)[1]
    try:
        data = bytes.fromhex(encoded)
    except ValueError:
        return href
    if not data:
        return href
    key = data[0]
    return "".join(chr(byte ^ key) for byte in data[1:])


def normalized_mailto(href: str) -> str:
    decoded = unescape(decode_cloudflare_email_href(unescape(href)))
    if decoded.startswith(f"{CONTACT_EMAIL}?"):
        return f"mailto:{decoded}"
    return decoded


def body_from_href(href: str) -> str:
    parsed = urlparse(normalized_mailto(href))
    query = parse_qs(parsed.query)
    return unquote(query.get("body", [""])[0])


def recipient_from_href(href: str) -> str:
    parsed = urlparse(normalized_mailto(href))
    return parsed.path.lower()


def add_real_email(text: str, email_labels: set[str]) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        replaced = False
        for label in email_labels:
            prefix = f"{label}:"
            if stripped.startswith(prefix):
                value = stripped[len(prefix):].strip()
                if "@" not in value:
                    lines.append(f"{label}: traveler@realmail.com")
                    replaced = True
                    break
        if not replaced:
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


def public_paths(generator) -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    for lang in generator.LANGS:
        paths.append((lang, localized_path(lang, "resources")))
        paths.append((lang, localized_path(lang, "keepsakes")))
        for slug in generator.GUARDIANS:
            paths.append((lang, localized_path(lang, f"characters/{slug}")))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public structured lead mailto bodies remain importable.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    deploy_smoke = load_module("public_deploy_smoke_mailto_import", ROOT / "tools" / "public_deploy_smoke.py")
    generator = load_module("lovetypes_generator_public_mailto_import", ROOT / "tools" / "generate_multilingual_site.py")
    email_labels = {copy["email"] for copy in generator.LEAD_INTAKE_FORM.values()}

    pages_checked = 0
    rows = 0
    importable_rows = 0
    protected_rows = 0
    copy_templates = 0
    issues: list[str] = []
    covered_events: set[str] = set()

    for _lang, path in public_paths(generator):
        response = deploy_smoke.request_url(urljoin(base_url + "/", path.lstrip("/")))
        pages_checked += 1
        if response.status != 200:
            issues.append(f"{path}: expected HTTP 200, got {response.status}")
            continue
        assets = deploy_smoke.extract_head_assets(response.text)
        for anchor in assets.anchors:
            event = anchor.get("data-funnel-event", "")
            if event not in EVENTS:
                continue
            covered_events.add(event)
            rows += 1
            href = anchor.get("href", "")
            if href.startswith("/cdn-cgi/l/email-protection#"):
                protected_rows += 1
            if recipient_from_href(href) != CONTACT_EMAIL:
                issues.append(f"{path} {event}: expected {CONTACT_EMAIL} recipient")
                continue
            body = body_from_href(href)
            if "owned_asset_request" not in body:
                issues.append(f"{path} {event}: missing owned_asset_request")
            if "consent_status: explicit_reply_ok" not in body:
                issues.append(f"{path} {event}: missing explicit reply consent")
            if "Campaign content" not in body and "推廣內容" not in body and "utm_content" not in body:
                issues.append(f"{path} {event}: missing campaign content")
            ok, output = run_import_check(add_real_email(body, email_labels))
            if ok:
                importable_rows += 1
            else:
                detail = output.splitlines()[-1] if output else "unknown import failure"
                issues.append(f"{path} {event}: mailto body is not importable ({detail})")
        copy_templates += response.text.count("data-copy-contact-template")

    expected_minimum = len(generator.LANGS) * (len(generator.GUARDIANS) * 3 + len(generator.GUARDIANS))
    if rows < expected_minimum:
        issues.append(f"expected at least {expected_minimum} public lead mailto rows, got {rows}")
    missing_events = sorted(EVENTS - covered_events)
    if missing_events:
        issues.append("missing public lead mailto events: " + ", ".join(missing_events))

    print(f"public_lead_mailto_importability_pages_checked={pages_checked}")
    print(f"public_lead_mailto_importability_rows={rows}")
    print(f"public_lead_mailto_importability_importable_rows={importable_rows}")
    print(f"public_lead_mailto_importability_protected_rows={protected_rows}")
    print(f"public_lead_mailto_importability_copy_templates={copy_templates}")
    print(f"public_lead_mailto_importability_events_covered={len(covered_events)}")
    print(f"public_lead_mailto_importability_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
