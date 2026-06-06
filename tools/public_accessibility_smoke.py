#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
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


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    text: str


class AccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.title = ""
        self.ids: list[str] = []
        self.h1_count = 0
        self.main_count = 0
        self.navs: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.buttons: list[dict[str, object]] = []
        self.images: list[dict[str, str]] = []
        self.controls: list[dict[str, str]] = []
        self.labels_for: set[str] = set()
        self.summaries: list[dict[str, object]] = []
        self.iframes: list[dict[str, str]] = []
        self.idrefs: list[tuple[str, str, str]] = []
        self.aria_current: list[tuple[str, str]] = []
        self._stack: list[tuple[str, dict[str, str], list[str]]] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        self._stack.append((tag, data, []))
        if tag == "html":
            self.html_lang = data.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "main":
            self.main_count += 1
        elif tag == "nav":
            self.navs.append(data)
        elif tag == "a":
            data["_text"] = ""
            data["_image_alt"] = ""
            self.links.append(data)
        elif tag == "button":
            self.buttons.append({"attrs": data, "text": []})
        elif tag == "img":
            self.images.append(data)
            alt = data.get("alt", "")
            if alt:
                for stack_tag, stack_attrs, _text in reversed(self._stack[:-1]):
                    if stack_tag == "a":
                        stack_attrs["_image_alt"] = f"{stack_attrs.get('_image_alt', '')} {alt}".strip()
                        break
        elif tag in {"input", "textarea", "select"}:
            self.controls.append(data)
        elif tag == "label" and data.get("for"):
            self.labels_for.add(data["for"])
        elif tag == "summary":
            self.summaries.append({"attrs": data, "text": []})
        elif tag == "iframe":
            self.iframes.append(data)

        if "id" in data:
            self.ids.append(data["id"])
        for attr in IDREF_ATTRS:
            if attr in data:
                for ref in data[attr].split():
                    self.idrefs.append((tag, attr, ref[1:] if ref.startswith("#") else ref))
        if "aria-current" in data:
            self.aria_current.append((tag, data["aria-current"]))

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._stack:
            self._stack[-1][2].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if not self._stack:
            return
        current_tag, data, text_parts = self._stack.pop()
        text = normalize("".join(text_parts))
        if current_tag == "a":
            data["_text"] = text
        elif current_tag == "button":
            for button in reversed(self.buttons):
                if button.get("attrs") is data:
                    button["text"] = [text]
                    break
        elif current_tag == "summary":
            for summary in reversed(self.summaries):
                if summary.get("attrs") is data:
                    summary["text"] = [text]
                    break
        if self._stack and text:
            self._stack[-1][2].append(text)


def normalize(value: str) -> str:
    return " ".join(value.split())


def accessible_name(attrs: dict[str, str], text: str = "") -> str:
    return normalize(
        attrs.get("aria-label", "")
        or attrs.get("title", "")
        or attrs.get("alt", "")
        or attrs.get("_image_alt", "")
        or text
    )


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public accessibility smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                return Response(raw.geturl(), raw.status, raw.read().decode("utf-8", errors="replace"))
        except HTTPError as error:
            return Response(error.geturl(), error.code, error.read().decode("utf-8", errors="replace"))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def sitemap_locations(base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as error:
        return [], [f"/sitemap.xml: invalid XML: {error}"]
    locations = [
        (node.findtext("sm:loc", default="", namespaces=SITEMAP_NS) or "").strip()
        for node in root.findall("sm:url", SITEMAP_NS)
    ]
    locations = [loc for loc in locations if loc]
    issues = []
    if len(locations) != len(set(locations)):
        issues.append("/sitemap.xml: duplicate loc values")
    return locations, issues


def audit_page(url: str, html: str) -> tuple[list[str], dict[str, int]]:
    parser = AccessibilityParser()
    parser.feed(html)
    issues: list[str] = []
    stats = {
        "links": 0,
        "buttons": 0,
        "images": 0,
        "controls": 0,
        "navs": 0,
        "idrefs": 0,
        "aria_current": 0,
    }

    duplicate_ids = [item for item, count in Counter(parser.ids).items() if count > 1]
    for item in duplicate_ids:
        issues.append(f"{url}: duplicate id #{item}")
    ids = set(parser.ids)

    if not parser.html_lang:
        issues.append(f"{url}: html missing lang")
    if not normalize(parser.title):
        issues.append(f"{url}: missing title")
    if parser.main_count != 1:
        issues.append(f"{url}: expected one main landmark, found {parser.main_count}")
    if parser.h1_count != 1:
        issues.append(f"{url}: expected one h1, found {parser.h1_count}")

    stats["navs"] = len(parser.navs)
    for nav in parser.navs:
        if not accessible_name(nav):
            issues.append(f"{url}: nav missing accessible label")

    for link in parser.links:
        stats["links"] += 1
        href = link.get("href", "")
        if not href:
            issues.append(f"{url}: anchor missing href")
        if not accessible_name(link, link.get("_text", "")):
            issues.append(f"{url}: link {href or '(no href)'} missing accessible name")

    for button in parser.buttons:
        stats["buttons"] += 1
        attrs = button.get("attrs", {})
        text = " ".join(button.get("text", [])) if isinstance(button.get("text"), list) else ""
        if isinstance(attrs, dict) and not accessible_name(attrs, text):
            issues.append(f"{url}: button missing accessible name")

    for summary in parser.summaries:
        attrs = summary.get("attrs", {})
        text = " ".join(summary.get("text", [])) if isinstance(summary.get("text"), list) else ""
        if isinstance(attrs, dict) and not accessible_name(attrs, text):
            issues.append(f"{url}: details summary missing accessible name")

    for image in parser.images:
        stats["images"] += 1
        if "alt" not in image:
            issues.append(f"{url}: image {image.get('src', '(no src)')} missing alt")
        if image.get("loading") == "lazy" and ("width" not in image or "height" not in image):
            issues.append(f"{url}: lazy image {image.get('src', '(no src)')} missing width/height")

    for control in parser.controls:
        stats["controls"] += 1
        control_type = control.get("type", "")
        if control_type in {"hidden", "submit", "button"}:
            continue
        control_id = control.get("id", "")
        if control_id and control_id in parser.labels_for:
            continue
        if accessible_name(control):
            continue
        issues.append(f"{url}: control {control.get('name', control.get('data-field', 'unnamed'))} missing label")

    for iframe in parser.iframes:
        if not accessible_name(iframe):
            issues.append(f"{url}: iframe {iframe.get('src', '(no src)')} missing title")

    for tag, attr, ref in parser.idrefs:
        stats["idrefs"] += 1
        if not ref:
            issues.append(f"{url}: {tag} {attr} has empty reference")
        elif ref not in ids:
            issues.append(f"{url}: {tag} {attr} references missing id #{ref}")

    for tag, value in parser.aria_current:
        stats["aria_current"] += 1
        if value not in VALID_ARIA_CURRENT:
            issues.append(f"{url}: {tag} has invalid aria-current={value!r}")

    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes accessibility structure across sitemap pages.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    locations, issues = sitemap_locations(base_url)
    pages_checked = 0
    totals = Counter()
    for loc in locations:
        response = request_url(loc)
        if response.status != 200:
            issues.append(f"{loc}: expected status 200, got {response.status}")
            continue
        page_issues, stats = audit_page(loc, response.text)
        issues.extend(page_issues)
        totals.update(stats)
        pages_checked += 1

    print(f"public_accessibility_pages_checked={pages_checked}")
    print(f"public_accessibility_links_checked={totals['links']}")
    print(f"public_accessibility_buttons_checked={totals['buttons']}")
    print(f"public_accessibility_images_checked={totals['images']}")
    print(f"public_accessibility_controls_checked={totals['controls']}")
    print(f"public_accessibility_navs_checked={totals['navs']}")
    print(f"public_accessibility_idrefs_checked={totals['idrefs']}")
    print(f"public_accessibility_aria_current_checked={totals['aria_current']}")
    print(f"public_accessibility_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
