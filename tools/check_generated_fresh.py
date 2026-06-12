#!/usr/bin/env python3
from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".github", ".wrangler", "__pycache__", "node_modules", "output"}
EXCLUDED_SUFFIXES = {".pyc", ".xlsx"}


def site_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if relative.parts and relative.parts[0] == "tools":
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        files[relative.as_posix()] = path
    return files


def copy_repo(target: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        ignored = set()
        for name in names:
            if name in EXCLUDED_DIRS:
                ignored.add(name)
            elif Path(name).suffix in EXCLUDED_SUFFIXES:
                ignored.add(name)
        return ignored

    shutil.copytree(ROOT, target, ignore=ignore)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lovetypes-generated-") as tmp:
        tmp_root = Path(tmp) / "site"
        copy_repo(tmp_root)
        subprocess.run([sys.executable, "tools/generate_multilingual_site.py"], cwd=tmp_root, check=True)

        current = site_files(ROOT)
        generated = site_files(tmp_root)
        issues: list[str] = []

        for name in sorted(set(current) - set(generated)):
            issues.append(f"current site file missing after regeneration: {name}")
        for name in sorted(set(generated) - set(current)):
            issues.append(f"regeneration creates uncommitted site file: {name}")
        for name in sorted(set(current) & set(generated)):
            if not filecmp.cmp(current[name], generated[name], shallow=False):
                issues.append(f"generated site file is stale: {name}")

        print(f"generated_site_files={len(generated)}")
        print(f"generated_fresh_issues={len(issues)}")
        for issue in issues[:200]:
            print(issue)
        if len(issues) > 200:
            print(f"... {len(issues) - 200} more issue(s)")
        return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
