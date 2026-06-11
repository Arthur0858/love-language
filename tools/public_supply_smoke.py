#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {
    "zh": "/resources/",
    "en": "/en/resources/",
    "ja": "/ja/resources/",
    "ko": "/ko/resources/",
    "es": "/es/resources/",
}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
TYPE_GUIDE_ROUTES = {
    "iris": "guides/words-of-affirmation-scripts",
    "noah": "guides/quality-time-long-distance",
    "vivian": "guides/gifts-are-not-materialism",
    "claire": "guides/acts-of-service-boundaries",
    "dora": "guides/physical-touch-consent-safety",
}
BOOKS_HOST = "www.books.com.tw"
AFFILIATE_TOKENS = ("arthur0858", "utm_campaign=ap-202604")


def load_generator_config():
    generator_path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_generator_supply_smoke", generator_path)
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
    text: str


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    text: str = ""
    children: list["Element"] = field(default_factory=list)


class SupplyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root = Element("root", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        element = Element(tag.lower(), {key.lower(): value or "" for key, value in attrs})
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


def request_url(url: str, attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public supply smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                return Response(raw.geturl(), raw.status, raw.read().decode("utf-8", errors="replace"))
        except HTTPError as error:
            return Response(error.geturl(), error.code, error.read().decode("utf-8", errors="replace"))
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


def descendants(element: Element, tag: str | None = None) -> list[Element]:
    items = walk(element)[1:]
    return [item for item in items if tag is None or item.tag == tag]


def text_content(element: Element) -> str:
    return " ".join(item.text.strip() for item in walk(element) if item.text.strip())


def has_class(element: Element, class_name: str) -> bool:
    return class_name in element.attrs.get("class", "").split()


def find_by_id(root: Element, element_id: str) -> Element | None:
    return next((element for element in walk(root) if element.attrs.get("id") == element_id), None)


def find_all(root: Element, *, tag: str | None = None, class_name: str | None = None, attr: str | None = None) -> list[Element]:
    items = walk(root)
    if tag:
        items = [item for item in items if item.tag == tag]
    if class_name:
        items = [item for item in items if has_class(item, class_name)]
    if attr:
        items = [item for item in items if attr in item.attrs]
    return items


def localized_path(lang: str, route: str = "") -> str:
    prefix = "" if lang == "zh" else f"/{lang}"
    route = route.strip("/")
    if not route:
        return f"{prefix}/" if prefix else "/"
    return f"{prefix}/{route}/" if prefix else f"/{route}/"


def is_affiliate_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == BOOKS_HOST and all(token in value for token in AFFILIATE_TOKENS)


def mailto_query(value: str) -> dict[str, list[str]]:
    if not value.startswith("mailto:"):
        return {}
    _head, _sep, query = value.partition("?")
    return parse_qs(query)


def validate_summary(source: str, slug: str, value: str) -> list[str]:
    issues: list[str] = []
    try:
        summary = json.loads(unquote(value))
    except json.JSONDecodeError as error:
        return [f"{source}: {slug} data-route-summary is invalid JSON: {error}"]
    for key in ("title", "guardian", "practice", "supply", "book", "url"):
        if not isinstance(summary.get(key), str) or not summary[key].strip():
            issues.append(f"{source}: {slug} route summary missing {key}")
    if f"#supply-{slug}" not in summary.get("url", ""):
        issues.append(f"{source}: {slug} route summary should point to #supply-{slug}")
    return issues


def validate_page(base_url: str, lang: str, path: str, expected_formats: list[str]) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "pages": 0,
        "quick_cards": 0,
        "route_cards": 0,
        "guide_links": 0,
        "luna_links": 0,
        "route_request_mailtos": 0,
        "route_product_stacks": 0,
        "route_product_links": 0,
        "copy_buttons": 0,
        "affiliate_links": 0,
        "affiliate_book_cards": 0,
        "route_tags": 0,
        "wishlist_cards": 0,
        "wishlist_formats": 0,
        "wishlist_mailtos": 0,
        "wishlist_copy_buttons": 0,
        "safety_sections": 0,
        "safety_bridge_sections": 0,
        "safety_bridge_links": 0,
        "decision_sections": 0,
        "decision_cards": 0,
        "decision_links": 0,
    }
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["pages"] = 1
    parser = SupplyParser()
    parser.feed(response.text)
    root = parser.root

    if "affiliate-disclosure" not in response.text or "affiliate-link-note" not in response.text:
        issues.append(f"{path}: missing affiliate disclosure and fallback note")
    if "supply-trust" not in response.text:
        issues.append(f"{path}: missing supply trust safety section")
    else:
        stats["safety_sections"] += 1
    safety_bridge = next((item for item in walk(root) if item.attrs.get("data-safety-boundary-bridge") == ""), None)
    if safety_bridge is None:
        issues.append(f"{path}: missing safety boundary bridge")
    else:
        stats["safety_bridge_sections"] += 1
        bridge_hrefs = {link.attrs.get("href", "") for link in descendants(safety_bridge, "a")}
        expected_bridge_hrefs = {
            localized_path(lang, "privacy"),
            localized_path(lang, "terms"),
            localized_path(lang, "contact") + "#site-repair-report",
        }
        for expected in expected_bridge_hrefs:
            if expected not in bridge_hrefs:
                issues.append(f"{path}: safety boundary bridge missing {expected}")
            else:
                stats["safety_bridge_links"] += 1
    if "data-supply-owned-signal" not in response.text:
        issues.append(f"{path}: missing owned supply wishlist section")
    decision_section = next((item for item in walk(root) if item.attrs.get("data-supply-decision-matrix") == ""), None)
    if decision_section is None:
        issues.append(f"{path}: missing supply decision matrix")
    else:
        stats["decision_sections"] += 1
        decision_cards = [item for item in descendants(decision_section) if item.attrs.get("data-supply-decision-card") == ""]
        decision_links = descendants(decision_section, "a")
        stats["decision_cards"] += len(decision_cards)
        stats["decision_links"] += len(decision_links)
        if len(decision_cards) != 4:
            issues.append(f"{path}: expected four supply decision cards, got {len(decision_cards)}")
        expected_decision_hrefs = {
            localized_path(lang, "repair-plan"),
            localized_path(lang, "luna-yoga-music"),
            localized_path(lang, "resources") + "#affiliate-books",
            localized_path(lang, "contact") + "#luna-supply-request",
        }
        actual_decision_hrefs = {link.attrs.get("href", "") for link in decision_links}
        for expected in expected_decision_hrefs:
            if expected not in actual_decision_hrefs:
                issues.append(f"{path}: supply decision matrix missing CTA {expected}")

    quick_cards = find_all(root, tag="a", class_name="supply-quick-card")
    if len(quick_cards) != len(GUARDIAN_SLUGS):
        issues.append(f"{path}: expected five quick route cards, got {len(quick_cards)}")
    for slug in GUARDIAN_SLUGS:
        quick = next((card for card in quick_cards if card.attrs.get("data-guardian-domain") == slug), None)
        if quick is None:
            issues.append(f"{path}: missing quick route card for {slug}")
        else:
            stats["quick_cards"] += 1
            if quick.attrs.get("href") != f"#supply-{slug}":
                issues.append(f"{path}: {slug} quick route should target #supply-{slug}")

        card = find_by_id(root, f"supply-{slug}")
        if card is None:
            issues.append(f"{path}: missing #supply-{slug} route card")
            continue
        if not has_class(card, "supply-route-card"):
            issues.append(f"{path}: #supply-{slug} should be a supply-route-card")
        stats["route_cards"] += 1
        links = descendants(card, "a")
        buttons = descendants(card, "button")
        hrefs = [link.attrs.get("href", "") for link in links]

        expected_guide = localized_path(lang, TYPE_GUIDE_ROUTES[slug])
        if expected_guide in hrefs:
            stats["guide_links"] += 1
        else:
            issues.append(f"{path}: {slug} route missing guide link {expected_guide}")
        expected_luna = localized_path(lang, "luna-yoga-music") + f"#luna-{slug}"
        if expected_luna in hrefs:
            stats["luna_links"] += 1
        else:
            issues.append(f"{path}: {slug} route missing Luna link {expected_luna}")
        request_links = [
            link
            for link in links
            if link.attrs.get("href", "").startswith("mailto:contact@lovetypes.tw")
            or link.attrs.get("href", "").startswith("/cdn-cgi/l/email-protection")
        ]
        if not request_links:
            issues.append(f"{path}: {slug} route should include a contact request mailto or protected email link")
        else:
            stats["route_request_mailtos"] += len(request_links)
            for request_link in request_links:
                href = request_link.attrs["href"]
                query = mailto_query(href)
                if href.startswith("mailto:") and (not query.get("subject") or not query.get("body")):
                    issues.append(f"{path}: {slug} route contact request should include subject and body")
        product_stacks = [item for item in descendants(card) if has_class(item, "supply-product-stack")]
        if len(product_stacks) != 1:
            issues.append(f"{path}: {slug} route should include one supply product stack, got {len(product_stacks)}")
        else:
            stats["route_product_stacks"] += 1
            product_hrefs = [link.attrs.get("href", "") for link in descendants(product_stacks[0], "a")]
            expected_product_targets = (
                localized_path(lang, "keepsakes") + f"#keepsake-card-{slug}",
                localized_path(lang, "luna-yoga-music") + f"#luna-{slug}",
            )
            for expected in expected_product_targets:
                if expected not in product_hrefs:
                    issues.append(f"{path}: {slug} product stack missing {expected}")
                else:
                    stats["route_product_links"] += 1
            product_request_links = [
                href
                for href in product_hrefs
                if href.startswith("mailto:contact@lovetypes.tw") or href.startswith("/cdn-cgi/l/email-protection")
            ]
            if len(product_request_links) != 1:
                issues.append(f"{path}: {slug} product stack should include one request mailto or protected email link")
            else:
                stats["route_product_links"] += 1
        affiliate_links = [link for link in links if is_affiliate_url(link.attrs.get("href", ""))]
        if len(affiliate_links) != 1:
            issues.append(f"{path}: {slug} route should include one tracked books.com.tw link, got {len(affiliate_links)}")
        else:
            stats["affiliate_links"] += 1
            rel_tokens = set(affiliate_links[0].attrs.get("rel", "").split())
            if not {"noopener", "noreferrer", "sponsored"}.issubset(rel_tokens):
                issues.append(f"{path}: {slug} affiliate route link missing safe sponsored rel")
        copy_button = next((button for button in buttons if "data-copy-supply-route" in button.attrs), None)
        if copy_button is None:
            issues.append(f"{path}: {slug} route missing copy button")
        else:
            stats["copy_buttons"] += 1
            issues.extend(validate_summary(path, slug, copy_button.attrs.get("data-route-summary", "")))

    affiliate_cards = find_all(root, tag="article", class_name="affiliate-book-card")
    if len(affiliate_cards) != 4:
        issues.append(f"{path}: expected four affiliate book cards, got {len(affiliate_cards)}")
    for card in affiliate_cards:
        links = descendants(card, "a")
        book_links = [link for link in links if has_class(link, "affiliate-book-link")]
        route_tags = [link for link in links if has_class(link, "affiliate-route-tag")]
        if len(book_links) != 1:
            issues.append(f"{path}: affiliate book card should include one book CTA")
        elif not is_affiliate_url(book_links[0].attrs.get("href", "")):
            issues.append(f"{path}: affiliate book CTA should use tracked books.com.tw URL")
        else:
            stats["affiliate_book_cards"] += 1
        if not route_tags:
            issues.append(f"{path}: affiliate book card should show matching guardian route tags")
        stats["route_tags"] += len(route_tags)
        for tag in route_tags:
            if not tag.attrs.get("href", "").startswith("#supply-"):
                issues.append(f"{path}: affiliate route tag should point to supply anchor")

    wishlist_cards = find_all(root, tag="article", attr="data-supply-owned-card")
    if len(wishlist_cards) != len(GUARDIAN_SLUGS):
        issues.append(f"{path}: expected five owned supply wishlist cards, got {len(wishlist_cards)}")
    for card in wishlist_cards:
        stats["wishlist_cards"] += 1
        card_text = text_content(card)
        for expected_format in expected_formats:
            if expected_format not in card_text:
                issues.append(f"{path}: wishlist card missing format {expected_format!r}")
            else:
                stats["wishlist_formats"] += 1
        contact_links = [
            link
            for link in descendants(card, "a")
            if link.attrs.get("href", "").startswith("mailto:contact@lovetypes.tw")
            or link.attrs.get("href", "").startswith("/cdn-cgi/l/email-protection")
        ]
        if len(contact_links) != 1:
            issues.append(f"{path}: wishlist card should include one contact mailto or protected email link")
            continue
        stats["wishlist_mailtos"] += 1
        href = contact_links[0].attrs["href"]
        query = parse_qs(urlparse(href).query)
        if href.startswith("mailto:") and (not query.get("subject") or not query.get("body")):
            issues.append(f"{path}: wishlist mailto should include subject and body")
        if href.startswith("mailto:"):
            body_text = "\n".join(query.get("body", []))
            for expected_format in expected_formats:
                if expected_format not in body_text:
                    issues.append(f"{path}: wishlist mailto body missing format {expected_format!r}")
        copy_buttons = [button for button in descendants(card, "button") if "data-copy-contact-template" in button.attrs]
        if len(copy_buttons) != 1:
            issues.append(f"{path}: wishlist card should include one copy template button")
        elif not copy_buttons[0].attrs.get("data-copy-text"):
            issues.append(f"{path}: wishlist copy template button missing data-copy-text")
        else:
            copy_text = copy_buttons[0].attrs["data-copy-text"]
            for expected_format in expected_formats:
                if expected_format not in copy_text:
                    issues.append(f"{path}: wishlist copy template missing format {expected_format!r}")
            stats["wishlist_copy_buttons"] += 1

    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes guardian supply routes and affiliate conversion safety.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    generator = load_generator_config()
    issues: list[str] = []
    totals = {
        "pages": 0,
        "quick_cards": 0,
        "route_cards": 0,
        "guide_links": 0,
        "luna_links": 0,
        "route_request_mailtos": 0,
        "route_product_stacks": 0,
        "route_product_links": 0,
        "copy_buttons": 0,
        "affiliate_links": 0,
        "affiliate_book_cards": 0,
        "route_tags": 0,
        "wishlist_cards": 0,
        "wishlist_formats": 0,
        "wishlist_mailtos": 0,
        "wishlist_copy_buttons": 0,
        "safety_sections": 0,
        "safety_bridge_sections": 0,
        "safety_bridge_links": 0,
        "decision_sections": 0,
        "decision_cards": 0,
        "decision_links": 0,
    }
    for lang, path in LANG_PATHS.items():
        page_issues, stats = validate_page(base_url, lang, path, generator.SUPPLY_WISHLIST[lang]["formats"])
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"public_supply_pages_checked={totals['pages']}")
    print(f"public_supply_quick_cards_checked={totals['quick_cards']}")
    print(f"public_supply_route_cards_checked={totals['route_cards']}")
    print(f"public_supply_guide_links_checked={totals['guide_links']}")
    print(f"public_supply_luna_links_checked={totals['luna_links']}")
    print(f"public_supply_route_request_mailtos_checked={totals['route_request_mailtos']}")
    print(f"public_supply_route_product_stacks_checked={totals['route_product_stacks']}")
    print(f"public_supply_route_product_links_checked={totals['route_product_links']}")
    print(f"public_supply_copy_buttons_checked={totals['copy_buttons']}")
    print(f"public_supply_affiliate_links_checked={totals['affiliate_links']}")
    print(f"public_supply_affiliate_book_cards_checked={totals['affiliate_book_cards']}")
    print(f"public_supply_affiliate_route_tags_checked={totals['route_tags']}")
    print(f"public_supply_wishlist_cards_checked={totals['wishlist_cards']}")
    print(f"public_supply_wishlist_formats_checked={totals['wishlist_formats']}")
    print(f"public_supply_wishlist_mailtos_checked={totals['wishlist_mailtos']}")
    print(f"public_supply_wishlist_copy_buttons_checked={totals['wishlist_copy_buttons']}")
    print(f"public_supply_safety_sections_checked={totals['safety_sections']}")
    print(f"public_supply_safety_bridge_sections_checked={totals['safety_bridge_sections']}")
    print(f"public_supply_safety_bridge_links_checked={totals['safety_bridge_links']}")
    print(f"public_supply_decision_sections_checked={totals['decision_sections']}")
    print(f"public_supply_decision_cards_checked={totals['decision_cards']}")
    print(f"public_supply_decision_links_checked={totals['decision_links']}")
    print(f"public_supply_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
