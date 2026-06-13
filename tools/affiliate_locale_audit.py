#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMAZON_TAG = "parenttechche-20"
ZH_TARGETS = [
    ROOT / "resources" / "index.html",
    ROOT / "repair-plan" / "index.html",
    ROOT / "quiz-data-zh-20260613-localized-affiliate.js",
    *(ROOT / "characters" / slug / "index.html" for slug in ("iris", "noah", "vivian", "claire", "dora")),
]
OTHER_LANGS = ("en", "ja", "ko", "es")
OTHER_TARGET_NAMES = [
    "resources/index.html",
    "repair-plan/index.html",
    "quiz-data-{lang}-20260613-localized-affiliate.js",
    "characters/iris/index.html",
    "characters/noah/index.html",
    "characters/vivian/index.html",
    "characters/claire/index.html",
    "characters/dora/index.html",
]


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    issues: list[str] = []
    zh_files_checked = 0
    other_files_checked = 0

    for path in ZH_TARGETS:
        text = read(path)
        zh_files_checked += 1
        if "books.com.tw" not in text:
            issues.append(f"{path.relative_to(ROOT)}: Traditional Chinese affiliate path should keep Books.com.tw")
        if "amazon.com/dp/" in text or AMAZON_TAG in text:
            issues.append(f"{path.relative_to(ROOT)}: Traditional Chinese affiliate path should not use Amazon")

    for lang in OTHER_LANGS:
        for name in OTHER_TARGET_NAMES:
            path = ROOT / (name.format(lang=lang) if name.startswith("quiz-data-") else f"{lang}/{name}")
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
