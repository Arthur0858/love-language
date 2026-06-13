#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import promotion_post_writeback as writeback


ROOT = Path(__file__).resolve().parents[1]
POST_IMPORT_TOOL = ROOT / "tools" / "promotion_post_text_import.py"
PLACEHOLDER_URLS = (
    "https://example.com/post",
    "https://example.com/replace-with-real-post-url",
    "https://www.youtube.com/shorts/replace-with-real-post-id",
    "https://www.youtube.com/shorts/placeholder",
)
SAFE_SAMPLE_URL = "https://www.youtube.com/shorts/lovetypes-proof-url-123"


def sample_text(post_url: str) -> str:
    return "\n".join([
        "LoveTypes platform post writeback",
        "platform: youtube_shorts",
        "task_id: publish-lt-s01-iris-silence",
        "status: published",
        "published_date: 2026-06-15",
        f"post_url: {post_url}",
        "views: 0",
        "site_clicks: 0",
        "quiz_starts: 0",
        "quiz_completions: 0",
        "proof_note: post URL and first metrics verified",
        "",
    ])


def run_import_check(text: str) -> tuple[int, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, str(POST_IMPORT_TOOL), "check", "--input", str(temp_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    return result.returncode, result.stdout


def validate() -> tuple[dict[str, int], list[str]]:
    issues: list[str] = []
    rejected_by_validator = 0
    rejected_by_import = 0
    for url in PLACEHOLDER_URLS:
        if writeback.valid_post_url(url):
            issues.append(f"placeholder URL should be rejected by validator: {url}")
        else:
            rejected_by_validator += 1
        code, output = run_import_check(sample_text(url))
        if code == 0 or "promotion_post_text_import_issues=0" in output:
            issues.append(f"placeholder URL should be rejected by import check: {url}")
        else:
            rejected_by_import += 1

    safe_validator_passed = 1 if writeback.valid_post_url(SAFE_SAMPLE_URL) else 0
    safe_code, safe_output = run_import_check(sample_text(SAFE_SAMPLE_URL))
    safe_import_passed = 1 if safe_code == 0 and "promotion_post_text_import_issues=0" in safe_output else 0
    if not safe_validator_passed:
        issues.append("safe sample URL should pass validator")
    if not safe_import_passed:
        issues.append("safe sample URL should pass import check")

    return {
        "placeholderUrls": len(PLACEHOLDER_URLS),
        "rejectedByValidator": rejected_by_validator,
        "rejectedByImport": rejected_by_import,
        "safeValidatorPassed": safe_validator_passed,
        "safeImportPassed": safe_import_passed,
    }, issues


def main() -> int:
    metrics, issues = validate()
    print(f"promotion_placeholder_url_checked={metrics['placeholderUrls']}")
    print(f"promotion_placeholder_url_rejected_by_validator={metrics['rejectedByValidator']}")
    print(f"promotion_placeholder_url_rejected_by_import={metrics['rejectedByImport']}")
    print(f"promotion_placeholder_url_safe_validator_passed={metrics['safeValidatorPassed']}")
    print(f"promotion_placeholder_url_safe_import_passed={metrics['safeImportPassed']}")
    print(f"promotion_placeholder_url_safety_issues={len(issues)}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
