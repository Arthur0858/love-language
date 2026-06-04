#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_TOOLS = [
    "tools/generate_multilingual_site.py",
    "tools/site_quality_audit.py",
    "tools/check_generated_fresh.py",
]


def run_step(name: str, command: list[str], env: dict[str, str] | None = None) -> None:
    print(f"== {name} ==", flush=True)
    subprocess.run(command, cwd=ROOT, check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LoveTypes pre-deploy quality checks.")
    parser.add_argument(
        "--visual",
        action="store_true",
        help="Also run tools/visual_check.mjs. Start a local server or set BASE_URL first.",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="BASE_URL for the optional visual check, for example http://127.0.0.1:4173.",
    )
    args = parser.parse_args()

    run_step("python compile", [sys.executable, "-m", "py_compile", *PYTHON_TOOLS])
    run_step("generated freshness", [sys.executable, "tools/check_generated_fresh.py"])
    run_step("site quality audit", [sys.executable, "tools/site_quality_audit.py"])

    if args.visual:
        node = "/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
        env = os.environ.copy()
        if args.base_url:
            env["BASE_URL"] = args.base_url
        run_step("browser visual check", [node, "tools/visual_check.mjs"], env=env)

    print("predeploy_checks=ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
