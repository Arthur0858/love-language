#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://lovetypes.tw"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
ASSET_SUFFIXES = {
    ".css",
    ".ico",
    ".jpg",
    ".jpeg",
    ".js",
    ".png",
    ".svg",
    ".webmanifest",
    ".webp",
}
IMMUTABLE_PATH_RE = re.compile(
    r"^/(assets/|shared-[^/]+\.css$|site-interactions-[^/]+\.js$|deferred-external-[^/]+\.js$|quiz-data-[^/]+\.js$)"
)


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes = b""


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "link" and data.get("href"):
            rel = set(data.get("rel", "").lower().split())
            if rel.intersection({"stylesheet", "icon", "apple-touch-icon", "manifest", "preload"}):
                self.refs.append(data["href"])
        if tag == "script" and data.get("src"):
            self.refs.append(data["src"])
        if tag in {"img", "source"}:
            if data.get("src"):
                self.refs.append(data["src"])
            if data.get("srcset"):
                self.refs.extend(srcset_urls(data["srcset"]))
        if tag == "meta":
            prop = data.get("property", "").lower()
            name = data.get("name", "").lower()
            if prop in {"og:image", "og:image:secure_url"} and data.get("content"):
                self.refs.append(data["content"])
            if name == "twitter:image" and data.get("content"):
                self.refs.append(data["content"])


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") or DEFAULT_BASE_URL


def request_url(url: str, *, method: str = "GET", attempts: int = 3) -> Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, method=method, headers={"User-Agent": "LoveTypes public asset integrity smoke/1.0"})
            with urlopen(request, timeout=20) as raw:
                body = b"" if method == "HEAD" else raw.read()
                return Response(raw.geturl(), raw.status, {key.lower(): value for key, value in raw.headers.items()}, body)
        except HTTPError as error:
            body = b"" if method == "HEAD" else error.read()
            if method == "HEAD" and error.code in {405, 501}:
                return request_url(url, method="GET", attempts=attempts)
            return Response(error.geturl(), error.code, {key.lower(): value for key, value in error.headers.items()}, body)
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def srcset_urls(value: str) -> list[str]:
    urls: list[str] = []
    for candidate in value.split(","):
        part = candidate.strip().split()
        if part:
            urls.append(part[0])
    return urls


def sitemap_locations(base_url: str) -> tuple[list[str], list[str]]:
    response = request_url(urljoin(base_url + "/", "sitemap.xml"))
    if response.status != 200:
        return [], [f"/sitemap.xml: expected status 200, got {response.status}"]
    try:
        root = ET.fromstring(response.body)
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


def public_path(url: str) -> str:
    return urlparse(url).path or "/"


def asset_url(base_url: str, raw: str) -> str | None:
    if raw.startswith("data:") or raw.startswith("mailto:") or raw.startswith("#"):
        return None
    absolute = urljoin(base_url + "/", raw)
    parsed = urlparse(absolute)
    base_host = urlparse(base_url).netloc
    if parsed.scheme not in {"http", "https"} or parsed.netloc != base_host:
        return None
    suffix = "." + parsed.path.rsplit(".", 1)[-1].lower() if "." in parsed.path.rsplit("/", 1)[-1] else ""
    if suffix not in ASSET_SUFFIXES:
        return None
    return absolute


def content_type_ok(path: str, content_type: str) -> bool:
    content_type = content_type.split(";", 1)[0].strip().lower()
    suffix = "." + path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""
    if content_type == "text/html":
        return False
    if suffix == ".css":
        return content_type in {"text/css"}
    if suffix == ".js":
        return content_type in {"application/javascript", "text/javascript", "application/x-javascript"}
    if suffix == ".webmanifest":
        return content_type in {"application/manifest+json", "application/json", "application/octet-stream"}
    if suffix in {".jpg", ".jpeg"}:
        return content_type == "image/jpeg"
    if suffix == ".png":
        return content_type == "image/png"
    if suffix == ".webp":
        return content_type == "image/webp"
    if suffix == ".svg":
        return content_type in {"image/svg+xml", "application/octet-stream"}
    if suffix == ".ico":
        return content_type in {"image/x-icon", "image/vnd.microsoft.icon", "image/png", "application/octet-stream"}
    return bool(content_type)


def immutable_expected(path: str) -> bool:
    return bool(IMMUTABLE_PATH_RE.match(path.lstrip("/") if path.startswith("//") else path))


def check_asset(url: str) -> tuple[list[str], bool]:
    issues: list[str] = []
    response = request_url(url, method="HEAD")
    path = public_path(url)
    if response.status != 200:
        issues.append(f"{path}: expected status 200, got {response.status}")
        return issues, False
    content_type = response.headers.get("content-type", "")
    if not content_type_ok(path, content_type):
        issues.append(f"{path}: unexpected content-type {content_type!r}")
    immutable_checked = False
    if immutable_expected(path):
        immutable_checked = True
        cache_control = response.headers.get("cache-control", "")
        if "max-age=31536000" not in cache_control.lower() or "immutable" not in cache_control.lower():
            issues.append(f"{path}: immutable cache-control missing, got {cache_control!r}")
    return issues, immutable_checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that public LoveTypes asset references resolve correctly.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public deployment base URL.")
    args = parser.parse_args()
    base_url = normalize_base_url(args.base_url)

    locations, issues = sitemap_locations(base_url)
    pages_checked = 0
    asset_refs_seen = 0
    assets: set[str] = set()
    for loc in locations:
        response = request_url(loc)
        path = public_path(loc)
        if response.status != 200:
            issues.append(f"{path}: expected page status 200, got {response.status}")
            continue
        page_parser = AssetParser()
        page_parser.feed(response.body.decode("utf-8", errors="replace"))
        pages_checked += 1
        for raw in page_parser.refs:
            absolute = asset_url(base_url, raw)
            if absolute:
                asset_refs_seen += 1
                assets.add(absolute)

    immutable_assets_checked = 0
    for url in sorted(assets):
        asset_issues, immutable_checked = check_asset(url)
        issues.extend(asset_issues)
        immutable_assets_checked += 1 if immutable_checked else 0

    print(f"public_asset_pages_checked={pages_checked}")
    print(f"public_asset_refs_seen={asset_refs_seen}")
    print(f"public_asset_unique_assets_checked={len(assets)}")
    print(f"public_asset_immutable_assets_checked={immutable_assets_checked}")
    print(f"public_asset_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
