#!/usr/bin/env python3
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_SCRIPT = ROOT / "tools" / "generate_multilingual_site.py"
AMAZON_TAG = "parenttechche-20"
OTHER_LANGS = ("en", "ja", "ko", "es")


def load_generator_module():
    spec = importlib.util.spec_from_file_location("lovetypes_generate_multilingual_site", GENERATOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator script: {GENERATOR_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def zh_targets() -> list[Path]:
    generator = load_generator_module()
    return [
        ROOT / "resources" / "index.html",
        ROOT / "repair-plan" / "index.html",
        ROOT / generator.QUIZ_DATA_ASSETS["zh"].lstrip("/"),
        *(ROOT / "characters" / slug / "index.html" for slug in ("iris", "noah", "vivian", "claire", "dora")),
    ]


def other_targets(lang: str) -> list[Path]:
    generator = load_generator_module()
    return [
        ROOT / lang / "resources" / "index.html",
        ROOT / lang / "repair-plan" / "index.html",
        ROOT / generator.QUIZ_DATA_ASSETS[lang].lstrip("/"),
        *(ROOT / lang / "characters" / slug / "index.html" for slug in ("iris", "noah", "vivian", "claire", "dora")),
    ]


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    issues: list[str] = []
    zh_files_checked = 0
    other_files_checked = 0

    for path in zh_targets():
        text = read(path)
        zh_files_checked += 1
        if "books.com.tw" not in text:
            issues.append(f"{path.relative_to(ROOT)}: Traditional Chinese affiliate path should keep Books.com.tw")
        if "amazon.com/dp/" in text or AMAZON_TAG in text:
            issues.append(f"{path.relative_to(ROOT)}: Traditional Chinese affiliate path should not use Amazon")

    for lang in OTHER_LANGS:
        for path in other_targets(lang):
            text = read(path)
            other_files_checked += 1
            if "books.com.tw" in text:
                issues.append(f"{path.relative_to(ROOT)}: non-zh affiliate path should not use Books.com.tw")
            if "amazon.com/dp/" not in text or AMAZON_TAG not in text:
                issues.append(f"{path.relative_to(ROOT)}: non-zh affiliate path should use Amazon tag={AMAZON_TAG}")

    print(f"affiliate_locale_zh_files_checked={zh_files_checked}")
    print(f"affiliate_locale_other_files_checked={other_files_checked}")
    if issues:
        print("affiliate_locale_issues=" + str(len(issues)))
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("affiliate_locale_issues=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
