#!/usr/bin/env python3
"""Build a read-only, fail-closed AdSense final-review evidence packet."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "adsense-final-review-packet.json"
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_:-]+)=(.*)$")


@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: tuple[str, ...]
    timeout: int
    environment: dict[str, str] = field(default_factory=dict)
    visual: bool = False


CHECKS = (
    CheckSpec("submission_gate", (sys.executable, "tools/adsense_submission_gate.py"), 30),
    CheckSpec("github_ci", (sys.executable, "tools/github_ci_status.py"), 60),
    CheckSpec("local_review_surface", (sys.executable, "tools/predeploy_check.py", "--site-only"), 300),
    CheckSpec("public_review_surface", (sys.executable, "tools/public_adsense_review_smoke.py"), 300),
    CheckSpec("public_support_sync", (sys.executable, "tools/public_support_sync_smoke.py"), 240),
    CheckSpec("public_editorial_trust", (sys.executable, "tools/public_editorial_trust_smoke.py"), 240),
    CheckSpec(
        "public_indexability",
        (sys.executable, "tools/public_indexability_smoke.py", "--base-url", "https://lovetypes.tw"),
        240,
    ),
    CheckSpec(
        "public_headers",
        (sys.executable, "tools/public_headers_smoke.py", "--base-url", "https://lovetypes.tw"),
        180,
    ),
    CheckSpec(
        "public_assets",
        (sys.executable, "tools/public_asset_integrity_smoke.py", "--base-url", "https://lovetypes.tw"),
        240,
    ),
    CheckSpec(
        "public_internal_links",
        (sys.executable, "tools/public_internal_link_smoke.py", "--base-url", "https://lovetypes.tw"),
        300,
    ),
    CheckSpec(
        "public_editorial_link_graph",
        (sys.executable, "tools/public_editorial_link_graph_smoke.py", "--base-url", "https://lovetypes.tw"),
        300,
    ),
    CheckSpec(
        "public_metadata",
        (sys.executable, "tools/public_metadata_smoke.py", "--base-url", "https://lovetypes.tw"),
        300,
    ),
    CheckSpec(
        "public_schema",
        (sys.executable, "tools/public_schema_smoke.py", "--base-url", "https://lovetypes.tw"),
        240,
    ),
    CheckSpec(
        "public_schema_urls",
        (sys.executable, "tools/public_schema_url_smoke.py", "--base-url", "https://lovetypes.tw"),
        300,
    ),
    CheckSpec(
        "public_external_links",
        (sys.executable, "tools/public_external_link_smoke.py", "--base-url", "https://lovetypes.tw"),
        240,
    ),
    CheckSpec(
        "public_runtime_performance",
        ("node", "tools/runtime_performance_smoke.mjs"),
        240,
        {"BASE_URL": "https://lovetypes.tw", "PERFORMANCE_REPORT_PATH": "output/adsense-final-runtime-performance.json"},
    ),
    CheckSpec(
        "public_not_found",
        ("node", "tools/public_not_found_smoke.mjs"),
        180,
        {"BASE_URL": "https://lovetypes.tw"},
    ),
    CheckSpec(
        "public_visual",
        (
            sys.executable,
            "tools/predeploy_check.py",
            "--visual-only",
            "--base-url",
            "https://lovetypes.tw",
        ),
        1500,
        visual=True,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--skip-visual",
        action="store_true",
        help="Rehearsal only. The packet remains blocked because final visual evidence is required.",
    )
    parser.add_argument("--list", action="store_true", help="List the required checks without running them.")
    parser.add_argument("--timeout-scale", type=float, default=1.0)
    return parser.parse_args()


def command_text(command: tuple[str, ...]) -> str:
    return shlex.join(command)


def parse_metrics(output: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for line in output.splitlines():
        match = KEY_VALUE_RE.match(line.strip())
        if match:
            metrics[match.group(1)] = match.group(2)
    return metrics


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=30,
    )
    return result.stdout.strip()


def repository_state() -> dict[str, object]:
    head = git_output("rev-parse", "HEAD")
    origin_parts = git_output("ls-remote", "origin", "refs/heads/main").split()
    origin = origin_parts[0] if origin_parts else ""
    dirty_paths = [line for line in git_output("status", "--porcelain").splitlines() if line]
    return {
        "head": head,
        "originMain": origin,
        "headMatchesOriginMain": bool(head) and head == origin,
        "clean": not dirty_paths,
        "dirtyPathCount": len(dirty_paths),
    }


def run_check(spec: CheckSpec, timeout_scale: float) -> dict[str, object]:
    started = time.monotonic()
    environment = os.environ.copy()
    environment.update(spec.environment)
    try:
        result = subprocess.run(
            list(spec.command),
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=max(1, int(spec.timeout * timeout_scale)),
        )
        code = result.returncode
        output = result.stdout
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        code = 124
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        output = stdout + stderr
        timed_out = True
    return {
        "name": spec.name,
        "command": command_text(spec.command),
        "status": "passed" if code == 0 else "failed",
        "exitCode": code,
        "timedOut": timed_out,
        "elapsedSeconds": round(time.monotonic() - started, 2),
        "metrics": parse_metrics(output),
        "outputTail": output[-4000:],
    }


def skipped_check(spec: CheckSpec) -> dict[str, object]:
    return {
        "name": spec.name,
        "command": command_text(spec.command),
        "status": "skipped",
        "exitCode": None,
        "timedOut": False,
        "elapsedSeconds": 0,
        "metrics": {},
        "outputTail": "",
    }


def summarize(checks: list[dict[str, object]], repository: dict[str, object]) -> dict[str, object]:
    passed = sum(item.get("status") == "passed" for item in checks)
    failed = sum(item.get("status") == "failed" for item in checks)
    skipped = sum(item.get("status") == "skipped" for item in checks)
    gate = next((item for item in checks if item.get("name") == "submission_gate"), {})
    gate_ready = gate.get("metrics", {}).get("adsense_submission_ready") == "true"
    blocked_reasons = [
        *[f"check failed: {item.get('name')}" for item in checks if item.get("status") == "failed"],
        *[f"check skipped: {item.get('name')}" for item in checks if item.get("status") == "skipped"],
    ]
    if not gate_ready:
        blocked_reasons.append("AdSense submission gate is not ready")
    if repository.get("clean") is not True:
        blocked_reasons.append("repository has uncommitted changes")
    if repository.get("headMatchesOriginMain") is not True:
        blocked_reasons.append("HEAD does not match origin/main")
    ready = (
        passed == len(CHECKS)
        and failed == 0
        and skipped == 0
        and gate_ready
        and repository.get("clean") is True
        and repository.get("headMatchesOriginMain") is True
    )
    return {
        "requiredChecks": len(CHECKS),
        "passedChecks": passed,
        "failedChecks": failed,
        "skippedChecks": skipped,
        "submissionGateReady": gate_ready,
        "repositoryClean": repository.get("clean") is True,
        "headMatchesOriginMain": repository.get("headMatchesOriginMain") is True,
        "blockedReasons": blocked_reasons,
        "readyToSubmit": ready,
    }


def main() -> int:
    args = parse_args()
    if args.timeout_scale <= 0:
        raise SystemExit("--timeout-scale must be greater than zero")
    if args.list:
        for spec in CHECKS:
            print(f"{spec.name}={command_text(spec.command)}")
        print(f"adsense_final_required_checks={len(CHECKS)}")
        return 0

    checks: list[dict[str, object]] = []
    for spec in CHECKS:
        print(f"adsense_final_step={spec.name} status=running", flush=True)
        result = skipped_check(spec) if args.skip_visual and spec.visual else run_check(spec, args.timeout_scale)
        checks.append(result)
        print(f"adsense_final_step={spec.name} status={result['status']}", flush=True)

    repository = repository_state()
    summary = summarize(checks, repository)
    packet = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "site": "https://lovetypes.tw/",
        "mode": "rehearsal" if args.skip_visual else "final",
        "readOnly": True,
        "submitsReview": False,
        "repository": repository,
        "summary": summary,
        "checks": checks,
        "result": "pass" if summary["readyToSubmit"] else "blocked",
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"adsense_final_packet={output}")
    print(f"adsense_final_required_checks={summary['requiredChecks']}")
    print(f"adsense_final_passed_checks={summary['passedChecks']}")
    print(f"adsense_final_failed_checks={summary['failedChecks']}")
    print(f"adsense_final_skipped_checks={summary['skippedChecks']}")
    print(f"adsense_final_ready_to_submit={'true' if summary['readyToSubmit'] else 'false'}")
    return 0 if summary["readyToSubmit"] else 1


if __name__ == "__main__":
    sys.exit(main())
