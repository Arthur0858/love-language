#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import json
import re
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
    "lab/index.html",
    "lab/quiz-scoring-test/index.html",
    "repair-plan/index.html",
    "robots.txt",
    "sitemap.xml",
    "feed.xml",
    "site.webmanifest",
    "llms.txt",
    "humans.txt",
    "security.txt",
    "ads.txt",
    "site-index.json",
    "guardian-profiles.json",
    "safety-index.json",
    "ai-discovery.json",
    "commerce-catalog.json",
    "promotion-kit.json",
    "release.json",
    "search-indexing.json",
    "site-health.json",
}
REQUIRED_SPECIAL_FILES = {"_headers", "_redirects", "_routes.json", "_worker.js"}
FORBIDDEN_PREFIXES = {
    ".git/",
    ".github/",
    ".wrangler/",
    "config/",
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
    "_routes.json",
    "_worker.js",
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
    deploy = load_deploy_module()
    return BASE_REQUIRED_MANIFEST_FILES | {
        generator.CSS_ASSET.lstrip("/"),
        generator.INTERACTIONS_ASSET.lstrip("/"),
    } | {generator.QUIZ_DATA_ASSETS["zh"].lstrip("/")} | deploy.PUBLIC_TOOL_HTML_PATHS


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
    generator = load_generator_module()
    required_files = required_manifest_files()
    special_upload_files = deployment_special_upload_files()
    manifest_paths = {
        path.relative_to(ROOT).as_posix()
        for path in deploy.collect_manifest_paths(ROOT)
    }
    issues: list[str] = []
    manifest_html = {path for path in manifest_paths if path.endswith(".html")}
    expected_html = deploy.REVIEW_HTML_PATHS
    if manifest_html != expected_html:
        issues.append(
            "review HTML allowlist drift: "
            f"missing={sorted(expected_html-manifest_html)} extra={sorted(manifest_html-expected_html)}"
        )

    missing_public_support = sorted(set(deploy.PUBLIC_SUPPORT_FILES) - required_files)
    if missing_public_support:
        issues.append(f"public support allowlist missing from required manifest files: {missing_public_support}")

    expected_neutral_assets = {
        generator.CSS_ASSET.lstrip("/"),
        generator.INTERACTIONS_ASSET.lstrip("/"),
        generator.QUIZ_DATA_ASSETS["zh"].lstrip("/"),
        generator.COMPASS_TOOL_ASSET.lstrip("/"),
    }
    missing_neutral_assets = sorted(expected_neutral_assets.difference(manifest_paths))
    if missing_neutral_assets:
        issues.append(f"neutral product assets missing from deploy manifest: {missing_neutral_assets}")
    internal_version_assets = sorted(
        path
        for path in manifest_paths
        if any(
            term in path.lower()
            for term in ("review-surface", "compass-tool-review", "funnel-kpi", "quiz-metrics")
        )
    )
    if internal_version_assets:
        issues.append(f"internal review version assets leaked into deploy manifest: {internal_version_assets}")

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

    routes = json.loads((ROOT / "_routes.json").read_text(encoding="utf-8"))
    expected_route_includes = {"/tools/love-compatibility*"} | {
        f"/tools/{slug}*"
        for slug in generator.LONG_TAIL_COMPATIBILITY_PAGES
    } | {
        f"/guides/{slug}*"
        for slug, _title, _desc, _target in generator.LEGACY_ZH_GUIDES
    } | {
        f"{path.rstrip('/')}*"
        for path in generator.COMMERCIAL_RETIRED_PATHS
    } | set(generator.RETIRED_PUBLIC_ASSET_PATHS)
    if routes.get("version") != 1 or set(routes.get("include", [])) != expected_route_includes or routes.get("exclude") != []:
        issues.append("Pages Function route allowlist does not match retired review paths")

    worker = (ROOT / "_worker.js").read_text(encoding="utf-8")
    expected_retired_paths = {
        *(f"/tools/{slug}/" for slug in generator.LONG_TAIL_COMPATIBILITY_PAGES),
        *(f"/guides/{slug}/" for slug, _title, _desc, _target in generator.LEGACY_ZH_GUIDES),
        *generator.COMMERCIAL_RETIRED_PATHS,
    }
    missing_worker_paths = sorted(path for path in expected_retired_paths if json.dumps(path) not in worker)
    if missing_worker_paths:
        issues.append(f"retired paths missing from Pages Function: {missing_worker_paths}")
    missing_worker_assets = sorted(
        path for path in generator.RETIRED_PUBLIC_ASSET_PATHS if json.dumps(path) not in worker
    )
    if missing_worker_assets:
        issues.append(f"retired assets missing from Pages Function: {missing_worker_assets}")
    for required_worker_signal in ('status: 410', '"X-Robots-Tag": "noindex, nofollow"', 'path === "/tools/love-compatibility/"', '301'):
        if required_worker_signal not in worker:
            issues.append(f"Pages Function missing required behavior: {required_worker_signal}")

    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    missing_noindex_support_headers = sorted(
        path
        for path in (*generator.NOINDEX_SUPPORT_PATHS, *generator.NOINDEX_LAB_PATHS)
        if not re.search(
            rf"(?m)^{re.escape(path)}\n(?:  .+\n)*  X-Robots-Tag: noindex, follow$",
            headers,
        )
    )
    if missing_noindex_support_headers:
        issues.append(f"public support noindex headers missing: {missing_noindex_support_headers}")

    for rel_path in sorted(manifest_paths):
        if rel_path in FORBIDDEN_FILES:
            issues.append(f"forbidden file in manifest: {rel_path}")
        if any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES) and rel_path not in deploy.PUBLIC_TOOL_HTML_PATHS:
            issues.append(f"forbidden path in manifest: {rel_path}")
        if any(rel_path.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            issues.append(f"forbidden suffix in manifest: {rel_path}")

    print(f"deploy_manifest_files={len(manifest_paths)}")
    print(f"deploy_manifest_required_files={len(required_files)}")
    print(f"deploy_manifest_public_support_files={len(deploy.PUBLIC_SUPPORT_FILES)}")
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
