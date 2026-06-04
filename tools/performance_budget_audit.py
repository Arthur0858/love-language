#!/usr/bin/env python3
from __future__ import annotations

import gzip
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".github", ".wrangler", "__pycache__", "node_modules", "output"}
TEXT_SUFFIXES = {".css", ".html", ".js"}
RASTER_SUFFIXES = {".ico", ".jpg", ".jpeg", ".png", ".webp"}

MAX_TOTAL_STATIC_BYTES = 22 * 1024 * 1024
MAX_HTML_BYTES = 140 * 1024
MAX_HTML_GZIP_BYTES = 45 * 1024
MAX_CSS_BYTES = 110 * 1024
MAX_CSS_GZIP_BYTES = 24 * 1024
MAX_JS_BYTES = 40 * 1024
MAX_JS_GZIP_BYTES = 14 * 1024
MAX_IMAGE_BYTES = 360 * 1024
MAX_ROOT_ICON_BYTES = 320 * 1024


def site_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        files.append(path)
    return sorted(files)


def gzip_size(path: Path) -> int:
    data = path.read_bytes()
    return len(gzip.compress(data, compresslevel=9))


def budget_for(path: Path) -> tuple[int | None, int | None]:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return MAX_HTML_BYTES, MAX_HTML_GZIP_BYTES
    if suffix == ".css":
        return MAX_CSS_BYTES, MAX_CSS_GZIP_BYTES
    if suffix == ".js":
        return MAX_JS_BYTES, MAX_JS_GZIP_BYTES
    return None, None


def image_budget_for(path: Path) -> int:
    if path.name in {"apple-touch-icon.png", "icon-192.png", "icon-512.png"}:
        return MAX_ROOT_ICON_BYTES
    return MAX_IMAGE_BYTES


def main() -> int:
    files = site_files()
    issues: list[str] = []
    total_bytes = sum(path.stat().st_size for path in files)
    text_assets_checked = 0
    raster_assets_checked = 0

    if total_bytes > MAX_TOTAL_STATIC_BYTES:
        issues.append(f"static asset total exceeds budget: {total_bytes} > {MAX_TOTAL_STATIC_BYTES}")

    for path in files:
        relative = path.relative_to(ROOT)
        suffix = path.suffix.lower()
        size = path.stat().st_size
        max_size, max_gzip = budget_for(path)

        if suffix in TEXT_SUFFIXES:
            text_assets_checked += 1
            if max_size is not None and size > max_size:
                issues.append(f"{relative}: file size exceeds budget: {size} > {max_size}")
            if max_gzip is not None:
                compressed = gzip_size(path)
                if compressed > max_gzip:
                    issues.append(f"{relative}: gzip size exceeds budget: {compressed} > {max_gzip}")

        if suffix in RASTER_SUFFIXES:
            raster_assets_checked += 1
            max_image_size = image_budget_for(path)
            if size > max_image_size:
                issues.append(f"{relative}: image size exceeds budget: {size} > {max_image_size}")

    print(f"performance_files_checked={len(files)}")
    print(f"text_assets_checked={text_assets_checked}")
    print(f"raster_assets_checked={raster_assets_checked}")
    print(f"static_asset_bytes={total_bytes}")
    print(f"performance_budget_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
