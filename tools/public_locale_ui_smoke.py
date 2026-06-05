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
KEY_ROUTES = (
    "",
    "garden-map",
    "guides",
    "characters",
    "theory",
    "resources",
    "repair-plan",
    "keepsakes",
    "luna-yoga-music",
    "about",
    "contact",
    "privacy",
    "terms",
)


@dataclass(frozen=True)
class LocalePage:
    lang: str
    path: str
    html_lang: str
    nav_labels: tuple[str, ...]
    footer_labels: tuple[str, ...]
    language_names: tuple[str, ...]


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


def route_path(prefix: str, route: str) -> str:
    if not route:
        return f"/{prefix}/" if prefix else "/"
    return f"/{prefix}/{route}/" if prefix else f"/{route}/"


def expectations() -> list[LocalePage]:
    generator = load_module("lovetypes_generator_locale_smoke", ROOT / "tools" / "generate_multilingual_site.py")
    language_names = tuple(cfg["name"] for cfg in generator.LANGS.values())
    pages: list[LocalePage] = []
    for lang, prefix in LOCALE_PREFIXES.items():
        labels = generator.LANGS[lang]
        nav_labels = (
            labels["map"],
            labels["guides"],
            labels["guardians"],
            labels["theory"],
            labels["resources"],
            labels["about"],
        )
        footer_labels = (labels["privacy"], labels["terms"], labels["contact"])
        for route in KEY_ROUTES:
            pages.append(
                LocalePage(
                    lang=lang,
                    path=route_path(prefix, route),
                    html_lang=labels["code"],
                    nav_labels=nav_labels,
                    footer_labels=footer_labels,
                    language_names=language_names,
                )
            )
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Check localized public UI chrome on key LoveTypes pages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    deploy_smoke = load_module("public_deploy_smoke_locale_import", ROOT / "tools" / "public_deploy_smoke.py")

    issues: list[str] = []
    pages_checked = 0
    nav_labels_checked = 0
    footer_labels_checked = 0
    language_menu_labels_checked = 0
    active_language_links_checked = 0

    for page in expectations():
        response = deploy_smoke.request_url(urljoin(base_url + "/", page.path.lstrip("/")))
        pages_checked += 1
        if response.status != 200:
            issues.append(f"{page.path}: expected status 200, got {response.status}")
            continue
        assets = deploy_smoke.extract_head_assets(response.text)
        if assets.html_lang != page.html_lang:
            issues.append(f"{page.path}: html lang should be {page.html_lang!r}, got {assets.html_lang!r}")
        if 'aria-current="page"' not in response.text:
            issues.append(f"{page.path}: missing active page marker")
        if f'href="{page.path}" lang="{page.html_lang}" aria-current="page"' in response.text or (
            page.lang == "zh" and f'href="{page.path}" lang="zh-TW" aria-current="page"' in response.text
        ):
            active_language_links_checked += 1
        else:
            issues.append(f"{page.path}: missing active language switcher link for {page.html_lang}")
        for label in page.nav_labels:
            nav_labels_checked += 1
            if f">{label}</a>" not in response.text and f">{label}</span>" not in response.text:
                issues.append(f"{page.path}: missing localized nav label {label!r}")
        for label in page.footer_labels:
            footer_labels_checked += 1
            if f">{label}</a>" not in response.text:
                issues.append(f"{page.path}: missing localized footer label {label!r}")
        for name in page.language_names:
            language_menu_labels_checked += 1
            if name not in response.text:
                issues.append(f"{page.path}: language menu missing {name!r}")

    print(f"public_locale_pages_checked={pages_checked}")
    print(f"public_locale_nav_labels_checked={nav_labels_checked}")
    print(f"public_locale_footer_labels_checked={footer_labels_checked}")
    print(f"public_locale_language_menu_labels_checked={language_menu_labels_checked}")
    print(f"public_locale_active_language_links_checked={active_language_links_checked}")
    print(f"public_locale_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
