#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "site-health.md"
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_:-]+)=(.*)$")


CHECKS = [
    ("predeploy", [sys.executable, "tools/predeploy_check.py"]),
    ("cloudflare_dry_run", [sys.executable, "tools/deploy_cloudflare_pages.py", "--dry-run"]),
    ("public_deploy_smoke", [sys.executable, "tools/public_deploy_smoke.py"]),
    ("public_sitemap_smoke", [sys.executable, "tools/public_sitemap_smoke.py"]),
]


def run(command: list[str], timeout: int = 180) -> tuple[int, str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return result.returncode, result.stdout


def git_value(*args: str) -> str:
    code, output = run(["git", *args], timeout=30)
    return output.strip() if code == 0 else ""


def parse_key_values(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in output.splitlines():
        match = KEY_VALUE_RE.match(line.strip())
        if match:
            values[match.group(1)] = match.group(2)
    return values


def check_status(code: int, values: dict[str, str]) -> str:
    if code != 0:
        return "failed"
    issue_keys = [key for key in values if key.endswith("issues") or key.endswith("_issues")]
    if any(values.get(key) not in {"0", ""} for key in issue_keys):
        return "issues"
    if values.get("predeploy_checks") == "ok":
        return "ok"
    return "ok"


def render_section(name: str, code: int, values: dict[str, str]) -> list[str]:
    status = check_status(code, values)
    lines = [f"## {name}", "", f"- status: `{status}`"]
    important_keys = [
        "predeploy_checks",
        "issues",
        "content_uniqueness_issues",
        "multilingual_route_issues",
        "guardian_conversion_issues",
        "accessibility_issues",
        "image_asset_issues",
        "performance_budget_issues",
        "deploy_manifest_issues",
        "public_deploy_issues",
        "public_sitemap_issues",
        "Remote missing hashes",
        "Commit dirty",
        "pages",
        "indexable_pages",
        "sitemap_urls",
        "sitemap_alternates",
        "affiliate_pages",
        "affiliate_links",
        "public_pages_checked",
        "public_external_links_checked",
        "public_affiliate_links_checked",
        "public_sitemap_pages_checked",
        "public_sitemap_hreflang_links_checked",
        "image_assets_checked",
        "priority_images_checked",
        "image_preloads_checked",
        "deploy_manifest_files",
    ]
    for key in important_keys:
        if key in values:
            lines.append(f"- {key}: `{values[key]}`")
    return lines


def parse_cloudflare_dry_run(output: str) -> dict[str, str]:
    values = parse_key_values(output)
    for line in output.splitlines():
        for label in ("Commit hash", "Commit message", "Commit dirty", "Static assets", "Remote missing hashes"):
            prefix = f"{label}: "
            if line.startswith(prefix):
                values[label] = line.removeprefix(prefix).strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a LoveTypes health summary from current checks.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown output path.")
    args = parser.parse_args()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    head = git_value("rev-parse", "--short", "HEAD")
    full_head = git_value("rev-parse", "HEAD")
    branch = git_value("status", "--short", "--branch").splitlines()[0]
    remote = git_value("ls-remote", "origin", "refs/heads/main").split()
    remote_sha = remote[0] if remote else ""

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sections: list[str] = [
        "# LoveTypes Site Health",
        "",
        f"- generated_at_utc: `{generated_at}`",
        f"- commit_short: `{head}`",
        f"- commit_full: `{full_head}`",
        f"- origin_main: `{remote_sha}`",
        f"- branch_status: `{branch}`",
        f"- production: `https://lovetypes.tw/`",
        f"- cloudflare_project: `lovetypes`",
        "",
    ]

    failed = False
    for name, command in CHECKS:
        code, output = run(command)
        if name == "cloudflare_dry_run":
            values = parse_cloudflare_dry_run(output)
        else:
            values = parse_key_values(output)
        sections.extend(render_section(name, code, values))
        sections.append("")
        if check_status(code, values) != "ok":
            failed = True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"site_health_output={output_path}")
    print(f"site_health_status={'failed' if failed else 'ok'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
