#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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


def load_generator_config():
    generator_path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_generator_keepsake_smoke", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {generator_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def expected_story_cta(lang: str, slug: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    return f"lovetypes.tw{prefix}/keepsakes/#keepsake-{slug}"


def localized_route(lang: str, route: str, anchor: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    return f"{prefix}/{route}/#{anchor}" if prefix else f"/{route}/#{anchor}"


def localized_page(lang: str, route: str) -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    return f"{prefix}/{route}/" if prefix else f"/{route}/"


def decode_cloudflare_email_href(href: str) -> str:
    if not href.startswith("/cdn-cgi/l/email-protection#"):
        return href
    encoded = href.split("#", 1)[1]
    try:
        data = bytes.fromhex(encoded)
    except ValueError:
        return href
    if not data:
        return href
    key = data[0]
    return "".join(chr(byte ^ key) for byte in data[1:])


def contact_request_hrefs(links: list[Element]) -> list[str]:
    hrefs = [decode_cloudflare_email_href(link.attrs.get("href", "")) for link in links]
    return [
        href
        for href in hrefs
        if href.startswith("mailto:contact@lovetypes.tw") or href.startswith("contact@lovetypes.tw")
    ]


def check_story_asset(base_url: str, source: str, path: str, image_cache: dict[str, Response]) -> list[str]:
    issues: list[str] = []
    absolute = urljoin(base_url + "/", path.lstrip("/"))
    host = urlparse(base_url).hostname or ""
    if absolute not in image_cache:
        image_cache[absolute] = request_url(absolute, method="HEAD")
    response = image_cache[absolute]
    if response.status != 200:
        issues.append(f"{source}: story image expected status 200 for {path}, got {response.status}")
    if not response.headers.get("content-type", "").startswith("image/"):
        issues.append(f"{source}: story image expected image content-type for {path}")
    cache_control = response.headers.get("cache-control", "").lower()
    if host not in {"127.0.0.1", "localhost"} and ("max-age=31536000" not in cache_control or "immutable" not in cache_control):
        issues.append(f"{source}: story image should be immutable cached, got {cache_control!r}")
    return issues


def validate_page(
    base_url: str,
    lang: str,
    path: str,
    image_cache: dict[str, Response],
    expected_waitlist_cards: int,
) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "pages": 0,
        "shelf_cards": 0,
        "collector_cards": 0,
        "download_links": 0,
        "collector_open_events": 0,
        "collector_download_events": 0,
        "story_buttons": 0,
        "route_links": 0,
        "plan_links": 0,
        "story_images": 0,
        "collector_request_mailtos": 0,
        "practice_cards": 0,
        "practice_plan_links": 0,
        "practice_route_links": 0,
        "practice_print_buttons": 0,
        "free_asset_cards": 0,
        "free_asset_events": 0,
        "free_asset_request_mailtos": 0,
        "safety_bridge_sections": 0,
        "safety_bridge_links": 0,
        "waitlist_cards": 0,
        "waitlist_mailtos": 0,
        "waitlist_option_mailtos": 0,
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
        open_links = [link for link in links if link.attrs.get("href") == story and link.attrs.get("target") == "_blank"]
        if not open_links:
            issues.append(f"{source}: {slug} collector card missing open story image link")
        elif not any(link.attrs.get("data-funnel-event") == "collector_story_open" for link in open_links):
            issues.append(f"{source}: {slug} collector card open story link missing collector_story_open event")
        else:
            stats["collector_open_events"] += 1
        if any(link.attrs.get("href") == story and "download" in link.attrs for link in links):
            stats["download_links"] += 1
            if any(link.attrs.get("href") == story and "download" in link.attrs and link.attrs.get("data-funnel-event") == "collector_story_download" for link in links):
                stats["collector_download_events"] += 1
            else:
                issues.append(f"{source}: {slug} collector card download link missing collector_story_download event")
        else:
            issues.append(f"{source}: {slug} collector card missing story image download link")
        request_links = contact_request_hrefs(links)
        if len(request_links) != 1:
            issues.append(f"{source}: {slug} collector card should include one supply request mailto, got {len(request_links)}")
        elif "subject=" not in request_links[0] or "body=" not in request_links[0]:
            issues.append(f"{source}: {slug} collector request mailto should include subject and body")
        else:
            stats["collector_request_mailtos"] += 1
        story_button = next((button for button in buttons if button.attrs.get("data-result-action") == "story"), None)
        if story_button is None:
            issues.append(f"{source}: {slug} collector card missing story button")
        else:
            stats["story_buttons"] += 1
            if story_button.attrs.get("data-story-slug") != slug:
                issues.append(f"{source}: {slug} story button should carry data-story-slug={slug}")
            expected_cta = expected_story_cta(lang, slug)
            if story_button.attrs.get("data-story-cta", "") != expected_cta:
                issues.append(f"{source}: {slug} story button should carry localized keepsake CTA {expected_cta}")

        practice = find_by_id(root, f"practice-card-{slug}")
        if practice is None:
            issues.append(f"{source}: missing #practice-card-{slug}")
        else:
            stats["practice_cards"] += 1
            if practice.attrs.get("data-keepsake-practice-card") != slug:
                issues.append(f"{source}: #practice-card-{slug} missing data-keepsake-practice-card={slug}")
            practice_hrefs = [link.attrs.get("href", "") for link in descendants(practice, "a")]
            if localized_route(lang, "repair-plan", f"plan-{slug}") in practice_hrefs:
                stats["practice_plan_links"] += 1
            else:
                issues.append(f"{source}: {slug} practice card missing repair plan link")
            if localized_route(lang, "resources", f"supply-{slug}") in practice_hrefs:
                stats["practice_route_links"] += 1
            else:
                issues.append(f"{source}: {slug} practice card missing supply route link")
            print_buttons = [button for button in descendants(practice, "button") if "window.print()" in button.attrs.get("onclick", "")]
            if print_buttons:
                stats["practice_print_buttons"] += 1
            else:
                issues.append(f"{source}: {slug} practice card missing print button")

        free_asset = find_by_id(root, f"free-keepsake-{slug}")
        if free_asset is None:
            issues.append(f"{source}: missing #free-keepsake-{slug}")
        else:
            stats["free_asset_cards"] += 1
            free_links = descendants(free_asset, "a")
            free_events = {link.attrs.get("data-funnel-event", "") for link in free_links}
            expected_free_events = {"free_keepsake_open", "free_keepsake_download", "free_keepsake_asset_request"}
            missing_free_events = expected_free_events - free_events
            if missing_free_events:
                issues.append(f"{source}: {slug} free keepsake card missing events {', '.join(sorted(missing_free_events))}")
            else:
                stats["free_asset_events"] += len(expected_free_events)
            request_links = [link for link in free_links if link.attrs.get("data-funnel-event") == "free_keepsake_asset_request"]
            if len(request_links) != 1:
                issues.append(f"{source}: {slug} free keepsake should include one direct asset request link, got {len(request_links)}")
            elif request_links[0].attrs.get("data-free-keepsake-request") != slug:
                issues.append(f"{source}: {slug} free keepsake request should carry guardian slug")
            else:
                request_href = decode_cloudflare_email_href(request_links[0].attrs.get("href", ""))
                parsed = urlparse(request_href)
                query = parse_qs(parsed.query)
                if not (request_href.startswith("mailto:contact@lovetypes.tw") or request_href.startswith("contact@lovetypes.tw")):
                    issues.append(f"{source}: {slug} free keepsake request should be a contact mailto")
                elif not query.get("subject") or not query.get("body"):
                    issues.append(f"{source}: {slug} free keepsake request should include subject and body")
                else:
                    stats["free_asset_request_mailtos"] += 1

    safety_bridge = next((item for item in walk(root) if item.attrs.get("data-safety-boundary-bridge") == ""), None)
    if safety_bridge is None:
        issues.append(f"{source}: missing safety boundary bridge")
    else:
        stats["safety_bridge_sections"] += 1
        bridge_hrefs = {link.attrs.get("href", "") for link in descendants(safety_bridge, "a")}
        expected_bridge_hrefs = {
            localized_page(lang, "privacy"),
            localized_page(lang, "terms"),
            localized_route(lang, "contact", "site-repair-report"),
        }
        for expected in expected_bridge_hrefs:
            if expected not in bridge_hrefs:
                issues.append(f"{source}: safety boundary bridge missing {expected}")
            else:
                stats["safety_bridge_links"] += 1

    waitlist = find_by_id(root, "keepsake-supply-waitlist")
    if waitlist is None:
        issues.append(f"{source}: missing keepsake supply waitlist section")
    else:
        waitlist_cards = [item for item in descendants(waitlist, "article") if has_class(item, "contact-request-grid") is False]
        if len(waitlist_cards) != expected_waitlist_cards:
            issues.append(f"{source}: expected {expected_waitlist_cards} keepsake waitlist request cards, got {len(waitlist_cards)}")
        else:
            stats["waitlist_cards"] += len(waitlist_cards)
        waitlist_links = descendants(waitlist, "a")
        if not any(link.attrs.get("href") == localized_route(lang, "contact", "luna-supply-request") for link in waitlist_links):
            issues.append(f"{source}: keepsake waitlist missing contact page bridge")
        mailto_hrefs = contact_request_hrefs(waitlist_links)
        expected_mailtos = expected_waitlist_cards + 2
        if len(mailto_hrefs) != expected_mailtos:
            issues.append(f"{source}: keepsake waitlist should include {expected_mailtos} contact mailto or protected email links, got {len(mailto_hrefs)}")
        else:
            for href in mailto_hrefs:
                query = parse_qs(urlparse(href).query)
                if not query.get("subject") or not query.get("body"):
                    issues.append(f"{source}: keepsake waitlist mailto should include subject and body")
                    break
            else:
                stats["waitlist_mailtos"] += expected_mailtos
        structured_links = [link for link in waitlist_links if link.attrs.get("data-lead-intake-send") is not None]
        if len(structured_links) != 1:
            issues.append(f"{source}: keepsake waitlist should include one structured lead intake mailto, got {len(structured_links)}")
        elif structured_links[0].attrs.get("data-funnel-event") != "keepsake_structured_request_mailto":
            issues.append(f"{source}: structured lead intake link should use keepsake_structured_request_mailto")
        option_links = [link for link in waitlist_links if "data-keepsake-waitlist-option" in link.attrs]
        if len(option_links) != expected_waitlist_cards:
            issues.append(f"{source}: keepsake waitlist should include {expected_waitlist_cards} direct option mailtos, got {len(option_links)}")
        else:
            stats["waitlist_option_mailtos"] += len(option_links)
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
    generator = load_generator_config()
    image_cache: dict[str, Response] = {}
    issues: list[str] = []
    totals = {
        "pages": 0,
        "shelf_cards": 0,
        "collector_cards": 0,
        "download_links": 0,
        "collector_open_events": 0,
        "collector_download_events": 0,
        "story_buttons": 0,
        "route_links": 0,
        "plan_links": 0,
        "story_images": 0,
        "collector_request_mailtos": 0,
        "practice_cards": 0,
        "practice_plan_links": 0,
        "practice_route_links": 0,
        "practice_print_buttons": 0,
        "free_asset_cards": 0,
        "free_asset_events": 0,
        "free_asset_request_mailtos": 0,
        "safety_bridge_sections": 0,
        "safety_bridge_links": 0,
        "waitlist_cards": 0,
        "waitlist_mailtos": 0,
        "waitlist_option_mailtos": 0,
        "waitlist_copy_buttons": 0,
    }
    for lang, path in LANG_PATHS.items():
        page_issues, stats = validate_page(
            base_url,
            lang,
            path,
            image_cache,
            len(generator.CONTACT_REQUESTS[lang]["items"]),
        )
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"public_keepsake_pages_checked={totals['pages']}")
    print(f"public_keepsake_shelf_cards_checked={totals['shelf_cards']}")
    print(f"public_keepsake_collector_cards_checked={totals['collector_cards']}")
    print(f"public_keepsake_story_images_checked={totals['story_images']}")
    print(f"public_keepsake_download_links_checked={totals['download_links']}")
    print(f"public_keepsake_collector_open_events_checked={totals['collector_open_events']}")
    print(f"public_keepsake_collector_download_events_checked={totals['collector_download_events']}")
    print(f"public_keepsake_story_buttons_checked={totals['story_buttons']}")
    print(f"public_keepsake_route_links_checked={totals['route_links']}")
    print(f"public_keepsake_plan_links_checked={totals['plan_links']}")
    print(f"public_keepsake_collector_request_mailtos_checked={totals['collector_request_mailtos']}")
    print(f"public_keepsake_practice_cards_checked={totals['practice_cards']}")
    print(f"public_keepsake_practice_plan_links_checked={totals['practice_plan_links']}")
    print(f"public_keepsake_practice_route_links_checked={totals['practice_route_links']}")
    print(f"public_keepsake_practice_print_buttons_checked={totals['practice_print_buttons']}")
    print(f"public_keepsake_free_asset_cards_checked={totals['free_asset_cards']}")
    print(f"public_keepsake_free_asset_events_checked={totals['free_asset_events']}")
    print(f"public_keepsake_free_asset_request_mailtos_checked={totals['free_asset_request_mailtos']}")
    print(f"public_keepsake_safety_bridge_sections_checked={totals['safety_bridge_sections']}")
    print(f"public_keepsake_safety_bridge_links_checked={totals['safety_bridge_links']}")
    print(f"public_keepsake_waitlist_cards_checked={totals['waitlist_cards']}")
    print(f"public_keepsake_waitlist_mailtos_checked={totals['waitlist_mailtos']}")
    print(f"public_keepsake_waitlist_option_mailtos_checked={totals['waitlist_option_mailtos']}")
    print(f"public_keepsake_waitlist_copy_buttons_checked={totals['waitlist_copy_buttons']}")
    print(f"public_keepsake_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
