#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".github",
    ".well-known",
    "docs",
    "node_modules",
    "output",
    "tools",
}
IDREF_ATTRS = {
    "aria-activedescendant",
    "aria-controls",
    "aria-describedby",
    "aria-details",
    "aria-errormessage",
    "aria-labelledby",
    "for",
}
VALID_ARIA_CURRENT = {"page", "step", "location", "date", "time", "true", "false"}
WHITESPACE_RE = re.compile(r"\s+")


def normalize(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value).strip()


def class_tokens(attrs: dict[str, str]) -> set[str]:
    return set(attrs.get("class", "").split())


def has_ancestor(stack: list[tuple[str, dict[str, str], list[str]]], tag: str) -> bool:
    return any(item_tag == tag for item_tag, _attrs, _text in stack)


def html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel_parts = path.relative_to(ROOT).parts
        if rel_parts and rel_parts[0] in SKIP_DIRS:
            continue
        files.append(path)
    return sorted(files)


class AccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[dict[str, str]] = []
        self.buttons: list[dict[str, object]] = []
        self.images: list[dict[str, str]] = []
        self.controls: list[dict[str, str]] = []
        self.labels_for: set[str] = set()
        self.navs: list[dict[str, str]] = []
        self.mains: list[dict[str, str]] = []
        self.summaries: list[dict[str, object]] = []
        self.iframes: list[dict[str, str]] = []
        self.idrefs: list[tuple[str, str, str]] = []
        self.aria_current: list[tuple[str, str]] = []
        self.stack: list[tuple[str, dict[str, str], list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        self.stack.append((tag, data, []))

        if "id" in data:
            self.ids.append(data["id"])
        for attr in IDREF_ATTRS:
            if attr not in data:
                continue
            for ref in data[attr].split():
                if ref.startswith("#"):
                    ref = ref[1:]
                self.idrefs.append((tag, attr, ref))
        if "aria-current" in data:
            self.aria_current.append((tag, data["aria-current"]))

        if tag == "a":
            self.links.append(data)
        elif tag == "button":
            self.buttons.append({"attrs": data, "text": []})
        elif tag == "img":
            self.images.append(data)
            if has_ancestor(self.stack[:-1], "a") and data.get("alt"):
                self.stack[-1][2].append(data["alt"])
        elif tag in {"input", "textarea", "select"}:
            self.controls.append(data)
        elif tag == "label" and data.get("for"):
            self.labels_for.add(data["for"])
        elif tag == "nav":
            self.navs.append(data)
        elif tag == "main":
            self.mains.append(data)
        elif tag == "summary":
            self.summaries.append({"attrs": data, "text": []})
        elif tag == "iframe":
            self.iframes.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            return
        popped_tag, _attrs, text_parts = self.stack.pop()
        text = "".join(text_parts)
        if popped_tag == "a" and self.links:
            self.links[-1]["_text"] = normalize(text)
        elif popped_tag == "button" and self.buttons:
            self.buttons[-1]["text"] = [normalize(text)]
        elif popped_tag == "summary" and self.summaries:
            self.summaries[-1]["text"] = [normalize(text)]
        if self.stack and text:
            self.stack[-1][2].append(text)

    def handle_data(self, data: str) -> None:
        if self.stack:
            self.stack[-1][2].append(data)


def accessible_name(attrs: dict[str, str], text: str = "") -> str:
    return normalize(
        attrs.get("aria-label", "")
        or attrs.get("aria-labelledby", "")
        or attrs.get("title", "")
        or attrs.get("alt", "")
        or text
    )


def audit_file(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    parser = AccessibilityParser()
    parser.feed(path.read_text(encoding="utf-8"))
    issues: list[str] = []
    ids = set(parser.ids)

    duplicate_ids = [item for item, count in Counter(parser.ids).items() if count > 1]
    for item in duplicate_ids:
        issues.append(f"{rel}: duplicate id #{item}")

    if not any(main.get("id") == "main" for main in parser.mains):
        issues.append(f"{rel}: missing main id for skip link")

    for nav in parser.navs:
        if not accessible_name(nav):
            issues.append(f"{rel}: nav missing accessible label")

    for link in parser.links:
        href = link.get("href", "")
        if not href:
            issues.append(f"{rel}: anchor missing href")
        if not accessible_name(link, link.get("_text", "")):
            issues.append(f"{rel}: link {href or '(no href)'} missing accessible name")

    for button in parser.buttons:
        attrs = button["attrs"]
        text = " ".join(button["text"]) if isinstance(button["text"], list) else ""
        if isinstance(attrs, dict) and not accessible_name(attrs, text):
            issues.append(f"{rel}: button missing accessible name")

    for summary in parser.summaries:
        attrs = summary["attrs"]
        text = " ".join(summary["text"]) if isinstance(summary["text"], list) else ""
        if isinstance(attrs, dict) and not accessible_name(attrs, text):
            issues.append(f"{rel}: details summary missing accessible name")

    for image in parser.images:
        if "alt" not in image:
            issues.append(f"{rel}: image {image.get('src', '(no src)')} missing alt")
        if image.get("alt", "") and not normalize(image["alt"]):
            issues.append(f"{rel}: image {image.get('src', '(no src)')} has blank non-decorative alt")
        if image.get("src") and image.get("loading") == "lazy":
            if "width" not in image or "height" not in image:
                issues.append(f"{rel}: lazy image {image.get('src')} missing width or height")

    for control in parser.controls:
        control_id = control.get("id", "")
        control_type = control.get("type", "")
        if control_type == "hidden":
            continue
        if control_id and control_id in parser.labels_for:
            continue
        if accessible_name(control):
            continue
        issues.append(f"{rel}: {control.get('name', control.get('data-field', 'control'))} missing label")

    for iframe in parser.iframes:
        if not accessible_name(iframe):
            issues.append(f"{rel}: iframe {iframe.get('src', '(no src)')} missing title")

    for tag, attr, ref in parser.idrefs:
        if not ref:
            issues.append(f"{rel}: {tag} {attr} has empty reference")
        elif ref not in ids:
            issues.append(f"{rel}: {tag} {attr} references missing id #{ref}")

    for tag, value in parser.aria_current:
        if value not in VALID_ARIA_CURRENT:
            issues.append(f"{rel}: {tag} has invalid aria-current={value!r}")

    return issues


def main() -> int:
    files = html_files()
    issues: list[str] = []
    for path in files:
        issues.extend(audit_file(path))

    print(f"accessibility_pages_checked={len(files)}")
    print(f"accessibility_issues={len(issues)}")
    for issue in issues[:200]:
        print(f"ISSUE {issue}")
    if len(issues) > 200:
        print(f"ISSUE ... {len(issues) - 200} more")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
