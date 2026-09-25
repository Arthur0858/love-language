#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = ".lovetypes-dist-manifest.json"
SPECIAL_FILES = ("_headers", "_redirects", "_routes.json", "_worker.js")


def load_deploy_module():
    path = ROOT / "tools" / "deploy_cloudflare_pages.py"
    spec = importlib.util.spec_from_file_location("lovetypes_dist_deploy", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load deployment manifest from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_generator_module():
    path = ROOT / "tools" / "generate_multilingual_site.py"
    spec = importlib.util.spec_from_file_location("lovetypes_dist_generator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load site generator from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_files() -> dict[str, Path]:
    deploy = load_deploy_module()
    files = {
        path.relative_to(ROOT).as_posix(): path
        for path in deploy.collect_manifest_paths(ROOT)
    }
    for relative in SPECIAL_FILES:
        source = ROOT / relative
        if not source.is_file():
            raise RuntimeError(f"Required Pages file missing: {relative}")
        files[relative] = source
    return dict(sorted(files.items()))


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source_surface(files: dict[str, Path]) -> None:
    deploy = load_deploy_module()
    generator = load_generator_module()
    html_paths = {path for path in files if path.endswith(".html")}
    if html_paths != deploy.REVIEW_HTML_PATHS:
        raise RuntimeError(
            "HTML allowlist mismatch: "
            f"missing={sorted(deploy.REVIEW_HTML_PATHS - html_paths)} "
            f"extra={sorted(html_paths - deploy.REVIEW_HTML_PATHS)}"
        )
    indexable = {
        f"{route.strip('/')}/index.html" if route.strip("/") else "index.html"
        for route in generator.site_index_paths()
    }
    lab = {f"lab/{report['slug']}/index.html" for report in generator.LAB_REPORTS}
    commercial = {f"{route.strip('/')}/index.html" for route in generator.NOINDEX_COMMERCIAL_PATHS}
    expected = indexable | lab | commercial | {"404.html"}
    if html_paths != expected:
        raise RuntimeError(
            f"Expected {len(expected)} HTML files ({len(indexable)} indexed, "
            f"{len(lab)} lab, {len(commercial)} commercial, 404), got {len(html_paths)}"
        )
    if len(indexable) != 30 or len(lab) != 8 or len(commercial) != 3:
        raise RuntimeError(
            f"Review surface counts changed: indexed={len(indexable)} lab={len(lab)} commercial={len(commercial)}"
        )
    for route in (*generator.NOINDEX_LAB_PATHS, *generator.NOINDEX_COMMERCIAL_PATHS):
        relative = f"{route.strip('/')}/index.html"
        raw = files[relative].read_text(encoding="utf-8")
        if '<meta name="robots" content="noindex, follow"' not in raw:
            raise RuntimeError(f"noindex meta missing: {route}")
        canonical = f'<link rel="canonical" href="https://lovetypes.tw{route}"'
        if canonical not in raw:
            raise RuntimeError(f"self-canonical missing: {route}")
    for retired in generator.RETIRED_PUBLIC_ASSET_PATHS:
        relative = retired.lstrip("/")
        if relative in files:
            raise RuntimeError(f"retired asset is present in dist: {relative}")


def inventory(directory: Path) -> set[str]:
    return {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != MARKER
    }


def verify_dist(dist: Path, files: dict[str, Path] | None = None) -> dict[str, int]:
    files = files or source_files()
    validate_source_surface(files)
    if not dist.is_dir():
        raise RuntimeError(f"Built output directory not found: {dist}")
    expected_paths = set(files)
    actual_paths = inventory(dist)
    if actual_paths != expected_paths:
        raise RuntimeError(
            "dist inventory mismatch: "
            f"missing={sorted(expected_paths - actual_paths)} extra={sorted(actual_paths - expected_paths)}"
        )
    for relative, source in files.items():
        output = dist / relative
        if file_digest(output) != file_digest(source):
            raise RuntimeError(f"dist file differs from allowlisted source: {relative}")
    html_paths = {path for path in expected_paths if path.endswith(".html")}
    return {
        "files": len(expected_paths),
        "html": len(html_paths),
        "indexable_html": 30,
        "noindex_lab_html": 8,
        "noindex_commercial_html": 3,
    }


def build_dist(dist: Path) -> dict[str, int]:
    files = source_files()
    validate_source_surface(files)
    marker_payload = {"managed_by": "tools/build_review_dist.py", "files": sorted(files)}
    stage = Path(tempfile.mkdtemp(prefix=".lovetypes-dist-stage-", dir=ROOT))
    backup: Path | None = None
    try:
        for relative, source in files.items():
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        (stage / MARKER).write_text(json.dumps(marker_payload, indent=2) + "\n", encoding="utf-8")
        if dist.exists():
            marker = dist / MARKER
            if not marker.is_file():
                raise RuntimeError(f"Refusing to replace unmanaged directory: {dist}")
            previous = json.loads(marker.read_text(encoding="utf-8"))
            if previous.get("managed_by") != marker_payload["managed_by"] or inventory(dist) != set(previous.get("files", [])):
                raise RuntimeError(f"Refusing to replace modified or unmanaged dist directory: {dist}")
            backup = ROOT / f".lovetypes-dist-backup-{uuid.uuid4().hex}"
            os.replace(dist, backup)
        try:
            os.replace(stage, dist)
        except Exception:
            if backup and backup.exists() and not dist.exists():
                os.replace(backup, dist)
            raise
        if backup:
            shutil.rmtree(backup)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return verify_dist(dist, files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the allowlisted Cloudflare Pages output into dist/.")
    parser.add_argument("--site-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        result = verify_dist(args.site_dir) if args.verify_only else build_dist(args.site_dir)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"review_dist_error={error}")
        return 1
    for name, value in result.items():
        print(f"review_dist_{name}={value}")
    print("review_dist_status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
