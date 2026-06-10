#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
CONTACT_EMAIL = "contact@lovetypes.tw"
LOCALE_PREFIXES = {"zh": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
CONTACT_SOURCE_ROUTES = {
    "luna-yoga-music": "luna-supply-request",
    "about": "site-repair-report",
    "privacy": "site-repair-report",
    "terms": "site-repair-report",
}


@dataclass(frozen=True)
class LocaleExpectation:
    lang: str
    path: str
    html_lang: str
    subjects: set[str]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def localized_path(lang: str, route: str) -> str:
    prefix = LOCALE_PREFIXES[lang]
    parts = [part for part in (prefix, route.strip("/")) if part]
    return "/" + "/".join(parts) + "/"


def localized_contact_anchor(lang: str, target: str) -> str:
    return localized_path(lang, "contact") + f"#{target}"


def expectations() -> list[LocaleExpectation]:
    generator = load_module("lovetypes_generator_contact_smoke", ROOT / "tools" / "generate_multilingual_site.py")
    return [
        LocaleExpectation(
            lang=lang,
            path=f"/{prefix}/contact/" if prefix else "/contact/",
            html_lang=generator.LANGS[lang]["code"],
            subjects={
                generator.CONTACT_REQUESTS[lang]["subject"],
                generator.CONTACT_REPAIR_REPORTS[lang]["subject"],
            },
        )
        for lang, prefix in LOCALE_PREFIXES.items()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public contact repair and mailto routes.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    deploy_smoke = load_module("public_deploy_smoke_contact_import", ROOT / "tools" / "public_deploy_smoke.py")
    generator = load_module("lovetypes_generator_contact_expectations", ROOT / "tools" / "generate_multilingual_site.py")
    issues: list[str] = []
    pages_checked = 0
    mailto_links_checked = 0
    mailto_bodies_checked = 0
    template_blocks_checked = 0
    template_buttons_checked = 0
    contact_subjects_checked = 0
    anchor_targets_checked = 0
    protected_email_links_checked = 0
    source_routes_checked = 0
    saved_result_sections_checked = 0
    contact_quiz_data_refs_checked = 0

    for item in expectations():
        response = deploy_smoke.request_url(urljoin(base_url + "/", item.path.lstrip("/")))
        pages_checked += 1
        if response.status != 200:
            issues.append(f"{item.path}: expected status 200, got {response.status}")
            continue
        assets = deploy_smoke.extract_head_assets(response.text)
        if assets.html_lang != item.html_lang:
            issues.append(f"{item.path}: expected html lang {item.html_lang}, got {assets.html_lang}")
        for target in ("luna-supply-request", "site-repair-report"):
            anchor_targets_checked += 1
            if target not in assets.ids:
                issues.append(f"{item.path}: missing #{target}")
        if "data-contact-saved" not in response.text:
            issues.append(f"{item.path}: missing saved result contact handoff section")
        else:
            saved_result_sections_checked += 1
        expected_quiz_data = generator.QUIZ_DATA_ASSETS[item.lang]
        if expected_quiz_data not in response.text:
            issues.append(f"{item.path}: missing localized quiz data for saved result handoff")
        else:
            contact_quiz_data_refs_checked += 1
        mailto_subjects: set[str] = set()
        mailto_bodies_by_subject: dict[str, list[str]] = {}
        protected_email_links = 0
        for anchor in assets.anchors:
            href = anchor.get("href", "")
            parsed = urlparse(href)
            if href.startswith("/cdn-cgi/l/email-protection"):
                protected_email_links += 1
                protected_email_links_checked += 1
                continue
            if parsed.scheme != "mailto":
                continue
            mailto_links_checked += 1
            if parsed.path.lower() != CONTACT_EMAIL:
                issues.append(f"{item.path}: mailto should use {CONTACT_EMAIL}, got {href}")
            query = parse_qs(parsed.query)
            subjects = query.get("subject", [])
            bodies = query.get("body", [])
            mailto_subjects.update(subjects)
            for subject in subjects:
                mailto_bodies_by_subject.setdefault(subject, []).extend(bodies)
        email_protection_active = protected_email_links >= 3 and "__cf_email__" in response.text
        missing_subjects = sorted(item.subjects.difference(mailto_subjects))
        if missing_subjects and not email_protection_active:
            issues.append(f"{item.path}: missing mailto subjects {', '.join(missing_subjects)}")
        else:
            contact_subjects_checked += len(item.subjects)
        if not email_protection_active:
            for subject in sorted(item.subjects):
                bodies = mailto_bodies_by_subject.get(subject, [])
                if any(body.strip() for body in bodies):
                    mailto_bodies_checked += 1
                else:
                    issues.append(f"{item.path}: mailto subject {subject} should include a prefilled body")
        visible_text = response.text
        for subject in item.subjects:
            if subject not in visible_text:
                issues.append(f"{item.path}: missing visible suggested subject {subject}")
        template_blocks = response.text.count("contact-request-template")
        template_buttons = response.text.count(" data-copy-contact-template ")
        if template_blocks < 2:
            issues.append(f"{item.path}: expected two copyable contact templates, got {template_blocks}")
        else:
            template_blocks_checked += 2
        if template_buttons != 2:
            issues.append(f"{item.path}: expected two copy contact template buttons, got {template_buttons}")
        else:
            template_buttons_checked += 2
        expected_bodies = {
            generator.CONTACT_REQUESTS[item.lang]["body"],
            generator.CONTACT_REPAIR_REPORTS[item.lang]["body"],
        }
        for expected_body in expected_bodies:
            if expected_body.strip() not in visible_text:
                issues.append(f"{item.path}: missing visible copyable email template")
        if not mailto_subjects and not email_protection_active:
            issues.append(f"{item.path}: expected mailto links or Cloudflare email protection links")

        for route, target in CONTACT_SOURCE_ROUTES.items():
            source_path = localized_path(item.lang, route)
            expected_href = localized_contact_anchor(item.lang, target)
            source_response = deploy_smoke.request_url(urljoin(base_url + "/", source_path.lstrip("/")))
            source_routes_checked += 1
            if source_response.status != 200:
                issues.append(f"{source_path}: expected status 200, got {source_response.status}")
                continue
            source_assets = deploy_smoke.extract_head_assets(source_response.text)
            hrefs = {anchor.get("href", "") for anchor in source_assets.anchors}
            if expected_href not in hrefs:
                issues.append(f"{source_path}: missing contact route {expected_href}")

    print(f"public_contact_pages_checked={pages_checked}")
    print(f"public_contact_anchor_targets_checked={anchor_targets_checked}")
    print(f"public_contact_mailto_links_checked={mailto_links_checked}")
    print(f"public_contact_mailto_bodies_checked={mailto_bodies_checked}")
    print(f"public_contact_template_blocks_checked={template_blocks_checked}")
    print(f"public_contact_template_buttons_checked={template_buttons_checked}")
    print(f"public_contact_protected_email_links_checked={protected_email_links_checked}")
    print(f"public_contact_subjects_checked={contact_subjects_checked}")
    print(f"public_contact_source_routes_checked={source_routes_checked}")
    print(f"public_contact_saved_result_sections_checked={saved_result_sections_checked}")
    print(f"public_contact_quiz_data_refs_checked={contact_quiz_data_refs_checked}")
    print(f"public_contact_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
