#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lovetypes.tw"
LOCAL_HOSTS = {"lovetypes.tw", "www.lovetypes.tw"}
EXPECTED_HREFLANGS = {"zh-TW", "en", "ja", "ko", "es", "x-default"}
SITEMAP_PATH = ROOT / "sitemap.xml"
ROBOTS_PATH = ROOT / "robots.txt"
SITEMAP_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []
        self.anchors: list[dict[str, str]] = []
        self.buttons: list[list[object]] = []
        self.controls: list[tuple[str, dict[str, str]]] = []
        self.images: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.ids: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.title_parts: list[str] = []
        self.jsonld_blocks: list[str] = []
        self.html_lang: str | None = None
        self._stack: list[tuple[str, dict[str, str], list[str]]] = []
        self._in_title = False
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        self._stack.append((tag, data, []))
        if tag == "html":
            self.html_lang = data.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "script" and data.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = []
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a":
            self.anchors.append(data)
        if tag == "button":
            self.buttons.append([data, ""])
        if tag in ("input", "select", "textarea"):
            self.controls.append((tag, data))
        if tag == "img":
            self.images.append(data)
        if tag == "link":
            self.links.append(data)
        if tag == "meta":
            self.metas.append(data)
        for attr in ("href", "src", "poster"):
            if attr in data:
                self.refs.append((tag, attr, data[attr]))
        if tag in ("img", "source") and "srcset" in data:
            self.refs.append((tag, "srcset", data["srcset"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self.jsonld_blocks.append("".join(self._jsonld_buf))
            self._in_jsonld = False
            self._jsonld_buf = []
        if not self._stack:
            return
        current_tag, data, text_parts = self._stack.pop()
        text = "".join(text_parts).strip()
        if current_tag == "button":
            for button in reversed(self.buttons):
                if button[0] is data:
                    button[1] = text
                    break
        if self._stack and text:
            self._stack[-1][2].append(text)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        if self._stack:
            self._stack[-1][2].append(data)

    def meta_content(self, name: str) -> str:
        for meta in self.metas:
            if meta.get("name") == name or meta.get("property") == name:
                return meta.get("content", "")
        return ""

    def links_with_rel(self, rel: str) -> list[dict[str, str]]:
        return [link for link in self.links if rel in link.get("rel", "").split()]


def html_pages() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)


def target_for(page: Path, value: str) -> tuple[Path | None, str]:
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        if parsed.netloc not in LOCAL_HOSTS:
            return None, parsed.fragment
        path = parsed.path or "/"
    else:
        if value.startswith("//"):
            return None, parsed.fragment
        path = parsed.path
    if path == "":
        target = page
    elif path.startswith("/"):
        clean = unquote(path.lstrip("/"))
        target = ROOT / "index.html" if clean == "" else ROOT / clean
    else:
        target = page.parent / unquote(path)
    if path.endswith("/") or path == "" or (not target.suffix and not target.exists()):
        if target.is_dir() or not target.suffix:
            target = target / "index.html"
    return target, parsed.fragment


def local_html_target_exists(page: Path, value: str, parsers: dict[Path, PageParser]) -> bool:
    target, fragment = target_for(page, value)
    if target is None:
        return True
    if not target.exists():
        return False
    if fragment and target.suffix == ".html":
        target_parser = parsers.get(target)
        return bool(target_parser and fragment in target_parser.ids)
    return True


def public_url_for_page(page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{DOMAIN}/"
    if rel.endswith("/index.html"):
        return f"{DOMAIN}/{rel[: -len('index.html')]}"
    return f"{DOMAIN}/{rel}"


def is_noindex(parser: PageParser) -> bool:
    return "noindex" in parser.meta_content("robots").lower()


def parse_sitemap(parsers: dict[Path, PageParser]) -> tuple[set[str], list[str], Counter]:
    issues: list[str] = []
    stats = Counter()
    if not SITEMAP_PATH.exists():
        return set(), [f"{SITEMAP_PATH}: missing sitemap.xml"], stats

    try:
        root = ET.parse(SITEMAP_PATH).getroot()
    except ET.ParseError as exc:
        return set(), [f"{SITEMAP_PATH}: invalid XML: {exc}"], stats

    if root.tag != f"{{{SITEMAP_NS['sm']}}}urlset":
        issues.append(f"{SITEMAP_PATH}: root element should be urlset")

    urls: set[str] = set()
    for url_node in root.findall("sm:url", SITEMAP_NS):
        loc_nodes = url_node.findall("sm:loc", SITEMAP_NS)
        if len(loc_nodes) != 1:
            issues.append(f"{SITEMAP_PATH}: expected one loc per url entry, found {len(loc_nodes)}")
            continue

        loc = (loc_nodes[0].text or "").strip()
        stats["sitemap_urls"] += 1
        parsed_loc = urlparse(loc)
        if parsed_loc.scheme != "https" or parsed_loc.netloc != "lovetypes.tw":
            issues.append(f"{SITEMAP_PATH}: loc must be absolute https lovetypes.tw URL: {loc}")
        if parsed_loc.fragment:
            issues.append(f"{SITEMAP_PATH}: loc should not contain fragment: {loc}")
        if loc in urls:
            issues.append(f"{SITEMAP_PATH}: duplicate loc: {loc}")
        urls.add(loc)

        target, _ = target_for(ROOT / "index.html", loc)
        if target is None or not target.exists():
            issues.append(f"{SITEMAP_PATH}: loc target missing: {loc}")

        if url_node.find("sm:lastmod", SITEMAP_NS) is None:
            issues.append(f"{SITEMAP_PATH}: missing lastmod for {loc}")
        if url_node.find("sm:changefreq", SITEMAP_NS) is None:
            issues.append(f"{SITEMAP_PATH}: missing changefreq for {loc}")
        priority_node = url_node.find("sm:priority", SITEMAP_NS)
        if priority_node is None:
            issues.append(f"{SITEMAP_PATH}: missing priority for {loc}")
        else:
            try:
                priority = float((priority_node.text or "").strip())
            except ValueError:
                issues.append(f"{SITEMAP_PATH}: invalid priority for {loc}")
            else:
                if not 0 <= priority <= 1:
                    issues.append(f"{SITEMAP_PATH}: priority out of range for {loc}")

        alternates = url_node.findall("xhtml:link", SITEMAP_NS)
        stats["sitemap_alternates"] += len(alternates)
        hreflang_map: dict[str, str] = {}
        for link in alternates:
            if link.attrib.get("rel") != "alternate":
                issues.append(f"{SITEMAP_PATH}: sitemap xhtml link must use rel=alternate for {loc}")
            hreflang = link.attrib.get("hreflang", "")
            href = link.attrib.get("href", "")
            if hreflang in hreflang_map:
                issues.append(f"{SITEMAP_PATH}: duplicate sitemap hreflang {hreflang} for {loc}")
            hreflang_map[hreflang] = href
            parsed_href = urlparse(href)
            if parsed_href.scheme != "https" or parsed_href.netloc != "lovetypes.tw":
                issues.append(f"{SITEMAP_PATH}: alternate href must be absolute https lovetypes.tw URL: {href}")
            href_target, _ = target_for(ROOT / "index.html", href)
            if href_target is None or not href_target.exists():
                issues.append(f"{SITEMAP_PATH}: alternate href target missing: {href}")
            elif href_target.suffix == ".html" and is_noindex(parsers.get(href_target, PageParser())):
                issues.append(f"{SITEMAP_PATH}: alternate href points to noindex page: {href}")

        missing_hreflangs = sorted(EXPECTED_HREFLANGS.difference(hreflang_map))
        extra_hreflangs = sorted(set(hreflang_map).difference(EXPECTED_HREFLANGS))
        if missing_hreflangs:
            issues.append(f"{SITEMAP_PATH}: missing sitemap hreflang alternates for {loc}: {', '.join(missing_hreflangs)}")
        if extra_hreflangs:
            issues.append(f"{SITEMAP_PATH}: unexpected sitemap hreflang alternates for {loc}: {', '.join(extra_hreflangs)}")
        if hreflang_map.get("x-default") and hreflang_map.get("zh-TW") and hreflang_map["x-default"] != hreflang_map["zh-TW"]:
            issues.append(f"{SITEMAP_PATH}: x-default sitemap alternate should match zh-TW for {loc}")

    return urls, issues, stats


def check_robots(sitemap_urls: set[str]) -> list[str]:
    issues: list[str] = []
    if not ROBOTS_PATH.exists():
        return [f"{ROBOTS_PATH}: missing robots.txt"]
    lines = [line.strip() for line in ROBOTS_PATH.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    lower_lines = [line.lower() for line in lines]
    if "user-agent: *" not in lower_lines:
        issues.append(f"{ROBOTS_PATH}: missing User-agent: *")
    if "allow: /" not in lower_lines:
        issues.append(f"{ROBOTS_PATH}: missing Allow: /")
    if "disallow: /" in lower_lines:
        issues.append(f"{ROBOTS_PATH}: should not globally disallow /")
    sitemap_line = f"Sitemap: {DOMAIN}/sitemap.xml"
    if sitemap_line not in lines:
        issues.append(f"{ROBOTS_PATH}: missing exact sitemap declaration {sitemap_line}")
    if not sitemap_urls:
        issues.append(f"{ROBOTS_PATH}: referenced sitemap has no URLs")
    return issues


def main() -> int:
    pages = html_pages()
    parsers: dict[Path, PageParser] = {}
    issues: list[str] = []
    stats = Counter()

    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        parsers[page] = parser

    for page, parser in parsers.items():
        stats["pages"] += 1
        stats["images"] += len(parser.images)
        stats["jsonld_blocks"] += len(parser.jsonld_blocks)
        if is_noindex(parser):
            stats["noindex_pages"] += 1
        else:
            stats["indexable_pages"] += 1

        if not "".join(parser.title_parts).strip():
            issues.append(f"{page}: missing <title>")
        if not parser.meta_content("description"):
            issues.append(f"{page}: missing meta description")
        if not parser.meta_content("robots"):
            issues.append(f"{page}: missing robots meta")
        if not parser.html_lang:
            issues.append(f"{page}: missing html lang")

        canonicals = parser.links_with_rel("canonical")
        stats["canonical_links"] += len(canonicals)
        if len(canonicals) != 1:
            issues.append(f"{page}: expected one canonical link, found {len(canonicals)}")
        else:
            canonical = canonicals[0].get("href", "")
            parsed_canonical = urlparse(canonical)
            if parsed_canonical.scheme != "https" or parsed_canonical.netloc != "lovetypes.tw":
                issues.append(f"{page}: canonical must be absolute https lovetypes.tw URL: {canonical}")
            if parsed_canonical.fragment:
                issues.append(f"{page}: canonical should not contain fragment: {canonical}")
            if not local_html_target_exists(page, canonical, parsers):
                issues.append(f"{page}: canonical target missing: {canonical}")
            if parser.meta_content("og:url") != canonical:
                issues.append(f"{page}: og:url does not match canonical")

        alternate_links = parser.links_with_rel("alternate")
        hreflang_links = [link for link in alternate_links if link.get("hreflang")]
        stats["hreflang_links"] += len(hreflang_links)
        hreflangs = [link.get("hreflang", "") for link in hreflang_links]
        missing_hreflangs = sorted(EXPECTED_HREFLANGS.difference(hreflangs))
        duplicate_hreflangs = [value for value, count in Counter(hreflangs).items() if count > 1]
        if missing_hreflangs:
            issues.append(f"{page}: missing hreflang alternates {', '.join(missing_hreflangs)}")
        if duplicate_hreflangs:
            issues.append(f"{page}: duplicate hreflang alternates {', '.join(duplicate_hreflangs)}")
        for link in hreflang_links:
            href = link.get("href", "")
            parsed_href = urlparse(href)
            if parsed_href.scheme != "https" or parsed_href.netloc != "lovetypes.tw":
                issues.append(f"{page}: hreflang must be absolute https lovetypes.tw URL: {href}")
            if not local_html_target_exists(page, href, parsers):
                issues.append(f"{page}: hreflang target missing: {href}")
        hreflang_map = {link.get("hreflang", ""): link.get("href", "") for link in hreflang_links}
        if hreflang_map.get("x-default") and hreflang_map.get("zh-TW") and hreflang_map["x-default"] != hreflang_map["zh-TW"]:
            issues.append(f"{page}: x-default hreflang should match zh-TW alternate")

        duplicate_ids = [value for value, count in Counter(parser.ids).items() if count > 1]
        if duplicate_ids:
            issues.append(f"{page}: duplicate ids {', '.join(duplicate_ids[:10])}")

        if not parser.jsonld_blocks:
            issues.append(f"{page}: missing JSON-LD")
        for block in parser.jsonld_blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                issues.append(f"{page}: invalid JSON-LD: {exc}")

        for image in parser.images:
            src = image.get("src", "")
            if "alt" not in image:
                issues.append(f"{page}: image missing alt: {src}")
            if not image.get("width") or not image.get("height"):
                issues.append(f"{page}: image missing width/height: {src}")
            if not image.get("decoding"):
                issues.append(f"{page}: image missing decoding: {src}")

        for attrs, text in parser.buttons:
            if not (str(text).strip() or attrs.get("aria-label") or attrs.get("title")):
                issues.append(f"{page}: button missing accessible name")

        for tag, attrs in parser.controls:
            input_type = attrs.get("type", "text")
            if input_type in ("hidden", "submit", "button"):
                continue
            if not (attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("placeholder")):
                issues.append(f"{page}: {tag} missing label hint")
            if tag == "textarea" and attrs.get("autocomplete") != "off":
                issues.append(f"{page}: textarea should use autocomplete=off")

        for anchor in parser.anchors:
            href = anchor.get("href", "")
            parsed = urlparse(href)
            if parsed.scheme in ("http", "https") and parsed.netloc not in LOCAL_HOSTS:
                stats["external_links"] += 1
                rel = set(anchor.get("rel", "").split())
                if anchor.get("target") == "_blank" and not {"noopener", "noreferrer"}.issubset(rel):
                    issues.append(f"{page}: external _blank link missing noopener/noreferrer: {href}")
                if "books.com.tw" in parsed.netloc and "sponsored" not in rel:
                    issues.append(f"{page}: affiliate link missing sponsored rel: {href}")

        for tag, attr, raw in parser.refs:
            values = [raw]
            if attr == "srcset":
                values = [part.strip().split()[0] for part in raw.split(",") if part.strip()]
            for value in values:
                if not value or value.startswith(("mailto:", "tel:", "javascript:", "data:")):
                    continue
                target, fragment = target_for(page, value)
                if target is None:
                    continue
                stats["internal_refs"] += 1
                if not target.exists():
                    issues.append(f"{page}: missing target for {value} -> {target}")
                    continue
                if fragment and target.suffix == ".html":
                    target_parser = parsers.get(target)
                    if target_parser and fragment not in target_parser.ids:
                        issues.append(f"{page}: missing anchor #{fragment} in {target}")

    sitemap_urls, sitemap_issues, sitemap_stats = parse_sitemap(parsers)
    issues.extend(sitemap_issues)
    stats.update(sitemap_stats)
    issues.extend(check_robots(sitemap_urls))

    indexable_canonicals: set[str] = set()
    for page, parser in parsers.items():
        canonicals = parser.links_with_rel("canonical")
        if len(canonicals) == 1 and not is_noindex(parser):
            indexable_canonicals.add(canonicals[0].get("href", ""))
        if is_noindex(parser) and public_url_for_page(page) in sitemap_urls:
            issues.append(f"{SITEMAP_PATH}: noindex page should not be listed: {public_url_for_page(page)}")

    missing_sitemap_urls = sorted(indexable_canonicals.difference(sitemap_urls))
    unexpected_sitemap_urls = sorted(sitemap_urls.difference(indexable_canonicals))
    for url in missing_sitemap_urls[:50]:
        issues.append(f"{SITEMAP_PATH}: indexable canonical missing from sitemap: {url}")
    if len(missing_sitemap_urls) > 50:
        issues.append(f"{SITEMAP_PATH}: {len(missing_sitemap_urls) - 50} more indexable canonical URL(s) missing from sitemap")
    for url in unexpected_sitemap_urls[:50]:
        issues.append(f"{SITEMAP_PATH}: sitemap URL is not an indexable canonical: {url}")
    if len(unexpected_sitemap_urls) > 50:
        issues.append(f"{SITEMAP_PATH}: {len(unexpected_sitemap_urls) - 50} more unexpected sitemap URL(s)")

    print(f"pages={stats['pages']}")
    print(f"indexable_pages={stats['indexable_pages']}")
    print(f"noindex_pages={stats['noindex_pages']}")
    print(f"images={stats['images']}")
    print(f"jsonld_blocks={stats['jsonld_blocks']}")
    print(f"canonical_links={stats['canonical_links']}")
    print(f"hreflang_links={stats['hreflang_links']}")
    print(f"sitemap_urls={stats['sitemap_urls']}")
    print(f"sitemap_alternates={stats['sitemap_alternates']}")
    print(f"internal_refs={stats['internal_refs']}")
    print(f"external_links={stats['external_links']}")
    print(f"issues={len(issues)}")
    for issue in issues[:200]:
        print(issue)
    if len(issues) > 200:
        print(f"... {len(issues) - 200} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
