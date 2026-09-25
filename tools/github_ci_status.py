#!/usr/bin/env python3
"""Verify that the current LoveTypes commit has successful required GitHub checks."""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Arthur0858/love-language"
# Require the workflow that validates and deploys the allowlisted Cloudflare Pages build.
# GitHub Pages is a separate legacy redirect surface, not the production deployment signal.
REQUIRED_WORKFLOWS = ("LoveTypes build, deploy, and verify",)
RUN_RE = re.compile(
    rf'<a(?P<attrs_before>[^>]*?)href="/{re.escape(REPOSITORY)}/actions/runs/(?P<run_id>\d+)"'
    rf'(?P<attrs_after>[^>]*)>(?P<body>.*?)</a>',
    re.I | re.S,
)


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=30,
    )
    return result.stdout.strip()


def visible_text(raw: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def parse_workflows(raw: str) -> dict[str, dict[str, object]]:
    matches = list(RUN_RE.finditer(raw))
    workflows: dict[str, dict[str, object]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        block = raw[match.start() : end]
        body_match = re.search(r"<span>(.*?)</span>", match.group("body"), re.I | re.S)
        if body_match is None:
            continue
        name = visible_text(body_match.group(1))
        link_attributes = match.group("attrs_before") + match.group("attrs_after")
        run_label_match = re.search(r'aria-label="([^"]+)"', link_attributes, re.I)
        run_label = visible_text(run_label_match.group(1)).lower() if run_label_match else ""
        success_jobs = len(
            re.findall(r'aria-label="(?:This job succeeded|completed successfully:?)\s*"', block, re.I)
        )
        failed_jobs = len(
            re.findall(
                r'aria-label="(?:This job (?:failed|was cancelled|was skipped)|completed (?:with failure|cancelled|skipped):?)\s*"',
                block,
                re.I,
            )
        )
        visible_status_block = re.sub(r"<template\b[^>]*>.*?</template>", "", block, flags=re.I | re.S)
        active_status_marker = re.search(
            r'aria-label="(?:in progress|currently running|queued)(?::[^"]*)?"',
            visible_status_block,
            re.I,
        )
        pending = run_label.startswith(("currently running:", "queued:")) or active_status_marker is not None or (
            success_jobs == 0
            and any(marker in visible_status_block.lower() for marker in ("currently running", "queued"))
        )
        workflows[name] = {
            "runId": match.group("run_id"),
            "successJobs": success_jobs,
            "failedJobs": failed_jobs,
            "pending": pending,
            "succeeded": success_jobs > 0 and failed_jobs == 0 and not pending,
        }
    return workflows


def workflow_issues(workflows: dict[str, dict[str, object]]) -> list[str]:
    issues: list[str] = []
    for name in REQUIRED_WORKFLOWS:
        item = workflows.get(name)
        if item is None:
            issues.append(f"required GitHub workflow missing: {name}")
        elif item.get("pending") is True:
            issues.append(f"required GitHub workflow is still in progress: {name}")
        elif item.get("succeeded") is not True:
            issues.append(f"required GitHub workflow is not successful: {name}")
    return issues


def main() -> int:
    head = git_head()
    issues: list[str] = []
    workflows: dict[str, dict[str, object]] = {}
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        issues.append("current Git HEAD is unavailable")
    else:
        url = f"https://github.com/{REPOSITORY}/commit/{head}/checks"
        try:
            request = Request(url, headers={"User-Agent": "LoveTypes-final-review/1.0"})
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            issues.append(f"GitHub checks page unavailable: {exc}")
        else:
            workflows = parse_workflows(raw)
            issues.extend(workflow_issues(workflows))

    required = {name: workflows.get(name, {}) for name in REQUIRED_WORKFLOWS}
    print(f"github_ci_commit={head}")
    print(f"github_ci_workflows_required={len(REQUIRED_WORKFLOWS)}")
    print(f"github_ci_workflows_found={sum(bool(item) for item in required.values())}")
    print(f"github_ci_workflows_succeeded={sum(item.get('succeeded') is True for item in required.values())}")
    for name, item in required.items():
        key = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        print(f"github_ci_{key}_run_id={item.get('runId', '')}")
    print(f"github_ci_issues={len(issues)}")
    for issue in issues:
        print(f"- {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
