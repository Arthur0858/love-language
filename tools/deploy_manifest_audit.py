#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPLOY_SCRIPT = ROOT / "tools" / "deploy_cloudflare_pages.py"
GENERATOR_SCRIPT = ROOT / "tools" / "generate_multilingual_site.py"
BASE_REQUIRED_MANIFEST_FILES = {
    "index.html",
    "characters/iris/index.html",
    "resources/index.html",
    "repair-plan/index.html",
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
}
REQUIRED_SPECIAL_FILES = {"_headers", "_redirects"}
FORBIDDEN_PREFIXES = {
    ".git/",
    ".github/",
    ".wrangler/",
    "docs/",
    "node_modules/",
    "output/",
    "tools/",
}
FORBIDDEN_SUFFIXES = {".md", ".py", ".mjs", ".map"}
FORBIDDEN_FILES = {
    ".DS_Store",
    ".gitignore",
    "CLOUDFLARE_PAGES.md",
    "CNAME",
    "_headers",
    "_redirects",
}


def load_deploy_module():
    spec = importlib.util.spec_from_file_location("lovetypes_deploy_cloudflare_pages", DEPLOY_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load deploy script: {DEPLOY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_generator_module():
    spec = importlib.util.spec_from_file_location("lovetypes_generate_multilingual_site", GENERATOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator script: {GENERATOR_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def required_manifest_files() -> set[str]:
    generator = load_generator_module()
    return BASE_REQUIRED_MANIFEST_FILES | {
        generator.CSS_ASSET.lstrip("/"),
        generator.INTERACTIONS_ASSET.lstrip("/"),
        generator.AFFILIATE_ASSET.lstrip("/"),
    } | {asset.lstrip("/") for asset in generator.QUIZ_DATA_ASSETS.values()}


def main() -> int:
    deploy = load_deploy_module()
    required_files = required_manifest_files()
    manifest_paths = {
        path.relative_to(ROOT).as_posix()
        for path in deploy.collect_manifest_paths(ROOT)
    }
    issues: list[str] = []

    for rel_path in sorted(required_files):
        if rel_path not in manifest_paths:
            issues.append(f"missing required manifest file: {rel_path}")

    for rel_path in sorted(REQUIRED_SPECIAL_FILES):
        if not (ROOT / rel_path).exists():
            issues.append(f"missing required special deployment file: {rel_path}")
        if rel_path in manifest_paths:
            issues.append(f"special deployment file should not be in asset manifest: {rel_path}")

    for rel_path in sorted(manifest_paths):
        if rel_path in FORBIDDEN_FILES:
            issues.append(f"forbidden file in manifest: {rel_path}")
        if any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            issues.append(f"forbidden path in manifest: {rel_path}")
        if any(rel_path.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            issues.append(f"forbidden suffix in manifest: {rel_path}")

    print(f"deploy_manifest_files={len(manifest_paths)}")
    print(f"deploy_manifest_required_files={len(required_files)}")
    print(f"deploy_manifest_special_files={len(REQUIRED_SPECIAL_FILES)}")
    print(f"deploy_manifest_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
