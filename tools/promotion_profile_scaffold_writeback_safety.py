#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "promotion" / "first-round"
PROFILE_PROOF_FILES = (
    SOURCE_DIR / "proof-youtube_shorts.txt",
    SOURCE_DIR / "proof-tiktok.txt",
    SOURCE_DIR / "proof-instagram_reels.txt",
)
EXPECTED_REJECTION = "profile proof_note still looks like the scaffold screenshot filename"


def run_tool(args: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, "tools/promotion_profile_text_import.py", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout


def main() -> int:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="lovetypes-profile-scaffold-") as temp_name:
        temp_root = Path(temp_name)
        temp_docs = temp_root / "docs" / "promotion" / "first-round"
        temp_docs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_DIR, temp_docs)

        checked = 0
        rejected = 0
        for proof_file in PROFILE_PROOF_FILES:
            temp_proof = temp_docs / proof_file.name
            code, output = run_tool(["check", "--input", str(temp_proof)], ROOT)
            checked += 1
            if code != 0 or "promotion_profile_text_import_issues=0" not in output:
                issues.append(f"{proof_file.name}: scaffold should remain checkable for formatting\n{output}")
            code, output = run_tool(["add", "--input", str(temp_proof)], ROOT)
            if code != 0 and EXPECTED_REJECTION in output:
                rejected += 1
            else:
                issues.append(f"{proof_file.name}: scaffold add should be rejected\n{output}")

    print(f"promotion_profile_scaffold_writeback_safety_checked={checked}")
    print(f"promotion_profile_scaffold_writeback_safety_rejected={rejected}")
    print(f"promotion_profile_scaffold_writeback_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
