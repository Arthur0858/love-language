#!/usr/bin/env python3
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_SCRIPT = ROOT / "tools" / "generate_multilingual_site.py"
AMAZON_TAG = "parenttechche-20"


def load_generator_module():
    spec = importlib.util.spec_from_file_location("lovetypes_generate_multilingual_site", GENERATOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator script: {GENERATOR_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def route_path(route: str) -> Path:
    return ROOT / "index.html" if not route else ROOT / route / "index.html"


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    generator = load_generator_module()
    issues: list[str] = []
    commerce_files_checked = 0
    isolated_files_checked = 0

    resources_path = ROOT / "resources" / "index.html"
    resources_text = read(resources_path)
    commerce_files_checked += 1
    if "books.com.tw" not in resources_text:
        issues.append("resources/index.html: Traditional Chinese affiliate page should keep Books.com.tw")
    if "amazon.com/dp/" in resources_text or AMAZON_TAG in resources_text:
        issues.append("resources/index.html: Traditional Chinese affiliate page should not use Amazon")

    isolated_paths = [
        *(route_path(route) for route in generator.site_index_paths("zh")),
        ROOT / generator.QUIZ_DATA_ASSETS["zh"].lstrip("/"),
    ]
    for path in isolated_paths:
        text = read(path)
        isolated_files_checked += 1
        if "books.com.tw" in text or "amazon.com/dp/" in text or AMAZON_TAG in text:
            issues.append(f"{path.relative_to(ROOT)}: affiliate link leaked outside resources/index.html")

    print(f"affiliate_locale_commerce_files_checked={commerce_files_checked}")
    print(f"affiliate_locale_isolated_files_checked={isolated_files_checked}")
    if issues:
        print("affiliate_locale_issues=" + str(len(issues)))
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("affiliate_locale_issues=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
