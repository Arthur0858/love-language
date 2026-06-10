#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


DEFAULT_BASE_URL = "https://lovetypes.tw"
LANG_PATHS = {
    "zh": "/luna-yoga-music/",
    "en": "/en/luna-yoga-music/",
    "ja": "/ja/luna-yoga-music/",
    "ko": "/ko/luna-yoga-music/",
    "es": "/es/luna-yoga-music/",
}
ALIAS_PATHS = {
    "zh": ("/luna/", "/luna-yoga-music/"),
    "en": ("/en/luna/", "/en/luna-yoga-music/"),
    "ja": ("/ja/luna/", "/ja/luna-yoga-music/"),
    "ko": ("/ko/luna/", "/ko/luna-yoga-music/"),
    "es": ("/es/luna/", "/es/luna-yoga-music/"),
}
GUARDIAN_SLUGS = ("iris", "noah", "vivian", "claire", "dora")
YOUTUBE_CHANNEL = "https://www.youtube.com/channel/UCPeQjvN9q2kY2s09PuRSL6w"


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict[str, str]
    text: str


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    text: str = ""
    children: list["Element"] = field(default_factory=list)


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001,N802
        return None


class LunaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root = Element("root", {})
        self.stack = [self.root]
        self.robots = ""
        self.canonical = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "meta" and data.get("name", "").lower() == "robots":
            self.robots = data.get("content", "")
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href", "")
        element = Element(tag, data)
        self.stack[-1].children.append(element)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
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


def request_url(url: str, *, follow_redirects: bool = True, attempts: int = 3) -> Response:
    opener = build_opener() if follow_redirects else build_opener(NoRedirectHandler)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes public Luna smoke/1.0"})
            with opener.open(request, timeout=20) as raw:
                return Response(
                    raw.geturl(),
                    raw.status,
                    {key.lower(): value for key, value in raw.headers.items()},
                    raw.read().decode("utf-8", errors="replace"),
                )
        except HTTPError as error:
            return Response(
                error.geturl(),
                error.code,
                {key.lower(): value for key, value in error.headers.items()},
                error.read().decode("utf-8", errors="replace"),
            )
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


def validate_aliases(base_url: str) -> tuple[list[str], int]:
    issues: list[str] = []
    checked = 0
    for lang, (alias, target) in ALIAS_PATHS.items():
        response = request_url(urljoin(base_url + "/", alias.lstrip("/")), follow_redirects=False)
        checked += 1
        if response.status != 301:
            issues.append(f"{alias}: expected 301 redirect, got {response.status}")
            continue
        location = response.headers.get("location", "")
        if location != target:
            issues.append(f"{alias}: expected redirect to {target}, got {location!r}")
    return issues, checked


def validate_page(base_url: str, lang: str, path: str) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "pages": 0,
        "protocol_cards": 0,
        "use_cases": 0,
        "offer_cards": 0,
        "guardian_cards": 0,
        "guardian_repair_links": 0,
        "guardian_supply_links": 0,
        "hero_ctas": 0,
        "offer_ctas": 0,
        "resume_templates": 0,
        "use_case_ctas": 0,
    }
    response = request_url(urljoin(base_url + "/", path.lstrip("/")))
    if response.status != 200:
        return [f"{path}: expected status 200, got {response.status}"], stats
    stats["pages"] = 1
    parser = LunaParser()
    parser.feed(response.text)
    root = parser.root
    robots_tokens = {token.strip().lower() for token in parser.robots.split(",") if token.strip()}
    if {"index", "follow"}.difference(robots_tokens) or "noindex" in robots_tokens:
        issues.append(f"{path}: formal Luna page should be index/follow, got {parser.robots!r}")
    expected_canonical = base_url + localized_path(lang, "luna-yoga-music")
    if parser.canonical != expected_canonical:
        issues.append(f"{path}: canonical should be {expected_canonical}, got {parser.canonical!r}")

    if "data-luna-saved" not in response.text or "luna-resume-card" not in response.text:
        issues.append(f"{path}: missing Luna saved result resume template")
    else:
        stats["resume_templates"] += 1

    protocol_cards = find_all(root, tag="article")
    protocol_section = next((item for item in walk(root) if has_class(item, "luna-night-protocol")), None)
    if protocol_section is None:
        issues.append(f"{path}: missing Luna night protocol section")
    else:
        protocol_items = descendants(protocol_section, "article")
        stats["protocol_cards"] += len(protocol_items)
        if len(protocol_items) != 3:
            issues.append(f"{path}: expected three Luna protocol cards, got {len(protocol_items)}")
        protocol_hrefs = [link.attrs.get("href", "") for link in descendants(protocol_section, "a")]
        for expected in (localized_path(lang, "repair-plan"), localized_path(lang, "guides/repair-after-conflict"), localized_path(lang, "resources")):
            if expected not in protocol_hrefs:
                issues.append(f"{path}: Luna protocol missing {expected} action")

    use_section = next((item for item in walk(root) if has_class(item, "luna-use-cases")), None)
    if use_section is None:
        issues.append(f"{path}: missing Luna use cases section")
    else:
        use_items = descendants(use_section, "article")
        stats["use_cases"] += len(use_items)
        if len(use_items) != 4:
            issues.append(f"{path}: expected four Luna use cases, got {len(use_items)}")
        use_hrefs = [link.attrs.get("href", "") for link in descendants(use_section, "a")]
        for expected in (
            localized_path(lang, "repair-plan"),
            localized_path(lang, "guides/repair-after-conflict"),
            localized_path(lang, "resources"),
            localized_path(lang, "") + "#quiz-section",
        ):
            if expected not in use_hrefs:
                issues.append(f"{path}: Luna use cases missing CTA {expected}")
            else:
                stats["use_case_ctas"] += 1

    offer_section = next((item for item in walk(root) if has_class(item, "luna-offer-section")), None)
    if offer_section is None:
        issues.append(f"{path}: missing Luna offer section")
    else:
        offer_items = descendants(offer_section, "article")
        stats["offer_cards"] += len(offer_items)
        if len(offer_items) != 3:
            issues.append(f"{path}: expected three Luna offer cards, got {len(offer_items)}")
        offer_hrefs = [link.attrs.get("href", "") for link in descendants(offer_section, "a")]
        for expected in (YOUTUBE_CHANNEL, localized_path(lang, "resources"), localized_path(lang, "contact") + "#luna-supply-request"):
            if expected not in offer_hrefs:
                issues.append(f"{path}: Luna offer missing CTA {expected}")
            else:
                stats["offer_ctas"] += 1

    hero_hrefs = [link.attrs.get("href", "") for link in find_all(root, tag="a")]
    for expected in (YOUTUBE_CHANNEL, localized_path(lang, "resources"), localized_path(lang, "guides/repair-after-conflict")):
        if expected not in hero_hrefs:
            issues.append(f"{path}: Luna hero missing CTA {expected}")
        else:
            stats["hero_ctas"] += 1

    for slug in GUARDIAN_SLUGS:
        card = find_by_id(root, f"luna-{slug}")
        if card is None:
            issues.append(f"{path}: missing #luna-{slug} guardian night card")
            continue
        if not has_class(card, "luna-guardian-card"):
            issues.append(f"{path}: #luna-{slug} should be luna-guardian-card")
        stats["guardian_cards"] += 1
        hrefs = [link.attrs.get("href", "") for link in descendants(card, "a")]
        repair = localized_path(lang, "repair-plan") + f"#plan-{slug}"
        supply = localized_path(lang, "resources") + f"#supply-{slug}"
        if repair in hrefs:
            stats["guardian_repair_links"] += 1
        else:
            issues.append(f"{path}: {slug} Luna card missing repair plan link")
        if supply in hrefs:
            stats["guardian_supply_links"] += 1
        else:
            issues.append(f"{path}: {slug} Luna card missing supply route link")

    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public LoveTypes Luna page positioning, guardian routes, and alias redirects.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)
    issues, alias_redirects_checked = validate_aliases(base_url)
    totals = {
        "pages": 0,
        "protocol_cards": 0,
        "use_cases": 0,
        "offer_cards": 0,
        "guardian_cards": 0,
        "guardian_repair_links": 0,
        "guardian_supply_links": 0,
        "hero_ctas": 0,
        "offer_ctas": 0,
        "resume_templates": 0,
        "use_case_ctas": 0,
    }
    for lang, path in LANG_PATHS.items():
        page_issues, stats = validate_page(base_url, lang, path)
        issues.extend(page_issues)
        for key, value in stats.items():
            totals[key] += value

    print(f"public_luna_pages_checked={totals['pages']}")
    print(f"public_luna_alias_redirects_checked={alias_redirects_checked}")
    print(f"public_luna_protocol_cards_checked={totals['protocol_cards']}")
    print(f"public_luna_use_cases_checked={totals['use_cases']}")
    print(f"public_luna_offer_cards_checked={totals['offer_cards']}")
    print(f"public_luna_guardian_cards_checked={totals['guardian_cards']}")
    print(f"public_luna_guardian_repair_links_checked={totals['guardian_repair_links']}")
    print(f"public_luna_guardian_supply_links_checked={totals['guardian_supply_links']}")
    print(f"public_luna_hero_ctas_checked={totals['hero_ctas']}")
    print(f"public_luna_offer_ctas_checked={totals['offer_ctas']}")
    print(f"public_luna_use_case_ctas_checked={totals['use_case_ctas']}")
    print(f"public_luna_resume_templates_checked={totals['resume_templates']}")
    print(f"public_luna_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
