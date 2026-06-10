#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {
    "zh": "/keepsakes/",
    "en": "/en/keepsakes/",
    "ja": "/ja/keepsakes/",
    "ko": "/ko/keepsakes/",
    "es": "/es/keepsakes/",
}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
STORY_SIZE = ("1080", "1920")


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict[str, str]
    text: str = ""


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    text: str = ""
    children: list["Element"] = field(default_factory=list)


class KeepsakeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root = Element("root", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        element = Element(tag.lower(), data)
        self.stack[-1].children.append(element)
        if tag.lower() not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(element)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.stack[-1].text += data


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, *, method: str = "GET", attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(
                url,
                method=method,
                headers={"User-Agent": "LoveTypes public keepsake smoke/1.0", "Accept": "text/html,image/*,*/*;q=0.8"},
            )
            with urlopen(request, timeout=20) as raw:
                text = "" if method == "HEAD" else raw.read().decode("utf-8", errors="replace")
                return Response(raw.geturl(), raw.status, {key.lower(): value for key, value in raw.headers.items()}, text)
        except HTTPError as error:
            text = "" if method == "HEAD" else error.read().decode("utf-8", errors="replace")
            return Response(error.geturl(), error.code, {key.lower(): value for key, value in error.headers.items()}, text)
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def walk(element: Element) -> list[Element]:
    elements = [element]
    for child in element.children:
        elements.extend(walk(child))
    return elements


def has_class(element: Element, class_name: str) -> bool:
    return class_name in element.attrs.get("class", "").split()


def descendants(element: Element, tag: str | None = None) -> list[Element]:
    items = walk(element)[1:]
    return [item for item in items if tag is None or item.tag == tag]


def find_by_id(root: Element, element_id: str) -> Element | None:
    return next((element for element in walk(root) if element.attrs.get("id") == element_id), None)


def find_all(root: Element, *, tag: str | None = None, class_name: str | None = None) -> list[Element]:
    items = walk(root)
    if tag:
        items = [item for item in items if item.tag == tag]
    if class_name:
        items = [item for item in items if has_class(item, class_name)]
    return items


def expected_story(lang: str, slug: str) -> str:
    return f"/assets/lovetypes/share/{slug}-story-{lang}.webp"


def localized_route(lang: str, route: str, anchor: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    return f"{prefix}/{route}/#{anchor}" if prefix else f"/{route}/#{anchor}"


def check_story_asset(base_url: str, source: str, path: str, image_cache: dict[str, Response]) -> list[str]:
    issues: list[str] = []
    absolute = urljoin(base_url + "/", path.lstrip("/"))
    if absolute not in image_cache:
        image_cache[absolute] = request_url(absolute, method="HEAD")
    response = image_cache[absolute]
    if response.status != 200:
        issues.append(f"{source}: story image expected status 200 for {path}, got {response.status}")
    if not response.headers.get("content-type", "").startswith("image/"):
        issues.append(f"{source}: story image expected image content-type for {path}")
    cache_control = response.headers.get("cache-control", "").lower()
    if "max-age=31536000" not in cache_control or "immutable" not in cache_control:
        issues.append(f"{source}: story image should be immutable cached, got {cache_control!r}")
    return issues


def validate_page(base_url: str, lang: str, path: str, image_cache: dict[str, Response]) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "pages": 0,
        "shelf_cards": 0,
        "collector_cards": 0,
        "download_links": 0,
        "story_buttons": 0,
        "route_links": 0,
        "plan_links": 0,
        "story_images": 0,
        "waitlist_cards": 0,
        "waitlist_mailtos": 0,
        "waitlist_copy_buttons": 0,
    }
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    source = path
    if response.status != 200:
        return [f"{source}: expected status 200, got {response.status}"], stats
    stats["pages"] = 1
    parser = KeepsakeParser()
    parser.feed(response.text)
    root = parser.root

    shelf_cards = find_all(root, tag="a", class_name="keepsake-shelf-card")
    if len(shelf_cards) != len(GUARDIAN_SLUGS):
        issues.append(f"{source}: expected five keepsake shelf cards, got {len(shelf_cards)}")
    for slug in GUARDIAN_SLUGS:
        story = expected_story(lang, slug)
        shelf = next((card for card in shelf_cards if card.attrs.get("data-guardian-domain") == slug), None)
        if shelf is None:
            issues.append(f"{source}: missing shelf card for {slug}")
        else:
            stats["shelf_cards"] += 1
            if shelf.attrs.get("href") != f"#keepsake-card-{slug}":
                issues.append(f"{source}: {slug} shelf href should target #keepsake-card-{slug}")
            shelf_img = next((img for img in descendants(shelf, "img") if img.attrs.get("src") == story), None)
            if shelf_img is None:
                issues.append(f"{source}: {slug} shelf should show localized story image {story}")

        anchor = find_by_id(root, f"keepsake-{slug}")
        if anchor is None:
            issues.append(f"{source}: missing #keepsake-{slug} anchor")
        card = find_by_id(root, f"keepsake-card-{slug}")
        if card is None:
            issues.append(f"{source}: missing #keepsake-card-{slug}")
            continue
        stats["collector_cards"] += 1

        images = [img for img in descendants(card, "img") if img.attrs.get("src") == story]
        if len(images) != 1:
            issues.append(f"{source}: {slug} collector card should include one localized story image {story}, got {len(images)}")
        elif (images[0].attrs.get("width"), images[0].attrs.get("height")) != STORY_SIZE:
            issues.append(f"{source}: {slug} story image dimensions should be {STORY_SIZE}")
        else:
            stats["story_images"] += 1
            issues.extend(check_story_asset(base_url, f"{source}:{slug}", story, image_cache))

        links = descendants(card, "a")
        buttons = descendants(card, "button")
        hrefs = [link.attrs.get("href", "") for link in links]
        if localized_route(lang, "resources", f"supply-{slug}") in hrefs:
            stats["route_links"] += 1
        else:
            issues.append(f"{source}: {slug} collector card missing supply route link")
        if localized_route(lang, "repair-plan", f"plan-{slug}") in hrefs:
            stats["plan_links"] += 1
        else:
            issues.append(f"{source}: {slug} collector card missing repair plan link")
        if not any(link.attrs.get("href") == story and link.attrs.get("target") == "_blank" for link in links):
            issues.append(f"{source}: {slug} collector card missing open story image link")
        if any(link.attrs.get("href") == story and "download" in link.attrs for link in links):
            stats["download_links"] += 1
        else:
            issues.append(f"{source}: {slug} collector card missing story image download link")
        story_button = next((button for button in buttons if button.attrs.get("data-result-action") == "story"), None)
        if story_button is None:
            issues.append(f"{source}: {slug} collector card missing story button")
        else:
            stats["story_buttons"] += 1
            if story_button.attrs.get("data-story-slug") != slug:
                issues.append(f"{source}: {slug} story button should carry data-story-slug={slug}")
            if not story_button.attrs.get("data-story-cta", "").endswith("/keepsakes"):
                issues.append(f"{source}: {slug} story button should carry keepsakes CTA")

    waitlist = find_by_id(root, "keepsake-supply-waitlist")
    if waitlist is None:
        issues.append(f"{source}: missing keepsake supply waitlist section")
    else:
        waitlist_cards = [item for item in descendants(waitlist, "article") if has_class(item, "contact-request-grid") is False]
        if len(waitlist_cards) != 3:
            issues.append(f"{source}: expected three keepsake waitlist request cards, got {len(waitlist_cards)}")
        else:
            stats["waitlist_cards"] += len(waitlist_cards)
        waitlist_links = descendants(waitlist, "a")
        if not any(link.attrs.get("href") == localized_route(lang, "contact", "luna-supply-request") for link in waitlist_links):
            issues.append(f"{source}: keepsake waitlist missing contact page bridge")
        mailto_links = [
            link
            for link in waitlist_links
            if link.attrs.get("href", "").startswith("mailto:contact@lovetypes.tw")
            or link.attrs.get("href", "").startswith("/cdn-cgi/l/email-protection")
        ]
        if len(mailto_links) != 1:
            issues.append(f"{source}: keepsake waitlist should include one contact mailto or protected email link, got {len(mailto_links)}")
        else:
            href = mailto_links[0].attrs["href"]
            query = parse_qs(urlparse(href).query)
            if href.startswith("mailto:") and (not query.get("subject") or not query.get("body")):
                issues.append(f"{source}: keepsake waitlist mailto should include subject and body")
            else:
                stats["waitlist_mailtos"] += 1
        copy_buttons = [button for button in descendants(waitlist, "button") if "data-copy-contact-template" in button.attrs]
        if len(copy_buttons) != 1:
            issues.append(f"{source}: keepsake waitlist should include one copy template button, got {len(copy_buttons)}")
        elif not copy_buttons[0].attrs.get("data-copy-text"):
            issues.append(f"{source}: keepsake waitlist copy template button missing data-copy-text")
        else:
            stats["waitlist_copy_buttons"] += 1

    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes keepsake hall cards and story-card actions.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    image_cache: dict[str, Response] = {}
    issues: list[str] = []
    totals = {
        "pages": 0,
        "shelf_cards": 0,
        "collector_cards": 0,
        "download_links": 0,
        "story_buttons": 0,
        "route_links": 0,
        "plan_links": 0,
        "story_images": 0,
        "waitlist_cards": 0,
        "waitlist_mailtos": 0,
        "waitlist_copy_buttons": 0,
    }
    for lang, path in LANG_PATHS.items():
        page_issues, stats = validate_page(base_url, lang, path, image_cache)
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"public_keepsake_pages_checked={totals['pages']}")
    print(f"public_keepsake_shelf_cards_checked={totals['shelf_cards']}")
    print(f"public_keepsake_collector_cards_checked={totals['collector_cards']}")
    print(f"public_keepsake_story_images_checked={totals['story_images']}")
    print(f"public_keepsake_download_links_checked={totals['download_links']}")
    print(f"public_keepsake_story_buttons_checked={totals['story_buttons']}")
    print(f"public_keepsake_route_links_checked={totals['route_links']}")
    print(f"public_keepsake_plan_links_checked={totals['plan_links']}")
    print(f"public_keepsake_waitlist_cards_checked={totals['waitlist_cards']}")
    print(f"public_keepsake_waitlist_mailtos_checked={totals['waitlist_mailtos']}")
    print(f"public_keepsake_waitlist_copy_buttons_checked={totals['waitlist_copy_buttons']}")
    print(f"public_keepsake_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
