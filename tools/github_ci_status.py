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
# GitHub's native Pages deployment can be attached to the preceding source commit.
# Production deployment is verified separately by the Cloudflare evidence gate and public smokes.
REQUIRED_WORKFLOWS = ("LoveTypes predeploy check",)
RUN_RE = re.compile(
    rf'<a href="/{re.escape(REPOSITORY)}/actions/runs/(\d+)"[^>]*>.*?<span>(.*?)</span>',
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
        name = visible_text(match.group(2))
        success_jobs = block.count('aria-label="This job succeeded"')
        failed_jobs = len(re.findall(r'aria-label="This job (?:failed|was cancelled|was skipped)"', block, re.I))
        pending = "currently running" in block.lower() or "queued" in block.lower()
        workflows[name] = {
            "runId": match.group(1),
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
