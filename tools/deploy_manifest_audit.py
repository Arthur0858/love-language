#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import json
import sys
from urllib.parse import urlparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPLOY_SCRIPT = ROOT / "tools" / "deploy_cloudflare_pages.py"
GENERATOR_SCRIPT = ROOT / "tools" / "generate_multilingual_site.py"
RELEASE_PATH = ROOT / "release.json"
SITE_HEALTH_PATH = ROOT / "site-health.json"
BASE_REQUIRED_MANIFEST_FILES = {
    "index.html",
    "start/index.html",
    "characters/iris/index.html",
    "resources/index.html",
    "repair-plan/index.html",
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
    "humans.txt",
    "funnel-events.json",
    "commerce-catalog.json",
    "site-index.json",
    "guardian-profiles.json",
    "safety-index.json",
    "ai-discovery.json",
    "site-health.json",
    "release.json",
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
PUBLIC_TOOL_HTML_PATHS = {
    "tools/love-compatibility/index.html",
    "en/tools/love-compatibility/index.html",
    "es/tools/love-compatibility/index.html",
    "ja/tools/love-compatibility/index.html",
    "ko/tools/love-compatibility/index.html",
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
    return BASE_REQUIRED_MANIFEST_FILES | declared_index_and_support_files() | {
        generator.CSS_ASSET.lstrip("/"),
        generator.INTERACTIONS_ASSET.lstrip("/"),
        generator.AFFILIATE_ASSET.lstrip("/"),
    } | {asset.lstrip("/") for asset in generator.QUIZ_DATA_ASSETS.values()} | PUBLIC_TOOL_HTML_PATHS


def declared_index_and_support_files() -> set[str]:
    required: set[str] = set()
    release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    site_health = json.loads(SITE_HEALTH_PATH.read_text(encoding="utf-8"))
    indexes = release.get("publicIndexes") if isinstance(release, dict) else None
    if isinstance(indexes, dict):
        for value in indexes.values():
            if not isinstance(value, str):
                continue
            parsed = urlparse(value)
            if parsed.netloc == "lovetypes.tw" and parsed.path:
                required.add(parsed.path.lstrip("/"))
    support_files = site_health.get("supportFiles") if isinstance(site_health, dict) else None
    if isinstance(support_files, list):
        required.update(value for value in support_files if isinstance(value, str) and value)
    return required


def deployment_special_upload_files() -> set[str]:
    tree = ast.parse(DEPLOY_SCRIPT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "create_deployment":
            return {
                constant.value
                for constant in ast.walk(node)
                if isinstance(constant, ast.Constant)
                and isinstance(constant.value, str)
                and constant.value in REQUIRED_SPECIAL_FILES
            }
    return set()


def main() -> int:
    deploy = load_deploy_module()
    required_files = required_manifest_files()
    declared_files = declared_index_and_support_files()
    special_upload_files = deployment_special_upload_files()
    manifest_paths = {
        path.relative_to(ROOT).as_posix()
        for path in deploy.collect_manifest_paths(ROOT)
    }
    issues: list[str] = []

    missing_declared_required_files = sorted(declared_files.difference(required_files))
    if missing_declared_required_files:
        issues.append(
            "required manifest files drift from release/site-health declarations: "
            f"missing={missing_declared_required_files}"
        )

    for rel_path in sorted(required_files):
        if rel_path not in manifest_paths:
            issues.append(f"missing required manifest file: {rel_path}")

    for rel_path in sorted(REQUIRED_SPECIAL_FILES):
        if not (ROOT / rel_path).exists():
            issues.append(f"missing required special deployment file: {rel_path}")
        if rel_path in manifest_paths:
            issues.append(f"special deployment file should not be in asset manifest: {rel_path}")

    missing_special_upload_files = sorted(REQUIRED_SPECIAL_FILES.difference(special_upload_files))
    if missing_special_upload_files:
        issues.append(
            "required special deployment files missing from deploy upload logic: "
            f"{', '.join(missing_special_upload_files)}"
        )

    for rel_path in sorted(manifest_paths):
        if rel_path in FORBIDDEN_FILES:
            issues.append(f"forbidden file in manifest: {rel_path}")
        if any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES) and rel_path not in PUBLIC_TOOL_HTML_PATHS:
            issues.append(f"forbidden path in manifest: {rel_path}")
        if any(rel_path.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            issues.append(f"forbidden suffix in manifest: {rel_path}")

    print(f"deploy_manifest_files={len(manifest_paths)}")
    print(f"deploy_manifest_required_files={len(required_files)}")
    print(f"deploy_manifest_declared_files={len(declared_files)}")
    print(f"deploy_manifest_missing_declared_required_files={len(missing_declared_required_files)}")
    print(f"deploy_manifest_special_files={len(REQUIRED_SPECIAL_FILES)}")
    print(f"deploy_manifest_special_upload_files={len(special_upload_files)}")
    print(f"deploy_manifest_issues={len(issues)}")
    for issue in issues[:100]:
        print(issue)
    if len(issues) > 100:
        print(f"... {len(issues) - 100} more issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
