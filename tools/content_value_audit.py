#!/usr/bin/env python3
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE_LANG_PREFIXES = {
    "zh": "",
    "en": "en",
    "ja": "ja",
    "ko": "ko",
    "es": "es",
}
LATIN_MIN_WORDS = 850
CJK_MIN_CHARS = 1200
CORE_LATIN_MIN_WORDS = 520
CORE_CJK_MIN_CHARS = 900
CORE_ROUTES = ["", "about", "theory", "guides", "characters"]


class PageTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.text: list[str] = []
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag in {"script", "style", "nav", "footer", "header", "noscript", "svg"}:
            self.skip_depth += 1
        if tag == "meta" and attr.get("name", "").lower() == "robots" and "noindex" in attr.get("content", "").lower():
            self.noindex = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "header", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.text.append(data)


def read_visible_text(path: Path) -> tuple[str, bool]:
    parser = PageTextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return " ".join(parser.text), parser.noindex


def guide_paths() -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for lang, prefix in GUIDE_LANG_PREFIXES.items():
        base = ROOT / prefix / "guides" if prefix else ROOT / "guides"
        for path in sorted(base.glob("*/index.html")):
            if path.parent.name == "index":
                continue
            rows.append((lang, path))
    return rows


def page_path(lang: str, route: str) -> Path:
    prefix = GUIDE_LANG_PREFIXES[lang]
    parts = [part for part in (prefix, route, "index.html") if part]
    if not route:
        parts = [part for part in (prefix, "index.html") if part]
    return ROOT.joinpath(*parts)


def core_paths() -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for lang in GUIDE_LANG_PREFIXES:
        for route in CORE_ROUTES:
            path = page_path(lang, route)
            if path.exists():
                rows.append((lang, path))
    return rows


def audit() -> dict:
    issues: list[str] = []
    checked = 0
    latin_checked = 0
    cjk_checked = 0
    for lang, path in guide_paths():
        text, noindex = read_visible_text(path)
        if noindex:
            continue
        checked += 1
        rel = path.relative_to(ROOT)
        if lang in {"en", "es"}:
            latin_checked += 1
            words = re.findall(r"[A-Za-zÀ-ÿĀ-ž]+", text)
            if len(words) < LATIN_MIN_WORDS:
                issues.append(f"{rel}: latin guide too thin ({len(words)} words < {LATIN_MIN_WORDS})")
        else:
            cjk_checked += 1
            cjk_chars = re.findall(r"[一-龥ぁ-んァ-ン가-힣]", text)
            if len(cjk_chars) < CJK_MIN_CHARS:
                issues.append(f"{rel}: CJK guide too thin ({len(cjk_chars)} chars < {CJK_MIN_CHARS})")
    core_checked = 0
    core_latin_checked = 0
    core_cjk_checked = 0
    for lang, path in core_paths():
        text, noindex = read_visible_text(path)
        if noindex:
            continue
        core_checked += 1
        rel = path.relative_to(ROOT)
        if lang in {"en", "es"}:
            core_latin_checked += 1
            words = re.findall(r"[A-Za-zÀ-ÿĀ-ž]+", text)
            if len(words) < CORE_LATIN_MIN_WORDS:
                issues.append(f"{rel}: latin core page too thin ({len(words)} words < {CORE_LATIN_MIN_WORDS})")
        else:
            core_cjk_checked += 1
            cjk_chars = re.findall(r"[一-龥ぁ-んァ-ン가-힣]", text)
            if len(cjk_chars) < CORE_CJK_MIN_CHARS:
                issues.append(f"{rel}: CJK core page too thin ({len(cjk_chars)} chars < {CORE_CJK_MIN_CHARS})")
    return {
        "checked": checked,
        "latinChecked": latin_checked,
        "cjkChecked": cjk_checked,
        "coreChecked": core_checked,
        "coreLatinChecked": core_latin_checked,
        "coreCjkChecked": core_cjk_checked,
        "issues": issues,
    }


def main() -> int:
    result = audit()
    print(f"content_value_guides_checked={result['checked']}")
    print(f"content_value_latin_guides_checked={result['latinChecked']}")
    print(f"content_value_cjk_guides_checked={result['cjkChecked']}")
    print(f"content_value_core_pages_checked={result['coreChecked']}")
    print(f"content_value_core_latin_pages_checked={result['coreLatinChecked']}")
    print(f"content_value_core_cjk_pages_checked={result['coreCjkChecked']}")
    print(f"content_value_issues={len(result['issues'])}")
    for issue in result["issues"]:
        print(issue)
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
