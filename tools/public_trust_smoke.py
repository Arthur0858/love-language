#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
LOCALE_PREFIXES = {"zh": "", "en": "en", "ja": "ja", "ko": "ko", "es": "es"}
TRUST_SLUGS = ("about", "theory", "contact", "privacy", "terms")
POLICY_SLUGS = {"contact", "privacy", "terms"}
FORBIDDEN_COMMERCIAL_SNIPPETS = (
    "books.com.tw",
    "deferred-external-",
    "affiliate-disclosure",
    "data-affiliate",
)


@dataclass(frozen=True)
class TrustPage:
    lang: str
    path: str
    slug: str
    html_lang: str
    boundary_text: str


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


def page_path(prefix: str, slug: str) -> str:
    return f"/{prefix}/{slug}/" if prefix else f"/{slug}/"


def localized_path(lang: str, route: str = "") -> str:
    prefix = LOCALE_PREFIXES[lang]
    route = route.strip("/")
    parts = [part for part in (prefix, route) if part]
    return "/" + "/".join(parts) + ("/" if parts else "")


def expectations() -> list[TrustPage]:
    generator = load_module("lovetypes_generator_trust_smoke", ROOT / "tools" / "generate_multilingual_site.py")
    pages: list[TrustPage] = []
    for lang, prefix in LOCALE_PREFIXES.items():
        for slug in TRUST_SLUGS:
            pages.append(
                TrustPage(
                    lang=lang,
                    path=page_path(prefix, slug),
                    slug=slug,
                    html_lang=generator.LANGS[lang]["code"],
                    boundary_text=generator.LANGS[lang]["boundary_text"],
                )
            )
    return pages


def count_substring(source: str, needle: str) -> int:
    return source.count(needle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public trust, policy, and safety-boundary pages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    deploy_smoke = load_module("public_deploy_smoke_trust_import", ROOT / "tools" / "public_deploy_smoke.py")
    generator = load_module("lovetypes_generator_trust_expectations", ROOT / "tools" / "generate_multilingual_site.py")

    issues: list[str] = []
    pages_checked = 0
    boundary_texts_checked = 0
    policy_compass_cards_checked = 0
    policy_detail_cards_checked = 0
    trust_action_routes_checked = 0
    trust_action_events_checked = 0
    contact_route_anchors_checked = 0
    about_trust_cards_checked = 0
    about_garden_pass_cards_checked = 0
    about_hero_actions_checked = 0
    about_hero_events_checked = 0
    theory_domain_cards_checked = 0
    theory_domain_events_checked = 0
    theory_guardian_cards_checked = 0
    theory_faq_cards_checked = 0
    theory_hero_actions_checked = 0
    theory_hero_events_checked = 0
    about_theory_distinction_checks = 0
    noncommercial_pages_checked = 0

    for page in expectations():
        response = deploy_smoke.request_url(urljoin(base_url + "/", page.path.lstrip("/")))
        pages_checked += 1
        if response.status != 200:
            issues.append(f"{page.path}: expected status 200, got {response.status}")
            continue
        assets = deploy_smoke.extract_head_assets(response.text)
        expected_canonical = f"https://lovetypes.tw{page.path}"
        if assets.canonical != expected_canonical:
            issues.append(f"{page.path}: canonical should be {expected_canonical!r}, got {assets.canonical!r}")
        if assets.html_lang != page.html_lang:
            issues.append(f"{page.path}: html lang should be {page.html_lang!r}, got {assets.html_lang!r}")
        robots_tokens = {token.strip().lower() for token in assets.robots.split(",") if token.strip()}
        if "noindex" in robots_tokens or {"index", "follow"}.difference(robots_tokens):
            issues.append(f"{page.path}: robots should include index/follow and not noindex, got {assets.robots!r}")

        if page.boundary_text not in response.text:
            issues.append(f"{page.path}: missing localized safety boundary text")
        else:
            boundary_texts_checked += 1

        for snippet in FORBIDDEN_COMMERCIAL_SNIPPETS:
            if snippet in response.text:
                issues.append(f"{page.path}: trust page should not include commercial snippet {snippet!r}")
        noncommercial_pages_checked += 1

        if page.slug in POLICY_SLUGS:
            compass_count = count_substring(response.text, 'class="policy-compass-card"')
            detail_count = count_substring(response.text, 'class="policy-detail-card"')
            policy_compass_cards_checked += compass_count
            policy_detail_cards_checked += detail_count
            if compass_count != 3:
                issues.append(f"{page.path}: expected 3 policy compass cards, got {compass_count}")
            if detail_count != 3:
                issues.append(f"{page.path}: expected 3 policy detail cards, got {detail_count}")
            if page.slug in {"privacy", "terms"} and generator.UPDATED not in response.text:
                issues.append(f"{page.path}: missing updated date")
        elif page.slug == "about":
            if 'data-trust-hero-actions="about"' not in response.text:
                issues.append(f"{page.path}: missing about-specific trust hero actions")
            else:
                for key in ("quiz", "guardians", "theory"):
                    if f'data-trust-hero-link="{key}"' not in response.text:
                        issues.append(f"{page.path}: about hero missing {key} action")
                    else:
                        about_hero_actions_checked += 1
                    event = f'trust_hero_about_{key}'
                    if f'data-funnel-event="{event}"' not in response.text:
                        issues.append(f"{page.path}: about hero missing event {event}")
                    else:
                        about_hero_events_checked += 1
            garden_pass_count = count_substring(response.text, 'class="garden-pass-card"')
            about_garden_pass_cards_checked += garden_pass_count
            if garden_pass_count != 3:
                issues.append(f"{page.path}: expected 3 about garden pass cards, got {garden_pass_count}")
            card_count = count_substring(response.text, 'class="about-trust-card"')
            about_trust_cards_checked += card_count
            if card_count != 4:
                issues.append(f"{page.path}: expected 4 about trust cards, got {card_count}")
            if 'data-about-garden-pass' not in response.text:
                issues.append(f"{page.path}: missing garden pass section")
            if 'data-theory-domain-compass' in response.text or 'class="faq-section"' in response.text:
                issues.append(f"{page.path}: about page should not include theory-only compass or FAQ sections")
            else:
                about_theory_distinction_checks += 1
        elif page.slug == "theory":
            if 'data-trust-hero-actions="about"' in response.text or 'data-about-garden-pass' in response.text:
                issues.append(f"{page.path}: theory page should not include about-only hero or garden pass")
            else:
                about_theory_distinction_checks += 1
            for expected in (f'href="{localized_path(page.lang)}#quiz-section"', f'href="{localized_path(page.lang, "characters")}"'):
                if expected not in response.text:
                    issues.append(f"{page.path}: theory hero missing action {expected}")
                else:
                    theory_hero_actions_checked += 1
            for event in ("trust_hero_theory_quiz", "trust_hero_theory_guardians"):
                if f'data-funnel-event="{event}"' not in response.text:
                    issues.append(f"{page.path}: theory hero missing event {event}")
                else:
                    theory_hero_events_checked += 1
            domain_count = count_substring(response.text, 'class="theory-domain-card"')
            theory_domain_cards_checked += domain_count
            if domain_count != 5:
                issues.append(f"{page.path}: expected 5 theory domain cards, got {domain_count}")
            domain_event_count = count_substring(response.text, 'data-funnel-event="theory_domain_guardian"')
            theory_domain_events_checked += domain_event_count
            if domain_event_count != 5:
                issues.append(f"{page.path}: expected 5 theory domain events, got {domain_event_count}")
            if 'data-funnel-event="theory_domain_section_guardians"' not in response.text:
                issues.append(f"{page.path}: theory domain section missing guardians event")
            guardian_count = count_substring(response.text, 'class="guardian-card"')
            theory_guardian_cards_checked += guardian_count
            if guardian_count != 5:
                issues.append(f"{page.path}: expected 5 theory guardian cards, got {guardian_count}")
            faq_count = count_substring(response.text, "<article><h3>")
            theory_faq_cards_checked += faq_count
            if faq_count != 4:
                issues.append(f"{page.path}: expected 4 theory FAQ cards, got {faq_count}")

        if page.slug in {"about", "theory"}:
            action_count = count_substring(response.text, 'class="trust-action-card"')
            if 'id="trust-action-routes"' not in response.text:
                issues.append(f"{page.path}: missing trust action routes")
            elif action_count != 4:
                issues.append(f"{page.path}: expected 4 trust action cards, got {action_count}")
            else:
                trust_action_routes_checked += action_count
            action_event_count = count_substring(response.text, f'data-funnel-event="trust_action_{page.slug}_')
            trust_action_events_checked += action_event_count
            if action_event_count != 4:
                issues.append(f"{page.path}: expected 4 trust action events, got {action_event_count}")
        if page.slug == "contact":
            for target in ("luna-supply-request", "site-repair-report"):
                contact_route_anchors_checked += 1
                if target not in assets.ids:
                    issues.append(f"{page.path}: missing contact anchor #{target}")
            if "contact@lovetypes.tw" not in response.text and "__cf_email__" not in response.text:
                issues.append(f"{page.path}: missing contact email or Cloudflare protected email")

    print(f"public_trust_pages_checked={pages_checked}")
    print(f"public_trust_boundary_texts_checked={boundary_texts_checked}")
    print(f"public_trust_policy_compass_cards_checked={policy_compass_cards_checked}")
    print(f"public_trust_policy_detail_cards_checked={policy_detail_cards_checked}")
    print(f"public_trust_about_garden_pass_cards_checked={about_garden_pass_cards_checked}")
    print(f"public_trust_about_hero_actions_checked={about_hero_actions_checked}")
    print(f"public_trust_about_hero_events_checked={about_hero_events_checked}")
    print(f"public_trust_about_cards_checked={about_trust_cards_checked}")
    print(f"public_trust_theory_domain_cards_checked={theory_domain_cards_checked}")
    print(f"public_trust_theory_domain_events_checked={theory_domain_events_checked}")
    print(f"public_trust_theory_guardian_cards_checked={theory_guardian_cards_checked}")
    print(f"public_trust_theory_faq_cards_checked={theory_faq_cards_checked}")
    print(f"public_trust_theory_hero_actions_checked={theory_hero_actions_checked}")
    print(f"public_trust_theory_hero_events_checked={theory_hero_events_checked}")
    print(f"public_trust_about_theory_distinction_checks={about_theory_distinction_checks}")
    print(f"public_trust_action_routes_checked={trust_action_routes_checked}")
    print(f"public_trust_action_events_checked={trust_action_events_checked}")
    print(f"public_trust_contact_route_anchors_checked={contact_route_anchors_checked}")
    print(f"public_trust_noncommercial_pages_checked={noncommercial_pages_checked}")
    print(f"public_trust_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
