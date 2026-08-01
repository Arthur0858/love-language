#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIN_TEXT_CHARS = 220
SHINGLE_SIZE = 8
MAX_JACCARD_SIMILARITY = 0.30
MAX_CONTAINMENT_SIMILARITY = 0.45
GENERAL_MAX_JACCARD_SIMILARITY = 0.45
GENERAL_MAX_CONTAINMENT_SIMILARITY = 0.65
GUARDIAN_CJK_SHINGLE_SIZE = 6
GUARDIAN_MAX_JACCARD_SIMILARITY = 0.30
GUARDIAN_MAX_CONTAINMENT_SIMILARITY = 0.45


class MainTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.main_text_parts: list[str] = []
        self.robots = ""
        self.html_lang = ""
        self._in_title = False
        self._main_depth = 0
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and data.get("name") == "robots":
            self.robots = data.get("content", "")
        elif tag == "main":
            self._main_depth += 1
        elif self._main_depth and tag in {"script", "style", "nav"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif self._main_depth and tag in {"script", "style", "nav"} and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "main" and self._main_depth:
            self._main_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._main_depth and not self._skip_depth and data.strip():
            self.main_text_parts.append(data)

    @property
    def title(self) -> str:
        return normalize_text(" ".join(self.title_parts))

    @property
    def main_text(self) -> str:
        return normalize_text(" ".join(self.main_text_parts))

    @property
    def noindex(self) -> bool:
        return "noindex" in self.robots.lower()


@dataclass(frozen=True)
class PageText:
    path: Path
    title: str
    html_lang: str
    text: str
    shingles: frozenset[tuple[str, ...]]


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def tokenize(value: str) -> list[str]:
    return re.findall(r"[\w\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+", value.lower())


def make_shingles(value: str) -> frozenset[tuple[str, ...]]:
    tokens = tokenize(value)
    if len(tokens) < SHINGLE_SIZE:
        return frozenset((token,) for token in tokens)
    return frozenset(tuple(tokens[index : index + SHINGLE_SIZE]) for index in range(len(tokens) - SHINGLE_SIZE + 1))


def html_pages() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "node_modules" not in path.parts and "output" not in path.parts
    )


def parse_page(path: Path) -> PageText | None:
    parser = MainTextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    text = parser.main_text
    if parser.noindex or len(text) < MIN_TEXT_CHARS:
        return None
    return PageText(
        path=path,
        title=parser.title,
        html_lang=parser.html_lang,
        text=text,
        shingles=make_shingles(text),
    )


def same_locale(left: PageText, right: PageText) -> bool:
    return bool(left.html_lang and right.html_lang and left.html_lang == right.html_lang)


def compare_pages(left: PageText, right: PageText) -> tuple[float, float]:
    if not left.shingles or not right.shingles:
        return 0.0, 0.0
    overlap = len(left.shingles & right.shingles)
    union = len(left.shingles | right.shingles)
    smaller = min(len(left.shingles), len(right.shingles))
    jaccard = overlap / union if union else 0.0
    containment = overlap / smaller if smaller else 0.0
    return jaccard, containment


def is_formal_guide(page: PageText) -> bool:
    relative = page.path.relative_to(ROOT)
    return len(relative.parts) == 3 and relative.parts[0] == "guides" and relative.parts[2] == "index.html"


def is_zh_guardian(page: PageText) -> bool:
    relative = page.path.relative_to(ROOT)
    return (
        page.html_lang == "zh-TW"
        and len(relative.parts) == 3
        and relative.parts[0] == "characters"
        and relative.parts[2] == "index.html"
    )


def cjk_character_shingles(value: str) -> frozenset[str]:
    characters = "".join(re.findall(r"[\u3400-\u9fff]", value))
    if len(characters) < GUARDIAN_CJK_SHINGLE_SIZE:
        return frozenset({characters}) if characters else frozenset()
    return frozenset(
        characters[index : index + GUARDIAN_CJK_SHINGLE_SIZE]
        for index in range(len(characters) - GUARDIAN_CJK_SHINGLE_SIZE + 1)
    )


def main() -> int:
    pages = [page for path in html_pages() if (page := parse_page(path))]
    issues: list[str] = []
    near_duplicate_pairs = 0
    max_guide_jaccard = 0.0
    max_guide_containment = 0.0
    max_guardian_jaccard = 0.0
    max_guardian_containment = 0.0

    fingerprints: dict[str, list[PageText]] = {}
    for page in pages:
        fingerprints.setdefault(page.text.lower(), []).append(page)

    for matches in fingerprints.values():
        if len(matches) > 1:
            joined = ", ".join(str(page.path.relative_to(ROOT)) for page in matches[:8])
            issues.append(f"exact duplicate main content across indexable pages: {joined}")

    for index, left in enumerate(pages):
        for right in pages[index + 1 :]:
            if not same_locale(left, right):
                continue
            jaccard, containment = compare_pages(left, right)
            guide_pair = is_formal_guide(left) and is_formal_guide(right)
            if guide_pair:
                max_guide_jaccard = max(max_guide_jaccard, jaccard)
                max_guide_containment = max(max_guide_containment, containment)
            max_jaccard = MAX_JACCARD_SIMILARITY if guide_pair else GENERAL_MAX_JACCARD_SIMILARITY
            max_containment = MAX_CONTAINMENT_SIMILARITY if guide_pair else GENERAL_MAX_CONTAINMENT_SIMILARITY
            if jaccard >= max_jaccard or containment >= max_containment:
                near_duplicate_pairs += 1
                issues.append(
                    "near duplicate main content "
                    f"jaccard={jaccard:.3f} containment={containment:.3f}: "
                    f"{left.path.relative_to(ROOT)} ({left.title}) <-> "
                    f"{right.path.relative_to(ROOT)} ({right.title})"
                )

    guardians = [page for page in pages if is_zh_guardian(page)]
    for index, left in enumerate(guardians):
        left_shingles = cjk_character_shingles(left.text)
        for right in guardians[index + 1 :]:
            right_shingles = cjk_character_shingles(right.text)
            overlap = len(left_shingles & right_shingles)
            union = len(left_shingles | right_shingles)
            smaller = min(len(left_shingles), len(right_shingles))
            jaccard = overlap / union if union else 0.0
            containment = overlap / smaller if smaller else 0.0
            max_guardian_jaccard = max(max_guardian_jaccard, jaccard)
            max_guardian_containment = max(max_guardian_containment, containment)
            if (
                jaccard >= GUARDIAN_MAX_JACCARD_SIMILARITY
                or containment >= GUARDIAN_MAX_CONTAINMENT_SIMILARITY
            ):
                near_duplicate_pairs += 1
                issues.append(
                    "near duplicate guardian character content "
                    f"cjk_jaccard={jaccard:.3f} cjk_containment={containment:.3f}: "
                    f"{left.path.relative_to(ROOT)} <-> {right.path.relative_to(ROOT)}"
                )

    print(f"content_pages_checked={len(pages)}")
    print(f"max_guide_jaccard={max_guide_jaccard:.3f}")
    print(f"max_guide_containment={max_guide_containment:.3f}")
    print(f"max_guardian_cjk_jaccard={max_guardian_jaccard:.3f}")
    print(f"max_guardian_cjk_containment={max_guardian_containment:.3f}")
    print(f"near_duplicate_pairs={near_duplicate_pairs}")
    print(f"content_uniqueness_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
