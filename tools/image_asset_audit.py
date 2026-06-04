#!/usr/bin/env python3
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image


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
RASTER_SUFFIXES = {".ico", ".jpg", ".jpeg", ".png", ".webp"}


class ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []
        self.preloads: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "img":
            self.images.append(data)
        elif tag == "link" and data.get("rel") == "preload" and data.get("as") == "image":
            self.preloads.append(data)


def html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] in SKIP_DIRS:
            continue
        files.append(path)
    return sorted(files)


def local_asset_path(src: str, page: Path) -> Path | None:
    parsed = urlparse(src)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    if parsed.path.startswith("/"):
        return ROOT / parsed.path.lstrip("/")
    return (page.parent / parsed.path).resolve()


def parse_int(value: str) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def image_size(path: Path) -> tuple[int, int] | None:
    if path.suffix.lower() not in RASTER_SUFFIXES:
        return None
    with Image.open(path) as image:
        return image.size


def audit_page(path: Path) -> tuple[int, int, int, list[str]]:
    rel = path.relative_to(ROOT).as_posix()
    parser = ImageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    issues: list[str] = []
    images_checked = 0
    priority_images = 0
    preloads_checked = 0

    for image in parser.images:
        src = image.get("src", "")
        if not src:
            issues.append(f"{rel}: image missing src")
            continue
        asset = local_asset_path(src, path)
        if asset is None:
            continue
        images_checked += 1
        if not asset.exists():
            issues.append(f"{rel}: image asset missing: {src}")
            continue
        width = parse_int(image.get("width", ""))
        height = parse_int(image.get("height", ""))
        if width is None or height is None:
            issues.append(f"{rel}: image {src} missing positive width or height")
        else:
            actual = image_size(asset)
            if actual and actual != (width, height):
                issues.append(f"{rel}: image {src} dimensions {width}x{height} do not match file {actual[0]}x{actual[1]}")

        fetchpriority = image.get("fetchpriority", "")
        loading = image.get("loading", "")
        if fetchpriority == "high":
            priority_images += 1
            if loading != "eager":
                issues.append(f"{rel}: priority image {src} should use loading=eager")
            if image.get("decoding") != "async":
                issues.append(f"{rel}: priority image {src} should use decoding=async")
        elif loading == "eager" and image.get("decoding") != "async":
            issues.append(f"{rel}: eager image {src} should use decoding=async")

        if fetchpriority == "low" and loading != "lazy":
            issues.append(f"{rel}: low priority image {src} should use loading=lazy")

    for preload in parser.preloads:
        href = preload.get("href", "")
        asset = local_asset_path(href, path)
        if asset is None:
            continue
        preloads_checked += 1
        if not asset.exists():
            issues.append(f"{rel}: preload image asset missing: {href}")
        if preload.get("fetchpriority") == "high" and preload.get("as") != "image":
            issues.append(f"{rel}: high priority preload is not as=image: {href}")

    return images_checked, priority_images, preloads_checked, issues


def main() -> int:
    files = html_files()
    images_checked = 0
    priority_images = 0
    preloads_checked = 0
    issues: list[str] = []

    for path in files:
        page_images, page_priority, page_preloads, page_issues = audit_page(path)
        images_checked += page_images
        priority_images += page_priority
        preloads_checked += page_preloads
        issues.extend(page_issues)

    print(f"image_asset_pages_checked={len(files)}")
    print(f"image_assets_checked={images_checked}")
    print(f"priority_images_checked={priority_images}")
    print(f"image_preloads_checked={preloads_checked}")
    print(f"image_asset_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
